# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os
import xml.etree.ElementTree as ET 
import pandas as pd
import argparse

from pathlib import Path

from dataclasses import dataclass


@dataclass
class Annotation:

    # shortcut to remove all the duplicative empty returns for all variables and set to None

    def field(field_type: str, initial_value: str = None) -> str:    
        storage_name = '_' + field_type

        @property
        def field_property(self) -> str:
            field_value = getattr(self, storage_name)
            if field_value == None:
                ''
            return field_value
        
        @field_property.setter
        def field_property(self, field_value: str):
            setattr(self, storage_name, field_value)
        
        field_property = initial_value
        return field_property
    
    name: str = field('name')
    data_type: str = field('data_type')
    data_quality_type: str = field('data_quality_type')
    description: str = field('description')
    units: str = field('units')
    relationships: str = field('relationships')
    notes: str = field('notes')

    # function should no longer be referenceable outside of class: delete
    del field

    def set_data_type(self, data_dictionary_type: str, data_quality_type: str) -> None: 
        if data_dictionary_type == 'numeric' and data_quality_type == 'categorical':
            self.data_type = 'integer'
        elif data_dictionary_type == 'string' and data_quality_type == 'categorical':
            self.data_type = 'string'
        elif data_dictionary_type == 'numeric' and data_quality_type == 'numerical':
            self.data_type = 'number'
        elif data_dictionary_type == 'string' and data_quality_type == 'none': 
            self.data_type = 'string'
        else:
            self.data_type = None

    def set_data_quality_type(self, length_of_categories: int, data_dictionary_type: str) -> None:
        if length_of_categories > 1:
            self.data_quality_type = 'categorical'
        elif length_of_categories == 0 and data_dictionary_type == 'string':
            self.data_quality_type = 'none'
        elif length_of_categories == 0 and data_dictionary_type == 'numeric': 
            self.data_quality_type = 'numerical'


    def set_annotation_if_redacted(self, is_redacted: bool) -> None:
        if not is_redacted:
            return 
        self.data_type = '(redacted)'
        self.data_quality_type = 'none'
        self.units = None
        self.relationships = None
        self.notes = None

    def set_missing_if_mode_is_9s(self, mode: float, data_quality_type: bool) -> None:
        if data_quality_type != 'numerical' and self.notes == None:
            return 
    
        mode_9s = None

        for m in mode:
            try:
                for char in str(int(m)):
                    if char != 9:
                        break
                    mode_9s = int(m)
            except:
                pass

        if mode_9s != None:
            self.notes = str(mode_9s)

    def set_data_type_if_numerical_integer(self, is_all_integers: bool, data_quality_type: str) -> None:
        if data_quality_type != 'numerical' or not is_all_integers: 
            return

        self.data_type = 'integer' 


class TSDCVariableParser:

    def get_attribute(self, desired_attribute: str, variable_attributes: dict) -> Annotation:
        if desired_attribute in variable_attributes:
            return variable_attributes[desired_attribute]
        return None
    
    def has_categories(self, variable: ET.Element) -> bool:
        has_categories = False

        if len(list(variable)):
            has_categories = True

        return has_categories
    
    def check_for_missing_value(self, variable: ET.Element) -> str:
        for category in list(variable):
            if category.attrib['label'] == 'Missing value':
                return category.attrib['code']
        return None
    
    
def parseTSDCDataDictionary(file_path: str) -> dict[Annotation]: 

    tree = ET.parse(file_path)
    root = tree.getroot()
    annotations = {}

    for item in root:
        variable_parser = TSDCVariableParser()
        annotation = Annotation()
        annotation.name = variable_parser.get_attribute('name', item.attrib)
        if annotation.name != None:
            annotation.name = annotation.name.lower()
        annotation.description = variable_parser.get_attribute('desc', item.attrib)
        data_dictionary_type = variable_parser.get_attribute('type', item.attrib)
        if variable_parser.has_categories(item):
            annotation.notes = variable_parser.check_for_missing_value(item)
        annotation.set_data_quality_type(len(item), data_dictionary_type)
        annotation.set_data_type(data_dictionary_type, annotation.data_quality_type)
        annotations[annotation.name] = annotation

    return annotations


class TSDCExploratoryDataAnalysis: 

    def mode(self, dataset: pd.DataFrame, column_name: str) -> float:
        return dataset[column_name].mode()
    
    def is_redacted(self, dataset: pd.DataFrame, column_name: str) -> bool: 
        is_redacted = False

        if dataset[column_name][0] == 'REDACTED':
            is_redacted = True
            
        return is_redacted
    
    def exclusively_integers(self, dataset: pd.DataFrame, column_name: str) -> bool: 
        is_integers = True

        for _, row in dataset.iterrows():
            str_value = str(row[column_name])
            split_str_value = str_value.split('.')
            if len(split_str_value) > 1:
                is_integers = False

        return is_integers


class AnnotationsSheet: 

    def __init__(self):
        self.names = []
        self.data_types = []
        self.data_quality_types = []
        self.descriptions = []
        self.units = []
        self.relationships = []
        self.notes = []

    def add_annotations(self, annotation: Annotation): 
        self.names.append(annotation.name)
        self.data_types.append(annotation.data_type)
        self.data_quality_types.append(annotation.data_quality_type)
        self.descriptions.append(annotation.description)
        self.units.append(annotation.units)
        self.relationships.append(annotation.relationships)
        self.notes.append(annotation.notes)

    def write_sheet(self, sheet_name: str, writer: pd.ExcelWriter): 
        df = pd.DataFrame({'Name': self.names, 'Type': self.data_types, 'Data Quality Class': self.data_quality_types,
                             'Description': self.descriptions, 'Units': self.units, 'Relationships': self.relationships,
                             'Notes': self.notes})
        df.to_excel(writer, sheet_name, index=False)


class PartialAnnotations: 

    def __init__(self):
        self.sheets = {}
        self.used_annotations = {}

    def add_sheet(self, file_path: str, annotations: dict[Annotation]):
        current_df = pd.read_csv(file_path)
        sheet_annotations = AnnotationsSheet()
        for column_name in current_df.columns:
            if column_name not in annotations.keys():
                empty_annotation = Annotation()
                empty_annotation.name = column_name
                sheet_annotations.add_annotations(empty_annotation)
            else:
                annotation = annotations[column_name]
                eda = TSDCExploratoryDataAnalysis()
                annotation.set_annotation_if_redacted(eda.is_redacted(current_df, column_name))
                annotation.set_missing_if_mode_is_9s(eda.mode(current_df, column_name), annotation.data_quality_type)
                annotation.set_data_type_if_numerical_integer(eda.exclusively_integers(current_df, column_name), annotation.data_quality_type)
                self.used_annotations[annotation.name] = annotation
                sheet_annotations.add_annotations(annotation)

        self.sheets[Path(file_path).stem] = sheet_annotations

    def add_unused_annotations_sheet(self, annotations: dict[Annotation], unused_annotations=True):
        if not unused_annotations:
            return 
        unused_annotations_sheet = AnnotationsSheet()
        for _, annotation in annotations.items():
            if annotation.name in self.used_annotations.keys():
                continue
            unused_annotations_sheet.add_annotations(annotation)
        self.sheets['unused_annotations'] = unused_annotations_sheet
    
    def write_annotations_file(self, output_file_path: str): 
        writer = pd.ExcelWriter(output_file_path, engine='openpyxl')
        for file_name, annotation_sheet in self.sheets.items():
            annotation_sheet.write_sheet(file_name, writer)
        writer.close()

    
if __name__ == "__main__": 
    parser = argparse.ArgumentParser('Break down TSDC XML files and format them as partial annotations')
    parser.add_argument('--unused_annotations', '-unused', type=str, default='true', help='create an extra sheet that has all the XML annotations that did not have a match in the data')
    args = parser.parse_args()

    if args.unused_annotations.lower() == 'true': 
        unused_annotations = True
    else:
        unused_annotations = False
    
    file_path = 'C:\\Users\\RUMSPD\\Desktop\\Livewire\\data\\TSDC\\tsdc.ds72\\data-dictionary.xml.txt'
    data_dir = 'C:\\Users\\RUMSPD\\Desktop\\Livewire\\data\\TSDC\\tsdc.ds72\\mtsa-san-francisco-2000-raw-data\\data'
    annotations_path = 'C:\\Users\\RUMSPD\\Desktop\\Livewire\\data\\TSDC\\tsdc.ds72\\partial_annotations.xlsx'

    formatted_dictionary_annotations = parseTSDCDataDictionary(file_path)
    partial_sheeted_annotations = PartialAnnotations()
    for file_name in os.listdir(data_dir): 
        partial_sheeted_annotations.add_sheet(os.path.join(data_dir, file_name), formatted_dictionary_annotations)
    partial_sheeted_annotations.add_unused_annotations_sheet(formatted_dictionary_annotations, unused_annotations)
    partial_sheeted_annotations.write_annotations_file(annotations_path)