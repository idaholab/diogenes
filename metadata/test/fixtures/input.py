# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest
import json

from metadata_generation import insight

from metadata_generation.utils.file_iterator import MetadataIterator

from metadata_generation.utils.constraints import VeritasConstraints, Constraint, Constraints


@pytest.fixture
def good_data_directory_prefix():
    good_data_directory_prefix = './test/test_data/data/good'
    return good_data_directory_prefix


@pytest.fixture
def empty_data_directory_prefix():
    empty_data_directory_prefix = './test/test_data/data/empty'
    return empty_data_directory_prefix


@pytest.fixture
def partially_empty_data_directory_prefix():
    partially_empty_data_directory_prefix = './test/test_data/data/partially_empty'
    return partially_empty_data_directory_prefix


@pytest.fixture
def good_metadata_directory_prefix():
    good_metadata_directory_prefix = './test/test_data/metadata/good' 
    return good_metadata_directory_prefix


@pytest.fixture
def empty_metadata_directory_prefix():
    empty_metadata_directory_prefix = './test/test_data/metadata/empty'
    return empty_metadata_directory_prefix


@pytest.fixture
def good_configuration_directory_prefix():
    good_configuration_directory_prefix = './test/test_data/configuration/good'
    return good_configuration_directory_prefix


@pytest.fixture
def bad_configuration_directory_prefix():
    bad_configuration_directory_prefix = './test/test_data/configuration/bad'
    return bad_configuration_directory_prefix


@pytest.fixture
def unit_constraints_file_name():
    unit_constraints_file_name = '/unit_constraints.csv'
    return unit_constraints_file_name


@pytest.fixture
def general_constraints_file_name():
    general_constraints_file_name = '/general_constraints.csv'
    return general_constraints_file_name


@pytest.fixture
def existing_file_names():
    good_file_name = ['/data/one_example.csv', '/data/two_example.csv']
    return good_file_name


@pytest.fixture
def non_existing_file_names():
    bad_file_name = ['/data/one_example.csv', '/data/bad_example.csv']
    return bad_file_name


@pytest.fixture
def metadata_file_name():
    metadata_file_name = '/metadata/example.json'
    return metadata_file_name


@pytest.fixture
def good_data_path(good_data_directory_prefix, existing_file_names):
    good_data_path = good_data_directory_prefix + existing_file_names[0]
    return good_data_path


@pytest.fixture
def bad_data_path(good_data_directory_prefix, non_existing_file_names):
    bad_data_path = good_data_directory_prefix + non_existing_file_names[1]
    return bad_data_path    


@pytest.fixture
def good_data_paths(good_data_directory_prefix, existing_file_names):
    good_data_paths = [good_data_directory_prefix + existing_file_names[0], good_data_directory_prefix + existing_file_names[1]]
    return good_data_paths


@pytest.fixture
def bad_data_paths(good_data_directory_prefix, non_existing_file_names):
    bad_data_paths = [good_data_directory_prefix + non_existing_file_names[0], good_data_directory_prefix + non_existing_file_names[1]]
    return bad_data_paths    


@pytest.fixture
def empty_data_paths(empty_data_directory_prefix, existing_file_names):
    empty_data_paths = [empty_data_directory_prefix + existing_file_names[0], empty_data_directory_prefix + existing_file_names[1]]
    return empty_data_paths   


@pytest.fixture
def partially_empty_data_paths(partially_empty_data_directory_prefix, existing_file_names):
    partially_empty_data_paths = [partially_empty_data_directory_prefix + existing_file_names[0], partially_empty_data_directory_prefix + existing_file_names[1]]
    return partially_empty_data_paths  


@pytest.fixture
def good_metadata_file_path(good_metadata_directory_prefix, metadata_file_name):
    metadata_file_path = good_metadata_directory_prefix + metadata_file_name
    return metadata_file_path


@pytest.fixture
def empty_metadata_file_path(empty_metadata_directory_prefix, metadata_file_name):
    empty_metadata_file_path = empty_metadata_directory_prefix + metadata_file_name
    return empty_metadata_file_path


@pytest.fixture
def metadata(good_metadata_file_path):
    metadata_file_handle = open(good_metadata_file_path, 'r')
    metadata = json.load(metadata_file_handle)
    metadata_file_handle.close()
    return metadata


@pytest.fixture
def metadata_iterator(metadata):
    metadata_iterator = MetadataIterator(metadata)
    return metadata_iterator


@pytest.fixture
def good_general_configuration_file_path(good_configuration_directory_prefix, general_constraints_file_name):
    good_general_configuration_file_path = good_configuration_directory_prefix + general_constraints_file_name
    return good_general_configuration_file_path


@pytest.fixture
def good_unit_configuration_file_path(good_configuration_directory_prefix, unit_constraints_file_name):
    good_unit_configuration_file_path = good_configuration_directory_prefix + unit_constraints_file_name
    return good_unit_configuration_file_path
    

@pytest.fixture
def bad_configuration_file_path(bad_configuration_directory_prefix, unit_constraints_file_name):
    bad_configuration_file_path = bad_configuration_directory_prefix + unit_constraints_file_name
    return bad_configuration_file_path


@pytest.fixture
def expected_tokenized_unit_line():
    expected_tokenized_unit_line = ['V', 'N/A', 'N/A', 'Volt']
    return expected_tokenized_unit_line


@pytest.fixture
def expected_number_of_columns():
    expected_number_of_columns = 4
    return expected_number_of_columns


@pytest.fixture
def general_constraints(good_general_configuration_file_path):
    general_constraints = Constraints(good_general_configuration_file_path)
    general_constraints.set_constraints()
    return general_constraints


@pytest.fixture
def unit_constraints(good_unit_configuration_file_path):
    unit_constraints = Constraints(good_unit_configuration_file_path)
    unit_constraints.set_constraints()
    return unit_constraints


@pytest.fixture
def veritas_constraints(general_constraints, unit_constraints):
    veritas_constraints.general_constraints = general_constraints
    veritas_constraints.unit_constraints = unit_constraints
    return veritas_constraints



    