# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import numpy as np

from dateutil.parser import parse


class DateTimeTranslator:


    def __init__(self): 
        pass


    def translate_dates(self, df, date_time_column_name):
        date_time_parser = DateTimeParser()
        vec_parse_date_times = np.vectorize(date_time_parser.parse_date_times)
        date_times = vec_parse_date_times(df[date_time_column_name])
        return date_times


class DateTimeParser:


    def __init__(self):
        pass


    def parse_date_times(self, date_time):
        parsed_date_time = None

        try:
            parsed_date_time = parse(date_time, fuzzy=True)
        except Exception as e:
            parsed_date_time = 'nan'

        return parsed_date_time


    