# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os.path

def check_if_file_exists(file_path):
    if not os.path.isfile(file_path):
        raise IOError("File does not exist: '{}'".format(file_path))


def check_if_path_exists(path):
    if not os.path.exists(path):
        raise IOError("Path does not exist: '{}".format(path))





