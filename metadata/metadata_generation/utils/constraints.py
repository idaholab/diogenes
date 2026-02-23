# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import math

from dataclasses import dataclass

from ..utils.file_iterator import CSVIterator
from ..utils.datatype_conversion import format_for_string_equality
from ..utils.error_handling import ConstraintErrorHandler


@dataclass
class ConstraintRange:

    _upper_bound = None
    _lower_bound = None

    def __init__(self, line_number=None):
        self._constraint_error_handler = ConstraintErrorHandler(line_number)

    @property
    def lower_bound(self) -> float:
        return self._lower_bound
    
    @lower_bound.setter
    def lower_bound(self, lower_bound: float) -> None:
        try:
            self._lower_bound = -math.inf

            if format_for_string_equality(lower_bound) != 'n/a':
                self._lower_bound = float(lower_bound)

        except Exception as error:
            self._constraint_error_handler.raise_could_not_set_constraint_error(error)

    @property 
    def upper_bound(self) -> float:
        return self._upper_bound
    
    @upper_bound.setter
    def upper_bound(self, upper_bound: float) -> None:
        try:
            self._upper_bound = math.inf

            if format_for_string_equality(upper_bound) != 'n/a':
                self._upper_bound = float(upper_bound)
        except Exception as error:
            self._constraint_error_handler.raise_could_not_set_constraint_error(error)


class Constraint:

    def __init__(self, lower_bound: float, upper_bound: float, line_number: int = -1):
        self._constraint_range = ConstraintRange(line_number)
        self._constraint_range.lower_bound = lower_bound
        self._constraint_range.upper_bound = upper_bound
        self._constraint_error_handler = ConstraintErrorHandler(line_number)

    def within_constraint(self, value: int | float | str) -> bool:
        try:
            within_constraint = False

            if self._constraint_range.lower_bound <= float(value) <= self._constraint_range.upper_bound:
                within_constraint = True

        except Exception as error:
            self._constraint_error_handler.non_numeric_meta_data(error, value)

        return within_constraint
    
    def get_constraint_range(self) -> ConstraintRange: 
        return self._constraint_range


class Constraints:

    EXPECTED_NUMBER_OF_COLUMNS = 4

    def __init__(self, file_path):
        self._constraints = {}

        self._file_iterator = CSVIterator(file_path, skip_header=True)
        self._file_iterator.open_file()

    def set_constraints(self) -> None:
        line_number = 0

        for line_number in self._file_iterator.iterate_lines():
            tokenized_line = self._file_iterator.get_tokenized_line(self.EXPECTED_NUMBER_OF_COLUMNS)

            name = tokenized_line[0]
            (lower_bound, upper_bound) = (tokenized_line[1], tokenized_line[2])
            constraint = Constraint(lower_bound, upper_bound, line_number)

            self._constraints[name] = constraint
        
        self._file_iterator.close_file()

    def in_constraints(self, constraint_name: str) -> bool:
        in_constraints = False 

        if constraint_name in self._constraints.keys():
            in_constraints = True   

        return in_constraints  
    
    def get_constraint(self, constraint_name: str) -> Constraint: 
        if not self.in_constraints(constraint_name):
            return None

        constraint = self._constraints[constraint_name]
        return constraint

    def within_constraint(self, constraint_name: str, value: int | float | str) -> bool:
        value_within_constraint = False 
        
        if self.in_constraints(constraint_name):
            value_within_constraint = self._constraints[constraint_name].within_constraint(value)    
        else:
            raise IOError("Constraint is missing: {}".format(constraint_name))

        return value_within_constraint
    
      
class VeritasConstraints:

    def __init__(self):
        self.general_constraints = None
        self.unit_contraints = None




          