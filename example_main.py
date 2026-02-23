# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os
import datetime

os.chdir("metadata")

ENABLE_ANNOTATION_TOOL = False

from metadata.generate_metadata import run_metadata_generation
from annotation_tool.start import start_annotation

def main():

    dataset_id = 'ds2'
    annotation_agent = 'ml_tree' #{"none": BaseAgent, "tree": TreeAgent, "ml_tree": MLTreeAgent}

    cur_dir = os.path.abspath(os.path.dirname(__file__))

    input_dir = os.path.join(cur_dir,'example_input')
    input_folder = os.path.join(input_dir, dataset_id)
    output_dir = os.path.join(cur_dir,'output',dataset_id)
    description_path = os.path.join(input_dir,'descriptive_information','descriptions.csv')
    annotations_path = os.path.join(input_folder, "descriptive_information", "annotations.xlsx")

    if not os.path.exists(description_path):
        description_path = None

    if ENABLE_ANNOTATION_TOOL:
        if  os.path.exists(annotations_path):
            stamp = datetime.datetime.now().strftime("%m%d%y%H%M")
            old_path = os.path.join(input_folder, "descriptive_information", f"annotations_{stamp}.xlsx")
            os.rename(annotations_path, old_path)

        start_annotation(tree=annotation_agent, output=input_folder+'/descriptive_information', desc=description_path, counts=True, input=input_folder+'/data')
    
    #run_metadata_generation(identifier='ds2', annotations='true', input_path=input_folder) # creates output folder in diogenes/metadata/output
    run_metadata_generation(identifier=dataset_id, annotations='true', input_path=input_folder, output_path=output_dir) #creates output folder at the location specified by out_dir

    
if __name__ == "__main__":
    main()