# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from ..utils.file_system_tools import FullFileNameFinder
from ..utils.file_iterator import MetadataIterator
from ..utils.file_parsing import MetadataTableParser
from collections import Counter

import pandas as pd
import os


class DictAggregator:

    def __init__(self) -> None:
        self.__data = dict()

    def __getitem__(self, key):
        return self.__data[key]
    
    def __setitem__(self, key, value):
        self.__data[key] = value

    def keys(self):
        return self.__data.keys()

    def set_dict(self, key, value) -> None:
        self.__data[key] = value

    def add_dict(self, key, value) -> None:
        if key in self.__data.keys():
            self.__data[key] += value
        else:
            self.__data[key] = value

# Would having these exist as individual helper functions be fine?
# I don't think I gain any functionality by having them in a class, at least not now.

class TableAggregation():

    def __init__(self, tables) -> None:
        super().__init__()
        self.__tables = tables

    def get_aggregate(self) -> dict:
        if len(self.__tables) <= 1:
            return self.__tables[0]

        attribute_aggregation = AttributeAggregation()
        measure_aggregation = MeasureAggregation()

        for table in self.__tables:
            attribute_aggregation.add_table(table)
            measure_aggregation.add_table(table)

        new_table_dict = dict()

        # TODO: Figure out a better way to do this... Seems like you know this needs a new home probably
        names = [x['name'] for x in self.__tables]
        name = os.path.commonprefix(names)
        if name != "":
            new_table_dict['name'] = f"File Group with common prefix: '{name}'"
        else:
            names = ""
            if len(names) > 3:
                names = f"{names[0]}, {names[1]}, {names[2]}..."
            elif len(names) == 2:
                names = f"{names[0]} & {names[1]}"
            else:
                names = names[0]

            new_table_dict['name'] = f"File Group that contains '{names}'"

        new_table_dict['count'] = sum([x['count'] for x in self.__tables])

        types = Counter([x['type'] for x in self.__tables])
        new_table_dict['type'] = types.most_common(1)[0][0]

        new_table_dict['attributes'] = attribute_aggregation.get_aggregate()

        new_table_dict['dataQualitySummary'] = dict()
        new_table_dict['dataQualitySummary']['measures'] = measure_aggregation.get_aggregate()

        return new_table_dict


class MeasureAggregation():
    def __init__(self) -> None:
        super().__init__()
        self.__names = set()
        self.__values = DictAggregator()
        self.__units = DictAggregator()
        self.__counts = DictAggregator()

    def get_aggregate(self) -> list[dict]:
        output_measures = list()
        for name in self.__names:
            output_measures.append({
                'name': name,
                'value': self.__values[name] / self.__counts[name],
                'units': self.__units[name],
                'notes': f"Mean of {self.__values[name]} records/rows"
            })
        return output_measures

    def add_table(self, table: dict) -> None:
        measures = table['dataQualitySummary']['measures']
        for measure in measures:
            name = measure['name']
            self.__names.add(name)
            self.__counts.add_dict(name, 1)
            self.__values.add_dict(name, measure['value'])
            self.__units.set_dict(name, measure['units'])


class AttributeAggregation():
    def __init__(self) -> None:
        super().__init__()
        self.__names = set()
        self.__has_dataQuality = DictAggregator()
        self.__types = DictAggregator()
        self.__units = DictAggregator()
        self.__description = DictAggregator()
        self.__dataQualityClass = DictAggregator()
        self.__dataQuality = DictAggregator()

    def add_table(self, table) -> None:
        attributes = table['attributes']
        for attribute in attributes:
            name = attribute['name']
            self.__names.add(name)
            self.__types.set_dict(name, attribute['type'])
            self.__units.set_dict(name, attribute['units'])
            self.__description.set_dict(name, attribute['description'])
            if 'dataQualityClass' in attribute.keys():
                self.__has_dataQuality.set_dict(name, True)
                self.__dataQualityClass.set_dict(
                    name, attribute['dataQualityClass'])
                self.__dataQuality.add_dict(
                    name, [attribute['dataQuality']])
            else:
                self.__has_dataQuality.set_dict(name, False)

    def get_aggregate(self) -> dict:
        aggregated_attributes = list()
        for name in self.__names:
            newdict = {
                'name': name,
                'type': self.__types[name],
                'units': self.__units[name],
                'description': self.__description[name],
            }

            if self.__has_dataQuality[name]:
                newdict['dataQualityClass'] = self.__dataQualityClass[name]
                data_quality_aggregation = DataQualityAggregation()
                for data_quality in self.__dataQuality[name]:
                    data_quality_aggregation.add_quality(data_quality)
                newdict['dataQuality'] = data_quality_aggregation.get_data_quality_aggregate()

            aggregated_attributes.append(newdict)
        return aggregated_attributes


class DataQualityAggregation():
    def __init__(self) -> None:
        super().__init__()
        self.__names = set()
        self.__values = DictAggregator()
        self.__counts = DictAggregator()
        self.__units = DictAggregator()
        self.__descriptions = DictAggregator()
        self.__frequencies = DictAggregator()

    def add_quality(self, attribute_qualities) -> None:
        for quality in attribute_qualities:
            name = quality['name']
            self.__names.add(name)
            self.__values.add_dict(name, quality['value'])
            self.__counts.add_dict(name, 1)
            self.__units.set_dict(name, quality['units'])
            self.__descriptions.set_dict(name, quality['description'])
            if 'frequencies' in quality.keys():
                self.__frequencies.add_dict(
                    name, [quality['frequencies']])

    def get_data_quality_aggregate(self) -> list[dict]:
        output_data_qualities = list()
        for name in self.__names:
            output_data_quality = {
                'name': name,
                'value': self.__values[name] / self.__counts[name],
                'units': self.__units[name],
                'description': self.__descriptions[name],
            }
            frequency_aggregation = FrequencyAggregation()
            if name in self.__frequencies.keys():
                for frequency in self.__frequencies[name]:
                    frequency_aggregation.add_frequencies(frequency)
                output_data_quality['frequencies'] = frequency_aggregation.get_frequency_aggregation()
            output_data_qualities.append(output_data_quality)
        return output_data_qualities


class FrequencyAggregation():

    def __init__(self) -> None:
        super().__init__()
        self.__names = set()
        self.__frequencies = DictAggregator()
        self.__frequency_counts = DictAggregator()
        self.__frequency_percents = DictAggregator()

    def add_frequencies(self, frequncies) -> None:
        for frequency in frequncies:
            name = frequency['name']
            self.__names.add(name)
            self.__frequencies.add_dict(name, frequency['frequencyN'])
            self.__frequency_counts.add_dict(name, 1)
            self.__frequency_percents.add_dict(name, frequency['frequencyPercent'])

    def get_frequency_aggregation(self) -> list[dict]:
        output_frequencies = list()
        for name in self.__names:
            output_frequencies.append({
                'name': name,
                'frequencyN': self.__frequencies[name] / self.__frequency_counts[name],
                'frequencyPercent': self.__frequency_percents[name] / self.__frequency_counts[name]
            })
        return output_frequencies


class FileGroups:
    file_groups = dict()

    def __init__(self) -> None:
        pass

    @classmethod
    def add_file(cls, file_name: str, group: int = -1):
        if group in cls.file_groups.keys():
            cls.file_groups[group].append(file_name)
        else:
            cls.file_groups[group] = [file_name]

    @classmethod
    def contains_key(cls, x):
        return x in cls.file_groups.keys()

    @classmethod
    def __getitem__(cls, x):
        return cls.file_groups[x]

    def __iter__(self) -> iter:
        return FileGroupIterator(self)


class FileGroupIterator:
    def __init__(self, file_group: FileGroups) -> None:
        self.__file_group = file_group
        self.__file_index = 0
        if self.__file_group.contains_key(-1):
            self.__group_index = -1
        else:
            self.__group_index = 0

    def __iter__(self):
        return self

    def __next__(self) -> list[str]:
        try:
            if self.__file_group == -1 and self.__group_index < len(self.__file_group[-1]):
                file_names = [self.__file_group[-1][self.__file_index]]
            else:
                file_names = self.__file_group[self.__group_index]
            self.__increment_index()
            return file_names
        except KeyError:
            raise StopIteration

    def __increment_index(self):
        if self.__file_group == -1:
            self.__file_index += 1
            if self.__file_index >= len(self.__file_group[self.__group_index]):
                self.__file_index = 0
                self.__group_index += 1
        else:
            self.__group_index += 1


class FileGrouping:

    file_grouping = FileGroups()

    def __init__(self) -> None:
        pass

    @classmethod
    def group_metadata(cls, metadata: dict) -> list[dict]:
        metadata_groups = list()
        metadata_iterator = MetadataIterator(metadata)
        for file_group in cls.file_grouping:
            metadata_group = list()
            for table_metadata_index in metadata_iterator.iterate_table():
                metadata_table_parser = MetadataTableParser(
                    metadata, table_metadata_index)
                name = metadata_table_parser.get_table_value('name')
                if name in file_group:
                    metadata_group.append(
                        metadata['objects'][table_metadata_index])
            metadata_groups.append(metadata_group)
        return metadata_groups

    @classmethod
    def aggregate_groups(cls, metadata_groupings: list[dict]):
        output_objects = list()
        for metadata_group in metadata_groupings:
            attribute_aggregation = TableAggregation(metadata_group)
            output_objects.append(attribute_aggregation.get_aggregate())
        return output_objects

    @classmethod
    def group_files(cls, metadata: dict) -> dict:

        metadata_groupings = cls.group_metadata(metadata)
        aggregated_groups = cls.aggregate_groups(metadata_groupings)

        metadata['objects'] = aggregated_groups
        return metadata
    
    @classmethod
    def add_full_file(cls, file_name, grouping, sheet_name):
        full_file_name = cls.full_file_name_finder.get_full_file_name_from_part(file_name)
        cls.real_name_to_excel_name_map[full_file_name] = sheet_name
        cls.file_grouping.add_file(full_file_name, grouping)

    # TODO: Break up this function even more.

    def valid_file_name(file_name):
        if (file_name != file_name):
            return False
        if (str(file_name) == ""):
            return False
        return True

    @classmethod
    def get_excel_name_map(cls, excel_annotations, data_directory_path):
        cls.full_file_name_finder = FullFileNameFinder(data_directory_path)
        cls.real_name_to_excel_name_map = dict()
        grouping = 0

        for sheet_name in excel_annotations.sheet_names:
            data = pd.read_excel(excel_annotations, sheet_name=sheet_name)
            found_names = False
            if "Files" in data.columns:
                for file_name in data["Files"]:
                    if cls.valid_file_name(file_name):
                        cls.add_full_file(file_name, grouping, sheet_name)
                        found_names = True
            
            if found_names == False:
                cls.add_full_file(sheet_name, grouping, sheet_name)

            grouping += 1
        return cls.real_name_to_excel_name_map
