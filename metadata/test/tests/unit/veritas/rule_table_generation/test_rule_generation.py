# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest

from test.fixtures.input import metadata
from test.fixtures.input import veritas_constraints

from metadata_generation.veritas.datatypes import JSONIndex

from metadata_generation.utils.file_parsing import MetadataAttributeParser

from metadata_generation.veritas.rule_table_generation.rule_generation import KeyRulesGenerator, CategoricalRulesGenerator
from metadata_generation.veritas.rule_table_generation.rule_generation import NumericalRulesGenerator, DateRulesGenerator


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * *  AttributeRulesGenerator Tests  * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################






#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * * *  KeyRulesGenerator Tests  * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################

def setup_key_rules_generator(JSON_index, metadata):
    metadata_attribute_parser = MetadataAttributeParser(metadata, JSON_index)    
    key_rules_generator = KeyRulesGenerator(JSONIndex, metadata_attribute_parser)
    return key_rules_generator

@pytest.mark.parametrize(
    'JSON_index, expected_rules_length',
    [(JSONIndex(0, 0), 1),
     (JSONIndex(2, 0), 0)]
)
def test_add_uniqueness_rule(JSON_index, expected_rules_length, metadata):
    key_rules_generator = setup_key_rules_generator(JSON_index, metadata)
    key_rules_generator.add_uniqueness_rule()
    rules = key_rules_generator.get_rules()

    assert len(rules) == expected_rules_length
    
@pytest.mark.parametrize(
    'JSON_index, expected_rules_length',
    [(JSONIndex(2, 1), 0),
     (JSONIndex(2, 0), 1)]
)
def test_add_key_relation_rule(JSON_index, expected_rules_length, metadata):
    key_rules_generator = setup_key_rules_generator(JSON_index, metadata)
    key_rules_generator.add_key_relation_rule()
    rules = key_rules_generator.get_rules()

    assert len(rules) == expected_rules_length


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * *  CategoricalRulesGenerator Tests  * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################

def setup_categorical_rules_generator(JSON_index, metadata):
    metadata_attribute_parser = MetadataAttributeParser(metadata, JSON_index)    
    categorical_rules_generator = CategoricalRulesGenerator(JSONIndex, metadata_attribute_parser)
    return categorical_rules_generator

@pytest.mark.parametrize(
    'JSON_index, expected_rules_length',
    [(JSONIndex(0, 1), 1),
     (JSONIndex(1, 1), 1),
     (JSONIndex(1, 0), 0)]
)
def test_add_frequency_rule(JSON_index, expected_rules_length, metadata):
    categorical_rules_generator = setup_categorical_rules_generator(JSON_index, metadata)
    categorical_rules_generator.add_frequency_rule()
    rules = categorical_rules_generator.get_rules()

    assert len(rules) == expected_rules_length


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * *  NumericalRulesGenerator Tests  * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################

def setup_numerical_rules_generator(JSON_index, metadata):
    metadata_attribute_parser = MetadataAttributeParser(metadata, JSON_index)    
    key_rules_generator = NumericalRulesGenerator(JSON_index, metadata_attribute_parser)
    return key_rules_generator

@pytest.mark.parametrize(
    'JSON_index, expected_rules_length',
    [(JSONIndex(0, 5), 1),
     (JSONIndex(0, 15), 0),
     (JSONIndex(1, 7), 1)]
)
def test_add_unit_boundary_rule(JSON_index, expected_rules_length, metadata, veritas_constraints):
    numerical_rules_generator = setup_numerical_rules_generator(JSON_index, metadata)
    numerical_rules_generator.add_unit_boundary_rule(veritas_constraints.unit_constraints)
    rules = numerical_rules_generator.get_rules()

    assert len(rules) == expected_rules_length

@pytest.mark.parametrize(
    'JSON_index, expected_rules_length',
    [(JSONIndex(1, 15), 1),
     (JSONIndex(1, 12), 0),
     (JSONIndex(1, 16), 0)]
)
def test_add_normal_outlier_rule(JSON_index, expected_rules_length, metadata, veritas_constraints):
    numerical_rules_generator = setup_numerical_rules_generator(JSON_index, metadata)
    numerical_rules_generator.add_normal_outlier_rule(veritas_constraints.general_constraints)
    rules = numerical_rules_generator.get_rules()

    assert len(rules) == expected_rules_length


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * DateRulesGenerator Tests  * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################

def test_add_date_outlier_rule():
    JSON_index = JSONIndex(2, 9)
    expected_rules_length = 1

    date_rules_generator = DateRulesGenerator(JSON_index)
    date_rules_generator.add_date_outlier_rule()
    rules = date_rules_generator.get_rules()

    assert len(rules) == expected_rules_length



