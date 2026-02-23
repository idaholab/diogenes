# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest

from metadata_generation.pdf_generation.factories.html_table import ValueFormatter


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * ValueFormatter Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'value, rounding_precision, expected_formatted_string',
    [(100, 2, '100'),
     (98.654, 2, '98.65'),
     (98.654, 3, '98.654'),
     (1000000, 3, '1,000,000'),
     (1000.7645, 3, '1,000.764')],
)
def test_format_numeric_value(value, rounding_precision, expected_formatted_string):
    value_formatter = ValueFormatter()  
    formatted_value = value_formatter.format_numeric_value(value, rounding_precision)
    assert formatted_value == expected_formatted_string