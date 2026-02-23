# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import csv

from ..utils.file_system_tools import load_json

from ..veritas.datatypes import JSONIndex


class JSONIndexIterator:

    def __init__(self, metadata_file_path=None, metadata=None):
        if metadata_file_path != None: 
            metadata = load_json(metadata_file_path)
        elif metadata == None: 
            raise ValueError('No metadata file path or metadata passed to JSONIndexIterator')
        self.__metadata_iterator = MetadataIterator(metadata)

    def iterate(self):
        for table_metadata_index in self.__metadata_iterator.iterate_table():
            for attribute_metadata_index in self.__metadata_iterator.iterate_attribute():
                JSON_index = JSONIndex(table_metadata_index, attribute_metadata_index)
                yield JSON_index   

    def iterate_tables(self):
         for table_metadata_index in self.__metadata_iterator.iterate_table():
            yield table_metadata_index      


class MetadataIterator:

    def __init__(self, metadata):
        self.__metadata = metadata
        self.__current_table_index = 0
        self.__current_attribute_index = 0
        self.__current_data_quality_metric = None

    def iterate_table(self):
        tables = self.__metadata['objects']
        number_of_tables = len(tables)

        for self.__current_table_index in range(number_of_tables):
            yield self.__current_table_index

    def iterate_attribute(self):
        attributes = self.__get_attributes()
        number_of_attributes = len(attributes)

        for self.__current_attribute_index in range(number_of_attributes):
            yield self.__current_attribute_index

    def iterate_data_quality_metrics(self):
        attribute = self.__get_attribute()
        assert 'dataQuality' in attribute.keys()
        data_quality_metrics = attribute['dataQuality']

        for self.__current_data_quality_metric in data_quality_metrics:
            yield self.__current_data_quality_metric  

    def iterate_categorical(self):
        assert 'frequencies' in self.__current_data_quality_metric.keys()
        frequencies = self.__current_data_quality_metric['frequencies']

        for frequency in frequencies:
            yield (frequency['name'], frequency['frequencyN'], frequency['frequencyPercent'])

    def __get_attributes(self):
        attributes = self.__metadata['objects'][self.__current_table_index]['attributes']
        return attributes

    def __get_attribute(self):
        attribute = self.__metadata['objects'][self.__current_table_index]['attributes'][self.__current_attribute_index]
        return attribute   


class CSVIterator:
    
    def __init__(self, csv_file_path, skip_header=False):
        self.__csv_file_path = csv_file_path
        self.__csv_file_handle = None
        self.__csv_reader = None
        self.__current_tokenized_line = None
        self.__line_number = 1
        self.__skip_header = skip_header

    def open_file(self):
        self.__csv_file_handle = open(self.__csv_file_path, 'r')
        self.__csv_reader = csv.reader(self.__csv_file_handle, delimiter=',')

    def close_file(self):
        self.__csv_file_handle.close()

    def iterate_lines(self):
        if self.__skip_header == True:
            next(self.__csv_reader)
            self.__line_number += 1

        for self.__current_tokenized_line in self.__csv_reader:
            yield self.__line_number
            self.__line_number += 1
            
    def get_tokenized_line(self, required_column_length):
        assert self.__current_tokenized_line != None

        if len(self.__current_tokenized_line) != required_column_length:
            raise IOError("Column number is not equal to {} in file: {}".format(required_column_length, self.__csv_file_path))

        return self.__current_tokenized_line