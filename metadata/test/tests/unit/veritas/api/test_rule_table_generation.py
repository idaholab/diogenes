# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest

from test.fixtures.input import good_metadata_file_path as metadata_file_path
from test.fixtures.input import veritas_constraints

from metadata_generation.veritas.datatypes import JSONIndex

from metadata_generation.veritas.api.rule_table_generation import RuleTableGenerator


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * RuleTableGenerator Tests  * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'JSON_index, expected_rule_length',
    [(JSONIndex(0, 0), 0),
     (JSONIndex(2, 10), 2)],
)
def test_add_attribute_rules_to_tables(JSON_index, expected_rule_length, metadata_file_path, veritas_constraints):
    rule_table_generator = RuleTableGenerator(metadata_file_path)
    rule_table_generator.add_attribute_rules_to_tables(JSON_index, veritas_constraints)
    rules = rule_table_generator.get_rules()

    assert len(rules) == expected_rule_length
