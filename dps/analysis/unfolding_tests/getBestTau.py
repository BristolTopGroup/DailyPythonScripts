'''
Created on 20 Sep 2016

@author: Burns

run dps/analysis/unfolding_tests/makeConfig.py first

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
    python dps/analysis/unfolding_tests/getBestTau.py config/unfolding/VisiblePS/*.json -n 100 -t 0.005 --refold_plots --test
    -n = number of tau points
    -t = specific tau value
    --refold_plots = output some comparison plots for every tau (suggest few tau)
    --test = runs the measured distribution as data. Should return P(Chi2|NDF) of 0 i.e. exact
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
from ROOT import TUnfoldDensity, TUnfold, TCanvas, TPad, TLegend, TMath, gROOT, TRandom3

from dps.config.variable_binning import reco_bin_edges_vis
# , gen_bin_edges_vis
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
        files = set( 
            [self.truth['file'],
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

        # Initialise the TauFinding class
        regularisation_settings = TauFinding( input_values )
        variable = regularisation_settings.variable
        channel = regularisation_settings.channel
        com = regularisation_settings.centre_of_mass_energy

        # Specific channel or variable
        if args.ch:
            if args.ch not in channel: continue
        if args.var:
            if args.var not in variable: continue

        print 'Running for:'
        print 'Variable = {0}, channel = {1}, sqrt(s) = {2}'.format(variable, channel, com)

        # Set additional elements
        regularisation_settings.taus_to_test = get_tau_values(args.n_tau_in_log)
        isTauCalculator = True

        # Specific unfolding tests go here
        if args.specific_tau is not None:
            regularisation_settings.taus_to_test = [args.specific_tau]
            df_chi2_specific_tau = get_chi2(regularisation_settings, args)
            isTauCalculator = False

        if args.run_measured_as_data:
            regularisation_settings.taus_to_test = [0]
            regularisation_settings.h_data = regularisation_settings.h_measured
            df_chi2_measured = get_chi2(regularisation_settings, args)
            isTauCalculator = False

        if args.run_smeared_measured_as_data:
            regularisation_settings.taus_to_test = [0]
            regularisation_settings.h_data = regularisation_settings.h_measured
            h_data = hist_to_value_error_tuplelist(regularisation_settings.h_data)
            h_data_varied = [(return_rnd_Poisson(val),return_rnd_Poisson(err)) for val, err in h_data ]
            h_data_varied = value_error_tuplelist_to_hist(h_data_varied, reco_bin_edges_vis[variable])
            regularisation_settings.h_data = h_data_varied
            df_chi2_smeared = get_chi2(regularisation_settings, args, smearing_test=True)
            isTauCalculator = False
        
        # Dont need to calculate chi2 for given tau tests
        if not isTauCalculator: continue

        # Find Chi2 for each tau and write to file
        df_chi2 = get_chi2(regularisation_settings, args)

    # Dont need to calculate tau for given tests
    if not isTauCalculator: sys.exit()

    # Have the dataframes now - albeit read to a file
    # Read in each one corresponding to their channel
    # Find the best tau and print to screen
    for channel in ['electron', 'muon', 'combined']:
        chi2_cut = 0.005
        path = regularisation_settings.outpath+'tbl_'+channel+'_tauscan.txt'
        df_chi2 = get_df_from_file(path)
        if df_chi2 is None: continue
        print '\n', "1 - P(Chi2|NDF)", '\n', df_chi2, '\n'

        # cutoff to be changed to 0.001 when able to
        best_taus = interpolate_tau(chi2_cut, df_chi2)
        chi2_to_plots(args, df_chi2, regularisation_settings, chi2_cut, channel)
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
    parser.add_argument( "--measured_test", 
        dest = "run_measured_as_data",
        action = "store_true", 
        help = "For debugging. Run the measured distribution as data." ) 
    parser.add_argument( "--smeared_test", 
        dest = "run_smeared_measured_as_data",
        action = "store_true", 
        help = "Test. Run (poisson) smeared measured distribution as data" ) 
    parser.add_argument( "-p", "--refold_plots", 
        dest = "create_refold_plots",
        action = "store_true", 
        help = "Plot. Produce unfolded vs refolded plot for each tau run" ) 
    parser.add_argument( "-n", "--n_tau_in_log", 
        dest = "n_tau_in_log",
        default = 10,
        type = int,
        help = "How many taus in the range do you want" ) 
    parser.add_argument( "-t", "--tau", 
        dest = "specific_tau",
        default = None,
        type = float,
        help = "How many taus in the range do you want" ) 
    parser.add_argument( "-u", "--unfolded_binning", 
        dest = "unfolded_binning",
        action = "store_true", 
        help = "Run the tau scans for unfolded (gen) binning" ) 
    parser.add_argument( "-c", "--channel", 
        dest = "ch",
        default = None, 
        type = str,
        help = "Which channel to run over" ) 
    parser.add_argument( "-v", "--variable", 
        dest = "var",
        default = None, 
        type = str,
        help = "Which varibale to run over" ) 
    args = parser.parse_args()

    if args.unfolded_binning:
        print "Calculating the chi2 in the unfolded (gen) binning scheme"

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

def get_tau_values(logSpacing, logMin = log10(pow(10,-16)), logMax = log10(1)):
    '''
    Large scanning range from 1 to 10^-16. Split into equal points based on log system 
    given the number of tau points to scan over.
    '''
    r = int(logMax - logMin)
    tau_values = [10**(logMax - i/float(logSpacing)) for i in range(r*logSpacing)]
    return tau_values

def get_chi2( regularisation_settings, args, smearing_test=False ):
    '''
        Takes each tau value, unfolds and refolds, calcs the chi2, the prob of chi2 given ndf (n_bins)
        and returns a dictionary of (1-P(Chi2|NDF)) for each tau
        For measured test where we only worry about tau=0 outputs tau variables to data frame (+smeared measured values)
    '''
    h_truth, h_response, h_measured, h_data, h_fakes = regularisation_settings.get_histograms()

    # Dont remove any fakes if we are using the true mc distribution
    if not args.run_measured_as_data or not args.run_smeared_measured_as_data: 
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

        # print("Data")
        # print (hist_to_value_error_tuplelist(h_data))
        # print("Unfolded Data")
        # print (hist_to_value_error_tuplelist(h_unfolded_data))
        # print("Refolded Data")
        # print (hist_to_value_error_tuplelist(h_refolded_data))

        regularisation_settings.h_refolded = h_refolded_data
        ndf = regularisation_settings.ndf

        if args.unfolded_binning:
            unfolding.refolded_data = h_refolded_data.rebinned(2)
            unfolding.data = h_data.rebinned(2)
            ndf = int(regularisation_settings.ndf / 2)
            regularisation_settings.h_refolded = unfolding.refolded_data
            regularisation_settings.h_data = unfolding.data
        if args.create_refold_plots:
            plot_data_vs_refold(args, regularisation_settings, tau)

        # Calculate the chi2 between refold and unfold 
        chi2 = unfolding.getUnfoldRefoldChi2()
        # Calculate the Prob chi2 given NDF
        prob = TMath.Prob( chi2, ndf ) 
        # 1-P(Chi2|NDF)
        chi2_ndf.append(1-prob)
        # print( tau, chi2, prob, 1-prob )

    # Create tau and Chi2 dictionary
    d_chi2 = {variable : pd.Series( chi2_ndf )}
    d_taus = {'tau' : pd.Series( taus )}

    if smearing_test: 
        d_tau_vars = {
            variable : {
                'Tau' : tau,
                'Chi2' : chi2,
                'Prob' : prob,
                '1-Prob' : 1-prob,
            }
        }
        df_unfold_tests = tau_vars_to_df(d_tau_vars, regularisation_settings)
        return df_unfold_tests

    df_chi2 = chi2_to_df(d_chi2, d_taus, regularisation_settings )
    return df_chi2

def tau_vars_to_df(tau_vars, regularisation_settings):
    '''
    Take the list of taus and chi2 for each variable and append to those already there
    '''
    variable = regularisation_settings.variable
    channel = regularisation_settings.channel
    outpath = regularisation_settings.outpath

    df_new = pd.DataFrame(tau_vars)

    make_folder_if_not_exists(outpath)
    tblName = os.path.join(outpath,'tbl_{}_tauscan_smeared.txt').format(channel)
    df_existing = get_df_from_file(tblName)

    if df_existing is not None:
        df_new = pd.concat([df_new, df_existing], axis=1)

    # overwrite old df with new one
    with open(tblName,'w') as f:
        df_new.to_string(f, index=True)
        f.write('\n')
        f.close()
    print('DataFrame {} written to file'.format(tblName))
    # return the new df
    return df_new

def chi2_to_df(chi2, taus, regularisation_settings, appendage=''):
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
    tblName = os.path.join(outpath,'tbl_{}_tauscan{}.txt'.format(channel, appendage))
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
    # if os.path.exists(p) and os.stat(p).st_size != 0:
    if(os.path.exists(p)):
        with open(p,'r') as f:
            df = pd.read_table(f, delim_whitespace=True)
    else:
        print "Cannot find path : ", p
    return df

def chi2_to_plots(args,df_chi2, regularisation_settings, chi2_cut, channel):
    '''
    Plot chi2 figures
    '''
    plot_outpath = regularisation_settings.outpath.replace('tables/', 'plots/') + 'tauscan/'
    make_folder_if_not_exists(plot_outpath)

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(1, 1, 1)
    ax1.set_xlim([pow(10,-6), 1])
    ax1.set_ylim([pow(10,-6), 1])
    for var in df_chi2.columns:
        if var == 'tau': continue

        # Plot tau distributions for each variable
        plt.loglog(
            df_chi2['tau'],
            df_chi2[var],
            label = variables_latex[var],
        )
    # Plot current chi2 cutoff value
    plt.axhline(y=chi2_cut, color='black', linestyle='dashed')

    # Plot legend
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles, labels, loc=4)

    # Plot axis titles
    ax1.set_xlabel('Regularisation Parameter \ensuremath{\\tau}')
    ax1.set_ylabel('\ensuremath{1-P(\\chi^{2}|NDF)}')

    # Save plot
    pltName = os.path.join(plot_outpath,'{channel}_all_tauscan.pdf'.format(channel = channel))
    if args.unfolded_binning:
        pltName = pltName.replace('.pdf', '_unf_binning.pdf')
    fig1.savefig(pltName) 
    print "Written plots to {plot_outpath}{pltName}".format(plot_outpath = plot_outpath, pltName = pltName)
    return

def plot_data_vs_refold(args, regularisation_settings, tau):
    '''
    Plot the differences between the unfolded and refolded distributions

    TODO Include also with best tau - redo unfolding with best tau then come here
    '''
    from ROOT import gStyle

    variable = regularisation_settings.variable
    channel = regularisation_settings.channel
    plot_outpath = regularisation_settings.outpath.replace('tables/', 'plots/')+'tauscan/taus/'
    make_folder_if_not_exists(plot_outpath)

    # tau as string name for output
    tau = str(tau).replace('.', 'p')

    outfile = plot_outpath+'data_vs_refold_'+channel+'_'+variable+'_tau_'+tau+'.pdf'
    if args.run_measured_as_data:
        outfile = plot_outpath+'measured_vs_refold_'+channel+'_'+variable+'_tau_'+tau+'.pdf'
    if args.run_smeared_measured_as_data:
        outfile = plot_outpath+'smeared_vs_refold_'+channel+'_'+variable+'_tau_'+tau+'.pdf'
    if args.unfolded_binning:
        outfile = outfile.replace('.pdf', '_unf_binning.pdf')

    c = TCanvas('c1','c1',1000,800)
    gStyle.SetOptStat(0)

    p1 = TPad("pad1", "p1",0.0,0.2,1.0,1.0,21)
    p1.SetFillColor(0);
    p1.Draw()
    p2 = TPad("pad2", "p2",0.0,0.0,1.0,0.2,22)
    p2.SetFillColor(0);
    p2.Draw()

    p1.cd()
    regularisation_settings.h_data.SetTitle("Data vs Refolded Data;;NEvents")
    regularisation_settings.h_data.Draw()

    regularisation_settings.h_refolded.SetLineColor(2)
    regularisation_settings.h_refolded.Draw("same")

    leg1 = TLegend(0.7, 0.8, 0.9, 0.9)
    leg1.SetLineColor(0)
    leg1.SetFillColor(0)
    leg1.AddEntry(regularisation_settings.h_data, "Data")
    leg1.AddEntry(regularisation_settings.h_refolded, "Refolded Data")
    leg1.Draw()

    p2.cd()
    h_ratio = regularisation_settings.h_data.Clone()
    h_ratio.Divide(regularisation_settings.h_refolded)
    h_ratio.SetTitle(";"+variable+";")
    h_ratio.SetLineColor(1);
    h_ratio.Draw()

    c.SaveAs(outfile)
    c.Delete()
    print "Written plots to {outfile}".format(outfile = outfile)
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
        
def return_rnd_Poisson(mu):
    '''
    Returning a random poisson number
            lambda^{k} . e^{-lambda}
    Po() =  ------------------------
                       k!

    k       : events
    lambda  : expected separation
    '''
    gRandom = TRandom3()
    gRandom.SetSeed(0)
    # Cache for quicker running
    poisson = gRandom.Poisson
    rnd_po = poisson( mu )
    return rnd_po

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

if __name__ == '__main__':
    set_root_defaults( set_batch = True, msg_ignore_level = 3001 )
    main()
