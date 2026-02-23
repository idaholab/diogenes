# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pandas as pd


class QueryableErroneousRecords:


    def __init__(self, reference_table):
        self.__table_to_query = reference_table


    def aggregate_error_ids(self):
        assert 'error_ID' in self.__table_to_query
        aggregate_records = self.__table_to_query['error_ID'].unique().tolist()
        return aggregate_records


    def error_is_multi_table(self, error_id):
        error_is_multi_table = False
        
        query = "error_ID == {x}".format(x=error_id)
        mask = self.__table_to_query.eval(query)
        records_with_error_id = self.__table_to_query[mask]  
        unique_table_names = records_with_error_id['table_name'].unique().tolist()
        number_of_unique_table_names = len(unique_table_names)

        if 1 < number_of_unique_table_names:
            error_is_multi_table = True

        return error_is_multi_table


    def error_is_multi_record(self, error_id):
        error_is_multi_record = False
        
        query = "error_ID == {x}".format(x=error_id)
        mask = self.__table_to_query.eval(query)
        records_with_error_id = self.__table_to_query[mask] 
        number_of_records_with_error_id = len(records_with_error_id)

        if 1 < number_of_records_with_error_id:
            error_is_multi_record = True

        return error_is_multi_record


class QueryableErrors:

    def __init__(self, reference_table):
        self.__table_to_query = reference_table


    def get_rule_specific_error_info(self, error_id):
        query = "error_ID == {x}".format(x=error_id)
        mask = self.__table_to_query.eval(query)
        records_with_error_id = self.__table_to_query[mask]   
        rule_specific_error_info = records_with_error_id.iloc[0]['rule_specific_error_info']
        return rule_specific_error_info


    def get_rule_id(self, error_id):
        query = "error_ID == {x}".format(x=error_id)
        mask = self.__table_to_query.eval(query)
        records_with_error_id = self.__table_to_query[mask]  
        rule_id = records_with_error_id.iloc[0]['rule_ID']
        return rule_id


    def get_rule_type(self, error_id):
        query = "error_ID == {x}".format(x=error_id)
        mask = self.__table_to_query.eval(query)
        records_with_error_id = self.__table_to_query[mask]  
        rule_id = records_with_error_id.iloc[0]['rule_type']
        return rule_id