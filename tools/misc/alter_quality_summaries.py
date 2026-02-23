# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os,json

original_data_dir = 'C:\\Users\\RUMSPD\\source\\repos\\livewire\\data\\llmd'

for file_name in os.listdir(original_data_dir):
    split_tokens = file_name.split('.')
    if split_tokens[-2] == 'summary':
        with open(os.path.join(original_data_dir, file_name), 'r') as summary_file_handler: 
            summary_json = json.load(summary_file_handler) 
            new_json = {'dataQualitySummary' : {}}
            new_json['dataQualitySummary']['measures'] = summary_json['dataQualitySummary']['measures']
            new_json['dataQualitySummary']['referenceURL'] = summary_json['dataQualitySummary']['referenceURL']
            new_file_name = ""
            for file_name_substr in split_tokens[:-2]:
                new_file_name += file_name_substr + '.'
            new_file_name += 'summary.json'
        with open( os.path.join('C:\\Users\\RUMSPD\\source\\repos\\livewire\\data\\llmd', new_file_name), 'w+') as json_out_file_handle:
            json.dump(new_json, json_out_file_handle, indent=2)
