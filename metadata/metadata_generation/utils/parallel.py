# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from multiprocessing import Pool
from functools import partial
import numpy as np


class ParallelExecutor:


    def __init__(self, num_of_processes=1):
        assert num_of_processes >= 1
        self.__num_of_processes = num_of_processes


    def execute_in_parallel(self, dataframe, func):
        parallelized_func = ParallelizedFunc(self.__num_of_processes)
        apply_call_wrapper = SubsetWrapper(func)
        work_subset = parallelized_func.execute(dataframe, apply_call_wrapper.get_wrapped_apply_call)


class ParallelizedFunc:


    def __init__(self, wrapped_func, num_of_processes):
        self.__wrapped_func = wrapped_func
        self.__num_of_processes = num_of_processes 


    def execute(self, dataframe, wrapped_apply_call):
        dataframe_split = np.array_split(dataframe, self.__num_of_processes)
        pool = Pool(self.__num_of_processes)
        result = pd.concat(pool.map(wrapped_apply_call, dataframe_split))
        pool.close()
        pool.join()
        return result


class SubsetWrapper:


    def __init__(self, func):
        self.__func = func

    
    def get_wrapped_apply_call(dataframe_subset):
        wrapped_apply_call = dataframe_subset.apply(self.__func, axis=1)
        return wrapped_apply_call

