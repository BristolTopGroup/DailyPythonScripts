'''
Created on 26 Nov 2012

@author: kreczko
'''


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

def fetch_grid_file(grid_path):
    '''
    fetch a grid file by having only the path.
    1) Use DAS (https://cmsweb.cern.ch/das) to figure out where the file is located
    2) lookup LFN for file
    3) queue the file for transfer: either FTS or to local disk in a different thread
    '''


def delete_grid_folder(folder, recursive = False):
    pass

def remote_copy_folder(location, destination):
    pass