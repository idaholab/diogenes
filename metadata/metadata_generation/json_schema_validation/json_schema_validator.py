# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import math
import jsonschema
from jsonschema import validators

from ..utils.file_system_tools_proto.file_reader import JsonSchemaReader, VeritasOutputMetadataReader

def _is_finite_number(checker, instance):
    if isinstance(instance, bool):
        return False
    if isinstance(instance, int):
        return True
    if isinstance(instance, float):
        return math.isfinite(instance)
    return False

def _finite_number_validator():
    base = jsonschema.Draft7Validator
    type_checker = base.TYPE_CHECKER.redefine("number", _is_finite_number)
    return validators.extend(base, type_checker=type_checker)

class JsonSchemaValidator(object):

    def validate_json_schema(self):
        json_schema = JsonSchemaReader.read_schema()
        json = VeritasOutputMetadataReader.read_output_metadata()
        try:
            validator = _finite_number_validator()(json_schema)
            validator.validate(json)
            print('Schema...... valid')
        except Exception as e:
            print(e)
            print('Schema...... invalid')
            exit()



