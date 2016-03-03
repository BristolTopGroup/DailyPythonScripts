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
from rootpy.io import File
import matplotlib
matplotlib.use('agg')

from uncertainties import ufloat
import numpy
from pylab import plot
from ROOT import TF1

import rootpy.plotting.root2matplotlib as rplt
from rootpy import asrootpy
import matplotlib.pyplot as plt
from copy import deepcopy

from tools.file_utilities import make_folder_if_not_exists
from tools.hist_utilities import value_error_tuplelist_to_hist, get_fit_results_histogram
from tools.ROOT_utils import set_root_defaults
from tools.Unfolding import Unfolding, get_unfold_histogram_tuple
from config.variable_binning import bin_edges_full
from config import CMS, XSectionConfig
from config.latex_labels import variables_latex


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
                           error_treatment = 0,
                           verbose = 1 )
    unfolding.unfold( h_data )
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

def draw_d_i( d_i ):
    global variable, output_folder, output_formats, test, k_values, k_values_crosscheck
    plt.figure( figsize = CMS.figsize, dpi = CMS.dpi, facecolor = CMS.facecolor )
    fit_all_bins = TF1("fit_all_bins", 'expo', 0, d_i.nbins(0)-1)

    fit_exclude_first_bin = TF1("fit_exclude_first_bin", 'expo', 1, d_i.nbins(0)-1)
    fit_all_bins_plus_flat = TF1("fit_all_bins_plus_flat", 'TMath::Exp([0]*x+[1])+[2]', 0, d_i.nbins(0)-1)
    fit_all_bins_plus_flat.SetParameter(0,-2.)
    fit_all_bins_plus_flat.SetParameter(1,3.)
    fit_all_bins_plus_flat.SetParameter(2,1.)
    # fit_all_bins_plus_flat.SetParLimits(2,0.1,2.)    

    fit_all_bins_plus_linear = TF1("fit_all_bins_plus_linear", 'TMath::Exp([0]*x+[1])+[2]+[3]*x', 0, d_i.nbins(0)-1)
    fit_all_bins_plus_linear.SetParameter(0,-2.)
    fit_all_bins_plus_linear.SetParameter(1,3.)
    fit_all_bins_plus_linear.SetParameter(2,0.)
    fit_all_bins_plus_linear.SetParameter(3,0.)
    # fit_all_bins_plus_linear.SetParLimits(2,0.1,10.)   
    fit_all_bins_plus_linear.SetParLimits(3,-10.,0.)
    
    d_i.Fit(fit_all_bins, 'WWSQR')
    d_i.Fit(fit_exclude_first_bin, 'WWSQR')
    d_i.Fit(fit_all_bins_plus_flat, 'WWSQR')
    d_i.Fit(fit_all_bins_plus_linear, 'WWSQR')

    p0_all_bins = ufloat(fit_all_bins.GetParameter(0), fit_all_bins.GetParError(0))
    p1_all_bins = ufloat(fit_all_bins.GetParameter(1), fit_all_bins.GetParError(1))
    k_value_all_bins = -p0_all_bins / p1_all_bins # other way of estimation: crossing the d = 1 line by exponential
    
    p0_exclude_first_bin = ufloat(fit_exclude_first_bin.GetParameter(0), fit_exclude_first_bin.GetParError(0))
    p1_exclude_first_bin = ufloat(fit_exclude_first_bin.GetParameter(1), fit_exclude_first_bin.GetParError(1))
    k_value_exclude_first_bin = -p0_exclude_first_bin / p1_exclude_first_bin # other way of estimation: crossing the d = 1 line by exponential

    p0_fit_all_bins_plus_flat = ufloat(fit_all_bins_plus_flat.GetParameter(0), fit_all_bins_plus_flat.GetParError(0))
    p1_fit_all_bins_plus_flat = ufloat(fit_all_bins_plus_flat.GetParameter(1), fit_all_bins_plus_flat.GetParError(1))
    p2_fit_all_bins_plus_flat = ufloat(fit_all_bins_plus_flat.GetParameter(2), fit_all_bins_plus_flat.GetParError(2))
    k_value_fit_all_bins_plus_flat = -1.0 / p0_fit_all_bins_plus_flat.nominal_value * ( p1_fit_all_bins_plus_flat.nominal_value - numpy.log( p2_fit_all_bins_plus_flat.nominal_value*0.1 ) )
    # Either round value to nearest integer, or pick the bin the value is in
    # Chosen latter for now
    # k_value_fit_all_bins_plus_flat = numpy.round(1+k_value_fit_all_bins_plus_flat,0)
    k_value_fit_all_bins_plus_flat = 1+ int( k_value_fit_all_bins_plus_flat )
    if k_value_fit_all_bins_plus_flat < 2:
        k_value_fit_all_bins_plus_flat = 2
    
    p0_fit_all_bins_plus_linear = ufloat(fit_all_bins_plus_linear.GetParameter(0), fit_all_bins_plus_linear.GetParError(0))
    p1_fit_all_bins_plus_linear = ufloat(fit_all_bins_plus_linear.GetParameter(1), fit_all_bins_plus_linear.GetParError(1))
    p2_fit_all_bins_plus_linear = ufloat(fit_all_bins_plus_linear.GetParameter(2), fit_all_bins_plus_linear.GetParError(2))
    p3_fit_all_bins_plus_linear = ufloat(fit_all_bins_plus_linear.GetParameter(3), fit_all_bins_plus_linear.GetParError(3))
    # k_value_fit_all_bins_plus_linear = -1.0 / p0_fit_all_bins_plus_linear.nominal_value * ( p1_fit_all_bins_plus_linear.nominal_value - numpy.log( p2_fit_all_bins_plus_linear.std_dev ) )

    x = 1
    y = numpy.exp( p0_fit_all_bins_plus_linear.nominal_value * x + p1_fit_all_bins_plus_linear.nominal_value )
    while y > 0.1 * ( p2_fit_all_bins_plus_linear.nominal_value + p3_fit_all_bins_plus_linear.nominal_value*x):
        x += 0.01
        y = numpy.exp( p0_fit_all_bins_plus_linear.nominal_value * x + p1_fit_all_bins_plus_linear.nominal_value )
        if x > 10: break
    # Either round value to nearest integer, or pick the bin the value is in
    # Chosen latter for now
    # k_value_fit_all_bins_plus_linear = numpy.round(1+x,0)
    k_value_fit_all_bins_plus_linear = 1+int(x)
    if k_value_fit_all_bins_plus_linear < 2:
        k_value_fit_all_bins_plus_linear = 2

    # print 'Fitted f_all = $e^{%.2f \\times i + %.2f }$' % ( p1_all_bins.nominal_value, p0_all_bins.nominal_value )
    # print 'Best k-value for %s using exponential fitted to all bins crossing d=1 method: %.2f +- %.2f' % (variable, k_value_all_bins.nominal_value, k_value_all_bins.std_dev)

    # print 'p1_all_bins: %f +- %f ' % ( p1_all_bins.nominal_value, p1_all_bins.std_dev )
    # print 'p0_all_bins: %f +- %f ' % ( p0_all_bins.nominal_value, p0_all_bins.std_dev )

    # print 'Fitted fit_exclude_first_bin = $e^{%.2f \\times i + %.2f }$' % ( p1_exclude_first_bin.nominal_value, p0_exclude_first_bin.nominal_value )
    # print 'Best k-value for %s using exponential fitted to all but 1st bin crossing d=1 method: %.2f +- %.2f' % (variable, k_value_exclude_first_bin.nominal_value, k_value_exclude_first_bin.std_dev)

    # print 'p1_exclude_first_bin: %f +- %f ' % ( p1_exclude_first_bin.nominal_value, p1_exclude_first_bin.std_dev )
    # print 'p0_exclude_first_bin: %f +- %f ' % ( p0_exclude_first_bin.nominal_value, p0_exclude_first_bin.std_dev )

    # print 'Fitted fit_all_bins_plus_flat = $e^{%.2f \\times i + %.2f }$' % ( p1_fit_all_bins_plus_flat.nominal_value, p0_fit_all_bins_plus_flat.nominal_value )

    print 'Fit exponential plus flat'
    print 'p0_fit_all_bins_plus_flat: %f +- %f ' % ( p0_fit_all_bins_plus_flat.nominal_value, p0_fit_all_bins_plus_flat.std_dev )
    print 'p1_fit_all_bins_plus_flat: %f +- %f ' % ( p1_fit_all_bins_plus_flat.nominal_value, p1_fit_all_bins_plus_flat.std_dev )
    print 'p2_fit_all_bins_plus_flat: %f +- %f ' % ( p2_fit_all_bins_plus_flat.nominal_value, p2_fit_all_bins_plus_flat.std_dev )

    print 'Fit exponential plus linear'
    print 'p0_fit_all_bins_plus_linear: %f +- %f ' % ( p0_fit_all_bins_plus_linear.nominal_value, p0_fit_all_bins_plus_linear.std_dev )
    print 'p1_fit_all_bins_plus_linear: %f +- %f ' % ( p1_fit_all_bins_plus_linear.nominal_value, p1_fit_all_bins_plus_linear.std_dev )
    print 'p2_fit_all_bins_plus_linear: %f +- %f ' % ( p2_fit_all_bins_plus_linear.nominal_value, p2_fit_all_bins_plus_linear.std_dev )
    print 'p3_fit_all_bins_plus_linear: %f +- %f ' % ( p3_fit_all_bins_plus_linear.nominal_value, p3_fit_all_bins_plus_linear.std_dev )

    # print '============== Suggested k value : ',1+k_value_fit_all_bins_plus_flat, numpy.round(1+k_value_fit_all_bins_plus_flat,0)

    k_values[variable] = k_value_fit_all_bins_plus_flat
    k_values_crosscheck[variable] = k_value_fit_all_bins_plus_linear
    print '============== ',variable,channel,k_value_fit_all_bins_plus_flat
    print '=== Other ',x,y,k_value_fit_all_bins_plus_linear

    rplt.hist( d_i )
    plt.title( r'SVD unfolding $d_i$ for $' + variables_latex[variable] + '$', CMS.title )
    plt.xlabel( r'$i$', CMS.x_axis_title )
    plt.ylabel( r'$d_i$', CMS.y_axis_title )
    axes = plt.axes()

    # x_all_bins = numpy.linspace(fit_all_bins.GetXmin(), fit_all_bins.GetXmax(), fit_all_bins.GetNpx()*4)#*4 for a very smooth curve
    # function_data_all_bins = numpy.frompyfunc(fit_all_bins.Eval, 1, 1)
    # plot(x_all_bins, function_data_all_bins(x_all_bins), axes=axes, color='red', linewidth=2)
    
    # x_exclude_first_bin = numpy.linspace(fit_exclude_first_bin.GetXmin(), fit_exclude_first_bin.GetXmax(), fit_exclude_first_bin.GetNpx()*4)#*4 for a very smooth curve
    # function_data_exclude_first_bin = numpy.frompyfunc(fit_exclude_first_bin.Eval, 1, 1)
    # plot(x_exclude_first_bin, function_data_exclude_first_bin(x_exclude_first_bin), axes=axes, color='red', linewidth=2)

    # #fill between fits
    x = numpy.arange(0, d_i.nbins(0), 0.1)
    # exp1 = numpy.exp( p1_all_bins.nominal_value*x + p0_all_bins.nominal_value )
    # exp2 = numpy.exp( p1_exclude_first_bin.nominal_value*x + p0_exclude_first_bin.nominal_value )
    # plt.fill_between(x, exp1, exp2, color='k', alpha=.5)

    x_all_bins_plus_flat = numpy.linspace(fit_all_bins_plus_flat.GetXmin(), fit_all_bins_plus_flat.GetXmax(), fit_all_bins_plus_flat.GetNpx()*4)#*4 for a very smooth curve
    function_data_all_bins_plus_flat = numpy.frompyfunc(fit_all_bins_plus_flat.Eval, 1, 1)
    plot(x_all_bins_plus_flat, function_data_all_bins_plus_flat(x_all_bins_plus_flat), axes=axes, color='green', linewidth=2)

    # x_all_bins_plus_linear = numpy.linspace(fit_all_bins_plus_linear.GetXmin(), fit_all_bins_plus_linear.GetXmax(), fit_all_bins_plus_linear.GetNpx()*4)#*4 for a very smooth curve
    # function_data_all_bins_plus_linear = numpy.frompyfunc(fit_all_bins_plus_linear.Eval, 1, 1)
    # plot(x_all_bins_plus_linear, function_data_all_bins_plus_linear(x_all_bins_plus_linear), axes=axes, color='blue', linewidth=2, linestyle = 'dashed')

    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )

    axes.set_yscale( 'log', nonposy = "clip" )

    #adjust the y limits so all d_i are visible on log scale
    value_range = sorted( list( d_i.y() ) )
    for i, value in enumerate(value_range):
        if value == 0:
            del value_range[i]
    axes.set_ylim( ymin = min(value_range)/10 )

    text = 'Fit function:' 
    # text += '\n$f_{all~bins} = e^{%.2f \\times i + %.2f }$' % ( p1_all_bins.nominal_value, p0_all_bins.nominal_value )
    # text += '\n$f_{excl.1st} = e^{%.2f \\times i + %.2f }$' % ( p1_exclude_first_bin.nominal_value, p0_exclude_first_bin.nominal_value )
    text += '\n$f_{exp~plus~flat} = e^{%.2f \\times i + %.2f } + %.2f$' % ( p0_fit_all_bins_plus_flat.nominal_value, p1_fit_all_bins_plus_flat.nominal_value, p2_fit_all_bins_plus_flat.nominal_value )
    # text += '\n$f_{exp~plus~linear} = e^{%.2f \\times i + %.2f } + %.2f  %.2f \\times i$ ' % ( p0_fit_all_bins_plus_linear.nominal_value, p1_fit_all_bins_plus_linear.nominal_value, p2_fit_all_bins_plus_linear.nominal_value, p3_fit_all_bins_plus_linear.nominal_value )
    axes.text(0.3, 0.8, text,
        verticalalignment='bottom', horizontalalignment='left',
        transform=axes.transAxes,
        color='black', fontsize=30, bbox=dict(facecolor='white', edgecolor='none', alpha=0.5))

    # text = 'k value : %.1g (%.1g)' % ( k_value_fit_all_bins_plus_flat, k_value_fit_all_bins_plus_linear )
    text = 'k value : %.1g ' % ( k_value_fit_all_bins_plus_flat )

    axes.text(0.3, 0.7, text,
        verticalalignment='bottom', horizontalalignment='left',
        transform=axes.transAxes,
        color='black', fontsize=30, bbox=dict(facecolor='white', edgecolor='none', alpha=0.5))

    # Plot error band on flat component only
    line = plt.axhline( y = p2_fit_all_bins_plus_flat.nominal_value, linewidth = 2, color = 'red', linestyle = 'dashed' )
    # +/- 10%
    plt.fill_between(x, 0.9*p2_fit_all_bins_plus_flat.nominal_value, 1.1*p2_fit_all_bins_plus_flat.nominal_value, color='k', alpha=.25)
    # # +/- 1 sigma
    # plt.fill_between(x, p2_fit_all_bins_plus_flat.nominal_value-p2_fit_all_bins_plus_flat.std_dev, p2_fit_all_bins_plus_flat.nominal_value+p2_fit_all_bins_plus_flat.std_dev, color='k', alpha=.25)

    if CMS.tight_layout:
        plt.tight_layout()

    save_as_name = 'k_from_d_i_%s_channel_%s_%s' % ( channel, variable, test )

    for output_format in output_formats:
        plt.savefig(output_folder + save_as_name + '.' + output_format)

    
if __name__ == '__main__':
    set_root_defaults()

    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data/M3_angle_bl/',
                      help="set path to JSON files")
    parser.add_option("-o", "--output_folder", dest = "output_folder", default = 'plots/unfolding_tests/',
                      help = "set path to save plots" )
    parser.add_option("-c", "--centre-of-mass-energy", dest = "CoM", default = 13, type = int,
                      help = "set the centre of mass energy for analysis. Default = 13 [TeV]" )
    parser.add_option("-t", "--test", dest="test", default='data',
                      help="set the test type for k-value determination: bias, closure or data (default)")  
    parser.add_option("-u", "--unfolding_method", dest="unfolding_method", default = 'RooUnfoldSvd',
                      help="Unfolding method: RooUnfoldSvd (default), TSVDUnfold, RooUnfoldTUnfold, RooUnfoldInvert, RooUnfoldBinByBin, RooUnfoldBayes")
    parser.add_option("-f", "--load_fakes", dest="load_fakes", action="store_true",
                      help="Load fakes histogram and perform manual fake subtraction in TSVDUnfold")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type used in the analysis of MET-dependent variables")

    ( options, args ) = parser.parse_args()
    measurement_config = XSectionConfig( options.CoM )
    output_formats = ['pdf']
    centre_of_mass = options.CoM
    path_to_JSON = options.path
    met_type = measurement_config.translate_options[options.metType]
    method = options.unfolding_method
    load_fakes = options.load_fakes
    output_folder = options.output_folder + '/%dTeV/k_values/' % measurement_config.centre_of_mass_energy
    make_folder_if_not_exists(output_folder)
    test = options.test


    ttbar_xsection = measurement_config.ttbar_xsection
    luminosity = measurement_config.luminosity * measurement_config.luminosity_scale

    input_filename_central = measurement_config.unfolding_madgraph
    input_filename_bias = measurement_config.unfolding_mcatnlo

    input_file = File( input_filename_central, 'read' )
    input_file_bias = File( input_filename_bias, 'read' )

    variables = ['MET', 'WPT', 'MT', 'ST', 'HT']

    print 'Determining optimal k-values at', centre_of_mass, 'TeV'

    taus_from_global_correlaton = {}
    taus_from_L_shape = {}
    k_values_channel = {}
    k_values_crosscheck_channel = {}
    for channel in ['electron', 'muon']:
        taus_from_global_correlaton[channel] = {}
        taus_from_L_shape[channel] = {}

        k_values = {}
        k_values_crosscheck = {}

        for variable in variables:
            if variable is 'MT': continue
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
            # print 'h_fakes = ', h_fakes
            
            h_data = None
            if test == 'data':
                h_data = get_fit_results_histogram( data_path = path_to_JSON,
                               centre_of_mass = centre_of_mass,
                               channel = channel,
                               variable = variable,
                               met_type = met_type,
                               bin_edges = bin_edges_full[variable] )
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
            elif test == 'closure':
                h_data = deepcopy( h_measured )
            else:
                raise Exception("Unknown test attempted - please choose data, bias or closure")
            
            
            k, hist_di = get_k_from_d_i( h_truth, h_measured, h_response, h_fakes, h_data )
            # print 'Best k-value for %s using d_i >= 1 method: %d' % ( variable, k )
            draw_d_i( hist_di )
        k_values_channel[channel] = k_values
        k_values_crosscheck_channel[channel] = k_values_crosscheck

    for channel in k_values_channel:
        print 'k-values for ',channel,centre_of_mass,'TeV'
        for variable in k_values_channel[channel]:
            print variable,k_values_channel[channel][variable]
            if k_values_channel[channel][variable] != k_values_crosscheck_channel[channel][variable]:
                print '!!! Crosscheck suggests :',k_values_crosscheck_channel[channel][variable]
