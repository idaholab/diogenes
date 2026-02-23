# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest
import pandas as pd

from pandas.testing import assert_frame_equal
from test.fixtures.error_catalog_generation import error_batches

from metadata_generation.veritas.datatypes import KeyLocationEnum, NumericalLocationEnum

from metadata_generation.veritas.error_catalog_generation.error_tables import ErrorTablesBuilder, ErrorsGenerator, ErroneousRecordsGenerator


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * ErrorTablesBuilder Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################
    

def test_add_reference_errors(error_batches):
    reference_batch = error_batches['reference']

    error_tables_builder = ErrorTablesBuilder()
    error_tables_builder.add_reference_errors(reference_batch)


def test_add_grouped_errors(error_batches):
    low_frequency_batch = error_batches['low_frequency']

    error_tables_builder = ErrorTablesBuilder()
    error_tables_builder.add_grouped_errors(low_frequency_batch)


def test_add_single_errors(error_batches):
    unit_outlier_batch = error_batches['unit_outlier']

    error_tables_builder = ErrorTablesBuilder()
    error_tables_builder.add_single_errors(unit_outlier_batch)


def test_get_error_tables(error_batches):
    pass


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * *  ErrorsGenerator Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################
    

def test_add_error(error_batches):
    
    unit_outlier_batch = error_batches['unit_outlier']
    normal_outlier_batch = error_batches['normal_outlier']

    errors_generator = ErrorsGenerator()
    error_ids = []
    error_ids.append(errors_generator.add_error(unit_outlier_batch))
    error_ids.append(errors_generator.add_error(normal_outlier_batch))
    expected_error_ids = [(0, 0), (1, 1)]

    assert expected_error_ids == error_ids  


def test_add_errors(error_batches):
    unit_outlier_batch = error_batches['unit_outlier']
    normal_outlier_batch = error_batches['normal_outlier']

    errors_generator = ErrorsGenerator()
    (error_ids, error_indices) = errors_generator.add_errors(unit_outlier_batch)
    (new_error_ids, new_error_indices) = errors_generator.add_errors(normal_outlier_batch)
    error_ids += new_error_ids
    error_indices += new_error_indices

    expected_error_ids = [0, 1, 2, 3, 4]
    expected_error_indices = [0, 1, 2, 3, 4]

    assert expected_error_ids == error_ids


def test_set_group_ids(error_batches):
    pass


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * *  MissingRecordsGenerator Tests  * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################
    

def test_add_missing():
    pass


def test_get_error_id_of_missing_record(): 
    pass


def test_get_missing_records(): 
    pass


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * *  ErroneousRecordsGenerator Tests  * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################
    

'''def test_add_erroneous_records_batch(error_batches):
    uniqueness_batch = error_batches['uniqueness']
    uniqueness_batch.errors_table['error_ID'] = [1, 2, 2, 1]

    normal_outlier_batch = error_batches['normal_outlier']
    normal_outlier_batch.errors_table['error_ID'] = [3, 4]

    erroneous_records_generator = ErroneousRecordsGenerator()
    erroneous_records_generator.add_erroneous_records_batch(uniqueness_batch)
    erroneous_records_generator.add_erroneous_records_batch(normal_outlier_batch)
    erroneous_records = erroneous_records_generator.get_raw_records() 

    uniqueness_batch.errors_table['location_ID'] = [KeyLocationEnum.UNIQUENESS_VIOLATION] * 4
    normal_outlier_batch.errors_table['location_ID'] = [NumericalLocationEnum.OUTSIDE_FOUR_STD_DEV] * 2
    expected_erroneous_records = pd.concat([uniqueness_batch.errors_table, normal_outlier_batch.errors_table])

    assert expected_erroneous_records.equals(erroneous_records)
'''

#def test_get_erroneous_records(error_batches):
#    pass


