# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os, json

with open('C:\\Users\\RUMSPD\\source\\repos\\livewire\\data\\d3.json', 'r', encoding='utf-8') as json_file_handle:
    llmd = json.load(json_file_handle)
    dataset_identifiers = []
    for datasets in llmd['dataset']:
        dataset_identifiers.append(datasets['identifier'])

    print(dataset_identifiers)

with open('C:\\Users\\RUMSPD\\source\\repos\\livewire\\data\\d3_identifiers.json', 'w') as json_file_handle:
    json.dump(dataset_identifiers, json_file_handle)
