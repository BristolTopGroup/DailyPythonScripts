'''
    Condor job for dps.analysis.unfolding_tests.create_unfolding_pull_data
'''
from .. import Job

class UnfoldingPullJob(Job):

    '''
        Condor job for dps.analysis.unfolding_tests.create_unfolding_pull_data
    '''

    def __init__(self, input_file_name, method, channel,
                 centre_of_mass, variable, n_toy_mc, n_toy_data,
                 output_folder, offset_toy_mc, offset_toy_data,
                 k_value, tau_value=-1, run_matrix=None):
        '''
            Constructor
        '''
        Job.__init__(self)
        self.input_file_name = input_file_name
        self.method = method
        self.channel = channel
        self.centre_of_mass = centre_of_mass
        self.variable = variable
        self.n_toy_mc = n_toy_mc
        self.n_toy_data = n_toy_data
        self.output_folder = output_folder
        self.offset_toy_mc = offset_toy_mc
        self.offset_toy_data = offset_toy_data
        self.k_value = k_value
        self.tau_value = tau_value
        self.run_matrix = run_matrix
        
        self.additional_input_files = [input_file_name]

    def run(self):
        '''
            Run the workload
        '''
        import dps.analysis.unfolding_tests.create_unfolding_pull_data as pull
        pull.create_unfolding_pull_data(self.input_file_name, self.method,
                                        self.channel, self.centre_of_mass,
                                        self.variable, self.n_toy_mc,
                                        self.n_toy_data,
                                        self.output_folder, self.offset_toy_mc,
                                        self.offset_toy_data, self.k_value,
                                        self.tau_value, self.run_matrix)

    def split(self, n):
        '''
            In this case the split function has to establish the size of the
            matrix and create jobs with sub-matrices.

            Case 1:
                - use_n_toy = 10
                - offset_toy_mc = 0
                - offset_toy_data = 0
                - n = 5

            Case 2:
                - use_n_toy = 10
                - offset_toy_mc = 5
                - offset_toy_data = 5
                - n = 5

            For case 1 we can either construct five 4 x 5, 5 x 4 or 2 x 10 
            matrices. For case 2 we can construct five 1 x 5 or 5 x 1 matrices.
            In either case it would make sense to have the smallest unit either
            a column or a row.

            In order not to double-count, use_n_toy needs to be reduced per job.

        '''
        import dps.analysis.unfolding_tests.create_unfolding_pull_data as pull
        if n == 1:
            return self
        run_matrix = pull.create_run_matrix(self.n_toy_mc,
                                                     self.n_toy_data,
                                                     self.offset_toy_mc,
                                                     self.offset_toy_data)
        self.run_matrix = list(run_matrix)
        # after this the run matrix is empty (generator)!
        l = list(self.run_matrix) 
        n_per_job = int(len(l) / n)

        run_matrices = []
        for _ in range(n):
            run_matrix = []
            for _ in range(n_per_job):
                if l:
                    run_matrix.append(l.pop())
            run_matrices.append(run_matrix)
        if l:  # if anything is left
            for i in l:
                run_matrices[-1].append(i)

        jobs = []
        for r in run_matrices:
            offsets_and_ranges = UnfoldingPullJob.get_offsets_and_ranges(r)
            offset_toy_mc, offset_toy_data = offsets_and_ranges[:2]
            n_toy_mc, n_toy_data = offsets_and_ranges[2:]
            j = UnfoldingPullJob(self.input_file_name, self.method,
                                 self.channel, self.centre_of_mass,
                                 self.variable, n_toy_mc,
                                 n_toy_data,
                                 self.output_folder, offset_toy_mc,
                                 offset_toy_data, self.k_value,
                                 self.tau_value, r)
            jobs.append(j)

        return jobs

    @staticmethod
    def get_offsets_and_ranges(run_matrix):
        '''
            Extracts offsets and ranges for data & mc from the run_matrix
        '''
        mc, data = zip(*run_matrix)
        min_toy_mc = min(mc)
        min_toy_data = min(data)
        max_toy_mc = max(mc)
        max_toy_data = max(data)

        offset_toy_mc = min_toy_mc - 1
        offset_toy_data = min_toy_data - 1
        n_toy_mc = max_toy_mc - min_toy_mc + 1
        n_toy_data = max_toy_data - min_toy_data + 1

        return offset_toy_mc, offset_toy_data, n_toy_mc, n_toy_data
    
    def tar_output(self, job_id, subjob_id):
        '''
            Creates a tar file from the output of the job
        '''
        import tarfile
        import os
        file_template = 'UnfoldingPullJob_{method}_{variable}_{channel}'
        file_template += '_{com}TeV_{job_id}.{subjob_id}.tar.gz'
        output_file = file_template.format(
                                           variable = self.variable,
                                           channel = self.channel,
                                           com = self.centre_of_mass,
                                           job_id = job_id,
                                           subjob_id = subjob_id,
                                           method = self.method,
                                           )
        with tarfile.open(output_file, 'w:gz') as tar:
            source_dir = self.output_folder
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        return output_file

if __name__ == '__main__':
    # a test example
    import pickle
    j = UnfoldingPullJob('data/toy_mc/toy_mc_N_300_from_0_to_1000_13TeV.root',
                         'RooUnfoldSvd',
                         'electron',
                         13,
                         'MET',
                         300,
                         300,
                         'data/pull_data/',
                         0,
                         0,
                         3,
                         50.0,
                         )
    jobs = j.split(1000)
    jobs_test = j.split(1000)
    for j1, j2 in zip(jobs, jobs_test):
        assert(j1.run_matrix == j2.run_matrix)
    
    for i, job in enumerate(jobs):
        if i == 863:
            f = open('job_{0}.pkl'.format(i), 'w+')
            pickle.dump(job, f)
            job.run()
