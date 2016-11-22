'''
    Takes AnalysisSoftware (https://github.com/BristolTopGroup/AnalysisSoftware)
    output files and extracts the TTJet normalisation for each measured variable
    by subtracting backgrounds from data.

    Usage:
        python dps/analysis/xsection/01_get_ttjet_normalisation.py \
        -c <centre of mass energy> -v <variable> -i <path to input folder> \
        -p <output path>

    Example:
        python dps/analysis/xsection/01_get_ttjet_normalisation.py \
        -c 13 -v MET -i config/measurements/background_subtraction/

    TODO: In the end this and 01_get_fit_results.py should be merged.
    All should come down to the function to extract the # events from TTJet
'''
from __future__ import division
from optparse import OptionParser
from dps.utils.logger import log
from dps.config.xsection import XSectionConfig
from dps.analysis.xsection.lib import closure_tests
from dps.utils.file_utilities import write_data_to_JSON, get_files_in_path
from dps.utils.hist_utilities import clean_control_region, \
    hist_to_value_error_tuplelist, fix_overflow

import os
from copy import deepcopy
from dps.utils.Calculation import combine_complex_results
from dps.utils.measurement import Measurement
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
    def __init__(self,
                 config,
                 measurement,
                 phase_space='FullPS'):
        self.config = config
        self.variable = measurement.variable
        self.category = measurement.name
        self.channel = measurement.channel
        self.phase_space = phase_space
        self.measurement = measurement
        self.measurement.read()

        self.normalisation = {}
        self.initial_normalisation = {}
        # self.unity_normalisation = {}
        self.auxiliary_info = {}

        self.have_normalisation = False

        # for sample, hist in self.measurement.histograms.items():
        #     h = deepcopy(hist)
        #     h_norm = h.integral()
        #     if h_norm > 0:
        #         h.Scale(1 / h.integral())
        #     self.unity_normalisation[sample] = hist_to_value_error_tuplelist(h)

        self.auxiliary_info['norms'] = measurement.aux_info_norms

    @mylog.trace()
    def calculate_normalisation(self):
        '''
            1. get file names
            2. get histograms from files
            3. ???
            4. calculate normalisation
        '''
        if self.have_normalisation:
            return
        histograms = self.measurement.histograms

        for sample, hist in histograms.items():
            # TODO: this should be a list of bin-contents
            hist = fix_overflow(hist)
            histograms[sample] = hist
            self.initial_normalisation[sample] = hist_to_value_error_tuplelist(hist)
            self.normalisation[sample] = self.initial_normalisation[sample]

        self.background_subtraction(histograms)

        # next, let's round all numbers (they are event numbers after all
        for sample, values in self.normalisation.items():
            new_values = [(round(v, 1), round(e, 1)) for v, e in values]
            self.normalisation[sample] = new_values

        self.have_normalisation = True

    @mylog.trace()
    def background_subtraction(self, histograms):
        ttjet_hist = clean_control_region(
            histograms,
            subtract=['QCD', 'V+Jets', 'SingleTop']
        )
        self.normalisation['TTJet'] = hist_to_value_error_tuplelist(ttjet_hist)

    @mylog.trace()
    def save(self, output_path):
        if not self.have_normalisation:
            self.calculate_normalisation()

        file_template = '{type}_{channel}.txt'
        folder_template = '{path}/normalisation/{method}/{CoM}TeV/{variable}/{phase_space}/{category}/'
        output_folder = folder_template.format(
            path = output_path,
            CoM = self.config.centre_of_mass_energy,
            variable = self.variable,
            category = self.category,
            method = 'background_subtraction',
            phase_space = self.phase_space,
        )

        write_data_to_JSON(
            self.normalisation,
            output_folder + file_template.format(type='normalisation', channel=self.channel)
        )
        write_data_to_JSON(
            self.initial_normalisation, 
            output_folder + file_template.format(type='initial_normalisation', channel=self.channel)
        )
        # write_data_to_JSON(
        #     self.unity_normalisation,
        #     output_folder + file_template.format(type='unity_normalisation', channel=self.channel)
        # )
        write_data_to_JSON(
            self.auxiliary_info,
            output_folder + file_template.format(type='auxiliary_info', channel=self.channel)
        )
        return output_folder

    @mylog.trace()
    def combine(self, other):
        if not self.have_normalisation or not other.have_normalisation:
            mylog.warn(
                'One of the TTJetNormalisations does not have a normalisation, aborting.')
            return

        self.normalisation = combine_complex_results(
            self.normalisation, other.normalisation)
        self.initial_normalisation = combine_complex_results(
            self.initial_normalisation, other.initial_normalisation)
        # self.unity_normalisation = combine_complex_results(
        #     self.unity_normalisation, other.unity_normalisation)
        self.channel = 'combined'


def parse_options():
    parser = OptionParser(__doc__)
    parser.add_option("-p", "--path", dest="path", default='data',
                      help="set output path for JSON files. Default is 'data'.")
    parser.add_option("-i", "--input", dest="input",
                      default='config/measurements/background_subtraction/',
                      help="set output path for JSON files")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                      help="set the variable to analyse (MET, HT, ST, MT, WPT). Default is MET.")
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=13, type=int,
                      help="set the centre of mass energy for analysis. Default = 13 [TeV]")
    parser.add_option('-d', '--debug', dest="debug", action="store_true",
                      help="Print the debug information")
    parser.add_option('--closure_test', dest="closure_test", action="store_true",
                      help="Perform fit on data == sum(MC) * scale factor (MC process)")
    parser.add_option('--closure_test_type', dest="closure_test_type", default='simple',
                      help="Type of closure test (relative normalisation):" + '|'.join(closure_tests.keys()))
    parser.add_option('--test', dest="test", action="store_true",
                      help="Just run the central measurement")
    parser.add_option('--visiblePS', dest="visiblePS", action="store_true",
                      help="Unfold to visible phase space")

    (options, args) = parser.parse_args()
    # fix some of the inputs
    if not options.path.endswith('/'):
        options.path = options.path + '/'
    if not options.input.endswith('/'):
        options.input = options.input + '/'

    return options, args

@mylog.trace()
def main():
    # construct categories from files:
    input_template = options.input + '{energy}TeV/{channel}/{variable}/{phase_space}/'

    phase_space = 'FullPS'
    if options.visiblePS:
        phase_space = 'VisiblePS'
    results = {}

    for channel in ['electron', 'muon']:
        measurement_filepath = input_template.format(
            energy = options.CoM,
            channel = channel,
            variable = variable,
            phase_space = phase_space,
        )
        measurement_files = get_files_in_path(measurement_filepath, file_ending='.json')

        for f in sorted(measurement_files):
            print('Processing file ' + f)
            measurement = Measurement.fromJSON(f)
            # for each measurement
            norm = TTJetNormalisation(
                config=measurement_config,
                measurement=measurement,
                phase_space=phase_space,
            )
            norm.calculate_normalisation()
            mylog.info('Saving results to {0}'.format(output_path))
            norm.save(output_path)
            # store results for later combination
            r_name = f.replace(channel, '')
            if not results.has_key(r_name):
                results[r_name] = [norm]
            else:
                results[r_name].append(norm)

    for f, r_list in results.items():
        if not len(r_list) == 2:
            msg = 'Only found results ({0}) for one channel, not combining.'
            mylog.warn(msg.format(f))
            continue
        n1, n2 = r_list
        n1.combine(n2)
        n1.save(output_path)

if __name__ == '__main__':
    set_root_defaults()

    options, args = parse_options()

    # set global variables
    debug = options.debug
    if debug:
        log.setLevel(log.DEBUG)

    measurement_config = XSectionConfig(options.CoM)
    # caching of variables for shorter access
    variable = options.variable
    output_path = options.path
    if options.closure_test:
        output_path += '/closure_test/'
        output_path += options.closure_test_type + '/'

    main()
