# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from collections import defaultdict

from ...utils import datatype_conversion

class FrequencyFormatter:

    @classmethod 
    def get_counts(cls, unformatted_value_counts):
        formatted_value_counts = defaultdict(int)

        for value_counts in unformatted_value_counts.items():
            value = value_counts[0]
            count = value_counts[1]

            if value in formatted_value_counts.keys():
                formatted_value_counts[value] += count
            elif datatype_conversion.is_string_integer(value):
                formatted_value_counts[datatype_conversion.convert_string_to_int(value)] += count 
            elif datatype_conversion.is_numeric_integer(value):
                formatted_value_counts[int(value)] += count 
            else:
                formatted_value_counts[value] += count

        return formatted_value_counts