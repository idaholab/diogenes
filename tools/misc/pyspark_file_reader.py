# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import file_utils as f_utils

from pyspark.sql import SparkSession


class PySparkFileReader:

    def __init__(self, input_file_name, file_type):
        f_utils.check_if_file_exists(input_file_name)
        self.input_file_name = input_file_name
        self.file_type = file_type
        self.spark_context = None


    def activate_spark_context(self, name_of_context):
        self.spark_context = SparkSession.builder.appName(name_of_context).getOrCreate()


    def close_spark_context(self):
        self.spark_context.stop()


    def read_file(self, number_of_rows=-1, column_indices=[]):
        partitioned_df = self.__read_using_correct_function()
        partitioned_df = self.__get_columnar_subset_of_dataframe_if_specified(column_indices, partitioned_df)
        partitioned_df = self.__get_row_subset_of_dataframe_if_specified(number_of_rows, partitioned_df)

        return partitioned_df


    def __read_using_correct_function(self):
        if self.file_type == "csv":
            partitioned_df = self.spark_context.read.csv(self.input_file_name, header=True)
        if self.file_type == "parquet":
            partitioned_df = self.spark_context.read.parquet(self.input_file_name)

        return partitioned_df


    def __get_columnar_subset_of_dataframe_if_specified(self, column_indices, partitioned_df):
        if column_indices == []:
            return partitioned_df

        try:
            columns_in_df = [partitioned_df.columns[c] for c in column_indices]
            subset_df = partitioned_df.select(columns_in_df)
        except Exception as e:
            print("\nFailed to get column-wise subset from table: {}".format(self.input_file_name))
            print("Error: " + str(e))
            exit()
            
        return subset_df

    
    def __get_row_subset_of_dataframe_if_specified(self, number_of_rows, partitioned_df):
        if number_of_rows == -1:
            return partitioned_df

        try:
            subset_df = partitioned_df.limit(number_of_rows)
        except Exception as e:
            print("\nFailed to get row-wise subset from table: {}".format(self.input_file_name))
            print("Error: " + str(e))
            exit()

        return subset_df