# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import argparse
import os
import glob
import math
import random
import time
import multiprocessing


class Reservoir_Sampler():
    '''
    The sampling algorithm is an implementation the reservoir sampling algorithm described by Kim-Hung Li in their paper [Reservoir-sampling algorithms of time complexity O(n(1 + log(N/n)))](https://dl.acm.org/doi/10.1145/198429.198435)

    This [link](https://en.wikipedia.org/wiki/Reservoir_sampling#Optimal:_Algorithm_L) from wikipedia provides a summary of the algorithm. 
    '''

    def __init__(self, input_path: str, output_path: str, n_rows: int, multiprocessors: int = 1) -> None:
        random.seed(time.time())
        self.input_path = input_path
        self.output_path = output_path
        self.n_rows = n_rows
        self.multiprocessors = multiprocessors

        # Obtain all CSV files to sample and sample them
        self.input_files = glob.glob(pathname="*.csv", root_dir=input_path)

    # Method called to generate sample.
    def sample(self):
        print(f"Sampling Files from {self.input_path}")
        for i in range(0, len(self.input_files), self.multiprocessors):
            processes = []
            for file in self.input_files[i:i+self.multiprocessors]:
                process = multiprocessing.Process(target=self._process_file, args=(file,))
                process.start()
                processes.append(process)
            for process in processes:
                process.join()
        print(f"Files Sampled and Saved to {self.output_path}")

    def _process_file(self, file):
        sampled_rows = self._sample_file(file)
        self._save_sample(file, sampled_rows)

    def _save_sample(self, file, rows):
        output_file = os.path.join(self.output_path, file)
        with open(output_file, "w") as file:
            file.writelines(rows)

    def _sample_file(self, file):
        reservoir = []
        headers = []
        # Sample file
        with open(os.path.join(self.input_path, file), "r") as file:
            # CSV column names must be saved.
            headers.append(file.readline())
            # Obtain initial count of n_rows
            reservoir = self._fill_reservoir(reservoir, file)
            # Sample the rest of the file.
            reservoir = self._sample_reservoir(reservoir, file)
        # Extend headers with data and return
        headers.extend(reservoir)
        return headers

    def _fill_reservoir(self, reservoir, file):
        i = 0
        line = file.readline()
        while line != "":
            i += 1
            if i > self.n_rows:
                break
            else:
                reservoir.append(line)
            line = file.readline()
        return reservoir

    def _sample_reservoir(self, reservoir, file):
        # One may read https://en.wikipedia.org/wiki/Reservoir_sampling#Optimal:_Algorithm_L for a description of this algorithm
        w = math.exp(
            math.log(random.random()) / self.n_rows)
        line = file.readline()
        while line != "":
            skip = math.floor(math.log(random.random()) / math.log(1 - w)) + 1
            while line != "" and skip > 0:
                line = file.readline()
                skip -= 1
            if line != "":
                reservoir[random.randrange(0, self.n_rows)] = line
                w = w * math.exp(math.log(random.random()) / self.n_rows)
        return reservoir
