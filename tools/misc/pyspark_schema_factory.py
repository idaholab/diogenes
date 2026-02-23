# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import file_utils as f_utils
import csv 

from pyspark.sql.types import StructType
from pyspark_field_factory import PySparkFieldFactory


class PySparkSchemaReader:


    def __init__(self, schema_file_path, original_schema):
        f_utils.check_if_file_exists(schema_file_path)
        self.schema_file_path = schema_file_path
        self.original_schema = original_schema
   

    def read_pyspark_schema(self):
        fields = []
        fields = self.get_schema_fields()
        schema = StructType(fields)
        return schema


    def get_schema_fields(self):
        fields = []
        field_factory = PySparkFieldFactory()

        schema_file_handle = open(self.schema_file_path)
        schema_csv_reader = csv.reader(schema_file_handle, delimiter=',', quotechar='"', skipinitialspace=True)

        for i, tokenized_schema_line in enumerate(schema_csv_reader, start=1):
            if i == 1:
                pass
            else:
                processed_field = field_factory.create_pyspark_field(tokenized_schema_line, i)
                fields.append(processed_field)

        self.__validate_fields_are_formatted_correct(fields)
        self.__validate_correct_number_of_fields(fields)
        self.__validate_field_names_are_correct_and_in_order(fields)

        return fields 


    def __validate_fields_are_formatted_correct(self, fields):
        if None in fields:
            raise IOError("Incorrectly formatted field(s) in schema: '{}'".format(self.schema_file_path)) 

    
    def __validate_correct_number_of_fields(self, fields):
        if len(fields) != len(self.original_schema):
            raise IOError("Incorrect number of field(s) in schema: '{}'".format(self.schema_file_path)) 

    
    def __validate_field_names_are_correct_and_in_order(self, fields):
        for original_field, new_field in zip(self.original_schema, fields):
            original_field_names = []
            incorrect_field_names = []
            old_field_name = original_field.name
            new_field_name = new_field.name

            if old_field_name != new_field_name or ():
                original_field_names.append(old_field_name)
                incorrect_field_names.append(new_field_name)

            if len(incorrect_field_names) != 0:    
                raise Exception("Original field name(s) \'{}\' does not match read field name(s) \'{}\'".format(original_field_names, incorrect_field_names))


class PySparkSchemaWriter:

    ABNORMAL_FIELD_TYPES = { 
        "boolean" : "bool",
        "tinyint" : "byte",
        "bigint" : "long",
        "smallint" : "short"
    }


    def write_schema(self, schema_file_path, partitioned_df):
        schema = partitioned_df.schema

        try:
            schema_file_handle = open(schema_file_path, 'w+')
            schema_file_handle.write("Field Name, Field Type, Nullable, Metadata\n")
            for field in schema:
                field_type = self.get_field_type(field.dataType.simpleString())
                schema_file_handle.write(str(field.name) + ', \"' + str(field_type) + '\", ' + str(field.nullable) + ', ' + str(field.metadata) + '\n')
            schema_file_handle.close()
        except Exception as e:
            raise Exception(str(e))

    
    def get_field_type(self, raw_field_type):
        field_type = raw_field_type

        if raw_field_type in self.ABNORMAL_FIELD_TYPES.keys():
            field_type = self.ABNORMAL_FIELD_TYPES[raw_field_type]
        
        return field_type 

