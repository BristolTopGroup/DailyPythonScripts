'''
Created on 9 Mar 2015

@author: kreczko

This script creates
 - global correlation plots for tau (float) & k (int) regularisation parameters
 - optimal tau & k values
 - d_i plots with fits for k values
 
What it needs:
 - a set of four histograms:
   - truth: quantity at generator level
   - gen_vs_reco: quantity after selection, generated vs reco
   - measured: measured (reco) quantity including fakes (background)
   - data
For example config files, please have a look at config/unfolding/*.json
   
usage:
    python get_best_regularisation.py config.json
    # for full 7 + 8 TeV stuff:
    python src/unfolding_tests/get_best_regularisation.py config/unfolding/*.json -c
'''
# imports
from __future__ import division
from math import log10, pow
from optparse import OptionParser
import sys
# rootpy
from rootpy.io import File
# DailyPythonScripts
from dps.utils.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from dps.utils.Unfolding import Unfolding, get_unfold_histogram_tuple
#from dps.analysis.xsection.lib import get_unfold_histogram_tuple
from dps.utils.ROOT_utils import set_root_defaults, get_histogram_from_file
from dps.config.xsection import XSectionConfig, CMS
from dps.config.variable_binning import bin_edges_full, bin_edges_vis
from dps.utils.hist_utilities import value_error_tuplelist_to_hist
from dps.utils.table import PrintTable
import matplotlib.pyplot as plt
from dps.utils.plotting import Histogram_properties
from matplotlib import rc
from dps.config.latex_labels import variables_latex
rc('font',**CMS.font)
rc( 'text', usetex = True )

class RegularisationSettings():
    n_toy = int( 1000 )
    n_tau_scan_points = int( 100 )
    
    def __init__( self, input_values ):
        self.centre_of_mass_energy = input_values['centre-of-mass energy']
        self.measurement_config = XSectionConfig( self.centre_of_mass_energy )
        self.channel = input_values['channel']
        self.variable = input_values['variable']
        self.phaseSpace = input_values['phaseSpace']
        self.output_folder = input_values['output_folder']
        self.output_format = input_values['output_format']
        self.truth = input_values['truth']
        self.gen_vs_reco = input_values['gen_vs_reco']
        self.measured = input_values['measured']
        self.data = input_values['data']
        
        # optional
        if input_values.has_key('n_tau_scan_points'):
            self.n_tau_scan_points = input_values['n_tau_scan_points']
        if input_values.has_key('n_toy'):
            self.n_toy = input_values['n_toy']
            
        self.__set_unfolding_histograms__()
        
    def __set_unfolding_histograms__( self ):
        # at the moment only one file is supported for the unfolding input
        files = set( [self.truth['file'],
                     self.gen_vs_reco['file'],
                     self.measured['file']]
                    )
        if len( files ) > 1:
            print "Currently not supported to have different files for truth, gen_vs_reco and measured"
            sys.exit()
            
        input_file = files.pop()
        t, m, r, _ = get_unfold_histogram_tuple( File(input_file),
                                              self.variable,
                                              self.channel,
                                              centre_of_mass = self.centre_of_mass_energy,
                                              ttbar_xsection=self.measurement_config.ttbar_xsection,
                                              luminosity=self.measurement_config.luminosity,
                                            )
        self.h_truth = t
        self.h_response = r
        self.h_measured = m
        
        data_file = self.data['file']
        if data_file.endswith('.root'):
            self.h_data = get_histogram_from_file(self.data['histogram'], self.data['file'])
        elif data_file.endswith('.json') or data_file.endswith('.txt'):
            data_key = self.data['histogram']
            # assume configured bin edges
            edges = []
            if self.phaseSpace == 'FullPS':
                edges = bin_edges_full[self.variable]
            elif self.phaseSpace == 'VisiblePS':
                edges = bin_edges_vis[self.variable]
            json_input = read_data_from_JSON(data_file)
            if data_key == "": # JSON file == histogram
                self.h_data = value_error_tuplelist_to_hist(json_input, edges)
            else:
                self.h_data = value_error_tuplelist_to_hist(json_input[data_key], edges)
        else:
            print 'Unkown file extension', data_file.split('.')[-1]
            
    def get_histograms( self ):
        return self.h_truth, self.h_response, self.h_measured, self.h_data
    
def main():
    options, input_values_sets, json_input_files = parse_options()
    use_current_k_values = options.compare
    results = {}
    for input_values, json_file in zip( input_values_sets, json_input_files ):
        print 'Processing', json_file
        regularisation_settings = RegularisationSettings( input_values )
        variable = regularisation_settings.variable
        channel = regularisation_settings.channel
        com = regularisation_settings.centre_of_mass_energy
        if not results.has_key(com): results[com] = {}
        if not results[com].has_key(variable): results[com][variable] = {}
        print 'Variable = %s, channel = "%s", sqrt(s) = %d' % (variable, channel, com)

        k_results = get_best_k_from_global_correlation( regularisation_settings )
        tau_results = get_best_tau_from_global_correlation( regularisation_settings )
        results[com][variable][channel] = (k_results, tau_results)
        plot(regularisation_settings, (k_results, tau_results), 
                 use_current_k_values)
    table(results, use_current_k_values, options.style)

def parse_options():
    parser = OptionParser( __doc__ )
    parser.add_option( "-c", "--compare", dest = "compare", action = "store_true",
                      help = "Compare to current values (k vs tau)", default = False )
    parser.add_option( "-t", "--table-style", dest = "style", default = 'simple',
                      help = "Style for table printing: simple|latex|twiki (default = simple)" )

    ( options, args ) = parser.parse_args()
    
    input_values_sets = []
    json_input_files = []
    add_set = input_values_sets.append
    add_json_file = json_input_files.append
    for arg in args:
        input_values = read_data_from_JSON( arg )
        add_set( input_values )
        add_json_file( arg )

    return options, input_values_sets, json_input_files
            
def get_best_k_from_global_correlation( regularisation_settings ):
    '''
        returns optimal_k, k_values, tau_values, rho_values
         - optimal_k: k-value with lowest rho
         - minimal_rho: lowest rho value
         - k_values: all scanned k-values
         - tau_values: tau values for all scanned k-values
         - rho_values: rho values for all scanned k-values
    '''
    h_truth, h_response, h_measured, h_data = regularisation_settings.get_histograms()
    n_toy = regularisation_settings.n_toy
    # initialise variables
    optimal_k = 0
    minimal_rho = 9999
    n_bins = h_data.nbins()
    k_values = []
    tau_values = []
    rho_values = []
    # first calculate one set to get the matrices
    # tau = 0 is equal to k = nbins
    unfolding = Unfolding( h_truth,
                                  h_measured,
                                  h_response,
                                  method = 'RooUnfoldSvd',
                                  tau = 0.,  # no regularisation
                  k_value = -1, )
    unfolding.unfold( h_data )
    # get unfolding object
    svd_unfold = unfolding.Impl()
    # get covariance matrix
    cov = svd_unfold.get_data_covariance_matrix( h_data )
   
    # cache functions and save time in the loop
    SetTau = svd_unfold.SetTau
    GetCovMatrix = svd_unfold.GetUnfoldCovMatrix
    GetRho = svd_unfold.get_global_correlation
    kToTau = svd_unfold.kToTau
    add_k = k_values.append
    add_tau = tau_values.append
    add_rho = rho_values.append
    
    
    # now lets loop over all possible k-values
    for k in range( 2, n_bins + 1 ):
        tau_from_k = kToTau( k )
        SetTau( tau_from_k )
        cov_matrix = GetCovMatrix( cov, n_toy, 1 )
        rho = GetRho( cov_matrix, h_data )
        add_k( k )
        add_tau( tau_from_k )
        add_rho( rho )
        
        if rho < minimal_rho:
            optimal_k = k
            minimal_rho = rho
    
    return optimal_k, minimal_rho, k_values, tau_values, rho_values
     
     
def get_best_tau_from_global_correlation( regularisation_settings ):
    '''
        returns optimal_tau, tau_values, rho_values
         - optimal_tau: k-value with lowest rho
         - minimal_rho: lowest rho value
         - tau_values: all scanned tau values
         - rho_values: rho values for all scanned tau-values
    '''
    h_truth, h_response, h_measured, h_data = regularisation_settings.get_histograms()
    n_toy = regularisation_settings.n_toy   
    number_of_iterations = regularisation_settings.n_tau_scan_points
    tau_min = 0.1
    tau_max = 1000
    optimal_tau = 0
    minimal_rho = 9999
    tau_values = []
    rho_values = []

    # first calculate one set to get the matrices
    # tau = 0 is equal to k = nbins
    unfolding = Unfolding( h_truth,
                                  h_measured,
                                  h_response,
                                  method = 'RooUnfoldSvd',
                                  tau = 0.,  # no regularisation
                  k_value = -1, )
    unfolding.unfold( h_data )
    # get unfolding object
    svd_unfold = unfolding.Impl()
    # get covariance matrix
    cov = svd_unfold.get_data_covariance_matrix( h_data )
   
    # cache functions and save time in the loop
    SetTau = svd_unfold.SetTau
    GetCovMatrix = svd_unfold.GetUnfoldCovMatrix
    GetRho = svd_unfold.get_global_correlation
    add_tau = tau_values.append
    add_rho = rho_values.append
    
    # now lets loop over all tau-values in range
    for current_tau in get_tau_range(tau_min, tau_max, number_of_iterations):
        SetTau( current_tau )
        cov_matrix = GetCovMatrix(cov, n_toy, 1)
        current_rho = GetRho(cov_matrix, h_data)
        
        add_tau( current_tau )
        add_rho( current_rho )
        
        if current_rho < minimal_rho:
            minimal_rho = current_rho
            optimal_tau = current_tau
    
    print 'Best tau for',regularisation_settings.channel,':',optimal_tau       
    return optimal_tau, minimal_rho, tau_values, rho_values

def get_tau_range( tau_min, tau_max, number_of_points ):
    # Use 3 scan points minimum
    if number_of_points < 3:
        number_of_points = 3
        
    if tau_min == 0:
        tau_min = 0.1

    # Find the scan points
    # Use equidistant steps on a logarithmic scale
    step = ( log10( tau_max ) - log10( tau_min ) ) / ( number_of_points - 1 );
    for i in range ( number_of_points ):
        yield pow( 10., ( log10( tau_min ) + i * step ) );

def plot(regularisation_settings, results, use_current_k_values = False):
    variable = regularisation_settings.variable
    channel = regularisation_settings.channel
    com = regularisation_settings.centre_of_mass_energy
    output_folder = regularisation_settings.output_folder
    output_format = regularisation_settings.output_format
    measurement_config = XSectionConfig(com)
    
    name = 'reg_param_from_global_correlation_%s_channel_%s' % (channel, variable)
    hp = Histogram_properties()
    hp.name = name
    hp.x_axis_title = r'log($\tau$)'
    hp.y_axis_title = r'$\bar{\rho}(\tau)$'
    hp.title = r'global correlation for $%s$, %s channel, $\sqrt{s} = %d$ TeV'
    hp.title = hp.title % (variables_latex[variable], channel, com)
    
    k_results, tau_results = results    
    optimal_tau, minimal_rho, tau_values, rho_values = tau_results
    optimal_k, optimal_k_rho, k_values, k_tau_values, k_rho_values = k_results
    
    plt.figure( figsize = ( 16, 16 ), dpi = 200, facecolor = 'white' )
    plt.plot( tau_values, rho_values )
    plt.plot( k_tau_values, k_rho_values, 'ro' )
    
    plt.title(hp.title, CMS.title)
    plt.xlabel( hp.x_axis_title, CMS.x_axis_title )
    plt.ylabel( hp.y_axis_title, CMS.y_axis_title )
    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )
    
    ax = plt.axes()

    current_k, closest_tau, _, _ = get_k_tau_set(measurement_config, channel, variable, results) 
    current_k_rho = k_rho_values[k_values.index(current_k)]
    
    # first best k
    tau_index = k_values.index(optimal_k)
    closest_tau_best_k = k_tau_values[tau_index]
    ax.annotate( r"$\tau = %.2g$" % optimal_tau,
            xy = ( optimal_tau, minimal_rho ), xycoords = 'data',
            xytext = ( optimal_tau*0.9, minimal_rho*1.15 ), textcoords = 'data',
            bbox=dict(boxstyle="round4", fc="w"),
            arrowprops = dict( arrowstyle = "fancy,head_length=0.4,head_width=0.4,tail_width=0.4",
                            connectionstyle = "arc3" ),
            size = 40,
            )
    
    ax.annotate( r"$\tau(k_b = %d) = %.2g$" % ( optimal_k, closest_tau_best_k ),
                xy = ( closest_tau_best_k, optimal_k_rho ), xycoords = 'data',
                xytext = ( closest_tau_best_k * 10, optimal_k_rho ), textcoords = 'data',
                bbox=dict(boxstyle="round4", fc="w"),
                arrowprops = dict( arrowstyle = "<-",
                                connectionstyle = "arc3", lw = 3 ),
                size = 40,
                )
    # then current k
    if use_current_k_values:
        ax.annotate( r"$\tau(k_c = %d) = %.2g$" % (current_k, closest_tau),
                xy = ( closest_tau, current_k_rho ), xycoords = 'data',
                xytext = ( closest_tau, current_k_rho*0.9 ), textcoords = 'data',
                bbox=dict(boxstyle="round4", fc="w"),
                arrowprops = dict( arrowstyle = "<-",
                                connectionstyle = "arc3", lw = 3 ),
                size = 40,
                )
    
    plt.xscale('log')
    make_folder_if_not_exists(output_folder)
    for f in output_format:
        plt.savefig( output_folder + '/' + hp.name + '.' + f )
    
    
    
def table(result_dict, use_current_k_values = False, style = 'simple'):
    '''
        result_dict has the form
        {
            centre-of-mass energy : 
            {
                variable : 
                {
                    channel : (k_results,  tau_results)
                }
            }
        }
        <reg>_results are of the form:
            best_<reg>, best_<reg>_rho, <reg>s, rhos
    '''
    for com in result_dict.keys():
        # step 1: group the results by centre of mass energy
        headers = []
        if use_current_k_values:
            headers = ['Variable', 'current k', 'closest tau', 'best tau', 'best k']
        else:
            headers = ['Variable', 'best k', 'rho (best k)', 'best tau', 'rho (best tau)']
        data = []
        configOutputElectron = {}
        configOutputMuon = {}
        configOutputCombined = {}
        measurement_config = XSectionConfig(com)
        for variable in result_dict[com].keys():
            has_both_channels = len(result_dict[com][variable]) == 3
            # step 2: if have electron and muon channel, group them: electron (muon)
            if has_both_channels:
                electron_results = result_dict[com][variable]['electron']
                muon_results = result_dict[com][variable]['muon']
                combined_results = result_dict[com][variable]['combined']
                
                configOutputElectron[variable] = electron_results[1][0]
                configOutputMuon[variable] = muon_results[1][0]
                configOutputCombined[variable] = combined_results[1][0]
                entry = []
                if use_current_k_values:
                    electron_set = get_k_tau_set(measurement_config, 'electron',
                                                variable, electron_results)
                    muon_set = get_k_tau_set(measurement_config, 'muon',
                                                variable, muon_results)
                    combined_set = get_k_tau_set(measurement_config, 'combined',
                                                variable, combined_results)
                    entry = [variable, 
                             '%d (%d)' % (electron_set[0], muon_set[0], combined_set[0]),
                             '%.1f (%.1f)' % (electron_set[1], muon_set[1], combined_set[1]),
                             '%.1f (%.1f)' % (electron_set[2], muon_set[2], combined_set[2]),
                             '%d (%d)' % (electron_set[3], muon_set[3], combined_set[3]), 
                             ]
                else:
                    entry = [variable, 
                             '%d %d %d' % (electron_results[0][0], muon_results[0][0], combined_results[0][0]),
                             '%.1f %.1f %.1f' % (electron_results[0][1], muon_results[0][1], combined_results[0][1]),
                             '%.1f %.1f %.1f' % (electron_results[1][0], muon_results[1][0], combined_results[1][0]),
                             '%.1f %.1f %.1f' % (electron_results[1][1], muon_results[1][1], combined_results[1][1]),    
                             ]
                    
                data.append(entry)
            else:
                channel = result_dict[com][variable].keys()[0]
                results = result_dict[com][variable][channel]
                print channel
                if channel == 'electron':
                    configOutputElectron[variable] = results[1][0]
                elif channel == 'muon':
                    configOutputMuon[variable] = results[1][0]
                else :
                    configOutputCombined[variable] = results[1][0]

                if use_current_k_values:
                    result_set = get_k_tau_set(measurement_config, channel,
                                                variable, results)
                    entry = [variable, 
                             '%d' % result_set[0],
                             '%.1f' % result_set[1],
                             '%.1f' % result_set[2],
                             '%d' % result_set[3],    
                             ]
                else:
                    entry = [variable, 
                             '%d' % results[0][0],
                             '%.1f' % results[0][1],
                             '%.1f' % results[1][0],
                             '%.1f' % results[1][1],    
                             ]
                    
                data.append(entry)
        
        print '\nOutput for __init__\n'
        print configOutputElectron
        print configOutputMuon
        print configOutputCombined
        print 'Electron'
        for var in configOutputElectron:
            print '"%s" : %s,' % (var, configOutputElectron[var])
        print '\n'
        print 'Muon'
        for var in configOutputMuon:
            print '"%s" : %s,' % (var, configOutputMuon[var])
        print '\n'
        print 'Combined'
        for var in configOutputCombined:
            print '"%s" : %s,' % (var, configOutputCombined[var])
        print '\n'
        table = PrintTable(data, headers)
        
        print 'Printing table for sqrt(s) = %d TeV' % com
        if style == 'simple':
            print table.simple()
        elif style == 'latex':
            print table.latex()
        elif style == 'twiki':
            print table.twiki()
        else:
            print 'unknown printing style "%s"' % style

def get_k_tau_set(config, channel, variable, results):
    k_results, tau_results = results
    optimal_tau, _, tau_values, rho_values = tau_results
    optimal_k, _, k_values, _, k_rho_values = k_results

    current_k = config.k_values_electron[variable]
    rho_index = k_values.index(current_k)
    current_k_rho = k_rho_values[rho_index]
    
    tau_index = min(range(len(rho_values)), 
                    key = lambda i: abs(rho_values[i] - current_k_rho))
    closest_tau = tau_values[tau_index]
    
    return current_k, closest_tau, optimal_tau, optimal_k
    
    
if __name__ == '__main__':
    set_root_defaults()
    main()
