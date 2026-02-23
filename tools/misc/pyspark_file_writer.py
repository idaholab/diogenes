# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import shutil, glob

class PySparkFileWriter:

    def __init__(self, partitioned_df, output_file_path, file_type):
        self.partitioned_df = partitioned_df
        self.output_file_path = output_file_path
        self.file_type = file_type


    def write_to_single_file(self):
        directory_path_of_partitioned_files = "dir_" + self.output_file_path
        self.__write_using_correct_function(directory_path_of_partitioned_files)
        verbosely_named_file = self.__get_coalesced_file(directory_path_of_partitioned_files)
        shutil.move(verbosely_named_file, self.output_file_path)
        shutil.rmtree(directory_path_of_partitioned_files)


    def __get_coalesced_file(self, directory_path_of_partitioned_csv_files):
        file_with_prefix_part = glob.glob(directory_path_of_partitioned_csv_files + '/' + r'part*.' + self.file_type)

        if len(file_with_prefix_part) != 1:
            raise Exception("Expected one file in folder: {}".format(directory_path_of_partitioned_csv_files))

        return file_with_prefix_part[0]

    
    def __write_using_correct_function(self, directory_path_of_partitioned_files):
        if self.file_type == "csv":
            self.partitioned_df.coalesce(1).write.csv(directory_path_of_partitioned_files, mode='overwrite', header=True)
        if self.file_type == "parquet":
            self.partitioned_df.coalesce(1).write.parquet(directory_path_of_partitioned_files, mode='overwrite')
