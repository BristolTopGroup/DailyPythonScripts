'''
Created on 9 Mar 2015

@author: kreczko

This script creates, for each variable:
 - global correlation as function of log tau
 - optimal tau value

 
What it needs:
 - the response matrix file
 - the data to be unfolded
   
usage:
    python get_best_regularisation.py config.json
    # for 13 TeV in the visible phase space :
    python src/unfolding_tests/get_best_regularisation_TUnfold.py config/unfolding/VisiblePS/*.json
'''
# imports
from __future__ import division
from math import log10, pow
from optparse import OptionParser
import sys
# rootpy
from rootpy.io import File
from rootpy.plotting import Graph, Canvas
from rootpy.matrix import Matrix
# DailyPythonScripts
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from tools.Unfolding import Unfolding, get_unfold_histogram_tuple, removeFakes
#from src.cross_section_measurement.lib import get_unfold_histogram_tuple
from tools.ROOT_utils import set_root_defaults, get_histogram_from_file
from config import XSectionConfig
from config.variable_binning import reco_bin_edges_vis
from tools.hist_utilities import value_error_tuplelist_to_hist
import matplotlib.pyplot as plt
from tools.plotting import Histogram_properties
from matplotlib import rc
from config import CMS
from config.latex_labels import variables_latex
from ROOT import TGraph, TSpline3, Double, TUnfoldDensity, TUnfold, TDecompSVD, TMatrixD, TCanvas, gROOT
from numpy.linalg import svd
from rootpy import asrootpy

rc('font',**CMS.font)
rc( 'text', usetex = True )

class RegularisationSettings(object):
    '''
        Class for storing input configuration, and for getting and storing response matrix histograms
    '''
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
        if 'n_tau_scan_points' in input_values:
            self.n_tau_scan_points = input_values['n_tau_scan_points']
        if 'n_toy' in input_values:
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

        visiblePS = False
        if self.phaseSpace == 'VisiblePS':
            visiblePS = True

        t, m, r, f = get_unfold_histogram_tuple( File(input_file),
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
    options, input_values_sets, json_input_files = parse_options()
    results = {}
    for input_values, json_file in zip( input_values_sets, json_input_files ):
        print 'Processing', json_file
        regularisation_settings = RegularisationSettings( input_values )
        variable = regularisation_settings.variable
        channel = regularisation_settings.channel
        com = regularisation_settings.centre_of_mass_energy
        if not results.has_key(com): results[com] = {}
        if not results[com].has_key(channel): results[com][channel] = {}
        if not results[com][channel].has_key(variable): results[com][channel][variable] = {}
        print 'Variable = {0}, channel = {1}, sqrt(s) = {2}'.format(variable, channel, com)

        h_truth, h_response, h_measured, h_data, h_fakes = regularisation_settings.get_histograms()

        unfolding = Unfolding( 
                                h_data, 
                                h_truth, 
                                h_measured, 
                                h_response,
                                fakes = None,
                                method = 'TUnfold', 
                                k_value = -1, 
                                tau = 0. 
                            )

        # get_condition_number( unfolding.unfoldObject )
        tau_results = get_best_tau( regularisation_settings )
        results[com][channel][variable] = (tau_results)
    print_results_to_screen(results)

def parse_options():
    parser = OptionParser( __doc__ )

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

def tau_from_L_curve( unfoldingObject ):
    '''
    Get best tau via l curve method
    Not tested
    '''
    lCurve = TGraph()
    logTauX = TSpline3()
    logTauY = TSpline3()
    iBest = unfoldingObject.ScanLcurve(500, 0., 0., lCurve, logTauX, logTauY);

    # Additional info, plots
    t = Double(0)
    x = Double(0)
    y = Double(0)
    logTauX.GetKnot(iBest,t,x);
    logTauY.GetKnot(iBest,t,y);

    bestLcurve = Graph(1);
    bestLcurve.SetPoint(1,x,y);
    lCurve.SetMarkerColor(600)
    lCurve.SetMarkerSize(1)
    lCurve.SetMarkerStyle(5)

    # lCurve.Draw("AP");
    bestLcurve.markercolor = 'red'
    # bestLcurve.Draw("*");

    return unfoldingObject.GetTau()

def tau_from_scan( unfoldingObject, regularisation_settings ):
    variable = regularisation_settings.variable

    # Plots that get outputted by the scan
    lCurve = TGraph()
    scanResult = TSpline3()
    d = 'signal'
    a = ''

    # Parameters of scan
    # Number of points to scan, and min/max tau
    nScan = 1000
    minTau = 1.E-6
    maxTau = 1.E-0

    if variable == 'abs_lepton_eta':
        minTau = 1.E-8
        maxTau = 1.E-3
    elif variable == 'lepton_pt':
        minTau = 1.E-6
        maxTau = 1.E-2
    elif variable == 'NJets':
        minTau = 1.E-6
        maxTau = 1.E-2

    # Scan is performed here    
    iBest = unfoldingObject.ScanTau(nScan, minTau, maxTau, scanResult, TUnfoldDensity.kEScanTauRhoSquareAvg);

    # Plot the scan result
    # Correlation as function of log tau
    canvas = TCanvas()
    scanResult.SetMarkerColor(600)
    scanResult.SetMarkerSize(1)
    scanResult.SetMarkerStyle(5)
    scanResult.Draw('LP')

    # Add point corresponding to optimum tau
    t = Double(0)
    x = Double(0)
    scanResult.GetKnot(iBest,t,x);
    bestTau = Graph(1)
    bestTau.SetPoint(1,t,x)
    bestTau.markercolor = 'red'
    bestTau.SetMarkerSize(1.25)
    bestTau.Draw('*')

    # Write to file
    output_dir = regularisation_settings.output_folder
    make_folder_if_not_exists(output_dir)
    canvas.SaveAs(output_dir + '/{0}.png'.format(variable) )

    return unfoldingObject.GetTau()

def get_best_tau( regularisation_settings ):
    '''
        returns TODO
         - optimal_tau: TODO
    '''
    h_truth, h_response, h_measured, h_data, h_fakes = regularisation_settings.get_histograms()
    variable = regularisation_settings.variable

    h_data = removeFakes( h_measured, h_fakes, h_data )

    unfolding = Unfolding( 
                            h_data, 
                            h_truth, 
                            h_measured, 
                            h_response,
                            fakes = None,
                            method = 'TUnfold', 
                            k_value = -1, 
                            tau = -1
                        )

    # bestTau_LCurve = tau_from_L_curve( unfolding.unfoldObject )
    # unfolding.tau = bestTau_LCurve

    bestTauScan = tau_from_scan( unfolding.unfoldObject, regularisation_settings )
    unfolding.tau = bestTauScan

    return unfolding.tau

def get_condition_number( unfoldingObject ):

    probMatrix = unfoldingObject.GetProbabilityMatrix( 'ProbMatrix')
    # probabilityMatrix = unfoldingObject.GetProbabilityMatrix( probMatrix, TUnfold.kHistMapOutputVert)
    probMatrix.Print()
    # probMatrix.Draw('COLZ')
    raw_input()
    nBins = probMatrix.GetNbinsX()
    m = TMatrixD( nBins, nBins )
    for xbin in range(1, probMatrix.GetNbinsX() ):
        for ybin in range(1,probMatrix.GetNbinsY() ):
            m[xbin, ybin] = probMatrix.GetBinContent( xbin, ybin)
    svd = TDecompSVD( m )
    svd.Decompose()
    svd.Print()
    sig = svd.GetSig()
    sig.Print()
    nSig = len(sig)
    sigmaMax = sig[0]
    sigmaMin = sig[nSig-2]
    condition = sigmaMax / max(0,sigmaMin)
    # condition = 1
    print condition
    return condition

def print_results_to_screen(result_dict):
    '''
        Print the results to the screen
        Can copy straight into config
    '''

    for com in result_dict.keys():
        for channel in result_dict[com].keys():
            print "\nCHANNEL : ", channel
            for variable in result_dict[com][channel].keys():
                print '"{0}" : {1},'.format(variable, result_dict[com][channel][variable])
        

if __name__ == '__main__':
    set_root_defaults( set_batch = True, msg_ignore_level = 3001 )
    main()
