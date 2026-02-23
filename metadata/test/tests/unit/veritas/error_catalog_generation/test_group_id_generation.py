# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest 

import pandas as pd

from metadata_generation.veritas.datatypes import RuleTypeEnum, DataQualityTypeEnum
from metadata_generation.veritas.datatypes import KeyGroupEnum, CategoricalGroupEnum 
from metadata_generation.veritas.datatypes import NumericalGroupEnum, DateGroupEnum

from metadata_generation.veritas.error_catalog_generation.rule_execution import ErrorBatch, ErrorInfo, ReferenceErrorInfo
from metadata_generation.veritas.error_catalog_generation.rule_execution import SingleErrorInfo, NormalityOutlierErrorInfo, CategoricalFrequencyErrorInfo

from metadata_generation.veritas.error_catalog_generation.group_id_generation import KeyGroupIDGenerator, CategoricalGroupIDGenerator
from metadata_generation.veritas.error_catalog_generation.group_id_generation import NumericalGroupIDGenerator, DateGroupIDGenerator
from metadata_generation.veritas.error_catalog_generation.group_id_generation import PercentageErroneousGroupIDSelector, FrequencyErroneousGroupIDSelector, KeyErroneousGroupIDSelector


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * * KeyGroupIDGenerator Tests * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'rule_type, rule_specific_error_info, expected_group_id',
    [(RuleTypeEnum.REFERENCE_KEY_EXISTS, ReferenceErrorInfo(DataQualityTypeEnum.KEY, 'mock_primary_table', 'mock_foreign_table'), False, KeyGroupEnum.MULTI_RECORD),
     (RuleTypeEnum.REFERENCE_KEY_EXISTS, ReferenceErrorInfo(DataQualityTypeEnum.KEY, 'mock_primary_table', 'mock_foreign_table'), True, KeyGroupEnum.MULTI_TABLE)]
)
def test_key_get_group_id_reference(rule_type, rule_specific_error_info, is_multi_table, expected_group_id):
    rule_specific_error_info.set_is_multi_record(True)
    rule_specific_error_info.set_is_multi_table(is_multi_table)
    group_id_generator = KeyGroupIDGenerator(rule_type)
    group_id = group_id_generator.get_group_id(rule_specific_error_info)

    assert group_id == expected_group_id


@pytest.mark.parametrize(
    'rule_type, rule_specific_error_info, expected_group_id',
    [(RuleTypeEnum.KEY_IS_UNIQUE, SingleErrorInfo(DataQualityTypeEnum.KEY, 100, 1), KeyGroupEnum.AFFECTS_FEW_RECORDS)]
)
def test_key_get_group_id_reference(rule_type, rule_specific_error_info, expected_group_id):
    group_id_generator = KeyGroupIDGenerator(rule_type)
    group_id = group_id_generator.get_group_id(rule_specific_error_info)

    assert group_id == expected_group_id
#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * CategoricalGroupIDGenerator Tests * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


def test_categorical_get_group_id():
    number_of_sub_threshold_categories = 1
    rule_specific_error_info = CategoricalFrequencyErrorInfo(DataQualityTypeEnum.CATEGORICAL, number_of_sub_threshold_categories)

    group_id_generator = CategoricalGroupIDGenerator()
    group_id = group_id_generator.get_group_id(rule_specific_error_info)

    assert group_id == CategoricalGroupEnum.SINGLE_SUB_THRESHOLD


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * *  NumericalGroupIDGenerator Tests  * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'rule_specific_error_info, expected_group_id',
    [(NormalityOutlierErrorInfo(DataQualityTypeEnum.NUMERICAL, 1, 1, 100, 1), NumericalGroupEnum.AFFECTS_FEW_RECORDS),
     (SingleErrorInfo(DataQualityTypeEnum.NUMERICAL, 100, 1), NumericalGroupEnum.AFFECTS_FEW_RECORDS)]
)
def test_numerical_get_group_id(rule_specific_error_info, expected_group_id):  
    group_id_generator = DateGroupIDGenerator()
    group_id = group_id_generator.get_group_id(rule_specific_error_info)

    assert group_id == expected_group_id


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * * DateGroupIDGenerator Tests  * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


def test_date_get_group_id():
    number_of_total_records = 100
    number_of_records_erroneous = 1
    rule_specific_error_info = SingleErrorInfo(DataQualityTypeEnum.DATE, number_of_total_records, number_of_records_erroneous)

    group_id_generator = DateGroupIDGenerator()
    group_id = group_id_generator.get_group_id(rule_specific_error_info)

    assert group_id == DateGroupEnum.AFFECTS_FEW_RECORDS


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * PercentageErroneousGroupIDSelector Tests  * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'data_quality_type, erroneous_row_percentage, expected_group_id',
    [(DataQualityTypeEnum.NUMERICAL, 1, NumericalGroupEnum.AFFECTS_FEW_RECORDS),
     (DataQualityTypeEnum.NUMERICAL, 13, NumericalGroupEnum.AFFECTS_SOME_RECORDS),
     (DataQualityTypeEnum.NUMERICAL, 75, NumericalGroupEnum.AFFECTS_MANY_RECORDS),
     (DataQualityTypeEnum.DATE, 1, DateGroupEnum.AFFECTS_FEW_RECORDS),
     (DataQualityTypeEnum.DATE, 13, DateGroupEnum.AFFECTS_SOME_RECORDS),
     (DataQualityTypeEnum.DATE, 75, DateGroupEnum.AFFECTS_MANY_RECORDS),]
)
def test_percentage_erroneous_get_group_id(data_quality_type, erroneous_row_percentage, expected_group_id):
    group_id_selector = PercentageErroneousGroupIDSelector(data_quality_type)
    group_id = group_id_selector.get_group_id(erroneous_row_percentage)

    assert group_id == expected_group_id 


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * FrequencyErroneousGroupIDSelector Tests * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'data_quality_type, number_of_sub_threshold_categories, expected_group_id',
    [(DataQualityTypeEnum.CATEGORICAL, 1, CategoricalGroupEnum.SINGLE_SUB_THRESHOLD),
     (DataQualityTypeEnum.CATEGORICAL, 3, CategoricalGroupEnum.FEW_SUB_THRESHOLD),
     (DataQualityTypeEnum.CATEGORICAL, 10, CategoricalGroupEnum.MULTIPLE_SUB_THRESHOLD)]
)
def test_percentage_erroneous_get_group_id(data_quality_type, number_of_sub_threshold_categories, expected_group_id):
    group_id_selector = FrequencyErroneousGroupIDSelector(data_quality_type)
    group_id = group_id_selector.get_group_id(erroneous_row_percentage)

    assert group_id == expected_group_id 


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * KeyErroneousGroupIDSelector Tests * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'is_multi_record, is_multi_table, expected_group_id',
    [(False, True, KeyGroupEnum.MULTI_TABLE),
     (True, True, KeyGroupEnum.MULTI_TABLE),
     (True, False, KeyGroupEnum.MULTI_RECORD),
     (False, False, KeyGroupEnum.SINGLE_RECORD)]
)
def test_percentage_erroneous_get_group_id(is_multi_record, is_multi_table, expected_group_id):
    group_id_selector = KeyErroneousGroupIDSelector()
    group_id = group_id_selector.get_group_id(is_multi_record, is_multi_table)

    assert group_id == expected_group_id 