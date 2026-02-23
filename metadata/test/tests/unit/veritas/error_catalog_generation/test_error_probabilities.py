# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest

from metadata_generation.veritas.datatypes import DataQualityTypeEnum
from metadata_generation.veritas.datatypes import NumericalGroupEnum, NumericalLocationEnum
from metadata_generation.veritas.datatypes import CategoricalGroupEnum, CategoricalLocationEnum
from metadata_generation.veritas.datatypes import KeyGroupEnum, KeyLocationEnum
from metadata_generation.veritas.datatypes import DateGroupEnum, DateLocationEnum

from metadata_generation.veritas.error_catalog_generation.error_probabilities import KeyErrorProbabilities, CategoricalErrorProbabilities
from metadata_generation.veritas.error_catalog_generation.error_probabilities import NumericalErrorProbabilities, DateErrorProbabilities


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * KeyErrorProbabilities Tests * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'group_id, location_id, expected_probability',
        [(KeyGroupEnum.MULTI_RECORD, KeyLocationEnum.MISSING_PRIMARY_KEY, 0.8),
        (KeyGroupEnum.MULTI_TABLE, KeyLocationEnum.MISSING_PRIMARY_KEY, 1),
        (KeyGroupEnum.SINGLE_RECORD, KeyLocationEnum.MISSING_PRIMARY_KEY, 0.2),
        (KeyGroupEnum.MULTI_RECORD, KeyLocationEnum.ORPHAN_FOREIGN_KEY, 0.2),
        (KeyGroupEnum.MULTI_TABLE, KeyLocationEnum.ORPHAN_FOREIGN_KEY, 0),
        (KeyGroupEnum.SINGLE_RECORD, KeyLocationEnum.ORPHAN_FOREIGN_KEY, 0.8),
        (KeyGroupEnum.AFFECTS_MANY_RECORDS, KeyLocationEnum.UNIQUENESS_VIOLATION, 0),
        (KeyGroupEnum.AFFECTS_SOME_RECORDS, KeyLocationEnum.UNIQUENESS_VIOLATION, 0.10),
        (KeyGroupEnum.AFFECTS_FEW_RECORDS, KeyLocationEnum.UNIQUENESS_VIOLATION, 1)]
)
def test_key_get_error_probability(group_id, location_id, expected_probability):
    probability_generator = KeyErrorProbabilities()
    probability = probability_generator.get_error_probability(group_id, location_id)

    assert probability == expected_probability


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * CategoricalErrorProbabilities Tests * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'group_id, location_id, expected_probability',
        [(CategoricalGroupEnum.MULTIPLE_SUB_THRESHOLD, CategoricalLocationEnum.PLAIN_RECORD, 0),
            (CategoricalGroupEnum.FEW_SUB_THRESHOLD, CategoricalLocationEnum.PLAIN_RECORD, 0.10),
            (CategoricalGroupEnum.SINGLE_SUB_THRESHOLD, CategoricalLocationEnum.PLAIN_RECORD, 1)]
)
def test_categorical_get_error_probability(group_id, location_id, expected_probability):
    probability_generator = CategoricalErrorProbabilities()
    probability = probability_generator.get_error_probability(group_id, location_id)

    assert probability == expected_probability


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * *  NumericalErrorProbabilities Tests  * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'group_id, location_id, expected_probability',
        [(NumericalGroupEnum.AFFECTS_MANY_RECORDS, NumericalLocationEnum.PLAIN_RECORD, 0),
         (NumericalGroupEnum.AFFECTS_SOME_RECORDS, NumericalLocationEnum.PLAIN_RECORD, 0.10),
         (NumericalGroupEnum.AFFECTS_FEW_RECORDS, NumericalLocationEnum.PLAIN_RECORD, 1),
         (NumericalGroupEnum.AFFECTS_MANY_RECORDS, NumericalLocationEnum.OUTSIDE_THREE_STD_DEV, 0),
         (NumericalGroupEnum.AFFECTS_SOME_RECORDS, NumericalLocationEnum.OUTSIDE_THREE_STD_DEV, 0.10),
         (NumericalGroupEnum.AFFECTS_FEW_RECORDS, NumericalLocationEnum.OUTSIDE_THREE_STD_DEV, 1),
         (NumericalGroupEnum.AFFECTS_MANY_RECORDS, NumericalLocationEnum.OUTSIDE_FOUR_STD_DEV, 0),
         (NumericalGroupEnum.AFFECTS_SOME_RECORDS, NumericalLocationEnum.OUTSIDE_FOUR_STD_DEV, 0.10),
         (NumericalGroupEnum.AFFECTS_FEW_RECORDS, NumericalLocationEnum.OUTSIDE_FOUR_STD_DEV, 1)]
)
def test_numerical_get_error_probability(group_id, location_id, expected_probability):
    probability_generator = NumericalErrorProbabilities()
    probability = probability_generator.get_error_probability(group_id, location_id)

    assert probability == expected_probability


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * DateErrorProbabilities Tests  * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'group_id, location_id, expected_probability',
        [(DateGroupEnum.AFFECTS_MANY_RECORDS, DateLocationEnum.PLAIN_RECORD, 0),
         (DateGroupEnum.AFFECTS_SOME_RECORDS, DateLocationEnum.PLAIN_RECORD, 0.10),
         (DateGroupEnum.AFFECTS_FEW_RECORDS, DateLocationEnum.PLAIN_RECORD, 1)]
)
def test_date_get_error_probability(group_id, location_id, expected_probability):
    probability_generator = DateErrorProbabilities()
    probability = probability_generator.get_error_probability(group_id, location_id)

    assert probability == expected_probability
