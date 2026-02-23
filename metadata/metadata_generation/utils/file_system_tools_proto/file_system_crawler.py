# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os
import glob


def get_isolated_file_path_from_directory(directory_file_path):
    directory_file_paths = get_directory_file_paths(directory_file_path) 

    if len(directory_file_paths) != 1:
        raise IOError("There is not exactly 1 file in directory: {}".format(directory_file_path))
    
    file_path = directory_file_paths[0]

    return file_path

def get_directory_file_paths(directory_file_path, extensions=None):
    """
    Get file paths from a directory matching specified extensions.
    
    Args:
        directory_file_path (str): Path to the directory to search
        extensions (list or str, optional): File extensions to match. Can be:
            - None: Match all common tabular data formats
            - str: Single extension (e.g., '.csv' or 'csv')
            - list: Multiple extensions (e.g., ['.csv', '.xlsx', '.parquet'])
    
    Returns:
        list: List of file paths matching the specified extensions
        
    Raises:
        IOError: If no files with specified extensions are found
    """
    # Default to common tabular data formats if no extensions specified
    if extensions is None:
        extensions = ['.csv', '.tsv', '.xlsx', '.xls', '.parquet', 
                     '.json', '.jsonl', '.feather', '.orc', '.avro']
    
    # Convert single extension string to list
    if isinstance(extensions, str):
        extensions = [extensions]
    
    # Normalize extensions to ensure they start with a dot
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
    
    directory_file_paths = []
    
    for ext in extensions:
        pattern = os.path.join(directory_file_path, f'*{ext}')
        directory_file_paths.extend(glob.glob(pattern))

    if len(directory_file_paths) == 0:
        ext_list = ', '.join(extensions)
        raise IOError(f"There are no {ext_list} files in directory: {directory_file_path}")

    return directory_file_paths