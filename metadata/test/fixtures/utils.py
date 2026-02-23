# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest
import pandas as pd


@pytest.fixture
def errors():
    errors = pd.DataFrame(columns=['rule_ID, error_ID, group_ID, rule_specific_error_info'])
    errors = errors.append({'rule_ID' : 1, 'error_ID' : 1, 'group_ID' : -1 , 'rule_specific_error_info' : 'mock1'}, ignore_index=True)
    errors = errors.append({'rule_ID' : 1, 'error_ID' : 1, 'group_ID' : -1 , 'rule_specific_error_info' : 'mock1'}, ignore_index=True)
    errors = errors.append({'rule_ID' : 2, 'error_ID' : 2, 'group_ID' : -1 , 'rule_specific_error_info' : 'mock2'}, ignore_index=True)
    return errors


