'''

'''
import pickle
from tools.file_utilities import make_folder_if_not_exists
import time
import subprocess


class Condor(object):

    '''
        Class to control condor work flows
    '''

    def __init__(self, n_jobs_to_run=1, n_jobs_to_split = -1, request_memory=200):
        '''
            @n_jobs_to_run: Number of subjobs to submit per job
            @request_memory: the amount of memory the job will use (in MB)
        '''
        self.n_jobs_to_run = n_jobs_to_run
        if n_jobs_to_split == -1:
            self.n_jobs_to_split = n_jobs_to_run
        else:
            self.n_jobs_to_split = n_jobs_to_split
        self.request_memory = request_memory

        self.constructed_jobs = False
        self.unprepared_jobs = []
        self.prepared_jobs = []

    def submit(self):
        '''
            Submits all registered jobs to the local HTCondor scheduler using
            a job template (DailyPythonScripts/condor/job_template) description
            file and the 'condor_submit' command
        '''
        today = time.strftime("%d-%m-%Y")
        job_folder = 'jobs/{0}/'.format(today)
        make_folder_if_not_exists(job_folder)
        make_folder_if_not_exists(job_folder + 'logs')
        # construct jobs
        self._construct_jobs()
        # convert each job into a pickle file
        # construct a class ad for each job
        with open('condor/job_template', 'r') as template:
            job_template = template.read()
        condor_jobs = []

        for i, job in enumerate(self.prepared_jobs):
            job_file = job_folder + 'job_{0}.pkl'.format(i)
            job_desc_file = job_folder + 'job_{0}.dsc'.format(i)
            job_description = job_template.replace('%pkl_file%', job_file)
            job_description = job_description.replace('%total_memory%',
                                                      str(self.request_memory))
            job_description = job_description.replace('%n_jobs_to_run%',
                                                      str(self.n_jobs_to_run))
            job_description = job_description.replace('%n_jobs_to_split%',
                                                      str(self.n_jobs_to_split))
            input_files = ['dps.tar']
            if hasattr(job, 'additional_input_files'):
                input_files.extend(job.additional_input_files)
            input_files_str = ','.join(input_files)
            job_description = job_description.replace('%input_files%',
                                                      input_files_str)
            job_description = job_description.replace('%today%', today)

            with open(job_file, 'w+') as jf:
                pickle.dump(job, jf)
            with open(job_desc_file, 'w+') as jdf:
                jdf.write(job_description)

            condor_jobs.append(job_desc_file)
        # prepare DPS for submission
        subprocess.Popen(['./condor/prepare_dps.sh'])
        # submit jobs
        for j in condor_jobs:
            p = subprocess.Popen(['condor_submit', j])
            p.communicate()  # wait until command completed

    def submit_with_htcondor(self, job):
        '''
            === In development ===
            Submits all registered jobs to the local HTCondor scheduler using
            the HTCondor python bindings
        '''
        import htcondor
        import classad
        # following
        # http://osgtech.blogspot.co.uk/2014/03/submitting-jobs-to-htcondor-using-python.html
        schedd = htcondor.Schedd()
        job_ad = classad.ClassAd()
        job_ad['executable'] = 'condor/run_job'
        # TODO
        schedd.submit(job_ad)

    def add_job(self, job):
        '''
            Register a job for submission. Must be of type or derive from 
            condor.job.Job.
        '''
        self.unprepared_jobs.append(job)

    def _construct_jobs(self):
        '''
            Allows to prepare jobs in a predefined manner.
            Currently not in use.
        '''
        if self.constructed_jobs:
            return

        for job in self.unprepared_jobs:
            # do any preparation you wish
            self.prepared_jobs.append(job)
        self.constructed_jobs = True


class Job(object):

    '''
        Base class for Condor jobs. The job will be pickled and submited
        to a worker node.
    '''

    def __init__(self):
        self.additional_input_files = []
        self.filter_jobs = []

    def run(self):
        '''
            Execute some code. 
        '''
        pass

    def split(self, n):
        '''
            Implements the splitting procedure for a Job into N jobs.
            For examples see DailyPythonScripts/condor/jobtypes/*.py
        '''
        if n == 1:
            return self

    def tar_output(self, job_id, subjob_id):
        '''
            Collects all output (if needed) into a single tar file.
        '''
        pass


def parse_filter_jobs(filter_jobs):
    result = []
    if not filter_jobs:
        return result
    jobs = filter_jobs.split(',')
    result = [int(j) for j in jobs]
    return result
