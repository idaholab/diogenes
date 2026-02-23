# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os, shutil
import fnmatch
import json

from pathlib import Path

from ..utils.error_handling import format_error
from ..utils.string_ops import find_match


class FileIntegrityHelper:

    @classmethod
    def verify_file_exists(cls, file_path):
        if not os.path.exists(file_path):
            raise IOError("File does not exist: {}".format(file_path))

    @classmethod
    def verify_files_not_empty(cls, file_paths):
        empty_files = []

        for file_path in file_paths:
            if os.stat(file_path).st_size == 0:
                empty_files.append(file_path)

        if len(empty_files) != 0:
            raise IOError("Files are empty: {}".format(empty_files))

    @classmethod
    def verify_file_not_empty(cls, file_path):
        if os.stat(file_path).st_size == 0:
            raise IOError("File is empty: {}".format(file_path))


class ConfigurationFilePathFinder:

    def __init__(self, configuration_directory):
        self.__general_constraints_file_name = "general_constraints.csv"
        self.__unit_constraints_file_name = "unit_constraints.csv"

        self.__configuration_file_paths = {
            self.__general_constraints_file_name: configuration_directory
            + "/"
            + self.__general_constraints_file_name,
            self.__unit_constraints_file_name: configuration_directory
            + "/"
            + self.__unit_constraints_file_name,
        }

        self.__file_integrity_helper = FileIntegrityHelper()

    def verify_configuration_files_exist(self):
        try:
            for _, configuration_file_path in self.__configuration_file_paths.items():
                self.__file_integrity_helper.verify_file_exists(configuration_file_path)
                self.__file_integrity_helper.verify_file_not_empty(
                    configuration_file_path
                )
        except IOError as error:
            self.__raise_configuration_io_error(error)

    def get_configuration_file_path(self, configuration_file):
        assert configuration_file in self.__configuration_file_paths.keys()
        configuration_file_path = self.__configuration_file_paths[configuration_file]

        return configuration_file_path

    def __raise_configuration_io_error(self, error):
        error_message = format_error(error)
        error_message += (
            "Veritas requires the following non-empty configuration files: \n"
        )
        error_message += self.__general_constraints_file_name + "\n"
        error_message += self.__unit_constraints_file_name + "\n"

        raise IOError(error_message)


class InputFilePathFinder:

    def get_metadata_file_path(self, metadata_directory_path):
        metadata_file_path = FileSystemCrawler.get_isolated_file_path_from_directory(
            metadata_directory_path
        )
        FileIntegrityHelper.verify_file_not_empty(metadata_file_path)
        return metadata_file_path

    def get_data_set_file_paths(self, data_set_directory_path):
        data_set_file_paths = []
        data_set_file_paths = FileSystemCrawler.get_directory_file_paths(
            data_set_directory_path
        )
        FileIntegrityHelper.verify_files_not_empty(data_set_file_paths)
        return data_set_file_paths

    # TODO: Add functionality that retrieves the correct error catalog files: get_error_catalog_files(self)


class FileSystemCrawler:

    @classmethod
    def get_isolated_file_path_from_directory(cls, directory_file_path):
        directory_file_paths = cls.get_directory_file_paths(directory_file_path)

        if len(directory_file_paths) != 1:
            raise IOError(
                "There is not exactly 1 file in directory: {}".format(
                    directory_file_path
                )
            )

        file_path = directory_file_paths[0]

        return file_path

    @classmethod
    def get_directory_file_paths(cls, directory_file_path):
        directory_file_names = os.listdir(directory_file_path)

        if len(directory_file_names) == 0:
            raise IOError(
                "There are no files in directory: {}".format(directory_file_path)
            )

        directory_file_paths = []

        for directory_file_name in directory_file_names:
            directory_file_paths.append(directory_file_path + "/" + directory_file_name)

        return directory_file_paths


class FullFileNameFinder:

    def __init__(self, directory_path_to_full_files):
        self.__directory_path_to_full_files = directory_path_to_full_files

    def get_full_file_name_from_part(self, partial_file_name: str) -> str:
        file_name = None
        files = os.listdir(self.__directory_path_to_full_files)
        # Correction of minor bug
        match = find_match(partial_file_name, files)

        if match != None:
            file_name = os.path.splitext(match)[0]
        else:
            raise ValueError(
                f"No matching file for annotations listed for lookup: {partial_file_name}"
            )
        return file_name


class DirectoryCreator:

    def __init__(self, error_when_file_exists):
        self.__error_when_file_exists = error_when_file_exists

    def create_directory(self, output_directory_path):
        directory_handler = DirectoryHandler()

        if self.__error_when_file_exists:
            directory_handler.error_if_exists(output_directory_path)
        else:
            directory_handler.overwrite_if_exists(output_directory_path)


class DirectoryHandler:

    def overwrite_if_exists(self, output_directory_path):
        if os.path.exists(output_directory_path):
            shutil.rmtree(output_directory_path)
        os.makedirs(output_directory_path)

    def error_if_exists(self, output_directory_path):
        if os.path.exists(output_directory_path):
            raise OSError("File exists: {}".format(output_directory_path))
        os.makedirs(output_directory_path)


def load_json(metadata_file_path):
    metadata = None

    with open(metadata_file_path) as metadata_file_handle:
        metadata = json.load(metadata_file_handle)

    return metadata


def get_file_name_from_path(file_path):
    return Path(file_path).stem
