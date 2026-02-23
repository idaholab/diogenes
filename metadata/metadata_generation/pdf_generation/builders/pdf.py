# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from datetime import date

from ...utils.file_parsing import MetadataParser, MetadataTableParser
from ...utils.file_writer import PDFGenerationFileWriter

from ...pdf_generation.builders.html import HTMLBuilder


class PDFBuilder: 

    def __init__(self, metadata):
        self.__html_builder = HTMLBuilder()
        self.__metadata = metadata

    def add_title_page(self):
        metadata_parser = MetadataParser(self.__metadata)
        data_set_title = metadata_parser.get_data_set_value('name')
        metadata_authors = metadata_parser.get_data_set_value('authors')
        metadata_modified_date = metadata_parser.get_data_set_value('modified').split(' ')[0]
        self.__html_builder.append_html_header_information(data_set_title)
        generated_date = date.today()
        self.__html_builder.append_title_page(data_set_title, metadata_authors, metadata_modified_date, generated_date)

    def add_title_supplement_page(self):
        metadata_parser = MetadataParser(self.__metadata)        
        data_set_title = metadata_parser.get_data_set_value('name')
        data_set_description = metadata_parser.get_data_set_value('description')
        self.__html_builder.append_title_supplement(data_set_title, data_set_description, self.__metadata)

    def add_table_pages(self, current_table_index, metadata_iterator):
        metadata_table_parser = MetadataTableParser(self.__metadata, current_table_index)
        table_name = metadata_table_parser.get_table_value('name')
        if metadata_table_parser.in_table_values('description'):
            description = metadata_table_parser.get_table_value('description')
        else:
            description = None
        row_count = metadata_table_parser.get_table_value('count')
        self.__html_builder.append_table(table_name, description, row_count, self.__metadata, current_table_index, metadata_iterator)
    
    def add_table_attributes(self, metadata_iterator):
        self.__livewire_pdf.add_cell('Attributes', text_styling='B', size=14, line_break_height=10)

    def add_attributes(self, metadata_iterator, current_table_index, add_page=False):
        if add_page == True:
            self.__livewire_pdf.add_page()
        
        self.__livewire_pdf.add_cell('Attributes', self.__table_headings_format)
        data_quality_pdf_table_builder = PDFTableBuilder(self.__livewire_pdf, self.__metadata, 'attributes', current_table_index, metadata_iterator)
        data_quality_pdf_table_builder.render_table_header()
        data_quality_pdf_table_builder.render_table()
        self.__livewire_pdf.ln()

    def print(self, metadata_file_name, error_when_file_exists, ignore_bad_chars_in_output):
        pdf_html = self.__html_builder.get_html()
        pdf_generation_file_writer = PDFGenerationFileWriter(error_when_file_exists, ignore_bad_chars_in_output)
        pdf_generation_file_writer.write_pdf(metadata_file_name, pdf_html)
        pdf_generation_file_writer.write_html(metadata_file_name, pdf_html)

        
        
