"""
Script for determining the optimal tau value for the Singular Value Decomposition (SVD) unfolding.

From http://root.cern.ch/root/html/TUnfold.html:
Note1: ALWAYS choose a higher number of bins on the reconstructed side
         as compared to the generated size!
Note2: the events which are generated but not reconstructed
         have to be added to the appropriate overflow bins of A
Note3: make sure all bins have sufficient statistics and their error is
         non-zero. By default, bins with zero error are simply skipped;
         however, this may cause problems if You try to unfold something
         which depends on these input bins.
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
from config.variable_binning_8TeV import bin_edges
from config import CMS
from config.latex_labels import variables_latex
from config.cross_section_measurement_common import translate_options
from rootpy import asrootpy

matplotlib.rc('font',**CMS.font)
matplotlib.rc('text', usetex = True)

def get_k_from_d_i( h_truth, h_measured, h_response, h_fakes = None, h_data = None ):
    global method
    k_start = h_measured.nbins()
    unfolding = Unfolding( h_truth,
                           h_measured,
                           h_response,
                           h_fakes,
                           method = method,
                           k_value = k_start,
                           Hreco = 0,
                           verbose = 1 )
    if h_data:
        unfolding.unfold( h_data )
    else:  # closure test
        unfolding.unfold( h_measured )
    hist_d_i = None
    if method == 'RooUnfoldSvd':
        hist_d_i = asrootpy( unfolding.unfoldObject.Impl().GetD() )
    elif method == 'TSVDUnfold':
        hist_d_i = asrootpy( unfolding.unfoldObject.GetD() )
    best_k = k_start
    for i, d_i in enumerate( hist_d_i.y() ):
        # i count starts at 0
        if d_i >= 1:
            continue
        else:
            # first i when d_i < 0, is k
            # because i starts at 0
            best_k = i
            break
            
    return best_k, hist_d_i.clone()


def get_data_histogram( path_to_JSON, channel, variable, met_type ):
    fit_result_input = path_to_JSON + '/8TeV/%(variable)s/fit_results/central/fit_results_%(channel)s_%(met_type)s.txt'
    fit_results = read_data_from_JSON( fit_result_input % {'channel': channel, 'variable': variable, 'met_type':met_type} )
    fit_data = fit_results['TTJet']
    h_data = value_error_tuplelist_to_hist( fit_data, bin_edges[variable] )
    return h_data

def draw_d_i( d_i ):
    global variable, output_folder, output_formats
    plt.figure( figsize = CMS.figsize, dpi = CMS.dpi, facecolor = CMS.facecolor )
    rplt.hist( d_i )
    plt.title( r'SVD unfolding $d_i$ for $' + variables_latex[variable] + '$', CMS.title )
    plt.xlabel( r'$i$', CMS.x_axis_title )
    plt.ylabel( r'$d_i$', CMS.y_axis_title )
    axes = plt.axes()

    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )

    axes.set_yscale( 'log', nonposy = "clip" )

    #adjust the y limits so all d_i are visible on log scale
    value_range = sorted( list( d_i.y() ) )
    for i, value in enumerate(value_range):
        if value == 0:
            del value_range[i]
    axes.set_ylim( ymin = min(value_range)/10 )
    
    plt.axhline( y = 1, linewidth = 3, color = 'red' )

    if CMS.tight_layout:
        plt.tight_layout()

    if use_data:
        save_as_name = 'k_from_d_i_%s_channel_%s_DATA' % ( channel, variable )
    else:
        save_as_name = 'k_from_d_i_%s_channel_%s_MC' % ( channel, variable )

    for output_format in output_formats:
        plt.savefig(output_folder + save_as_name + '.' + output_format)

    
if __name__ == '__main__':
    from ROOT import gROOT
    gROOT.SetBatch( True )
    gROOT.ProcessLine( 'gErrorIgnoreLevel = 1001;' )

    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='../cross_section_measurement/data/',
                      help="set path to JSON files")
    parser.add_option("-o", "--output_folder", dest = "output_folder", default = 'plots_k_values/',
                      help = "set path to save plots" )
    parser.add_option("-c", "--centre-of-mass-energy", dest = "CoM", default = 8, type = int,
                      help = "set the centre of mass energy for analysis. Default = 8 [TeV]" )
    parser.add_option("-d", "--use-data", dest = "use_data", action="store_true",
                      help = "use fitted results from data" )
    parser.add_option("-u", "--unfolding_method", dest="unfolding_method", default = 'TSVDUnfold',
                      help="Unfolding method: RooUnfoldSvd, TSVDUnfold (default), TopSVDUnfold, RooUnfoldTUnfold, RooUnfoldInvert, RooUnfoldBinByBin, RooUnfoldBayes")
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
        
    # ST and HT have the problem of the overflow bin in the truth/response matrix
    # 7 input bins and 8 output bins (includes 1 overflow bin)
    variables = ['MET', 'WPT', 'MT' , 'ST', 'HT']
    
    taus_from_global_correlaton = {}
    taus_from_L_shape = {}
    for channel in ['electron', 'muon']:
        taus_from_global_correlaton[channel] = {}
        taus_from_L_shape[channel] = {}
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
            
            
            k, hist_di = get_k_from_d_i( h_truth, h_measured, h_response, h_fakes, h_data )
            print 'Best k-value for %s = %d' % ( variable, k )
            draw_d_i( hist_di )
