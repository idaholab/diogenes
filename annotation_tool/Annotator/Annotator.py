# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os
import random
from xlsxwriter import Workbook
import pandas as pd
from .constants import DATA_TYPES, DATA_QUALITY_CLASSES, ROW_LIMIT, UNITS


class Annotator:
    def __init__(self, input_directory, output_directory, agent, description_file):
        self.input_directory = input_directory

        self.out_file_path = os.path.join(output_directory, "annotations.xlsx")
        self.out_text_path = os.path.join(output_directory, "annotations.txt")
        if os.path.exists(self.out_file_path) or os.path.exists(self.out_text_path):
            raise RuntimeError(
                "Annotator attempted to overwrite an existing file!\nFor safety reasons this behavior is not allowed!"
            )

        self.agent = agent

        if description_file is not None:
            self.descriptions = pd.read_csv(description_file)
            self.descriptions["Name"] = self.descriptions["Name"].str.lower()
        else:
            self.descriptions = None

    def create_annotation_file(self):
        self.wb = Workbook(self.out_file_path)
        # Formatting Stuff
        self.header_format = self.wb.add_format({"bold": True, "border": 2})
        self.error_format = self.wb.add_format(
            {"bg_color": "#FFC7CE", "font_color": "#9C0006"}
        )
        self.validation_format = {
            "type": "text",
            "criteria": "begins with",
            "value": "?",
            "format": self.error_format,
        }
        self.data_drop_down = {"validate": "list", "source": DATA_TYPES}
        self.quality_drop_down = {"validate": "list", "source": DATA_QUALITY_CLASSES}
        self.unit_drop_down = {"validate": "list", "source": UNITS, "show_error": False}

        # Go through and create the sheets...
        # Agent Effectiveness Variables
        self.guesses = 0
        self.no_guesses = 0
        self.total_rows = 0
        self.text_data = []
        for input_file in self._get_data_files():
            self._create_sheet(input_file)

        # Save the annotation file
        self.wb.close()
        # Helpful Terminal Stuff
        # I'm multiplying total_rows by 2 so we can get % of annotations instead of % of rows
        self.total_rows *= 2
        guess_rate = 100 * (self.guesses / self.total_rows)
        fill_rate = 100 * ((self.total_rows - self.no_guesses) / self.total_rows)

        print(f"Agent completed {fill_rate:.2f}% of the annotations")
        print(f"Agent guessed for {guess_rate:.2f}% of the annotations")

        print(f'Saved annotations file at "{os.path.abspath(self.out_file_path)}"')
        print("Please ensure to complete and verify the generated annotations!")

        self._write_text_file()

    def _get_data_files(self):
        return [f for f in os.listdir(self.input_directory) if f.endswith('.csv')]

    def _get_row_names(self, data):
        return list(data.columns.str.strip())

    def _create_sheet(self, input_file):
        # Use only the table name (last dot-separated segment before the extension)
        # to avoid exceeding Excel's 31-character sheet name limit
        base = os.path.splitext(os.path.basename(input_file))[0]
        sheet_name = base.split(".")[-1][:31]
        sheet = self.wb.add_worksheet(sheet_name)

        self._create_header(sheet, input_file)

        filepath = os.path.join(self.input_directory, input_file)
        with open(filepath) as f:
            total_rows = sum(1 for _ in f) - 1  # subtract header row

        if total_rows <= ROW_LIMIT:
            data = pd.read_csv(filepath, low_memory=False)
        else:
            skip_prob = 1 - ROW_LIMIT / total_rows
            skip_rows = lambda i: i > 0 and random.random() < skip_prob
            data = pd.read_csv(filepath, skiprows=skip_rows, low_memory=False)
            # For columns that appear entirely null in the sample, fall back to the
            # full column so sparse entries (e.g. a single "REDACTED" value) are not
            # silently dropped and misclassified as (none).
            null_cols = [col for col in data.columns if data[col].isna().all()]
            if null_cols:
                full_sparse = pd.read_csv(filepath, usecols=null_cols, low_memory=False)
                for col in null_cols:
                    data[col] = full_sparse[col]
        row_names = self._get_row_names(data)
        self._create_rows(sheet, row_names)
        if self.descriptions is not None:
            self._add_descriptions(sheet, row_names)

        self._add_validation(sheet, len(row_names))

        descriptions = self._collect_descriptions(row_names)
        row_results = self._run_agent(sheet, row_names, data)

        self.text_data.append({
            "file": input_file,
            "rows": [
                {
                    "name": row_names[i],
                    "type": row_results[i][0],
                    "class": row_results[i][1],
                    "description": descriptions.get(row_names[i], ""),
                }
                for i in range(len(row_names))
            ],
        })

    def _create_header(self, sheet, input_file):
        sheet.freeze_panes(1, 1)
        columns = [
            "Name",
            "Type",
            "Data Quality Class",
            "Description",
            "Format Function",
            "Units",
            "Relationships",
            "Notes",
            "Files",
            "Manual Annotations",
        ]

        for i in range(0, len(columns)):
            sheet.write(0, i, columns[i], self.header_format)

        sheet.write(1, 8, input_file)

    def _create_rows(self, sheet, row_names):
        # Add rows.
        for i in range(0, len(row_names)):
            sheet.write(1 + i, 0, row_names[i], self.header_format)

    def _add_descriptions(self, sheet, row_names):
        for i in range(0, len(row_names)):
            row_key = row_names[i].lower()
            description = self.descriptions[self.descriptions["Name"] == row_key]
            if len(description) > 0:
                description = str(description["Label"].values[0])
                sheet.write(1 + i, 3, description)

    def _collect_descriptions(self, row_names):
        if self.descriptions is None:
            return {}
        result = {}
        for row_name in row_names:
            row_key = row_name.lower()
            match = self.descriptions[self.descriptions["Name"] == row_key]
            if len(match) > 0:
                result[row_name] = str(match["Label"].values[0])
        return result

    def _add_validation(self, sheet, row_count):
        sheet.data_validation(1, 1, 1 + row_count, 1, self.data_drop_down)
        sheet.data_validation(1, 2, 1 + row_count, 2, self.quality_drop_down)
        sheet.data_validation(1, 5, 1 + row_count, 5, self.unit_drop_down)
        sheet.conditional_format(1, 1, 1 + row_count, 2, self.validation_format)

    def _run_agent(self, sheet, row_names, data):
        results = []
        for i, row_name in enumerate(row_names):
            row = data[row_name]
            type_guess, class_guess = self.agent.guess(row_name, row)
            sheet.write(1 + i, 1, type_guess)
            sheet.write(1 + i, 2, class_guess)
            results.append((type_guess, class_guess))

            # Effectiveness Measurements
            self.total_rows += 1
            if type_guess == "?":
                self.no_guesses += 1
            elif "?" in type_guess:
                self.guesses += 1

            if class_guess == "?":
                self.no_guesses += 1
            elif "?" in class_guess:
                self.guesses += 1
        return results

    def _write_text_file(self):
        width = 80
        sep = "=" * width
        thin_sep = "-" * width

        with open(self.out_text_path, "w") as f:
            f.write("ANNOTATIONS REVIEW\n")
            f.write(f"Generated by Diogenes Annotation Tool\n")
            f.write(f"Source: {os.path.abspath(self.input_directory)}\n")
            f.write(sep + "\n\n")

            for sheet in self.text_data:
                f.write(sep + "\n")
                f.write(f"  FILE: {sheet['file']}\n")
                f.write(sep + "\n\n")

                label_w = 24
                for row in sheet["rows"]:
                    f.write(f"  {row['name']}\n")
                    f.write(f"    {'Type':<{label_w}}{row['type']}\n")
                    f.write(f"    {'Data Quality Class':<{label_w}}{row['class']}\n")
                    if row["description"]:
                        f.write(f"    {'Description':<{label_w}}{row['description']}\n")
                    f.write(f"  {thin_sep[2:]}\n")

                f.write("\n")

        print(f'Saved annotations text file at "{os.path.abspath(self.out_text_path)}"')
