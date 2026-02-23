# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest 
import os, shutil
 
from argparse import Namespace
from pathlib import Path

from metadata_generation.utils.file_system_tools import InputFilePathFinder, ConfigurationFilePathFinder, FileIntegrityHelper, FullFileNameFinder

from test.fixtures.input import good_data_directory_prefix, empty_data_directory_prefix, partially_empty_data_directory_prefix
from test.fixtures.input import good_metadata_directory_prefix, empty_metadata_directory_prefix
from test.fixtures.input import good_data_path, bad_data_path, good_data_paths, bad_data_paths
from test.fixtures.input import empty_data_paths, partially_empty_data_paths
from test.fixtures.input import good_metadata_file_path, empty_metadata_file_path
from test.fixtures.input import good_configuration_directory_prefix, good_unit_configuration_file_path


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * *  * FileIntegrityHelper Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


def test_verify_file_exists(good_data_path, bad_data_path):
    file_integrity_helper = FileIntegrityHelper()

    file_integrity_helper.verify_file_exists(good_data_path)

    with pytest.raises(IOError):
        file_integrity_helper.verify_file_exists(bad_data_path)

    
def test_verify_files_exists(good_data_paths, bad_data_paths):
    file_integrity_helper = FileIntegrityHelper()

    file_integrity_helper.verify_files_exist(good_data_paths)

    with pytest.raises(IOError):
        file_integrity_helper.verify_files_exist(bad_data_paths)


def test_verify_files_not_empty_good_input(good_data_paths):
    file_integrity_helper = FileIntegrityHelper()
    file_integrity_helper.verify_files_not_empty(good_data_paths)


def test_verify_files_not_empty_empty_input(empty_data_paths):
    file_integrity_helper = FileIntegrityHelper()

    with pytest.raises(IOError):
        file_integrity_helper.verify_files_not_empty(empty_data_paths)


def test_verify_files_not_empty_partially_empty_input(partially_empty_data_paths):
    file_integrity_helper = FileIntegrityHelper()

    with pytest.raises(IOError):
        file_integrity_helper.verify_files_not_empty(partially_empty_data_paths)


def test_verify_file_not_empty_good_input(good_data_path):
    file_integrity_helper = FileIntegrityHelper()
    file_integrity_helper.verify_file_not_empty(good_data_path)


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * *  InputFilePathFinder Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


def setup_input_file_path_finder_tests(directory_prefix):
    args = Namespace(input=directory_prefix)
    file_path_finder = InputFilePathFinder(args)
    return file_path_finder


def test_get_dataset_file_paths_good_input(good_data_directory_prefix, good_data_paths):
    file_path_finder = setup_input_file_path_finder_tests(good_data_directory_prefix)
    retrieved_data_file_paths = file_path_finder.get_dataset_file_paths()

    assert retrieved_data_file_paths[0] == good_data_paths[0]
    assert retrieved_data_file_paths[1] == good_data_paths[1]


def test_get_file_paths_empty_input(empty_data_directory_prefix):
    file_path_finder = setup_input_file_path_finder_tests(empty_data_directory_prefix)

    with pytest.raises(IOError):
        file_path_finder.get_dataset_file_paths()


def test_get_file_paths_partially_empty_input(partially_empty_data_directory_prefix):
    file_path_finder = setup_input_file_path_finder_tests(partially_empty_data_directory_prefix)

    with pytest.raises(IOError):
        file_path_finder.get_dataset_file_paths()


def test_get_file_path_good_metadata_input(good_metadata_directory_prefix, good_metadata_file_path):
    file_path_finder = setup_input_file_path_finder_tests(good_metadata_directory_prefix)
    retrieved_metadata_file_path = file_path_finder.get_metadata_file_path()    

    assert retrieved_metadata_file_path == good_metadata_file_path


def test_get_file_path_empty_metadata_input(empty_metadata_directory_prefix):
    file_path_finder = setup_input_file_path_finder_tests(empty_metadata_directory_prefix)
        
    with pytest.raises(IOError):
        file_path_finder.get_metadata_file_path()


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * *  ConfigurationFilePathFinder Tests  * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


def setup_configuration_file_path_finder_tests(directory_prefix):
    constraint_args = Namespace(config=directory_prefix)
    file_path_finder = ConfigurationFilePathFinder(constraint_args)
    return file_path_finder


def test_verify_configuration_files_exist(good_configuration_directory_prefix):
    bad_directory_prefix = '/this/directory/does/not/exist'
    good_file_path_finder = setup_configuration_file_path_finder_tests(good_configuration_directory_prefix)
    bad_file_path_finder = setup_configuration_file_path_finder_tests(bad_directory_prefix)

    good_file_path_finder.verify_configuration_files_exist()

    with pytest.raises(IOError):
        bad_file_path_finder.verify_configuration_files_exist() 
    

def test_get_configuration_file_path(good_configuration_directory_prefix, good_unit_configuration_file_path):
    file_path_finder = setup_configuration_file_path_finder_tests(good_configuration_directory_prefix)
    config_file_name = os.path.basename(good_unit_configuration_file_path)

    retrieved_configuration_file = file_path_finder.get_configuration_file_path(config_file_name)

    assert retrieved_configuration_file == good_unit_configuration_file_path


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * *   FullFileNameFinder Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################



def setup_test_directory() -> str:
    test_directory_name = 'test/test_data/test_directory'
    os.makedirs(test_directory_name)
    return test_directory_name

def setup_files_in_directory(test_directory_name: str, file_names: list[str]) -> None:
    for file_name in file_names:
        Path(os.path.join(test_directory_name, file_name)).touch()

def teardown_test_directory(test_directory_name: str) -> None:
    shutil.rmtree(test_directory_name)

@pytest.mark.parametrize(
    'file_to_create, file_name_regex, expected_file_name',
    [(['testfiles.csv'], 'testfile', 'testfiles'),
     (['test.files.csv'], 'test.', 'test.files'), 
     (['evwatts.analysis.highresdiagnostic.csv'], 'evwatts.analysis.highresdiagnos*', 'evwatts.analysis.highresdiagnostic')])
def test_get_full_file_name_from_regex(file_to_create: list[str], file_name_part: str, expected_file_name: str) -> None:
    test_directory_name = setup_test_directory()
    setup_files_in_directory(test_directory_name, file_to_create)
    full_file_name_finder = FullFileNameFinder(test_directory_name)
    file_name = full_file_name_finder.get_full_file_name_from_part(file_name_part)
    teardown_test_directory(test_directory_name)
    assert file_name == expected_file_name