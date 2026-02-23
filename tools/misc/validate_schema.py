# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import jsonschema
import json, os

class JsonSchemaValidator(object):

    def validate_json_schema(self, json_schema, json):
        try:
            jsonschema.validate(instance=json, schema=json_schema)
            print('Schema...... valid')
        except Exception as e:
            #print(e)
            print('Schema...... invalid')
            #exit()

if __name__ == "__main__":

    validator = JsonSchemaValidator()
    base = 'C:\\Users\\RUMSPD\\source\\repos\\meta\\meta\\'
    #base = 'C:\\Users\\RUMSPD\\source\\repos\\livewire\\data\\meta\\'
    paths = [
     base + 'dot-dtg.json',
     base + 'inl-avta.json',
     base + 'inl-reachnow.json',
     base + 'lscfa-bastrop.json',
     base + 'ngv-uptime.json',
     base + 'nrel-drivecat.json',
     base + 'nrel-fleetdna.json',
     base + 'nrel-tsdc.json',
     base + 'roadmap.json',
    ]
    low_level_path = 'C:\\Users\\RUMSPD\\source\\repos\\livewire\\data\\move_to_nrel_repo\\llmd'
    high_level_schema = 'C:\\Users\\RUMSPD\\source\\repos\\livewire\\tools\\schemas\\catalog\\catalog-strict.json'
    low_level_schema = 'C:\\Users\\RUMSPD\\source\\repos\\livewire\\tools\\schemas\\dictionary\\dictionary.json'
    with open(low_level_schema, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    for file_name in os.listdir(low_level_path):
        if '.summary' in file_name: 
            continue
        print(file_name)
        with open(os.path.join(low_level_path, file_name), 'r', encoding='utf-8') as f: 
            metadata = json.load(f)
            validator.validate_json_schema(schema, metadata)