# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from ...settings import VeritasFilePaths

from ...metadata_generation_input import MetadataGenerationInput

from ...utils.file_system_tools import InputFilePathFinder
from ...utils.file_iterator import JSONIndexIterator
from ...utils.file_writer import VeritasFileWriter

from ...veritas.datatypes import TableRuleGenerationInput, AttributeRuleGenerationInput 
from ...veritas.rule_table_generation.rule_generation import RuleBookBuilder
from ...veritas.error_catalog_generation.rule_execution import RuleBookExecution
from ...veritas.scorecard_distillation.scorecard_distiller import DatasetQualityCharacterization


class FullAnalysisDriver:
        
    def set_input_file_paths(self) -> None:
        input_file_path_finder = InputFilePathFinder()
        self.__input_metadata_file_path = input_file_path_finder.get_metadata_file_path(VeritasFilePaths.input_metadata_directory_path)
    
    def set_veritas_file_writer(self, error_when_file_exists: bool) -> None:
        self.__veritas_file_writer = VeritasFileWriter(self.__input_metadata_file_path, error_when_file_exists)

    def generate_data_quality_rules(self, metadata_generation_input: MetadataGenerationInput) -> None:
        json_index_iterator = JSONIndexIterator(self.__input_metadata_file_path)
        rule_book_builder = RuleBookBuilder()

        for JSON_index in json_index_iterator.iterate():
            rule_generation_input = AttributeRuleGenerationInput(JSON_index, self.__input_metadata_file_path, metadata_generation_input)
            rule_book_builder.add_attribute_rules(rule_generation_input)
        for table_metadata_index in json_index_iterator.iterate_tables():
            rule_generation_input = TableRuleGenerationInput(table_metadata_index, self.__input_metadata_file_path, metadata_generation_input)
            rule_book_builder.add_table_rules(rule_generation_input)
        self.__rule_book = rule_book_builder.get_rule_book()
        self.__veritas_file_writer.write_rules(self.__rule_book)

    def execute_rules(self, metadata_generation_input: MetadataGenerationInput) -> None:
        rule_book_execution = RuleBookExecution()
        rule_book_execution.execute_rules(metadata_generation_input, self.__rule_book)
        
    def distill_data_quality_characterization(self, metadata_generation_input: MetadataGenerationInput) -> None:
        data_quality_characterization = DatasetQualityCharacterization()
        for dataset_file_name, dataset_file in metadata_generation_input.dataset_files:
            data_quality_characterization.add_table_data_quality(dataset_file_name, dataset_file.data_quality)
        self.__veritas_file_writer.write_json(data_quality_characterization, self.__input_metadata_file_path)
        metadata_generation_input.print_dataset()


class DistillationDriver:

    def set_distillation_file_paths(self):
        pass
        #TODO: Add this functionality    

    def distill_scorecard_from_error_catalog(self):
        pass
        #TODO: Add this functionality