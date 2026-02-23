# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import copy

from typing import Tuple

from ...veritas.datatypes import DataQualityClassEnum, RuleTypeEnum
from ...veritas.datatypes import CodependentRuleGroupEnum, AttributeRuleGenerationInput, TableRuleGenerationInput
from ...veritas.rule_table_generation.rule import Rule
from ...veritas.rule_table_generation.rule import ReferenceRuleParameters, UniquenessRuleParameters
from ...veritas.rule_table_generation.rule import NormalOutlierRuleParameters, UnitOutlierRuleParameters
from ...veritas.rule_table_generation.rule import LowFrequencyRuleParameters, DateOutlierRuleParameters
from ...veritas.rule_table_generation.rule import FormatOutlierRuleParameters
from ...veritas.rule_table_generation.rule import SequentialOutlierRuleParameters


"""
    Creates a unique ID for every new rule
"""

class RuleIDGenerator:

    def __init__(self, start_rule_ids_at: int ):
        self.__next_rule_id = start_rule_ids_at

    def generate_next_id(self):
        new_id = self.__next_rule_id
        self.__next_rule_id += 1
        return new_id
    
    def peek_next_id(self):
        return self.__next_rule_id


class CodependentRuleGroup:

    def __init__(self, rule_group_ID: CodependentRuleGroupEnum):
        self.__codependent_rules = []
        self.__rule_group_ID = rule_group_ID

    @property
    def rule_group_ID(self): 
        return self.__rule_group_ID
    
    @property
    def rule_type(self) -> RuleTypeEnum: 
        if len(self.__codependent_rules) == 0:
            return None
        return self.__codependent_rules[0].rule_type
    
    @property
    def active_rule(self):
        is_active_rule = False
        for rule in self.__codependent_rules:
            if rule.active_rule == True:
                is_active_rule = True
        return is_active_rule

    def add_rule(self, rule: Rule) -> None:
        self.__codependent_rules.append(rule)

    def iterate(self, iterate_inactive_rules: bool = False) -> Rule:
        for rule in self.__codependent_rules:
            if rule.active_rule or iterate_inactive_rules:
                yield copy.deepcopy(rule)


""" 
    A codependent rule will have its group codes potentially affected by the 
    the execution of another. E.g. a record is more likely to be missing 
    when it is referenced in several tables but is not present in their primary key table.
"""

class CodependentRules:

    def __init__(self):
        self.__codependent_rules = {}

    def iterate(self, iterate_inactive_rule_groups=False) -> CodependentRuleGroup:
        for _, rule_group in self.__codependent_rules.items():
            if rule_group.active_rule or iterate_inactive_rule_groups:
                yield rule_group

    def add_rule(self, rule: Rule) -> None:
        if rule == None: 
            return 
        rule_parameters = rule.rule_parameters
        codependent_rule_id = rule_parameters.codependent_rule_ID
        if codependent_rule_id not in self.__codependent_rules.keys():
            self.__codependent_rules[codependent_rule_id] = CodependentRuleGroup(rule_parameters.codependent_rule_type)
        self.__codependent_rules[codependent_rule_id].add_rule(rule)


""" 
    An independent rule will not have its group codes affected by the execution of other rules. 
"""

class IndependentRules:

    def __init__(self):
        self.__rules = []

    def iterate(self, iterate_inactive_rules: bool = False) -> Rule:
        for rule in self.__rules:
            if rule.active_rule or iterate_inactive_rules:
                yield copy.deepcopy(rule)

    def add_rule(self, rule: Rule) -> None:
        self.__rules.append(rule)


class ForeignKeyRuleFactory: 

    def generate_rules(self, rule_generation_input: TableRuleGenerationInput, rule_ID_generator: RuleIDGenerator) -> Rule: 
        metadata_table_parser = rule_generation_input.initialize_metadata_table_parser()
        if not metadata_table_parser.in_table_values("relationships"): 
            return None
        if not metadata_table_parser.in_relationships("refersToPrimaryKeyTables"): 
            return None
        for referenced_primary_key_table, key_ID in metadata_table_parser.get_primary_key_table_references():
            rule_parameters = ReferenceRuleParameters(rule_generation_input)
            rule_parameters.initialize_parameters(rule_generation_input, (referenced_primary_key_table, key_ID))
            rule = Rule(rule_ID_generator.generate_next_id(), RuleTypeEnum.REFERENCED_PRIMARY_KEY_EXISTS, rule_parameters)
            yield rule


class AttributeRuleFactory: 

    def __init__(self): 
        self.__rule_factory_registry = {
                                        DataQualityClassEnum.PRIMARY_KEY : [('independent', RuleTypeEnum.PRIMARY_KEY_IS_UNIQUE, UniquenessRuleParameters)], \
                                        DataQualityClassEnum.COMPOSITE_PRIMARY_KEY : [('independent', RuleTypeEnum.PRIMARY_KEY_IS_UNIQUE, UniquenessRuleParameters)], \
                                        DataQualityClassEnum.COMPOSITE_PRIMARY_KEY_FOREIGN_KEY : [('independent', RuleTypeEnum.PRIMARY_KEY_IS_UNIQUE, UniquenessRuleParameters)], \
                                        DataQualityClassEnum.CATEGORICAL : [('independent', RuleTypeEnum.LOW_FREQUENCY, LowFrequencyRuleParameters)], \
                                        DataQualityClassEnum.NUMERICAL : [('independent', RuleTypeEnum.NORMAL_OUTLIER, NormalOutlierRuleParameters), \
                                                                            ('independent', RuleTypeEnum.UNIT_OUTLIER, UnitOutlierRuleParameters)], \
                                        DataQualityClassEnum.DATE : [('independent', RuleTypeEnum.DATE_OUTLIER, DateOutlierRuleParameters),
                                                                    ('independent', RuleTypeEnum.FORMAT_OUTLIER, FormatOutlierRuleParameters)],
                                        DataQualityClassEnum.DATE_TIME : [('independent', RuleTypeEnum.DATE_OUTLIER, DateOutlierRuleParameters),
                                                                         ('independent', RuleTypeEnum.FORMAT_OUTLIER, FormatOutlierRuleParameters)],
                                        DataQualityClassEnum.TIME: [('independent', RuleTypeEnum.DATE_OUTLIER, DateOutlierRuleParameters),
                                                                         ('independent', RuleTypeEnum.FORMAT_OUTLIER, FormatOutlierRuleParameters)],
                                        DataQualityClassEnum.SEQUENCE : [('independent', RuleTypeEnum.SEQUENTIAL_OUTLIER, SequentialOutlierRuleParameters)] 
                                       }

    def generate_rules(self, rule_generation_input: AttributeRuleGenerationInput, data_quality_type: DataQualityClassEnum, 
                       rule_ID_generator: RuleIDGenerator) -> tuple[str, Rule]: 
        if data_quality_type not in self.__rule_factory_registry.keys():
            return
        for rule_set, rule_type, rule_parameters_class in self.__rule_factory_registry[data_quality_type]:
            rule_parameters = rule_parameters_class()
            rule_parameters.initialize_parameters(rule_generation_input)
            rule = Rule(rule_ID_generator.generate_next_id(), rule_type, rule_parameters)
            yield (rule_set, rule)
    

class RuleBook:

    def __init__(self, codependent_rules: CodependentRules, independent_rules: IndependentRules):
        self.__codependent_rules = codependent_rules
        self.__independent_rules = independent_rules

    def iterate_codependent_rule_groups(self, iterate_inactive_rules: bool = False):
        for rule_group in self.__codependent_rules.iterate(iterate_inactive_rules):
            yield rule_group

    def iterate_independent_rules(self, iterate_inactive_rules: bool = False):
        for rule in self.__independent_rules.iterate(iterate_inactive_rules):
            yield rule


class RuleBookBuilder:

    def __init__(self):
        self.__rule_sets = {'codependent': CodependentRules(), 'independent': IndependentRules()}
        self.__attribute_rule_factory = AttributeRuleFactory()
        self.__foreign_key_rule_factory = ForeignKeyRuleFactory()
        self.__rule_id_generator = RuleIDGenerator(0)

    def add_table_rules(self, rule_generation_input: TableRuleGenerationInput) -> None:
        for rule in self.__foreign_key_rule_factory.generate_rules(rule_generation_input, self.__rule_id_generator):
            self.__rule_sets['codependent'].add_rule(rule)

    def add_attribute_rules(self, rule_generation_input: AttributeRuleGenerationInput) -> None:
        metadata_attribute_parser = rule_generation_input.initialize_metadata_attribute_parser()
        data_quality_type_str = metadata_attribute_parser.get_data_quality_class()
        data_quality_type = DataQualityClassEnum(data_quality_type_str)
        for (rule_set, rule) in self.__attribute_rule_factory.generate_rules(rule_generation_input, data_quality_type, 
                                                                             self.__rule_id_generator): 
            self.__rule_sets[rule_set].add_rule(rule)
        
    def get_rule_book(self) -> RuleBook:
        codependent_rules = self.__rule_sets['codependent']
        independent_rules = self.__rule_sets['independent']
        return RuleBook(copy.deepcopy(codependent_rules), copy.deepcopy(independent_rules))