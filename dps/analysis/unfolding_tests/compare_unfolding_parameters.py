"""
The purpose of this of this script is to compare the unfolding performance for 
different unfolding parameters k. Three kinds of tests are envisioned:
1) closure tests: 
    - using the same MC to create the response matrix & provide pseudo-data
    - comparing result to input

2) bias test:
    - using default MC for response matrix but modified MC for pseudo-data
    - the MC is modified such it has a different shape compared to the default
    - the unfolded result should not be biased towards the input
    
3) data test:
    - test if the unfolded result is biased towards a certain shape 
"""
from optparse import OptionParser
from copy import deepcopy
from ROOT import TH1F
from dps.utils.ROOT_utils import set_root_defaults
import collections
from rootpy.io import File

from dps.config import latex_labels
from dps.config.xsection import XSectionConfig
from dps.config.variable_binning import bin_edges_vis
from dps.utils.plotting import Histogram_properties, compare_measurements
from dps.utils.Unfolding import get_unfold_histogram_tuple, Unfolding
from dps.utils.hist_utilities import get_fit_results_histogram
from dps.utils.hist_utilities import spread_x
from dps.utils.file_utilities import make_folder_if_not_exists

def get_test_k_values( h_truth, h_measured, h_response, h_data = None ):
    """
        k values should be between 2 and the number of bins
    """
    n_bins = len( h_measured )
    
    return [i for i in range( 2, n_bins - 1 )]

def run_test( h_truth, h_measured, h_response, h_data, h_fakes = None, variable = 'MET' ):
    global method, load_fakes
    k_values = get_test_k_values( h_truth, h_measured, h_response, h_data )
    
    k_value_results = {}
    for k_value in k_values:
        unfolding = Unfolding( h_truth,
                          h_measured,
                          h_response,
                          fakes = h_fakes,
                          method = method,
                          k_value = k_value )
        unfolded_data = unfolding.unfold( h_data )
        k_value_results[k_value] = deepcopy( unfolded_data )
    
        
    return { 'k_value_results' : k_value_results }

def compare( central_mc, expected_result = None, measured_result = None, results = {}, variable = 'MET',
             channel = 'electron', bin_edges = [] ):
    global input_file, plot_location, ttbar_xsection, luminosity, centre_of_mass, method, test, log_plots

    channel_label = ''
    if channel == 'electron':
        channel_label = 'e+jets, $\geq$4 jets'
    elif channel == 'muon':
        channel_label = '$\mu$+jets, $\geq$4 jets'
    else:
        channel_label = '$e, \mu$ + jets combined, $\geq$4 jets'

    if test == 'data':
        title_template = 'CMS Preliminary, $\mathcal{L} = %.1f$ fb$^{-1}$  at $\sqrt{s}$ = %d TeV \n %s'
        title = title_template % ( luminosity / 1000., centre_of_mass, channel_label )
    else:
        title_template = 'CMS Simulation at $\sqrt{s}$ = %d TeV \n %s'
        title = title_template % ( centre_of_mass, channel_label )

    models = {latex_labels.measurements_latex['MADGRAPH'] : central_mc}
    if expected_result and test == 'data':
        models.update({'fitted data' : expected_result})
        # scale central MC to lumi
        nEvents = input_file.EventFilter.EventCounter.GetBinContent( 1 )  # number of processed events 
        lumiweight = ttbar_xsection * luminosity / nEvents
        central_mc.Scale( lumiweight )
    elif expected_result:
        models.update({'expected' : expected_result})
    if measured_result and test != 'data':
        models.update({'measured' : measured_result})
    
    measurements = collections.OrderedDict()
    for key, value in results['k_value_results'].iteritems():
        measurements['k = ' + str( key )] = value
    
    # get some spread in x    
    graphs = spread_x( measurements.values(), bin_edges )
    for key, graph in zip( measurements.keys(), graphs ):
        measurements[key] = graph

    histogram_properties = Histogram_properties()
    histogram_properties.name = channel + '_' + variable + '_' + method + '_' + test
    histogram_properties.title = title + ', ' + latex_labels.b_tag_bins_latex['2orMoreBtags']
    histogram_properties.x_axis_title = '$' + latex_labels.variables_latex[variable] + '$'
    histogram_properties.y_axis_title = r'Events'
#     histogram_properties.y_limits = [0, 0.03]
    histogram_properties.x_limits = [bin_edges[0], bin_edges[-1]]

    if log_plots:
        histogram_properties.set_log_y = True
        histogram_properties.name += '_log'

    compare_measurements( models, measurements, show_measurement_errors = True,
                          histogram_properties = histogram_properties,
                          save_folder = plot_location, save_as = ['pdf'] )
    
    
    
if __name__ == '__main__':
    set_root_defaults()
    # Do not let ROOT handle pointers. That just asks for trouble.
    TH1F.AddDirectory( False )

    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "data_path", default = 'data/absolute_eta_M3_angle_bl',
                  help = "set input path for data JSON files (for data test)" )
    parser.add_option( "-o", "--output-folder", dest = "output_folder", default = 'plots/unfolding_tests/',
                      help = "set path to save plots" )
    parser.add_option( "-c", "--centre-of-mass-energy", dest = "CoM", default = 8, type = int,
                      help = "set the centre of mass energy for analysis. Default = 8 [TeV]" )
    parser.add_option( "-f", "--load-fakes", dest = "load_fakes", action = "store_true",
                      help = "Load fakes histogram and perform manual fake subtraction in TSVDUnfold" )
    parser.add_option( "-u", "--unfolding-method", dest = "unfolding_method", default = 'RooUnfoldSvd',
                      help = "Unfolding method: RooUnfoldSvd (default), TSVDUnfold, RooUnfoldTUnfold, RooUnfoldInvert, RooUnfoldBinByBin, RooUnfoldBayes" )
    parser.add_option( "-m", "--metType", dest = "metType", default = 'type1',
                      help = "set MET type used in the analysis of MET-dependent variables" )
    parser.add_option( "-t", "--test", dest = "test", default = 'closure',
                      help = "set the test type for comparison: bias, closure (default) or data" )    
    parser.add_option( "-l", "--log-plots", dest = "log_plots", action = "store_true",
                      help = "plots the y axis in log scale" )

    ( options, args ) = parser.parse_args()
    measurement_config = XSectionConfig( options.CoM)
    
    centre_of_mass = measurement_config.centre_of_mass_energy
    luminosity = measurement_config.luminosity * measurement_config.luminosity_scale
    ttbar_xsection = measurement_config.ttbar_xsection
    load_fakes = options.load_fakes
    method = options.unfolding_method
    path_to_JSON = options.data_path
    plot_location = options.output_folder + '/' + str(centre_of_mass) + 'TeV/' + options.test + '/'
    met_type = measurement_config.translate_options[options.metType]
    log_plots = options.log_plots
    make_folder_if_not_exists( plot_location )

    test = options.test

    input_filename_central = measurement_config.unfolding_madgraph
    input_filename_bias = measurement_config.unfolding_mcatnlo

    variables = ['MET', 'WPT', 'MT', 'ST', 'HT']

    input_file = File( input_filename_central, 'read' )
    input_file_bias = File( input_filename_bias, 'read' )

    print 'Performing', test, 'unfolding checks at', centre_of_mass, 'TeV'
    
    for channel in ['electron', 'muon']:
        for variable in variables:
            print 'Doing', variable, 'variable in', channel, 'channel'
            h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( 
                                inputfile = input_file,
                                variable = variable,
                                channel = channel,
                                met_type = met_type,
                                centre_of_mass = centre_of_mass,
                                ttbar_xsection = ttbar_xsection,
                                luminosity = luminosity,
                                load_fakes = load_fakes )
            h_data = None
            h_expected = None
            
            if test == 'data':
                h_data = get_fit_results_histogram( data_path = path_to_JSON,
                               centre_of_mass = centre_of_mass,
                               channel = channel,
                               variable = variable,
                               met_type = met_type,
                               bin_edges = bin_edges_vis[variable] )
                h_expected = deepcopy( h_data )
            elif test == 'bias':
                h_truth_bias, h_measured_bias, _, h_fakes = get_unfold_histogram_tuple( 
                                inputfile = input_file_bias,
                                variable = variable,
                                channel = channel,
                                met_type = met_type,
                                centre_of_mass = centre_of_mass,
                                ttbar_xsection = ttbar_xsection,
                                luminosity = luminosity,
                                load_fakes = load_fakes )
                h_data = deepcopy( h_measured_bias )
                h_expected = h_truth_bias
                # h_fakes = None
            elif test == 'closure':
                h_data = deepcopy( h_measured )
            else:
                raise Exception("Unknown test attempted - please choose data, bias or closure")

            results = run_test( h_truth, h_measured, h_response, h_data, h_fakes, variable )
                
            compare( central_mc = h_truth, expected_result = h_expected, measured_result = h_data,
                     results = results, variable = variable, channel = channel,
                     bin_edges = bin_edges_vis[variable] )
    # done
    
