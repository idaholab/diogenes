# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import os, json
import shutil

from pathlib import Path


main_keys_ordered = ['identifier', 'title', 'shortName', 'description', 'identifierSchema', 'accessLevel', \
                     'accessRestriction', 'bureauCode', 'programCode', 'contactPoint', 'keyword', 'spatial', \
                     'temporal', 'publisher', 'modified', 'distribution', 'describedBy', 'describedByType', 'references',  \
                     'landingPage', '@type', 'rights', 'accrualPeriodicity', 'conformsTo', 'dataQuality', \
                     'issued', 'language', 'license', 'primaryITInvestmentUII', 'systemOfRecords', 'isPartOf', \
                     'theme', 'doiName']

def has_attribute_value_in_dict_list(current_metadata: list, attribute: str, value: str) -> tuple[bool, int]:
    for index, dict_entry in enumerate(current_metadata):
        if attribute in dict_entry.keys():
            if dict_entry[attribute] == value:
                return True, index
    return False, -1

def add_references(current_metadata: dict, referenceURL_pdf: str, reference_URL_json: str) -> dict:
    reference_attribute_name = 'references'
    reference_pdf = {'referenceTitle' : 'Livewire Data Dictionary: ' + current_metadata['title'] + ' (PDF)', \
                     'referenceCategory' : 'platform-reference', 
                     'referenceURL' : f'{referenceURL_pdf}.pdf'}
                     
    reference_json = {'referenceTitle' : 'Livewire Detailed Metadata: ' + current_metadata['title'] + ' (JSON)', \
                     'referenceCategory' : 'platform-metadata', 
                     'referenceURL' : f'{reference_URL_json}.json'}
    
    if reference_attribute_name not in current_metadata.keys():
        current_metadata[reference_attribute_name] = []        

    has_pdf, index_pdf = has_attribute_value_in_dict_list(current_metadata[reference_attribute_name], 'referenceCategory', 'platform-reference')
    has_json, index_json = has_attribute_value_in_dict_list(current_metadata[reference_attribute_name], 'referenceCategory', 'platform-metadata')
    print(index_pdf)
    print(index_json)
    if has_pdf and has_json:
        current_metadata[reference_attribute_name][index_pdf] = reference_pdf
        current_metadata[reference_attribute_name][index_json] = reference_json
        print(current_metadata[reference_attribute_name])
        return current_metadata[reference_attribute_name]
    elif has_pdf or has_json:
        raise IOError('Project metadata: has pdf or json entry but not both')
    
    current_metadata[reference_attribute_name].append(reference_pdf)
    current_metadata[reference_attribute_name].append(reference_json)
        
    return current_metadata[reference_attribute_name]

def add_attributes_in_order(current_metadata: dict, reference_URL_pdf: str, reference_URL_json: str) -> tuple[dict, str]:
    ordered_metadata = {}
    attribute_after_references = None
    references_seen = False
    for attribute in main_keys_ordered:
        if attribute not in main_keys_ordered:
            raise IOError(f'Unrecognized project metadata (dataset) attribute {attribute}')
        elif attribute == 'describedBy':
            ordered_metadata['describedBy'] = reference_URL_json + '.json'
        elif attribute == 'describedByType':
            ordered_metadata['describedByType'] = 'application/json'
        elif attribute == 'references':
            ordered_metadata['references'] = add_references(current_metadata, reference_URL_pdf, reference_URL_json)
            references_seen = True
        elif attribute not in current_metadata.keys():
            continue 
        else:
            if references_seen and attribute_after_references == None:
                attribute_after_references = attribute
            ordered_metadata[attribute] = current_metadata[attribute]
    
    return ordered_metadata, attribute_after_references

def get_identifiers(file_name: str) -> tuple[str, str]: 
    base_name = os.path.basename(file_name).replace('.json', '')
    project_identifier = base_name.split('.')[0]
    dataset_identifier = ''
    for partial_name in base_name.split('.')[1:]:
        dataset_identifier += partial_name + '.'
    if dataset_identifier[-1] == '.': 
        dataset_identifier = dataset_identifier[:-1]
    return project_identifier, dataset_identifier

def get_project_metadata_file_name(project_metadata_dir: str) -> str:
    for file_name in os.listdir(project_metadata_dir):
        if project_identifier in file_name: 
            project_metadata_file_name = file_name
    if project_metadata_file_name == None: 
        IOError(f'No project {project_identifier}')
    return project_metadata_file_name

def create_reference_URLs(project_identifier: str, dataset_identifier: str) -> str: 
    reference_URL_pdf = f'/api/datasets/{project_identifier}/{dataset_identifier}/files/dictionary-{project_identifier}.{dataset_identifier}'
    reference_URL_json = f'/api/datasets/{project_identifier}/{dataset_identifier}/files/dictionary-{project_identifier}.{dataset_identifier}'
    return reference_URL_pdf, reference_URL_json

def change_dataset_metadata(current_metadata: list, reference_URL_pdf: str, reference_URL_json: str) -> tuple[int, dict]:
    new_dataset_metadata = None

    for index, dataset in enumerate(current_metadata['dataset']):
        if dataset['identifier'] == dataset_identifier:
            new_dataset_metadata, attribute_after_references = add_attributes_in_order(dataset, reference_URL_pdf, reference_URL_json)
            current_metadata['dataset'][index] = new_dataset_metadata
            print(new_dataset_metadata)
            break
    if new_dataset_metadata == None: 
        raise IOError(f'No dataset identifier {dataset_identifier} in {project_identifier}')
    
    return index, current_metadata, attribute_after_references

def write_new_block(final_project_metadata_file_handle, temp_project_metadata_file_path: str, 
                    dataset_identifier: str, attribute_after_references: str):
    opened_dataset_block = False
    opened_reference_block = False
    seen_described_by_type = False
    with open(temp_project_metadata_file_path, 'r') as temp_file_handle:
        for line in temp_file_handle.readlines():
            print(line)
            if ('identifier' in line) and (dataset_identifier in line): 
                opened_dataset_block = True
            elif ('references' in line) and (opened_dataset_block == True): 
                opened_reference_block = True
                final_project_metadata_file_handle.write(line)
            elif opened_dataset_block and ('\"describedBy\" : \"/api/datasets' in line or \
                                           '\"describedBy\": \"/api/datasets' in line):
                final_project_metadata_file_handle.write('\n')
                final_project_metadata_file_handle.write(line)
            elif opened_dataset_block and 'describedByType' in line:
                seen_described_by_type = True
                final_project_metadata_file_handle.write(line)
                final_project_metadata_file_handle.write('\n')
            elif opened_dataset_block and seen_described_by_type:
                print(line)
                final_project_metadata_file_handle.write(line)
                if line == "      ],\n" and opened_reference_block == True: 
                    break

def reorder_json(original_project_metadata_file_path: str, temp_project_metadata_file_path: 
                 str, final_project_metadata_file_path: str, dataset_identifier: str, attribute_after_references: str) -> None:
    original_project_metadata_handle = open(original_project_metadata_file_path, 'r', encoding='utf-8')
    opened_dataset_block = False
    opened_references_block = False
    last_line_was_line_break = False
    with open(final_project_metadata_file_path, 'a+') as final_project_metadata_file_handle:
        lines = original_project_metadata_handle.readlines()
        len_file = len(lines)
        for index, line in enumerate(lines):
            if opened_dataset_block and (index != (len_file - 1)):
                if lines[index + 1] == '    }\n':
                    #final_project_metadata_file_handle.write(line[:-1] + ',\n')
                    continue

            if ('identifier' in line) and (dataset_identifier in line): 
                opened_dataset_block = True
            elif opened_dataset_block and (attribute_after_references == None) and ((line == '    },\n') or ('    }\n' == line)):
                write_new_block(final_project_metadata_file_handle, temp_project_metadata_file_path, 
                                dataset_identifier, attribute_after_references)
                break
                #final_project_metadata_file_handle.write(line)
                opened_dataset_block = False
                continue
            elif opened_dataset_block and (f'\"{attribute_after_references}\"' in line):             
                write_new_block(final_project_metadata_file_handle, temp_project_metadata_file_path, 
                                dataset_identifier, attribute_after_references)
                break
            elif opened_dataset_block and ('\"describedBy\" : \"/api/datasets' in line or
                                           '\"describedBy\": \"/api/datasets' in line):
                continue
            elif opened_dataset_block and ('describedByType' in line):
                continue
            elif opened_dataset_block and (('    },\n' == line) or ('    }\n' == line)): 
                opened_dataset_block = False
            elif opened_dataset_block and ('\"references\": [' in line):
                opened_references_block = True
            elif opened_references_block and (('      ]\n' in line) or ('      ],\n' in line)):
                opened_references_block = False
            elif opened_references_block:
                continue
            elif line == '\n' and last_line_was_line_break:
                continue
            last_line_was_line_break = False
            #final_project_metadata_file_handle.write(line) 
            if line == '\n':
                last_line_was_line_break = True
        
    original_project_metadata_handle.close()





if __name__ == "__main__":

    metadata_to_be_moved_dir = 'C:\\Users\\RUMSPD\\source\\repos\\livewire\\data\\move_to_nrel_repo\\llmd'
    pdf_to_be_moved_dir = 'C:\\Users\\RUMSPD\\source\\repos\\livewire\\data\\move_to_nrel_repo\\pdf'
    project_metadata_dir = 'C:\\Users\\RUMSPD\\source\\repos\\livewire\\data\\meta'
    files_dir = 'C:\\Users\\RUMSPD\\source\\repos\\livewire\\data\\files\\dataset'
    temp_output_dir = 'C:\\Users\\RUMSPD\\source\\repos\\livewire\\data\\temp_metadata'
    final_output_dir = 'C:\\Users\\RUMSPD\\source\\repos\\livewire\\data\\final_project_metadata'

    for file_name in os.listdir(metadata_to_be_moved_dir):
        if ('.summary.json' in file_name) or ('.pdf' in file_name):
            continue
        project_identifier, dataset_identifier = get_identifiers(file_name)
        project_metadata_name = get_project_metadata_file_name(project_metadata_dir)
        if project_identifier == 'dtg':
            continue

        original_project_metadata_file_path = os.path.join(project_metadata_dir, project_metadata_name)
        new_project_metadata_file_path = os.path.join(temp_output_dir, project_metadata_name)
        final_project_metadata_file_path = os.path.join(final_output_dir, project_metadata_name)
        with open(original_project_metadata_file_path, 'r', encoding='utf-8') as f:
            print(original_project_metadata_file_path) 
            current_metadata = json.load(f)
            if 'dataset' not in current_metadata.keys(): 
                raise IOError(f'No dataset attribute in {project_metadata_name}')
            reference_URL_pdf, reference_URL_json = create_reference_URLs(project_identifier, dataset_identifier)
            index, current_metadata, attribute_after_references = change_dataset_metadata(current_metadata, reference_URL_pdf, reference_URL_json)

        with open(new_project_metadata_file_path, 'w+') as f:
            json.dump(current_metadata, f, indent=2)

        reorder_json(original_project_metadata_file_path, new_project_metadata_file_path,
                     final_project_metadata_file_path, dataset_identifier, attribute_after_references)
        
        src_base_file_name = (project_identifier + '.' + dataset_identifier)
        dest_base_dir = os.path.join(files_dir, project_identifier, dataset_identifier)
        dest_base_path = os.path.join(dest_base_dir, src_base_file_name)
        if not os.path.exists(dest_base_dir):
            Path(dest_base_dir).mkdir(parents=True, exist_ok=True)
        shutil.copy(os.path.join(metadata_to_be_moved_dir, src_base_file_name) + '.json', dest_base_path + '.json')
        shutil.copy(os.path.join(metadata_to_be_moved_dir, src_base_file_name) + '.summary' + '.json', dest_base_path + '.summary' + '.json')
        shutil.copy(os.path.join(pdf_to_be_moved_dir, 'dictionary-' + src_base_file_name) + '.pdf', dest_base_dir + '//' + 'dictionary-' + src_base_file_name + '.pdf')