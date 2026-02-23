# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest
import copy

import pandas as pd

from metadata_generation.veritas.error_catalog_generation.error_tables import ErrorTables

from metadata_generation.veritas.scorecard_distillation.scorecard_distiller import ScorecardMetrics


@pytest.fixture
def error_tables_dir_path():
    error_tables_dir_path = './test/test_data/error_tables/'
    return error_tables_dir_path


@pytest.fixture
def error_tables(error_tables_dir_path):
    dfs = {}
    file_names = ['errors', 'erroneous_records', 'missing_records']

    for file_name in file_names:
        dfs[file_name] = pd.read_csv(error_tables_dir_path + file_name + '.csv') 

    dfs['erroneous_records'] = dfs['erroneous_records'].set_index('Unnamed: 0')
    dfs['missing_records'] = dfs['missing_records'].set_index('Unnamed: 0')
    error_tables = (dfs['errors'], dfs['erroneous_records'], dfs['missing_records'])

    return error_tables
