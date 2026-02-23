# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest

from test.fixtures.input import metadata, veritas_constraints
from test.fixtures.error_catalog_generation import dataset

from metadata_generation.utils.file_parsing import MetadataAttributeParser
from metadata_generation.veritas.datatypes import JSONIndex, JSONDescriptor, DataQualityTypeEnum, RuleTypeEnum

from metadata_generation.veritas.rule_table_generation.rule_generation import RuleFrame

from metadata_generation.veritas.error_catalog_generation.rule_execution import UniquenessRuleExecutor, ReferenceRuleExecutor, LowFrequencyRuleExecutor
from metadata_generation.veritas.error_catalog_generation.rule_execution import NormalOutlierRuleExecutor, UnitOutlierRuleExecutor, DateOutlierRuleExecutor
from metadata_generation.veritas.error_catalog_generation.error_tables import ErrorTablesBuilder


def setup_JSON_descriptor(metadata, JSON_index):
    metadata_attribute_parser = MetadataAttributeParser(metadata, JSON_index)
    JSON_descriptor = JSONDescriptor(metadata_attribute_parser)
    return JSON_descriptor


def setup_rule(JSON_index, data_quality_type, rule_type):
    rule_frame = RuleFrame(JSON_index, data_quality_type)
    rule = rule_frame.instantiate_new_rule(rule_type) 
    return rule


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * KeyRuleExecutor Tests * * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################

def test_uniqueness_rule_executor(dataset, metadata):
    JSON_index = JSONIndex(3, 0) #vehicleList - VehicleID
    JSON_descriptor = setup_JSON_descriptor(metadata, JSON_index)
    rule = setup_rule(JSON_index, DataQualityTypeEnum.KEY, RuleTypeEnum.KEY_IS_UNIQUE)

    UniquenessRuleExecutor(rule, dataset, JSON_descriptor).execute(ErrorTablesBuilder(), metadata)

def test_reference_rule_executor(dataset, metadata):
    JSON_index = JSONIndex(2, 0) #batteryTestSummary - VehicleID
    JSON_descriptor = setup_JSON_descriptor(metadata, JSON_index)
    rule = setup_rule(JSON_index, DataQualityTypeEnum.KEY, RuleTypeEnum.REFERENCE_KEY_EXISTS)

    ReferenceRuleExecutor(rule, dataset, JSON_descriptor).execute(ErrorTablesBuilder(), metadata)


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * CategoricalRuleExecutor Tests * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################
    
def test_low_frequency_rule_executor(dataset, metadata, veritas_constraints):
    JSON_index = JSONIndex(0, 1) #batteryList - BatteryManufacturer
    JSON_descriptor = setup_JSON_descriptor(metadata, JSON_index)
    rule = setup_rule(JSON_index, DataQualityTypeEnum.CATEGORICAL, RuleTypeEnum.LOW_FREQUENCY)

    LowFrequencyRuleExecutor(rule, dataset, JSON_descriptor, veritas_constraints).execute(ErrorTablesBuilder(), metadata)


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * *  NumericalRuleExecutor Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################
    
def test_normal_outlier_rule_executor(dataset, metadata, veritas_constraints):
    JSON_index = JSONIndex(1, 25) #batteryTestData - EnergyRemoved_kWh
    mean = -10.059
    std_dev =  7.64
    
    veritas_constraints.general_constraints.add_normality_constraint(mean, std_dev, JSON_index)
    JSON_descriptor = setup_JSON_descriptor(metadata, JSON_index)
    rule = setup_rule(JSON_index, DataQualityTypeEnum.NUMERICAL, RuleTypeEnum.NORMAL_OUTLIER)

    NormalOutlierRuleExecutor(rule, dataset, JSON_descriptor, veritas_constraints).execute(ErrorTablesBuilder(), metadata)

def test_unit_outlier_rule_executor(dataset, metadata, veritas_constraints):
    JSON_index = JSONIndex(1, 24) #batteryTestData - CapacityRemoved_Ah
    JSON_descriptor = setup_JSON_descriptor(metadata, JSON_index)
    rule = setup_rule(JSON_index, DataQualityTypeEnum.NUMERICAL, RuleTypeEnum.UNIT_OUTLIER)

    UnitOutlierRuleExecutor(rule, dataset, JSON_descriptor, veritas_constraints).execute(ErrorTablesBuilder(), metadata)


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * * DateRuleExecutor Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################

def test_date_outlier_rule_executor(dataset, metadata, veritas_constraints):
    JSON_index = JSONIndex(2, 9) #batteryTestSummary - Date_Of_Test
    JSON_descriptor = setup_JSON_descriptor(metadata, JSON_index)
    rule = setup_rule(JSON_index, DataQualityTypeEnum.DATE, RuleTypeEnum.DATE_OUTLIER)

    DateOutlierRuleExecutor(rule, dataset, JSON_descriptor, veritas_constraints).execute(ErrorTablesBuilder(), metadata)