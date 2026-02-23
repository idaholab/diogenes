# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import sys, copy

from dataclasses import dataclass
from ...veritas.datatypes import AttributeRuleGenerationInput, Key, ForeignKey, DataQualityClassEnum

from ...veritas.datatypes import RuleTypeEnum, CodependentRuleGroupEnum
from ...veritas.datatypes import AttributeRuleGenerationInput, RuleTypeDescriptions

from ...utils.constraints import Constraint, ConstraintRange
from ...utils.statistics import NormalDistribution


class TableRuleParameters():
    
    _table_name: str = None

    def initialize_parameters(self, rule_generation_input: AttributeRuleGenerationInput) -> None:
        metadata_table_parser = rule_generation_input.initialize_metadata_table_parser()
        self._table_name = metadata_table_parser.get_table_value('name')
        return metadata_table_parser  
    
    @property
    def table_name(self) -> str:
        return self._table_name      
    
    @property
    def attribute_name(self) -> str:
        return 'N/A'  
    
    @property
    def active_rule(self) -> bool: 
        return True
    

class AttributeRuleParameters(TableRuleParameters):
    
    _attribute_name: str = None
    
    def initialize_parameters(self, rule_generation_input: AttributeRuleGenerationInput) -> None:
        super().initialize_parameters(rule_generation_input)
        metadata_attribute_parser = rule_generation_input.initialize_metadata_attribute_parser()
        self._attribute_name = metadata_attribute_parser.get_attribute_name()
        return metadata_attribute_parser
    
    @property
    def attribute_name(self) -> str:
        return self._attribute_name
    

@dataclass
class Rule:

    _rule_id: int = -1
    _rule_type: RuleTypeEnum = None
    _rule_parameters: AttributeRuleParameters = None

    @property
    def rule_type(self) -> RuleTypeEnum:
        return self._rule_type

    @property
    def active_rule(self) -> bool:
        return self._rule_parameters.active_rule
    
    @property
    def rule_parameters(self) -> AttributeRuleParameters:
        return copy.deepcopy(self._rule_parameters)

    def format_rule_as_csv(self) -> str:        
        csv_rule = str(self._rule_id) + ','
        csv_rule += self._rule_parameters.table_name + ','
        csv_rule += self._rule_parameters.attribute_name + ','
        csv_rule += str(self._rule_parameters.active_rule) + ','
        rule_type_descriptions = RuleTypeDescriptions()
        csv_rule += rule_type_descriptions.get_description(self._rule_type) + '\n'
        return csv_rule
    

@dataclass
class UniquenessRuleParameters(AttributeRuleParameters): 

    _primary_key: Key = None
    _covered_under_another_rule: bool = False

    def initialize_parameters(self, rule_generation_input: AttributeRuleGenerationInput) -> None:
        metadata_attribute_parser = super().initialize_parameters(rule_generation_input)
        enumerated_data_quality_type = DataQualityClassEnum(metadata_attribute_parser.get_data_quality_class())
        self._primary_key = Key(self._table_name, [self._attribute_name])
        if enumerated_data_quality_type == DataQualityClassEnum.COMPOSITE_PRIMARY_KEY:
            metadata_table_parser = rule_generation_input.initialize_metadata_table_parser()
            primary_key_attributes = metadata_table_parser.get_primary_keys()
            self._primary_key = Key(self._table_name, primary_key_attributes)
            self._covered_under_another_rule = metadata_table_parser.composite_uniqueness_rule_previously_covered(self._attribute_name)
    
    @property
    def primary_key(self):
        return copy.deepcopy(self._primary_key)
    
    property
    def active_rule(self):
        active_rule = True
        if self._covered_under_another_rule == True: 
            active_rule = False
        return active_rule

@dataclass
class ReferenceRuleParameters(TableRuleParameters):

    _foreign_key: ForeignKey = None
    _covered_under_another_rule: bool = False

    def initialize_parameters(self, rule_generation_input: AttributeRuleGenerationInput, args = None) -> None:
        primary_key_table_name, key_ID = args
        metadata_table_parser = super().initialize_parameters(rule_generation_input)
        if not metadata_table_parser.in_table_values('relationships'):
            raise IOError(f"Table {self._table_name} has no relationships attribute.")
        if not metadata_table_parser.in_relationships("refersToPrimaryKeyTables"):
            raise IOError(f"Table {self._table_name} references no primary key tables.")
        primary_key_attributes = metadata_table_parser.get_key_attributes(primary_key_table_name, key_ID, "foreignKeyRefersTo")
        foreign_key_attributes = metadata_table_parser.get_key_attributes(primary_key_table_name, key_ID, "foreignKey")
        self._foreign_key = ForeignKey(self._table_name, foreign_key_attributes, primary_key_table_name, primary_key_attributes)
    
    @property
    def foreign_key(self) -> ForeignKey:
        return copy.deepcopy(self._foreign_key)
    
    @property
    def codependent_rule_ID(self): 
        return str(self._foreign_key.alphabetized_primary_key_name) + '_' + str(self._foreign_key.primary_key_table_name) 
    
    @property
    def codependent_rule_type(self) -> CodependentRuleGroupEnum:
        if self._foreign_key.is_composite_key == True:
            return CodependentRuleGroupEnum.COMPOSITE_PRIMARY_KEY_REFERENCE_CHECKS
        else:
            return CodependentRuleGroupEnum.PRIMARY_KEY_REFERENCE_CHECKS
    
    @property
    def active_rule(self):
        active_rule = True
        if self._covered_under_another_rule == True: 
            active_rule = False
        return active_rule


@dataclass 
class LowFrequencyRuleParameters(AttributeRuleParameters):

    _low_frequency_values: None

    def __init__(self): 
        self._low_frequency_values = []

    def initialize_parameters(self, rule_generation_input: AttributeRuleGenerationInput) -> None:
        metadata_attribute_parser = super().initialize_parameters(rule_generation_input)

        constraints = rule_generation_input.general_constraints
        for attribute_value, frequency_percent in metadata_attribute_parser.iterate_categorical():
            if not constraints.within_constraint('Frequency_Threshold', frequency_percent): 
                self._low_frequency_values.append(attribute_value)

    @property
    def low_frequency_values(self) -> list:
        return copy.deepcopy(self._low_frequency_values)
    
    @property
    def number_of_low_frequency_values(self) -> int: 
        return len(self._low_frequency_values)

    @property
    def active_rule(self):
        active_rule = True
        if self._low_frequency_values == []: 
            active_rule = False
        return active_rule


@dataclass
class NormalOutlierRuleParameters(AttributeRuleParameters):
    
    _normal_distribution = None

    def initialize_parameters(self, rule_generation_input: AttributeRuleGenerationInput) -> None:
        metadata_attribute_parser = super().initialize_parameters(rule_generation_input)   
        
        if not metadata_attribute_parser.in_data_quality_metrics('Skewness') or \
           not metadata_attribute_parser.in_data_quality_metrics('Kurtosis'):
            return
        
        skewness = metadata_attribute_parser.get_data_quality_metric('Skewness')
        kurtosis = metadata_attribute_parser.get_data_quality_metric('Kurtosis')
        if skewness == 0 or kurtosis == 0: 
            return
            #raise IOError(f'Skewness or Kurtosis equals zero for {self._table_name}: {self._attribute_name}. This is very unlikely. Verify data.')

        constraints = rule_generation_input.general_constraints
        skewness_is_normal = constraints.within_constraint('Skewness', skewness)
        kurtosis_is_normal = constraints.within_constraint('Kurtosis', kurtosis)

        if skewness_is_normal and kurtosis_is_normal:
            self._normal_distribution = NormalDistribution(float(metadata_attribute_parser.get_data_quality_metric('Mean')), 
                                                           float(metadata_attribute_parser.get_data_quality_metric('Standard Deviation')))

    def get_constraint_ranges_x_std_devs_from_mean(self, std_dev_from_mean: int, 
                                                   bounded: bool) -> tuple[ConstraintRange, ConstraintRange]:
        if bounded == True:
            constraint_ranges = (self._normal_distribution.bounded_range_x_std_devs_from_mean(-std_dev_from_mean),
                                 self._normal_distribution.bounded_range_x_std_devs_from_mean(std_dev_from_mean))
        else:
            constraint_ranges = (self._normal_distribution.unbounded_range_x_std_devs_from_mean(-std_dev_from_mean),
                                 self._normal_distribution.unbounded_range_x_std_devs_from_mean(std_dev_from_mean)) 

        return constraint_ranges           
    
    @property
    def active_rule(self): 
        active_rule = True
        if self._normal_distribution == None:
            active_rule = False
        return active_rule
            

@dataclass
class UnitOutlierRuleParameters(AttributeRuleParameters):

    _unit_constraint_name: str = None
    _unit_constraint: ConstraintRange = None
    _no_values_fall_outside_range: bool = False

    def initialize_parameters(self, rule_generation_input: AttributeRuleGenerationInput) -> None:
        metadata_attribute_parser = super().initialize_parameters(rule_generation_input)  

        units_exist = metadata_attribute_parser.in_attribute_values('units')
        if not units_exist:
            return
        
        unit_name = metadata_attribute_parser.get_attribute_value('units')
        unit_constraints = rule_generation_input.unit_constraints
        if not unit_constraints.in_constraints(unit_name) or metadata_attribute_parser.get_data_quality_metric('Count') == 0:
            return
        self._unit_constraint_name = unit_name
        self._unit_constraint = unit_constraints.get_constraint(unit_name) 
        
        min_value = metadata_attribute_parser.get_data_quality_metric('Minimum Value')
        max_value = metadata_attribute_parser.get_data_quality_metric('Maximum Value') 

        if unit_constraints.within_constraint(self._unit_constraint_name, max_value) and \
           unit_constraints.within_constraint(self._unit_constraint_name, min_value): 
              self._no_values_fall_outside_range = True

    @property
    def unit_constraint_name(self) -> str: 
        return self._unit_constraint_name
    
    @property
    def unit_constraint_range(self) -> ConstraintRange: 
        return copy.deepcopy(self._unit_constraint.get_constraint_range())

    @property
    def active_rule(self) -> bool: 
        active_rule = True
        if self._unit_constraint_name == None or self._unit_constraint == None: 
            active_rule = False
        elif self._no_values_fall_outside_range: 
            active_rule = False
        return active_rule


@dataclass
class DateOutlierRuleParameters(AttributeRuleParameters):

    _date_constraint: Constraint = None

    def initialize_parameters(self, rule_generation_input: AttributeRuleGenerationInput) -> None:
        super().initialize_parameters(rule_generation_input)
        general_constraints = rule_generation_input.general_constraints
        if not general_constraints.in_constraints("Date"):
            raise IOError("Date constraint not set within the general constraints")
        self._date_constraint = general_constraints.get_constraint("Date") 
    
    @property
    def date_constraint_range(self) -> ConstraintRange: 
        return copy.deepcopy(self._date_constraint.get_constraint_range())
    

# TODO: Ensure Format Parameters Function as Anticipated
@dataclass
class FormatOutlierRuleParameters(AttributeRuleParameters):
    
    _format_constraint: str = None

    def initialize_parameters(self, rule_generation_input: AttributeRuleGenerationInput) -> None:
        metadata_attribute_parser = super().initialize_parameters(rule_generation_input)
        units_exist = metadata_attribute_parser.in_attribute_values('units')
        if not units_exist:
            return
        
        unit_name = metadata_attribute_parser.get_attribute_value('units')
        format_str = None
        # TODO: Should this default to "mixed" or None?
        if unit_name != None and unit_name != "" and unit_name != "n/a":
            format_str = unit_name

        general_constraints = rule_generation_input.general_constraints
        if not general_constraints.in_constraints("Date-Format"):
            raise IOError("Format constraint not set within the general constraints")
        
        self._format_constraint = format_str
    
    def get_format(self) -> str:
        return self._format_constraint

@dataclass
class SequentialOutlierRuleParameters(AttributeRuleParameters):

    _is_monotonic: bool = False
    
    def initialize_parameters(self, rule_generation_input: AttributeRuleGenerationInput) -> None:
        metadata_attribute_parser = super().initialize_parameters(rule_generation_input)
        if not metadata_attribute_parser.in_data_quality_metrics('Monotonicity Ratio'):
            return
        monotonicity_ratio = metadata_attribute_parser.get_data_quality_metric('Monotonicity Ratio')
        constraints = rule_generation_input.general_constraints
        self._is_monotonic = constraints.within_constraint('Monotonicity', monotonicity_ratio)
        
    @property
    def active_rule(self) -> bool: 
        active_rule = True
        if self._is_monotonic == False: 
            active_rule = False
        return active_rule
