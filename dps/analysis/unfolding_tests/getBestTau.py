'''
Created on 20 Sep 2016

@author: Burns

run src/unfolding_tests/makeConfig.py first

This script creates, for each variable:
 - 1-P(Chi2|NDF) between data and refolded data for various tau 
 - Plots for data vs refolded data for each particular tau
 - Optimal tau value

What it needs:
 - the response matrix file
 - the data to be unfolded
   
usage:
    python getBestTau.py config.json
    # for 13 TeV in the visible phase space :
    python src/unfolding_tests/getBestTau.py config/unfolding/VisiblePS/*.json -n 100 --refold_plots
    -n = number of tau points
    --refold_plots = output some comparison plots for every tau (suggest few tau)
'''
# imports
from __future__ import division
from math import log10, pow
from argparse import ArgumentParser

# rootpy
from rootpy import asrootpy
from rootpy.io import File, root_open
# DailyPythonScripts
from dps.utils.ROOT_utils import set_root_defaults, get_histogram_from_file
from dps.config.xsection import XSectionConfig
from dps.utils.plotting import Histogram_properties
from dps.config import CMS
from dps.config.latex_labels import variables_latex
from ROOT import TUnfoldDensity, TUnfold, TCanvas, TPad, TMath, gROOT

from dps.config.variable_binning import reco_bin_edges_vis
from dps.utils.Unfolding import Unfolding, get_unfold_histogram_tuple, removeFakes
from dps.utils.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from dps.utils.hist_utilities import hist_to_value_error_tuplelist, value_error_tuplelist_to_hist

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# rc('font',**CMS.font)
# rc( 'text', usetex = True )
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 4096)
pd.set_option('display.max_rows', 65536)
pd.set_option('display.width', 1000)


class TauFinding(object):
    '''
        Class for storing input configuration, and for getting and storing response matrix histograms
    '''    
    def __init__( self, input_values ):
        self.centre_of_mass_energy = input_values['centre-of-mass energy']
        self.measurement_config = XSectionConfig( self.centre_of_mass_energy )
        self.channel = input_values['channel']
        self.variable = input_values['variable']
        self.ndf = len(reco_bin_edges_vis[self.variable])-1
        self.phaseSpace = input_values['phaseSpace']
        self.output_folder = input_values['output_folder']
        self.output_format = input_values['output_format']
        self.truth = input_values['truth']
        self.gen_vs_reco = input_values['gen_vs_reco']
        self.measured = input_values['measured']

        self.data = input_values['data']

        self.taus_to_test = []
        self.outpath = 'tables/taufinding/'

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
        visiblePS = self.phaseSpace

        t, m, r, f = get_unfold_histogram_tuple( 
            File(input_file),
            self.variable,
            self.channel,
            centre_of_mass = self.centre_of_mass_energy,
            ttbar_xsection=self.measurement_config.ttbar_xsection,
            luminosity=self.measurement_config.luminosity,
            load_fakes = True,
            visiblePS = visiblePS
        )

        self.h_truth = asrootpy ( t )
        self.h_response = asrootpy ( r )
        self.h_measured = asrootpy ( m )
        self.h_fakes = asrootpy ( f )
        self.h_refolded = None

        data_file = self.data['file']
        if data_file.endswith('.root'):
            self.h_data = get_histogram_from_file(self.data['histogram'], self.data['file'])
        elif data_file.endswith('.json') or data_file.endswith('.txt'):
            data_key = self.data['histogram']
            # assume configured bin edges
            edges = []
            edges = reco_bin_edges_vis[self.variable]

            json_input = read_data_from_JSON(data_file)

            if data_key == "": # JSON file == histogram
                self.h_data = value_error_tuplelist_to_hist(json_input, edges)
            else:
                self.h_data = value_error_tuplelist_to_hist(json_input[data_key], edges)
        else:
            print 'Unkown file extension', data_file.split('.')[-1]

            
    def get_histograms( self ):
        return self.h_truth, self.h_response, self.h_measured, self.h_data, self.h_fakes

def main():
    args, input_values_sets, json_input_files = parse_options()

    results = {}
    clear_old_df('tables/taufinding/')

    for input_values, json_file in zip( input_values_sets, json_input_files ):
        print '\nProcessing', json_file
        # Initialise the TauFinding class
        regularisation_settings = TauFinding( input_values )
        # Set additional elemtents
        regularisation_settings.taus_to_test = get_tau_list(args.n_ticks_in_log)
        if args.run_measured_as_data:
            regularisation_settings.taus_to_test = [0]
            regularisation_settings.h_data = regularisation_settings.h_measured

        variable = regularisation_settings.variable
        channel = regularisation_settings.channel
        com = regularisation_settings.centre_of_mass_energy
        print 'Variable = {0}, channel = {1}, sqrt(s) = {2}'.format(variable, channel, com)

        # Find the corresponding Chi2
        pd_chi2, pd_taus = get_chi2s_of_tau_range(regularisation_settings, args)

        # Write to file
        df_chi2 = chi2_to_df(pd_chi2, pd_taus, regularisation_settings) 

    # No point in trying to find best tau if it is given as 0...
    if args.run_measured_as_data: return

    # Have the dataframes now - albeit read to a file
    # Read in each one corresponding to their channel
    # Find the best tau and pront to screen
    # Maybe find way to include in previous loop (would requires three dataframes instantiations)
    for channel in ['electron', 'muon', 'combined']:
        path = regularisation_settings.outpath+'tbl_'+channel+'_tauscan.txt'
        df_chi2 = get_df_from_file(path)
        if df_chi2 is None: continue
        print '\n', "1 - P(Chi2|NDF)", '\n', df_chi2, '\n'

        # cutoff to be changed to 0.001 when able to
        best_taus = interpolate_tau(0.3, df_chi2)
        chi2_to_plots(df_chi2, regularisation_settings, channel)
        print_results_to_screen(best_taus, channel)
    return


def parse_options():
    '''
    parse the config jsons from command line and read the contents of the json files
    '''
    parser = ArgumentParser( __doc__ )
    parser.add_argument("in_files",
        nargs='*',
        help="List of the input files")
    parser.add_argument( "-t", "--test", 
        dest = "run_measured_as_data",
        action = "store_true", 
        help = "For debugging - run the measured distribution as data." ) 
    parser.add_argument( "-p", "--refold_plots", 
        dest = "run_refold_plots",
        action = "store_true", 
        help = "For debugging - output unfolded vs refolded for each tau" ) 
    parser.add_argument( "-n", "--n_ticks_in_log", 
        dest = "n_ticks_in_log",
        default = 10,
        type = int,
        help = "How many taus in the range do you want" ) 

    args = parser.parse_args()

    input_values_sets = []
    json_input_files = []
    add_set = input_values_sets.append
    add_json_file = json_input_files.append
    for arg in args.in_files:
        input_values = read_data_from_JSON( arg )
        add_set( input_values )
        add_json_file( arg )

    return args, input_values_sets, json_input_files

def clear_old_df(path):
    '''
    Delete any previous dataframe. (Code would append a new dataframe to file instead of replace)
    '''

    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
    return

def get_tau_list(logSpacing, logMin = log10(pow(10,-8)), logMax = log10(1)):
    '''
    Large scanning range from unity to 10^-8. Split into equal points based on log system 
    given the number of tau points to scan over.
    '''
    taus = []
    r = int(logMax - logMin)
    tau_test_range = [10**(logMax - i/float(logSpacing)) for i in range(r*logSpacing)]
    return tau_test_range

def get_chi2s_of_tau_range( regularisation_settings, args ):
    '''
        Takes each tau value, unfolds and refolds, calcs the chi2, the prob of chi2 given ndf (n_bins)
        and returns a dictionary of (1-P(Chi2|NDF)) for each tau
    '''
    h_truth, h_response, h_measured, h_data, h_fakes = regularisation_settings.get_histograms()
    if not args.run_measured_as_data : 
        h_data = removeFakes( h_measured, h_fakes, h_data )
    variable = regularisation_settings.variable
    taus = regularisation_settings.taus_to_test
    chi2_ndf = []

    for tau in taus:

        unfolding = Unfolding( 
            h_data, 
            h_truth, 
            h_measured, 
            h_response,
            fakes = None,#Fakes or no?
            method = 'TUnfold', 
            tau = tau
        )
        # Cannot refold without first unfolding
        h_unfolded_data = unfolding.unfold()
        h_refolded_data = unfolding.refold()
        # if test:
        regularisation_settings.h_refolded = h_refolded_data
        if args.run_refold_plots:
            plot_unfold_vs_refold(args, regularisation_settings, tau)

        data = np.array( [val for (val, err) in hist_to_value_error_tuplelist(h_data)] )
        ref = np.array( [val for (val, err) in hist_to_value_error_tuplelist(h_refolded_data)] )

        chi2 = unfolding.getUnfoldRefoldChi2()
        prob = TMath.Prob( chi2, regularisation_settings.ndf ) #bins-1?
        chi2_ndf.append(1-prob)
        # print( tau, chi2, prob, 1-prob )

    # Create pandas dictionary
    d_chi2 = {variable : pd.Series( chi2_ndf )}
    d_taus = {'tau' : pd.Series( taus )}
    return d_chi2, d_taus

def chi2_to_df(chi2, taus, regularisation_settings):
    '''
    Take the list of taus and chi2 for each variable and append to those already there
    '''
    variable = regularisation_settings.variable
    channel = regularisation_settings.channel
    outpath = regularisation_settings.outpath

    df_new = pd.DataFrame(chi2)
    df_tau = pd.DataFrame(taus)

    # better output path
    make_folder_if_not_exists(outpath)
    tblName = os.path.join(outpath,'tbl_{}_tauscan.txt'.format(channel))
    df_existing = get_df_from_file(tblName)

    if df_existing is not None:
        df_new = pd.concat([df_new, df_existing], axis=1)
        if 'tau' not in df_existing.columns:
            df_new = pd.concat([df_new, df_tau], axis=1)

    # overwrite old df with new one
    with open(tblName,'w') as f:
        df_new.to_string(f, index=True)
        f.write('\n')
        f.close()
    print('DataFrame {} written to file'.format(tblName))
    # return the new df
    return df_new

def get_df_from_file(p):
    '''
    Get the dataframe from the file
    '''
    df = None
    # check if the file exists and is not empty
    if os.path.exists(p) and os.stat(p).st_size != 0:
        with open(p,'r') as f:
            df = pd.read_table(f, delim_whitespace=True)
    else:
        print "Cannot find path : ", p
    return df

def chi2_to_plots(df_chi2, regularisation_settings, channel):
    '''
    Plot chi2 figures
    '''
    # variable = regularisation_settings.variable
    plot_outpath = regularisation_settings.outpath.replace('tables/', 'plots/') + 'tauscan/'
    make_folder_if_not_exists(plot_outpath)

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(1, 1, 1)
    ax1.set_xlim([pow(10,-5), 1])
    ax1.set_ylim([pow(10,-5), 1])
    for var in df_chi2.columns:
        if var == 'tau': continue

        plt.loglog(
            df_chi2['tau'],
            df_chi2[var],
            label = variables_latex[var],
        )

    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles, labels)
    ax1.set_xlabel('Regularisation Parameter \ensuremath{\\tau}')
    ax1.set_ylabel('\ensuremath{1-P(\\chi^{2}|NDF)}')

    pltName = os.path.join(plot_outpath,'{channel}_all_tauscan.pdf'.format(channel = channel))
    plt.show()
    plt.savefig(pltName) 
    print "Written plots to {plot_outpath}{channel}_all_tauscan.pdf".format(plot_outpath = plot_outpath, channel = channel)

    return

def interpolate_tau(cutoff, df_chi2):
    '''
    Interpolate to get best tau from tau scan
    1e-8 < tau < 1
    n    <  i  < 0

    chisq_lo    chisq cutoff        chisq_hi
    |------------|-------------------------|
           a                  b
    Find ratio a/(a+b)
    Interpolate to find best tau
    tau = tau_lo + ratio * (tau_hi - tau_lo)

                 |
                \|/
    |--------------------------------------|
    tau_lo      best tau            tau_hi
    '''
    best_tau = {}
    for variable in df_chi2.columns:
        if variable == 'tau': continue

        i=0
        for chisq in df_chi2[variable]:
            if chisq > cutoff:
                i+=1
                continue
            else:
                break
        if chisq > cutoff:
            print "{var} exceeds required cut".format(var=variable)
            # last i becomes out of range
            best_tau[variable] = df_chi2['tau'][i-1]
        else:
            chisq_lo = df_chi2[variable][i+1]
            chisq_hi = df_chi2[variable][i]
            ratio = (cutoff - chisq_lo) / (chisq_hi - chisq_lo)
            tau_lo = df_chi2['tau'][i+1]
            tau_hi = df_chi2['tau'][i]
            tau = tau_lo + ratio*(tau_hi - tau_lo)
            best_tau[variable] = tau
    return best_tau


def plot_unfold_vs_refold(args, regularisation_settings, tau):
    '''
    Plot the differences between the unfolded and refolded distributions

    TODO Include also with best tau - redo unfolding with best tau then come here
    '''
    tau = str(tau).replace('.', 'p')
    # data =  hist_to_value_error_tuplelist(regularisation_settings.h_data)
    # measured = hist_to_value_error_tuplelist(regularisation_settings.h_measured)
    variable = regularisation_settings.variable
    channel = regularisation_settings.channel
    plot_outpath = regularisation_settings.outpath.replace('tables/', 'plots/')+variable+'/'
    make_folder_if_not_exists(plot_outpath)
    outfile = plot_outpath+channel+'_unfold_refold_test_tau_'+tau+'.pdf'
    if args.run_measured_as_data:
        outfile = plot_outpath+channel+'_run_measured_as_data_tau_'+tau+'.pdf'

    c = TCanvas('c1','c1',600,400)
    c.SetFillColor(2);
    p1 = TPad("pad1", "p1",0.0,0.2,1.0,1.0,21)
    p2 = TPad("pad2", "p2",0.0,0.0,1.0,0.2,22)
    p1.SetFillColor(0);
    p2.SetFillColor(0);
    p1.Draw()
    p2.Draw()
    p1.cd()
    regularisation_settings.h_refolded.SetMarkerStyle(10);
    regularisation_settings.h_refolded.SetMarkerColor(4);
    # regularisation_settings.h_refolded.SetMarkerSize(10);
    regularisation_settings.h_refolded.Draw()
    regularisation_settings.h_data.SetFillColor(3);
    regularisation_settings.h_data.Draw("hist same");

    p2.cd()
    h_ratio = regularisation_settings.h_data.Clone()
    h_ratio.Divide(regularisation_settings.h_refolded)
    h_ratio.Draw()
    c.SaveAs(outfile)
    c.Delete()
    return

def print_results_to_screen(best_taus, channel):
    '''
        Print the results to the screen
        Can copy straight into config
    '''
    print "\nCHANNEL : ", channel
    for variable, tau in best_taus.iteritems():
        print '"{0}" : {1},'.format(variable, tau)
    return
        

if __name__ == '__main__':
    set_root_defaults( set_batch = True, msg_ignore_level = 3001 )
    main()
