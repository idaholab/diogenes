# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pandas as pd

from dataclasses import dataclass

from ...veritas.error_catalog_generation.group_id import GeneralGroupIDRegistry, LowFrequencyGroupIDRegistry

from ...veritas.datatypes import LocationIDEnum

from ...veritas.datatypes import GeneralGroupIDEnum, LowFrequencyGroupIDEnum


@dataclass
class IDTag(): 

    _group_ID : GeneralGroupIDEnum = None
    _location_ID: LocationIDEnum = None

    def __init__(self, group_ID=None, location_ID=None):
        self._group_ID = group_ID
        self._location_ID = location_ID

    @property
    def group_ID(self) -> GeneralGroupIDEnum: 
        return self._group_ID

    @property
    def location_ID(self) -> LocationIDEnum:
        return self._location_ID
    
    @location_ID.setter
    def location_ID(self, location_id_info: tuple[LocationIDEnum, pd.DataFrame]) -> None:
        location_ID, error_df = location_id_info
        if error_df is None: 
            self._location_ID = None
            return
        self._location_ID = location_ID
    

class PercentErroneousBasedIDTag(IDTag):
    
    @property
    def group_ID(self) -> GeneralGroupIDEnum:
        return self._group_ID
    
    @group_ID.setter
    def group_ID(self, group_id_info: tuple[pd.DataFrame, int]) -> None:
        error_df, original_df_size = group_id_info
        if error_df is None: 
            self._group_id = None
            return
        error_percentage = (float(len(error_df.index)) / float(original_df_size)) * 100 
        self._group_ID = GeneralGroupIDRegistry.get_group_id(error_percentage)


class LowFrequencyBasedIDTag(IDTag): 

    @property
    def group_ID(self) -> LowFrequencyGroupIDEnum:
        return self._group_ID
    
    @group_ID.setter
    def group_ID(self, number_of_values_low_frequency) -> None:
        self._group_ID = LowFrequencyGroupIDRegistry.get_group_id(number_of_values_low_frequency)

    @property
    def location_ID(self) -> LocationIDEnum:
        return self._location_ID
    
    @location_ID.setter
    def location_ID(self, location_ID: LocationIDEnum) -> None:
        self._location_ID = location_ID
    
