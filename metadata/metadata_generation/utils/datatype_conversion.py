# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import re
import numpy as np


def convert_string_to_bool(bool_string):
    lowercase_bool_string = bool_string.lower()
    processed_bool_string = lowercase_bool_string.strip()

    if processed_bool_string == 'true':
        bool_value = True
    elif processed_bool_string == 'false':
        bool_value = False
    else:
        raise TypeError("Could not convert value to bool: {}".format(bool_string))

    return bool_value

def format_for_string_equality(parsed_value):
    formatted_value = parsed_value 

    if type(parsed_value) == str:
        lowered_value = parsed_value.lower()
        formatted_value = lowered_value.strip()
        
    return formatted_value

def is_string_integer(value):
    is_string_integer = False

    if isinstance(value, str) or isinstance(value, object):
        try:
            if float(value) - convert_string_to_int(value) == 0:
                is_string_integer = True
        except ValueError:
            pass

    return is_string_integer

def is_numeric_integer(value):
    is_numeric_integer = False

    if not isinstance(value, str) and not isinstance(value, object): 
        if value - int(value) == 0:
            is_numeric_integer = True

    return is_numeric_integer

def convert_string_to_int(value):
    return int(round(float(value)))


def int_to_multiples_of_2(original_int: int, highest_bit: int) -> str:
    bit_string = format(original_int, str(highest_bit) + 'b')
    assert len(bit_string) == highest_bit

    multiples_of_2_str = ''
    current_multiple_of_2 = highest_bit - 1 #the multiple of two is len(bit_str) - 1
    for bit in bit_string:
        if bit == '1':
            multiples_of_2_str = str(current_multiple_of_2) + ',' + multiples_of_2_str
        current_multiple_of_2 -= 1
    
    return multiples_of_2_str[:-1]

