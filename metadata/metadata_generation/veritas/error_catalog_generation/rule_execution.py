# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from abc import ABC, abstractmethod

from ...veritas.datatypes import RuleTypeEnum, LocationIDEnum, ForeignKey
from ...veritas.datatypes import CodependentRuleGroupEnum, ReferenceGroupIDEnum
from ...metadata_generation_input import MetadataGenerationInput
from ...dataframe import DatasetFile

from ...veritas.rule_table_generation.rule_generation import RuleBook, CodependentRuleGroup
from ...veritas.rule_table_generation.rule import Rule, TableRuleParameters, AttributeRuleParameters
from ...veritas.rule_table_generation.rule import LowFrequencyRuleParameters, NormalOutlierRuleParameters
from ...veritas.rule_table_generation.rule import UnitOutlierRuleParameters, DateOutlierRuleParameters
from ...veritas.rule_table_generation.rule import SequentialOutlierRuleParameters

from ...veritas.error_catalog_generation.id_tags import IDTag, PercentErroneousBasedIDTag, LowFrequencyBasedIDTag
from ...veritas.error_catalog_generation.error_state import  ErrorStateRegistry
from ...veritas.error_catalog_generation.result import MissingResult

from _strptime import TimeRE


class IndependentRuleExecutionStrategy(): 

    @abstractmethod
    def execute_rule(self, dataset_file: DatasetFile, rule_parameters: AttributeRuleParameters) -> None: 
        pass


class CodependentRuleExecutionStrategy():

    @abstractmethod
    def precondition_data(self, metadata_generation_input: MetadataGenerationInput, 
                          rule_parameter: TableRuleParameters) -> None:
        pass

    @abstractmethod
    def postcondition_data(self, metadata_generation_input: MetadataGenerationInput, 
                           rule_parameter: TableRuleParameters) -> None:
        pass

    @abstractmethod
    def execute_rule(self, metadata_generation_input: MetadataGenerationInput, 
                     rule_parameter: TableRuleParameters) -> None:
        pass


class ReferenceKeyStrategy(CodependentRuleExecutionStrategy):

    def _get_correct_tables(self, metadata_generation_input: MetadataGenerationInput, 
                            foreign_key: ForeignKey) -> tuple[DatasetFile, DatasetFile]:
        foreign_key_table = metadata_generation_input.get_dataset_file(foreign_key.table_name)
        primary_key_table = metadata_generation_input.get_dataset_file(foreign_key.primary_key_table_name)       
        return foreign_key_table, primary_key_table

    def precondition_data(self, metadata_generation_input: MetadataGenerationInput, rule_group: CodependentRuleGroup) -> None:
        for rule in rule_group.iterate(): 
            foreign_key = rule.rule_parameters.foreign_key
            foreign_key_table, primary_key_table = self._get_correct_tables(metadata_generation_input, foreign_key) 
            if rule.rule_parameters.codependent_rule_type == CodependentRuleGroupEnum.COMPOSITE_PRIMARY_KEY_REFERENCE_CHECKS:
                foreign_key_table.create_composite_key(foreign_key.foreign_key(order_by_primary_key=True))
                primary_key_table.create_composite_key(foreign_key.alphabetized_primary_key) 

    def postcondition_data(self, metadata_generation_input: MetadataGenerationInput, rule_group: CodependentRuleGroup) -> None:
        for rule in rule_group.iterate():
            foreign_key = rule.rule_parameters.foreign_key
            foreign_key_table, primary_key_table = self._get_correct_tables(metadata_generation_input, foreign_key) 
            if rule.rule_parameters.codependent_rule_type == CodependentRuleGroupEnum.COMPOSITE_PRIMARY_KEY_REFERENCE_CHECKS:
                foreign_key_table.drop_composite_key()
        if rule.rule_parameters.codependent_rule_type == CodependentRuleGroupEnum.COMPOSITE_PRIMARY_KEY_REFERENCE_CHECKS: 
            primary_key_table.drop_composite_key() 

    def execute_rule(self, metadata_generation_input: MetadataGenerationInput, rule_group: CodependentRuleGroup) -> MissingResult:            
        missing_result = MissingResult()
        for rule in rule_group.iterate(): 
            foreign_key = rule.rule_parameters.foreign_key
            foreign_key_table, primary_key_table = self._get_correct_tables(metadata_generation_input, foreign_key) 
            missing_df = foreign_key_table.get_rows_with_missing_values_from_compared(primary_key_table, foreign_key)
            missing_result.add_to_result(foreign_key, missing_df)  
        missing_result.primary_key = foreign_key.primary_key
        missing_result.tabulate_table_occurrences()
        return missing_result
    
    def assign_error_values(self, metadata_generation_input: MetadataGenerationInput, missing_result: MissingResult, logging_attribute_name: str):
        if missing_result.empty_result: 
            return
        primary_key_table = metadata_generation_input.get_dataset_file(missing_result.primary_key.table_name)
        for result_subset_type in [ReferenceGroupIDEnum.SINGLE_RECORD, ReferenceGroupIDEnum.MULTI_RECORD, ReferenceGroupIDEnum.MULTI_TABLE]:
            result_subset = missing_result.get_result_df(result_subset_type)
            primary_key_table.add_missing(result_subset.num_records_missing)
            for foreign_key in missing_result.foreign_keys_with_missing_records:
                foreign_key_table = metadata_generation_input.get_dataset_file(foreign_key.table_name)
                foreign_key_table.change_record_probability_for_missing(foreign_key.key_name, 
                                                                        result_subset.records_df, 
                                                                        result_subset.orphan_key_error_state,
                                                                        logging_attribute_name)
            

class KeyUniquenessStrategy(IndependentRuleExecutionStrategy):

    def execute_rule(self, dataset_file: DatasetFile, rule_parameters: AttributeRuleParameters) -> None:
        primary_key = rule_parameters.primary_key
        if primary_key.is_composite_key == True:
            dataset_file.create_composite_key(primary_key.attribute_names())
        duplicate_IDs = dataset_file.get_rows_with_duplicate_values(primary_key.key_name)
        id_tags = PercentErroneousBasedIDTag()
        id_tags.location_ID = (LocationIDEnum.UNIQUENESS_VIOLATION, duplicate_IDs)
        id_tags.group_ID = (duplicate_IDs, dataset_file.num_rows)
        error_state = ErrorStateRegistry.get_error_state(id_tags)
        dataset_file.change_record_probability_lookup_index(primary_key.key_name, duplicate_IDs, error_state)
        if primary_key.is_composite_key == True:
            dataset_file.drop_composite_key()


class LowFrequencyStrategy(IndependentRuleExecutionStrategy): 

    def execute_rule(self, dataset_file: DatasetFile, rule_parameters: LowFrequencyRuleParameters) -> None:
        low_frequency_values = dataset_file.get_rows_where_attribute_values_equal(rule_parameters.attribute_name, 
                                                                                  rule_parameters.low_frequency_values)
        id_tags = LowFrequencyBasedIDTag()
        id_tags.location_ID = LocationIDEnum.LOW_FREQUENCY
        id_tags.group_ID = rule_parameters.number_of_low_frequency_values
        error_state = ErrorStateRegistry.get_error_state(id_tags)
        dataset_file.change_record_probability_lookup_index(rule_parameters.attribute_name, low_frequency_values, error_state)


class NormalOutlierStrategy(IndependentRuleExecutionStrategy):

    def execute_rule(self, dataset_file: DatasetFile, rule_parameters: NormalOutlierRuleParameters) -> None:
        self._execute_normal_outlier_rule(dataset_file, 3, rule_parameters, LocationIDEnum.OUTSIDE_THREE_STD_DEV, bounded=True)
        self._execute_normal_outlier_rule(dataset_file, 4, rule_parameters, LocationIDEnum.OUTSIDE_FOUR_STD_DEV, bounded=False)

    def _execute_normal_outlier_rule(self, dataset_file: DatasetFile, std_devs: int, 
                                     rule_parameters: NormalOutlierRuleParameters, 
                                     location_ID: LocationIDEnum,
                                     bounded):
        range_std_dev_low, range_std_dev_high = rule_parameters.get_constraint_ranges_x_std_devs_from_mean(std_devs, bounded)
        outside_range_df = dataset_file.get_values_outside_std_dev(rule_parameters.attribute_name,
                                                                   range_std_dev_low, range_std_dev_high)
        id_tags = PercentErroneousBasedIDTag()
        id_tags.location_ID = (location_ID, outside_range_df)
        id_tags.group_ID = (outside_range_df, dataset_file.num_rows)
        error_state = ErrorStateRegistry.get_error_state(id_tags)
        dataset_file.change_record_probability_lookup_index(rule_parameters.attribute_name, outside_range_df, error_state)


class UnitOutlierStrategy(IndependentRuleExecutionStrategy):

    def execute_rule(self, dataset_file: DatasetFile, rule_parameters: UnitOutlierRuleParameters) -> None:
        unit_outlier_df = dataset_file.get_rows_outside_numerical_constraint(rule_parameters.attribute_name, 
                                                                             rule_parameters.unit_constraint_range)
        id_tags = PercentErroneousBasedIDTag()
        id_tags.location_ID = (LocationIDEnum.UNIT_OUTLIER, unit_outlier_df)
        id_tags.group_ID = (unit_outlier_df, dataset_file.num_rows)
        error_state = ErrorStateRegistry.get_error_state(id_tags)
        dataset_file.change_record_probability_lookup_index(rule_parameters.attribute_name, unit_outlier_df, error_state)        


class DateOutlierStrategy(IndependentRuleExecutionStrategy):

    def execute_rule(self, dataset_file: DatasetFile, rule_parameters: DateOutlierRuleParameters) -> None:
        date_outlier_df = dataset_file.get_rows_outside_date_constraint(rule_parameters.attribute_name, 
                                                                        rule_parameters.date_constraint_range)
        id_tags = PercentErroneousBasedIDTag()
        id_tags.location_ID = (LocationIDEnum.DATE_OUTLIER, date_outlier_df)
        id_tags.group_ID = (date_outlier_df, dataset_file.num_rows)
        error_state = ErrorStateRegistry.get_error_state(id_tags)
        dataset_file.change_record_probability_lookup_index(rule_parameters.attribute_name, date_outlier_df, error_state) 


class FormatOutlierStrategy(IndependentRuleExecutionStrategy):
    def execute_rule(self, dataset_file: DatasetFile, rule_parameters: AttributeRuleParameters) -> None:
        format_str = rule_parameters.get_format()
        if format_str == None:
            # Do not run rule if not format specified.
            return
        
        time_re = TimeRE()
        format_regex = time_re.compile(format_str)
        format_outlier_df = dataset_file.get_rows_outside_format_constraint(rule_parameters.attribute_name, format_regex)

        id_tags = PercentErroneousBasedIDTag()
        id_tags.location_ID = (LocationIDEnum.FORMAT_OUTLIER, format_outlier_df)
        id_tags.group_ID = (format_outlier_df, dataset_file.num_rows)
        error_state = ErrorStateRegistry.get_error_state(id_tags)
        dataset_file.change_record_probability_lookup_index(rule_parameters.attribute_name, format_outlier_df, error_state)

class SequentialOutlierStrategy(IndependentRuleExecutionStrategy):

    def execute_rule(self, dataset_file: DatasetFile, rule_parameters: SequentialOutlierRuleParameters) -> None:
        sequential_outliers_df = dataset_file.identify_sequential_outliers(rule_parameters.attribute_name)
        id_tags = PercentErroneousBasedIDTag()
        id_tags.location_ID = (LocationIDEnum.SEQUENTIAL_OUTLIER, sequential_outliers_df)
        id_tags.group_ID = (sequential_outliers_df, dataset_file.num_rows)
        error_state = ErrorStateRegistry.get_error_state(id_tags)
        dataset_file.change_record_probability_lookup_index(rule_parameters.attribute_name, sequential_outliers_df, error_state)

class RuleExecutionStrategyRegistry():
    def __init__(self): 
        self.__registry =   {
                                RuleTypeEnum.PRIMARY_KEY_IS_UNIQUE : KeyUniquenessStrategy(), \
                                CodependentRuleGroupEnum.PRIMARY_KEY_REFERENCE_CHECKS: ReferenceKeyStrategy(), \
                                CodependentRuleGroupEnum.COMPOSITE_PRIMARY_KEY_REFERENCE_CHECKS: ReferenceKeyStrategy(), \
                                RuleTypeEnum.LOW_FREQUENCY: LowFrequencyStrategy(), \
                                RuleTypeEnum.NORMAL_OUTLIER: NormalOutlierStrategy(), \
                                RuleTypeEnum.UNIT_OUTLIER: UnitOutlierStrategy(), \
                                RuleTypeEnum.DATE_OUTLIER: DateOutlierStrategy(), \
                                RuleTypeEnum.FORMAT_OUTLIER: FormatOutlierStrategy(), \
                                RuleTypeEnum.SEQUENTIAL_OUTLIER: SequentialOutlierStrategy()
                            }

        
    def get_rule_execution_strategy(self, rule_type: RuleTypeEnum | CodependentRuleGroupEnum) -> IndependentRuleExecutionStrategy | CodependentRuleExecutionStrategy: 
        try: 
            return self.__registry[rule_type]
        except KeyError: 
            raise TypeError(f"Unrecognized rule type: {rule_type}")
   

class RuleBookExecution: 

    def __init__(self): 
        self.__rule_execution_strategy_registry = RuleExecutionStrategyRegistry()

    def execute_rules(self, metadata_generation_input: MetadataGenerationInput, rule_book: RuleBook) -> None: 
        for rule in rule_book.iterate_independent_rules():
            strategy = self.__rule_execution_strategy_registry.get_rule_execution_strategy(rule.rule_type)
            rule_parameters = rule.rule_parameters
            dataset_file = metadata_generation_input.get_dataset_file(rule_parameters.table_name)
            strategy.execute_rule(dataset_file, rule_parameters)
        for rule_group in rule_book.iterate_codependent_rule_groups():
            strategy = self.__rule_execution_strategy_registry.get_rule_execution_strategy(rule_group.rule_group_ID)
            strategy.precondition_data(metadata_generation_input, rule_group)
            missing_result = strategy.execute_rule(metadata_generation_input, rule_group)
            strategy.assign_error_values(metadata_generation_input, missing_result, 'composite_foreign_key')
            strategy.postcondition_data(metadata_generation_input, rule_group)