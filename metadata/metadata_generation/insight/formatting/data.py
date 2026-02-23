# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

class ColumnFormatter:

    def __init__(self, df_sheet):
        self.__df_sheet = df_sheet

    def get_formatted_column(self, column_annotations):
        module_str = column_annotations.format_module()
        formatted_column = self.__df_sheet[column_annotations.name()]
        
        if module_str != 'n/a':
            print(module_str)
            module = importlib.import_module('insight.formatting.' + module_str)
            func_str = column_annotations.format_function()
            func = getattr(module, func_str)
            formatted_column = func(formatted_column)
            
        return formatted_column