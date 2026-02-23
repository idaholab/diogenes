# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest
import pandas as pd

#from test.fixtures.utils import multi_record_erroneous_records, multi_table_erroneous_records
#from test.fixtures.utils import single_error_erroneous_records, errors
from test.fixtures.utils import errors 

from metadata_generation.utils.dataframe_tools import QueryableErroneousRecords, QueryableErrors


def multi_table_erroneous_records():
    multi_table_erroneous_records = pd.DataFrame(columns=['table_name', 'attribute_name', 'error_ID', 'value', 'location_ID'])
    multi_table_erroneous_records = multi_table_erroneous_records.append({'table_name' : 'batteryList', 'attribute_name' : 'batteryID', 'error_ID' : 1, 'value' : 0, 'location_ID' : -1}, ignore_index=True)
    multi_table_erroneous_records = multi_table_erroneous_records.append({'table_name' : 'batteryList', 'attribute_name' : 'batteryID', 'error_ID' : 1, 'value' : 1, 'location_ID' : -1}, ignore_index=True)
    multi_table_erroneous_records = multi_table_erroneous_records.append({'table_name' : 'batteryList', 'attribute_name' : 'batteryID', 'error_ID' : 1, 'value' : 2, 'location_ID' : -1}, ignore_index=True)
    multi_table_erroneous_records = multi_table_erroneous_records.append({'table_name' : 'batteryTestSummary', 'attribute_name' : 'batteryIdentifier', 'error_ID' : 1, 'value' : 0, 'location_ID' : -1}, ignore_index=True)
    multi_table_erroneous_records = multi_table_erroneous_records.append({'table_name' : 'batteryTestSummary', 'attribute_name' : 'batteryIdentifier', 'error_ID' : 1, 'value' : 1, 'location_ID' : -1}, ignore_index=True)
    return multi_table_erroneous_records


def multi_record_erroneous_records():
    multi_record_erroneous_records = pd.DataFrame(columns=['table_name', 'attribute_name', 'error_ID', 'value', 'location_ID'])
    multi_record_erroneous_records = multi_record_erroneous_records.append({'table_name' : 'batteryList', 'attribute_name' : 'batteryID', 'error_ID' : 1, 'value' : 0, 'location_ID' : -1}, ignore_index=True)
    multi_record_erroneous_records = multi_record_erroneous_records.append({'table_name' : 'batteryList', 'attribute_name' : 'batteryID', 'error_ID' : 1, 'value' : 1, 'location_ID' : -1}, ignore_index=True)
    multi_record_erroneous_records = multi_record_erroneous_records.append({'table_name' : 'batteryList', 'attribute_name' : 'batteryID', 'error_ID' : 1, 'value' : 2, 'location_ID' : -1}, ignore_index=True)
    multi_record_erroneous_records = multi_record_erroneous_records.append({'table_name' : 'batteryTestSummary', 'attribute_name' : 'batteryIdentifier', 'error_ID' : 2, 'value' : 0, 'location_ID' : -1}, ignore_index=True)
    multi_record_erroneous_records = multi_record_erroneous_records.append({'table_name' : 'batteryTestSummary', 'attribute_name' : 'batteryIdentifier', 'error_ID' : 2, 'value' : 1, 'location_ID' : -1}, ignore_index=True)
    return multi_record_erroneous_records


def single_error_erroneous_records():
    single_error_erroneous_records = pd.DataFrame(columns=['table_name', 'attribute_name', 'error_ID', 'value', 'location_ID'])
    single_error_erroneous_records = single_error_erroneous_records.append({'table_name' : 'batteryList', 'attribute_name' : 'batteryID', 'error_ID' : 1, 'value' : 0, 'location_ID' : -1}, ignore_index=True)
    single_error_erroneous_records = single_error_erroneous_records.append({'table_name' : 'batteryList', 'attribute_name' : 'batteryID', 'error_ID' : 2, 'value' : 1, 'location_ID' : -1}, ignore_index=True)
    single_error_erroneous_records = single_error_erroneous_records.append({'table_name' : 'batteryList', 'attribute_name' : 'batteryID', 'error_ID' : 3, 'value' : 2, 'location_ID' : -1}, ignore_index=True)
    single_error_erroneous_records = single_error_erroneous_records.append({'table_name' : 'batteryTestSummary', 'attribute_name' : 'batteryIdentifier', 'error_ID' : 4, 'value' : 0, 'location_ID' : -1}, ignore_index=True)
    single_error_erroneous_records = single_error_erroneous_records.append({'table_name' : 'batteryTestSummary', 'attribute_name' : 'batteryIdentifier', 'error_ID' : 5, 'value' : 1, 'location_ID' : -1}, ignore_index=True)
    return single_error_erroneous_records


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * QueryableErroneousRecords Tests * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'erroneous_records_table, expected_error_ids',
    [(multi_table_erroneous_records(), [1]),
     (multi_record_erroneous_records(), [1,2]),
     (single_error_erroneous_records(), [1,2,3,4,5])]
)
def test_aggregate_error_ids(erroneous_records_table, expected_error_ids):
    queryable_erroneous_records = QueryableErroneousRecords(erroneous_records_table)
    error_ids = queryable_erroneous_records.aggregate_error_ids()

    assert error_ids == expected_error_ids 


@pytest.mark.parametrize(
    'erroneous_records_table, expected_bool_value',
    [(multi_table_erroneous_records(), True),
     (multi_record_erroneous_records(), False),
     (single_error_erroneous_records(), False)]
)
def test_error_is_multi_table(erroneous_records_table, expected_bool_value):
    error_id = 1
    queryable_erroneous_records = QueryableErroneousRecords(erroneous_records_table)
    bool_value = queryable_erroneous_records.error_is_multi_table(error_id)

    assert bool_value == expected_bool_value 


@pytest.mark.parametrize(
    'erroneous_records_table, expected_bool_value',
    [(multi_table_erroneous_records(), True),
     (multi_record_erroneous_records(), True),
     (single_error_erroneous_records(), False)]
)
def test_error_is_multi_record(erroneous_records_table, expected_bool_value):
    error_id = 1
    queryable_erroneous_records = QueryableErroneousRecords(erroneous_records_table)
    bool_value = queryable_erroneous_records.error_is_multi_record(error_id)

    assert bool_value == expected_bool_value 


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * * QueryableErrors Tests * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'error_id, expected_rule_specific_error_info',
    [(1, 'mock1'),
     (2, 'mock2')]
)
def test_get_rule_specific_error_info(error_id, expected_rule_specific_error_info, errors):
    queryable_errors = QueryableErrors(errors)
    rule_specific_error_info = queryable_errors.get_rule_specific_error_info(error_id)

    assert rule_specific_error_info == expected_rule_specific_error_info


@pytest.mark.parametrize(
    'error_id, expected_rule_id',
    [(1, 1),
     (2, 2)]
)
def test_get_rule_id(error_id, expected_rule_id, errors):
    queryable_errors = QueryableErrors(errors)
    rule_id = queryable_errors.get_rule_id(error_id)

    assert rule_id == expected_rule_id