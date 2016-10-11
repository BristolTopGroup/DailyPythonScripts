'''
    Condor job for dps.analysis.unfolding_tests.create_unfolding_pull_data
'''
from .. import Job
from dps.config.xsection import XSectionConfig

class UnfoldingPullJob(Job):

    '''
        Condor job for dps.analysis.unfolding_tests.create_unfolding_pull_data
    '''

    def __init__(self, input_file_directory, method, channels,
                 centre_of_mass, response, samples,
                 variables, n_toy_data,
                 output_folder, do_best_tau,
                 tau_values):
        '''
            Constructor
        '''
        Job.__init__(self)
        self.input_file_directory = input_file_directory
        self.method = method
        self.centre_of_mass = centre_of_mass
        self.response = response
        self.all_samples = samples
        self.n_toy_data = n_toy_data
        self.output_folder = output_folder
        self.all_channels = channels
        self.all_variables = variables
        self.do_best_tau = do_best_tau
        self.all_tau_values = tau_values
        self.cross_section_config = XSectionConfig(self.centre_of_mass)

        # self.additional_input_files = []
        # for sample in self.all_samples:
        #     additional_input_file_template = '{directory}/toy_mc_{sample}_N_{n}_{com}TeV.root'
        #     additional_input_file = additional_input_file_template.format(
        #                                                             directory = self.input_file_directory,
        #                                                             sample = sample,
        #                                                             n = self.n_toy_data,
        #                                                             com = self.centre_of_mass
        #                                                             )
        #     self.additional_input_files.append(additional_input_file)

    def run(self):
        '''
            Run the workload
        '''
        import dps.analysis.unfolding_tests.create_unfolding_pull_data as pull
        from dps.utils.ROOT_utils import set_root_defaults
        set_root_defaults(msg_ignore_level=3001)
        pulls_file_name = pull.create_unfolding_pull_data(self.input_file_name,
                                        self.method,
                                        self.channel_to_run,
                                        self.centre_of_mass,
                                        self.variable_to_run,
                                        self.sample_to_run,
                                        self.response,
                                        self.n_toy_data,
                                        self.output_folder,
                                        self.tau_value_to_run
                                        )

        # import dps.analysis.unfolding_tests.make_unfolding_pull_plots as plots
        # plots.makeAllPlots(
        #     file_name = pulls_file_name,
        #     output_directory_base = 'plots/unfolding_pulls'
        #     )

    def split(self, n):
        subjobs = []

        for variable in self.all_variables:
            for sample in self.all_samples:
                for channel in self.all_channels:
                    tau_values_to_run = []
                    tau_values_to_run.extend( self.all_tau_values )

                    if self.do_best_tau:
                        best_tau_value = self.get_best_tau_value( variable, channel )
                        tau_values_to_run.append( best_tau_value )

                    for tau_value in tau_values_to_run:
                        j = UnfoldingPullJob(input_file_directory=self.input_file_directory,
                                             method=self.method,
                                             channels=self.all_channels,
                                             centre_of_mass=self.centre_of_mass,
                                             response=self.response,
                                             samples=self.all_samples,
                                             variables=self.all_variables,
                                             n_toy_data=self.n_toy_data,
                                             output_folder=self.output_folder,
                                             do_best_tau=self.do_best_tau,
                                             tau_values=self.all_tau_values
                                            )
                        j.variable_to_run = variable
                        j.sample_to_run = sample
                        j.channel_to_run = channel
                        j.tau_value_to_run = tau_value

                        input_file_name = self.get_input_file_name( self.input_file_directory, sample, self.centre_of_mass, self.n_toy_data)
                        j.input_file_name = input_file_name
                        # j.additional_input_files = [input_file_name]

                        subjobs.append(j)
        if len(subjobs) != n :
            print ('Warning in unfolding_pull_job_new split() : Did not get the expected number of subjobs')
            print ('n :',n,'subjobs :',len(subjobs))
        return subjobs

    def tar_output(self, job_id, subjob_id):
        '''
            Creates a tar file from the output of the job
        '''
        import tarfile
        file_template = 'UnfoldingPullJob_{sample}'
        file_template += '_{com}TeV_{job_id}.{subjob_id}.tar.gz'
        output_file = file_template.format(
                                           sample = self.sample_to_run,
                                           com = self.centre_of_mass,
                                           job_id = job_id,
                                           subjob_id = subjob_id,
                                           )
        with tarfile.open(output_file, 'w:gz') as tar:
            source_dir = self.output_folder
            tar.add(source_dir, source_dir)
        return output_file

    def get_best_tau_value( self, variable, channel ):
        '''
            Returns the tau value from the cross section config file
        '''
        best_tau_value = -1
        if channel == 'combined':
            best_tau_value = self.cross_section_config.tau_values_combined[variable]
        elif channel == 'muon':
            best_tau_value = self.cross_section_config.tau_values_muon[variable]
        elif channel == 'electron':
            best_tau_value = self.cross_section_config.tau_values_electron[variable]

        return best_tau_value

    def get_input_file_name( self, input_file_directory, sample, centre_of_mass, n_toy_data):
        file_name_template = '{directory}/toy_mc_{sample}_N_{n}_{com}TeV.root'
        file_name = file_name_template.format(
                                                directory = input_file_directory,
                                                sample = sample,
                                                n = n_toy_data,
                                                com = centre_of_mass
                                            )
        return file_name
