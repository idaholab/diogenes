# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from dataclasses import dataclass

from ...veritas.datatypes import GeneralGroupIDEnum, ReferenceGroupIDEnum, LowFrequencyGroupIDEnum
from ...veritas.datatypes import LocationIDEnum 

from ...veritas.error_catalog_generation.id_tags import IDTag


@dataclass(frozen=True)
class ErrorState: 
      
    error_state: int = 0
    probability_for_state: float = 0
    description: str = ''


class ErrorStateRegistry: 

    _error_state_registry = {
    (ReferenceGroupIDEnum.SINGLE_RECORD, LocationIDEnum.ORPHAN_FOREIGN_KEY) :           ErrorState(2**0, 1, 'single_record_orphan'),
    (ReferenceGroupIDEnum.MULTI_RECORD, LocationIDEnum.ORPHAN_FOREIGN_KEY) :            ErrorState(2**1, 0.2, 'multi_record_orphan'),
    (ReferenceGroupIDEnum.MULTI_TABLE, LocationIDEnum.ORPHAN_FOREIGN_KEY) :             ErrorState(2**2, 0, 'multi_table_orphan'),
    (GeneralGroupIDEnum.AFFECTS_MANY_RECORDS, LocationIDEnum.UNIQUENESS_VIOLATION) :    ErrorState(2**3, 0, 'affects_many_uniqueness'),
    (GeneralGroupIDEnum.AFFECTS_SOME_RECORDS, LocationIDEnum.UNIQUENESS_VIOLATION) :    ErrorState(2**4, 0.1, 'affects_some_uniqueness'),
    (GeneralGroupIDEnum.AFFECTS_FEW_RECORDS, LocationIDEnum.UNIQUENESS_VIOLATION) :     ErrorState(2**5, 1, 'affects_few_uniqueness'),
    (LowFrequencyGroupIDEnum.MULTIPLE_SUB_THRESHOLD, LocationIDEnum.LOW_FREQUENCY) :    ErrorState(2**6, 0, 'multiple_sub_thresh_frequency'),
    (LowFrequencyGroupIDEnum.FEW_SUB_THRESHOLD, LocationIDEnum.LOW_FREQUENCY) :         ErrorState(2**7, 0.1, 'few_sub_threshold_frequency'),
    (LowFrequencyGroupIDEnum.SINGLE_SUB_THRESHOLD, LocationIDEnum.LOW_FREQUENCY) :      ErrorState(2**8, 1, 'single_sub_threshold_frequency'),
    (GeneralGroupIDEnum.AFFECTS_MANY_RECORDS, LocationIDEnum.UNIT_OUTLIER) :            ErrorState(2**9, 0, 'affects_many_unit'),
    (GeneralGroupIDEnum.AFFECTS_SOME_RECORDS, LocationIDEnum.UNIT_OUTLIER) :            ErrorState(2**10, 0.1, 'affects_some_unit'),
    (GeneralGroupIDEnum.AFFECTS_FEW_RECORDS, LocationIDEnum.UNIT_OUTLIER) :             ErrorState(2**11, 1, 'affects_few_unit'),
    (GeneralGroupIDEnum.AFFECTS_MANY_RECORDS, LocationIDEnum.OUTSIDE_THREE_STD_DEV) :   ErrorState(2**12, 0, 'affects_many_3_std'),
    (GeneralGroupIDEnum.AFFECTS_SOME_RECORDS, LocationIDEnum.OUTSIDE_THREE_STD_DEV) :   ErrorState(2**13, 0.1, 'affects_some_3_std'),
    (GeneralGroupIDEnum.AFFECTS_FEW_RECORDS, LocationIDEnum.OUTSIDE_THREE_STD_DEV) :    ErrorState(2**14, 1, 'affects_few_3_std'),
    (GeneralGroupIDEnum.AFFECTS_MANY_RECORDS, LocationIDEnum.OUTSIDE_FOUR_STD_DEV) :    ErrorState(2**15, 0, 'affects_many_4_std'),
    (GeneralGroupIDEnum.AFFECTS_SOME_RECORDS, LocationIDEnum.OUTSIDE_FOUR_STD_DEV) :    ErrorState(2**16, 0.1, 'affects_many_4_std'),
    (GeneralGroupIDEnum.AFFECTS_FEW_RECORDS, LocationIDEnum.OUTSIDE_FOUR_STD_DEV) :     ErrorState(2**17, 1, 'affects_few_4_std'), 
    (GeneralGroupIDEnum.AFFECTS_MANY_RECORDS, LocationIDEnum.DATE_OUTLIER) :            ErrorState(2**18, 0, 'affects_many_date'),
    (GeneralGroupIDEnum.AFFECTS_SOME_RECORDS, LocationIDEnum.DATE_OUTLIER) :            ErrorState(2**19, 0.1, 'affects_some_date'),
    (GeneralGroupIDEnum.AFFECTS_FEW_RECORDS, LocationIDEnum.DATE_OUTLIER) :             ErrorState(2**20, 1, 'affects_few_date'),
    (GeneralGroupIDEnum.AFFECTS_MANY_RECORDS, LocationIDEnum.TIME_OUTLIER) :            ErrorState(2**21, 0, 'affects_many_date'),
    (GeneralGroupIDEnum.AFFECTS_SOME_RECORDS, LocationIDEnum.TIME_OUTLIER) :            ErrorState(2**22, 0.1, 'affects_some_date'),
    (GeneralGroupIDEnum.AFFECTS_FEW_RECORDS, LocationIDEnum.TIME_OUTLIER) :             ErrorState(2**23, 1, 'affects_few_date'),
    (GeneralGroupIDEnum.AFFECTS_MANY_RECORDS, LocationIDEnum.FORMAT_OUTLIER) :            ErrorState(2**24, 0, 'affects_many_date'),
    (GeneralGroupIDEnum.AFFECTS_SOME_RECORDS, LocationIDEnum.FORMAT_OUTLIER) :            ErrorState(2**25, 0.1, 'affects_some_date'),
    (GeneralGroupIDEnum.AFFECTS_FEW_RECORDS, LocationIDEnum.FORMAT_OUTLIER) :             ErrorState(2**26, 1, 'affects_few_date')
    }

    HIGHEST_CURRENT_BIT = len(_error_state_registry.items())

    @classmethod
    def get_error_state(cls, id_tags: IDTag) -> ErrorState: 
          if id_tags.location_ID == None or id_tags.group_ID == None:
               return None
          return cls._error_state_registry[(id_tags.group_ID, id_tags.location_ID)] 
    
    @property
    def generate_error_string(self, mask: int) -> int:
        total_bit_string = 0
        for _, error_state in self._error_state_registry.items():
            total_bit_string &= error_state.error_state
        all_error_codes_except_mask = total_bit_string ^ mask
        return all_error_codes_except_mask
    

MISSING_BIT_STRINGS = ErrorStateRegistry.get_error_state(IDTag(ReferenceGroupIDEnum.SINGLE_RECORD, 
                                    LocationIDEnum.ORPHAN_FOREIGN_KEY)).error_state * \
                      ErrorStateRegistry.get_error_state(IDTag(ReferenceGroupIDEnum.SINGLE_RECORD, 
                                    LocationIDEnum.ORPHAN_FOREIGN_KEY)).error_state * \
                      ErrorStateRegistry.get_error_state(IDTag(ReferenceGroupIDEnum.SINGLE_RECORD, 
                                    LocationIDEnum.ORPHAN_FOREIGN_KEY)).error_state

