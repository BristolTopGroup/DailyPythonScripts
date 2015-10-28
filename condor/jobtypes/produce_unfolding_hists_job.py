from condor import Job


class ProduceUnfoldingHistsJob(Job):
    '''
        Condor job class for src.produce_unfold_hists.py
    '''

    def __init__(self, params):
        Job.__init__(self)

    def run(self):
        pass

    def split(self, n):
        if n == 1:
            return self

    def tar_output(self, job_id, subjob_id):
        pass
