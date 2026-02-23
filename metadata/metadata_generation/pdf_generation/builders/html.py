# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os, copy, base64

from ...pdf_generation.factories.html_table import HTMLTableFactory

ABSOLUTE_FILE_PATH = os.getcwd()

class HTMLBuilder:

    FONT_LINK = "https://fonts.googleapis.com/css?family=IBM+Plex+Sans:400,400i,700|IBM+Plex+Sans+Condensed:400|IBM+Plex+Serif:400,700&display=swap"
    CSS_FILE_PATH = ABSOLUTE_FILE_PATH + "/_assets/livewire-dictionary.css"
    BANNER_FILE_PATH = ABSOLUTE_FILE_PATH + "/_assets/livewire-logo.png"
    FAQ_LINK = "https://livewire.energy.gov/faq"

    def __init__(self):
        self.__html_table_factory = HTMLTableFactory()
        self.__html = ""

    def append_html_header_information(self, data_set_title):
        title = "Livewire Data Platform: Data Dictionary -- " + data_set_title
        self.__html += "<!DOCTYPE html>\
                      \n<html>\
                      \n <head>\
                      \n   <meta charset=\"utf-8\">\
                      \n   <title>\
                      \n     {}\
                      \n   </title>\
                      \n   <style>\
                      \n        body {{ font-family: \"IBM Plex Sans\"; }}\
                      \n\
                      \n        div.section {{ break-after: always; page-break-after: always; }}\
                      \n        div.title-page header {{ margin: 0; padding: 13px; background-color: #262626; }}\
                      \n\
                      \n        h1, h2, h3, h4 {{ font-family: \"IBM Plex Serif\";}}\
                      \n        h3.object {{ break-before: always; page-break-before: always; }}\
                      \n\
                      \n        dt {{ font-weight: 700; }}\
                      \n\
                      \n        table {{ min-width: 67%; border-bottom: 1px solid #e0e0e0; font-size: 85%; }}\
                      \n        tr:nth-child(even) {{ background-color: #f8f8f8; }}\
                      \n        tr.summary, tr.summary td {{ border-top: 1px solid #e0e0e0; font-weight: bold; }}\
                      \n        th {{ background-color: #e8e8e8; }}\
                      \n        th, td {{ padding: 0.2em 0.67em; }}\
                      \n        td {{ vertical-align: top; font-family: \"IBM Plex Sans Condensed\"; }}\
                      \n        td.dq-metric-name {{ white-space: nowrap; }}\
                      \n        td.type {{ white-space: nowrap; }}\
                      \n        td.value {{ text-align: right; white-space: nowrap; }}\
                      \n        td.fd-header {{ text-align: center; }}\
                      \n        p.notes {{ font-family: \"IBM Plex Sans Condensed\"; font-size: 85%; }}\
                      \n\
                      \n        @media screen {{\
                      \n        body {{ margin: 3em; }}\
                      \n        }}\
                      \n\
                      \n        @media print {{\
                      \n        body {{ margin: 1em; }}\
                      \n        }}\
                      \n   </style>\
                      \n   </head>\n".format(title)            

        print(title)
                            
    def append_title_page(self, data_set_title, authors, modified_date_time, generated_date):
        with open(self.BANNER_FILE_PATH, "rb") as img:
            base64_LW_img_string = base64.b64encode(img.read()).decode('utf-8')

        self.__html += " <body>\
                      \n   <div class=\"section title-page\">\
                      \n     <header>\
                      \n       <img src=\"data:image/jpeg;base64, {}\" alt=\"Description of Image\">\
                      \n     </header>\
                      \n     <h1>Livewire Data Platform: Data Dictionary</h1>\
                      \n     <h2>{}</h2>\
                      \n     <dl>\
                      \n       <dt>Authors</dt>\
                      \n       <dd>{}</dd>\
                      \n       <dt>Modified</dt>\
                      \n       <dd>{}</dd>\
                      \n       <dt>Generated</dt>\
                      \n       <dd>{}</dd>\
                      \n     </dl>\
                      \n   </div>\n".format(base64_LW_img_string, data_set_title, authors, modified_date_time, generated_date)

    def append_title_supplement(self, data_set_title, description, metadata):
        self.__html += "   <div class=\"section\">\
                      \n     <h1>Livewire Data Platform: Data Dictionary</h1>\
                      \n     <h2>{}</h2>\
                      \n     <p class=\"description\">\
                      \n      {}\
                      \n     </p>\
                      \n     <h3>Data Quality Summary</h3>\n".format(data_set_title, description)
        data_quality_summary_html = self.__html_table_factory.create_data_quality_summary_table_html(metadata)
        self.__html += data_quality_summary_html
        self.__html += "     <p class=\"see-also\">\
                      \n       For more information on how the Livewire Data Platform project characterizes dataset quality, see the Livewire Data\
                      \n       Platform's Frequently Asked Questions (<a href=\"{}\">{})</a>.\
                      \n     </p>\
                      \n   </div>\
                      \n </body>\
                      \n</html>".format(self.FAQ_LINK, self.FAQ_LINK)

    def append_table(self, table_name, description, count, metadata, current_table_index, metadata_iterator): 
        self.__html += "     <h3 class=\"object\">{}</h3>\n".format(table_name)
        if description != None:
            self.__html += "     <dl class=\"object\">\
                           \n       <dt>Description</dt>\
                           \n       <dd>{}\n".format(description)
            self.__html += "        <dt>Count</dt>\
                           \n       <dd>{} rows/instances</dd>\
                           \n    </dl>\n".format(count)
        self.__html += "   \n<h4>Table Data Quality Summary</h4>\n"
        table_data_quality_summary_html = self.__html_table_factory.create_data_quality_summary_table_html(metadata, current_table_index)
        self.__html += table_data_quality_summary_html
        primary_key_html = self.__html_table_factory.create_primary_keys_table(metadata, current_table_index)
        if primary_key_html != None:
            self.__html += "   \n<h4>Primary Keys</h4>\n"
            self.__html += primary_key_html
        foreign_key_html = self.__html_table_factory.create_foreign_keys_table(metadata, current_table_index)
        if foreign_key_html != None:
            self.__html += "   \n<h4>Foreign Keys</h4>\n"
            self.__html += "   <p class=\"warn\"> \
                                <strong><em>IMPORTANT</em></strong>: \"Key #\" does not correspond to \"keyID\" in the JSON version of the metadata. \n\n \
                               </p>" 
            self.__html += foreign_key_html
        self.__html += "     <h4>Attributes</h4>\n"
        table_attributes_html = self.__html_table_factory.create_attributes_table_html(metadata, current_table_index, metadata_iterator)
        self.__html += table_attributes_html
        self.__html += "     <h4>Data Quality Measures</h4>\n"
        table_data_quality_measures_html = self.__html_table_factory.create_data_quality_measures_table_html(metadata, current_table_index, metadata_iterator)
        self.__html += table_data_quality_measures_html

    def render_table(self, table_line_break_height=1):
        self.__livewire_pdf.ln(table_line_break_height)

    def get_html(self):
        return copy.deepcopy(self.__html)

 


