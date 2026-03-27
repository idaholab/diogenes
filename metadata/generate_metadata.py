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
    import os
    import sys
    import datetime

    parser = argparse.ArgumentParser(description='Generate Low Level Metadata (LLMD) for Livewire Project')

    # Project / dataset shortcuts (mirrors example_main.py)
    parser.add_argument('-proj', '--project', help="Project name (used with --dataset to auto-construct input/output paths)", type=str, required=False)
    parser.add_argument('-ds', '--dataset', help="Dataset ID (used with --project to auto-construct paths; also used as identifier when --identifier is omitted)", type=str, required=False)

    parser.add_argument('-id', '--identifier', help="The name of the dataset's identifier in the partial metadata (defaults to --dataset when --project/--dataset are used)", type=str, required=False)
    parser.add_argument('-ext', '--file_extension', help="The type of extension for the file (.txt,.csv,etc...)", type=str, default='.csv')
    parser.add_argument('-d', '--delimiter', help="File delimiter", type=str, default=',')
    parser.add_argument('-m', '--mode', help="Full data quality analysis (full or f) or scorecard distillation (distill or d) from error catalog", default='f')
    parser.add_argument('-to_veritas', '--skip_to_veritas', help="Skip low-level metadata creation and process data quality immediately", default='false')
    parser.add_argument('-to_schema', '--skip_to_schema_validation', help="Skip LLMD, data quality, and validate LLMD from schema immediately", default='false')
    parser.add_argument('-to_pdf', '--skip_to_pdf_generation', help="Skip LLMD, data quality, schema validation, and create pdf immediately", default='false')
    parser.add_argument('-files_exist_error', '--files_exist_error', help="Raise an error if output files exist", default='false')
    parser.add_argument('-ignore_chars', '--ignore_bad_chars', help="true=Ignore bad characters and print them. false=Throw an error when attempting to print a bad character", default='false')
    parser.add_argument('-i', '--input_path', help="Path to Input Directory (overridden by --project/--dataset if both are set)", default=None, required=False)
    parser.add_argument('-o', '--output_path', help="Path to Output Directory (overridden by --project/--dataset if both are set)", default=None, required=False)
    parser.add_argument("-n", "--n_rows", help="Max Row Count", default=-1, required=False)
    parser.add_argument("-p", "--processes", help="Number of Processes to spawn for Sampling", default=1, required=False)
    parser.add_argument("-a", "--annotations", help="Use manual annotations, no inference.", default='False', required=False)

    # Annotation tool options
    parser.add_argument('--run_annotations', help="Run the annotation tool before metadata generation", action='store_true', default=False)
    parser.add_argument('--annotation_agent', help="Annotation agent type (none, tree, ml_tree, tree2prob)", type=str, default='tree2prob')
    parser.add_argument('--annotation_mode', help="How to handle existing annotation files: 'copy' renames them with a timestamp, 'overwrite' replaces them in place", choices=['copy', 'overwrite'], default='copy')

    args = parser.parse_args()

    # Resolve project root (one level above this file: diogenes/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Build paths from --project / --dataset when provided
    if args.project and args.dataset:
        input_base_folder  = os.path.abspath(args.input_path) if args.input_path else project_root
        output_base_folder = os.path.abspath(args.output_path) if args.output_path else project_root
        input_folder = os.path.join(input_base_folder, args.project, args.dataset)
        output_path  = os.path.join(output_base_folder, args.project, args.dataset)
        description_path = os.path.join(input_base_folder, args.project, 'descriptive_information', 'descriptions.csv')
        identifier = args.identifier or args.dataset
    else:
        if not args.identifier:
            parser.error("--identifier is required when --project/--dataset are not both provided")
        input_folder     = args.input_path or '/'
        output_path      = args.output_path or '/'
        description_path = os.path.join(input_folder, '..', 'descriptive_information', 'descriptions.csv')
        identifier       = args.identifier

    # Normalise description_path (may not exist)
    description_path = os.path.normpath(description_path)
    if not os.path.exists(description_path):
        description_path = None

    # Annotation tool
    if args.run_annotations:
        # Ensure annotation_tool package is importable
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from annotation_tool.start import start_annotation

        annotations_xlsx = os.path.join(input_folder, 'descriptive_information', 'annotations.xlsx')
        annotations_txt  = os.path.join(input_folder, 'descriptive_information', 'annotations.txt')

        if args.annotation_mode == 'copy':
            stamp = datetime.datetime.now().strftime("%m%d%y%H%M")
            if os.path.exists(annotations_xlsx):
                os.rename(annotations_xlsx, os.path.join(input_folder, 'descriptive_information', f'annotations_{stamp}.xlsx'))
            if os.path.exists(annotations_txt):
                os.rename(annotations_txt, os.path.join(input_folder, 'descriptive_information', f'annotations_{stamp}.txt'))
        else:  # overwrite: delete existing files so Annotator doesn't raise on them
            if os.path.exists(annotations_xlsx):
                os.remove(annotations_xlsx)
            if os.path.exists(annotations_txt):
                os.remove(annotations_txt)

        start_annotation(
            tree=args.annotation_agent,
            output=os.path.join(input_folder, 'descriptive_information'),
            desc=description_path,
            counts=True,
            input=os.path.join(input_folder, 'data'),
        )
    elif not os.path.exists(os.path.join(input_folder, 'descriptive_information', 'annotations.xlsx')):
        response = input("No annotations.xlsx found. Would you like to generate one now? (y/n): ").strip().lower()
        if response == 'y':
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            from annotation_tool.start import start_annotation
            start_annotation(
                tree=args.annotation_agent,
                output=os.path.join(input_folder, 'descriptive_information'),
                desc=description_path,
                counts=True,
                input=os.path.join(input_folder, 'data'),
            )
        else:
            print("Proceeding without annotations.")

    run_metadata_generation(
        identifier=identifier,
        file_extension=args.file_extension,
        delimiter=args.delimiter,
        mode=args.mode,
        skip_to_veritas=args.skip_to_veritas,
        skip_to_schema_validation=args.skip_to_schema_validation,
        skip_to_pdf_generation=args.skip_to_pdf_generation,
        files_exist_error=args.files_exist_error,
        ignore_bad_chars=args.ignore_bad_chars,
        input_path=input_folder,
        output_path=output_path,
        n_rows=args.n_rows,
        processes=args.processes,
        annotations=args.annotations,
    )


if __name__ == '__main__':
    main()