# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from ...utils.file_system_tools import load_json

from ...veritas.error_catalog_generation.rule_execution import RuleExecutor


class ErrorCatalogGenerator:


    def __init__(self, metadata_file_path):
        self.__error_tables = None
        self.__rule_executor = RuleExecutor()
        self.__metadata = load_json(metadata_file_path)


    def generate_error_catalog(self, metadata_generation_input, rules):
        for rule in rules:
            self.__rule_executor.execute_rule(rule, metadata_generation_input, self.__metadata)

        error_tables = self.__rule_executor.get_error_tables()
        return error_tables