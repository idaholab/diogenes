# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest

from test.fixtures.error_catalog_generation import error_batches

from metadata_generation.veritas.error_catalog_generation.error_tables import ErrorTablesBuilder, MissingRecordsGenerator


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * ErrorTablesBuilder Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


def test_get_error_tables(error_batches):
    reference_batch = error_batches['reference']
    uniqueness_batch = error_batches['uniqueness']
    low_frequency_batch = error_batches['low_frequency']
    normal_outlier_batch = error_batches['normal_outlier']
    unit_outlier_batch = error_batches['unit_outlier']
    date_outlier_batch = error_batches['date_outlier']

    error_tables_builder = ErrorTablesBuilder()
    error_tables_builder.add_reference_errors(reference_batch)
    error_tables_builder.add_grouped_errors(uniqueness_batch)
    error_tables_builder.add_grouped_errors(low_frequency_batch)
    error_tables_builder.add_single_errors(normal_outlier_batch)
    error_tables_builder.add_single_errors(unit_outlier_batch)
    error_tables_builder.add_single_errors(date_outlier_batch)

    grouped_errors = error_tables_builder.get_grouped_errors()
    erroneous_records = error_tables_builder.get_table_with_error_probabilities('erroneous')
    missing_records = error_tables_builder.get_table_with_error_probabilities('missing')
    error_tables = error_tables_builder.get_error_tables(grouped_errors, erroneous_records, missing_records)
    error_tables.print_to_csv('')


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * *  MissingRecordsGenerator Tests  * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################
    
    
def test_missing_records_generator(error_batches):
    reference_batch = error_batches['reference']

    missing_records_generator = MissingRecordsGenerator()
    missing_records_generator.add_missing(24, 0, reference_batch, 0)
    missing_records_generator.add_missing(23, 1, reference_batch, 1)

    error_id_index_pair = missing_records_generator.get_error_id_and_index(24, reference_batch)
    assert error_id_index_pair == (0, 0)
    error_id_index_pair = missing_records_generator.get_error_id_and_index(23, reference_batch)
    assert error_id_index_pair == (1, 1)


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * *  ErroneousRecordsGenerator Tests  * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################
    

def test_erroneous_records(error_batches):
    pass


