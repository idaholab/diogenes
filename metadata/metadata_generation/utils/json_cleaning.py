# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from abc import ABC


class JSONCleaner(ABC):

    def __init__(self):
        # characters with subsequences that make up other characters should come first in the list to avoid partial replacement #

        self._bad_to_good_characters_map = [ ("\u00e2\u20ac\u201c", "-"),    # —
                                             ("\u00e2\u20ac\u201d", "-"),    # —
                                             ("\u00e2\u20ac\u0153", "\""),   # “ 
                                             ("\u00e2\u20ac", "\""),         # ”
                                             ("\u00ef\u00ac", "fi"),         # fi
                                             ("\u201d", "\""),               # “
                                             ("\ufb01", "fi"),               # fi? 
                                             ("\u00ad", "-"),                # -
                                             ("\ufb02", "fl"),               # fl? 
                                             ("\ufb00", "ff"),               # ff
                                             ("\ufb03", "ffi"),              # ffi
                                             ("\u00a1", "!"),                # upside down !
                                             ("\u00c2", "ti"),               # ti
                                             ("\\n", " ")                    # explicit endlines 
                                           ]

class ProjectMetadataCleaner(JSONCleaner):

    def replace_bad_characters(self, project_metadata):
        for dataset_index, dataset_metadata in enumerate(project_metadata['dataset']):
            for bad_character, good_character in self._bad_to_good_characters_map:
                dataset_metadata['title'] = dataset_metadata['title'].replace(bad_character, good_character)
                dataset_metadata['description'] = dataset_metadata['description'].replace(bad_character, good_character)
            project_metadata['dataset'][dataset_index] = dataset_metadata
     
        return project_metadata


class TableDescriptionsCleaner(JSONCleaner):

    def replace_bad_characters(self, table_descriptions):
        for table_name, table_description in table_descriptions.items():
            for bad_character, good_character in self._bad_to_good_characters_map:
                table_description = table_description.replace(bad_character, good_character)
            table_descriptions[table_name] = table_description

        return table_descriptions


class ColumnDescriptionsCleaner(JSONCleaner):

    def replace_bad_characters(self, column_description):
        for bad_character, good_character in self._bad_to_good_characters_map:
            column_description = column_description.replace(bad_character, good_character)
        return column_description