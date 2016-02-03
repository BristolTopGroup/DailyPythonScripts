'''
Created on 26 Nov 2012

@author: kreczko
'''

import os
import json
import glob
from rootpy.io import File
from rootpy.io import root_open
import subprocess

def make_folder_if_not_exists(folder):
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except:
            print "Could not create a folder ", folder
        
def write_string_to_file(string, filename):
    path = get_path(filename)
    make_folder_if_not_exists(path)
    #write file
    output_file = open(filename, 'w')
    output_file.write(string)
    output_file.close()
    
def get_path(filename_with_path):
    absolute_path = os.path.abspath(filename_with_path)
    filename = absolute_path.split('/')[-1]
    path = absolute_path.replace(filename, '')
    return path

def write_data_to_JSON(data, JSON_output_file, indent = True):
    path = get_path(JSON_output_file)
    make_folder_if_not_exists(path)
    output_file = open(JSON_output_file, 'w')
    if indent:
        output_file.write(json.dumps(data, indent=4, sort_keys = True))
    else:
        output_file.write(json.dumps(data, sort_keys = True))
    output_file.close()

def read_data_from_JSON(JSON_input_file):
    input_file = open(JSON_input_file, 'r')
    input_JSON = ''.join(input_file.readlines())
    data = json.loads(input_JSON)
    input_file.close()
    return data

def get_files_in_path(path, file_ending = '.root'):
    path += '/*' + file_ending
    files = glob.glob(path)
    return files

def check_ROOT_file(filename):
    passesCheck = can_open_ROOT_file(filename)
    return passesCheck

def can_open_ROOT_file(filename):
    passesCheck = False
    try:
        openFile = File(filename, 'r')
        if openFile:
            passesCheck = True
            openFile.Close()
    except:
        print "Could not open ROOT file"
    
    return passesCheck

def extract_job_number_from_CRAB_output(output_file, position_from_end = 3):
    job_number = output_file.split('_')[-position_from_end]
    number = -1
    try:
        number = int(job_number)
    except:
        print "Could not find the job number for"
        print file
        print 'At the given position from the end:', position_from_end
    return number

def find_duplicate_CRAB_output_files(job_files):
    duplicates = []
    seen = []
    for job_file in job_files:
        job = extract_job_number_from_CRAB_output(job_file)
        if job in seen:
            duplicates.append(job_files)
        else:
            seen.append(job)
    return duplicates

def merge_ROOT_files(file_list, output_file, compression = 7, waitToFinish=False ):
    input_files = ' '.join(file_list)
    output_log_file = output_file.replace(".root", ".log")

    if waitToFinish:
        command = 'nice -n 19 hadd -f%d %s %s >& %s' %(compression, output_file, input_files, output_log_file)
    else:
        command = 'nice -n 19 hadd -f%d %s %s >& %s &' %(compression, output_file, input_files, output_log_file)

    p = subprocess.Popen(command, shell=True)

    if waitToFinish:
        print 'Waiting to finish merging...'
        p.wait()




def get_process_from_file(file_in_path):
    file_name = file_in_path.split('/')[-1]
    process_name = file_name.split('_')[0]
    return process_name

def saveHistogramsToROOTFile( data, mcStack, fileName ):
    with root_open(fileName, 'recreate') as outputFile:
        data.Write('Data')
        mcStack.Write('MC')


def read_xsection_measurement_results_with_errors(path_to_JSON, variable, met_type, phase_space, method, channel):
    category = 'central'

    file_template = '{path}/{category}/{name}_{channel}_{method}{suffix}.txt'
    file_template = file_template.format(
                path = path_to_JSON,
                category = category,
                name = 'normalised_xsection',
                channel = channel,
                method = method,
                suffix = '',
                )

    # file_template = path_to_JSON +  '/xsection_measurement_results/' + channel + '/' + category + '/normalised_xsection_' + met_type + '.txt' 

    file_name = file_template

    normalised_xsection_unfolded = read_data_from_JSON( file_name )
    
    normalised_xsection_measured_unfolded = {'measured':normalised_xsection_unfolded['TTJet_measured'],
                                            'unfolded':normalised_xsection_unfolded['TTJet_unfolded']}

    file_name = file_template.replace('.txt', '_with_errors.txt')
    normalised_xsection_unfolded_with_errors = read_data_from_JSON( file_name )
    file_name = file_template.replace('.txt', '_ttbar_generator_errors.txt')
    normalised_xsection_ttbar_generator_errors = read_data_from_JSON( file_name )

#     file_name = file_template.replace('.txt', '_MET_errors.txt')
#     normalised_xsection_MET_errors = read_data_from_JSON( file_name )

#     file_name = file_template.replace('.txt', '_topMass_errors.txt')
#     normalised_xsection_topMass_errors = read_data_from_JSON( file_name )

#     file_name = file_template.replace('.txt', '_kValue_errors.txt')
#     normalised_xsection_kValue_errors = read_data_from_JSON( file_name )

    file_name = file_template.replace('.txt', '_PDF_errors.txt')
    normalised_xsection_PDF_errors = read_data_from_JSON( file_name )

    file_name = file_template.replace('.txt', '_experimental_errors.txt')
    normalised_xsection_experimental_errors = read_data_from_JSON( file_name )

    file_name = file_template.replace('.txt', '_other_errors.txt')
    normalised_xsection_other_errors = read_data_from_JSON( file_name )

    file_name = file_template.replace('.txt', '_hadronisation_errors.txt')
    normalised_xsection_hadronisation_errors = read_data_from_JSON( file_name )

    file_name = file_template.replace('.txt', '_with_systematics_only_errors.txt')
    normalised_xsection_systematics_only = read_data_from_JSON( file_name )
#     file_name = file_template.replace('.txt', '_new_errors.txt')
#     normalised_xsection_new_errors = read_data_from_JSON( file_name )
    normalised_xsection_measured_unfolded.update({'measured_with_systematics':normalised_xsection_unfolded_with_errors['TTJet_measured'],
                                                'unfolded_with_systematics':normalised_xsection_unfolded_with_errors['TTJet_unfolded'],
                                                'measured_with_systematics_only':normalised_xsection_systematics_only['TTJet_measured'],
                                                'unfolded_with_systematics_only':normalised_xsection_systematics_only['TTJet_unfolded'],
                                                })
    normalised_xsection_measured_errors = normalised_xsection_other_errors['TTJet_measured']

    normalised_xsection_measured_errors.update(normalised_xsection_ttbar_generator_errors['TTJet_measured'])
    normalised_xsection_measured_errors.update(normalised_xsection_PDF_errors['TTJet_measured'])
    normalised_xsection_measured_errors.update(normalised_xsection_hadronisation_errors['TTJet_measured'])
#     normalised_xsection_measured_errors.update(normalised_xsection_MET_errors['TTJet_measured'])
#     normalised_xsection_measured_errors.update(normalised_xsection_topMass_errors['TTJet_measured'])
    ### normalised_xsection_measured_errors.update(normalised_xsection_kValue_errors['TTJet_measured'])
    normalised_xsection_measured_errors.update(normalised_xsection_experimental_errors['TTJet_measured'])
#     normalised_xsection_measured_errors.update(normalised_xsection_new_errors['TTJet_measured'])

    normalised_xsection_unfolded_errors = normalised_xsection_other_errors['TTJet_unfolded']
    normalised_xsection_unfolded_errors.update(normalised_xsection_ttbar_generator_errors['TTJet_unfolded'])
    normalised_xsection_unfolded_errors.update(normalised_xsection_PDF_errors['TTJet_unfolded'])
    normalised_xsection_unfolded_errors.update(normalised_xsection_hadronisation_errors['TTJet_unfolded'])
#     normalised_xsection_unfolded_errors.update(normalised_xsection_MET_errors['TTJet_unfolded'])
#     normalised_xsection_unfolded_errors.update(normalised_xsection_topMass_errors['TTJet_unfolded'])
    ### normalised_xsection_unfolded_errors.update(normalised_xsection_kValue_errors['TTJet_unfolded'])
    normalised_xsection_unfolded_errors.update(normalised_xsection_experimental_errors['TTJet_unfolded'])
#     normalised_xsection_unfolded_errors.update(normalised_xsection_new_errors['TTJet_unfolded'])

    return normalised_xsection_measured_unfolded, normalised_xsection_measured_errors, normalised_xsection_unfolded_errors