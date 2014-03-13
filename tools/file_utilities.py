'''
Created on 26 Nov 2012

@author: kreczko
'''

import os
import json
import glob
from rootpy.io import File
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

def write_data_to_JSON(data, JSON_output_file):
    path = get_path(JSON_output_file)
    make_folder_if_not_exists(path)
    output_file = open(JSON_output_file, 'w')
    output_file.write(json.dumps(data, indent=4, sort_keys = True))
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

def merge_ROOT_files(file_list, output_file, compression = 7):
    input_files = ' '.join(file_list)
    command = 'hadd -f%d %s %s' %(compression, output_file, input_files)
    subprocess.Popen(command, shell=True)

def get_process_from_file(file_in_path):
    file_name = file_in_path.split('/')[-1]
    process_name = file_name.split('_')[0]
    return process_name
