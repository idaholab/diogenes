# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from ...utils.file_system_tools_proto import file_system_crawler, file_integrity_helper, json_loader
from ...utils.json_cleaning import ProjectMetadataCleaner

from ...settings import JsonSchemaValidationFilePaths, VeritasFilePaths


class JsonSchemaReader:

	@classmethod
	def read_schema(self):
		schema_file_path = file_system_crawler.get_isolated_file_path_from_directory(JsonSchemaValidationFilePaths.input_json_schema_directory_path)
		file_integrity_helper.verify_file_not_empty(schema_file_path)
		schema = json_loader.load_json(schema_file_path)
		return schema


class VeritasOutputMetadataReader:

	@classmethod
	def read_output_metadata(self):
		output_metadata_file_path = file_system_crawler.get_isolated_file_path_from_directory(VeritasFilePaths.output_metadata_directory_path)
		file_integrity_helper.verify_file_not_empty(output_metadata_file_path)
		metadata = json_loader.load_json(output_metadata_file_path)
		return metadata
