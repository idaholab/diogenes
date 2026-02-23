# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest

from test.fixtures.input import good_metadata_file_path as metadata_file_path
from test.fixtures.input import good_unit_configuration_file_path, bad_configuration_file_path
from test.fixtures.input import expected_tokenized_unit_line, expected_number_of_columns
from test.fixtures.input import metadata

from metadata_generation.utils.file_parsing import MetadataAttributeParser
from metadata_generation.veritas.datatypes import JSONIndex


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * *  * MetadataAttributeParser Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'JSON_index, key, expected_bool',
    [(JSONIndex(0, 0), 'units', True), 
     (JSONIndex(0, 0), 'refersTo', False),
     (JSONIndex(1, 7), 'units', True)]
)
def test_in_attribute_value(JSON_index, key, expected_bool, metadata):
    metadata_attribute_parser = MetadataAttributeParser(metadata, JSON_index)
    bool_value = metadata_attribute_parser.in_attribute_values(key)
    assert bool_value == expected_bool


@pytest.mark.parametrize(
    'JSON_index, expected_unit, expected_data_quality_type',
    [(JSONIndex(0, 0), 'n/a', 'key'),
     (JSONIndex(0, 3), 'cells', 'categorical'), 
     (JSONIndex(1, 7), 'Ah', 'numerical')]
)
def test_get_attribute_value(JSON_index, expected_unit, expected_data_quality_type, metadata):
    metadata_attribute_parser = MetadataAttributeParser(metadata, JSON_index)
    units = metadata_attribute_parser.get_attribute_value('units')
    data_quality_type = metadata_attribute_parser.get_data_quality_type()

    assert units == expected_unit
    assert data_quality_type == expected_data_quality_type  


@pytest.mark.parametrize(
    'JSON_index, key, expected_bool_value',
    [(JSONIndex(0, 0), 'Count', True),
     (JSONIndex(0, 3), 'Minimum Value', True),
     (JSONIndex(0, 3), 'Kurtosis', False),
     (JSONIndex(1, 7), 'Mean', True)]
)
def test_in_data_quality_metrics(JSON_index, key, expected_bool_value, metadata):
    metadata_attribute_parser = MetadataAttributeParser(metadata, JSON_index)
    bool_value = metadata_attribute_parser.in_data_quality_metrics(key)
    assert bool_value == expected_bool_value


@pytest.mark.parametrize(
    'JSON_index, key, expected_metric_value',
    [(JSONIndex(0, 0), 'Count', 21 ),
     (JSONIndex(0, 3), 'Minimum Value', 32),
     (JSONIndex(1, 7), 'Median', 60)]
)
def test_get_data_quality_metric(JSON_index, key, expected_metric_value, metadata):
    metadata_attribute_parser = MetadataAttributeParser(metadata, JSON_index)
    metric_value = metadata_attribute_parser.get_data_quality_metric(key)
    assert metric_value == expected_metric_value

