# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import sys
import os

pytest_plugins = [
    "test.fixtures.input", 
    "test.fixtures.error_catalog_generation",
    "test.fixtures.scorecard_distillation"
]
