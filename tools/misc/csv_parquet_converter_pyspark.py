# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import file_utils as f_utils
import os, argparse, timeit

from pyspark.sql import SparkSession, types
from pyspark.sql.types import StructField, StructType
from pyspark_schema_factory import PySparkSchemaWriter, PySparkSchemaReader
from pyspark_file_writer import PySparkFileWriter
from pyspark_file_reader import PySparkFileReader

def csv_to_parquet(args):
    try:
        start_time = timeit.default_timer()
        pyspark_csv_reader = PySparkFileReader(args.input, "csv")  
        pyspark_csv_reader.activate_spark_context("CSV to Parquet Reader")
        partitioned_df = pyspark_csv_reader.read_file(args.rows)
        schema = get_parquet_table_schema(args.schema, partitioned_df)
        partitioned_df = set_parquet_table_schema_if_different(partitioned_df, schema)
        pyspark_writer = PySparkFileWriter(partitioned_df, args.output, "parquet")
        pyspark_writer.write_to_single_file()
        pyspark_csv_reader.close_spark_context()
        elapsed_time = timeit.default_timer() - start_time
    except Exception as e:
        print("Failed to convert CSV file to Parquet file: {}".format(args.input))
        print("Error: " + str(e))
        exit() 

    print_conversion_summary(args.input, args.output, elapsed_time)    
    print_parquet_sample(args.output, args.rows)


def get_parquet_table_schema(schema_file_path, partitioned_df):
    if schema_file_path == None:
        schema = partitioned_df.schema
        return schema

    try:
        original_schema = partitioned_df.schema
        schema_reader = PySparkSchemaReader(schema_file_path, original_schema)
        schema = schema_reader.read_pyspark_schema()
    except Exception as e:
        print("\nFailed to read Parquet schema: {}".format(schema_file_path))
        print("Error: " + str(e))
        exit()         

    return schema


def set_parquet_table_schema_if_different(partitioned_df, schema):
    if partitioned_df.schema == schema:
        return partitioned_df
    
    old_schema = partitioned_df.schema
    new_schema = schema
    fields_marked_for_cast = []

    try:
        for original_field, new_field in zip(old_schema, new_schema):
            fields_marked_for_cast += mark_field_for_cast_if_datatypes_differ(original_field, new_field)
        partitioned_df = cast_parquet_fields(partitioned_df, fields_marked_for_cast)
    except Exception as e:
        print("\nFailed to apply Parquet schema: {}".format(args.input))
        print("Error: " + str(e))
        exit()   

    return partitioned_df


def mark_field_for_cast_if_datatypes_differ(original_field, new_field):
    marked_field = []
    old_field_datatype = original_field.dataType.simpleString()
    new_field_datatype = new_field.dataType.simpleString()

    if old_field_datatype != new_field_datatype:
        marked_field = [new_field]

    return marked_field


def cast_parquet_fields(partitioned_df, fields_marked_for_cast):
    for field in fields_marked_for_cast:
        partitioned_df = partitioned_df.withColumn(field.name, partitioned_df[field.name].cast(field.dataType))

    return partitioned_df  


def print_parquet_sample(parquet_file_path, number_of_rows=5):
    if number_of_rows == 0:
        return

    try:
        pyspark_parquet_reader = PySparkFileReader(parquet_file_path, "parquet")
        pyspark_parquet_reader.activate_spark_context("Parquet Sample Reader")
        partitioned_df = pyspark_parquet_reader.read_file(number_of_rows=number_of_rows)
        partitioned_df.show(truncate=True)
        print("\n\n")
        pyspark_parquet_reader.close_spark_context()
    except Exception as e:
        print("\nFailed to produce sample from Parquet file: {}".format(parquet_file_path))
        print("Error: " + str(e))  


def parquet_to_csv(args):
    try:
        f_utils.check_if_path_exists(args.input)
        start_time = timeit.default_timer()
        pyspark_parquet_reader = PySparkFileReader(args.input, "parquet")
        pyspark_parquet_reader.activate_spark_context("Parquet to CSV Reader")
        partitioned_df = pyspark_parquet_reader.read_file(args.rows, args.columns)
        write_schema_from_parquet_table_if_specified(args.schema, partitioned_df)
        pyspark_writer = PySparkFileWriter(partitioned_df, args.output, "csv")
        pyspark_writer.write_to_single_file()  
        pyspark_parquet_reader.close_spark_context() 
        elapsed_time = timeit.default_timer() - start_time
    except Exception as e:
        print("\nFailed to convert Parquet file to CSV file: {}".format(args.input))
        print("Error: " + str(e))
        exit()
    
    print_conversion_summary(args.input, args.output, elapsed_time)
    print_csv_sample(args.output, args.rows)


def write_schema_from_parquet_table_if_specified(schema_file_path, partitioned_df):
    if args.schema == None:
        return 

    try:    
        schema_writer = PySparkSchemaWriter()
        schema_writer.write_schema(schema_file_path, partitioned_df)
    except Exception as e:
        print("\nFailed to write schema from csv file: {}".format(args.input))
        print("Error: " + str(e))
        exit()           


def print_csv_sample(csv_file_path, number_of_rows=5):
    if number_of_rows == 0:
        return

    try:
        pyspark_csv_reader = PySparkFileReader(csv_file_path, "csv")
        pyspark_csv_reader.activate_spark_context("Print Sample of CSV")
        partitioned_df = pyspark_csv_reader.read_file(number_of_rows=number_of_rows)
        partitioned_df.show(truncate=True)
        print("\n\n")
        pyspark_csv_reader.close_spark_context()
    except Exception as e:
        print("\nFailed to produce sample from CSV file: {}".format(csv_file_path))
        print("Error: " + str(e))


def print_conversion_summary(input_file_path, output_file_path, elapsed_time):

    print("\n\nOriginal file path:  {}".format(input_file_path))
    print("Converted file path: {}".format(output_file_path))
    print("Original file size: {} bytes".format(os.path.getsize(input_file_path)))
    print("New file size:      {} bytes\n".format(os.path.getsize(output_file_path)))

    print("Conversion time: {}\n".format(elapsed_time))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Convert between CSV and Parquet file format')
    parser.add_argument('-i', '--input', help="Name of file to convert", required=True)
    parser.add_argument('-o', '--output', help="Name of file that's to be converted to", default='converted_data')
    parser.add_argument('-m', '--mode', help='Conversion mode: parquet_to_csv or csv_to_parquet', required=True)
    parser.add_argument('-r', '--rows', help='Print sample rows from a CSV created from a parquet file', type=int, default=-1)
    parser.add_argument('-d', '--delimiter', help='The delimiter specifying different CSV values', default=',')
    parser.add_argument('-sc', '--schema', help="Name of the file containing pyarrow schema", default=None)
    parser.add_argument('-c', '--columns', nargs='*', help='Index of the columns converted to CSV', type=int, default=[])

    args = parser.parse_args()

    print(args.rows)

    if args.mode == 'parquet_to_csv':
        parquet_to_csv(args)
    elif args.mode == 'csv_to_parquet':
        csv_to_parquet(args)
    else:
        print("Conversion type does not exist: '{}'".format(args.mode))
