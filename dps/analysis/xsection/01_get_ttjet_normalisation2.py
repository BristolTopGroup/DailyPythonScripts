from __future__ import division
from argparse import ArgumentParser
from dps.utils.logger import log
from dps.config.xsection import XSectionConfig
from dps.utils.file_utilities import write_data_to_JSON, get_files_in_path, make_folder_if_not_exists, read_data_from_JSON
from dps.utils.hist_utilities import clean_control_region, hist_to_value_error_tuplelist, fix_overflow
from dps.utils.Calculation import combine_complex_results
from dps.utils.measurement2 import Measurement
from dps.utils.ROOT_utils import set_root_defaults

# define logger for this module
mylog = log["01b_get_ttjet_normalisation"]

class TTJetNormalisation(object):
    '''
    Determines the normalisation for top quark pair production.
    Unless stated otherwise all templates and (initial) normalisations 
    are taken from simulation, except for QCD where the template is 
    extracted from data.

    Subtracts the known backgrounds from data to obtain TTJet template
    and normalisation
    '''
    @mylog.trace()
    def __init__(self, measurement_config):
        self.config = measurement_config
        # self.variable = measurement.variable
        # self.category = measurement.name
        # self.channel = measurement.channel
        # self.phase_space = phase_space

        self.have_normalisation = False
        # normalisation for current config
        self.normalisation = {}

    # @mylog.trace()
    # def calculate_normalisation(self):
    #     '''
    #     '''
    #     # normalisation already calculated
    #     if self.have_normalisation: return


    #     histograms = self.measurement.histograms

    #     for sample, hist in histograms.items():
    #         hist = fix_overflow(hist)
    #         histograms[sample] = hist
    #         self.normalisation[sample] = self.initial_normalisation[sample]

    #     self.background_subtraction(histograms)

    #     # next, let's round all numbers (they are event numbers after all)
    #     for sample, values in self.normalisation.items():
    #         new_values = [(round(v, 1), round(e, 1)) for v, e in values]
    #         self.normalisation[sample] = new_values

    #     self.have_normalisation = True

    # @mylog.trace()
    # def background_subtraction(self, histograms):
    #     ttjet_hist = clean_control_region(
    #         histograms,
    #         subtract=['QCD', 'V+Jets', 'SingleTop']
    #     )
    #     self.normalisation['TTJet'] = hist_to_value_error_tuplelist(ttjet_hist)

    # @mylog.trace()
    # def save(self):
    #   # If normalisation hasnt been calculated  - then go calculate it!
    #     if not self.have_normalisation:
    #         self.calculate_normalisation()

    #     file_template = '{type}_{channel}.txt'
    #     output_folder = ''

    #     write_data_to_JSON(
    #         self.normalisation,
    #         output_folder + file_template.format(type='normalisation', channel=self.channel)
    #     )
    #     return 

def main():
    '''
    1 - Create config file reading in templates
    2 - Create 'jobs' for each config
    3 - Read in config
    4 - Differentiate between Syst and Central
    5 - Work in QCD from data
    '''
    results = {}

    # construct categories from files:
    input_template = 'TESTING/config/measurements/background_subtraction/{com}TeV/{ch}/{var}/{ps}/'

    # Create measuremewnt_filepath
    measurement_filepath = input_template

    if args.visiblePS:
        ps = 'VisiblePS'
    else:
        ps = 'FullPS'

    for ch in ['electron', 'muon']:
        for var in measurement_config.variables:

            # Create measurement_filepath
            measurement_filepath = input_template.format(
                com = args.CoM,
                ch = ch,
                var = var,
                ps = ps,
            )
            print measurement_filepath

            # Loop over channels
            measurement_files = get_files_in_path(measurement_filepath, file_ending='.json')

            for f in sorted(measurement_files):
                print('Processing file ' + f)
                # Read in Measurement JSON
                config = read_data_from_JSON(f)
                # print config
                # Create Measurement Class using JSON
                measurement = Measurement(config)
                measurement.calculate_normalisation()
                measurement.save()
    return

def parse_arguments():
    parser = ArgumentParser(__doc__)
    parser.add_argument("-v", "--variable", dest="variable", default='HT',
                            help="set the variable to analyse (MET, HT, ST, MT, WPT). Default is MET.")
    parser.add_argument("-c", "--centre-of-mass-energy", dest="CoM", default=13, type=int,
                            help="set the centre of mass energy for analysis. Default = 13 [TeV]")
    parser.add_argument('--visiblePS', dest="visiblePS", action="store_true",
                            help="Unfold to visible phase space")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    set_root_defaults()
    args = parse_arguments()
    measurement_config = XSectionConfig(args.CoM)
    main()



