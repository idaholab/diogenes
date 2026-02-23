# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest 

import pandas as pd

from metadata_generation.veritas.datatypes import RuleTypeEnum, DataQualityTypeEnum
from metadata_generation.veritas.datatypes import KeyLocationEnum, CategoricalLocationEnum 
from metadata_generation.veritas.datatypes import NumericalLocationEnum, DateLocationEnum
from metadata_generation.veritas.datatypes import JSONIndex

from metadata_generation.veritas.rule_table_generation.rule_generation import RuleFrame, Rule

from metadata_generation.veritas.error_catalog_generation.rule_execution import ErrorBatch, ErrorInfo, ReferenceErrorInfo
from metadata_generation.veritas.error_catalog_generation.rule_execution import SingleErrorInfo, NormalityOutlierErrorInfo, CategoricalFrequencyErrorInfo

from metadata_generation.veritas.error_catalog_generation.location_id_generation import KeyLocationIDGenerator, CategoricalLocationIDGenerator
from metadata_generation.veritas.error_catalog_generation.location_id_generation import NumericalLocationIDGenerator, DateLocationIDGenerator


def setup_error_batch(rule_type, rule_specific_error_info):
    JSON_index = JSONIndex(-1, -1)
    rule_frame = RuleFrame(JSON_index, rule_specific_error_info.data_quality_type)
    rule = Rule(rule_frame, rule_type)

    error_batch = ErrorBatch(rule, rule_specific_error_info, pd.DataFrame(), None)
    return error_batch


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * * KeyLocationIDGenerator Tests  * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'rule_id, rule_specific_error_info, expected_location_id',
    [(RuleTypeEnum.KEY_IS_UNIQUE, SingleErrorInfo(DataQualityTypeEnum.KEY, -1, -1), KeyLocationEnum.UNIQUENESS_VIOLATION),
     (RuleTypeEnum.REFERENCE_KEY_EXISTS, ReferenceErrorInfo(DataQualityTypeEnum.IDENTIFIER, 'mock_primary_table_name', 'mock_foreign_table_name'), KeyLocationEnum.ORPHAN_FOREIGN_KEY)]
)
def test_key_get_location_id(rule_id, rule_specific_error_info, expected_location_id):
    error_batch = setup_error_batch(rule_id, rule_specific_error_info)
    location_id_generator = KeyLocationIDGenerator(error_batch)
    location_id = location_id_generator.get_location_id()

    assert location_id == expected_location_id


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * CategoricalLocationIDGenerator Tests  * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


def test_categorical_get_location_id():
    location_id_generator = CategoricalLocationIDGenerator()
    location_id = location_id_generator.get_location_id()

    assert location_id == CategoricalLocationEnum.PLAIN_RECORD


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * NumericalLocationIDGenerator Tests  * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'rule_id, rule_specific_error_info, value, expected_location_id',
    [(RuleTypeEnum.NORMAL_OUTLIER, NormalityOutlierErrorInfo(DataQualityTypeEnum.NUMERICAL, 1, 1, 100, 1), 4.5, NumericalLocationEnum.OUTSIDE_THREE_STD_DEV),
     (RuleTypeEnum.NORMAL_OUTLIER, NormalityOutlierErrorInfo(DataQualityTypeEnum.NUMERICAL, 1, 1, 100, 1), 5.5, NumericalLocationEnum.OUTSIDE_FOUR_STD_DEV),
     (RuleTypeEnum.NORMAL_OUTLIER, NormalityOutlierErrorInfo(DataQualityTypeEnum.NUMERICAL, 1, 1, 100, 1), -2.5, NumericalLocationEnum.OUTSIDE_THREE_STD_DEV),
     (RuleTypeEnum.NORMAL_OUTLIER, NormalityOutlierErrorInfo(DataQualityTypeEnum.NUMERICAL, 1, 1, 100, 1), -3.5, NumericalLocationEnum.OUTSIDE_FOUR_STD_DEV),
     (RuleTypeEnum.UNIT_OUTLIER, SingleErrorInfo(DataQualityTypeEnum.NUMERICAL, 1, 1), -1, NumericalLocationEnum.PLAIN_RECORD)]
)
def test_numerical_get_location_id(rule_id, rule_specific_error_info, value, expected_location_id):
    error_batch = setup_error_batch(rule_id, rule_specific_error_info)
    location_id_generator = NumericalLocationIDGenerator(error_batch, value)

    location_id = location_id_generator.get_location_id()

    assert location_id == expected_location_id 


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * * DateLocationIDGenerator Tests * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


def test_date_get_location_id():
    location_id_generator = DateLocationIDGenerator()
    location_id = location_id_generator.get_location_id()

    assert location_id == DateLocationEnum.PLAIN_RECORD