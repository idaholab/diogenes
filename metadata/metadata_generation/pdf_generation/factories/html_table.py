# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from dataclasses import dataclass

from ...veritas.datatypes import DataQualityClassEnum
from ...pdf_generation.datatypes import JSONIndex 
from ...utils.file_parsing import  MetadataDataQualityParser, MetadataDataQualityMetricParser
from ...utils.file_parsing import MetadataAttributeParser, MetadataTableParser

import re

class HTMLTableFactory: 

    def __init__(self, category_show_limit=5):
        self.__category_show_limit = category_show_limit
        self.__value_formatter = ValueFormatter()

    def create_data_quality_summary_table_html(self, metadata, current_table_index=None):
        column_names = ['Quality Measure', 'Value', 'Notes']
        header_column_spans = [None, 2, None]
        number_of_data_columns = 4
        html_table_builder = HTMLTableBuilder(number_of_data_columns)
        html_table_builder.append_table_header(column_names, header_column_spans)

        metadata_data_quality_parser = MetadataDataQualityParser(metadata, current_table_index)
        data_quality_json = metadata_data_quality_parser.get_data_quality_metrics()
        html_table_builder.append_start_of_table_body()
        for metric_index in range(len(data_quality_json)):
            html_table_builder.append_data_to_table(data_quality_json[metric_index]['name'])
            formatted_value_string = self.__value_formatter.format_extremely_precise_string(data_quality_json[metric_index]['value'])
            html_table_builder.append_data_to_table(formatted_value_string, cell_class='value')
            html_table_builder.append_data_to_table('%')
            if metadata_data_quality_parser.metric_has_notes(data_quality_json[metric_index]['name']):
                notes = data_quality_json[metric_index]['notes']
                # Changed to regex to handle different cases
                result = re.search(r"([0-9]+)", notes)
                value_in_notes = float(result.group(1))
                formatted_value = self.__value_formatter.format_numeric_value(value_in_notes)
                html_table_builder.append_data_to_table(formatted_value + ' records/rows')
            else:
                html_table_builder.append_data_to_table('')
        html_table_builder.append_close_of_table_body()
        html_table_builder.append_close_of_table()
        
        return html_table_builder.get_table_html()
    
    def create_primary_keys_table (self, metadata, current_table_index):  
        metadata_table_parser = MetadataTableParser(metadata, current_table_index)
        if not metadata_table_parser.in_table_values('relationships'): 
            return None
        if not metadata_table_parser.in_relationships('primaryKeys'): 
            return None
   
        primary_key_column_names = ['Name', 'Type']
        header_column_spans = [None, None]

        html_table_builder = HTMLTableBuilder(len(primary_key_column_names))
        html_table_builder.append_table_header(primary_key_column_names, header_column_spans)
        
        html_table_builder.append_start_of_table_body()
        
        for primary_key in metadata_table_parser.get_primary_keys():
            for index, attribute_name in enumerate(metadata_table_parser.attributes()):
                if attribute_name != primary_key:
                    continue
                type = metadata_table_parser.get_attribute_value(index, 'type')
                html_table_builder.append_data_to_table(primary_key)
                html_table_builder.append_data_to_table(type)
        html_table_builder.append_close_of_table_body()
        html_table_builder.append_close_of_table()

        if html_table_builder.is_empty_table(): 
            return None
        return html_table_builder.get_table_html()
    
    def create_foreign_keys_table (self, metadata, current_table_index):     
        metadata_table_parser = MetadataTableParser(metadata, current_table_index)
        if not metadata_table_parser.in_table_values('relationships'): 
            return None
        if not metadata_table_parser.in_relationships('refersToPrimaryKeyTables'): 
            return None
        primary_key_column_names = ['Key #', 'Foreign Key', 'Refers To Table', 'Refers to Attribute']
        header_column_spans = [None, None, None, None]

        html_table_builder = HTMLTableBuilder(len(primary_key_column_names))
        html_table_builder.append_table_header(primary_key_column_names, header_column_spans)
        
        html_table_builder.append_start_of_table_body()

        metadata_table_parser = MetadataTableParser(metadata, current_table_index)
        for key_num, key_table_reference in enumerate(metadata_table_parser.get_primary_key_table_references()):
            referenced_primary_key_table, key_ID = key_table_reference
            foreign_keys = metadata_table_parser.get_key_attributes(referenced_primary_key_table, key_ID, 'foreignKey')
            referenced_attributes = metadata_table_parser.get_key_attributes(referenced_primary_key_table, key_ID, 'foreignKeyRefersTo')            
            for foreign_key, referenced_attribute in zip(foreign_keys, referenced_attributes): 
                html_table_builder.append_data_to_table(key_num)
                html_table_builder.append_data_to_table(foreign_key)
                html_table_builder.append_data_to_table(referenced_primary_key_table)                
                html_table_builder.append_data_to_table(referenced_attribute)

        html_table_builder.append_close_of_table()

        if html_table_builder.is_empty_table(): 
            return None
        return html_table_builder.get_table_html()


    def create_attributes_table_html(self, metadata, current_table_index, metadata_iterator):
        column_names = ['Name', 'Type', 'Units', 'Description']
        header_column_spans = [None, None, None, None]

        html_table_builder = HTMLTableBuilder(len(column_names))
        html_table_builder.append_table_header(column_names, header_column_spans)

        html_table_builder.append_start_of_table_body()
        for current_attribute_index in metadata_iterator.iterate_attribute():
            metadata_attribute_parser = MetadataAttributeParser(metadata, JSONIndex(current_table_index, current_attribute_index))
            html_table_builder.append_data_to_table(metadata_attribute_parser.get_attribute_value('name'))
            html_table_builder.append_data_to_table(metadata_attribute_parser.get_attribute_value('type'))
            if metadata_attribute_parser.in_attribute_values('units'):
                html_table_builder.append_data_to_table(metadata_attribute_parser.get_attribute_value('units'))
            else:
                html_table_builder.append_data_to_table('n/a')
            if metadata_attribute_parser.in_attribute_values('description'):
                html_table_builder.append_data_to_table(metadata_attribute_parser.get_attribute_value('description'))
            else:
                html_table_builder.append_data_to_table('')
        
        html_table_builder.append_close_of_table_body()
        html_table_builder.append_close_of_table()
        
        return html_table_builder.get_table_html()

    def create_data_quality_measures_table_html(self, metadata, current_table_index, metadata_iterator):
        column_names = ['Applies&nbsp;To', 'Name', 'Value', 'Units', 'Description']
        header_column_spans = [None, None, None, None, 3]

        html_table_builder = HTMLTableBuilder(len(column_names))
        html_table_builder.append_table_header(column_names, header_column_spans)

        html_table_builder.append_start_of_table_body()
        for current_attribute_index in metadata_iterator.iterate_attribute():
            metadata_attribute_parser = MetadataAttributeParser(metadata, JSONIndex(current_table_index, current_attribute_index))
            if not metadata_attribute_parser.in_attribute_values('dataQuality'):
                continue
            current_applies_to_column_value = None
            for data_quality_metric in metadata_iterator.iterate_data_quality_metrics():
                metadata_data_quality_parser = MetadataDataQualityMetricParser(data_quality_metric)
                new_applies_to_column_value = metadata_attribute_parser.get_attribute_value('name')
                applies_to_column_value = self.__get_correct_applies_to_column_value(current_applies_to_column_value, new_applies_to_column_value)
                current_applies_to_column_value = new_applies_to_column_value
                html_table_builder.append_data_to_table(applies_to_column_value, cell_class='dq-metric-name')
                metric_name = metadata_data_quality_parser.get_data_quality_metric_value('name')
                html_table_builder.append_data_to_table(metric_name, cell_class='type')
                value = self.__value_formatter.format_numeric_value(metadata_data_quality_parser.get_data_quality_metric_value('value'), 3)
                html_table_builder.append_data_to_table(value, cell_class='value')
                html_table_builder.append_data_to_table(metadata_data_quality_parser.get_data_quality_metric_value('units'))
                html_table_builder.append_data_to_table(metadata_data_quality_parser.get_data_quality_metric_value('description'), column_span=3)
                if metric_name == 'Number of Categories':
                    frequency_table_html = self.create_frequency_table_html(metadata_iterator)
                    html_table_builder.append_html_directly(frequency_table_html)
        
        html_table_builder.append_close_of_table_body()
        html_table_builder.append_close_of_table()
        
        return html_table_builder.get_table_html()

    def __get_correct_applies_to_column_value(self, previous_applies_to_column_value, current_applies_to_column_value):
        if previous_applies_to_column_value == current_applies_to_column_value:
            applies_to_column_value = ""
        else:
            applies_to_column_value = current_applies_to_column_value

        return applies_to_column_value

    def create_frequency_table_html(self, metadata_iterator):
        column_names = ['', 'Distribution', 'Category', 'n', '%']
        header_column_spans = [None, 3, None, None, None]
        header_column_classes = [None, None, 'fd-header', 'fd-header', 'fd-header']

        html_table_builder = HTMLSubTableBuilder(4)
        html_table_builder.append_table_header(column_names, header_column_spans, header_column_classes)
        category_count = 0
        for (category_name, category_row_count, frequency_percentage) in metadata_iterator.iterate_categorical():
            if category_count < self.__category_show_limit:
                html_table_builder.append_data_to_table('', column_span=4)
                html_table_builder.append_data_to_table(category_name)
                html_table_builder.append_data_to_table(category_row_count, cell_class="value")
                html_table_builder.append_data_to_table(frequency_percentage, cell_class="value")
            
            category_count += 1
        
        sub_table_html = html_table_builder.get_table_html()
        number_of_categories_not_counted = category_count - self.__category_show_limit
        if 0 < number_of_categories_not_counted:
            sub_table_html += "       <tr>\
                                   \n   <td colspan=\"4\"></td>\
                                   \n   <td colspan=\"3\">({} additional categories not shown)</td>\
                                   \n </tr>".format(number_of_categories_not_counted)

        return sub_table_html


class ValueFormatter:

    def format_extremely_precise_string(self, value):
        formatted_value_string = str(round(value, 3))

        if (value != 0) and (value < 0.01):
            formatted_value_string = '< 0.01'
        elif (value != 100) and (value > 99.99):
            formatted_value_string = '> 99.99'
        else:
            formatted_value_string = str(round(value, 2)) 

        return formatted_value_string

    def format_numeric_value(self, value, rounding_precision=None, scientific_threshold=1e6):
        if isinstance(value, str):
            return value
        
        if value is None:
            return "N/A"
    
        formatted_value = value

        abs_value = abs(value)
        if abs_value >= scientific_threshold or (abs_value < 0.001 and abs_value != 0):
            return f"{value:.{rounding_precision if rounding_precision else 2}e}"
        
        if float(value).is_integer():
            formatted_value = int(value)
        else:
            formatted_value = round(formatted_value, rounding_precision)

        formatted_value = "{:,}".format(formatted_value)

        return formatted_value


class HTMLTableBuilder:

    def __init__(self, number_of_data_columns):
        self.__html = ""
        self.__number_of_data_columns = number_of_data_columns
        self.__row_position = 0

    def append_table_header(self, column_names, column_spans):
        assert len(column_names) == len(column_spans)
        self.__html += "     <table>\
                      \n       <thead>\
                      \n        <tr>\n"
        for (column_name, column_span) in zip(column_names, column_spans):
            html_table_attributes_string_builder = HTMLCellAttributesStringBuilder(column_span=column_span)
            attributes = html_table_attributes_string_builder.get_html_attributes_string()
            self.__html += "          <th{}>{}</th>\n".format(attributes, str(column_name))       
        self.__html += "        </tr>\
                      \n       </thead>\n"

    def append_start_of_table_body(self):
        self.__html += "       <tbody>\n"

    def append_data_to_table(self, data, column_span=None, cell_class=None):
        row_attributes = get_html_table_row_attributes(data)
        if self.__row_position == 0: 
            self.__html += "          <tr{}>\n".format(row_attributes)

        html_table_attributes_string_builder = HTMLCellAttributesStringBuilder(column_span=column_span, cell_class=cell_class)
        attributes = html_table_attributes_string_builder.get_html_attributes_string()
        self.__html += "            <td{}>{}</td>\n".format(attributes, data)
        self.__row_position += 1
        if (self.__row_position % self.__number_of_data_columns) == 0:
            self.__html += "          </tr>\n"
            self.__row_position = 0

    def append_html_directly(self, html_to_append):
        self.__html += html_to_append

    def append_close_of_table_body(self):
        self.__html += "       </tbody>\n"

    def append_close_of_table(self):
        self.__html += "     </table>\n"

    def get_table_html(self): 
        return self.__html 
    
    def is_empty_table(self): 
        if "<td>" not in self.__html: 
            return True
        return False 


class HTMLSubTableBuilder:

    def __init__(self, number_of_data_columns):
        self.__html_table_builder = HTMLTableBuilder(number_of_data_columns)
        
    def append_table_header(self, column_names, column_spans, cell_classes):
        assert len(column_names) == len(column_spans)
        row_attributes = get_html_table_row_attributes(column_names)
        self.__html_table_builder.append_html_directly("        <tr{}>\n".format(row_attributes))
        for (column_name, column_span, cell_class) in zip(column_names, column_spans, cell_classes):
            html_table_attributes_string_builder = HTMLCellAttributesStringBuilder(column_span=column_span, cell_class=cell_class)
            attributes = html_table_attributes_string_builder.get_html_attributes_string()
            self.__html_table_builder.append_html_directly("          <td{}>{}</td>\n".format(attributes, str(column_name)))      
        self.__html_table_builder.append_html_directly("        </tr>\n")

    def append_data_to_table(self, data, column_span=None, cell_class=None): 
        self.__html_table_builder.append_data_to_table(data, column_span, cell_class)

    def get_table_html(self):
        return self.__html_table_builder.get_table_html()


class HTMLCellAttributesStringBuilder:

    def __init__(self, column_span=None, cell_class=None):
        self.__column_span = column_span
        self.__cell_class = cell_class
        self.__html_cell_attributes_string = ""

    def get_html_attributes_string(self):
        if self.__column_span != None:
            self.__html_cell_attributes_string += ' colspan=\"{}\"'.format(str(self.__column_span))
        if self.__cell_class != None:
            self.__html_cell_attributes_string += ' class=\"{}\"'.format(str(self.__cell_class))

        return self.__html_cell_attributes_string

def get_html_table_row_attributes(data):
    table_row_attributes_string = ''

    if data == 'Overall Quality Metric':
        table_row_attributes_string += ' class=summary'
    else:
        table_row_attributes_string += ''

    return table_row_attributes_string


@dataclass
class CellData: 

    contents: str = None
    is_row_end: bool = False





