# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os
import pandas as pd
pd.options.mode.chained_assignment = None
import warnings

from .utils.file_system_tools import FullFileNameFinder
from .utils.file_system_tools_proto import file_system_crawler
from .utils.file_system_tools_proto import json_loader
from .utils.file_system_tools import  ConfigurationFilePathFinder
from .utils.constraints import Constraints, VeritasConstraints
from .utils.json_cleaning import ProjectMetadataCleaner, TableDescriptionsCleaner

from .dataframe import Dataset
from .settings import InsightFilePaths, VeritasFilePaths


class MetadataGenerationInputReader:
  
    @classmethod
    def read_dataset(cls, settings, dataset_directory_path, dataframe_type='Pandas'):
        dataset = Dataset() 

        for dataset_file_path in file_system_crawler.get_directory_file_paths(dataset_directory_path):
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                dataset.add_dataset_file(dataset_file_path, settings.delimiter, dataframe_type)

        return dataset

    @classmethod
    def read_annotations(cls, annotations_file_path): 
        dataset_annotations = pd.ExcelFile(annotations_file_path)
        return dataset_annotations

    @classmethod
    def read_partial_dataset_metadata(cls, settings, project_metadata_file):
        partial_dataset_metadata = None
        project_metadata = json_loader.load_json(project_metadata_file)
        project_metadata_cleaner = ProjectMetadataCleaner()
        project_metadata = project_metadata_cleaner.replace_bad_characters(project_metadata)
        
        for current_partial_dataset_metadata in project_metadata['dataset']:
            if current_partial_dataset_metadata['identifier'] == settings.dataset_identifier:
                partial_dataset_metadata = current_partial_dataset_metadata
                break
        
        if partial_dataset_metadata == None:
            raise IOError('Cannot find dataset identifier \'{}\' in project metadata'.format(settings.dataset_identifier))
        
        partial_dataset_metadata['project_identifier'] = project_metadata['identifier']

        return partial_dataset_metadata

    @classmethod
    def read_table_descriptions(cls, table_descriptions_file_path): 
        table_descriptions = None
        
        if os.path.exists(table_descriptions_file_path):
            table_descriptions = json_loader.load_json(table_descriptions_file_path)
            table_descriptions_cleaner = TableDescriptionsCleaner()
            table_descriptions = table_descriptions_cleaner.replace_bad_characters(table_descriptions)

        return table_descriptions

    @classmethod
    def read_constraints(cls, configuration_directory_path):
        configuration_file_path_finder = ConfigurationFilePathFinder(configuration_directory_path)
        general_constraints_file_path = configuration_file_path_finder.get_configuration_file_path('general_constraints.csv')
        units_constraints_file_path = configuration_file_path_finder.get_configuration_file_path('unit_constraints.csv')
        veritas_constraints = VeritasConstraints()
        
        general_constraints = Constraints(general_constraints_file_path)
        general_constraints.set_constraints()
        veritas_constraints.general_constraints = general_constraints

        unit_constraints = Constraints(units_constraints_file_path)
        unit_constraints.set_constraints()
        veritas_constraints.unit_constraints = unit_constraints

        return veritas_constraints

    @classmethod
    def read_real_name_to_excel_name_map(cls, excel_annotations, data_directory_path):
        full_file_name_finder = FullFileNameFinder(data_directory_path)
        real_name_to_excel_name_map = {}

        for excel_dataset_file_name in sorted(excel_annotations.sheet_names):
            full_file_name = full_file_name_finder.get_full_file_name_from_part(excel_dataset_file_name)  
            real_name_to_excel_name_map[full_file_name] = excel_dataset_file_name
        
        return real_name_to_excel_name_map


class MetadataGenerationInput:

    def __init__(self, settings):
        metadata_generation_input_reader = MetadataGenerationInputReader()
        self.__dataset = metadata_generation_input_reader.read_dataset(settings, InsightFilePaths.data_directory_path)
        self.__annotations = metadata_generation_input_reader.read_annotations(InsightFilePaths.descriptive_info_path + '/annotations.xlsx')
        self.__partial_dataset_metadata = metadata_generation_input_reader.read_partial_dataset_metadata(settings, InsightFilePaths.descriptive_info_path + '/project_metadata.json')
        self.__table_descriptions = metadata_generation_input_reader.read_table_descriptions(InsightFilePaths.descriptive_info_path + '/table_descriptions.json')
        self.__dataset_excel_file_names = metadata_generation_input_reader.read_real_name_to_excel_name_map(self.__annotations, InsightFilePaths.data_directory_path)
        self.__constraints = metadata_generation_input_reader.read_constraints(VeritasFilePaths.configuration_directory_path)

    @property
    def dataset_files(self):
        for dataset_file_name, dataset_file in self.__dataset.dataset_files: 
            yield dataset_file_name, dataset_file 

    def get_dataset_file(self, file_name):
        return self.__dataset.get_dataset_file(file_name)

    @property
    def number_of_dataset_files(self):
        return len(self.__dataset.keys())

    @property
    def partial_dataset_metadata(self):
        return self.__partial_dataset_metadata

    @property
    def table_descriptions(self):
        return self.__table_descriptions

    def get_dataset_file_annotations(self, real_dataset_file_name):
        excel_sheet_name = self.__dataset_excel_file_names[real_dataset_file_name]
        annotations = pd.read_excel(self.__annotations, sheet_name=excel_sheet_name)

        # Ensure that the order of the annotations matches the order of the dataset file.
        original_columns = self.get_dataset_file(real_dataset_file_name).data_column_order
        # pd.Categorical turns string values into categorical values, which can be ordered non-alphabetically
        # In accordance to original column order
        annotations["Name"] = pd.Categorical(annotations["Name"], original_columns)
        sorted_annotations = annotations.sort_values("Name").reset_index(drop=True)
        return sorted_annotations

    @property
    def general_constraints(self):
        return self.__constraints.general_constraints

    @property
    def unit_constraints(self):
        return self.__constraints.unit_constraints
    
    def print_dataset(self, specified_output_dir: str = None) -> None: 
        self.__dataset.print_dataset(specified_output_dir)



