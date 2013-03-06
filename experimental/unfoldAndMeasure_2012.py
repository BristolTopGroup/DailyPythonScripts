# general
from __future__ import division
from optparse import OptionParser
import sys
from array import array
# rootpy
from rootpy import asrootpy
from rootpy.io import File
# DailyPythonScripts
from config.variable_binning_8TeV import bin_widths, bin_edges
from tools.Calculation import calculate_xsection, calculate_normalised_xsection
from tools.hist_utilities import hist_to_value_error_tuplelist, value_error_tuplelist_to_hist
from tools.Unfolding import Unfolding
from tools.file_utilities import read_data_from_JSON, write_data_to_JSON
import config.RooUnfold as unfoldCfg

luminosity = 5814
ttbar_xsection = 225.19
path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-13-015_V3/'
    
file_for_unfolding = File(path_to_files + 'unfolding_merged.root', 'read')
file_for_powheg = File(path_to_files + 'unfolding_TTJets_8TeV_powheg.root', 'read')
file_for_mcatnlo = File(path_to_files + 'unfolding_TTJets_8TeV_mcatnlo.root', 'read')
    
file_for_scaledown = File(path_to_files + 'unfolding_TTJets_8TeV_scaledown.root', 'read')
file_for_scaleup = File(path_to_files + 'unfolding_TTJets_8TeV_scaleup.root', 'read')
file_for_matchingdown = File(path_to_files + 'unfolding_TTJets_8TeV_matchingdown.root', 'read')
file_for_matchingup = File(path_to_files + 'unfolding_TTJets_8TeV_matchingup.root', 'read')

def unfold_results(results, h_truth, h_measured, h_response, method):
    global variable
    h_data = value_error_tuplelist_to_hist(results, bin_edges[variable])
    unfolding = Unfolding(h_truth, h_measured, h_response, method=method)
    h_unfolded_data = unfolding.unfold(h_data)
    
    return hist_to_value_error_tuplelist(h_unfolded_data)

def get_unfold_histogram_tuple(inputfile, variable, channel, met_type):
    folder = None
    if not 'HT' in variable:
        folder = inputfile.Get('unfolding_%s_analyser_%s_channel_%s' % (variable, channel, met_type))
    else:
        folder = inputfile.Get('unfolding_%s_analyser_%s_channel' % (variable, channel))
        
    n_bins = len(bin_edges[variable]) - 1
    bin_edge_array = array('d', bin_edges[variable])
    
    h_truth = asrootpy(folder.truth.Rebin(n_bins, 'truth', bin_edge_array))
    h_measured = asrootpy(folder.measured.Rebin(n_bins, 'measured', bin_edge_array))
    h_response = folder.response_without_fakes_AsymBins  # response_AsymBins
    
    nEvents = inputfile.EventFilter.EventCounter.GetBinContent(1)#number of processed events 
    lumiweight = ttbar_xsection * luminosity / nEvents #ttbar x-section = 225.2pb, lumi = 5814pb-1
    h_truth.Scale(lumiweight)
    h_measured.Scale(lumiweight)
    h_response.Scale(lumiweight)
    return h_truth, h_measured, h_response

def unfold_and_measure_cross_section(TTJet_fit_results, category, channel):
    global variable, met_type, path_to_JSON
    h_truth, h_measured, h_response = get_unfold_histogram_tuple(file_for_unfolding, variable, channel, met_type)
    MADGRAPH_results = hist_to_value_error_tuplelist(h_truth)
    POWHEG_results = hist_to_value_error_tuplelist(get_unfold_histogram_tuple(file_for_powheg, variable, channel, met_type)[0])
    MCATNLO_results = hist_to_value_error_tuplelist(get_unfold_histogram_tuple(file_for_mcatnlo, variable, channel, met_type)[0])
    
    matchingdown_results = hist_to_value_error_tuplelist(get_unfold_histogram_tuple(file_for_matchingdown, variable, channel, met_type)[0])
    matchingup_results = hist_to_value_error_tuplelist(get_unfold_histogram_tuple(file_for_matchingup, variable, channel, met_type)[0])
    scaledown_results = hist_to_value_error_tuplelist(get_unfold_histogram_tuple(file_for_scaledown, variable, channel, met_type)[0])
    scaleup_results = hist_to_value_error_tuplelist(get_unfold_histogram_tuple(file_for_scaleup, variable, channel, met_type)[0])
    
    TTJet_fit_results_unfolded = unfold_results(TTJet_fit_results,
                                                         h_truth,
                                                         h_measured,
                                                         h_response,
                                                         'RooUnfoldSvd')
    
    write_data_to_JSON(TTJet_fit_results, path_to_JSON + variable + '/xsection_measurement_results' + '/kv' + str(unfoldCfg.SVD_k_value) + '/' + category + '/TTJet_fit_results_' + channel + '_' + met_type + '.txt')
    normalisation_unfolded = {
                              'TTJet' : TTJet_fit_results_unfolded,
                              'MADGRAPH': MADGRAPH_results,
                              #other generators
                              'POWHEG': POWHEG_results,
                              'MCATNLO': MCATNLO_results,
                              #systematics
                              'matchingdown': matchingdown_results,
                              'matchingup': matchingup_results,
                              'scaledown': scaledown_results,
                              'scaleup': scaleup_results
                              }
    write_data_to_JSON(normalisation_unfolded, path_to_JSON + variable + '/xsection_measurement_results' + '/kv' + str(unfoldCfg.SVD_k_value) + '/' + category + '/normalisation_' + channel + '_' + met_type + '_unfolded.txt')
    
    # calculate the x-sections
    TTJet_xsection = calculate_xsection(TTJet_fit_results, luminosity, 0.15)  # L in pb1
    TTJet_xsection_unfolded = calculate_xsection(TTJet_fit_results_unfolded, luminosity, 0.15)  # L in pb1
    MADGRAPH_xsection = calculate_xsection(MADGRAPH_results, luminosity, 0.15)  # L in pb1
    POWHEG_xsection = calculate_xsection(POWHEG_results, luminosity, 0.15)  # L in pb1
    MCATNLO_xsection = calculate_xsection(MCATNLO_results, luminosity, 0.15)  # L in pb1
    matchingdown_xsection = calculate_xsection(matchingdown_results, luminosity, 0.15)  # L in pb1
    matchingup_xsection = calculate_xsection(matchingup_results, luminosity, 0.15)  # L in pb1
    scaledown_xsection = calculate_xsection(scaledown_results, luminosity, 0.15)  # L in pb1
    scaleup_xsection = calculate_xsection(matchingup_results, luminosity, 0.15)  # L in pb1
    
    xsection_unfolded = {'TTJet' : TTJet_xsection_unfolded,
                         'MADGRAPH': MADGRAPH_xsection,
                         'POWHEG': POWHEG_xsection,
                         'MCATNLO': MCATNLO_xsection,
                         #systematics
                         'matchingdown': matchingdown_xsection,
                         'matchingup': matchingup_xsection,
                         'scaledown': scaledown_xsection,
                         'scaleup': scaleup_xsection
                         }
    write_data_to_JSON(xsection_unfolded, path_to_JSON + variable + '/xsection_measurement_results' + '/kv' + str(unfoldCfg.SVD_k_value) + '/' + category + '/xsection_' + channel + '_' + met_type + '_unfolded.txt')
    
    TTJet_normalised_to_one_xsection = calculate_normalised_xsection(TTJet_fit_results, bin_widths[variable], normalise_to_one=True)
    TTJet_normalised_to_one_xsection_unfolded = calculate_normalised_xsection(TTJet_fit_results_unfolded, bin_widths[variable], normalise_to_one=True)
    MADGRAPH_normalised_to_one_xsection = calculate_normalised_xsection(MADGRAPH_results, bin_widths[variable], normalise_to_one=True)
    POWHEG_normalised_to_one_xsection = calculate_normalised_xsection(POWHEG_results, bin_widths[variable], normalise_to_one=True)
    MCATNLO_normalised_to_one_xsection = calculate_normalised_xsection(MCATNLO_results, bin_widths[variable], normalise_to_one=True)
    matchingdown_normalised_to_one_xsection = calculate_normalised_xsection(matchingdown_results, bin_widths[variable], normalise_to_one=True)
    matchingup_normalised_to_one_xsection = calculate_normalised_xsection(matchingup_results, bin_widths[variable], normalise_to_one=True)
    scaledown_normalised_to_one_xsection = calculate_normalised_xsection(scaledown_results, bin_widths[variable], normalise_to_one=True)
    scaleup_normalised_to_one_xsection = calculate_normalised_xsection(scaleup_results, bin_widths[variable], normalise_to_one=True)
    
    normalised_to_one_xsection_unfolded = {'TTJet' : TTJet_normalised_to_one_xsection_unfolded,
                                           'MADGRAPH': MADGRAPH_normalised_to_one_xsection,
                                           'POWHEG': POWHEG_normalised_to_one_xsection,
                                           'MCATNLO': MCATNLO_normalised_to_one_xsection,
                                           #systematics
                                           'matchingdown': matchingdown_normalised_to_one_xsection,
                                           'matchingup': matchingup_normalised_to_one_xsection,
                                           'scaledown': scaledown_normalised_to_one_xsection,
                                           'scaleup': scaleup_normalised_to_one_xsection
                                           }
    write_data_to_JSON(normalised_to_one_xsection_unfolded, path_to_JSON + variable + '/xsection_measurement_results' + '/kv' + str(unfoldCfg.SVD_k_value) + '/' + category + '/normalised_to_one_xsection_' + channel + '_' + met_type + '_unfolded.txt')
    
    TTJet_normalised_xsection = calculate_normalised_xsection(TTJet_fit_results, bin_widths[variable], normalise_to_one=False)
    TTJet_normalised_xsection_unfolded = calculate_normalised_xsection(TTJet_fit_results_unfolded, bin_widths[variable], normalise_to_one=False)
    MADGRAPH_normalised_xsection = calculate_normalised_xsection(MADGRAPH_results, bin_widths[variable], normalise_to_one=False)
    POWHEG_normalised_xsection = calculate_normalised_xsection(POWHEG_results, bin_widths[variable], normalise_to_one=False)
    MCATNLO_normalised_xsection = calculate_normalised_xsection(MCATNLO_results, bin_widths[variable], normalise_to_one=False)
    matchingdown_normalised_xsection = calculate_normalised_xsection(matchingdown_results, bin_widths[variable], normalise_to_one=False)
    matchingup_normalised_xsection = calculate_normalised_xsection(matchingup_results, bin_widths[variable], normalise_to_one=False)
    scaledown_normalised_xsection = calculate_normalised_xsection(scaledown_results, bin_widths[variable], normalise_to_one=False)
    scaleup_normalised_xsection = calculate_normalised_xsection(scaleup_results, bin_widths[variable], normalise_to_one=False)

    normalised_xsection_unfolded = {'TTJet' : TTJet_normalised_xsection_unfolded,
                                       'MADGRAPH': MADGRAPH_normalised_xsection,
                                       'POWHEG': POWHEG_normalised_xsection,
                                       'MCATNLO': MCATNLO_normalised_xsection,
                                       #systematics
                                       'matchingdown': matchingdown_normalised_xsection,
                                       'matchingup': matchingup_normalised_xsection,
                                       'scaledown': scaledown_normalised_xsection,
                                       'scaleup': scaleup_normalised_xsection
                                       }
    write_data_to_JSON(normalised_xsection_unfolded, path_to_JSON + variable + '/xsection_measurement_results' + '/kv' + str(unfoldCfg.SVD_k_value) + '/' + category + '/normalised_xsection_' + channel + '_' + met_type + '_unfolded.txt')    
    
    sum_xsec, sum_xsec_error = 0, 0
    for value, error in TTJet_xsection_unfolded:
        sum_xsec += value
        sum_xsec_error += error
    print 'Total x-sec in ' +channel + ' channel:', sum_xsec, '+-', sum_xsec_error
    
    for gen, value, value_nounfolding in zip(MADGRAPH_normalised_xsection, TTJet_normalised_xsection_unfolded, TTJet_normalised_xsection):
        print 'gen:', gen, 'unfolded:', value, '\t no unfolding:', value_nounfolding

if __name__ == '__main__':
    # setup
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data/',
                  help="set path to JSON files")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                      help="set the variable to analyse (MET, HT, ST, MT)")
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                      help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type for analysis of MET, ST or MT")
    parser.add_option("-k", "--k_value", type='int',
                      dest="k_value", default=6,
                      help="k-value for SVD unfolding")

    translateOptions = {
                        '0':'0btag',
                        '1':'1btag',
                        '2':'2btags',
                        '3':'3btags',
                        '0m':'0orMoreBtag',
                        '1m':'1orMoreBtag',
                        '2m':'2orMoreBtags',
                        '3m':'3orMoreBtags',
                        '4m':'4orMoreBtags',
                        #mettype:
                        'pf':'patMETsPFlow',
                        'type1':'patType1CorrectedPFMet'
                        }
    
    categories = [ 'central', 'matchingup', 'matchingdown', 'scaleup', 'scaledown', 'BJet_down', 'BJet_up', 'JES_down', 'JES_up', 'LightJet_down', 'LightJet_up', 'PU_down', 'PU_up' ]
    
    (options, args) = parser.parse_args()
    variable = options.variable
    unfoldCfg.SVD_k_value = options.k_value
    met_type = translateOptions[options.metType]
    b_tag_bin = translateOptions[options.bjetbin]
    path_to_JSON = options.path
    
    for category in categories:
        #read fit results from JSON
        TTJet_fit_results_electron = read_data_from_JSON(path_to_JSON + variable + '/fit_results/' + category + '/fit_results_electron_' + met_type + '.txt')['TTJet']
        TTJet_fit_results_muon = read_data_from_JSON(path_to_JSON + variable + '/fit_results/' + category + '/fit_results_muon_' + met_type + '.txt')['TTJet']
        
        #unfold and measure cross section
        unfold_and_measure_cross_section(TTJet_fit_results_electron, category, 'electron')
        unfold_and_measure_cross_section(TTJet_fit_results_muon, category, 'muon')
