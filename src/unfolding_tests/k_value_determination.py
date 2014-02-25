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
from tools.Unfolding import Unfolding, get_unfold_histogram_tuple
from rootpy.io import File
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
import matplotlib
from copy import deepcopy
from tools.file_utilities import read_data_from_JSON
from tools.hist_utilities import value_error_tuplelist_to_hist
from config.variable_binning_8TeV import bin_edges
from rootpy import asrootpy

font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 28}

matplotlib.rc( 'font', **font )


def get_k_from_d_i( h_truth, h_measured, h_response, h_data = None ):
    k_start = h_measured.nbins()
#     method = 'RooUnfoldSvd'
    method = 'TSVDUnfold'
    unfolding = Unfolding( h_truth,
                                  h_measured,
                                  h_response,
                                  method = method,
                                  k_value = k_start )
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
        if d_i > 1:
            continue
        else:
            # first i when d_i < 0, is k
            # because i starts at 0
            best_k = i
            break
            
    return best_k, hist_d_i.clone()



def get_data_histogram( channel, variable, met_type ):
    fit_result_input = 'data/8TeV/%(variable)s/fit_results/central/fit_results_%(channel)s_%(met_type)s.txt'
    fit_results = read_data_from_JSON( fit_result_input % {'channel': channel, 'variable': variable, 'met_type':met_type} )
    fit_data = fit_results['TTJet']
    h_data = value_error_tuplelist_to_hist( fit_data, bin_edges[variable] )
    return h_data

def draw_d_i( d_i ):
    global variable
    plt.figure( figsize = ( 16, 16 ), dpi = 200, facecolor = 'white' )
    rplt.hist( d_i )
    plt.title( r'SVD unfolding $d_i$ for ' + variable )
    plt.xlabel( r'$i$', fontsize = 40 )
    plt.ylabel( r'$d_i$', fontsize = 40 )
    axes = plt.axes()
    axes.set_ylim( ymin = 0.1 )
    
    plt.yscale( 'log' )
    plt.axhline( y = 1, color = 'red' )
    plt.tight_layout()

    if use_data:
        plt.savefig( 'plots/k_from_d_i_%s_channel_%s_DATA.png' % ( channel, variable ) )    
    else:
        plt.savefig( 'plots/k_from_d_i_%s_channel_%s_MC.png' % ( channel, variable ) )

    
if __name__ == '__main__':
    from ROOT import gROOT
    gROOT.SetBatch( True )
    gROOT.ProcessLine( 'gErrorIgnoreLevel = 1001;' )
    use_data = False
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
                
            
            k, hist_di = get_k_from_d_i( h_truth, h_measured, h_response, h_data )
            print 'Best k-value for %s = %d' % ( variable, k )
            draw_d_i( hist_di )
