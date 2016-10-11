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
from rootpy.io import File
import matplotlib.pyplot as plt
import matplotlib
from copy import deepcopy
from ROOT import Double, TH1F, TGraph

# @BROKEN
from dps.config.variable_binning import bin_edges
from dps.utils.file_utilities import read_data_from_JSON
from dps.utils.hist_utilities import value_error_tuplelist_to_hist
from dps.utils.Unfolding import Unfolding, get_unfold_histogram_tuple
from dps.utils.ROOT_utils import set_root_defaults
# from examples.Bin_Centers import nbins
from dps.config.xsection import XSectionConfig
used_k = 2

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
    global used_k
    # this gives 9.97e-05 with TUnfold
    tau_0 = 1
    tau_max = 1000
    number_of_iterations = int(100)
    n_toy = int(1000)
#     tau_step = ( tau_max - tau_0 ) / number_of_iterations
    
    optimal_tau = 0
    minimal_rho = 9999
#     bias_scale = 0.
    
    unfolding = Unfolding( h_truth,
                                  h_measured,
                                  h_response,
                                  method = 'RooUnfoldSvd',
                                  tau = tau_0,
				  k_value = -1, )
    data = None
    if h_data:
        data = h_data 
    else:  # closure test
        data = h_measured 
    unfolding.unfold( data )
    # get unfolding object
    tau_svd_unfold = unfolding.Impl()
    # get covariance matrix
    cov = tau_svd_unfold.get_data_covariance_matrix(data)
    # cache functions and save time in the loop
    SetTau = tau_svd_unfold.SetTau
    GetCovMatrix = tau_svd_unfold.GetUnfoldCovMatrix
    GetRho = tau_svd_unfold.get_global_correlation

    n_bins = h_data.nbins()
    print 'k to tau'
    to_return = None
    for k in range(2, n_bins + 1):
        tau_from_k = tau_svd_unfold.kToTau(k)
        SetTau( tau_from_k )
        cov_matrix = GetCovMatrix(cov, n_toy, 1)
        rho = GetRho(cov_matrix, data)
        if k == used_k:
            to_return = (tau_from_k, rho)
            print 'k =', k, ', tau = ', tau_from_k, ', rho = ', rho,  '<-- currently used'
        else:
            print 'k =', k, ', tau = ', tau_from_k, ', rho = ', rho
    #print 'used k (=%d) to tau' % used_k
    tau_from_k = tau_svd_unfold.kToTau(used_k)
    #SetTau( tau_from_k )
    #cov_matrix = GetCovMatrix(cov, 10, 1)
    #rho_from_tau_from_k = GetRho(cov_matrix, data)
    #print "tau from k", tau_from_k
    #print 'rho for tau from used k', rho_from_tau_from_k
    # create lists
    tau_values = []
    rho_values = []
    add_tau = tau_values.append
    add_rho = rho_values.append
#     for current_tau in drange(tau_0, tau_max, tau_step):
    for current_tau in get_tau_range( tau_0, tau_max, number_of_iterations ):
        SetTau( current_tau )
        cov_matrix = GetCovMatrix(cov, n_toy, 1)
        current_rho = GetRho(cov_matrix, data)
        
        add_tau( current_tau )
        add_rho( current_rho )
        
        if current_rho < minimal_rho:
            minimal_rho = current_rho
            optimal_tau = current_tau
    del unfolding
    print 'optimal tau = %.2f' % optimal_tau
    return optimal_tau, minimal_rho, tau_values, rho_values, to_return

def draw_global_correlation( tau_values, rho_values, tau, rho, channel, variable, tau_from_k ):
    global centre_of_mass
    plt.figure( figsize = ( 16, 16 ), dpi = 200, facecolor = 'white' )
    plt.plot( tau_values, rho_values )
    plt.xscale('log')
    plt.title(r'best $\tau$ from global correlation')
    plt.xlabel( r'$\tau$', fontsize = 40 )
    plt.ylabel( r'$\bar{\rho}(\tau)$', fontsize = 40 )
    ax = plt.axes()
    ax.annotate( r"$\tau = %.3g$" % tau,
            xy = ( tau, rho ), xycoords = 'data',
            xytext = ( tau*0.9, rho*1.15 ), textcoords = 'data',
            arrowprops = dict( arrowstyle = "fancy,head_length=0.4,head_width=0.4,tail_width=0.4",
                            connectionstyle = "arc3" ),
            size = 40,
            )
    
    ax.annotate( r"$\tau_{k} = %.3g$" % tau_from_k[0],
            xy = ( tau_from_k[0], tau_from_k[1] ), xycoords = 'data',
            xytext = ( tau_from_k[0], tau_from_k[1]*0.9 ), textcoords = 'data',
            arrowprops = dict( arrowstyle = "fancy,head_length=0.4,head_width=0.4,tail_width=0.4",
                            connectionstyle = "arc3" ),
            size = 40,
            )

    if use_data:
        plt.savefig( 'plots/unfolding_tests/%dTeV/tau_from_global_correlation_%s_channel_%s_DATA.png' % ( centre_of_mass, channel, variable ) )    
    else:
        plt.savefig( 'plots/unfolding_tests/%dTeV/tau_from_global_correlation_%s_channel_%s_MC.png' % ( centre_of_mass, channel, variable ) )

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
    fit_result_input = 'data/M3_angle_bl/13TeV/%(variable)s/fit_results/central/fit_results_%(channel)s_%(met_type)s.txt'
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
    used_k = 2
    set_root_defaults()
    use_data = True
    input_files = {
                   7 : '/hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_5th_draft/7TeV/unfolding/unfolding_TTJets_7TeV_asymmetric.root',
                   8 : '/hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_5th_draft/8TeV/unfolding/unfolding_TTJets_8TeV_asymmetric.root',
                   13 : 'unfolding/13TeV/unfolding_TTJets_13TeV_asymmetric.root',
                   }
    met_type = 'patType1CorrectedPFMet'
    
    # ST and HT have the problem of the overflow bin in the truth/response matrix
    # 7 input bins and 8 output bins (includes 1 overflow bin)
    variables = [ 
		# 'MET', 
		# 'WPT', 
		# 'MT' , 
		'ST',
		'HT'
		]
    centre_of_mass = 13
    measurement_config = XSectionConfig(centre_of_mass)
    ttbar_xsection = measurement_config.ttbar_xsection
    luminosity = measurement_config.luminosity
    input_file = File(input_files[centre_of_mass])
    
#     taus_from_global_correlaton = {}
#     taus_from_L_shape = {}
    for variable in variables:
#         taus_from_global_correlaton[channel] = {}
#         taus_from_L_shape[channel] = {}
        for channel in ['electron', 'muon']:
            if channel == 'electron':
                used_k = measurement_config.k_values_electron[variable]
            if channel == 'muon':
                used_k = measurement_config.k_values_muon[variable]
                
            print 'Doing variable"', variable, '" in', channel, 'channel'
        
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
                
            
            tau, rho, tau_values, rho_values, tau_from_k = get_tau_from_global_correlation( h_truth, h_measured, h_response, h_data )
            draw_global_correlation( tau_values, rho_values, tau, rho, channel, variable, tau_from_k )
            
            #tau, l_curve, x, y = get_tau_from_L_shape( h_truth, h_measured, h_response, h_data )
            #draw_l_shape( l_curve, tau, x, y, channel, variable )
        
