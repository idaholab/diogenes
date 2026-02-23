# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from ...utils.file_system_tools import load_json

from ...veritas.rule_table_generation.rule_generation import AttributeRulesGenerator



class RuleTableGenerator:

    def __init__(self, metadata_file_path):
        self.__rule_id_count = 0
        self.__rules = []        
        self.__metadata = load_json(metadata_file_path)

    def add_attribute_rules_to_tables(self, metadata_generation_input, JSON_index):
        attribute_rules_generator = AttributeRulesGenerator(self.__metadata, JSON_index)
        new_rules = attribute_rules_generator.generate_rules(metadata_generation_input.general_constraints, metadata_generation_input.unit_constraints)

        for new_rule in new_rules:
            new_rule.set_rule_id(self.__rule_id_count)
            self.__rule_id_count += 1

        self.__rules += new_rules

    def get_rules(self):
        return self.__rules
