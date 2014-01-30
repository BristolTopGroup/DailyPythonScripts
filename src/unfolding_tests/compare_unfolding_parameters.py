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
from copy import deepcopy
import collections
from rootpy.io import File
from tau_value_determination import get_tau_from_global_correlation, get_tau_from_L_shape, get_data_histogram
from tools.Unfolding import get_unfold_histogram_tuple, Unfolding
from tools.plotting import Histogram_properties, compare_measurements
from config import latex_labels
from tools.Calculation import calculate_normalised_xsection
from tools.hist_utilities import hist_to_value_error_tuplelist, \
    value_error_tuplelist_to_hist, spread_x
from config.variable_binning_8TeV import bin_widths, bin_edges

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
    tau_values = [0, tau_global, tau_L_shape, 1]
    
    return tau_values

def run_test( h_truth, h_measured, h_response, h_data, h_fakes = None, variable = 'MET' ):
    k_values = get_test_k_values( h_truth, h_measured, h_response, h_data )
    tau_values = get_test_tau_values( h_truth, h_measured, h_response, h_data )
    
    k_value_results = {}
    for k_value in k_values:
        unfolding = Unfolding( h_truth,
                          h_measured,
                          h_response,
                          method = 'RooUnfoldSvd',
                          k_value = k_value )
        unfolded_data = unfolding.unfold( h_data )

        result = calculate_normalised_xsection( 
                        hist_to_value_error_tuplelist( unfolded_data ),
                        bin_widths[variable],
                        normalise_to_one = True )
        h_result = value_error_tuplelist_to_hist( result, bin_edges[variable] )
        k_value_results[k_value] = deepcopy( h_result )
    
    tau_value_results = {}
    for tau_value in tau_values:
        unfolding = Unfolding( h_truth,
                          h_measured,
                          h_response,
                          fakes = h_fakes,
#                           method = 'RooUnfoldTUnfold',
                          method = 'TopSVDUnfold',
                          k_value = -1,
                          tau = tau_value )
        unfolded_data = unfolding.unfold( h_data )

        result = calculate_normalised_xsection( 
                        hist_to_value_error_tuplelist( unfolded_data ),
                        bin_widths[variable],
                        normalise_to_one = True )
        h_result = value_error_tuplelist_to_hist( result, bin_edges[variable] )
        tau_value_results[tau_value] = deepcopy( h_result )
        
    return {'k_value_results':k_value_results, 'tau_value_results' :tau_value_results}

def compare( central_mc, expected_result = None, results = {}, variable = 'MET',
             channel = 'electron', bin_edges = [] ):
    global plot_location, luminosity, centre_of_mass, test
    
    title_template = 'CMS Preliminary, $\mathcal{L} = %.1f$ fb$^{-1}$  at $\sqrt{s}$ = %d TeV \n %s'
    channel_label = ''
    if channel == 'electron':
        channel_label = 'e+jets, $\geq$4 jets'
    else:
        channel_label = '$\mu$+jets, $\geq$4 jets'
    title = title_template % ( luminosity / 1000., centre_of_mass, channel_label )
    
    models = {'central' : central_mc}
    if expected_result:
        models['expected'] = expected_result 
    
    measurements = collections.OrderedDict()
    for key, value in results['k_value_results'].iteritems():
        measurements['k = ' + str( key )] = value
    
    for key, value in results['tau_value_results'].iteritems():
        measurements['$\\tau$ = %.2g' % key] = value
    
    # get some spread in x    
    graphs = spread_x( measurements.values(), bin_edges )
    for key, graph in zip( measurements.keys(), graphs ):
        measurements[key] = graph

    histogram_properties = Histogram_properties()
    histogram_properties.name = channel + '_' + variable + '_' + test
    histogram_properties.title = title + ', ' + latex_labels.b_tag_bins_latex['2orMoreBtags']
    histogram_properties.x_axis_title = '$' + latex_labels.variables_latex[variable] + '$'
    histogram_properties.y_axis_title = r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + latex_labels.variables_latex[variable] + '} \left[\mathrm{GeV}^{-1}\\right]$'
#     histogram_properties.y_limits = [0, 0.03]
    histogram_properties.x_limits = [bin_edges[0], bin_edges[-1]]

    compare_measurements( models, measurements, show_measurement_errors = True,
                          histogram_properties = histogram_properties,
                          save_folder = plot_location )
    
    
    
if __name__ == '__main__':
    from ROOT import gROOT, TH1F
    gROOT.SetBatch( True )
    gROOT.ProcessLine( 'gErrorIgnoreLevel = 1001;' )
    # Do not let ROOT handle pointers. That just asks for trouble.
    TH1F.AddDirectory(False)
    tests = ['closure', 'bias', 'data']
    test = tests[0]
#     input_file_8Tev = '/storage/TopQuarkGroup/mc/8TeV/NoSkimUnfolding/v10/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/unfolding_v10_Summer12_DR53X-PU_S10_START53_V7C-v1_NoSkim/TTJets_nTuple_53X_mc_merged_001.root'
#     input_file_bias_8Tev = '/storage/TopQuarkGroup/mc/8TeV/NoSkimUnfolding/v10/TTJets_matchingdown_TuneZ2star_8TeV-madgraph-tauola/unfolding_v10_Summer12_DR53X-PU_S10_START53_V7A-v1_NoSkim/TTJets-matchingdown_nTuple_53X_mc_merged_001.root'
#     input_file_bias_8Tev = '/storage/TopQuarkGroup/mc/8TeV/NoSkimUnfolding/v10/TT_8TeV-mcatnlo/unfolding_v10_Summer12_DR53X-PU_S10_START53_V7A-v1_NoSkim/TTJets_nTuple_53X_mc_merged_001.root'
    input_file_8Tev = '/storage/TopQuarkGroup/results/histogramfiles/AN-13-015_V6_fixed_unfolding_new_variables_ARC_review/unfolding_merged.root'
    input_file_bias_8Tev = '/storage/TopQuarkGroup/results/histogramfiles/AN-13-015_V6_fixed_unfolding_new_variables_ARC_review/unfolding_TTJets_8TeV_mcatnlo.root'
    
    met_type = 'patType1CorrectedPFMet'
    plot_location = 'plots/unfolding_tests/'
    
    variables = ['MET', 'WPT', 'MT', 'ST', 'HT']
    centre_of_mass = 8
    ttbar_xsection = 225.2
    luminosity = 19712
    input_file = File( input_file_8Tev )
    input_file_bias = File( input_file_bias_8Tev )
    
    for channel in ['electron', 'muon']:
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
                                load_fakes = True )
            h_data = None
            h_expected = None
            
            if test == 'data':
                h_data = get_data_histogram( channel, variable, met_type )
            elif test == 'bias':
                h_truth_bias, h_measured_bias, _, h_fakes = get_unfold_histogram_tuple( 
                                inputfile = input_file_bias,
                                variable = variable,
                                channel = channel,
                                met_type = met_type,
                                centre_of_mass = centre_of_mass,
                                ttbar_xsection = ttbar_xsection,
                                luminosity = luminosity,
                                load_fakes = True )
                h_data = deepcopy( h_measured_bias )
                h_expected = h_truth_bias
                h_fakes = None
            else:
                h_data = deepcopy( h_measured )
            results = run_test( h_truth, h_measured, h_response, h_data, h_fakes, variable )
            
            central_mc_result = calculate_normalised_xsection( 
                            hist_to_value_error_tuplelist( h_truth ),
                            bin_widths[variable],
                            normalise_to_one = True )
            central_mc = value_error_tuplelist_to_hist( central_mc_result, bin_edges[variable] )
            if h_expected:
                expected_result = calculate_normalised_xsection( 
                            hist_to_value_error_tuplelist( h_expected ),
                            bin_widths[variable],
                            normalise_to_one = True )
                h_expected = value_error_tuplelist_to_hist( expected_result, bin_edges[variable] )
                
            compare( central_mc = central_mc, expected_result = h_expected,
                     results = results, variable = variable, channel = channel,
                     bin_edges = bin_edges[variable] )
    # done
    
