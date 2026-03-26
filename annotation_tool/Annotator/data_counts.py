# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os
import random
import pandas as pd


ROW_LIMIT = 10000


def create_counts(input_directory, output_directory):
    # Create the data counts directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    # Now we can go through and get all the value counts...
    for file in os.listdir(input_directory):
        file = os.path.join(input_directory, file)
        if file.endswith('.csv'):
            base_name = os.path.basename(file)
            file_base = os.path.splitext(base_name)[0]
            out_path = os.path.join(output_directory, f"{file_base}_data_counts.txt")

            with open(out_path, "w+") as out_file:
                out_file.write(f"Contents of {base_name}:\n")

                with open(file) as f:
                    total_rows = sum(1 for _ in f) - 1
                if total_rows <= ROW_LIMIT:
                    tmp = pd.read_csv(file, low_memory=False)
                else:
                    skip_prob = 1 - ROW_LIMIT / total_rows
                    skip_rows = lambda i: i > 0 and random.random() < skip_prob
                    tmp = pd.read_csv(file, skiprows=skip_rows, low_memory=False)

                columns = tmp.columns.to_list()
                columns.sort()
                for column in columns:
                    out_file.write(f"Values in {column}\n")
                    out_file.write(f"{tmp[column].value_counts()}\n\n")
