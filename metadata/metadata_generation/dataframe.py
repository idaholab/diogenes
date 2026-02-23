# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os, csv
import dateutil.parser
import numpy as np
import pandas as pd
import typing
import dateutil, datetime
import warnings

from abc import ABC, abstractmethod

from .settings import ErrorAnnotatedDataFilePaths

from .utils.statistics import monotonicity_ratio
from .utils.sequential_outlier_detection import OutlierClassifier, SequentialOutlierDetector

from .utils.constraints import ConstraintRange
from .utils.datatype_conversion import int_to_multiples_of_2
from .utils.file_writer import DirectoryCreator

from .veritas.error_catalog_generation.error_state import (
    ErrorState,
    ErrorStateRegistry,
    MISSING_BIT_STRINGS,
)
from .veritas.scorecard_distillation.scorecard_distiller import (
    DataQuality,
)

from .veritas.datatypes import ForeignKey

from _strptime import TimeRE


class Dataset:

    def __init__(self):
        self._dataset_files = {}

    @property
    def dataset_files(self):
        for dataset_file_name, dataset_file in self._dataset_files.items():
            yield dataset_file_name, dataset_file

    def add_dataset_file(self, dataset_file_path, delimiter, dataframe_type='Pandas'):
        if dataframe_type == "Pandas":
            dataset_file = PandasDatasetFile(dataset_file_path, delimiter)
        else:
            raise TypeError("Dataframe type not recognized")

        file_name = os.path.basename(dataset_file_path)
        file_name_no_ext = os.path.splitext(file_name)[0]
        self._dataset_files[file_name_no_ext] = dataset_file

    def get_dataset_file_names(self):
        table_names = self._dataset_files.keys()
        return table_names

    def get_dataset_file(self, file_name):
        assert file_name in self._dataset_files.keys()
        dataset_file = self._dataset_files[file_name]
        return dataset_file

    def print_dataset(self, specified_output_dir: str = None):
        if specified_output_dir == None:
            output_data_dir = (
                ErrorAnnotatedDataFilePaths.output_error_annotated_directory_path
            )
        directory_creator = DirectoryCreator(error_when_file_exists=False)
        directory_creator.create_directory(output_data_dir)

        for _, dataset_file in self.dataset_files:
            dataset_file.print_table(output_data_dir)


class DatasetFile(ABC):

    @property
    @abstractmethod
    def dataframe_library(self):
        pass

    @abstractmethod
    def get_rows_outside_numerical_constraint(
        self, attribute_name: str, constraint_range: ConstraintRange
    ):
        pass

    @abstractmethod
    def get_rows_outside_date_constraint(
        self, attribute_name: str, constraint_range: ConstraintRange
    ):
        pass

    @abstractmethod
    def get_rows_where_attribute_values_equal(self, attribute_name: str, values: list) -> typing.Any:
        pass

    @abstractmethod
    def get_rows_where_attribute_values_equal(
        self, attribute_name: str, values: list
    ) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_rows_with_duplicate_values(self, attribute_name: str):
        pass

    @abstractmethod
    def get_rows_with_missing_values_from_compared(
        self, 
        compared_table: typing.Any, 
        foreign_key: ForeignKey
    ):
        pass

    @abstractmethod
    def get_list_of_values(self, attribute_name: str) -> list:
        pass

    @abstractmethod
    def identify_sequential_outliers(self, attribute_name: str) -> typing.Any:
        pass

    @abstractmethod
    def count(self, column_name: str) -> int:
        pass

    @abstractmethod
    def min(self, column_name: str) -> float:
        pass

    @abstractmethod
    def max(self, column_name: str) -> float:
        pass

    @abstractmethod
    def std_dev(self, column_name: str) -> float:
        pass

    @abstractmethod
    def mean(self, column_name: str) -> float:
        pass

    @abstractmethod
    def median(self, column_name: str) -> float:
        pass

    @abstractmethod
    def skewness(self, column_name: str) -> float:
        pass

    @abstractmethod
    def kurtosis(self, column_name: str) -> float:
        pass

    @abstractmethod
    def delta(self, column_name: str, drop_first_row: bool = True) -> typing.Any:
        pass

    @abstractmethod
    def monotonicity_ratio(self, column_name: str) -> float:
        pass

    @abstractmethod
    def print_table(self, output_file_dir: str) -> None: 
        pass

    @abstractmethod
    def create_composite_key(self, foreign_key: ForeignKey) -> None: 
        pass

    @abstractmethod
    def drop_composite_key(self) -> None:
        pass


class PandasDatasetFile(DatasetFile):

    def __init__(self, dataset_file_path, delimiter):
        self._table_name = os.path.basename(dataset_file_path)
        self._df = pd.read_csv(dataset_file_path, 
                               delimiter=delimiter, 
                               na_values=['inf', '-inf'])
        self._replace_infinite() 
        self._data_order = self._df.columns
        self._missing_records = 0.0
        self._df["error_state"] = 0b0
        self._df["probability_error"] = 0.0
        self._errors = pd.DataFrame(
            columns=[
                "table_name",
                "attribute_name",
                "error_state",
                "probability",
                "num_affected",
                "example_affected_value",
            ]
        )



    @property
    def data_column_order(self):
        return self._data_order

    @property
    def table_name(self):
        return self._table_name

    @property
    def dataframe(self) -> pd.DataFrame:
        return self._df

    @property
    def data_quality(self) -> DataQuality:
        record_count = len(self._df)
        self._df["error_state"]
        erroneous_count = self._df["probability_error"].sum()
        error_affected_count = len(self._df[self._df["error_state"] != 0b0].index)
        missing_affected_mask = (self._df["error_state"] & MISSING_BIT_STRINGS) != 0
        missing_affected_count = len(self._df[missing_affected_mask].index)
        missing_count = self._missing_records

        return DataQuality(
            record_count,
            error_affected_count,
            erroneous_count,
            missing_affected_count,
            missing_count,
        )


    def _replace_infinite(self, columns: typing.Iterable[str] | None = None,
                          with_value = pd.NA) -> None:
        """
        Replace ±inf with a finite placeholder (default: missing).
        Restrict to numeric columns by default.
        """
        if columns is None:
            columns = self._df.select_dtypes(include=[np.number]).columns
        # Only operate on columns present (guard against empty selection)
        if len(columns) == 0:
            return
        self._df[columns] = self._df[columns].replace([np.inf, -np.inf], with_value)

    def _add_new_errors_row(self, attribute_name: str, erroneous_records_df: pd.DataFrame, error_state: ErrorState, logging_column_name: str):
        new_errors_row = pd.DataFrame(
            {
                "table_name": self.table_name,
                "attribute_name": logging_column_name,
                "error_state": error_state.description,
                "probability": error_state.probability_for_state,
                "num_affected": len(erroneous_records_df.index),
                "example_affected_value": erroneous_records_df[attribute_name].iloc[0],
            },
            index=[0],
        )
        with warnings.catch_warnings(action="ignore"):
            self._errors = pd.concat([self._errors, new_errors_row], ignore_index=True)
   
    """
        TODO: Check efficiency for up front probability assignment for atomic error probabilities versus delayed
    """

    def change_record_probability_for_missing(
        self,
        attribute_name: str,
        missing_records_df: pd.DataFrame,
        error_state: ErrorState,
        logging_column_name: str, 
        result_column_name: str = "foreign_key",
    ) -> None:
        if missing_records_df is None:
            return
        affected_records_mask = self._df[attribute_name].isin(
            missing_records_df[result_column_name]
        )
        self._df.loc[affected_records_mask, "error_state"] |= error_state.error_state
        self._add_new_errors_row(result_column_name, missing_records_df, error_state, logging_column_name)
        if error_state.probability_for_state == 0:
            return
        probability_lower_than_new_mask = affected_records_mask & (
            self._df["probability_error"] < error_state.probability_for_state
        )
        self._df.loc[probability_lower_than_new_mask, "probability_error"] = (
            error_state.probability_for_state
        )

    def change_record_probability_lookup_index(
        self,
        attribute_name: str,
        erroneous_records_df: pd.DataFrame,
        error_state: ErrorState,
    ) -> None:
        if erroneous_records_df is None:
            return
        affected_records_mask = self._df.index.isin(erroneous_records_df.index)
        self._df.loc[affected_records_mask, "error_state"] |= error_state.error_state
        self._add_new_errors_row(attribute_name, erroneous_records_df, error_state, attribute_name)
        if error_state.probability_for_state == 0:
            return
        probability_lower_than_new_mask = affected_records_mask & (
            self._df["probability_error"] < error_state.probability_for_state
        )
        self._df.loc[probability_lower_than_new_mask, "probability_error"] = (
            error_state.probability_for_state
        )

    def add_missing(self, amount_missing: float) -> None:
        self._missing_records += amount_missing

    @property
    def missing(self) -> float:
        return self._missing_count

    @property
    def dataframe_library(self) -> str:
        return "Pandas"

    @property
    def num_columns(self) -> int:
        return len(self._df.columns) - 2

    @property
    def num_rows(self) -> int:
        return len(self._df)

    def get_dataset_table_name(self) -> str:
        return os.path.basename(self._table_name)

    def get_values_outside_std_dev(
        self,
        attribute_name: str,
        lower_std_dev: ConstraintRange,
        higher_std_dev: ConstraintRange,
    ):
        numeric_mask = pd.to_numeric(self._df[attribute_name], errors="coerce").isna()
        df_numeric = self._df[numeric_mask == False]
        df_outside_numerical_constraint = df_numeric[
            (
                (df_numeric[attribute_name] >= lower_std_dev.lower_bound)
                & (df_numeric[attribute_name] < lower_std_dev.upper_bound)
            )
            | (
                (df_numeric[attribute_name] > higher_std_dev.lower_bound)
                & (df_numeric[attribute_name] <= higher_std_dev.upper_bound)
            )
        ]
        if len(df_outside_numerical_constraint.index) == 0:
            return None

        return df_outside_numerical_constraint

    def get_rows_outside_numerical_constraint(
        self, attribute_name: str, constraint_range: ConstraintRange
    ):
        numeric_mask = pd.to_numeric(self._df[attribute_name], errors="coerce").isna()
        df_numeric = self._df[numeric_mask == False]
        df_outside_numerical_constraint = df_numeric[
            (df_numeric[attribute_name] < constraint_range.lower_bound)
            | (df_numeric[attribute_name] > constraint_range.upper_bound)
        ]
        if len(df_outside_numerical_constraint.index) == 0:
            return None

        return df_outside_numerical_constraint

    def get_rows_outside_date_constraint(
        self, attribute_name: str, constraint_range: ConstraintRange
    ):
        df_null_excluded = self._df[self._df[attribute_name].notnull()]
        df_null_excluded[attribute_name] = pd.to_datetime(
            df_null_excluded[attribute_name], errors="coerce"
        )
        df_outside_date_constraint = df_null_excluded[
            (df_null_excluded[attribute_name].dt.year < constraint_range.lower_bound)
            | (df_null_excluded[attribute_name].dt.year > constraint_range.upper_bound)
        ]
        if len(df_outside_date_constraint.index) == 0:
            return None

        return df_outside_date_constraint
    
    def get_rows_outside_format_constraint(
        self, attribute_name: str, format_regex: str
    ):
        df_null_excluded = self._df[self._df[attribute_name].notnull()]
        invalid_rows = df_null_excluded[attribute_name].apply(
            PandasDatasetFile._is_date_time_format_invalid, args=[format_regex]
        )
        df_outside_format_constraint = df_null_excluded[invalid_rows]

        if len(df_outside_format_constraint.index) == 0:
            return None

        return df_outside_format_constraint

    @staticmethod
    def _is_date_time_format_invalid(row, format_regex):
        found = format_regex.match(row)
        if found:
            return False
        else:
            return True

    def get_rows_where_attribute_values_equal(
        self, attribute_name: str, values: list
    ) -> pd.DataFrame:
        df_where_attribute_equals = self._df[self._df[attribute_name].isin(values)]
        if len(df_where_attribute_equals.index) == 0:
            return None        
        return df_where_attribute_equals

    def get_rows_with_duplicate_values(self, attribute_name: str):
        df_null_excluded = self._df[self._df[attribute_name].notnull()]
        df_duplicates = df_null_excluded[
            df_null_excluded.duplicated(subset=[attribute_name]) == True
        ]
        if len(df_duplicates.index) == 0:
            return None

        return df_duplicates

    def get_rows_with_missing_values_from_compared(
        self, 
        compared_table: DatasetFile, 
        foreign_key: ForeignKey
    ):
        attribute_name = foreign_key.key_name
        compared_table_attribute_name = foreign_key.primary_key_attribute_name
        df_null_excluded = self._df[self._df[attribute_name].notnull()]
        values_from_df = set(df_null_excluded[attribute_name].unique().tolist())
        values_from_compared_table = set(
            compared_table.get_list_of_values(compared_table_attribute_name)
        )
        missing_values = values_from_df.difference(values_from_compared_table)
        df_missing = self._df[self._df[attribute_name].isin(missing_values)]
        if len(df_missing.index) == 0:
            return None
        return df_missing

    def get_list_of_values(self, attribute_name: str) -> list:
        attribute_list = self._df[attribute_name].unique().tolist()
        return attribute_list
    
    def identify_sequential_outliers(self, attribute_name: str) -> pd.Series:
        outlier_detector = SequentialOutlierDetector()
        nan_rows = self._df[self._df[attribute_name].isna()]
        outlier_detector.add_NaNs(nan_rows.index)
        outlier_classifier = OutlierClassifier()
        clusters = outlier_classifier.KDE(self, attribute_name)
        outlier_detector.add_cluster_labels(clusters)
        sequential_outliers_mask= outlier_detector.detect_outliers()
        outliers_df = self._df[sequential_outliers_mask]
        if len(outliers_df.index) == 0: 
            return None
        return outliers_df

    def count(self, column_name: str) -> int:
        return self._df[column_name].count()

    def value_counts(self, column_name: str) -> pd.Series:
        return self._df[column_name].value_counts()

    def min(self, column_name: str) -> float:
        return self._df[column_name].min()

    def max(self, column_name: str) -> float:
        return self._df[column_name].max()

    def std_dev(self, column_name: str) -> float:
        return self._df[column_name].std()

    def mean(self, column_name: str) -> float:
        return self._df[column_name].mean()

    def median(self, column_name: str) -> float:
        return self._df[column_name].median()

    def skewness(self, column_name: str) -> float:
        return self._df[column_name].skew()

    def kurtosis(self, column_name: str) -> float:
        return self._df[column_name].kurt()
    
    def delta(self, column_name: str, drop_first_row: bool = True) -> pd.Series:
        delta = self._df[column_name].dropna()
        delta = delta.diff()
        if drop_first_row == True:
            delta = delta.dropna()
        delta = delta.abs()
        return delta 
    
    def monotonicity_ratio(self, column_name: str) -> float:
        column_no_nans = self._df[column_name].dropna()
        sequence_np = column_no_nans.to_numpy()
        return monotonicity_ratio(sequence_np)
    
    def print_column(self, column_name: str) -> None:
        print(self._df[column_name])

    def print_table(self, output_data_dir, file_extension=".csv") -> None:
        self._errors.to_csv(
            os.path.join(output_data_dir, "errors.csv"),
            mode="a",
            header=not os.path.exists(os.path.join(output_data_dir, "errors.csv")),
            index=False,
        )
        self._df["error_state"] = self._df["error_state"].apply(
            lambda x: int_to_multiples_of_2(x, ErrorStateRegistry.HIGHEST_CURRENT_BIT)
        )

        # Normalize extension (ensure it starts with a dot)
        ext = file_extension if file_extension.startswith('.') else '.' + file_extension
    
        # Remove duplicate extension if present in table_name
        table_name = self._table_name[:-len(ext)] if self._table_name.endswith(ext) else self._table_name
    
        self._df.to_csv(
            os.path.join(output_data_dir, (table_name + file_extension)),
            index=False,
            quoting=csv.QUOTE_NONNUMERIC,
        )

    def create_composite_key(self, attributes: list[str]) -> None:
        self._df['composite_key'] = ''
        for partial_key in attributes:
            self._df['composite_key'] += '_' + self._df[partial_key].astype(str)
        self._df[self._df['composite_key'] == '']['composite_key'] = pd.NA

    def drop_composite_key(self) -> None:
        self._df = self._df.drop(['composite_key'], axis=1)
