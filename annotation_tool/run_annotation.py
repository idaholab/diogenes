# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os

# There's got to be a better way...
from .Annotator import Annotator, create_counts
from .Agents import BaseAgent, TreeAgent, MLTreeAgent

ASSIST_AGENTS = {"none": BaseAgent, "tree": TreeAgent, "ml_tree": MLTreeAgent}


def run_annotation(tree, output, desc, counts, input):
    input_directory = input
    output_directory = output
    description_file = desc
    generate_counts = counts
    assist = tree

    if not os.path.exists(input_directory):
        raise RuntimeError("Input Directory doesn't exist! Please create it!")
    if not os.path.exists(output_directory):
        raise RuntimeError("Output Directory doesn't exist! Please create it!")
    if description_file is not None:
        if not os.path.exists(description_file):
            raise RuntimeError("Description file doesn't exist!")
    if assist not in ASSIST_AGENTS:
        raise RuntimeError(
            "Assistant Agent Chosen is invalid, please choose one from the following:"
            + ASSIST_AGENTS
        )

    # Grab and initialize the assist agent
    agent = ASSIST_AGENTS[assist]()

    # Let's actually run the helper now
    print(f"Generating Annotations")
    annotator = Annotator(input_directory, output_directory, agent, description_file)
    annotator.create_annotation_file()

    # And finally, create the data counts if requested
    if generate_counts:
        data_count_directory = os.path.join(output_directory, "data_counts")
        print(f'Creating Data Counts in "{os.path.abspath(data_count_directory)}"')
        create_counts(input_directory, data_count_directory)
