# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os
import json

from playwright.sync_api import sync_playwright

from datetime import datetime

from ..settings import VERITAS_VERSION, VeritasFilePaths, PDFGenerationFilePaths, FinalMetadataFilePaths

from ..utils.file_system_tools import InputFilePathFinder, DirectoryCreator, load_json, get_file_name_from_path
from ..utils.file_iterator import MetadataIterator
from ..utils.file_parsing import MetadataTableParser

from ..veritas.scorecard_distillation.scorecard_distiller import DataQuality, DatasetQualityCharacterization


class VeritasFileWriter():

    def __init__(self, input_metadata_file_path, error_when_file_exists):
        directory_creator = DirectoryCreator(error_when_file_exists)
        directory_creator.create_directory(VeritasFilePaths.output_metadata_directory_path)
        self.__metadata = load_json(input_metadata_file_path)        
        directory_creator.create_directory(VeritasFilePaths.output_quality_files_directory_path)

    def write_rules(self, rule_book, write_inactive_rules=True):
        with open(VeritasFilePaths.output_quality_files_directory_path + '/rules.csv', 'w+') as rules_file:
            rules_file.write('rule_id,table_name,attribute_name,is_active,rule_description\n')

            for codependent_rule_group in rule_book.iterate_codependent_rule_groups(write_inactive_rules):
                for rule in codependent_rule_group.iterate(write_inactive_rules):
                    csv_rule = rule.format_rule_as_csv()
                    rules_file.write(csv_rule)
            for independent_rule in rule_book.iterate_independent_rules(write_inactive_rules):
                csv_rule = independent_rule.format_rule_as_csv()
                rules_file.write(csv_rule)

    def write_error_catalog(self, error_tables):
        error_tables.print_to_csv(VeritasFilePaths.output_quality_files_directory_path)
    
    def write_json(self, data_quality_characterization: DatasetQualityCharacterization, input_metadata_file_path: str) -> None:
        JSON_writer = JSONWriter(self.__metadata)
        metadata_iterator = MetadataIterator(self.__metadata)
        for table_index in metadata_iterator.iterate_table():
            metadata_table_parser = MetadataTableParser(self.__metadata, table_index)
            table_name = metadata_table_parser.get_table_value('name')
            table_data_quality = data_quality_characterization.get_data_quality_for_table(table_name)
            JSON_writer.add_table_data_quality(table_data_quality, table_index)
        JSON_writer.add_dataset_data_quality(data_quality_characterization.dataset_data_quality)
        input_metadata_file_name = get_file_name_from_path(input_metadata_file_path)
        output_metadata_file_path = VeritasFilePaths.output_metadata_directory_path + '/' + input_metadata_file_name 
        JSON_writer.write_json(output_metadata_file_path)        


class PDFGenerationFileWriter():

    def __init__(self, error_when_file_exists, ignore_bad_chars_in_output):
        self.__directory_creator = DirectoryCreator(error_when_file_exists)
        if ignore_bad_chars_in_output == True:
            self.__error_handling = 'ignore'
        else:
            self.__error_handling = 'strict'

        """ def write_pdf(self, metadata_file_path, pdf_html):
        self.__directory_creator.create_directory(PDFGenerationFilePaths.output_pdf_directory_path)
        output_pdf_file_path = PDFGenerationFilePaths.output_pdf_directory_path + '/' + FileNamer.get_pdf_file_name(metadata_file_path)
        pdfkit.from_string(pdf_html, output_pdf_file_path,
                           options={'--enable-local-file-access': True, '--footer-center': '[page] of [topage]', '--footer-font-name': 'IBM Plex Sans Condensed', '--footer-font-size': 8})
 """
    def write_pdf(self, metadata_file_path, pdf_html):

        self.__directory_creator.create_directory(PDFGenerationFilePaths.output_pdf_directory_path)
        output_pdf_file_path = PDFGenerationFilePaths.output_pdf_directory_path + '/' + FileNamer.get_pdf_file_name(metadata_file_path)    
        
        with sync_playwright() as p:

            browser = p.chromium.launch(args=["--enable-local-file-accesses","--allow-file-access-from-files"])
            context = browser.new_context()
            page = context.new_page()

            # Set the content of the page
            page.set_content(pdf_html, wait_until="networkidle")

            footer_template = """
            <style>
                .footer {
                    font-family: 'IBM Plex Sans Condensed';
                    font-size: 8px;
                    text-align: center;
                    width: 100%;
                    margin: 0 auto;
                    color: #000;
                }
            </style>
            <div class='footer'>
                <span class='pageNumber'></span> of <span class='totalPages'></span>
            </div>
            <script>
                (function() {
                    var pageNumber = document.querySelector('.pageNumber');
                    var totalPages = document.querySelector('.totalPages');
                    pageNumber.textContent = window.pageNumber;
                    totalPages.textContent = window.totalPages;
                })();
            </script>
            """

            # Convert the page to PDF
            page.pdf(
                path=output_pdf_file_path,
                print_background=True,
                format="Letter",
                display_header_footer = True,
                footer_template=footer_template,
                margin={"top": "20px", "bottom": "40px"}
            )
            browser.close()

 
    def write_html(self, metadata_file_path, pdf_html):
        self.__directory_creator.create_directory(PDFGenerationFilePaths.output_html_directory_path)
        output_html_file_path = PDFGenerationFilePaths.output_html_directory_path + '/' + FileNamer.get_pdf_file_name(metadata_file_path, '.html')
        with open(output_html_file_path, 'w+', errors=self.__error_handling) as html_file_handle:
            html_file_handle.write(pdf_html)


class JSONWriter:

    def __init__(self, metadata):
        self.__metadata = metadata

    def add_dataset_data_quality(self, data_quality: DataQuality) -> None:
        ordered_dataset_metadata = {}
        ordered_dataset_metadata['conformsTo'] = 'https://livewire.energy.gov/api/schemas/dictionary/dictionary.json'
        ordered_dataset_metadata['name'] = self.__metadata['name']
        if 'description' in self.__metadata.keys():
            ordered_dataset_metadata['description'] = self.__metadata['description']
        ordered_dataset_metadata['modified'] = str(datetime.now())
        ordered_dataset_metadata['version'] = VERITAS_VERSION
        ordered_dataset_metadata['authors'] = 'Livewire Data Platform'
        ordered_dataset_metadata['dataQualitySummary'] = self._dataset_data_quality_json(data_quality, 
                                                                                         self.__metadata['referenceURL'])
        ordered_dataset_metadata['objects'] = self.__metadata['objects']
        self.__metadata = ordered_dataset_metadata

    def add_table_data_quality(self, data_quality: DataQuality, table_index: int) -> None:
        ordered_table_metadata = {}
        ordered_table_metadata['name'] = self.__metadata['objects'][table_index]['name']
        if 'description' in self.__metadata['objects'][table_index].keys(): 
            ordered_table_metadata['description'] =  self.__metadata['objects'][table_index]['description'] 
        ordered_table_metadata['type'] = self.__metadata['objects'][table_index]['type']
        ordered_table_metadata['count'] = self.__metadata['objects'][table_index]['count']
        if 'relationships' in self.__metadata['objects'][table_index].keys():
            ordered_table_metadata['relationships'] = self.__metadata['objects'][table_index]['relationships']
        ordered_table_metadata['dataQualitySummary'] = self._data_quality_json(data_quality)
        ordered_table_metadata['attributes'] = self.__metadata['objects'][table_index]['attributes'] 
        self.__metadata['objects'][table_index] = ordered_table_metadata

    def write_json(self, output_json_file_path: str) -> None:
        with open(output_json_file_path + '.json', 'w+') as json_file_handle:
            json.dump(self.__metadata, json_file_handle, indent=2)

    def _data_quality_json(self, data_quality: DataQuality) -> dict:
        data_quality_summary = {
            'measures' : [
                { 'name' : 'Error Affected Records/Rows', 'value' : data_quality.percent_error_affected, 'units' : '%', 'notes' : str(round(data_quality.error_affected_count)) + ' records/rows'},
                { 'name' : 'Erroneous Records/Rows', 'value' : data_quality.percent_erroneous, 'units' : '%', 'notes' : str(round(data_quality.erroneous_count)) + ' records/rows'},
                { 'name' : 'Missing Records/Rows', 'value' : data_quality.percent_missing, 'units' : '%', 'notes' : str(round(data_quality.missing_count)) + ' records/rows'},
                { 'name' : 'Completeness Metric', 'value' : data_quality.completeness, 'units' : '%', 'showAsGraphic' : True, 'graphicLegend' : 'Completeness'},
                { 'name' : 'Accuracy Metric', 'value' : data_quality.accuracy, 'units' : '%', 'showAsGraphic' : True, 'graphicLegend' : 'Accuracy'},
                { 'name' : 'Overall Quality Metric', 'value' : data_quality.percent_overall, 'units' : '%'}
            ]
        }
        return data_quality_summary
    
    def _dataset_data_quality_json(self, data_quality: DataQuality, reference_URL: str) -> dict:
        data_quality_summary = self._data_quality_json(data_quality)
        data_quality_summary['referenceURL'] = reference_URL
        data_quality_summary['measures'][-1]['showAsGraphic'] = True
        data_quality_summary['measures'][-1]['showAsSummary'] = True
        data_quality_summary['measures'][-1]['graphicLegend'] = 'Overall'
        return data_quality_summary


class FinalMetadataWriter:

    def __init__(self, error_when_file_exists, ignore_bad_chars_in_output):
        input_file_path_finder = InputFilePathFinder()
        self.__metadata_file_path = input_file_path_finder.get_metadata_file_path(VeritasFilePaths.output_metadata_directory_path)
        self.__metadata = load_json(self.__metadata_file_path)
        directory_creator = DirectoryCreator(error_when_file_exists)
        directory_creator.create_directory(FinalMetadataFilePaths.output_metadata_directory_path)
        if ignore_bad_chars_in_output == True:
            self.__error_handling = 'ignore'
        else:
            self.__error_handling = 'strict'

    def write_metadata_with_url(self):
        partial_url = self.__metadata['dataQualitySummary']['referenceURL']
        partial_url_no_placeholder = os.path.dirname(partial_url)
        self.__metadata['dataQualitySummary']['referenceURL'] = partial_url_no_placeholder + '/' + FileNamer.get_pdf_file_name(self.__metadata_file_path)
        metadata_file_name = get_file_name_from_path(self.__metadata_file_path)
        output_metadata_file_path = FinalMetadataFilePaths.output_metadata_directory_path + '/' + metadata_file_name + '.json'
        with open(output_metadata_file_path, 'w+', errors=self.__error_handling) as metadata_file_handle:
            json.dump(self.__metadata, metadata_file_handle, indent=2)

    def write_data_quality_excerpt(self):
       data_quality_excerpt = {}
       data_quality_excerpt['dataQualitySummary'] = self.__metadata['dataQualitySummary']
       metadata_file_name = get_file_name_from_path(self.__metadata_file_path)
       output_excerpt_file_path = FinalMetadataFilePaths.output_metadata_directory_path + '/' + metadata_file_name + '.summary.json'
       with open(output_excerpt_file_path, 'w+', errors=self.__error_handling) as excerpt_file_handle:
           json.dump(data_quality_excerpt, excerpt_file_handle, indent=2)
    

class FileNamer:

    @classmethod
    def get_pdf_file_name(cls, metadata_file_path, extension='.pdf'):
        metadata_file_name = get_file_name_from_path(metadata_file_path)
        return 'dictionary-' + metadata_file_name + extension