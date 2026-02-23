# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

# Debug:
import pandas as pd

import copy
import os

from pathlib import Path

from ...settings import PDFGenerationFilePaths, VeritasFilePaths

from ...utils.file_system_tools import InputFilePathFinder, load_json, get_file_name_from_path
from ...utils.file_iterator import MetadataIterator
from ...utils.file_grouping import FileGrouping

from ...pdf_generation.builders.pdf import PDFBuilder


class PDFGenerator:

    def group_objects(self, metadata):
        file_grouper = FileGrouping()
        metadata = file_grouper.group_files(metadata)
        return metadata


    def generate_pdf_from_json(self, error_when_file_exists, ignore_bad_chars_in_output):
        input_file_path_finder = InputFilePathFinder()
        metadata_file_path = input_file_path_finder.get_metadata_file_path(
            PDFGenerationFilePaths.input_metadata_directory_path)
        metadata = load_json(metadata_file_path)
        # TODO: Figure this out
        # metadata = self.group_objects(metadata)
        pdf_builder = PDFBuilder(metadata)
        pdf_builder.add_title_page()
        pdf_builder.add_title_supplement_page()

        metadata_iterator = MetadataIterator(metadata)
        for current_table_index in metadata_iterator.iterate_table():
            pdf_builder.add_table_pages(current_table_index, metadata_iterator)

        pdf_builder.print(metadata_file_path, error_when_file_exists, ignore_bad_chars_in_output)