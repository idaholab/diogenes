# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED


import numpy as np
import re 


def time(df_column): 
    df_column = df_column.replace(np.nan, "P00DT00H00M")
    df_column = df_column.apply(lambda x: re.findall(r'\d+', x))
    df_column = df_column.apply(lambda x: int(x[0]) * 24 * 60 + int(x[1]) * 60 + int(x[2]))
    df_column = df_column.replace(0, np.nan)

    return df_column