# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

class MetadataParser:

    def __init__(self, metadata: dict):
        self.__metadata = metadata

    def in_data_set_values(self, key: str) -> bool:
        data_set_value_exists = False

        if key in self.__metadata.keys():
            data_set_value_exists = True

        return data_set_value_exists       

    def get_data_set_value(self, data_set_value):
        assert self.__metadata[data_set_value]
        return self.__metadata[data_set_value]


class MetadataDataQualityParser:

    def __init__(self, metadata: dict, table_metadata_index: int=None):
        if table_metadata_index != None:
            self.__data_quality_metrics = metadata['objects'][table_metadata_index]['dataQualitySummary']['measures']
        else:
            self.__data_quality_metrics = metadata['dataQualitySummary']['measures']

    def get_data_quality_metrics(self):
        return self.__data_quality_metrics

    def metric_has_notes(self, metric_name: str) -> bool:
        metric_exists = False

        for metric in self.__data_quality_metrics:
            if (metric['name'] == metric_name) and ('notes' in metric.keys()):
                metric_exists = True

        return metric_exists   


class MetadataAttributeParser:

    def __init__(self, full_metadata: dict = None, JSON_index: object = None, 
                 table_metadata: dict = None, attribute_index: int = None):
        if full_metadata != None:
            self.__table = full_metadata['objects'][JSON_index.table_metadata_index]
            self.__attribute = self.__table['attributes'][JSON_index.attribute_metadata_index]
        elif table_metadata != None:
            self.__table = table_metadata
            self.__attribute = self.__table['attributes'][attribute_index]
        else:
            raise ValueError('Metadata must be supplied to metadata attribute parser')

    def get_table_name(self) -> str: 
        table_name = self.__table['name']
        return table_name
    
    #TODO: Does this need to exist if get_attribute_value("name") already does the same thing? 

    def get_attribute_name(self) -> str:
        attribute_name = self.__attribute['name']
        return attribute_name

    def get_data_quality_class(self) -> str:
        data_quality_class = 'none'

        if self.in_attribute_values('dataQualityClass'):
            data_quality_class = self.__attribute['dataQualityClass']
        
        return data_quality_class
    
    def in_attribute_values(self, key):
        attribute_value_exists = False

        if key in self.__attribute.keys():
            attribute_value_exists = True

        return attribute_value_exists

    def get_attribute_value(self, attribute_value_name: str):
        attribute_value = self.__attribute[attribute_value_name]
        return attribute_value

    def in_data_quality_metrics(self, metric_name: str) -> bool:
        metric_exists = False
        data_quality_metrics = self.__attribute['dataQuality']

        for metric in data_quality_metrics:
            if metric['name'] == metric_name:
                metric_exists = True
                break

        return metric_exists  
    
    def in_manual_annotations(self, manual_annotation: str) -> bool: 
        manual_annotation_exists = False

        if manual_annotation in self.__attribute['manual_annotations']:
            manual_annotation_exists = True

        return manual_annotation_exists
    
    def get_manual_annotation(self, manual_annotation: str) -> str:
        assert self.in_manual_annotations
        return self.__attribute['manual_annotations'][manual_annotation]

    def get_data_quality_metric(self, metric_name: str, metric_attribute_name: str='value') -> float:
        metric_value = None
        data_quality_metrics = self.__attribute['dataQuality']

        for metric in data_quality_metrics:
            if metric['name'] == metric_name:
                metric_value = metric[metric_attribute_name]

        return metric_value       

    def get_reference_table_info(self) -> tuple[str, str]:
        assert self.in_attribute_values('refersTo')
        refers_to = self.get_attribute_value('refersTo')
        primary_key_table, primary_key_attribute = refers_to.split('.')
        return primary_key_table, primary_key_attribute 

    def iterate_categorical(self) -> tuple[str, str]:
        assert self.in_data_quality_metrics('Number of Categories')
        frequencies = self.get_data_quality_metric('Number of Categories', metric_attribute_name='frequencies')

        for frequency in frequencies:
            yield (frequency['name'], frequency['frequencyPercent'])


class MetadataDataQualityMetricParser:

    def __init__(self, data_quality_metric):
        self.__data_quality_metric = data_quality_metric

    def in_data_quality_metrics(self, metric_name: str) -> bool:
        metric_exists = False

        for metric in self.__data_quality_metrics:
            if metric['name'] == metric_name:
                metric_exists = True

        return metric_exists       

    def get_data_quality_metric_value(self, value) -> float:
        return self.__data_quality_metric[value]


class MetadataTableParser:

    def __init__(self, metadata: dict, table_metadata_index: int):
        self.__table = metadata['objects'][table_metadata_index]
 
    def in_table_values(self, key: str) -> bool:
        table_value_exists = False

        if key in self.__table.keys():
            table_value_exists = True

        return table_value_exists
    
    def in_relationships(self, key: str) -> bool: 
        in_relationships = False

        if key in self.__table['relationships']:
            in_relationships = True

        return in_relationships
    
    def attributes(self):
        for attribute in self.__table['attributes']: 
            yield attribute['name']

    def get_table_value(self, table_value: str):
        assert self.in_table_values(table_value)
        return self.__table[table_value]
    
    def get_primary_keys(self):
        assert self.in_relationships('primaryKeys')
        return self.__table['relationships']['primaryKeys']
    
    def get_referenced_primary_key_tables(self):
        for referenced_primary_key_table in self.__table['relationships']['refersToPrimaryKeyTables'].keys():
            yield referenced_primary_key_table

    def get_primary_key_table_references(self): 
        unique_foreign_key_references = {}
        for primary_key_table in self.get_referenced_primary_key_tables(): 
            unique_foreign_key_references[primary_key_table] = set()
            for foreign_key_reference in self.__table['relationships']['refersToPrimaryKeyTables'][primary_key_table]: 
                unique_foreign_key_references[primary_key_table].add(foreign_key_reference['keyID'])
        for primary_key_table in unique_foreign_key_references.keys(): 
            for key_ID in unique_foreign_key_references[primary_key_table]:
                yield primary_key_table, key_ID
    
    def attribute_reference_already_resolved(self, attribute_name: str) -> bool:
        if not self.in_table_values('relationships'):
            return False
        if not self.in_relationships('refersToPrimaryKeyTables'): 
            return False
        for primary_key_table in self.__table['relationships']['refersToPrimaryKeyTables']:
            for foreign_key in primary_key_table:
                if foreign_key['foreignKey'] == attribute_name:
                    return True
        return False
    
    def get_attribute_value(self, attribute_index: int, attribute_value_name: str) -> str:
        metadata_attribute_parser = MetadataAttributeParser(table_metadata = self.__table, attribute_index = attribute_index)
        if attribute_value_name == 'dataQualityClass':
            attribute_value = metadata_attribute_parser.get_data_quality_class()
        else:
            attribute_value = metadata_attribute_parser.get_attribute_value(attribute_value_name)
        return attribute_value
    
    def get_key_attributes(self, primary_table_name: str, key_ID: int, attribute_set: str) -> list[str]:
        key_attributes = []
        for key in self.__table['relationships']['refersToPrimaryKeyTables'][primary_table_name]:
            if key['keyID'] == key_ID:
                key_attributes.append(key[attribute_set])
        return key_attributes
    
    def composite_uniqueness_rule_previously_covered(self, attribute_name) -> bool: 
        primary_key_attributes = self.get_primary_keys()
        assert len(primary_key_attributes) != 0
        if attribute_name != primary_key_attributes[0]:
            return True
        return False