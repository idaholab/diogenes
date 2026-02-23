# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import json 


def load_json(file_path):
    json_contents = None 

    with open(file_path, errors='ignore') as json_file_handle:
        json_contents = json.load(json_file_handle)

    return json_contents 