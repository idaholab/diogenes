# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

from dataclasses import dataclass

@dataclass
class JSONIndex:

    table_metadata_index: int
    attribute_metadata_index: int


