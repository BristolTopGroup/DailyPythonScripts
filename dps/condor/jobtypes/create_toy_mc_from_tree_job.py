'''
    Condor jobs description for src/unfolding_tests/create_toy_mc_from_tree
'''
from .. import Job
from dps.config.xsection import XSectionConfig


class CreateToyMCFromTreeJob(Job):

    def __init__(self, output_folder, n_toy, n_input_mc,
                 centre_of_mass, start_at=0, split=1):
        Job.__init__(self)
        self.output_folder = output_folder
        self.n_toy = n_toy
        self.centre_of_mass = centre_of_mass
        self.start_at = start_at
        self.n_input_mc = n_input_mc
        self.config = XSectionConfig(centre_of_mass)
        self.part_of_split = split
        

    def run(self):
        import dps.analysis.unfolding_tests.create_toy_mc_from_tree as toy
        toy.generate_toy(
            n_toy=self.n_toy,
            n_input_mc=self.n_input_mc,
            config=self.config,
            output_folder=self.output_folder,
            start_at=self.start_at,
            split = self.part_of_split)

    def split(self, n):
        if n == 1:
            return [self]
        # otherwise create subjobs
        subjobs = []
        for start_i, n_input_mc_i in self.get_mapping(n):
            j = CreateToyMCFromTreeJob(
                self.output_folder,
                self.n_toy,
                n_input_mc_i,
                self.centre_of_mass,
                start_at=start_i, 
                split = n)
            subjobs.append(j)
        return subjobs

    def get_mapping(self, n):
        '''
            splits the current n_input_mc into n packages
        '''
        # construct a yield of
        new_n = int(self.n_input_mc / n)
        l = range(self.n_input_mc)
        for i in xrange(0, self.n_input_mc, new_n):
            yield i, len(l[i:i + new_n])

    def tar_output(self, job_id, subjob_id):
        import dps.analysis.unfolding_tests.create_toy_mc_from_tree as toy
        import shutil
        output_file = toy.get_output_file_name(self.output_folder,
                                               self.n_toy,
                                               self.start_at,
                                               self.n_input_mc,
                                               self.centre_of_mass)
        suffix = '_{0}.{1}.root'.format(job_id, subjob_id)
        new_file = output_file.replace('.root', suffix)
        shutil.move(output_file, new_file)

        return new_file

if __name__ == '__main__':
    j = CreateToyMCFromTreeJob(
        'data/toy_mc/',
        10,
        1000,
        13,
    )
    j.filter_jobs = [0,3]
    jobs = j.split(4)
    for i,job in enumerate(jobs):
        job.run()
        print 'Output file:', job.tar_output(i)
