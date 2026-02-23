# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from dataclasses import dataclass


@dataclass
class DataQuality:

    record_count: float = 0
    error_affected_count: float = 0
    erroneous_count: float = 0
    missing_affected_count: float = 0
    missing_count: float = 0

    @property
    def accuracy(self) -> float:
        assert self.erroneous_count <= self.record_count  
        accuracy = ((self.record_count - round(self.erroneous_count)) / self.record_count) * 100
        return accuracy
    
    @property
    def completeness(self) -> float:
        assert self.missing_count <= (self.record_count + round(self.missing_count))  
        completeness = (self.record_count / (self.record_count + round(self.missing_count))) * 100
        return completeness
    
    @property
    def percent_error_affected(self) -> float:
        assert self.error_affected_count <= self.record_count 
        percent_error_affected_count = (round(self.error_affected_count) / self.record_count) * 100
        return percent_error_affected_count
    
    @property
    def percent_erroneous(self) -> float:
        assert self.erroneous_count <= self.record_count
        percent_erroneous_count = (round(self.erroneous_count) / self.record_count) * 100
        return percent_erroneous_count
    
    @property
    def percent_missing_affected(self) -> float:
        assert self.missing_affected_count <= self.record_count 
        percent_missing_count_affected = (round(self.missing_affected_count) / 
                                         (self.record_count + round(self.missing_count))) * 100
        return percent_missing_count_affected 
      
    @property
    def percent_missing(self) -> float:
        assert self.missing_count <= (self.record_count + round(self.missing_count))
        percent_missing_count = (round(self.missing_count) / (self.record_count + round(self.missing_count))) * 100
        return percent_missing_count

    @property
    def percent_overall(self) -> float:
        assert (self.erroneous_count + self.missing_count) <= (self.record_count + self.missing_count)
        overall = (self.record_count - round(self.erroneous_count)) / (self.record_count + round(self.missing_count)) * 100
        return overall
    

class DatasetQualityCharacterization:

    def __init__(self): 
        self._dataset_data_quality = DataQuality()
        self._table_data_quality = {}
        
    def add_table_data_quality(self, table_name: str, table_data_quality : DataQuality) -> None: 
        self._table_data_quality[table_name] = table_data_quality
        self._dataset_data_quality.record_count += table_data_quality.record_count
        self._dataset_data_quality.error_affected_count += table_data_quality.error_affected_count
        self._dataset_data_quality.erroneous_count += table_data_quality.erroneous_count
        self._dataset_data_quality.missing_affected_count += table_data_quality.missing_affected_count
        self._dataset_data_quality.missing_count += table_data_quality.missing_count

    @property
    def dataset_data_quality(self) -> DataQuality: 
        return self._dataset_data_quality

    @property
    def table_data_quality(self) -> DataQuality: 
        for table_data_quality in self._table_data_quality: 
            yield table_data_quality

    def get_data_quality_for_table(self, table_name: str) -> None | DataQuality: 
        if table_name in self._table_data_quality.keys(): 
            return self._table_data_quality[table_name]
        return None
    