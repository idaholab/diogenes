# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest
import pickle

from metadata_generation.veritas.rule_table_generation.rule_generation import RuleFrame
from metadata_generation.metadata_generation_input import Dataset


@pytest.fixture
def dataset_dir_path():
    dataset_dir_path = './test/test_data/data/has_errors/'
    return dataset_dir_path


@pytest.fixture
def dataset(dataset_dir_path):
    dataset = Dataset()
    dataset_file_names = ['batteryList.csv', 'batteryTestData.csv', 'batteryTestSummary.csv', 'vehicleList.csv']

    for file_name in dataset_file_names:
        dataset.add_dataset_file(dataset_dir_path + file_name, ',', 'Pandas')

    return dataset


@pytest.fixture
def error_batch_dir_path():
    error_batch_dir_path = './test/test_data/error_batches/pickle/'
    return error_batch_dir_path


@pytest.fixture
def error_batches(error_batch_dir_path):
    error_batches = {}
    error_batch_file_names = ['uniqueness', 'reference', 'normal_outlier', 'unit_outlier', 'low_frequency', 'date_outlier']

    for file_name in error_batch_file_names:
        error_batch_file_path = error_batch_dir_path + file_name + '.pkl'

        with open(error_batch_file_path, 'rb') as error_batch_handle:
            error_batches[file_name] = pickle.load(error_batch_handle)

    return error_batches