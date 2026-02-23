# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os
import json

from dateutil.parser import parse


if __name__ == "__main__":
    DIR = "C:\\Users\\RUMSPD\\source\\repos\\livewire\\data\\llmd"
    sorted_files = []

    for file_name in os.listdir(DIR):
        if 'summary' in file_name or file_name == "readme.md":
            continue 
        with open(os.path.join(DIR, file_name), 'r') as file_handle: 
            print(file_name)
            metadata = json.load(file_handle)

            date = metadata['modified'].split(' ')[0]
            date_format = parse(date)

            if len(sorted_files) == 0:
                sorted_files.append((file_name, date_format))
                continue
            for index, packed_values in enumerate(sorted_files):
                _, current_date = packed_values
                if date_format < current_date: 
                    sorted_files.insert(index, (file_name, date_format)) 
                    break
                if index + 1 == len(sorted_files): 
                    sorted_files.append((file_name, date_format))
                    break
    
    for file_name, modified_date in sorted_files: 
        print(file_name + ' ' + str(modified_date.year))