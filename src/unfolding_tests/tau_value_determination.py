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
from math import log10, pow
from tools.Unfolding import Unfolding, get_unfold_histogram_tuple
from rootpy.io import File
from rootpy.plotting import Graph
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
import matplotlib
from copy import deepcopy
from ROOT import Double, TH1F, TGraph
from tools.file_utilities import read_data_from_JSON
from tools.hist_utilities import value_error_tuplelist_to_hist
from config.variable_binning_8TeV import bin_edges

font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 28}

matplotlib.rc( 'font', **font )

def drange( start, stop, step ):
    r = start
    while r < stop:
        yield r
        r += step

def get_tau_from_global_correlation( h_truth, h_measured, h_response, h_data = None ):
    tau_0 = 1e-7
    tau_max = 0.2
    number_of_iterations = 10000
#     tau_step = ( tau_max - tau_0 ) / number_of_iterations
    
    optimal_tau = 0
    minimal_rho = 9999
    bias_scale = 0.
    
    unfolding = Unfolding( h_truth,
                                  h_measured,
                                  h_response,
                                  method = 'RooUnfoldTUnfold',
                                  tau = tau_0 )
    if h_data:
        unfolding.unfold( h_data )
    else:  # closure test
        unfolding.unfold( h_measured )
    # cache functions and save time in the loop
    Unfold = unfolding.unfoldObject.Impl().DoUnfold
    GetRho = unfolding.unfoldObject.Impl().GetRhoI   
    
    # create lists
    tau_values = []
    rho_values = []
    add_tau = tau_values.append
    add_rho = rho_values.append
#     for current_tau in drange(tau_0, tau_max, tau_step):
    for current_tau in get_tau_range( tau_0, tau_max, number_of_iterations ):
        Unfold( current_tau, h_data, bias_scale )
        current_rho = GetRho( TH1F() )
        
        add_tau( current_tau )
        add_rho( current_rho )
        
        if current_rho < minimal_rho:
            minimal_rho = current_rho
            optimal_tau = current_tau
      
    return optimal_tau, minimal_rho, tau_values, rho_values

def draw_global_correlation( tau_values, rho_values, tau, rho, channel, variable ):
    plt.figure( figsize = ( 16, 16 ), dpi = 200, facecolor = 'white' )
    plt.plot( tau_values, rho_values )
    plt.xscale('log')
    plt.title(r'best $\tau$ from global correlation')
    plt.xlabel( r'$\tau$', fontsize = 40 )
    plt.ylabel( r'$\bar{\rho}(\tau)$', fontsize = 40 )
    ax = plt.axes()
    ax.annotate( r"$\tau = %.3g$" % tau,
            xy = ( tau, rho ), xycoords = 'data',
            xytext = ( 0.0010, 0.5 ), textcoords = 'data',
            arrowprops = dict( arrowstyle = "fancy,head_length=0.4,head_width=0.4,tail_width=0.4",
                            connectionstyle = "arc3" ),
            size = 40,
            )
    if use_data:
        plt.savefig( 'plots/tau_from_global_correlation_%s_channel_%s_DATA.png' % ( channel, variable ) )    
    else:
        plt.savefig( 'plots/tau_from_global_correlation_%s_channel_%s_MC.png' % ( channel, variable ) )

def get_tau_from_L_shape( h_truth, h_measured, h_response, h_data = None ):
    
    tau_min = 1e-7
    tau_max = 0.2
    number_of_scans = 10000
    
    # the best values depend on the variable!!!
#     number_of_scans = 60
#     tau_min = 1e-6
#     tau_max = 1e-7 * 20000 + tau_min
#     tau_min = 1e-7
#     tau_max = 1e-2
    unfolding = Unfolding( h_truth,
                                  h_measured,
                                  h_response,
                                  method = 'RooUnfoldTUnfold',
                                  tau = tau_min )
    if h_data:
        unfolding.unfold( h_data )
    else:  # closure test
        unfolding.unfold( h_measured )
        
    l_curve = TGraph()
        
    unfolding.unfoldObject.Impl().ScanLcurve( number_of_scans, tau_min, tau_max, l_curve )
    
    best_tau = unfolding.unfoldObject.Impl().GetTau()
    x_value = unfolding.unfoldObject.Impl().GetLcurveX()
    y_value = unfolding.unfoldObject.Impl().GetLcurveY()
    
    return best_tau, l_curve, x_value, y_value


def draw_l_shape( l_shape, best_tau, x_value, y_value, channel, variable ):
    total = l_shape.GetN()
    
    x_values = []
    y_values = []
    add_x = x_values.append
    add_y = y_values.append
    for i in range( 0, total ):
        x = Double( 0 )
        y = Double( 0 )
        l_shape.GetPoint( i, x, y )
        add_x( x )
        add_y( y )
    plt.figure( figsize = ( 16, 16 ), dpi = 200, facecolor = 'white' )
    plt.plot( x_values, y_values )
    plt.xlabel( r'log10($\chi^2$)', fontsize = 40 )
    plt.ylabel( 'log10(curvature)', fontsize = 40 )
    ax = plt.axes()
    ax.annotate( r"$\tau = %.3g$" % best_tau,
            xy = ( x_value, y_value ), xycoords = 'data',
            xytext = ( 0.3, 0.3 ), textcoords = 'figure fraction',
            arrowprops = dict( arrowstyle = "fancy,head_length=0.4,head_width=0.4,tail_width=0.4",
                            connectionstyle = "arc3" ),
            size = 40,
            )
    if use_data:
        plt.savefig( 'plots/tau_from_L_shape_%s_channel_%s_DATA.png' % ( channel, variable ) )
    else:
        plt.savefig( 'plots/tau_from_L_shape_%s_channel_%s_MC.png' % ( channel, variable ) )

def get_data_histogram( channel, variable, met_type ):
    fit_result_input = '../cross_section_measurement/data/8TeV/%(variable)s/fit_results/central/fit_results_%(channel)s_%(met_type)s.txt'
    fit_results = read_data_from_JSON( fit_result_input % {'channel': channel, 'variable': variable, 'met_type':met_type} )
    fit_data = fit_results['TTJet']
    h_data = value_error_tuplelist_to_hist( fit_data, bin_edges[variable] )
    return h_data

def get_tau_range( tau_min, tau_max, number_of_points ):
    # Use 3 scan points minimum
    if number_of_points < 3:
        number_of_points = 3

    # Setup Vector
    result = [0] * number_of_points

    # Find the scan points
    # Use equidistant steps on a logarithmic scale
    step = ( log10( tau_max ) - log10( tau_min ) ) / ( number_of_points - 1 );
    for i in range ( 0, number_of_points ):
        result[i] = pow( 10., ( log10( tau_min ) + i * step ) );

    return result;
    
if __name__ == '__main__':
    from ROOT import gROOT
    gROOT.SetBatch( True )
    gROOT.ProcessLine( 'gErrorIgnoreLevel = 1001;' )
    use_data = True
    input_file_8Tev = '/storage/TopQuarkGroup/mc/8TeV/NoSkimUnfolding/v10/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/unfolding_v10_Summer12_DR53X-PU_S10_START53_V7C-v1_NoSkim/TTJets_nTuple_53X_mc_merged_001.root'
    met_type = 'patType1CorrectedPFMet'
    
    # ST and HT have the problem of the overflow bin in the truth/response matrix
    # 7 input bins and 8 output bins (includes 1 overflow bin)
    variables = ['MET', 'WPT', 'MT' , 'ST', 'HT']
    centre_of_mass = 8
    ttbar_xsection = 225.2
    luminosity = 19712
    input_file = File( input_file_8Tev )
    
    taus_from_global_correlaton = {}
    taus_from_L_shape = {}
    for channel in ['electron', 'muon']:
        taus_from_global_correlaton[channel] = {}
        taus_from_L_shape[channel] = {}
        for variable in variables:
            print 'Doing variable"', variable, '" in', channel, '-channel'
        
            h_truth, h_measured, h_response, _ = get_unfold_histogram_tuple( 
                                inputfile = input_file,
                                variable = variable,
                                channel = channel,
                                met_type = met_type,
                                centre_of_mass = centre_of_mass,
                                ttbar_xsection = ttbar_xsection,
                                luminosity = luminosity )
            
            h_data = None
            if use_data:
                h_data = get_data_histogram( channel, variable, met_type )
            else:
                h_data = deepcopy( h_measured )
                
            
            tau, rho, tau_values, rho_values = get_tau_from_global_correlation( h_truth, h_measured, h_response, h_data )
            draw_global_correlation( tau_values, rho_values, tau, rho, channel, variable )
            
            tau, l_curve, x, y = get_tau_from_L_shape( h_truth, h_measured, h_response, h_data )
            draw_l_shape( l_curve, tau, x, y, channel, variable )
        
