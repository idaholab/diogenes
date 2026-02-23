# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from ..utils.file_iterator import JSONIndexIterator
from ..utils.file_parsing import MetadataAttributeParser, MetadataTableParser

from ..veritas.datatypes import DataQualityClassEnum


def delete_manual_annotations(metadata: dict) -> dict: 
    JSON_index_iterator = JSONIndexIterator(metadata=metadata)
    for JSON_index in JSON_index_iterator.iterate(): 
        metadata_attribute_parser = MetadataAttributeParser(metadata, JSON_index)
        if metadata_attribute_parser.in_attribute_values('manual_annotations'):
            current_table = metadata['objects'][JSON_index.table_metadata_index]
            current_attribute = current_table['attributes'][JSON_index.attribute_metadata_index]
            del current_attribute['manual_annotations']
            current_table['attributes'][JSON_index.attribute_metadata_index] = current_attribute
            metadata['objects'][JSON_index.table_metadata_index] = current_table
    return metadata
  
def resolve_foreign_key_references(metadata: dict) -> dict:
    JSON_index_iterator = JSONIndexIterator(metadata=metadata)
    for JSON_index in JSON_index_iterator.iterate(): 
        current_table = metadata['objects'][JSON_index.table_metadata_index]
        metadata_table_parser = MetadataTableParser(metadata, JSON_index.table_metadata_index)
        metadata_attribute_parser = MetadataAttributeParser(metadata, JSON_index)
        if not metadata_attribute_parser.in_attribute_values('manual_annotations'):
            continue
        if not metadata_attribute_parser.in_manual_annotations('foreign_key_references'): 
            continue
        if not metadata_table_parser.in_relationships('refersToPrimaryKeyTables'):
            current_table['relationships']['refersToPrimaryKeyTables'] = {}
        attribute_name = metadata_attribute_parser.get_attribute_name()
        primary_key_table_references = current_table['relationships']['refersToPrimaryKeyTables']
        for foreign_key in metadata_attribute_parser.get_manual_annotation('foreign_key_references'):
            primary_key_table = foreign_key['table']
            primary_key = foreign_key['key']
            key_id = 0
            if "id" in foreign_key: 
                key_id = foreign_key['id']
            if primary_key_table not in primary_key_table_references.keys():
                primary_key_table_references[primary_key_table] = []
            primary_key_table_references[primary_key_table].append({"foreignKey": attribute_name, "foreignKeyRefersTo": primary_key, "keyID": key_id})
        current_table['relationships']['refersToPrimaryKeyTables'] = primary_key_table_references
        metadata['objects'][JSON_index.table_metadata_index] = current_table
    return metadata

def resolve_manual_table_annotations(metadata: dict) -> dict:
    metadata = resolve_foreign_key_references(metadata)
    metadata = delete_manual_annotations(metadata)
    return metadata