# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pandas as pd
import warnings
from .Agent import BaseAgent


class TreeAgent(BaseAgent):
    """
    This is a simple (manually created) decision tree.
    It should be able to do a fair bit of simple annotation work.
    However, it is purposefully conservative, as we wish to avoid false annotations.
    Expect to have to manually annotate ~25% of the remaining annotations.
    """

    def __init__(self):
        self.max_categories = 1000
        self.categorical_cutoff = 0.33
        pass

    def guess(self, row_name, data):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            type_guess = self._guess_type(row_name, data)
        class_guess = self._guess_class(data, type_guess)
        return type_guess, class_guess

    def _guess_type(self, row_name, data):
        data = data.dropna()
        pd_guess = data.convert_dtypes().dtype
        data_type = "?"
        if len(data) == 0:
            data_type = "(redacted)"
        elif len(data) == 1 and "redact" in str(data.item()).lower():
            data_type = "(redacted)"
        elif pd_guess == "boolean":
            data_type = "boolean"
        elif pd_guess == "string":
            if "time" in row_name.lower():
                data_type = "time"
            try:
                pd.to_datetime(data)
                # Check to see if it has a time aspect.
                if data_type == "time":
                    data_type = "date-time"
                else:
                    # It could be "date" or "date-time"...
                    data_type = "?date"
            except:
                if "data_type" != "time":
                    tmp = data.str.lower().unique()
                    if len(tmp) <= 2 and ("true" in tmp or "false" in tmp):
                        data_type = "boolean"
                    else:
                        # To Do:
                        # Add detection for json / xml / blob.
                        data_type = "string"

        elif pd_guess == "Int64":
            data_type = "integer"
        elif pd_guess == "Float64":
            data_type = "float"

        return data_type

    def _guess_class(self, data, type_guess):
        if len(data.value_counts()) == 0 or type_guess == "(redacted)":
            return "none"

        if type_guess == "time":
            return "none"

        if type_guess == "date" or type_guess == "date-time":
            return "date"

        if type_guess == "?date":
            return "?date"

        if self._is_key(data):
            return "primary_key"

        if self._is_categorical(data) and type_guess != "float":
            if type_guess == "integer":
                return "?categorical"
            else:
                return "categorical"

        if type_guess == "integer" or type_guess == "float":
            return "numerical"

        if type_guess == "string":
            # Default return type for strings is categorical...
            return "categorical"

        return "?"

    def _is_key(self, data):
        return len(data.value_counts()) == len(data)

    def _is_categorical(self, data):
        if len(data.value_counts() <= self.max_categories):
            if len(data.value_counts()) / len(data) <= self.categorical_cutoff:
                return True
        return False
