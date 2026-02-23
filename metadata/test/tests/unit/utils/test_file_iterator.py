# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest

from test.fixtures.input import metadata_iterator

from metadata_generation.utils.file_iterator import  CSVIterator, MetadataIterator


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * *  * MetadataIterator Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################
   

def test_iterate_table(metadata_iterator):
    table_names = []
    expected_table_indices_length = 4
    
    for table_metadata_index in metadata_iterator.iterate_table():
        table_names.append(table_metadata_index)

    assert len(table_names) == expected_table_indices_length


def test_iterate_attribute(metadata_iterator):
    attribute_names = []
    expected_attributes_indices_length = 24

    for _ in metadata_iterator.iterate_table():
        for attribute_metadata_index in metadata_iterator.iterate_attribute():
            attribute_names.append(attribute_metadata_index)
        
        break

    assert len(attribute_names) == expected_attributes_indices_length

    
#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * CSVIterator Tests   * * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


def setup_csv_iterator_tests(csv_file_path):
    csv_iterator = CSVIterator(csv_file_path, skip_header=True)
    csv_iterator.open_file()
    return csv_iterator 


def get_first_line(csv_iterator, expected_number_of_columns):
    for _ in csv_iterator.iterate_lines():
        tokenized_line = csv_iterator.get_tokenized_line(expected_number_of_columns)
        break

    return tokenized_line


def test_iterate_lines(good_unit_configuration_file_path):
    expected_line_numbers = range(2,29) 
    index = 0
    csv_iterator = setup_csv_iterator_tests(good_unit_configuration_file_path)
    
    for line_number in csv_iterator.iterate_lines():
        assert line_number == expected_line_numbers[index]
        index += 1 

    csv_iterator.close_file()


def test_get_tokenized_line_good(good_unit_configuration_file_path, expected_tokenized_unit_line, expected_number_of_columns):
    csv_iterator = setup_csv_iterator_tests(good_unit_configuration_file_path)
    tokenized_line = get_first_line(csv_iterator, expected_number_of_columns)
    assert tokenized_line == expected_tokenized_unit_line
    csv_iterator.close_file()


def test_get_tokenized_line_bad(bad_configuration_file_path, expected_tokenized_unit_line, expected_number_of_columns):
    csv_iterator = setup_csv_iterator_tests(bad_configuration_file_path)

    with pytest.raises(IOError):
        _ = get_first_line(csv_iterator, expected_number_of_columns)
    
    csv_iterator.close_file()

    