# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pandas as pd
import os
import json
import sys


def read_json(file_path):
    with open(file_path, errors='ignore') as json_file_handle:
        json_contents = json.load(json_file_handle)
    return json_contents

def parse_table_elements(metadata):
    for table_element in metadata['objects']:
        yield table_element

def parse_column_elements(table_element):
    for column_element in table_element['attributes']:
        yield column_element


class AnnotationsBuilder:

    SHEET_NAME_CHARACTER_LIMIT = 31

    def __init__(self):
        self.__sheets = {}
        self.__current_table_name = None 

    def add_sheet(self, parsed_table_element):
        self.__current_table_name = parsed_table_element['name']
        if self.__current_table_name not in self.__sheets.keys():
            self.__sheets[self.__current_table_name] = pd.DataFrame(columns=['Name', 'Type', 'Data Quality Class', 'Description', 'Format Function', 'Units', 'Relationships', 'Notes'])

    def add_annotation_line(self, parsed_metadata_element):
        if 'refersTo' in parsed_metadata_element.keys():
            refersTo = parsed_metadata_element['refersTo']
        else:
            refersTo = ''
        if 'description' in parsed_metadata_element.keys():
            description = parsed_metadata_element['description']
        else:
            description = ''
        if 'dataQualityClass' in parsed_metadata_element.keys():
            data_quality_class = parsed_metadata_element['dataQualityClass']
        else:
            data_quality_class = ''
        temp_df = pd.DataFrame({'Name' : parsed_metadata_element['name'], 'Type' : parsed_metadata_element['type'], 'Data Quality Class' : data_quality_class, 
                                'Description' : description, 'Format Function' : '', 'Units' : parsed_metadata_element['units'], 
                                'Relationships' : refersTo, 'Notes' : ''}, index=[0])
        self.__sheets[self.__current_table_name] = pd.concat([self.__sheets[self.__current_table_name], temp_df])    
    
    def write_annotations(self, output_file_path):
        excel_writer = pd.ExcelWriter(output_file_path + '.xlsx' , engine='xlsxwriter')

        for sheet_name in self.__sheets.keys():
            sheet_tab_name = sheet_name
            if len(sheet_name) > self.SHEET_NAME_CHARACTER_LIMIT:
                sheet_tab_name = sheet_tab_name[:self.SHEET_NAME_CHARACTER_LIMIT]
            self.__sheets[sheet_name].to_excel(excel_writer, sheet_name=sheet_tab_name, index=False)

        excel_writer.close()

if __name__ == "__main__":
    input_file_path = 'C:\\Users\\RUMSPD\\source\\repos\\livewire\\tools\\misc\\tsdc.ds50.json'
    output_file_path = './/annotations'

    metadata = read_json(input_file_path)
    annotations_builder = AnnotationsBuilder()
    
    for parsed_table_element in parse_table_elements(metadata):
        annotations_builder.add_sheet(parsed_table_element)
        for parsed_column_element in parse_column_elements(parsed_table_element):
            annotations_builder.add_annotation_line(parsed_column_element)
    
    annotations_builder.write_annotations(output_file_path)



