# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import numpy as np
from datetime import datetime
from dateutil.parser import parse


def date_time(df_column):
    df_column = df_column.replace(np.nan, "1900-01-01T00:00:00Z")
    df_column = df_column.apply(lambda x: get_formatted_time(x))
    df_column = df_column.astype('datetime64[ns]')
    mask = df_column.isin(["1900-01-01 00:00:00"])
    df_column = df_column[~mask]
    return df_column


def get_formatted_time(unformatted_date):
    parsed_date = parse(unformatted_date)
    formatted_date = "{year}-{month}-{day}T{hour}:{minute}:{second}Z".format(year=parsed_date.year, 
                                                                              month=parsed_date.month,
                                                                              day=parsed_date.day, 
                                                                              hour=parsed_date.hour,
                                                                              minute=parsed_date.minute, 
                                                                              second=parsed_date.second)
    return formatted_date