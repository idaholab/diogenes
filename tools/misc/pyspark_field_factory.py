# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os.path
import pyarrow as pa
import re

from pyspark.sql import types
from pyspark.sql.types import StructType, StructField


class PySparkFieldFactory:


    def create_pyspark_field(self, tokenized_schema_line, schema_line_number):
        try:
            name = self.__convert_to_field_name(tokenized_schema_line[0])
            datatype = self.__convert_to_pyspark_datatype(tokenized_schema_line[1])
            nullable = self.__convert_to_boolean(tokenized_schema_line[2])
            metadata = self.__convert_to_metadata(tokenized_schema_line[3]) 
        except Exception as e:
            print("\nIncorrect field format on line: '{}' - Scheme Line Items: {}".format(schema_line_number, tokenized_schema_line)) 
            print("Error: " + str(e)) 
            return None

        return StructField(name, datatype, nullable, metadata)


    def __convert_to_field_name(self, raw_field_name):
        processed_field_name = raw_field_name.strip()

        if processed_field_name == '':
            raise TypeError("Missing field name")

        return processed_field_name


    def __convert_to_boolean(self, raw_boolean):
        stripped_boolean = raw_boolean.strip()

        if stripped_boolean.lower() == "true": 
            return True
        elif stripped_boolean.lower() == "false":
            return False
        else:
            raise TypeError("Could not convert to boolean")


    def __convert_to_metadata(self, raw_metadata):
        processed_raw_metadata = raw_metadata.strip()

        if processed_raw_metadata == r'{}':
            processed_raw_metadata = None
        else:
            raise NotImplementedError("Meta data is not none")

        return processed_raw_metadata


    def __convert_to_pyspark_datatype(self, raw_datatype):
        stripped_datatype = raw_datatype.strip()

        if stripped_datatype == "data":
            return types.DataType()
        if stripped_datatype == "null":
            return types.NullType()
        if stripped_datatype == "string":
            return types.StringType()
        if stripped_datatype == "binary":
            return types.BinaryType()
        if stripped_datatype == "bool":
            return types.BooleanType()
        if stripped_datatype == "date":
            return types.DateType()
        if stripped_datatype == "timestamp":
            return types.TimestampType()
        if stripped_datatype == "double":
            return types.DoubleType()
        if stripped_datatype == "float":
            return types.FloatType()
        if stripped_datatype == "byte":
            return types.ByteType()
        if stripped_datatype == "int":
            return types.IntegerType()
        if stripped_datatype == "long":
            return types.LongType()
        if stripped_datatype == "short":
            return types.ShortType()
        if self.__is_decimal_type(stripped_datatype):
            return self.__convert_to_pyspark_decimal_type(stripped_datatype)
        else:
            raise TypeError("Could not convert '{}' to PySpark datatype".format(raw_datatype))

    
    def __is_decimal_type(self, stripped_datatype):
        is_decimal = False
        regex = re.compile(r'^decimal\(\s*(\d+|\d+\s*,\s*\d+)?\s*\)$')

        if regex.match(stripped_datatype):
            is_decimal = True

        return is_decimal


    def __convert_to_pyspark_decimal_type(self, stripped_datatype):
        decimal_data_type = None
        arguments = self.__get_arguments_from_function_string(stripped_datatype)
        number_of_arguments = len(arguments)

        if number_of_arguments == 1:
            precision = int(arguments[0])
            decimal_data_type = types.DecimalType(precision)
        elif number_of_arguments == 2:
            (precision, scale) = (int(arguments[0]), int(arguments[1]))
            decimal_data_type = types.DecimalType(precision, scale)
        else:
            decimal_data_type = types.DecimalType()

        return decimal_data_type


    def __get_arguments_from_function_string(self, stripped_datatype):
        try:
            first_parenthesis_index = stripped_datatype.find('(')
            arguments_no_parentheses = stripped_datatype[first_parenthesis_index+1:-1]
            arguments = arguments_no_parentheses.split(',')
        except Exception:
            raise Exception("Unable to parse arguments from datatype \'{}\'".format(stripped_datatype))

        return arguments
