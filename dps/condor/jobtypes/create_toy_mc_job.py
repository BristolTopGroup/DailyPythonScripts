'''
    Condor jobs description for src/unfolding_tests/create_toy_mc
'''
from .. import Job


class CreateToyMCJob(Job):

    def __init__(self, input_file, output_folder, variable, n_toy,
                 centre_of_mass, ttbar_xsection, met_type, start_at=1):
        Job.__init__(self)
        self.input_file = input_file
        self.output_folder = output_folder
        self.n_toy = n_toy
        self.variable = variable
        self.centre_of_mass = centre_of_mass
        self.ttbar_xsection = ttbar_xsection
        self.met_type = met_type
        self.start_at = start_at
        
        self.additional_input_files = [input_file]

    def run(self):
        import dps.analysis.unfolding_tests.create_toy_mc as toy
        toy.create_toy_mc(input_file=self.input_file,
                          output_folder=self.output_folder,
                          variable=self.variable,
                          n_toy=self.n_toy,
                          centre_of_mass=self.centre_of_mass,
                          ttbar_xsection=self.ttbar_xsection,
                          met_type=self.met_type,
                          start_at=self.start_at)

    def split(self, n):
        if n == 1:
            return [self]
        # otherwise create subjobs
        subjobs = []
        for start_i, n_toy_i in self.get_mapping(n):
            j = CreateToyMCJob(self.input_file,
                               self.output_folder,
                               self.variable,
                               n_toy_i,
                               self.centre_of_mass,
                               self.ttbar_xsection,
                               self.met_type,
                               start_i)
            subjobs.append(j)
        return subjobs

    def get_mapping(self, n):
        '''
            splits the current n_toy into n packages
        '''
        # construct a yield of
        new_n = int(self.n_toy / n)
        l = range(self.n_toy)
        for i in xrange(0, self.n_toy, new_n):
            yield i + 1, len(l[i:i + new_n])

    def tar_output(self, job_id, subjob_id):
        import dps.analysis.unfolding_tests.create_toy_mc as toy
        import shutil
        output_file = toy.get_output_file_name(self.output_folder,
                                               self.start_at,
                                               self.n_toy,
                                               self.centre_of_mass)
        suffix = '_{0}.{1}.root'.format(job_id, subjob_id)
        new_file = output_file.replace('.root', suffix)
        shutil.move(output_file, new_file)

        return new_file

if __name__ == '__main__':
    j = CreateToyMCJob('/hdfs/TopQuarkGroup/run2/unfolding/13TeV/50ns/unfolding_TTJets_13TeV_asymmetric.root',
                       'data/unfolding_experimental',
                       'HT',
                       13,
                       13,
                       831.76,
                       'patType1CorrectedPFMet'
                       )
    jobs = j.split(6)
    for job in jobs:
        job.run()
