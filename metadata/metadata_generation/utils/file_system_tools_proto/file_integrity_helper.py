# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os


def verify_file_exists(file_path):
    if not os.path.exists(file_path):
        raise IOError("File does not exist: {}".format(file_path))
    
def verify_files_not_empty(file_paths):
    empty_files = []

    for file_path in file_paths:
        if os.stat(file_path).st_size == 0:
            empty_files.append(file_path)
        
    if len(empty_files) != 0:
        raise IOError("Files are empty: {}".format(empty_files))

def verify_file_not_empty(file_path):
    if os.stat(file_path).st_size == 0:
        raise IOError("File is empty: {}".format(file_path))