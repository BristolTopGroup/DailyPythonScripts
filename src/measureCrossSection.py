from __future__ import division
from tools.Calculation import calculate_xsection, calculate_normalised_xsection
from tools.hist_utilities import hist_to_value_error_tuplelist, value_error_tuplelist_to_hist
from tools.Unfolding import Unfolding
from array import array
#rootpy
from rootpy.io import File
from rootpy.utils import asrootpy

def unfold_results(results, h_truth, h_measured, h_response, method):
    global bin_edges

    h_data = value_error_tuplelist_to_hist(results, bin_edges)
    unfolding = Unfolding(h_truth, h_measured, h_response, method=method)
    h_unfolded_data = unfolding.unfold(h_data)
    
    return hist_to_value_error_tuplelist(h_unfolded_data)

def get_unfold_histogram_tuple(inputfile, channel):
    global bin_edges
    folder = None
    if channel == 'electron':
        folder = inputfile.unfoldingAnalyserElectronChannel
    else:#channel == 'muon'
        folder = inputfile.unfoldingAnalyserMuonChannel
        
    n_bins = len(bin_edges) - 1
    bin_edge_array = array('d', bin_edges)
    
    h_truth = asrootpy(folder.truth.Rebin(n_bins, 'truth', bin_edge_array))
    h_measured = asrootpy(folder.measured.Rebin(n_bins, 'measured', bin_edge_array))
    h_response = folder.response_withoutFakes_AsymBins #response_AsymBins
    return h_truth, h_measured, h_response

if __name__ == '__main__':
    #setup
    bin_edges = [0, 25, 45, 70, 100, 1000]
    bin_widths = [25,20,25,30,150]
    #possible options:
    #--continue : continue from saved - skips ROOT files, reads from JSON?
    
    #get data from histograms or JSON files
    
    #get fit values
    
    #mock input
    TTJet_fit_results_electron = [(2146,145), (3399,254), (3723,69), (2256, 53), (1722, 91)]
    MADGRAPH_results_electron = [(2146,145), (3399,254), (3723,69), (2256, 53), (1722, 91)]
    MADGRAPH_results = [(2146,145), (3399,254), (3723,69), (2256, 53), (1722, 91)]
    #get fit values for systematics
    #unfold all above
    inputfile = File('../data/unfolding_merged.root', 'read')
    h_truth, h_measured, h_response = get_unfold_histogram_tuple(inputfile, 'electron')
    TTJet_fit_results_electron_unfolded = unfold_results(TTJet_fit_results_electron, 
                                                         h_truth, 
                                                         h_measured, 
                                                         h_response, 
                                                         'RooUnfoldSvd')
    #calculate the x-sections and
    bin_widths = [25,20,25,30,150]
    xsection = calculate_xsection(TTJet_fit_results_electron_unfolded, 5050, 0.15) #L in pb1
    normalisedToOne_xsection = calculate_normalised_xsection(TTJet_fit_results_electron_unfolded, bin_widths, normalise_to_one = True)
    normalised_xsection = calculate_normalised_xsection(TTJet_fit_results_electron_unfolded, bin_widths, normalise_to_one = False)
    normalised_xsection_nounfolding = calculate_normalised_xsection(TTJet_fit_results_electron, bin_widths, normalise_to_one = False)
    
    sum_xsec, sum_xsec_error = 0,0
    for value, error in xsection:
        sum_xsec += value
        sum_xsec_error += error
    print 'Total x-sec:', sum_xsec, '+-', sum_xsec_error
    
    
    for value, value_nounfolding in zip(normalised_xsection,normalised_xsection_nounfolding):
        print 'unfolded:', value, '\t no unfolding:', value_nounfolding
        