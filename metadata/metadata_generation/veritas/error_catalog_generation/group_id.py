# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import sys 

from ...veritas.datatypes import GeneralGroupIDEnum, ReferenceGroupIDEnum, LowFrequencyGroupIDEnum


class GeneralGroupIDRegistry:

    @classmethod
    def get_group_id(cls, erroneous_row_percentage: float) -> GeneralGroupIDEnum:
        group_id = None

        if erroneous_row_percentage <= 0.01:
            group_id = GeneralGroupIDEnum.AFFECTS_FEW_RECORDS
        elif erroneous_row_percentage <= 5:
            group_id = GeneralGroupIDEnum.AFFECTS_SOME_RECORDS
        elif erroneous_row_percentage <= 100:
            group_id = GeneralGroupIDEnum.AFFECTS_MANY_RECORDS
        else:
            raise ValueError('Erroneous percentage greater than 100')

        return group_id   


class ReferenceGroupIDRegistry:

    @classmethod
    def get_group_id(cls, is_multi_record: bool, is_multi_table: bool) -> ReferenceGroupIDEnum:
        group_id = None

        if is_multi_table == True:
            group_id = ReferenceGroupIDEnum.MULTI_TABLE
        elif is_multi_record == True:
            group_id = ReferenceGroupIDEnum.MULTI_RECORD
        else:
            group_id = ReferenceGroupIDEnum.SINGLE_RECORD

        return group_id
       

class LowFrequencyGroupIDRegistry:

    @classmethod
    def get_group_id(cls, number_of_sub_threshold_categories: int) -> LowFrequencyGroupIDEnum:
        group_id = None

        if number_of_sub_threshold_categories == 1:
            group_id = LowFrequencyGroupIDEnum.SINGLE_SUB_THRESHOLD
        elif number_of_sub_threshold_categories <= 3:
            group_id = LowFrequencyGroupIDEnum.FEW_SUB_THRESHOLD
        elif number_of_sub_threshold_categories <= sys.maxsize:
            group_id = LowFrequencyGroupIDEnum.MULTIPLE_SUB_THRESHOLD

        return group_id



