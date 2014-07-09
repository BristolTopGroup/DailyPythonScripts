"""
The purpose of this of this script is to compare the unfolding performance for 
different unfolding parameters k or tau. Three kinds of tests are envisioned:
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
from tools.ROOT_utililities import set_root_defaults
import collections
from rootpy.io import File

from config import latex_labels, XSectionConfig
from config.variable_binning import bin_widths, bin_edges
from tools.plotting import Histogram_properties, compare_measurements
from tau_value_determination import get_tau_from_global_correlation
from tau_value_determination import get_tau_from_L_shape, get_data_histogram
from tools.Unfolding import get_unfold_histogram_tuple, Unfolding
from tools.Calculation import calculate_normalised_xsection
from tools.hist_utilities import hist_to_value_error_tuplelist
from tools.hist_utilities import value_error_tuplelist_to_hist, spread_x
from tools.file_utilities import make_folder_if_not_exists

def get_test_k_values( h_truth, h_measured, h_response, h_data = None ):
    """
        k values should be between 2 and the number of bins
    """
    n_bins = len( h_measured )
    
    return [i for i in range( 2, n_bins - 1 )]

def get_test_tau_values( h_truth, h_measured, h_response, h_data = None ):
    """
        tau values should be between 0 and large (> 1)
    """
    tau_global = get_tau_from_global_correlation( h_truth, h_measured, h_response, h_data )[0]
    tau_L_shape = get_tau_from_L_shape( h_truth, h_measured, h_response, h_data )[0]
    tau_values = [0, tau_global, tau_L_shape, 40]
    
    return tau_values

def run_test( h_truth, h_measured, h_response, h_data, h_fakes = None, variable = 'MET' ):
    global method, load_fakes, do_taus
    k_values = get_test_k_values( h_truth, h_measured, h_response, h_data )
    if do_taus:
        tau_values = get_test_tau_values( h_truth, h_measured, h_response, h_data )
    
    k_value_results = {}
    for k_value in k_values:
        unfolding = Unfolding( h_truth,
                          h_measured,
                          h_response,
                          fakes = h_fakes,
                          method = method,
                          k_value = k_value )
        unfolded_data = unfolding.unfold( h_data )

        result = calculate_normalised_xsection( 
                        hist_to_value_error_tuplelist( unfolded_data ),
                        bin_widths[variable],
                        normalise_to_one = False )
        h_result = value_error_tuplelist_to_hist( result, bin_edges[variable] )
        k_value_results[k_value] = deepcopy( h_result )
    
    tau_value_results = {}
    if do_taus:
        for tau_value in tau_values:
            unfolding = Unfolding( h_truth,
                              h_measured,
                              h_response,
                              fakes = h_fakes,
                              method = 'TopSVDUnfold',
                              k_value = -1,
                              tau = tau_value )
            unfolded_data = unfolding.unfold( h_data )

            result = calculate_normalised_xsection( 
                            hist_to_value_error_tuplelist( unfolded_data ),
                            bin_widths[variable],
                            normalise_to_one = False)
            h_result = value_error_tuplelist_to_hist( result, bin_edges[variable] )
            tau_value_results[tau_value] = deepcopy( h_result )
        
    return {'k_value_results':k_value_results, 'tau_value_results' :tau_value_results}

def compare( central_mc, expected_result = None, measured_result = None, results = {}, variable = 'MET',
             channel = 'electron', bin_edges = [] ):
    global plot_location, luminosity, centre_of_mass, method, test, do_taus, log_plots

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
    if expected_result:
        models.update({'expected' : expected_result})
    if measured_result and test != 'data':
        models.update({'measured' : measured_result})
    
    measurements = collections.OrderedDict()
    for key, value in results['k_value_results'].iteritems():
        measurements['k = ' + str( key )] = value
    
    if do_taus:
        for key, value in results['tau_value_results'].iteritems():
            measurements['$\\tau$ = %.2g' % key] = value
    
    # get some spread in x    
    graphs = spread_x( measurements.values(), bin_edges )
    for key, graph in zip( measurements.keys(), graphs ):
        measurements[key] = graph

    histogram_properties = Histogram_properties()
    histogram_properties.name = channel + '_' + variable + '_' + method + '_' + test
    histogram_properties.title = title + ', ' + latex_labels.b_tag_bins_latex['2orMoreBtags']
    histogram_properties.x_axis_title = '$' + latex_labels.variables_latex[variable] + '$'
    histogram_properties.y_axis_title = r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + latex_labels.variables_latex[variable] + '} \left[\mathrm{GeV}^{-1}\\right]$'
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
    parser.add_option( "-o", "--output-folder", dest = "output_folder", default = 'plots_unfolding_tests/',
                      help = "set path to save plots" )
    parser.add_option( "-c", "--centre-of-mass-energy", dest = "CoM", default = 8, type = int,
                      help = "set the centre of mass energy for analysis. Default = 8 [TeV]" )
    parser.add_option( "-f", "--load-fakes", dest = "load_fakes", action = "store_true",
                      help = "Load fakes histogram and perform manual fake subtraction in TSVDUnfold" )
    parser.add_option( "-u", "--unfolding-method", dest = "unfolding_method", default = 'RooUnfoldSvd',
                      help = "Unfolding method: RooUnfoldSvd (default), TSVDUnfold, TopSVDUnfold, RooUnfoldTUnfold, RooUnfoldInvert, RooUnfoldBinByBin, RooUnfoldBayes" )
    parser.add_option( "-m", "--metType", dest = "metType", default = 'type1',
                      help = "set MET type used in the analysis of MET-dependent variables" )
    parser.add_option( "-t", "--test", dest = "test", default = 'bias',
                      help = "set the test type for comparison: bias (default), closure or data" )    
    parser.add_option( "-a", "--plot-tau-values", dest = "do_taus", action = "store_true",
                      help = "include results for tau values" )
    parser.add_option( "-l", "--log-plots", dest = "log_plots", action = "store_true",
                      help = "plots the y axis in log scale" )

    ( options, args ) = parser.parse_args()
    measurement_config = XSectionConfig(options.CoM)
    
    centre_of_mass = options.CoM
    luminosity = measurement_config.luminosity * measurement_config.luminosity_scale
    ttbar_xsection = measurement_config.ttbar_xsection
    load_fakes = options.load_fakes
    method = options.unfolding_method
    plot_location = options.output_folder + '/' + options.test + '/'
    met_type = measurement_config.translate_options[options.metType]
    do_taus = options.do_taus
    log_plots = options.log_plots
    make_folder_if_not_exists( plot_location )

    test = options.test

    input_filename_central = measurement_config.unfolding_madgraph
    input_filename_bias = measurement_config.unfolding_mcatnlo

    variables = ['MET', 'WPT', 'MT', 'ST', 'HT']

    input_file = File( input_filename_central, 'read' )
    input_file_bias = File( input_filename_bias, 'read' )
    
    for channel in ['electron', 'muon', 'combined']:
        for variable in variables:
            print 'Doing variable"', variable, '" in', channel, 'channel'
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
                h_data = get_data_histogram( channel, variable, met_type )
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
            else:
                h_data = deepcopy( h_measured )
            results = run_test( h_truth, h_measured, h_response, h_data, h_fakes, variable )
            
            central_mc_result = calculate_normalised_xsection( 
                            hist_to_value_error_tuplelist( h_truth ),
                            bin_widths[variable],
                            normalise_to_one = False )
            central_mc = value_error_tuplelist_to_hist( central_mc_result, bin_edges[variable] )
            if h_expected:
                expected_result = calculate_normalised_xsection( 
                            hist_to_value_error_tuplelist( h_expected ),
                            bin_widths[variable],
                            normalise_to_one = False )
                h_expected = value_error_tuplelist_to_hist( expected_result, bin_edges[variable] )

            data_result = calculate_normalised_xsection( 
                            hist_to_value_error_tuplelist( h_data ),
                            bin_widths[variable],
                            normalise_to_one = False )
            h_data = value_error_tuplelist_to_hist( data_result, bin_edges[variable] )
                
            compare( central_mc = central_mc, expected_result = h_expected, measured_result = h_data,
                     results = results, variable = variable, channel = channel,
                     bin_edges = bin_edges[variable] )
    # done
    
