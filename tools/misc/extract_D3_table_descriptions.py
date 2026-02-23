# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import csv

with open('table_descriptions_raw.csv', 'r') as raw_file_handle:
    reader = csv.reader(raw_file_handle)
    descriptions = {}
    for row in reader:
        descriptions[row[0]] = row[3]

print("{")
for key, value in descriptions.items():
    print("\t" + "\"" + key + " Test Data\"" + ": " + "\"" + value + "\"" + ",")
print("}")