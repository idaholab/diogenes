# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os
from xlsxwriter import Workbook
import pandas as pd
from .constants import DATA_TYPES, DATA_QUALITY_CLASSES, ROW_LIMIT, UNITS


class Annotator:
    def __init__(self, input_directory, output_directory, agent, description_file):
        self.input_directory = input_directory

        self.out_file_path = os.path.join(output_directory, "annotations.xlsx")
        if os.path.exists(self.out_file_path):
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

    def _get_data_files(self):
        return [f for f in os.listdir(self.input_directory) if f.endswith('.csv')]

    def _get_row_names(self, data):
        return list(data.columns.str.strip())

    def _create_sheet(self, input_file):
        sheet_name = os.path.basename(input_file)[:31]
        sheet = self.wb.add_worksheet(sheet_name)

        self._create_header(sheet, input_file)

        data = pd.read_csv(
            os.path.join(self.input_directory, input_file),
            nrows=ROW_LIMIT,
            low_memory=False,
        )
        row_names = self._get_row_names(data)
        self._create_rows(sheet, row_names)
        if self.descriptions is not None:
            self._add_descriptions(sheet, row_names)

        self._add_validation(sheet, len(row_names))

        self._run_agent(sheet, row_names, data)

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

    def _add_validation(self, sheet, row_count):
        sheet.data_validation(1, 1, 1 + row_count, 1, self.data_drop_down)
        sheet.data_validation(1, 2, 1 + row_count, 2, self.quality_drop_down)
        sheet.data_validation(1, 5, 1 + row_count, 5, self.unit_drop_down)
        sheet.conditional_format(1, 1, 1 + row_count, 2, self.validation_format)

    def _run_agent(self, sheet, row_names, data):
        for i, row_name in enumerate(row_names):
            row = data[row_name]
            type_guess, class_guess = self.agent.guess(row_name, row)
            sheet.write(1 + i, 1, type_guess)
            sheet.write(1 + i, 2, class_guess)

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
