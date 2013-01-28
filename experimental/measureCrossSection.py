# general
from __future__ import division
from array import array
# rootpy
from rootpy.io import File
from rootpy import asrootpy
# DailyPythonScripts
from tools.Calculation import calculate_xsection, calculate_normalised_xsection, decombine_result
from tools.hist_utilities import hist_to_value_error_tuplelist, value_error_tuplelist_to_hist
from tools.Unfolding import Unfolding
from tools.Fitting import TMinuitFit
from tools.file_utilities import write_data_to_JSON

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
    else:  # channel == 'muon'
        folder = inputfile.unfoldingAnalyserMuonChannel
        
    n_bins = len(bin_edges) - 1
    bin_edge_array = array('d', bin_edges)
    
    h_truth = asrootpy(folder.truth.Rebin(n_bins, 'truth', bin_edge_array))
    h_measured = asrootpy(folder.measured.Rebin(n_bins, 'measured', bin_edge_array))
    h_response = folder.response_withoutFakes_AsymBins  # response_AsymBins
    
    nEvents = inputfile.EventFilter.EventCounter.GetBinContent(1)#number of processed events 
    lumiweight = 164.5 * 5050 / nEvents #ttbar x-section = 164.5pb, lumi = 5050pb-1
    h_truth.Scale(lumiweight)
    h_measured.Scale(lumiweight)
    h_response.Scale(lumiweight)
    return h_truth, h_measured, h_response

def get_histograms(input_files, met_type, met_bin, b_tag_bin, rebin=1):
    electron_histograms = {}
    muon_histograms = {}
    electron_abs_eta = 'TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_%s_bin_%s/electron_AbsEta' % (met_type, met_bin)
    muon_abs_eta = 'TTbarPlusMetAnalysis/MuPlusJets/Ref selection/BinnedMETAnalysis/Muon_%s_bin_%s/muon_AbsEta' % (met_type, met_bin)
    for sample, file_name in input_files.iteritems():
        h_electron_abs_eta = get_histogram(file_name, electron_abs_eta, b_tag_bin)
        h_muon_abs_eta = get_histogram(file_name, muon_abs_eta, b_tag_bin)

        h_electron_abs_eta.Rebin(rebin)
        h_muon_abs_eta.Rebin(rebin)
        
        electron_histograms[sample] = h_electron_abs_eta
        muon_histograms[sample] = h_muon_abs_eta
    
    if 'data_electron' in input_files.keys():
        # data-driven QCD
        electron_abs_eta = 'TTbarPlusMetAnalysis/EPlusJets/QCDConversions/BinnedMETAnalysis/Electron_%s_bin_%s/electron_AbsEta' % (met_type, met_bin)
        h_electron_abs_eta = get_histogram(input_files['data_electron'], electron_abs_eta, '0btag')
        h_electron_abs_eta.Rebin(rebin)
        electron_histograms['QCD'] = h_electron_abs_eta
        
    if 'data_muon' in input_files.keys():
        # data-driven QCD
        # for now custom file
        global muon_QCD_file
        muon_abs_eta = 'etaAbs_ge2j_data'
        h_muon_abs_eta = get_histogram(muon_QCD_file, muon_abs_eta, '')
        muon_histograms['QCD'] = h_muon_abs_eta
        
    return electron_histograms, muon_histograms

def get_histogram(input_file, histogram_path, b_tag_bin=''):
#    input_file = File(input_file)
    available_b_tag_bins = ['0btag', '1btag', '2btags', '3btags', '4orMoreBtags']
    b_tag_bin_sum_rules = {
                           '0orMoreBtags':available_b_tag_bins,
                           '1orMoreBtags': available_b_tag_bins[1:],
                           '2orMoreBtags': available_b_tag_bins[2:],
                           '3orMoreBtags': available_b_tag_bins[3:]
                           }
    histogram = None
    if b_tag_bin in b_tag_bin_sum_rules.keys():  # summing needed
        b_tag_bins_to_sum = b_tag_bin_sum_rules[b_tag_bin]
        histogram = input_file.Get(histogram_path + '_' + b_tag_bins_to_sum[0])
        for bin_i in b_tag_bins_to_sum[1:]:
            histogram += input_file.Get(histogram_path + '_' + bin_i)
            
    else:
        if b_tag_bin == '':
            histogram = input_file.Get(histogram_path)
        else:
            histogram = input_file.Get(histogram_path + '_' + b_tag_bin)
    
    return histogram

def get_fitted_normalisation(input_files, met_type, b_tag_bin, JSON=False):
    if JSON:
        return get_fitted_normalisation_from_JSON(input_files, met_type)  # no b_tag_bin as files are specific
    else:
        return get_fitted_normalisation_from_ROOT(input_files, met_type, b_tag_bin)

def get_fitted_normalisation_from_JSON(input_files, met_type):
    pass

def get_fitted_normalisation_from_ROOT(input_files, met_type, b_tag_bin):
    global met_bins_ROOT
    electron_results = {}
    electron_initial_values = {}
    muon_results = {}
    muon_initial_values = {}
    for met_bin in met_bins_ROOT:
        electron_histograms, muon_histograms = get_histograms(input_files={
                                  'TTJet': TTJet_file,
                                  'SingleTop': SingleTop_file,
                                  'V+Jets':VJets_file,
                                  'data_electron': data_file_electron,
                                  'data_muon': data_file_muon
                                  },
                   met_type=met_type,
                   met_bin=met_bin,
                   b_tag_bin=b_tag_bin,
                   rebin=20
                   )
        # prepare histograms
        # normalise histograms
        # TODO
        
        # store pre-fit information
        
        # create signal histograms
        h_electron_eta_signal = electron_histograms['TTJet'] + electron_histograms['SingleTop']
        h_muon_eta_signal = muon_histograms['TTJet'] + muon_histograms['SingleTop']
        fitter_electron = TMinuitFit(histograms={
                                      'data':electron_histograms['data_electron'],
                                      'signal':h_electron_eta_signal,
                                      'V+Jets':electron_histograms['V+Jets'],
                                      'QCD':electron_histograms['QCD']
                                      })
        fitter_muon = TMinuitFit(histograms={
                                      'data':muon_histograms['data_muon'],
                                      'signal':h_muon_eta_signal,
                                      'V+Jets':muon_histograms['V+Jets'],
                                      'QCD':muon_histograms['QCD']
                                      })
        
        fitter_electron.fit()
        fit_results_electron = fitter_electron.readResults()
        normalisation_electron = fitter_electron.normalisation
        
        N_ttbar_before_fit_electron = electron_histograms['TTJet'].Integral()
        N_SingleTop_before_fit_electron = electron_histograms['SingleTop'].Integral()
        
        TTJet_SingleTop_ratio_electron = N_ttbar_before_fit_electron / N_SingleTop_before_fit_electron
        N_ttbar_electron, N_SingleTop_electron = decombine_result(fit_results_electron['signal'], TTJet_SingleTop_ratio_electron)
        
        
        fit_results_electron['TTJet'] = N_ttbar_electron
        fit_results_electron['SingleTop'] = N_SingleTop_electron
        normalisation_electron['TTJet'] = N_ttbar_before_fit_electron
        normalisation_electron['SingleTop'] = N_SingleTop_before_fit_electron
        # this needs to
        if electron_results == {}:  # empty
            for sample in fit_results_electron.keys():
                electron_results[sample] = [fit_results_electron[sample]]
                electron_initial_values[sample] = [normalisation_electron[sample]]
        else:
            for sample in fit_results_electron.keys():
                electron_results[sample].append(fit_results_electron[sample])
                electron_initial_values[sample].append(normalisation_electron[sample])
        
        fitter_muon.fit()
        fit_results_muon = fitter_muon.readResults()
        normalisation_muon = fitter_muon.normalisation
        
        N_ttbar_before_fit_muon = muon_histograms['TTJet'].Integral()
        N_SingleTop_before_fit_muon = muon_histograms['SingleTop'].Integral()
        TTJet_SingleTop_ratio_muon = N_ttbar_before_fit_muon / N_SingleTop_before_fit_muon
        N_ttbar_muon, N_SingleTop_muon = decombine_result(fit_results_muon['signal'], TTJet_SingleTop_ratio_muon)
        
        fit_results_muon['TTJet'] = N_ttbar_muon
        fit_results_muon['SingleTop'] = N_SingleTop_muon
        normalisation_muon['TTJet'] = N_ttbar_before_fit_muon
        normalisation_muon['SingleTop'] = N_SingleTop_before_fit_muon
        
        if muon_results == {}:  # empty
            for sample in fit_results_muon.keys():
                muon_results[sample] = [fit_results_muon[sample]]
                muon_initial_values[sample] = [normalisation_muon[sample]]
        else:
            for sample in fit_results_muon.keys():
                muon_results[sample].append(fit_results_muon[sample])
                muon_initial_values[sample].append(normalisation_muon[sample])
        
    return electron_results, muon_results, electron_initial_values, muon_initial_values

def get_systematic_errors(central_results, channel):
    pass    
    
def write_fit_results_and_initial_values(fit_results_electron, fit_results_muon, initial_values_electron, initial_values_muon):    
    write_data_to_JSON(fit_results_electron, 'data/fit_results_electron.txt')
    write_data_to_JSON(fit_results_muon, 'data/fit_results_muon.txt')
    write_data_to_JSON(initial_values_electron, 'data/initial_values_electron.txt')
    write_data_to_JSON(initial_values_muon, 'data/initial_values_muon.txt')
    
def write_cross_section():
    pass

if __name__ == '__main__':
    # setup
    bin_edges = [0, 25, 45, 70, 100, 1000]
    bin_widths = [25, 20, 25, 30, 150]
    met_bins_ROOT = ['0-25', '25-45', '45-70', '70-100', '100-inf']
    path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-12-241_V4/'
    file_for_unfolding = File(path_to_files + 'unfolding_merged.root', 'read')
    file_for_powheg = File(path_to_files + 'unfolding_TTJets_7TeV_powheg.root', 'read')
    file_for_pythia = File(path_to_files + 'unfolding_TTJets_7TeV_pythia.root', 'read')
    file_for_mcatnlo = File(path_to_files + 'unfolding_merged.root', 'read')
    
    file_for_scaledown = File(path_to_files + 'unfolding_TTJets_7TeV_scaledown.root', 'read')
    file_for_scaleup = File(path_to_files + 'unfolding_TTJets_7TeV_scaleup.root', 'read')
    file_for_matchingdown = File(path_to_files + 'unfolding_TTJets_7TeV_matchingdown.root', 'read')
    file_for_matchingup = File(path_to_files + 'unfolding_TTJets_7TeV_matchingup.root', 'read')
    # possible options:
    # --continue : continue from saved - skips ROOT files, reads from JSON?
    
    # get data from histograms or JSON files
    TTJet_file = File(path_to_files + 'central/TTJet_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    SingleTop_file = File(path_to_files + 'central/SingleTop_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    VJets_file = File(path_to_files + 'central/VJets_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    data_file_electron = File(path_to_files + 'central/ElectronHad_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    data_file_muon = File(path_to_files + 'central/SingleMu_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    muon_QCD_file = File(path_to_files + 'QCD_data_mu.root')
    
    fit_results_electron, fit_results_muon, initial_values_electron, initial_values_muon = get_fitted_normalisation(
                input_files={
                                  'TTJet': TTJet_file,
                                  'SingleTop': SingleTop_file,
                                  'V+Jets':VJets_file,
                                  'data_electron': data_file_electron,
                                  'data_muon': data_file_muon
                                  },
                met_type='patType1CorrectedPFMet',
                b_tag_bin='2orMoreBtags',
                   )
    write_fit_results_and_initial_values(fit_results_electron, fit_results_muon, initial_values_electron, initial_values_muon)
    
    #continue with only TTJet
    TTJet_fit_results_electron = fit_results_electron['TTJet']
    TTJet_fit_results_muon = fit_results_muon['TTJet']
    
    # get t values for systematics
    # for systematics we only need the TTJet results!
    # unfold all above
    
    h_truth, h_measured, h_response = get_unfold_histogram_tuple(file_for_unfolding, 'electron')
    MADGRAPH_results_electron = hist_to_value_error_tuplelist(h_truth)
    POWHEG_results_electron = hist_to_value_error_tuplelist(get_unfold_histogram_tuple(file_for_powheg, 'electron')[1])
    PYTHIA_results_electron = hist_to_value_error_tuplelist(get_unfold_histogram_tuple(file_for_pythia, 'electron')[1])
    MCATNLO_results_electron = hist_to_value_error_tuplelist(get_unfold_histogram_tuple(file_for_mcatnlo, 'electron')[1])
    
    matchingdown_results_electron = hist_to_value_error_tuplelist(get_unfold_histogram_tuple(file_for_matchingdown, 'electron')[1])
    matchingup_results_electron = hist_to_value_error_tuplelist(get_unfold_histogram_tuple(file_for_matchingup, 'electron')[1])
    scaledown_results_electron = hist_to_value_error_tuplelist(get_unfold_histogram_tuple(file_for_scaledown, 'electron')[1])
    scaleup_results_electron = hist_to_value_error_tuplelist(get_unfold_histogram_tuple(file_for_scaleup, 'electron')[1])
    
    TTJet_fit_results_electron_unfolded = unfold_results(TTJet_fit_results_electron,
                                                         h_truth,
                                                         h_measured,
                                                         h_response,
                                                         'RooUnfoldSvd')
    
    write_data_to_JSON(TTJet_fit_results_electron, 'data/TTJet_fit_results_electron.txt')
    normalisation_electron_unfolded = {
                                       'TTJet' : TTJet_fit_results_electron_unfolded,
                                       'MADGRAPH': MADGRAPH_results_electron,
                                       #other generators
                                       'POWHEG': POWHEG_results_electron,
                                       'PYTHIA': PYTHIA_results_electron,
                                       'MCATNLO': MCATNLO_results_electron,
                                       #systematics
                                       'matchingdown': matchingdown_results_electron,
                                       'matchingup': matchingup_results_electron,
                                       'scaledown': scaledown_results_electron,
                                       'scaleup': scaleup_results_electron
                                       }
    write_data_to_JSON(normalisation_electron_unfolded, 'data/normalisation_electron_unfolded.txt')
    
    # calculate the x-sections and
    bin_widths = [25, 20, 25, 30, 150]
    TTJet_xsection = calculate_xsection(TTJet_fit_results_electron, 5050, 0.15)  # L in pb1
    TTJet_xsection_unfolded = calculate_xsection(TTJet_fit_results_electron_unfolded, 5050, 0.15)  # L in pb1
    MADGRAPH_xsection = calculate_xsection(MADGRAPH_results_electron, 5050, 0.15)  # L in pb1
    
    xsection_electron_unfolded = {'TTJet' : TTJet_xsection_unfolded,
                                       'MADGRAPH': MADGRAPH_xsection
                                       }
    write_data_to_JSON(xsection_electron_unfolded, 'data/xsection_electron_unfolded.txt')
    
    TTJet_normalised_to_one_xsection = calculate_normalised_xsection(TTJet_fit_results_electron, bin_widths, normalise_to_one=True)
    TTJet_normalised_to_one_xsection_unfolded = calculate_normalised_xsection(TTJet_fit_results_electron_unfolded, bin_widths, normalise_to_one=True)
    MADGRAPH_normalised_to_one_xsection = calculate_normalised_xsection(MADGRAPH_results_electron, bin_widths, normalise_to_one=True)
    
    normalised_to_one_xsection_electron_unfolded = {'TTJet' : TTJet_normalised_to_one_xsection_unfolded,
                                       'MADGRAPH': MADGRAPH_normalised_to_one_xsection
                                       }
    write_data_to_JSON(normalised_to_one_xsection_electron_unfolded, 'data/normalised_to_one_xsection_electron_unfolded.txt')
    
    TTJet_normalised_xsection = calculate_normalised_xsection(TTJet_fit_results_electron, bin_widths, normalise_to_one=False)
    TTJet_normalised_xsection_unfolded = calculate_normalised_xsection(TTJet_fit_results_electron_unfolded, bin_widths, normalise_to_one=False)
    MADGRAPH__normalised_xsection = calculate_normalised_xsection(MADGRAPH_results_electron, bin_widths, normalise_to_one=False)
    
    normalised_xsection_electron_unfolded = {'TTJet' : TTJet_normalised_xsection_unfolded,
                                       'MADGRAPH': MADGRAPH__normalised_xsection
                                       }
    write_data_to_JSON(normalised_xsection_electron_unfolded, 'data/normalised_xsection_electron_unfolded.txt')
    
    sum_xsec, sum_xsec_error = 0, 0
    for value, error in TTJet_xsection_unfolded:
        sum_xsec += value
        sum_xsec_error += error
    print 'Total x-sec:', sum_xsec, '+-', sum_xsec_error
    
    
    for gen, value, value_nounfolding in zip(MADGRAPH__normalised_xsection, TTJet_normalised_xsection_unfolded, TTJet_normalised_xsection):
        print 'gen:', gen, 'unfolded:', value, '\t no unfolding:', value_nounfolding
        
