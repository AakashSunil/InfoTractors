
import os
import errno
import json

# Template Import
from Part_Template_LOC import getPart
from Acquire_Template import getAquire
from Part_Template_ORG import getPartOrg
from Born_Template import getBorn

def task_2_template_extraction(sentences,dependency_parse_tree_list,ners_list,file_name):

    base = os.path.basename(file_name)

    print('\nStarting Task 2 - Extract Information Templates using Heuristic, or Statistical or Both Methods\n')
    print('Three Templates: \n1. Part(Location, Location) or Part(Organization, Organization)\n2. Acquire(Organization, Organization, Date)\n3. Born(Person/Organization, Date, Location)\n')

    output_part_template_org = getPartOrg(sentences,ners_list,dependency_parse_tree_list)
    output_part_template = getPart(sentences,ners_list)
    output_acquire_template = getAquire(sentences,ners_list,dependency_parse_tree_list)
    output_born_template = getBorn(sentences,ners_list,dependency_parse_tree_list)

    final_output_dictionary={}
    final_output_dictionary["document"]=base
    final_output_dictionary["extraction"]=[]

    for acquire_templates in output_acquire_template:
        final_output_dictionary['extraction'].append(acquire_templates)
                
    for born_templates in output_born_template:
        final_output_dictionary['extraction'].append(born_templates)

    for part_templates in output_part_template:
        final_output_dictionary['extraction'].append(part_templates)

    for part_templates_org in output_part_template_org:
        final_output_dictionary['extraction'].append(part_templates_org)


    # Create the Features Folder with TextFile Folder
    try:
        os.makedirs('Output_JSONs/')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
            
    output_file_name = os.path.splitext(base)[0]
    
    json_output_file_name = "Output_" + output_file_name + ".json"
    json_object_output = json.loads(json.dumps(final_output_dictionary))
    final_json_data = json.dumps(json_object_output, indent=2)

    output_file = open('Output_JSONs/'+json_output_file_name, "w")
    output_file.write(final_json_data)
    output_file.close()

    print('Output JSON for "' + base + '" created in the Output_JSONs Folder - File Name: ' + json_output_file_name)
    print("\n-----------------------------------------------------------------------------------------------------------")