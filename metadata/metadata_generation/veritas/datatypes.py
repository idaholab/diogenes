# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import copy 

from dataclasses import dataclass

from typing import Iterator

from enum import Enum, auto

from ..utils.file_system_tools import load_json
from ..utils.file_parsing import MetadataAttributeParser, MetadataTableParser
from ..utils.string_ops import separate_strings_with_underscore


"""
    This enum group is explicit because incoming annotation 
    tags are converted into enums and must have specific values
"""

class DataQualityClassEnum(Enum):
    PRIMARY_KEY = 'primary_key'
    COMPOSITE_PRIMARY_KEY = 'composite_primary_key'
    FOREIGN_KEY = 'foreign_key'
    COMPOSITE_FOREIGN_KEY = 'composite_foreign_key'
    COMPOSITE_PRIMARY_KEY_FOREIGN_KEY = 'composite_primary_key_foreign_key'
    SEQUENCE = 'sequence'
    CATEGORICAL = 'categorical'
    NUMERICAL = 'numerical'
    DATE = 'date'
    DATE_TIME = 'date-time'
    TIME = 'time'
    NONE = 'none'


class CodependentRuleGroupEnum(Enum):
    PRIMARY_KEY_REFERENCE_CHECKS = auto()
    COMPOSITE_PRIMARY_KEY_REFERENCE_CHECKS = auto()


class RuleTypeEnum(Enum):
    PRIMARY_KEY_IS_UNIQUE = auto()
    REFERENCED_PRIMARY_KEY_EXISTS = auto()
    LOW_FREQUENCY = auto()
    NORMAL_OUTLIER = auto()
    UNIT_OUTLIER = auto()
    DATE_OUTLIER = auto()
    TIME_OUTLIER = auto()
    FORMAT_OUTLIER = auto()
    SEQUENTIAL_OUTLIER = auto()


class RuleTypeDescriptions:

    def __init__(self):
        self.__descriptions = {
            RuleTypeEnum.PRIMARY_KEY_IS_UNIQUE : 'PRIMARY_KEY_IS_UNIQUE: Primary key must be unique', 
            RuleTypeEnum.REFERENCED_PRIMARY_KEY_EXISTS : 'REFERENCED_PRIMARY_KEY_EXISTS: Foreign key must have corresponding primary key',
            RuleTypeEnum.LOW_FREQUENCY : 'LOW_FREQUENCY: Categorical frequency must be above threshold',
            RuleTypeEnum.NORMAL_OUTLIER : 'NORMAL_OUTLIER: Value must be within standard deviation limit', 
            RuleTypeEnum.UNIT_OUTLIER : 'UNIT_OUTLIER: Value must be within unit constraints',
            RuleTypeEnum.DATE_OUTLIER : 'DATE_OUTLIER: Date must be within range',
            RuleTypeEnum.TIME_OUTLIER : 'TIME_OUTLIER: Time must be within range',
            RuleTypeEnum.FORMAT_OUTLIER : 'FORMAT_OUTLIER: Date/Time must be within format',
            RuleTypeEnum.SEQUENTIAL_OUTLIER: 'SEQUENTIAL_OUTLIER: Value abnormally distant from its immediate, sequential neighbors'
        }

    def get_description(self, rule_type: RuleTypeEnum) -> str:
        description = self.__descriptions[rule_type] 
        return description

"""
    Groups detail how a record is erroneous in aggregate. Does the record affect most records
    for an attribute, suggesting an overapplied rule? Is a reference to the same key missing 
    across multiple tables? All this allows for a more nuanced data quality assignment.
"""

class GeneralGroupIDEnum(Enum):
    AFFECTS_MANY_RECORDS = auto()
    AFFECTS_SOME_RECORDS = auto()
    AFFECTS_FEW_RECORDS = auto()


class ReferenceGroupIDEnum(Enum):
    MULTI_RECORD = auto()
    MULTI_TABLE = auto()
    SINGLE_RECORD = auto()


class LowFrequencyGroupIDEnum(Enum):
    MULTIPLE_SUB_THRESHOLD = auto()
    FEW_SUB_THRESHOLD = auto()
    SINGLE_SUB_THRESHOLD = auto()


"""
    LocationID marks how a record is in error. Slightly different than just saying, 
    'it was affected by this rule' there are subtle semantic differences as noted with
    the location IDs denoting a record whether a record is outside the third or fourth standard deviation.
"""

class LocationIDEnum(Enum):
    MISSING_PRIMARY_KEY = auto()
    ORPHAN_FOREIGN_KEY = auto()
    UNIQUENESS_VIOLATION = auto()
    LOW_FREQUENCY = auto()
    OUTSIDE_THREE_STD_DEV = auto()
    OUTSIDE_FOUR_STD_DEV = auto()
    UNIT_OUTLIER = auto()
    DATE_OUTLIER = auto()
    TIME_OUTLIER = auto()
    FORMAT_OUTLIER = auto()
    SEQUENTIAL_OUTLIER = auto()


@dataclass
class Key:

    def __init__(self, metadata_refers_to_entry: str):
        self.table_name = None
        self.attributes = None


@dataclass


class Key:

    def __init__(self, table_name: str, attribute_names: list[str]): 
        self._table_name = table_name
        self._attribute_names = attribute_names
        self._composite_key = False
        if len(self._attribute_names) > 1:
            self._composite_key = True

    def __str__(self) -> str:
        return f"Key(table_name={self.table_name}, attribute_names={self._attribute_names}, key_name={self.full_key_name})"

    @property
    def key_name(self) -> str:
        if self._composite_key == True:
            return 'composite_key'
        else:
            return self._attribute_names[0]
    
    @property
    def full_key_name(self) -> str:
        return separate_strings_with_underscore(self._attribute_names)

    @property
    def alphabetized_full_key_name(self) -> str:
        return separate_strings_with_underscore(self._attribute_names, alphabetize=True)
    
    def attribute_names(self, ordered=False) -> list[str]:
        attributes = self._attribute_names
        if ordered == True:
            attributes = sorted(self._attribute_names, key=str.lower)
        return attributes

    @property
    def table_name(self) -> str:
        return self._table_name
    
    @property
    def is_composite_key(self) -> bool: 
        return self._composite_key
    

class ForeignKey(Key):

    def __init__(self, table_name: str, attribute_names: list[str], 
                 primary_key_table_name: str, primary_key_attribute_names: list[str]): 
        super().__init__(table_name, attribute_names)
        self._primary_key = Key(primary_key_table_name, primary_key_attribute_names)
        if len(attribute_names) != len(primary_key_attribute_names):
            error_msg = (f"Length of attributes for primary key must equal length of attributes for foreign key table {table_name} \n"
                         f"Expected {len(attribute_names)} but got {len(primary_key_attribute_names)}")
            raise ValueError(error_msg)
        self._corresponding_primary_key_names = list(zip(attribute_names, primary_key_attribute_names))

    def __str__(self) -> str:
        return f"Key(table_name={self.table_name}, primary_key_table_name={self.primary_key_table_name}, attribute_names={self._attribute_names}, key_name={self.full_key_name})"

    def get_primary_key_from_foreign_key(self, foreign_key_attribute_lookup: str) -> str:
        return self._get_corresponding_key_name(foreign_key_attribute_lookup)
    
    def get_foreign_key_from_primary_key(self, primary_key_attribute_lookup: str) -> str:
        return self._get_corresponding_key_name(primary_key_attribute_lookup, primary_to_foreign=True)
        
    def _get_corresponding_key_name(self, attribute_lookup: str, primary_to_foreign: bool=False) -> str:            
        corresponding_key_name = None
        for foreign_primary_key_pairs in self._corresponding_primary_key_names:
            current_lookup, potential_sought_key = foreign_primary_key_pairs            
            if primary_to_foreign == True: 
                current_lookup, potential_sought_key = reversed(foreign_primary_key_pairs)
            if current_lookup == attribute_lookup:
                corresponding_key_name = potential_sought_key
                break
        if corresponding_key_name == None:
            error_msg = (f"(potentially partial) key lookup {attribute_lookup} does not exist")
            raise ValueError(error_msg)
        return corresponding_key_name
    
    @property
    def alphabetized_primary_key_name(self) -> str:
        return self._primary_key.alphabetized_full_key_name
    
    @property
    def alphabetized_primary_key(self) -> str:
        return self._primary_key.attribute_names(ordered=True)
    
    def foreign_key(self, order_by_primary_key=False) -> list[str]:
        if order_by_primary_key == True: 
            ordered_foreign_keys = []
            for partial_primary_key in self.alphabetized_primary_key:
                for foreign_key, primary_key in self._corresponding_primary_key_names:
                    if primary_key == partial_primary_key:
                        ordered_foreign_keys.append(foreign_key)
            return ordered_foreign_keys
        return self._attribute_names
    
    @property
    def primary_key_table_name(self) -> str:
        return self._primary_key.table_name
    
    @property
    def primary_key_attribute_name(self) -> str:
        return self._primary_key.key_name
    
    @property
    def primary_key(self) -> Key:
        return copy.deepcopy(self._primary_key)
    

@dataclass
class JSONIndex:

    table_metadata_index: int = -1
    attribute_metadata_index: int = -1


class TableRuleGenerationInput:

    def __init__(self, table_index: int, input_metadata_file_path: str, metadata_generation_input: object):
        self.table_index = table_index
        self.metadata = load_json(input_metadata_file_path)

    def initialize_metadata_table_parser(self) -> MetadataTableParser:
        metadata_table_parser = MetadataTableParser(self.metadata, self.table_index)
        return metadata_table_parser


class AttributeRuleGenerationInput(TableRuleGenerationInput):
    
    def __init__(self, JSON_index: JSONIndex, input_metadata_file_path: str, metadata_generation_input: object):
        super().__init__(JSON_index.table_metadata_index, input_metadata_file_path, metadata_generation_input)
        self.JSON_index = JSON_index
        self.general_constraints = metadata_generation_input.general_constraints
        self.unit_constraints = metadata_generation_input.unit_constraints 

    def initialize_metadata_attribute_parser(self) -> MetadataAttributeParser:
        metadata_attribute_parser = MetadataAttributeParser(self.metadata, self.JSON_index)
        return metadata_attribute_parser
    



