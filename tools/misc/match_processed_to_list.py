# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os
import pandas as pd

if __name__ == "__main__":

    DIR = './llmd'

    dataset_list = pd.read_csv('livewire_datasets_report.csv')
    dataset_list['done'] = 'No'

    for file in os.listdir(DIR):
        if ".summary" in file:
            continue
        split_name = file.split('.')
        project = split_name[0]
        if len(split_name) > 3:
            dataset = split_name[1] + '.' + split_name[2]
        else:
            dataset = split_name[1]
        dataset_list['done'].loc[(dataset_list['datasetIdentifier'] == dataset) & (dataset_list['projectIdentifier'] == project)] = 'Yes'

    dataset_list.to_csv('completed_processing.csv', index=False)