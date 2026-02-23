# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from .Agent import BaseAgent
from .Tree import TreeAgent
import pandas as pd
import numpy as np
import os
import json
from pickle import dump, load
import glob


ML_TREE_DISABLED = False
try:
    from sklearn.tree import DecisionTreeClassifier
except ModuleNotFoundError:
    print("Warning, scikit-learn cannot be found, this will disable the ML Tree Model.")
    ML_TREE_DISABLED = True


class MLTreeAgent(BaseAgent):
    """
    This is a decision tree trained on livewire data to make automatic type and class annotations.
    """

    max_depth = 5

    def __init__(self):
        if ML_TREE_DISABLED:
            raise RuntimeError("ML Tree is disabled without scikit-learn.")

        self.manual_tree = TreeAgent()

        dirname = os.path.dirname(__file__)
        self.class_path = os.path.join(dirname, "data", "sklearn_class_tree.pickle")
        self.type_path = os.path.join(dirname, "data", "sklearn_type_tree.pickle")

        if os.path.exists(self.class_path) and os.path.exists(self.type_path):
            self.need_training = False
            with open(self.class_path, "rb") as f:
                self.class_tree = load(f)
            with open(self.type_path, "rb") as f:
                self.type_tree = load(f)
        else:
            self.need_training = True
            self.class_tree = DecisionTreeClassifier(
                max_depth=self.max_depth, max_features="sqrt"
            )
            self.type_tree = DecisionTreeClassifier(
                max_depth=self.max_depth, max_features="sqrt"
            )

        self.class_map = {
            "?": -1,
            "none": 0,
            "date": 1,
            "?date": 2,
            "primary_key": 3,
            "?categorical": 4,
            "categorical": 5,
            "numerical": 6,
        }

        self.type_map = {
            "?": -1,
            "(redacted)": 0,
            "boolean": 1,
            "time": 2,
            "date-time": 3,
            "?date": 4,
            "string": 5,
            "integer": 6,
            "float": 7,
        }

        if self.need_training:
            print("Hello, the model needs to be trained!")
            print("Please enter the data input directory!")
            input_dir = input()
            print("Training on your data... This may take a while!")
            self._train(input_dir)
            print("Saving dataset!")
            self._save()

    def _get_data(self, files):
        input_names = []
        input_data = []
        true_types = []
        true_classes = []

        for file_path in files:
            data = None
            with open(file_path) as file:
                data = json.load(file)

            for data_piece in data["data"]:
                true_types.append(data_piece["data_type"])
                true_classes.append(data_piece["data_class"])

                input_data.append(data_piece["data"])
                input_names.append(data_piece["name"])

        true_types = [x if type(x) == str else "string" for x in true_types]
        true_classes = [x if type(x) == str else "none" for x in true_classes]
        return input_names, input_data, true_types, true_classes

    def _train(self, input_directory):
        files = glob.glob(input_directory + r"\*\*.json")
        input_names, input_data, true_types, true_classes = self._get_data(files)
        self.fit(input_names, input_data, true_types, true_classes)

    def _save(self):
        with open(self.class_path, "wb") as f:
            dump(self.class_tree, f)
        with open(self.type_path, "wb") as f:
            dump(self.type_tree, f)

    def _process_data(self, row_names, data):
        processed_data = []
        for row_name, x in zip(row_names, data):
            x = pd.Series(x)

            # Values to aquire
            if len(x):
                cat_ratio = len(x.value_counts()) / len(x)
            else:
                cat_ratio = 0
            tree_type, tree_class = self.manual_tree.guess(row_name, x)
            tree_type = self.type_map[tree_type]
            tree_class = self.class_map[tree_class]

            # Numerical Stuff
            if pd.api.types.is_numeric_dtype(x):
                # Clean up data so it's numeric
                x = pd.to_numeric(x, errors="coerce")
                # Okay, to make sure this works with sklearn, let's convert these to np.float16 values
                max_float32 = np.finfo(np.float32).max - 1
                min_float32 = np.finfo(np.float32).min + 1
                x = x.where((x < max_float32) & (x > min_float32))
                x = x.replace([-np.inf, np.inf], np.nan)
                x = x.astype(np.float32)
                x = x.dropna()

                is_numerical = 1
                mean = x.mean()
                median = x.median()
                standard_deviation = x.std()
                mode_min = x.mode().min()
                mode_max = x.mode().max()
                min_val = x.min()
                max_val = x.max()

            else:
                is_numerical = 0
                mean = 0
                median = 0
                standard_deviation = 0
                mode_min = 0
                mode_max = 0
                min_val = 0
                max_val = 0

            processed_data.append(
                [
                    tree_type,
                    tree_class,
                    cat_ratio,
                    is_numerical,
                    mean,
                    median,
                    standard_deviation,
                    mode_min,
                    mode_max,
                    min_val,
                    max_val,
                ]
            )

        return np.array(processed_data).astype(np.float32)

    def fit(self, row_name, data, true_type, true_class):
        processed_data = self._process_data(row_name, data)
        self.type_tree.fit(processed_data, true_type)
        self.class_tree.fit(processed_data, true_class)

    def guess(self, row_name, data, cutoff: float = 0.75):
        processed_data = self._process_data([row_name], [data])
        # Get the probabilities
        type_probabilities = self.type_tree.predict_proba(processed_data)[0]
        class_probabilities = self.class_tree.predict_proba(processed_data)[0]
        max_type = max(type_probabilities)
        max_class = max(class_probabilities)

        guess_type = str(self.type_tree.classes_[type_probabilities.argmax()])
        guess_class = str(self.class_tree.classes_[class_probabilities.argmax()])

        # Here's the cut-off for whether we think it's a guess or not
        if max_type < cutoff:
            guess_type = "?" + guess_type
        if max_class < cutoff:
            guess_class = "?" + guess_class

        # Manual Override for (redacted)
        if processed_data[0][0] == 0:
            guess_type = "(redacted)"
            guess_class = "none"

        return guess_type, guess_class
