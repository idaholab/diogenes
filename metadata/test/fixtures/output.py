# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest

from test.fixtures.input import veritas_constraints


@pytest.fixture
def output_file_directory():
    output_file_directory = './test/test_data/output'
    return output_file_directory
    

def rules_file_path(output_file_directory):
    rules_file_path = output_file_directory + '/' + 'rules.csv'
    return rules_file_path