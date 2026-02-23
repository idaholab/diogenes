# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from pathlib import Path

def separate_strings_with_underscore(strings: list, alphabetize: bool=False) -> str:
    if alphabetize == True:
        strings = sorted(strings, key=str.lower)
    connected_string = ''
    for string in strings:
        connected_string += string + '_'
    connected_string = connected_string[:-1]
    return connected_string

def find_match(name: str, filenames: list[str], extensions=None) -> str | None:
    """
    Find a matching filename, trying the exact name first, then with extensions.
    
    Args:
        name (str): Base filename to search for
        filenames (list[str]): List of available filenames to search in
        extensions (list or str, optional): Extensions to try. Can be:
            - None: Try common tabular data formats
            - str: Single extension (e.g., '.csv' or 'csv')
            - list: Multiple extensions (e.g., ['.csv', '.xlsx', '.parquet'])
    
    Returns:
        str | None: The matched filename, or None if no match found
    """
    # First try exact match
    if name in filenames:
        return name
    
    # Default to common tabular data formats if no extensions specified
    if extensions is None:
        extensions = ['.csv', '.tsv', '.xlsx', '.xls', '.parquet', 
                     '.json', '.jsonl', '.feather', '.orc', '.avro']
    
    # Convert single extension string to list
    if isinstance(extensions, str):
        extensions = [extensions]
    
    # Normalize extensions to ensure they start with a dot
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
    
    # Try each extension
    for ext in extensions:
        name_with_ext = f"{name}{ext}"
        if name_with_ext in filenames:
            return name_with_ext
    
    return None

# def find_match(name: str, filenames: list[str], extension: str = ".csv") -> str | None:
#     if name in filenames:
#         return name
#     name_with_ext = f"{name}{extension}"
#     if name_with_ext in filenames:
#         return name_with_ext
#     return None