# general
from __future__ import division
from array import array
# rootpy
from rootpy.io import File
from rootpy.utils import asrootpy
# DailyPythonScripts
from tools.Calculation import calculate_xsection, calculate_normalised_xsection, decombine_result
from tools.hist_utilities import hist_to_value_error_tuplelist, value_error_tuplelist_to_hist
from tools.Unfolding import Unfolding
from tools.Fitting import TMinuitFit

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
    muon_results = {}
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
        results_electron = fitter_electron.readResults()
        
        TTJet_SingleTop_ratio_electron = electron_histograms['TTJet'].Integral() / electron_histograms['SingleTop'].Integral()
        N_ttbar_electron, N_SingleTop_electron = decombine_result(results_electron['signal'], TTJet_SingleTop_ratio_electron)
        
        
        results_electron['TTJet'] = N_ttbar_electron
        results_electron['SingleTop'] = N_SingleTop_electron
        #this needs to
        if electron_results == {}:#empty
            for sample in results_electron.keys():
                electron_results[sample] = [results_electron[sample]]
        else:
            for sample in results_electron.keys():
                electron_results[sample].append(results_electron[sample])
        
        fitter_muon.fit()
        results_muon = fitter_muon.readResults()
        
        TTJet_SingleTop_ratio_muon = muon_histograms['TTJet'].Integral() / muon_histograms['SingleTop'].Integral()
        N_ttbar_muon, N_SingleTop_muon = decombine_result(results_muon['signal'], TTJet_SingleTop_ratio_muon)
        results_muon['TTJet'] = N_ttbar_muon
        results_muon['SingleTop'] = N_SingleTop_muon
        
        if muon_results == {}:#empty
            for sample in results_muon.keys():
                muon_results[sample] = [results_muon[sample]]
        else:
            for sample in results_muon.keys():
                muon_results[sample].append(results_muon[sample])
#        muon_results.append(results_muon)
        
    return electron_results, muon_results

def get_systematic_errors(central_results, channel):
    pass        
if __name__ == '__main__':
    # setup
    bin_edges = [0, 25, 45, 70, 100, 1000]
    bin_widths = [25, 20, 25, 30, 150]
    met_bins_ROOT = ['0-25', '25-45', '45-70', '70-100', '100-inf']
    path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-12-241_V4/'
    file_for_unfolding = File(path_to_files + 'unfolding_merged.root', 'read')
    # possible options:
    # --continue : continue from saved - skips ROOT files, reads from JSON?
    
    # get data from histograms or JSON files
    TTJet_file = File(path_to_files + 'central/TTJet_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    SingleTop_file = File(path_to_files + 'central/SingleTop_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    VJets_file = File(path_to_files + 'central/VJets_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    data_file_electron = File(path_to_files + 'central/ElectronHad_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    data_file_muon = File(path_to_files + 'central/SingleMu_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    muon_QCD_file = File(path_to_files + 'QCD_data_mu.root')
    
    results_electron, results_muon = get_fitted_normalisation(input_files={
                                  'TTJet': TTJet_file,
                                  'SingleTop': SingleTop_file,
                                  'V+Jets':VJets_file,
                                  'data_electron': data_file_electron,
                                  'data_muon': data_file_muon
                                  },
                   met_type='patType1CorrectedPFMet',
                   b_tag_bin='2orMoreBtags',
                   )

    TTJet_fit_results_electron = results_electron['TTJet']
    TTJet_fit_results_muon = results_muon['TTJet']
    # mock input
#    TTJet_fit_results_electron = [(2146, 145), (3399, 254), (3723, 69), (2256, 53), (1722, 91)]
    MADGRAPH_results_electron = [(2146, 145), (3399, 254), (3723, 69), (2256, 53), (1722, 91)]
    
    # get fit values for systematics
    #for systematics we only need the TTJet results!
    # unfold all above
    h_truth, h_measured, h_response = get_unfold_histogram_tuple(file_for_unfolding, 'electron')
    TTJet_fit_results_electron_unfolded = unfold_results(TTJet_fit_results_electron,
                                                         h_truth,
                                                         h_measured,
                                                         h_response,
                                                         'RooUnfoldSvd')
    # calculate the x-sections and
    bin_widths = [25, 20, 25, 30, 150]
    xsection = calculate_xsection(TTJet_fit_results_electron_unfolded, 5050, 0.15)  # L in pb1
    normalisedToOne_xsection = calculate_normalised_xsection(TTJet_fit_results_electron_unfolded, bin_widths, normalise_to_one=True)
    normalised_xsection = calculate_normalised_xsection(TTJet_fit_results_electron_unfolded, bin_widths, normalise_to_one=False)
    normalised_xsection_nounfolding = calculate_normalised_xsection(TTJet_fit_results_electron, bin_widths, normalise_to_one=False)
    
    sum_xsec, sum_xsec_error = 0, 0
    for value, error in xsection:
        sum_xsec += value
        sum_xsec_error += error
    print 'Total x-sec:', sum_xsec, '+-', sum_xsec_error
    
    
    for value, value_nounfolding in zip(normalised_xsection, normalised_xsection_nounfolding):
        print 'unfolded:', value, '\t no unfolding:', value_nounfolding
        
