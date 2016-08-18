'''
    Takes AnalysisSoftware (https://github.com/BristolTopGroup/AnalysisSoftware) 
    output files and extracts the TTJet normalisation for each measured variable
    by subtracting backgrounds from data.
    
    Usage:
        python src/cross_section_measurement/01_get_ttjet_normalisation.py \
        -c <centre of mass energy> -v <variable> -i <path to input folder> \
        -p <output path>
    
    Example:
        python src/cross_section_measurement/01_get_ttjet_normalisation.py \
        -c 8 -v MET -i config/measurements/background_subtraction/
        
    TODO: In the end this and 01_get_fit_results.py should be merged.
    All should come down to the function to extract the # events from TTJet
'''
from __future__ import division
from optparse import OptionParser
# from tools.ROOT_utils import set_root_defaults, get_histogram_from_file
import tools.ROOT_utils
from tools.logger import log
from config import XSectionConfig
from src.cross_section_measurement.lib import closure_tests
from tools.file_utilities import write_data_to_JSON
from tools.hist_utilities import clean_control_region, rebin_asymmetric, \
    hist_to_value_error_tuplelist, fix_overflow
from config.variable_binning import bin_edges as variable_bin_edges

import glob
import tools.measurement

# define logger for this module
mylog = log["01b_get_ttjet_normalisation"]


class TTJetNormalisation:

    '''
        Determines the normalisation for top quark pair production based on
        different methods. Unless stated otherwise all templates and 
        (initial) normalisations are taken from simulation, except for QCD 
        where the template is extracted from data.

        Supported methods:
        BACKGROUND_SUBTRACTION: 
            Subtracts the known backgrounds from data to obtain TTJet template 
            and normalisation
        SIMULTANEOUS_FIT:
            Uses Minuit and several fit variables (quotation needed) to perform
            a simultaneous fit (does not use statistical errors of templates).
        FRACTION_FITTER:
            Uses the TFractionFitter class to fit the TTJet normalisation
    '''

    BACKGROUND_SUBTRACTION = 10
    SIMULTANEOUS_FIT = 20
    FRACTION_FITTER = 30

    @mylog.trace()
    def __init__(self,
                 config,
                 measurement,
                 method=BACKGROUND_SUBTRACTION):
        self.config = config
        self.variable = measurement.variable
        self.category = measurement.name
        self.channel = measurement.channel
        self.method = method
        self.measurement = measurement
        self.measurement.read_samples()
        self.measurement.read_shapes()

        self.met_type = measurement.met_type
        self.fit_variables = ''

        self.normalisation = {}
        self.initial_normalisation = {}
        self.templates = {}

        self.have_normalisation = False

#         self.template_category = self.category
#         if self.category in measurement_config.rate_changing_systematics_names:
#             self.template_category = 'central'

    @mylog.trace()
    def calculate_normalisation(self):
        '''
            1. get file names
            2. get histograms from files
            3. scale histograms
            4. calculate normalisation based on self.method
        '''
        if self.have_normalisation:
            return
#         input_files = self.get_input_files()
        if self.measurement.__class__ == tools.measurement.Systematic:
            self.measurement.scale_histograms()
        histograms = self.measurement.histograms

        for sample, hist in histograms.items():
            bin_edges = variable_bin_edges[self.variable]
            histograms[sample] = rebin_asymmetric(hist, bin_edges)

        for sample, hist in histograms.items():
            # TODO: this should be a list of bin-contents
            # self.initial_normalisation[
            #     sample] = hist_to_value_error_tuplelist(fix_overflow(hist))
            self.initial_normalisation[
                sample] = hist_to_value_error_tuplelist(hist)
            nBins = hist.GetNbinsX()

            if self.method == self.BACKGROUND_SUBTRACTION and sample != 'TTJet':
                self.normalisation[sample] = self.initial_normalisation[sample]

        if self.method == self.BACKGROUND_SUBTRACTION:
            ttjet_hist = clean_control_region(histograms,
                                              subtract=['QCD', 'V+Jets', 'SingleTop'])
            self.normalisation[
                'TTJet'] = hist_to_value_error_tuplelist(ttjet_hist)

        # next, let's round all numbers (they are event numbers after all
        for sample, values in self.normalisation.items():
            new_values = [(round(v, 1), round(e, 1)) for v, e in values]
            self.normalisation[sample] = new_values

        self.have_normalisation = True

    @mylog.trace()
    def save(self, output_path):
        if not self.have_normalisation:
            self.calculate_normalisation()

        folder_template = '{path}/normalisation/{method}/{CoM}TeV/{variable}/{category}/'
        inputs = {
            'path': output_path,
            'CoM': self.config.centre_of_mass_energy,
            'variable': self.variable,
            'category': self.category,
            'method': self.method_string(),
        }
        output_folder = folder_template.format(**inputs)

        file_template = '{type}_{channel}_{met_type}.txt'
        inputs = {
            'channel': self.channel,
            'met_type': self.met_type,
        }
        write_data_to_JSON(self.normalisation,
                           output_folder + file_template.format(type='normalisation', **inputs))
        write_data_to_JSON(self.initial_normalisation,
                           output_folder + file_template.format(type='initial_normalisation', **inputs))
        write_data_to_JSON(self.templates,
                           output_folder + file_template.format(type='templates', **inputs))

        return output_folder

    @mylog.trace()
    def method_string(self):
        if self.method == self.BACKGROUND_SUBTRACTION:
            return 'background_subtraction'
        if self.method == self.SIMULTANEOUS_FIT:
            return 'simultaneous_fit_' + '_'.join(self.fit_variables)
        if self.method == self.FRACTION_FITTER:
            return 'fraction_fitter'

        return 'unknown_method'


def parse_options():
    parser = OptionParser(__doc__)
    parser.add_option("-p", "--path", dest="path", default='data',
                      help="set output path for JSON files. Default is 'data'.")
    parser.add_option("-i", "--input", dest="input",
                      default='config/measurements/background_subtraction/',
                      help="set output path for JSON files")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                      help="set the variable to analyse (MET, HT, ST, MT, WPT). Default is MET.")
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=8, type=int,
                      help="set the centre of mass energy for analysis. Default = 8 [TeV]")
    parser.add_option('-d', '--debug', dest="debug", action="store_true",
                      help="Print the debug information")
    parser.add_option('--closure_test', dest="closure_test", action="store_true",
                      help="Perform fit on data == sum(MC) * scale factor (MC process)")
    parser.add_option('--closure_test_type', dest="closure_test_type", default='simple',
                      help="Type of closure test (relative normalisation):" + '|'.join(closure_tests.keys()))
    parser.add_option('--test', dest="test", action="store_true",
                      help="Just run the central measurement")

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
    input_template = options.input + '{energy}TeV/{channel}/{variable}/*.json'

    categories = ['QCD_shape']
    categories.extend(measurement_config.categories_and_prefixes.keys())
    categories.extend(measurement_config.rate_changing_systematics_names)
    categories.extend(measurement_config.met_systematics_suffixes)
    categories.extend([measurement_config.vjets_theory_systematic_prefix +
                       systematic for systematic in measurement_config.generator_systematics])
    for met_unc in ['JetEnUp', 'JetEnDown', 'JetResUp', 'JetResDown']:
        # the above ones are done together with
        # categories_and_prefixes, see get_met_type
        categories.remove(met_unc)

    for channel in ['electron', 'muon']:
        inputs = {
            'energy': options.CoM,
            'channel': channel,
            'variable': variable,

        }
        measurement_files = glob.glob(input_template.format(**inputs))
        for f in measurement_files:
            print (f)
            measurement = tools.measurement.Measurement.fromJSON(f)
            # for each measurement
            norm = TTJetNormalisation(
                config=measurement_config,
                measurement=measurement,
                method=TTJetNormalisation.BACKGROUND_SUBTRACTION,
            )
            norm.calculate_normalisation()
            norm.save(output_path)


def get_category_from_file(json_file):
    filename = json_file.split('/')[-1]
    # remove type string
    category = filename.replace('_shape_systematic', '')
    category = category.replace('_rate_systematic', '')
    # remove file ending
    category = category.replace('.json', '')

    return category

if __name__ == '__main__':
    tools.ROOT_utils.set_root_defaults()

    options, args = parse_options()

    # set global variables
    debug = options.debug
    if debug:
        mylog.setLevel(log.DEBUG)

    measurement_config = XSectionConfig(options.CoM)
    # caching of variables for shorter access
    translate_options = measurement_config.translate_options
    variable = options.variable

    output_path = options.path
    if options.closure_test:
        output_path += '/closure_test/'
        output_path += options.closure_test_type + '/'

    main()
