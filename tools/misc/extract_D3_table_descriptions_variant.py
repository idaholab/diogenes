# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import csv

with open('table_descriptions_raw.csv', 'r') as raw_file_handle:
    reader = csv.reader(raw_file_handle)
    descriptions = {}
    for row in reader:
        if row[0] not in descriptions.keys():
            descriptions[row[0]] = ""
        descriptions[row[0]] += row[1] + "; "
    for key, item in descriptions.items():
        descriptions[key] = descriptions[key][0:-2]

print("{")
for key, value in descriptions.items():
    print("\t" + "\"" + key + " Test Data\"" + ": " + "\"" + value + "\"" + ",")
print("}")