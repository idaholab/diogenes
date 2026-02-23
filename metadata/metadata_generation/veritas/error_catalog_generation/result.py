# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pandas as pd

from ...veritas.datatypes import LocationIDEnum, ReferenceGroupIDEnum, Key, ForeignKey

from ...veritas.error_catalog_generation.id_tags import IDTag
from ...veritas.error_catalog_generation.error_state import ErrorState, ErrorStateRegistry


class MissingRecordsDataFrame:

    def __init__(self, records_df): 
        self._records_df = records_df

    @property
    def records_df(self) -> pd.DataFrame:
        if len(self._records_df.index) == 0:
             return None
        return self._records_df 
    
    @property
    def orphan_key_error_state(self) -> ErrorState:
        return self._orphan_key_error_state
    
    @property
    def num_records_missing(self) -> float: 
        if len(self._records_df.index) == 0:
            return 0
        no_duplicates_df = self._records_df['foreign_key'].drop_duplicates(keep='first')
        return len(no_duplicates_df) * (1 - self.orphan_key_error_state.probability_for_state)
    

class MissingSingleRecordsDataFrame(MissingRecordsDataFrame): 
        
        def __init__(self, records_df):
            super().__init__(records_df)
            self._orphan_key_error_state = ErrorStateRegistry.get_error_state(IDTag(ReferenceGroupIDEnum.SINGLE_RECORD, 
                                                                                    LocationIDEnum.ORPHAN_FOREIGN_KEY))


class MissingMultiRecordsDataFrame(MissingRecordsDataFrame): 
        
        def __init__(self, records_df):
            super().__init__(records_df)
            self._orphan_key_error_state = ErrorStateRegistry.get_error_state(IDTag(ReferenceGroupIDEnum.MULTI_RECORD, 
                                                            LocationIDEnum.ORPHAN_FOREIGN_KEY))


class MissingMultiTableDataFrame(MissingRecordsDataFrame): 
        
        def __init__(self, records_df):
            super().__init__(records_df)
            self._orphan_key_error_state = ErrorStateRegistry.get_error_state(IDTag(ReferenceGroupIDEnum.MULTI_TABLE, 
                                                                                    LocationIDEnum.ORPHAN_FOREIGN_KEY))


class MissingResult: 

    def __init__(self):
        self._primary_key = None
        self._no_primary_key_df: pd.DataFrame = None
        self._foreign_keys_with_missing_records = []

    def add_to_result(self, foreign_key: ForeignKey, partial_result_df: pd.DataFrame) -> None:
        if partial_result_df is None:
            return
        self._foreign_keys_with_missing_records.append(foreign_key)
        partial_result_df = partial_result_df.rename(columns={foreign_key.key_name: 'foreign_key'})
        partial_result_df['multi_record'] = partial_result_df.groupby('foreign_key')['foreign_key'].transform('count')
        if self._no_primary_key_df is None: 
            self._no_primary_key_df = partial_result_df
            return
        self._no_primary_key_df = pd.concat([self._no_primary_key_df, partial_result_df])

    # TODO requires sequential execution of the these two functions. 
    # Any way to remove this coupling while preserving execution speed?
    # Will fail if tabulate not executed 
        
    def tabulate_table_occurrences(self) -> None:
        if self.empty_result:
            return
        self._no_primary_key_df['multi_table'] = self._no_primary_key_df.groupby('foreign_key')['foreign_key'].transform('count')

    @property
    def primary_key(self):
        return self._primary_key
    
    @primary_key.setter
    def primary_key(self, primary_key: Key) -> None:
        self._primary_key = primary_key

    @property
    def foreign_keys_with_missing_records(self) -> list: 
        return self._foreign_keys_with_missing_records

    @property
    def empty_result(self) -> bool: 
        if self._no_primary_key_df is None:
            return True
        return False
    
    #change to group ID enum? 
    def get_result_df(self, error_state_type: ReferenceGroupIDEnum) -> MissingRecordsDataFrame:
        if self.empty_result:
            return None
        elif error_state_type == ReferenceGroupIDEnum.SINGLE_RECORD:
            result_df = self._no_primary_key_df[(self._no_primary_key_df['multi_record'] == 1) & 
                                                (self._no_primary_key_df['multi_table'] == 1)]
            return MissingSingleRecordsDataFrame(result_df)
        elif error_state_type == ReferenceGroupIDEnum.MULTI_RECORD:
            result_df = self._no_primary_key_df[(self._no_primary_key_df['multi_record'] > 1) & 
                                                (self._no_primary_key_df['multi_record'] == 
                                                 self._no_primary_key_df['multi_table'])]
            return MissingMultiRecordsDataFrame(result_df)
        elif error_state_type == ReferenceGroupIDEnum.MULTI_TABLE:
            result_df = self._no_primary_key_df[(self._no_primary_key_df['multi_table'] > 1) & 
                                                (self._no_primary_key_df['multi_record'] != 
                                                 self._no_primary_key_df['multi_table'])]  
            return MissingMultiTableDataFrame(result_df)
        else: 
            raise ValueError(f"No reference key error state type {error_state_type}")