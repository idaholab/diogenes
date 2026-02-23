# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os, shutil
import pandas as pd
import math
import numpy as np
import json

from ...settings import InsightFilePaths

from ...veritas.datatypes import DataQualityClassEnum

from ...insight.table_descriptions import TableDescriptionGenerator
from ...insight.column_annotations import ColumnAnnotations
from ...insight.formatting.json_formatting import FrequencyFormatter
from ...insight import key_maps
from ...insight import manual_annotations

from ...utils.file_iterator import MetadataIterator
from ...utils.file_parsing import MetadataTableParser


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            if obj == -9999.9999:
                return "Error"
            else:
                return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd._libs.tslibs.timestamps.Timestamp):
            return str(obj)
        else:
            return super(NpEncoder, self).default(obj)


def create_llmd(metadata_generation_input, use_annotations=False, write_excel=True):
    llmd_builder = LLMDBuilder(metadata_generation_input.partial_dataset_metadata, metadata_generation_input.table_descriptions)
    for dataset_file_name, dataset_file in metadata_generation_input.dataset_files:
        dataset_annotations = metadata_generation_input.get_dataset_file_annotations(dataset_file_name)
        llmd_builder.add_dataset_file_JSON(dataset_file_name, dataset_file, dataset_annotations)
    llmd_builder.add_key_info(use_annotations)

    if write_excel == True:
        llmd_builder.write_LLMD(metadata_generation_input.partial_dataset_metadata)

    llmd = llmd_builder.get_LLMD()
    return llmd


class LLMDBuilder:

    def __init__(self, partial_metadata, table_descriptions):
        project_identifier = partial_metadata['project_identifier']
        dataset_identifier = partial_metadata['identifier']
        self.__LLMD = {'name': partial_metadata['title'], 'description': partial_metadata['description'], 'modified': 'Placeholder', 'authors': 'Livewire Data Platform'}
        self.__LLMD['referenceURL'] = '/api/datasets/{}/{}/files/dictionary-{}.{}.pdf'.format(project_identifier, dataset_identifier, project_identifier, dataset_identifier)
        self.__LLMD['objects'] = []
        self.__table_description_generator = TableDescriptionGenerator(table_descriptions)

    def add_dataset_file_JSON(self, dataset_file_name, dataset_file, dataset_file_annotations):      
        llmd_columns = LLMDColumns(dataset_file_annotations)

        for i in range(dataset_file.num_columns):
            llmd_columns.add_column_LLMD(dataset_file, i)

        column_LLMD = llmd_columns.get_ordered_column_metadata(dataset_file.num_columns)
        table_description = self.__table_description_generator.get_table_description(dataset_file_name)

        object_dict = {}
        object_dict['name'] = dataset_file_name
        object_dict['count'] = dataset_file.num_rows
        if table_description.strip() != "":
            object_dict['description'] = table_description
        object_dict['type'] = 'table'
        object_dict['relationships'] = {}
        object_dict['attributes'] = column_LLMD

        self.__LLMD['objects'].append(object_dict)
        self.__LLMD = manual_annotations.resolve_manual_table_annotations(self.__LLMD)

    def add_key_info(self, use_annotations): 
        self.__LLMD = key_maps.map_primary_keys_to_table(self.__LLMD, use_annotations)
        self.__LLMD = key_maps.map_foreign_keys_to_table(self.__LLMD, use_annotations)
        metadata_iterator = MetadataIterator(self.__LLMD)
        for current_table_index in metadata_iterator.iterate_table(): 
            metadata_table_parser = MetadataTableParser(self.__LLMD, current_table_index)
            # if relationships is empty, delete
            if not bool(metadata_table_parser.get_table_value('relationships')):
                del self.__LLMD['objects'][current_table_index]['relationships']

    def get_LLMD(self): 
        return self.__LLMD

    def write_LLMD(self, partial_metadata):
        output_dir = InsightFilePaths.output_metadata_directory_path

        if os.path.exists(output_dir): 
            shutil.rmtree(output_dir)

        os.makedirs(output_dir)
        LLMD_file_name = partial_metadata['project_identifier'] + '.' + partial_metadata['identifier']

        with open(output_dir + '/' + LLMD_file_name + '.json', "w+") as outfile:
            json.dump(self.__LLMD, outfile, indent=2, cls=NpEncoder)


class LLMDColumns:

    def __init__(self, excel_dataset_descriptor):
        self.__LLMD_columns = {}
        self.__excel_dataset_descriptor = excel_dataset_descriptor

    def add_column_LLMD(self, dataset_file, column_index):
        column_annotations = ColumnAnnotations(column_index, self.__excel_dataset_descriptor)
        metric_JSON_blocks_factory= MetricJSONBlocksFactory()
        metric_blocks = metric_JSON_blocks_factory.get_metric_blocks(dataset_file, column_annotations)
        column_metadata_dictionary = self.__assemble_column_metadata_dictionary_in_order(metric_blocks, column_annotations)
        self.__LLMD_columns[column_annotations.name()] = column_metadata_dictionary

    def __assemble_column_metadata_dictionary_in_order(self, metric_JSON_blocks, column_annotations):
        column_metadata_dictionary = {}
        column_metadata_dictionary['name'] = column_annotations.name()
        column_metadata_dictionary['type'] = column_annotations.llmd_type()
        column_metadata_dictionary['units'] = column_annotations.units()
        if column_annotations.description_exists():
            column_metadata_dictionary['description'] = column_annotations.description()
        if metric_JSON_blocks != []:
            column_metadata_dictionary['dataQuality'] = metric_JSON_blocks
            column_metadata_dictionary['dataQualityClass'] = column_annotations.data_quality_class()
        if column_annotations.manual_annotations() != None:
            column_metadata_dictionary['manual_annotations'] = json.loads(column_annotations.manual_annotations())

        return column_metadata_dictionary
    
    def get_ordered_column_metadata(self, number_of_columns):
        sheets = []

        for column_index in range(number_of_columns):
            column_annotations = ColumnAnnotations(column_index, self.__excel_dataset_descriptor)
            sheets.append(self.__LLMD_columns[column_annotations.name()])

        return sheets


class MetricJSONBlocksFactory: 

    def __init__(self):
        self.__metric_factory_methods = {
            'n' : MetricJSONBlockFactory.count, 
            'ncat' : MetricJSONBlockFactory.number_of_categories, 
            'max' : MetricJSONBlockFactory.max, 
            'min' : MetricJSONBlockFactory.min, 
            'std_dev' : MetricJSONBlockFactory.std_dev, 
            'mean' : MetricJSONBlockFactory.mean,
            'median' : MetricJSONBlockFactory.median,
            'skewness' : MetricJSONBlockFactory.skewness, 
            'kurtosis' : MetricJSONBlockFactory.kurtosis, 
            'monotonicity_ratio' : MetricJSONBlockFactory.monotonicity_ratio
        }

        self.__metrics_for_each_data_quality_class = {
            DataQualityClassEnum.PRIMARY_KEY :                       ['n'],
            DataQualityClassEnum.COMPOSITE_PRIMARY_KEY :             ['n'],
            DataQualityClassEnum.COMPOSITE_PRIMARY_KEY_FOREIGN_KEY : ['n'], 
            DataQualityClassEnum.FOREIGN_KEY :                       ['n'],
            DataQualityClassEnum.COMPOSITE_FOREIGN_KEY:              ['n'], 
            DataQualityClassEnum.SEQUENCE :                          ['n'], 
            DataQualityClassEnum.NUMERICAL :                         ['n','min','max','mean','median','std_dev','skewness','kurtosis'],
            DataQualityClassEnum.CATEGORICAL :                       ['n','ncat'],
            DataQualityClassEnum.DATE :                              ['n'],
            DataQualityClassEnum.DATE_TIME :                         ['n'],
            DataQualityClassEnum.TIME:                               ['n'], 
            DataQualityClassEnum.NONE :                              ['n']
        }
        
    def get_metric_blocks(self, dataset_file, column_annotations):
        metric_JSON_blocks = []
        if column_annotations.llmd_type() == '(redacted)':
            return metric_JSON_blocks
        enumerated_data_quality_class = DataQualityClassEnum(column_annotations.data_quality_class())
        metrics_to_be_calculated = self.__metrics_for_each_data_quality_class[enumerated_data_quality_class]

        for metric in metrics_to_be_calculated:
            try:
                JSON_dict = self.__metric_factory_methods[metric](dataset_file, column_annotations)
                if not pd.isna(JSON_dict['value']):
                    metric_JSON_blocks.append(JSON_dict)
            except Exception as e:
                print(e)
                print(f"Exception occured during statistical analysis for (file_name: {dataset_file.get_dataset_table_name()}, column name: ", end='')
                print(f"{column_annotations.name()} - statistic: {metric}. Consider revising excel description")

        return metric_JSON_blocks


class MetricJSONBlockFactory: 
        
    @classmethod
    def count(cls, dataset_file, column_annotations):
        JSON_dict = {"name": "Count", "value": dataset_file.count(column_annotations.name()), "units": "n/a",
                     "description": "Number of rows with attribute/column specified"}

        return JSON_dict

    @classmethod
    def number_of_categories(cls, dataset_file, column_annotations):
        unformatted_frequencies = dataset_file.value_counts(column_annotations.name())
        formatted_frequencies = FrequencyFormatter.get_counts(unformatted_frequencies)
        JSON_frequencies = []

        for name, count in formatted_frequencies.items():
            JSON_frequencies.append({"name": name, "frequencyN": count,
                                "frequencyPercent": round(count / dataset_file.num_rows * 100, 3)})           

        number_of_categories = len(formatted_frequencies)

        JSON_dict = {"name": "Number of Categories", "value": number_of_categories,
                     "units": "n/a", "description": "Number of distinct/unique values for attribute/column",
                     "frequencies": JSON_frequencies}

        return JSON_dict

    @classmethod
    def max(cls, dataset_file, column_annotations):
        JSON_dict = {"name": "Maximum Value", "value": dataset_file.max(column_annotations.name()),
                     "units": column_annotations.units(), "description": "Maximum value for attribute/column"}

        return JSON_dict

    @classmethod    
    def min(cls, dataset_file, column_annotations):
        JSON_dict = {"name": "Minimum Value", "value": dataset_file.min(column_annotations.name()),
                     "units": column_annotations.units(), "description": "Minimum value for attribute/column"}

        return JSON_dict
    
    @classmethod
    def std_dev(cls, dataset_file, column_annotations):

        if math.isinf(dataset_file.std_dev(column_annotations.name())):
            std_dev_value = "Error"
        else:
            std_dev_value = round(dataset_file.std_dev(column_annotations.name()), 3)

        JSON_dict = {"name": "Standard Deviation", "value": std_dev_value,
                      "units": column_annotations.units(),
                      "description": "Statistical standard deviation for values specified for attribute/column"}

        return JSON_dict
    
    @classmethod
    def mean(cls, dataset_file, column_annotations):
        JSON_dict = {"name": "Mean", "value": round(dataset_file.mean(column_annotations.name()), 3),
                     "units": column_annotations.units(), "description": "Statistical mean for values specified for attribute/column"}

        return JSON_dict
    
    @classmethod
    def median(cls, dataset_file, column_annotations):
        JSON_dict = {"name": "Median", "value": round(dataset_file.median(column_annotations.name()), 3),
                     "units": column_annotations.units(), "description": "Statistical median for values specified for attribute/column"}

        return JSON_dict
    
    @classmethod    
    def skewness(cls, dataset_file, column_annotations):
        JSON_dict = {"name": "Skewness", "value": round(dataset_file.skewness(column_annotations.name()), 5), "units": "n/a",
                     "description": "Statistical measure of the asymmetry of the distribution of the values for this attribute/column relative to its mean."}
        return JSON_dict
    
    @classmethod
    def kurtosis(cls, dataset_file, column_annotations):
        JSON_dict = {"name": "Kurtosis", "value": round(dataset_file.kurtosis(column_annotations.name()), 5), "units": "n/a",
                     "description": "Statistical measure of the shape (peakedness) of the distribution of the values for this attribute/column."} 

        return JSON_dict
    
    @classmethod
    def monotonicity_ratio(cls, dataset_file, column_annotations): 
        JSON_dict = {"name": "Monotonicity Ratio", "value": round(dataset_file.monotonicity_ratio(column_annotations.name()), 5), "units": "n/a",
                            "description": "Custom statistical measure approximating the monotonic behavior for this attribute/column "} 
        return JSON_dict

