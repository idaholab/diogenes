# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import file_utils as f_utils
import argparse

from pyspark.sql import SparkSession


def preview_parquet_file(args):
    try:
        f_utils.check_if_file_exists(args.input)
        spark = SparkSession.builder.appName('CSV_Sampler').getOrCreate()
        df = spark.read.parquet(args.input, header=True)
        df.show(n=args.rows, truncate=True)
        print("\n\n")
        spark.stop()
    except Exception as e:
        print("\nFailed to read sample from Parquet file: {}".format(args.input))
        print("Error: " + str(e)) 


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Convert between CSV and Parquet file format')
    parser.add_argument('-i', '--input', help="Name of file to convert", required=True)
    parser.add_argument('-r', '--rows', help='Print sample rows from a CSV created from a parquet file', type=int, default=5)
    parser.add_argument('-c', '--columns', nargs='*', help='Index of the columns converted to CSV', type=int, default=[])
    args = parser.parse_args()

    preview_parquet_file(args)