# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os, shutil

from dataclasses import dataclass
from .utils.file_sampling import Reservoir_Sampler


VERITAS_VERSION = "v5.2.2"
MAX_NUM_CHAR_VARIATIONS_NEEDED_FOR_KEY_WARNING = 2


class DefaultFileLocations:

    INPUT_DIRECTORY_PATH: str = os.path.join(os.getcwd(), "input")
    OUTPUT_DIRECTORY_PATH: str = os.path.join(os.getcwd(), "output")
    CONFIGURATION_DIRECTORY_PATH: str = os.path.join(os.getcwd(), "configuration")
    DATA_DIRECTORY_PATH: str = os.path.join(INPUT_DIRECTORY_PATH, "data")
    DESCRIPTIVE_INFO_PATH: str = os.path.join(
        INPUT_DIRECTORY_PATH, "descriptive_information"
    )

    @classmethod
    def set_input(cls, input_path, n_rows, processes):
        # Sample the input and copy it into the input directory
        input_data_directory = cls.DATA_DIRECTORY_PATH
        if input_path and input_path != "/":
            if os.path.exists(input_path):
                # Update input_data_directory
                input_data_directory = os.path.join(input_path, "data")
                # Copy provided input to new input location.
                if os.path.exists(cls.INPUT_DIRECTORY_PATH):
                    shutil.rmtree(cls.INPUT_DIRECTORY_PATH)
                shutil.copytree(input_path, cls.INPUT_DIRECTORY_PATH)
            else:
                raise ValueError("Input directory does not exist!")

        # Sample Input
        if n_rows > 0:
            #input_data_directory = os.path.join()
            Reservoir_Sampler(
                input_data_directory, cls.DATA_DIRECTORY_PATH, n_rows, processes
            ).sample()

    @classmethod
    def set_output(cls, output_path):
        if output_path and output_path != "/":
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            cls.OUTPUT_DIRECTORY_PATH = output_path


@dataclass
class InsightFilePaths:

    data_directory_path: str = DefaultFileLocations.DATA_DIRECTORY_PATH
    descriptive_info_path: str = DefaultFileLocations.DESCRIPTIVE_INFO_PATH
    configuration_directory_path: str = os.path.join(
        DefaultFileLocations.CONFIGURATION_DIRECTORY_PATH, "insight"
    )
    output_metadata_directory_path: str = os.path.join(
        DefaultFileLocations.OUTPUT_DIRECTORY_PATH, "insight"
    )

    @classmethod
    def init(cls) -> None:
        cls.data_directory_path = DefaultFileLocations.DATA_DIRECTORY_PATH
        cls.descriptive_info_path = DefaultFileLocations.DESCRIPTIVE_INFO_PATH
        cls.configuration_directory_path = os.path.join(
            DefaultFileLocations.CONFIGURATION_DIRECTORY_PATH, "insight"
        )
        cls.output_metadata_directory_path = os.path.join(
            DefaultFileLocations.OUTPUT_DIRECTORY_PATH, "insight"
        )


@dataclass
class VeritasFilePaths:

    data_directory_path: str = DefaultFileLocations.DATA_DIRECTORY_PATH
    input_metadata_directory_path: str = InsightFilePaths.output_metadata_directory_path
    configuration_directory_path: str = os.path.join(
        DefaultFileLocations.CONFIGURATION_DIRECTORY_PATH, "veritas"
    )
    output_metadata_directory_path: str = os.path.join(
        DefaultFileLocations.OUTPUT_DIRECTORY_PATH, "veritas", "metadata"
    )
    output_quality_files_directory_path: str = os.path.join(
        DefaultFileLocations.OUTPUT_DIRECTORY_PATH, "veritas", "quality_files"
    )

    @classmethod
    def init(cls) -> None:
        cls.data_directory_path = DefaultFileLocations.DATA_DIRECTORY_PATH
        cls.input_metadata_directory_path = (
            InsightFilePaths.output_metadata_directory_path
        )
        cls.configuration_directory_path = os.path.join(
            DefaultFileLocations.CONFIGURATION_DIRECTORY_PATH, "veritas"
        )
        cls.output_metadata_directory_path = os.path.join(
            DefaultFileLocations.OUTPUT_DIRECTORY_PATH, "veritas", "metadata"
        )
        cls.output_quality_files_directory_path = os.path.join(
            DefaultFileLocations.OUTPUT_DIRECTORY_PATH, "veritas", "quality_files"
        )


@dataclass
class JsonSchemaValidationFilePaths:

    input_json_schema_directory_path: str = os.path.join(
        DefaultFileLocations.CONFIGURATION_DIRECTORY_PATH, "json_schema"
    )
    input_json_directory_path: str = VeritasFilePaths.output_metadata_directory_path

    @classmethod
    def init(cls) -> None:
        cls.input_json_schema_directory_path = os.path.join(
            DefaultFileLocations.CONFIGURATION_DIRECTORY_PATH, "json_schema"
        )
        cls.input_json_directory_path = VeritasFilePaths.output_metadata_directory_path


@dataclass
class PDFGenerationFilePaths:

    input_metadata_directory_path: str = VeritasFilePaths.output_metadata_directory_path
    output_pdf_directory_path: str = os.path.join(
        DefaultFileLocations.OUTPUT_DIRECTORY_PATH, "pdf_generation", "pdf"
    )
    output_html_directory_path: str = os.path.join(
        DefaultFileLocations.OUTPUT_DIRECTORY_PATH, "pdf_generation", "html"
    )

    @classmethod
    def init(cls) -> None:
        cls.input_metadata_directory_path = (
            VeritasFilePaths.output_metadata_directory_path
        )
        cls.output_pdf_directory_path = os.path.join(
            DefaultFileLocations.OUTPUT_DIRECTORY_PATH, "pdf_generation", "pdf"
        )
        cls.output_html_directory_path = os.path.join(
            DefaultFileLocations.OUTPUT_DIRECTORY_PATH, "pdf_generation", "html"
        )


@dataclass
class FinalMetadataFilePaths:

    output_metadata_directory_path: str = os.path.join(
        DefaultFileLocations.OUTPUT_DIRECTORY_PATH, "final", "metadata"
    )

    @classmethod
    def init(cls) -> None:
        cls.output_metadata_directory_path: str = os.path.join(
            DefaultFileLocations.OUTPUT_DIRECTORY_PATH, "final", "metadata"
        )


@dataclass
class ErrorAnnotatedDataFilePaths:
    output_error_annotated_directory_path: str = os.path.join(
        DefaultFileLocations.OUTPUT_DIRECTORY_PATH,
        "veritas",
        "quality_files",
        "error_annotated_data",
    )

    @classmethod
    def init(cls) -> None:
        cls.output_error_annotated_directory_path: str = os.path.join(
            DefaultFileLocations.OUTPUT_DIRECTORY_PATH,
            "veritas",
            "quality_files",
            "error_annotated_data",
        )


class MetadataGenerationSettings:

    def __init__(self):
        self.dataset_identifier = None
        self.file_extension = ".csv"
        self.delimiter = ","
        self.use_annotations = False
