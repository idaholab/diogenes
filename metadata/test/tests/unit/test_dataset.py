# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from test.fixtures.input import veritas_constraints
from test.fixtures.error_catalog_generation import dataset_dir_path

from metadata_generation.metadata_generation_input import Dataset, PandasDatasetFile


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * Dataset Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


def test_add_dataset_file(dataset_dir_path):
    dataset = Dataset()
    file_names = ['batteryTestData.csv', 'batteryTestSummary.csv', 'batteryList.csv', 'vehicleList.csv']

    for file_name in file_names:
        dataset.add_dataset_file(dataset_dir_path + file_name, ',', 'Pandas')

    expected_tables = ['batteryTestData', 'batteryTestSummary', 'batteryList', 'vehicleList']
    table_names = dataset.get_dataset_file_names()

    assert set(table_names) == set(expected_tables)
    

#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * PandasDatasetFile Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


def test_get_indices_outside_numerical_constraint(dataset_dir_path, veritas_constraints):
    attribute_name = 'CapacityRemoved_Ah'
    constraint_name = 'Ah'

    dataset_file_file_path = dataset_dir_path + 'batteryTestData.csv'
    table = PandasDatasetFile(dataset_file_file_path, ',')

    df_outside_numerical_constraint = table.get_rows_outside_numerical_constraint(attribute_name, veritas_constraints.unit_constraints, constraint_name)
    outside_values = df_outside_numerical_constraint[attribute_name].to_list()
    expected_outside_values = [-53, 53, -53]

    assert outside_values == expected_outside_values


def test_get_indices_outside_date_constraint(dataset_dir_path, veritas_constraints):
    attribute_name = 'Date_Of_Test'

    dataset_file_file_path = dataset_dir_path + 'batteryTestSummary.csv'
    table = PandasDatasetFile(dataset_file_file_path, ',')

    df_outside_date_constraint = table.get_rows_outside_date_constraint(attribute_name, veritas_constraints.general_constraints)
    outside_values = df_outside_date_constraint[attribute_name].to_list()
    expected_outside_values = ['5/15/1900', '1/2/1900', '1/2/2300']

    assert outside_values == expected_outside_values


def test_get_rows_where_attribute_value_equals(dataset_dir_path):
    attribute_name = 'BatteryManufacturer'
    desired_attribute_value = 'Panasonic'

    dataset_file_file_path = dataset_dir_path + 'batteryList.csv'
    table = PandasDatasetFile(dataset_file_file_path, ',')

    df_where_attribute_value_equals = table.get_rows_where_attribute_value_equals(attribute_name, desired_attribute_value)
    number_of_values = len(df_where_attribute_value_equals[attribute_name].to_list())
    expected_number_of_values = 3

    assert number_of_values == expected_number_of_values


def test_get_rows_with_duplicate_values(dataset_dir_path):
    attribute_name = 'VehicleID'

    dataset_file_file_path = dataset_dir_path + 'vehicleList.csv'
    table = PandasDatasetFile(dataset_file_file_path, ',')

    df_duplicate_values = table.get_rows_with_duplicate_values(attribute_name)
    duplicate_values = df_duplicate_values[attribute_name].to_list()
    expected_duplicate_values = [102, 103, 103, 102]

    assert duplicate_values == expected_duplicate_values


def test_get_rows_with_missing_values_from_compared(dataset_dir_path):
    attribute_name = 'VehicleID'

    dataset_file_file_path = dataset_dir_path + 'batteryTestSummary.csv'
    table = PandasDatasetFile(dataset_file_file_path, ',')
    compared_dataset_file_file_path = dataset_dir_path + 'vehicleList.csv'
    compared_table = PandasDatasetFile(compared_dataset_file_file_path, ',')

    df_missing = table.get_rows_with_missing_values_from_compared(compared_table, attribute_name, attribute_name)
    missing_values = df_missing[attribute_name].to_list()
    expected_missing_values = [24, 24, 24, 24, 24, 23, 23, 23, 23, 23]

    assert missing_values == expected_missing_values