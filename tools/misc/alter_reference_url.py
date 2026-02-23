# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os, json

llmd_dir = 'd3'
identifiers_path = 'C:\\Users\\RUMSPD\\source\\repos\\livewire\\data\\d3_identifiers.json'
new_files_dir = 'new_files'

def is_summary(file_name):
    if 'quality-summary' in file_name:
        return True
    else: 
        return False

for llmd_file in os.listdir(llmd_dir):
    llmd_file_path = os.path.join (llmd_dir, llmd_file)
    
    with open(identifiers_path, 'r') as json_file_handle:
        identifiers = json.load(json_file_handle)
    
    with open(llmd_file_path) as json_file_handle:
        llmd = json.load(json_file_handle)
        if is_summary(llmd_file):
            reference_URL = llmd['referenceURL']
        else:
            reference_URL = llmd['dataQualitySummary']['referenceURL']

    identifier = reference_URL.split('.')[1]
    #identifier_processed = reference_URL.split('-')[1]
    #print(identifier_processed)
    #identifier = identifier_processed.split('.')[-3] + '.' + identifier_processed.split('.')[-2]

    if identifier not in identifiers:
        print('Identifier: {} - not found'.format(identifier))
    else:
        new_file_path = os.path.join(new_files_dir, llmd_file)
        if is_summary(llmd_file):
            llmd['referenceURL'] = llmd['referenceURL'].replace('files', identifier + '/files')
        else:
            llmd['dataQualitySummary']['referenceURL'] = llmd['dataQualitySummary']['referenceURL'].replace('files', identifier + '/files')
        with open(new_file_path, 'w') as json_output_file:
            json.dump(llmd, json_output_file, indent=2)

