# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest
import pandas as pd
import collections

from metadata_generation.insight.formatting.json_formatting import FrequencyFormatter


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * Frequency Formatter Tests * * * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################

@pytest.mark.parametrize(
    'test_df, expected_keys, expected_values', 
    [(pd.DataFrame({'values' : [1,1,1,2,2,1.0,1.0]}), [1,2], [5,2]),
     (pd.DataFrame({'values' : ['1','1','1','2','2','1.0','1.0']}), [1,2], [5,2]),
     (pd.DataFrame({'values' : [1,'1',1,'2',2,1.0,'1.0']}), [1,2], [5,2]), 
     (pd.DataFrame({'values' : [1.78,'1',1.78,'2',2,1.0,'1.0']}), [1,1.78,2], [3,2,2]),
     (pd.DataFrame({'values' : [1.78,'1','A',1.78,'2',2,1.0,'1.0']}), [1,'A',1.78,2], [3,1,2,2])]     
)
def test_frequency_formatter(test_df, expected_keys, expected_values):
    frequency_formatter = FrequencyFormatter()
    frequencies = frequency_formatter.get_counts(test_df['values'].value_counts())
    keys = frequencies.keys()
    values = list(frequencies.values())
    assert collections.Counter(keys) == collections.Counter(expected_keys)
    assert collections.Counter(values) == collections.Counter(expected_values) 