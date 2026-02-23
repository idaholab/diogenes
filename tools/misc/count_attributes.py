# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os, json
from collections import defaultdict

if __name__ == '__main__':
    meta_high_level_metadata_dir = 'C:\\Users\\RUMSPD\\source\\repos\\meta\\meta'
    counts = defaultdict(int)

    for file_name in os.listdir(meta_high_level_metadata_dir):
        if file_name == 'test': 
            continue
        with open(os.path.join(meta_high_level_metadata_dir, file_name), 'r', encoding='utf-8') as f:
            high_level_metadata = json.load(f)
            if 'dataset' in high_level_metadata.keys():
                for dataset in high_level_metadata['dataset']:
                    for attribute in dataset:
                        counts[attribute] += 1

    for key, value in counts.items():
        print(f"{key}: {value}")