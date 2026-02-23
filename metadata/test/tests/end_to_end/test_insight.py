# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest
import pandas as pd
import json

from metadata_generation.utils.file_system_tools_proto import json_loader
from metadata_generation.settings import MetadataGenerationSettings

from metadata_generation.metadata_generation_input import MetadataGenerationInput
from metadata_generation.insight.factory import llmd_factory


def test_insight_end_to_end():
    settings = MetadataGenerationSettings()
    settings.file_extension = '.csv'
    settings.delimiter = ',' 
    metadata_generation_input = MetadataGenerationInput(settings)

    resulting_llmd = llmd_factory.create_llmd(metadata_generation_input, write_excel=True)
    expected_llmd = json_loader.load_json('C:/Users/RUMSPD/source/repos/livewire/metadata_generation/test/test_data/metadata/results/correct_insight_results_1.json')
    assert resulting_llmd == expected_llmd