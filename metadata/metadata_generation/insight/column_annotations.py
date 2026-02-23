# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pandas as pd

from ..utils.json_cleaning import ColumnDescriptionsCleaner


class ColumnAnnotations:


    def __init__(self, column_index, excel_dataset_annotations):
        self.__column_index = column_index
        self.__excel_column_annotations = excel_dataset_annotations[column_index:column_index+1]

    def name(self):
        name = self.__excel_column_annotations['Name'][self.__column_index]
        return name

    def data_quality_class(self):
        dq_class = self.__excel_column_annotations['Data Quality Class'][self.__column_index]
        if dq_class.startswith('?'):
            dq_class = dq_class[1:]
        
        return dq_class

    def llmd_type(self):
        dq_type = self.__excel_column_annotations['Type'][self.__column_index]
        if dq_type.startswith('?'):
            dq_type = dq_type[1:]
        
        return dq_type

    def units(self):
        units = self.__excel_column_annotations['Units'][self.__column_index]
        
        if pd.isna(units):
            units = 'n/a'

        return units 
    
    def format_module(self):
        module_str = self.__excel_column_annotations['Format Function'][self.__column_index] 

        if pd.isna(module_str):
            module_str = 'n/a'
        else:
            module_str = module_str.split('.')[0]
            module_str = module_str.strip()

        return module_str

    def format_function(self):
        func_call_str = self.__excel_column_annotations['Format Function'][self.__column_index]

        if pd.isna(func_call_str):
            func_call_str = 'n/a'
        else:
            func_call_str = func_call_str.split('.')[1]
            func_call_str = func_call_str.strip()

        return func_call_str

    def description(self):
        column_description_cleaner = ColumnDescriptionsCleaner()
        column_description = column_description_cleaner.replace_bad_characters(str(self.__excel_column_annotations['Description'][self.__column_index]))
        return column_description 
    
    def description_exists(self):
        if "Descriptions" not in self.__excel_column_annotations:
            return None
        description_exists = True
        if pd.isna(self.__excel_column_annotations['Description'][self.__column_index]) or \
           self.__excel_column_annotations['Description'][self.__column_index].strip() ==  "": 
            description_exists = False
        return description_exists
    
    def manual_annotations(self):
        if 'Manual Annotations' not in self.__excel_column_annotations:
            return None
        
        manual_annotations = self.__excel_column_annotations['Manual Annotations'][self.__column_index]
        if not pd.notna(manual_annotations): 
            manual_annotations = None

        return manual_annotations
