# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

class TableDescriptionGenerator:

    def __init__(self, table_descriptions):
        self.__table_descriptions = table_descriptions

    def get_table_description(self, file_name):
        table_description = ""
        
        if self.__table_descriptions != None: 
            assert file_name in self.__table_descriptions.keys()
            table_description = self.__table_descriptions[file_name]
        
        return table_description