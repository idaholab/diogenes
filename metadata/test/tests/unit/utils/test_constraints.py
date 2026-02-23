# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest
import math

from test.fixtures.input import good_unit_configuration_file_path

from metadata_generation.utils.constraints import Constraints, Constraint, ConstraintRange


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * *  Constraints Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


def test_in_constraints(good_unit_configuration_file_path):
    constraints = Constraints(good_unit_configuration_file_path)
    constraints.set_constraints()

    assert constraints.in_constraints('V') == True
    assert constraints.in_constraints('monkeys') == False


@pytest.mark.parametrize(
    'value, expected_bool', 
    [(0, True), 
     (100, True),
     (50, True), 
     (101, False),
     ('0', True), 
     ('100', True),
     ('50', True), 
     ('101', False)] 
)
def test_constraints_within_constraint(value, expected_bool, good_unit_configuration_file_path):
    constraints = Constraints(good_unit_configuration_file_path)
    constraints.set_constraints()   

    bool_value = constraints.within_constraint('percent', value) 

    assert bool_value == expected_bool


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * Constraint Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'value, expected_bool', 
    [(9, True), 
     (-9, True),
     (11, False), 
     (-11, False),
     ('9', True), 
     ('-9', True),
     ('11', False), 
     ('-11', False),
     ('-9.5', True), 
     ('10.5', False)]       
)
def test_constraint_within_constraint(value, expected_bool):
    lower_bound = -10
    upper_bound = 10
    line_number = 1

    constraint = Constraint(lower_bound, upper_bound, line_number)
    bool_value = constraint.within_constraint(value)

    assert bool_value == expected_bool


@pytest.mark.parametrize(
    'lower_bound, upper_bound, expected_bool', 
    [(-math.inf, 10, False), 
     (10, math.inf, True),
     (11, math.inf, False), 
     (-math.inf, 10.5, True), 
     (10.5, math.inf, True),
     (10.6, math.inf, False), 
     (-math.inf, 10.4, False)]       
)
def test_constraint_within_constraint_move_constraints(lower_bound, upper_bound, expected_bool):
    value_to_be_measured = 10.5
    line_number = 1

    constraint = Constraint(lower_bound, upper_bound, line_number)
    bool_value = constraint.within_constraint(value_to_be_measured)

    assert bool_value == expected_bool


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * *  ConstraintRange Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'lower_bound, expected', 
    [(1, 1), 
     ('N/A', -math.inf),
     ('n/A', -math.inf)] 
)
def test_set_lower_bound_good(lower_bound, expected):
    line_number = 1
    constraint_range = ConstraintRange(line_number)
    constraint_range.set_lower_bound(lower_bound)

    assert constraint_range.lower_bound == expected


def test_set_lower_bound_bad():
    bad_lower_bound = '1a'
    line_number = 1
    constraint_range = ConstraintRange(line_number)
    
    with pytest.raises(IOError):
        constraint_range.set_lower_bound(bad_lower_bound)


@pytest.mark.parametrize(
    'upper_bound, expected', 
    [(1, 1), 
     ('N/A', math.inf),
     ('n/A', math.inf)] 
)
def test_set_upper_bound_good(upper_bound, expected):
    line_number = 1
    constraint_range = ConstraintRange(line_number)
    constraint_range.set_upper_bound(upper_bound)
    assert constraint_range.upper_bound == expected


def test_set_upper_bound_bad():
    bad_upper_bound = '1a'
    line_number = 1
    constraint_range = ConstraintRange(line_number)
    
    with pytest.raises(IOError):
        constraint_range.set_upper_bound(bad_upper_bound)
