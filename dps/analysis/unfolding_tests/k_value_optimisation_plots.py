"""
Script for making various plots for optimisation of regularisation parameters, as provided by RooUnfoldParms class:
http://hepunx.rl.ac.uk/~adye/software/unfold/htmldoc/RooUnfoldParms.html

Plots produced:
- Chi squared values vs regularisation parameter
- RMS of the residuals given by the true and the unfolded distrbutions vs regularisation parameter
- RMS spread of the residuals vs regularisation parameter
- RMS errors vs regularisation parameter

"""
from __future__ import division
from optparse import OptionParser
from rootpy.io import File
import matplotlib
from copy import deepcopy
from dps.utils.ROOT_utils import set_root_defaults

from dps.utils.file_utilities import make_folder_if_not_exists
from dps.utils.hist_utilities import get_fit_results_histogram
from dps.utils.plotting import make_plot, Histogram_properties
from dps.utils.Unfolding import Unfolding, get_unfold_histogram_tuple
from dps.config.variable_binning import bin_edges_vis
from dps.config import CMS
from dps.config.xsection import XSectionConfig
from dps.config.latex_labels import variables_latex

matplotlib.use('agg')
matplotlib.rc('font',**CMS.font)
matplotlib.rc('text', usetex = True)

def draw_regularisation_histograms( h_truth, h_measured, h_response, h_fakes = None, h_data = None ):
    global method, variable, output_folder, output_formats, test
    k_max = h_measured.nbins()
    unfolding = Unfolding( h_truth,
                           h_measured,
                           h_response,
                           h_fakes,
                           method = method,
                           k_value = k_max,
                           error_treatment = 4,
                           verbose = 1 )
    
    RMSerror, MeanResiduals, RMSresiduals, Chi2 = unfolding.test_regularisation ( h_data, k_max )

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'chi2_%s_channel_%s' % ( channel, variable )
    histogram_properties.title = '$\chi^2$ for $%s$ in %s channel, %s test' % ( variables_latex[variable], channel, test )
    histogram_properties.x_axis_title = '$i$'
    histogram_properties.y_axis_title = '$\chi^2$'
    histogram_properties.set_log_y = True
    make_plot(Chi2, 'chi2', histogram_properties, output_folder, output_formats, draw_errorbar = True, draw_legend = False)

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'RMS_error_%s_channel_%s' % ( channel, variable )
    histogram_properties.title = 'Mean error for $%s$ in %s channel, %s test' % ( variables_latex[variable], channel, test )
    histogram_properties.x_axis_title = '$i$'
    histogram_properties.y_axis_title = 'Mean error'
    make_plot(RMSerror, 'RMS', histogram_properties, output_folder, output_formats, draw_errorbar = True, draw_legend = False)

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'RMS_residuals_%s_channel_%s' % ( channel, variable )
    histogram_properties.title = 'RMS of residuals for $%s$ in %s channel, %s test' % ( variables_latex[variable], channel, test )
    histogram_properties.x_axis_title = '$i$'
    histogram_properties.y_axis_title = 'RMS of residuals'
    if test == 'closure':
        histogram_properties.set_log_y = True
    make_plot(RMSresiduals, 'RMSresiduals', histogram_properties, output_folder, output_formats, draw_errorbar = True, draw_legend = False)

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'mean_residuals_%s_channel_%s' % ( channel, variable )
    histogram_properties.title = 'Mean of residuals for $%s$ in %s channel, %s test' % ( variables_latex[variable], channel, test )
    histogram_properties.x_axis_title = '$i$'
    histogram_properties.y_axis_title = 'Mean of residuals'
    make_plot(MeanResiduals, 'MeanRes', histogram_properties, output_folder, output_formats, draw_errorbar = True, draw_legend = False)

if __name__ == '__main__':
    set_root_defaults()

    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data/absolute_eta_M3_angle_bl/',
                      help="set path to JSON files")
    parser.add_option("-o", "--output_folder", dest = "output_folder", default = 'plots/unfolding_tests/',
                      help = "set path to save plots" )
    parser.add_option("-c", "--centre-of-mass-energy", dest = "CoM", default = 8, type = int,
                      help = "set the centre of mass energy for analysis. Default = 8 [TeV]" )
    parser.add_option("-u", "--unfolding_method", dest="unfolding_method", default = 'RooUnfoldSvd',
                      help="Unfolding method: RooUnfoldSvd (default), TSVDUnfold, RooUnfoldTUnfold, RooUnfoldInvert, RooUnfoldBinByBin, RooUnfoldBayes")
    parser.add_option("-f", "--load_fakes", dest="load_fakes", action="store_true",
                      help="Load fakes histogram and perform manual fake subtraction in TSVDUnfold")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type used in the analysis of MET-dependent variables")
    parser.add_option("-t", "--test", dest="test", default='bias',
                      help="set the test type for comparison: bias (default), closure or data")    

    ( options, args ) = parser.parse_args()
    measurement_config = XSectionConfig(options.CoM)
    
    output_formats = ['pdf']
    centre_of_mass = options.CoM
    path_to_JSON = options.path
    met_type = measurement_config.translate_options[options.metType]
    method = options.unfolding_method
    load_fakes = options.load_fakes
    output_folder_base = options.output_folder + '/%dTeV/k_optimisation/' % measurement_config.centre_of_mass_energy
    test = options.test

    ttbar_xsection = measurement_config.ttbar_xsection
    luminosity = measurement_config.luminosity * measurement_config.luminosity_scale

    input_filename_central = measurement_config.unfolding_madgraph
    input_filename_bias = measurement_config.unfolding_mcatnlo
    
    variables = ['MET', 'WPT', 'MT' , 'ST', 'HT']

    print 'Performing k-value optimisation checks using', test, 'info at', centre_of_mass, 'TeV'

    input_file = File( input_filename_central, 'read' )
    input_file_bias = File( input_filename_bias, 'read' )

    for channel in ['electron', 'muon']:
        for variable in variables:
            print 'Doing variable', variable, 'in', channel, 'channel'
        
            h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( 
                                inputfile = input_file,
                                variable = variable,
                                channel = channel,
                                met_type = met_type,
                                centre_of_mass = centre_of_mass,
                                ttbar_xsection = ttbar_xsection,
                                luminosity = luminosity,
                                load_fakes = load_fakes)
            print 'h_fakes = ', h_fakes
            
            h_data = None
            if test == 'data':
                h_data = get_fit_results_histogram( data_path = path_to_JSON,
                               centre_of_mass = centre_of_mass,
                               channel = channel,
                               variable = variable,
                               met_type = met_type,
                               bin_edges = bin_edges_vis[variable] )
                output_folder = output_folder_base + '/' + variable + '_data/'
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
                output_folder = output_folder_base + '/' + variable + '_bias/'
            elif test == 'closure':
                h_data = deepcopy( h_measured )
                output_folder = output_folder_base + '/' + variable + '_closure/'
            else:
                raise Exception("Unknown test attempted - please choose data, bias or closure")
            make_folder_if_not_exists(output_folder)
            
            draw_regularisation_histograms( h_truth, h_measured, h_response, h_fakes, h_data )