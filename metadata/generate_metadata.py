# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import argparse

if __name__ == '__main__':
    from metadata_generation.utils.datatype_conversion import convert_string_to_bool
    from metadata_generation.utils.file_writer import FinalMetadataWriter
    from metadata_generation.settings import *

    from metadata_generation.metadata_generation_input import MetadataGenerationInput
    from metadata_generation.insight.factory import llmd_factory
    from metadata_generation.veritas.api.drivers import FullAnalysisDriver, DistillationDriver
    from metadata_generation.json_schema_validation.json_schema_validator import JsonSchemaValidator
    from metadata_generation.pdf_generation.api.api import PDFGenerator
else:
    from .metadata_generation.utils.datatype_conversion import convert_string_to_bool
    from .metadata_generation.utils.file_writer import FinalMetadataWriter
    from .metadata_generation.settings import *

    from .metadata_generation.metadata_generation_input import MetadataGenerationInput
    from .metadata_generation.insight.factory import llmd_factory
    from .metadata_generation.veritas.api.drivers import FullAnalysisDriver, DistillationDriver
    from .metadata_generation.json_schema_validation.json_schema_validator import JsonSchemaValidator
    from .metadata_generation.pdf_generation.api.api import PDFGenerator


def run_metadata_generation(
    identifier,
    file_extension='.csv',
    delimiter=',',
    mode='f',
    skip_to_veritas='false',
    skip_to_schema_validation='false',
    skip_to_pdf_generation='false',
    files_exist_error='false',
    ignore_bad_chars='false',
    input_path='/',
    output_path='/',
    n_rows=-1,
    processes=1,
    annotations='False'
):
    """
    Generate Low Level Metadata (LLMD) for Livewire Project.
    
    Args:
        identifier (str): The name of the dataset's identifier in the partial metadata
        file_extension (str): The type of extension for the file (.txt,.csv,etc...)
        delimiter (str): File delimiter
        mode (str): Full data quality analysis ('full' or 'f') or scorecard distillation ('distill' or 'd')
        skip_to_veritas (str): Skip low-level metadata creation and process data quality immediately
        skip_to_schema_validation (str): Skip LLMD, data quality, and validate LLMD from schema immediately
        skip_to_pdf_generation (str): Skip LLMD, data quality, schema validation, and create pdf immediately
        files_exist_error (str): Raise an error if output files exist
        ignore_bad_chars (str): Ignore bad characters and print them vs throw error
        input_path (str): Path to Input Directory
        output_path (str): Path to Output Directory
        n_rows (int): Max Row Count
        processes (int): Number of Processes to spawn for Sampling
        annotations (str): Use manual annotations, no inference
    """

    settings = MetadataGenerationSettings()
    settings.dataset_identifier = identifier
    settings.file_extension = file_extension
    settings.delimiter = delimiter

    settings.input_path = input_path
    settings.n_rows = int(n_rows)
    settings.output_path = output_path
    settings.processes = int(processes)

    file_locs = DefaultFileLocations()
    file_locs.set_input(settings.input_path, settings.n_rows, settings.processes)
    file_locs.set_output(settings.output_path)
    InsightFilePaths().init()
    VeritasFilePaths().init()
    PDFGenerationFilePaths().init()
    FinalMetadataFilePaths().init()
    ErrorAnnotatedDataFilePaths().init()

    skip_to_veritas_bool = convert_string_to_bool(skip_to_veritas)
    skip_to_schema_validation_bool = convert_string_to_bool(skip_to_schema_validation)
    skip_to_pdf_creation_bool = convert_string_to_bool(skip_to_pdf_generation)

    error_when_files_exist = convert_string_to_bool(files_exist_error)

    metadata_generation_input = MetadataGenerationInput(settings)

    if skip_to_veritas_bool == skip_to_schema_validation_bool == skip_to_pdf_creation_bool == False:
        llmd_factory.create_llmd(metadata_generation_input, use_annotations=convert_string_to_bool(annotations))
    if skip_to_schema_validation_bool == skip_to_pdf_creation_bool == False:
        if mode == 'full' or mode == 'f':
            full_analysis_driver = FullAnalysisDriver()
            full_analysis_driver.set_input_file_paths()
            full_analysis_driver.set_veritas_file_writer(error_when_files_exist)
            full_analysis_driver.generate_data_quality_rules(metadata_generation_input)
            full_analysis_driver.execute_rules(metadata_generation_input)
            full_analysis_driver.distill_data_quality_characterization(metadata_generation_input)
        elif mode == 'distill' or mode == 'd':
            distillation_driver = DistillationDriver()
            distillation_driver.set_distillation_file_paths()
            distillation_driver.distill_scorecard_from_error_catalog()
        else:
            print("Mode not recognized: '{}'".format(mode))
    if skip_to_pdf_creation_bool == False:
        json_schema_validator = JsonSchemaValidator()
        json_schema_validator.validate_json_schema()
            
    ignore_bad_chars_in_output = convert_string_to_bool(ignore_bad_chars)

    pdf_generator = PDFGenerator()
    pdf_generator.generate_pdf_from_json(error_when_files_exist, ignore_bad_chars_in_output)   

    final_metadata_writer = FinalMetadataWriter(error_when_files_exist, ignore_bad_chars_in_output)
    final_metadata_writer.write_metadata_with_url()
    final_metadata_writer.write_data_quality_excerpt()

def main():
    
    parser = argparse.ArgumentParser(description='Generate Low Level Metadata (LLMD) for Livewire Project')
    parser.add_argument('-id', '--identifier', help="The name of the dataset's identifier in the partial metadata", type=str, required=True)
    parser.add_argument('-ext', '--file_extension', help="The type of extension for the file (.txt,.csv,etc...)", type=str, default='.csv')
    parser.add_argument('-d', '--delimiter', help="File delimiter", type=str, default=',')
    parser.add_argument('-m', '--mode', help="Full data quality analysis (full or f) or scorecard distillation (distill or d) from error catalog", default='f')
    parser.add_argument('-to_veritas', '--skip_to_veritas', help="Skip low-level metadata creation and process data quality immediately", default='false')
    parser.add_argument('-to_schema', '--skip_to_schema_validation', help="Skip LLMD, data quality, and validate LLMD from schema immediately", default='false')
    parser.add_argument('-to_pdf', '--skip_to_pdf_generation', help="Skip LLMD, data quality, schema validation, and create pdf immediately", default='false')
    parser.add_argument('-files_exist_error', '--files_exist_error', help="Raise an error if output files exist", default='false')
    parser.add_argument('-ignore_chars', '--ignore_bad_chars', help="true=Ignore bad characters and print them. false=Throw an error when attempting to print a bad character", default='false')
    parser.add_argument('-i', '--input_path', help="Path to Input Directory", default="/", required=False)
    parser.add_argument('-o', '--output_path', help="Path to Output Directory", default="/", required=False)
    parser.add_argument("-n", "--n_rows", help="Max Row Count", default=-1, required=False)
    parser.add_argument("-p", "--processes", help="Number of Processes to spawn for Sampling", default=1, required=False)
    parser.add_argument("-a", "--annotations", help="Use manual annotations, no inference.", default='False', required=False)
    args = parser.parse_args()

    run_metadata_generation(
        identifier=args.identifier,
        file_extension=args.file_extension,
        delimiter=args.delimiter,
        mode=args.mode,
        skip_to_veritas=args.skip_to_veritas,
        skip_to_schema_validation=args.skip_to_schema_validation,
        skip_to_pdf_generation=args.skip_to_pdf_generation,
        files_exist_error=args.files_exist_error,
        ignore_bad_chars=args.ignore_bad_chars,
        input_path=args.input_path,
        output_path=args.output_path,
        n_rows=args.n_rows,
        processes=args.processes,
        annotations=args.annotations
    )


if __name__ == '__main__':
    main()