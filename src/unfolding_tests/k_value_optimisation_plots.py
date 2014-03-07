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
from tools.Unfolding import Unfolding, get_unfold_histogram_tuple
from rootpy.io import File
import matplotlib
matplotlib.use('agg')
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from copy import deepcopy
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from tools.hist_utilities import value_error_tuplelist_to_hist
from tools.plotting import make_plot, Histogram_properties
from config.variable_binning_8TeV import bin_edges
from config import CMS
from config.latex_labels import variables_latex
from config.cross_section_measurement_common import translate_options
from rootpy import asrootpy

matplotlib.rc('font',**CMS.font)
matplotlib.rc('text', usetex = True)

def draw_regularisation_histograms( h_truth, h_measured, h_response, h_fakes = None, h_data = None ):
    global method, variable, output_folder, output_formats, use_data
    k_max = h_measured.nbins()
    unfolding = Unfolding( h_truth,
                           h_measured,
                           h_response,
                           h_fakes,
                           method = method,
                           k_value = k_max,
                           Hreco = 2,
                           verbose = 1 )
    
    RMSerror, MeanResiduals, RMSresiduals, Chi2 = unfolding.test_regularisation ( h_data, k_max )

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'chi2_%s_channel_%s' % ( channel, variable )
    if use_data:
        histogram_properties.name += '_DATA'
    else:
        histogram_properties.name += '_MC'
    histogram_properties.title = '$\chi^2$ for $' + variables_latex[variable] + '$' + ' in ' + channel + ' channel'
    histogram_properties.x_axis_title = '$i$'
    histogram_properties.y_axis_title = '$\chi^2$'
    make_plot(Chi2, 'chi2', histogram_properties, output_folder, output_formats, draw_legend = False)

    histogram_properties.name = 'RMS_error_%s_channel_%s' % ( channel, variable )
    if use_data:
        histogram_properties.name += '_DATA'
    else:
        histogram_properties.name += '_MC'
    histogram_properties.title = 'RMS error for $' + variables_latex[variable] + '$' + ' in ' + channel + ' channel'
    histogram_properties.x_axis_title = '$i$'
    histogram_properties.y_axis_title = 'RMS error'
    make_plot(RMSerror, 'RMS', histogram_properties, output_folder, output_formats, draw_legend = False)
    
    histogram_properties.name = 'RMS_residuals_%s_channel_%s' % ( channel, variable )
    if use_data:
        histogram_properties.name += '_DATA'
    else:
        histogram_properties.name += '_MC'
    histogram_properties.title = 'RMS residuals for $' + variables_latex[variable] + '$' + ' in ' + channel + ' channel'
    histogram_properties.x_axis_title = '$i$'
    histogram_properties.y_axis_title = 'RMS residuals'
    make_plot(RMSresiduals, 'RMSresiduals', histogram_properties, output_folder, output_formats, draw_legend = False)

    histogram_properties.name = 'mean_residuals_%s_channel_%s' % ( channel, variable )
    if use_data:
        histogram_properties.name += '_DATA'
    else:
        histogram_properties.name += '_MC'
    histogram_properties.title = 'Mean residuals for $' + variables_latex[variable] + '$' + ' in ' + channel + ' channel'
    histogram_properties.x_axis_title = '$i$'
    histogram_properties.y_axis_title = 'Mean residuals'
    make_plot(MeanResiduals, 'MeanRes', histogram_properties, output_folder, output_formats, draw_legend = False)


def get_data_histogram( path_to_JSON, channel, variable, met_type ):
    fit_result_input = path_to_JSON + '/8TeV/%(variable)s/fit_results/central/fit_results_%(channel)s_%(met_type)s.txt'
    fit_results = read_data_from_JSON( fit_result_input % {'channel': channel, 'variable': variable, 'met_type':met_type} )
    fit_data = fit_results['TTJet']
    h_data = value_error_tuplelist_to_hist( fit_data, bin_edges[variable] )
    return h_data

   
if __name__ == '__main__':
    from ROOT import gROOT
    gROOT.SetBatch( True )
    gROOT.ProcessLine( 'gErrorIgnoreLevel = 1001;' )

    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='../cross_section_measurement/data/',
                      help="set path to JSON files")
    parser.add_option("-o", "--output_folder", dest = "output_folder", default = 'plots_k_tests/',
                      help = "set path to save plots" )
    parser.add_option("-c", "--centre-of-mass-energy", dest = "CoM", default = 8, type = int,
                      help = "set the centre of mass energy for analysis. Default = 8 [TeV]" )
    parser.add_option("-d", "--use-data", dest = "use_data", action="store_true",
                      help = "use fitted results from data" )
    parser.add_option("-u", "--unfolding_method", dest="unfolding_method", default = 'RooUnfoldSvd',
                      help="Unfolding method: RooUnfoldSvd (default), TSVDUnfold, TopSVDUnfold, RooUnfoldTUnfold, RooUnfoldInvert, RooUnfoldBinByBin, RooUnfoldBayes")
    parser.add_option("-f", "--load_fakes", dest="load_fakes", action="store_true",
                      help="Load fakes histogram and perform manual fake subtraction in TSVDUnfold")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type used in the analysis of MET-dependent variables")

    ( options, args ) = parser.parse_args()

    output_formats = ['pdf']
    centre_of_mass = options.CoM
    use_data = options.use_data
    path_to_JSON = options.path
    met_type = translate_options[options.metType]
    method = options.unfolding_method
    load_fakes = options.load_fakes
    output_folder = options.output_folder
    make_folder_if_not_exists(options.output_folder)

    
    if options.CoM == 8:
        from config.variable_binning_8TeV import bin_edges
        import config.cross_section_measurement_8TeV as measurement_config
    elif options.CoM == 7:
        from config.variable_binning_7TeV import bin_edges
        import config.cross_section_measurement_7TeV as measurement_config
    else:
        import sys
        sys.exit( 'Unknown centre of mass energy' )

    ttbar_xsection = measurement_config.ttbar_xsection
    luminosity = measurement_config.luminosity * measurement_config.luminosity_scale

    input_file = File( measurement_config.unfolding_madgraph_file )
    
    variables = ['MET', 'WPT', 'MT' , 'ST', 'HT']    

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
            if use_data:
                h_data = get_data_histogram( path_to_JSON, channel, variable, met_type )
            else:
                h_data = deepcopy( h_measured )
            
            draw_regularisation_histograms( h_truth, h_measured, h_response, h_fakes, h_data )