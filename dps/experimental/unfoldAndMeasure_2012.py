# general
from __future__ import division
from optparse import OptionParser
import sys, os
from array import array
# rootpy
from ROOT import TFile
from rootpy import asrootpy
from rootpy.io import File
from rootpy.plotting import Hist, Hist2D
# DailyPythonScripts
from dps.config.variable_binning_8TeV import bin_widths, bin_edges
from dps.utils.Calculation import calculate_xsection, calculate_normalised_xsection
from dps.utils.hist_utilities import hist_to_value_error_tuplelist, value_error_tuplelist_to_hist
from dps.utils.Unfolding import Unfolding
from dps.utils.file_utilities import read_data_from_JSON, write_data_to_JSON, make_folder_if_not_exists
import dps.config.RooUnfold as unfoldCfg

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

def unfold_results(results, category, channel, h_truth, h_measured, h_response, method):
    global variable, path_to_JSON
    h_data = value_error_tuplelist_to_hist(results, bin_edges[variable])
    unfolding = Unfolding(h_truth, h_measured, h_response, method=method)
    
    #turning off the unfolding errors for systematic samples
    if category != 'central':
        unfoldCfg.Hreco = 0
    
    h_unfolded_data = unfolding.unfold(h_data)
    
    #export the D and SV distributions
    SVD_path = path_to_JSON + '/' + variable + '/unfolding_objects/' + channel + '/kv_' + str(unfoldCfg.SVD_k_value) + '/'
    make_folder_if_not_exists(SVD_path)
    if method == 'TSVDUnfold':
        SVDdist = TFile(SVD_path + method + '_SVDdistributions_' + category + '.root', 'recreate')
        directory = SVDdist.mkdir('SVDdist')
        directory.cd()
        unfolding.unfoldObject.GetD().Write()
        unfolding.unfoldObject.GetSV().Write()
        #    unfolding.unfoldObject.GetUnfoldCovMatrix(data_covariance_matrix(h_data), unfoldCfg.SVD_n_toy).Write()
        SVDdist.Close()
    else:
        SVDdist = TFile(SVD_path + method + '_SVDdistributions_Hreco' + str(unfoldCfg.Hreco) + '_' + category + '.root', 'recreate')
        directory = SVDdist.mkdir('SVDdist')
        directory.cd()
        unfolding.unfoldObject.Impl().GetD().Write()
        unfolding.unfoldObject.Impl().GetSV().Write()
        h_truth.Write()
        h_measured.Write()
        h_response.Write()
        #    unfolding.unfoldObject.Impl().GetUnfoldCovMatrix(data_covariance_matrix(h_data), unfoldCfg.SVD_n_toy).Write()
        SVDdist.Close()

    #export the whole unfolding object if it doesn't exist
    if method == 'TSVDUnfold':
        unfolding_object_file_name = SVD_path + method + '_unfoldingObject_' + category + '.root'
    else:
        unfolding_object_file_name = SVD_path + method + '_unfoldingObject_Hreco' + str(unfoldCfg.Hreco) + '_' + category + '.root'
    if not os.path.isfile(unfolding_object_file_name):
        unfoldingObjectFile = TFile(unfolding_object_file_name, 'recreate')
        directory = unfoldingObjectFile.mkdir('unfoldingObject')
        directory.cd()
        if method == 'TSVDUnfold':
            unfolding.unfoldObject.Write()
        else:
            unfolding.unfoldObject.Impl().Write()
        unfoldingObjectFile.Close()
    
    del unfolding
    return hist_to_value_error_tuplelist(h_unfolded_data)

def data_covariance_matrix(data):
    values = list(data)
    get_bin_error = data.GetBinError
    cov_matrix = Hist2D(len(values), -10, 10, len(values), -10, 10, type = 'D')
    for bin_i in range(len(values)):
        error = get_bin_error(bin_i+1)
        cov_matrix.SetBinContent(bin_i+1, bin_i+1, error*error)
    return cov_matrix

def get_unfold_histogram_tuple(inputfile, variable, channel, met_type):
    folder = None
    if not 'HT' in variable:
        folder = inputfile.Get('unfolding_%s_analyser_%s_channel_%s' % (variable, channel, met_type))
    else:
        folder = inputfile.Get('unfolding_%s_analyser_%s_channel' % (variable, channel))
        
    n_bins = len(bin_edges[variable]) - 1
    bin_edge_array = array('d', bin_edges[variable])
    
    #h_fakes = asrootpy(folder.fake_AsymBins)
    #h_truth = asrootpy(folder.truth.Rebin(n_bins, 'truth', bin_edge_array))
    h_truth = asrootpy(folder.truth_AsymBins).Clone()
    #h_measured = asrootpy(folder.measured.Rebin(n_bins, 'measured', bin_edge_array))
    h_measured = asrootpy(folder.measured_AsymBins).Clone()
    h_response = folder.response_without_fakes_AsymBins.Clone()  # response_AsymBins
    
    nEvents = inputfile.EventFilter.EventCounter.GetBinContent(1)#number of processed events 
    lumiweight = ttbar_xsection * luminosity / nEvents #ttbar x-section = 225.2pb, lumi = 5814pb-1
    h_truth.Scale(lumiweight)
    h_measured.Scale(lumiweight)
    h_response.Scale(lumiweight)
    return h_truth, h_measured, h_response

def get_unfolded_normalisation(TTJet_fit_results, category, channel):
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
                                                category,
                                                channel,
                                                h_truth,
                                                h_measured,
                                                h_response,
                                                'RooUnfoldSvd'
#                                                'TSVDUnfold'
                                                )
        
    normalisation_unfolded = {
                              'TTJet_measured' : TTJet_fit_results,
                              'TTJet_unfolded' : TTJet_fit_results_unfolded,
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
    write_data_to_JSON(normalisation_unfolded, path_to_JSON + '/' + variable + '/xsection_measurement_results' + '/kv' + str(unfoldCfg.SVD_k_value) + '/' + category + '/normalisation_' + channel + '_' + met_type + '.txt')
    
    return normalisation_unfolded
    
def calculate_xsections(normalisation, category, channel):
    global variable, met_type, path_to_JSON
    # calculate the x-sections
    TTJet_xsection = calculate_xsection(normalisation['TTJet_measured'], luminosity, 0.15)  # L in pb1
    TTJet_xsection_unfolded = calculate_xsection(normalisation['TTJet_unfolded'], luminosity, 0.15)  # L in pb1
    MADGRAPH_xsection = calculate_xsection(normalisation['MADGRAPH'], luminosity, 0.15)  # L in pb1
    POWHEG_xsection = calculate_xsection(normalisation['POWHEG'], luminosity, 0.15)  # L in pb1
    MCATNLO_xsection = calculate_xsection(normalisation['MCATNLO'], luminosity, 0.15)  # L in pb1
    matchingdown_xsection = calculate_xsection(normalisation['matchingdown'], luminosity, 0.15)  # L in pb1
    matchingup_xsection = calculate_xsection(normalisation['matchingup'], luminosity, 0.15)  # L in pb1
    scaledown_xsection = calculate_xsection(normalisation['scaledown'], luminosity, 0.15)  # L in pb1
    scaleup_xsection = calculate_xsection(normalisation['scaleup'], luminosity, 0.15)  # L in pb1
    
    xsection_unfolded = {'TTJet_measured' : TTJet_xsection,
                         'TTJet_unfolded' : TTJet_xsection_unfolded,
                         'MADGRAPH': MADGRAPH_xsection,
                         'POWHEG': POWHEG_xsection,
                         'MCATNLO': MCATNLO_xsection,
                         #systematics
                         'matchingdown': matchingdown_xsection,
                         'matchingup': matchingup_xsection,
                         'scaledown': scaledown_xsection,
                         'scaleup': scaleup_xsection
                         }
    write_data_to_JSON(xsection_unfolded, path_to_JSON + '/' + variable + '/xsection_measurement_results' + '/kv' + str(unfoldCfg.SVD_k_value) + '/' + category + '/xsection_' + channel + '_' + met_type + '.txt')
    
def calculate_normalised_xsections(normalisation, category, channel, normalise_to_one = False):
    global variable, met_type, path_to_JSON
    TTJet_normalised_xsection = calculate_normalised_xsection(normalisation['TTJet_measured'], bin_widths[variable], normalise_to_one)
    TTJet_normalised_xsection_unfolded = calculate_normalised_xsection(normalisation['TTJet_unfolded'], bin_widths[variable], normalise_to_one)
    MADGRAPH_normalised_xsection = calculate_normalised_xsection(normalisation['MADGRAPH'], bin_widths[variable], normalise_to_one)
    POWHEG_normalised_xsection = calculate_normalised_xsection(normalisation['POWHEG'], bin_widths[variable], normalise_to_one)
    MCATNLO_normalised_xsection = calculate_normalised_xsection(normalisation['MCATNLO'], bin_widths[variable], normalise_to_one)
    matchingdown_normalised_xsection = calculate_normalised_xsection(normalisation['matchingdown'], bin_widths[variable], normalise_to_one)
    matchingup_normalised_xsection = calculate_normalised_xsection(normalisation['matchingup'], bin_widths[variable], normalise_to_one)
    scaledown_normalised_xsection = calculate_normalised_xsection(normalisation['scaledown'], bin_widths[variable], normalise_to_one)
    scaleup_normalised_xsection = calculate_normalised_xsection(normalisation['scaleup'], bin_widths[variable], normalise_to_one)
    
    normalised_xsection = {'TTJet_measured' : TTJet_normalised_xsection,
                           'TTJet_unfolded' : TTJet_normalised_xsection_unfolded,
                           'MADGRAPH': MADGRAPH_normalised_xsection,
                           'POWHEG': POWHEG_normalised_xsection,
                           'MCATNLO': MCATNLO_normalised_xsection,
                           #systematics
                           'matchingdown': matchingdown_normalised_xsection,
                           'matchingup': matchingup_normalised_xsection,
                           'scaledown': scaledown_normalised_xsection,
                           'scaleup': scaleup_normalised_xsection
                           }
    
    filename = path_to_JSON + '/' + variable + '/xsection_measurement_results' + '/kv' + str(unfoldCfg.SVD_k_value) + '/' + category + '/normalised_xsection_' + channel + '_' + met_type + '.txt'
    if normalise_to_one:
        filename = filename.replace('normalised_xsection', 'normalised_to_one_xsection')
    write_data_to_JSON(normalised_xsection, filename)

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
    parser.add_option("-H", "--hreco", type='int',
                      dest="Hreco", default=2,
                      help="Hreco parameter for error treatment in RooUnfold")

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
                        'pf':'PFMET',
                        'type1':'patType1CorrectedPFMet'
                        }
    
    categories = [ 'central', 'matchingup', 'matchingdown', 'scaleup', 'scaledown', 'BJet_down', 'BJet_up', 'JES_down', 'JES_up', 'LightJet_down', 'LightJet_up', 'PU_down', 'PU_up' ]
    
    (options, args) = parser.parse_args()
    variable = options.variable
    unfoldCfg.SVD_k_value = options.k_value
    unfoldCfg.Hreco = options.Hreco
    met_type = translateOptions[options.metType]
    b_tag_bin = translateOptions[options.bjetbin]
    path_to_JSON = options.path
    
    for category in categories:
        #Setting up systematic MET for JES up/down samples
        met_type = translateOptions[options.metType]
        if category == 'JES_up':
            met_type += 'JetEnUp'
            if met_type == 'PFMETJetEnUp':
                met_type = 'patPFMetJetEnUp'
        elif category == 'JES_down':
            met_type += 'JetEnDown'
            if met_type == 'PFMETJetEnDown':
                met_type = 'patPFMetJetEnDown'
        
        #read fit results from JSON
        TTJet_fit_results_electron = read_data_from_JSON(path_to_JSON + '/' + variable + '/fit_results/' + category + '/fit_results_electron_' + met_type + '.txt')['TTJet']
        TTJet_fit_results_muon = read_data_from_JSON(path_to_JSON + '/' + variable + '/fit_results/' + category + '/fit_results_muon_' + met_type + '.txt')['TTJet']
        
        #change back to original MET type for the unfolding
        met_type = translateOptions[options.metType]
        #ad-hoc switch for PFMET -> patMETsPFlow
        if met_type == 'PFMET':
            met_type = 'patMETsPFlow'
        
        #get unfolded normalisation
        unfolded_normalisation_electron = get_unfolded_normalisation(TTJet_fit_results_electron, category, 'electron')
        unfolded_normalisation_muon = get_unfolded_normalisation(TTJet_fit_results_muon, category, 'muon')
        
        
        #measure xsection
        calculate_xsections(unfolded_normalisation_electron, category, 'electron')
        calculate_xsections(unfolded_normalisation_muon, category, 'muon')
        
        calculate_normalised_xsections(unfolded_normalisation_electron, category, 'electron')
        calculate_normalised_xsections(unfolded_normalisation_muon, category, 'muon')
        
        normalise_to_one = True
        calculate_normalised_xsections(unfolded_normalisation_electron, category, 'electron', normalise_to_one)
        calculate_normalised_xsections(unfolded_normalisation_muon, category, 'muon', normalise_to_one)
