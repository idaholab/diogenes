# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

def format_error(error):
    formatted_error = '\n\n' + str(error) + '\n\n'
    return formatted_error  


class ConstraintErrorHandler:


    def __init__(self, line_number):
        self.__line_number = line_number


    def raise_could_not_set_constraint_error(self, error):
        error_message = format_error(error)
        error_message += "Could not set constraint for unit on line {}".format(self.__line_number)
        raise IOError(error_message)


    def non_numeric_meta_data(self, error, value):
        error_message = format_error(error)
        error_message += "Metadata value is not numeric: {}".format(value)
        raise IOError(error)