# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import warnings
import nltk

from ..settings import MAX_NUM_CHAR_VARIATIONS_NEEDED_FOR_KEY_WARNING

from ..utils.file_iterator import JSONIndexIterator, MetadataIterator
from ..utils.file_parsing import MetadataTableParser, MetadataAttributeParser

from ..veritas.datatypes import DataQualityClassEnum

def check_for_duplicate_primary_keys(unique_key_checks: dict, use_annotations: bool) -> None:
    for table, primary_key in unique_key_checks.items(): 
        for referring_table, referring_primary_key in unique_key_checks.items():
            if table == referring_table:
                continue
            if primary_key == referring_primary_key and use_annotations != True:
                raise ValueError(f"Duplicate primary keys from tables {table},{referring_table}. Manual annotations required. ")

def map_primary_keys_to_table(metadata: dict, use_annotations: bool) -> dict: 
    index_iterator = JSONIndexIterator(metadata=metadata)
    unique_key_checks = {}
    for JSON_index in index_iterator.iterate(): 
        metadata_attribute_parser = MetadataAttributeParser(metadata, JSON_index)
        metadata_table_parser = MetadataTableParser(metadata, JSON_index.table_metadata_index)
        data_quality_class = DataQualityClassEnum(metadata_attribute_parser.get_data_quality_class())
        if data_quality_class != DataQualityClassEnum.PRIMARY_KEY and \
           data_quality_class != DataQualityClassEnum.COMPOSITE_PRIMARY_KEY and \
           data_quality_class != DataQualityClassEnum.COMPOSITE_PRIMARY_KEY_FOREIGN_KEY:
            continue
        current_table = metadata['objects'][JSON_index.table_metadata_index]
        if not metadata_table_parser.in_relationships('primaryKeys'): 
            current_table['relationships']['primaryKeys'] = []
            unique_key_checks[metadata_attribute_parser.get_table_name()] = []
        attribute_name = metadata_attribute_parser.get_attribute_name()
        current_table['relationships']['primaryKeys'].append(attribute_name)
        unique_key_checks[metadata_attribute_parser.get_table_name()].append(attribute_name)
        metadata['objects'][JSON_index.table_metadata_index] = current_table
    check_for_duplicate_primary_keys(unique_key_checks, use_annotations)
    return metadata

def create_dictionary_of_primary_keys(metadata:dict) -> dict[list[str]]: 
    primary_keys = {}
    metadata_iterator = MetadataIterator(metadata)   
    for current_table_index in metadata_iterator.iterate_table(): 
        metadata_table_parser = MetadataTableParser(metadata, current_table_index)
        table_name = metadata_table_parser.get_table_value('name')
        if not metadata_table_parser.in_relationships('primaryKeys'): 
            continue
        primary_keys[table_name] = metadata_table_parser.get_primary_keys()
    return primary_keys

def calculate_Levenshtein(s1: str, comparing_strings: list[str]) -> list:
    levenshtein_distances = []
    for s2 in comparing_strings:
        distance = nltk.edit_distance(s1, s2)
        levenshtein_distances.append((s2, distance))
    return levenshtein_distances
        
def rank_key_matches(table_name: str, attribute_name: str, dataset_primary_keys) -> dict: 
    ranked_key_matches = {}
    for primary_key_table, primary_keys in dataset_primary_keys.items(): 
        if table_name == primary_key_table: 
            continue
        levenshtein_distances = calculate_Levenshtein(attribute_name, primary_keys)
        for primary_key, distance in levenshtein_distances:
            if distance > MAX_NUM_CHAR_VARIATIONS_NEEDED_FOR_KEY_WARNING:
                continue
            if 0 in ranked_key_matches.keys():
                raise IOError(f"Key {attribute_name} has multiple matching attributes across tables. Manual annotations required.")
            elif distance < MAX_NUM_CHAR_VARIATIONS_NEEDED_FOR_KEY_WARNING:
                warnings.warn(f"Key {attribute_name} has multiple close matches across tables. Manually annotate carefully.")
            ranked_key_matches[distance] = (primary_key_table, primary_key)
    return ranked_key_matches

def warning_for_close_primary_key_matches(table_name: str, attribute_name: str, ranked_key_matches: dict) -> None:
    closest_matched_key = None
    for i in range(MAX_NUM_CHAR_VARIATIONS_NEEDED_FOR_KEY_WARNING):
        if i in ranked_key_matches.keys(): 
            closest_matched_table, closest_matched_key = ranked_key_matches[i]
            break
    if closest_matched_key == None:
        return
    warnings.warn(f"Table: {table_name}, Attribute {attribute_name} has no matching key but has a close match \
                    (Table: {closest_matched_table}, Attribute: {closest_matched_key}) that is \
                    {closest_matched_key} variations away. \n\nConsider revising annotations to explicitly list relationships.") 

def map_table_foreign_keys(metadata: dict, current_table_index: int, dataset_primary_keys: dict) -> dict: 
    foreign_key_matches = {}
    metadata_table_parser = MetadataTableParser(metadata, current_table_index)   
    table_name = metadata_table_parser.get_table_value('name')
    current_table = metadata['objects'][current_table_index]
    if 'refersToPrimaryKeyTables' not in current_table['relationships'].keys(): 
        current_table['relationships']['refersToPrimaryKeyTables'] = {}
    for attribute_index, attribute_name in enumerate(metadata_table_parser.attributes()):
        data_quality_class = DataQualityClassEnum(metadata_table_parser.get_attribute_value(attribute_index, 'dataQualityClass'))
        if metadata_table_parser.attribute_reference_already_resolved(attribute_name) or \
           (data_quality_class != DataQualityClassEnum.NONE and
            data_quality_class != DataQualityClassEnum.COMPOSITE_PRIMARY_KEY): 
            continue
        key_match_rankings = rank_key_matches(table_name, attribute_name, dataset_primary_keys)
        if 0 not in key_match_rankings:
            warning_for_close_primary_key_matches(table_name, attribute_name, key_match_rankings)
            continue
        matched_primary_key_table, matched_primary_key = key_match_rankings[0]
        if matched_primary_key_table not in foreign_key_matches.keys():
            foreign_key_matches[matched_primary_key_table] = []
        if data_quality_class == DataQualityClassEnum.COMPOSITE_PRIMARY_KEY:
            current_table['attributes'][attribute_index]['dataQualityClass'] = 'composite_primary_key_foreign_key'
        elif data_quality_class == DataQualityClassEnum.FOREIGN_KEY: 
            current_table['attributes'][attribute_index]['dataQualityClass'] = 'foreign_key'
        elif len(dataset_primary_keys[matched_primary_key_table]) > 1:
            current_table['attributes'][attribute_index]['dataQualityClass'] = 'composite_foreign_key'
        #TODO automated annotation of multiple foreign keys referencing the same primary key attribute (keyID not equal to 0)
        foreign_key_matches[matched_primary_key_table].append({"foreignKey": attribute_name, "foreignKeyRefersTo": matched_primary_key, "keyID": 0})
    if not bool(foreign_key_matches):
        del current_table['relationships']['refersToPrimaryKeyTables']
        return metadata
    primary_key_table_references = current_table['relationships']['refersToPrimaryKeyTables']
    primary_key_table_references = primary_key_table_references.update(foreign_key_matches)
    current_table['relationships']['refersToPrimaryKeyTables'] = primary_key_table_references
    metadata['objects'][current_table_index] = current_table
    return metadata

def map_foreign_keys_to_table(metadata: dict, use_annotations: bool) -> dict:
    if use_annotations == True: 
        return metadata
    dataset_primary_keys = create_dictionary_of_primary_keys(metadata) 
    metadata_iterator = MetadataIterator(metadata)   
    for current_table_index in metadata_iterator.iterate_table(): 
        metadata = map_table_foreign_keys(metadata, current_table_index, dataset_primary_keys)
    return metadata