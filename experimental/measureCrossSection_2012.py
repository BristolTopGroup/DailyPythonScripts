# general
from __future__ import division
from array import array
from optparse import OptionParser
import sys
# rootpy                                                                                                                                                                                                                      
from rootpy.io import File
from rootpy import asrootpy
# DailyPythonScripts
from tools.Calculation import calculate_xsection, calculate_normalised_xsection, decombine_result
from tools.hist_utilities import hist_to_value_error_tuplelist, value_error_tuplelist_to_hist
from tools.Unfolding import Unfolding
import config.RooUnfold as unfoldCfg
from tools.Fitting import TMinuitFit
from tools.file_utilities import write_data_to_JSON

def unfold_results(results, h_truth, h_measured, h_response, method):
    global bin_edges

    h_data = value_error_tuplelist_to_hist(results, bin_edges)
    unfolding = Unfolding(h_truth, h_measured, h_response, method=method)
    h_unfolded_data = unfolding.unfold(h_data)
    
    return hist_to_value_error_tuplelist(h_unfolded_data)

def get_unfold_histogram_tuple(inputfile, variable, channel, met_type):
    global bin_edges
    folder = None
    if not 'HT' in variable:
        folder = inputfile.Get('unfolding_%s_analyser_%s_channel_%s' % (variable, channel, met_type))
    else:
        folder = inputfile.Get('unfolding_%s_analyser_%s_channel' % (variable, channel))
        
    n_bins = len(bin_edges) - 1
    bin_edge_array = array('d', bin_edges)
    
    h_truth = asrootpy(folder.truth.Rebin(n_bins, 'truth', bin_edge_array))
    h_measured = asrootpy(folder.measured.Rebin(n_bins, 'measured', bin_edge_array))
    h_response = folder.response_without_fakes_AsymBins  # response_AsymBins
    
    nEvents = inputfile.EventFilter.EventCounter.GetBinContent(1)#number of processed events 
    lumiweight = 225.19 * 5814 / nEvents #ttbar x-section = 225.2pb, lumi = 5814pb-1
    h_truth.Scale(lumiweight)
    h_measured.Scale(lumiweight)
    h_response.Scale(lumiweight)
    return h_truth, h_measured, h_response

def get_histograms(input_files, variable, met_type, variable_bin, b_tag_bin, rebin=1):
    electron_histograms = {}
    muon_histograms = {}
    if variable == 'MET':
        electron_abs_eta = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_MET_Analysis/%s_bin_%s/electron_absolute_eta' % (met_type, variable_bin)
        muon_abs_eta = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Binned_MET_Analysis/%s_bin_%s/muon_absolute_eta' % (met_type, variable_bin)
    elif variable == 'HT':
        electron_abs_eta = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_HT_Analysis/HT_bin_%s/electron_absolute_eta' % (variable_bin)
        muon_abs_eta = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Binned_HT_Analysis/HT_bin_%s/muon_absolute_eta' % (variable_bin)
    elif variable == 'ST':
        electron_abs_eta = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_ST_Analysis/ST_with_%s_bin_%s/electron_absolute_eta' % (met_type, variable_bin)
        muon_abs_eta = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Binned_ST_Analysis/ST_with_%s_bin_%s/muon_absolute_eta' % (met_type, variable_bin)
    elif variable == 'MT':
        electron_abs_eta = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_MT_Analysis/MT_with_%s_bin_%s/electron_absolute_eta' % (met_type, variable_bin)
        muon_abs_eta = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Binned_MT_Analysis/MT_with_%s_bin_%s/muon_absolute_eta' % (met_type, variable_bin)
    else:
        print 'Fatal Error: unknown variable ', variable
        sys.exit()
    
    for sample, file_name in input_files.iteritems():
        h_electron_abs_eta = get_histogram(file_name, electron_abs_eta, b_tag_bin)
        h_muon_abs_eta = get_histogram(file_name, muon_abs_eta, b_tag_bin)

        h_electron_abs_eta.Rebin(rebin)
        h_muon_abs_eta.Rebin(rebin)
        
        electron_histograms[sample] = h_electron_abs_eta
        muon_histograms[sample] = h_muon_abs_eta
    
    if 'data_electron' in input_files.keys():
        # data-driven QCD
        electron_abs_eta.replace('Ref selection', 'QCDConversions')
        h_electron_abs_eta = get_histogram(input_files['data_electron'], electron_abs_eta, '0btag')
        h_electron_abs_eta.Rebin(rebin)
        electron_histograms['QCD'] = h_electron_abs_eta
        
    if 'data_muon' in input_files.keys():
        # data-driven QCD
        # for now custom file
        global muon_QCD_file, muon_QCD_MC_file

        h_muon_abs_eta_mc = get_histogram(muon_QCD_MC_file, muon_abs_eta, b_tag_bin)
        h_muon_abs_eta_mc.Rebin(rebin)
        muon_QCD_normalisation_factor = h_muon_abs_eta_mc.Integral()
        
        muon_abs_eta = 'muon_AbsEta_0btag'
        h_muon_abs_eta = get_histogram(muon_QCD_file, muon_abs_eta, '')
        h_muon_abs_eta.Rebin(rebin)
        h_muon_abs_eta.Scale(muon_QCD_normalisation_factor)
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
    
    return histogram.Clone()

def get_fitted_normalisation(input_files, variable, met_type, b_tag_bin, JSON=False):
    if JSON:
        return get_fitted_normalisation_from_JSON(input_files, variable, met_type)  # no b_tag_bin as files are specific
    else:
        return get_fitted_normalisation_from_ROOT(input_files, variable, met_type, b_tag_bin)

def get_fitted_normalisation_from_JSON(input_files, variable, met_type):
    pass

def get_fitted_normalisation_from_ROOT(input_files, variable, met_type, b_tag_bin):
    global variable_bins_ROOT
    electron_results = {}
    electron_initial_values = {}
    muon_results = {}
    muon_initial_values = {}
    for variable_bin in variable_bins_ROOT:
        electron_histograms, muon_histograms = get_histograms(input_files={
                                  'TTJet': TTJet_file,
                                  'SingleTop': SingleTop_file,
                                  'V+Jets':VJets_file,
                                  'data_electron': data_file_electron,
                                  'data_muon': data_file_muon
                                  },
                   variable=variable,
                   met_type=met_type,
                   variable_bin=variable_bin,
                   b_tag_bin=b_tag_bin,
                   rebin=2
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

        if (N_SingleTop_before_fit_electron!=0):
            TTJet_SingleTop_ratio_electron = N_ttbar_before_fit_electron / N_SingleTop_before_fit_electron
        else:
            print 'Bin ', variable_bin, ': ttbar/singleTop ratio undefined for electrons! Setting to 0.'
            TTJet_SingleTop_ratio_electron = 0

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
        
        if (N_SingleTop_before_fit_muon!=0):
            TTJet_SingleTop_ratio_muon = N_ttbar_before_fit_muon / N_SingleTop_before_fit_muon
        else:
            print 'Bin ', variable_bin, ': ttbar/singleTop ratio undefined for muons! Setting to 0.'
            TTJet_SingleTop_ratio_muon = 0
        
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
    
def unfold_and_measure_cross_section(TTJet_fit_results, channel):
    global variable, met_type
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
    
    write_data_to_JSON(TTJet_fit_results, 'data/TTJet_fit_results_' + channel + '.txt')
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
    write_data_to_JSON(normalisation_unfolded, 'data/normalisation_' + channel + '_unfolded.txt')
    
    # calculate the x-sections and
#    bin_widths = [25, 20, 25, 30, 50, 150]
    TTJet_xsection = calculate_xsection(TTJet_fit_results, 5814, 0.15)  # L in pb1
    TTJet_xsection_unfolded = calculate_xsection(TTJet_fit_results_unfolded, 5814, 0.15)  # L in pb1
    MADGRAPH_xsection = calculate_xsection(MADGRAPH_results, 5814, 0.15)  # L in pb1
    POWHEG_xsection = calculate_xsection(POWHEG_results, 5814, 0.15)  # L in pb1
    MCATNLO_xsection = calculate_xsection(MCATNLO_results, 5814, 0.15)  # L in pb1
    matchingdown_xsection = calculate_xsection(matchingdown_results, 5814, 0.15)  # L in pb1
    matchingup_xsection = calculate_xsection(matchingup_results, 5814, 0.15)  # L in pb1
    scaledown_xsection = calculate_xsection(scaledown_results, 5814, 0.15)  # L in pb1
    scaleup_xsection = calculate_xsection(matchingup_results, 5814, 0.15)  # L in pb1
    
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
    write_data_to_JSON(xsection_unfolded, 'data/xsection_' + channel + '_unfolded.txt')
    
    TTJet_normalised_to_one_xsection = calculate_normalised_xsection(TTJet_fit_results, bin_widths, normalise_to_one=True)
    TTJet_normalised_to_one_xsection_unfolded = calculate_normalised_xsection(TTJet_fit_results_unfolded, bin_widths, normalise_to_one=True)
    MADGRAPH_normalised_to_one_xsection = calculate_normalised_xsection(MADGRAPH_results, bin_widths, normalise_to_one=True)
    POWHEG_normalised_to_one_xsection = calculate_normalised_xsection(POWHEG_results, bin_widths, normalise_to_one=True)
    MCATNLO_normalised_to_one_xsection = calculate_normalised_xsection(MCATNLO_results, bin_widths, normalise_to_one=True)
    matchingdown_normalised_to_one_xsection = calculate_normalised_xsection(matchingdown_results, bin_widths, normalise_to_one=True)
    matchingup_normalised_to_one_xsection = calculate_normalised_xsection(matchingup_results, bin_widths, normalise_to_one=True)
    scaledown_normalised_to_one_xsection = calculate_normalised_xsection(scaledown_results, bin_widths, normalise_to_one=True)
    scaleup_normalised_to_one_xsection = calculate_normalised_xsection(scaleup_results, bin_widths, normalise_to_one=True)
    
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
    write_data_to_JSON(normalised_to_one_xsection_unfolded, 'data/normalised_to_one_xsection_' + channel + '_unfolded.txt')
    
    TTJet_normalised_xsection = calculate_normalised_xsection(TTJet_fit_results, bin_widths, normalise_to_one=False)
    TTJet_normalised_xsection_unfolded = calculate_normalised_xsection(TTJet_fit_results_unfolded, bin_widths, normalise_to_one=False)
    MADGRAPH_normalised_xsection = calculate_normalised_xsection(MADGRAPH_results, bin_widths, normalise_to_one=False)
    POWHEG_normalised_xsection = calculate_normalised_xsection(POWHEG_results, bin_widths, normalise_to_one=False)
    MCATNLO_normalised_xsection = calculate_normalised_xsection(MCATNLO_results, bin_widths, normalise_to_one=False)
    matchingdown_normalised_xsection = calculate_normalised_xsection(matchingdown_results, bin_widths, normalise_to_one=False)
    matchingup_normalised_xsection = calculate_normalised_xsection(matchingup_results, bin_widths, normalise_to_one=False)
    scaledown_normalised_xsection = calculate_normalised_xsection(scaledown_results, bin_widths, normalise_to_one=False)
    scaleup_normalised_xsection = calculate_normalised_xsection(scaleup_results, bin_widths, normalise_to_one=False)

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
    write_data_to_JSON(normalised_xsection_unfolded, 'data/normalised_xsection_' + channel + '_unfolded.txt')    
    
    sum_xsec, sum_xsec_error = 0, 0
    for value, error in TTJet_xsection_unfolded:
        sum_xsec += value
        sum_xsec_error += error
    print 'Total x-sec in ' +channel + ' channel:', sum_xsec, '+-', sum_xsec_error
    
    for gen, value, value_nounfolding in zip(MADGRAPH_normalised_xsection, TTJet_normalised_xsection_unfolded, TTJet_normalised_xsection):
        print 'gen:', gen, 'unfolded:', value, '\t no unfolding:', value_nounfolding


def write_cross_section():
    pass

if __name__ == '__main__':
    # setup
    parser = OptionParser()
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                      help="set the variable to analyse (MET, HT, ST, MT)")
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                      help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type for analysis of MET, ST or MT")
    parser.add_option("-u", "--unfolding",
                      action="store_false", dest="unfolding", default=True,
                      help="use unfolding")
    parser.add_option("-k", "--k_value", type='int',
                      dest="k_value", default=6,
                      help="k-value for SVD unfolding")
#    parser.add_option("-t", "--test",
#                  action="store_true", dest="test", default=False,
#                  help="Test analysis on first bin only")
#    parser.add_option("-c", "--constrain", dest="constrain", default=' ', #default='QCD,Z/W',
#                  help="Sets which constrains to use. Constrains separated by commas: QCD, Z/W, ZJets, WJets, VV")
    parser.add_option("-a", "--analysisType", dest="analysisType", default='EPlusJets',
                  help="set analysis type: EPlusJets or MuPlusJets")
    #more for: plot templates, plot fits
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
    
    (options, args) = parser.parse_args()
    variable = options.variable
    met_type = translateOptions[options.metType]
    b_tag_bin = translateOptions[options.bjetbin]
    do_unfolding = options.unfolding
    unfoldCfg.SVD_k_value = options.k_value
    path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-13-015_V3/'
    
    if variable == 'MET':
        bin_edges = [0, 25, 45, 70, 100, 150, 250]
        bin_widths = [25, 20, 25, 30, 50, 100]
        variable_bins_ROOT = ['0-25', '25-45', '45-70', '70-100', '100-150', '150-inf']
    elif variable == 'HT':
        bin_edges = [50, 150, 250, 350, 450, 650, 1100, 2000]
        bin_widths = [100, 100, 100, 100, 200, 450, 900]
        variable_bins_ROOT = ['50-150', '150-250', '250-350', '350-450', '450-650', '650-1100', '1100-inf']
    elif variable == 'ST':
        bin_edges = [150, 250, 350, 450, 550, 750, 1250, 2000]
        bin_widths = [100, 100, 100, 100, 200, 500, 750]
        variable_bins_ROOT = ['150-250', '250-350', '350-450', '450-550', '550-750', '750-1250', '1250-inf']
    elif variable == 'MT':
        bin_edges = [0, 40, 65, 85, 150, 300]
        bin_widths = [40, 25, 20, 65, 150]
        variable_bins_ROOT = ['0-40', '40-65', '65-85', '85-150', '150-inf']
    else:
        print 'Fatal Error: unknown variable ', variable
        sys.exit()
    
    file_for_unfolding = File(path_to_files + 'unfolding_merged.root', 'read')
    file_for_powheg = File(path_to_files + 'unfolding_TTJets_8TeV_powheg.root', 'read')
#    file_for_pythia = File(path_to_files + 'unfolding_TTJets_8TeV_pythia.root', 'read')
    file_for_mcatnlo = File(path_to_files + 'unfolding_TTJets_8TeV_mcatnlo.root', 'read')
    
    file_for_scaledown = File(path_to_files + 'unfolding_TTJets_8TeV_scaledown.root', 'read')
    file_for_scaleup = File(path_to_files + 'unfolding_TTJets_8TeV_scaleup.root', 'read')
    file_for_matchingdown = File(path_to_files + 'unfolding_TTJets_8TeV_matchingdown.root', 'read')
    file_for_matchingup = File(path_to_files + 'unfolding_TTJets_8TeV_matchingup.root', 'read')
    # possible options:
    # --continue : continue from saved - skips ROOT files, reads from JSON?
    
    # get data from histograms or JSON files
    TTJet_file = File(path_to_files + 'central/TTJet_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    SingleTop_file = File(path_to_files + 'central/SingleTop_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    VJets_file = File(path_to_files + 'central/VJets_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    data_file_electron = File(path_to_files + 'central/SingleElectron_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    data_file_muon = File(path_to_files + 'central/SingleMu_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    muon_QCD_file = File(path_to_files + 'QCD_data_mu.root')
    muon_QCD_MC_file = File(path_to_files + 'central/QCD_MuEnrichedPt5_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    
    fit_results_electron, fit_results_muon, initial_values_electron, initial_values_muon = get_fitted_normalisation(
                input_files={
                                  'TTJet': TTJet_file,
                                  'SingleTop': SingleTop_file,
                                  'V+Jets':VJets_file,
                                  'data_electron': data_file_electron,
                                  'data_muon': data_file_muon
                                  },
                variable=variable,                                                                                                                        
                met_type=met_type,
                b_tag_bin=b_tag_bin,
                   )
    write_fit_results_and_initial_values(fit_results_electron, fit_results_muon, initial_values_electron, initial_values_muon)
    
    #continue with only TTJet
    TTJet_fit_results_electron = fit_results_electron['TTJet']
    TTJet_fit_results_muon = fit_results_muon['TTJet']
    
    # get t values for systematics
    # for systematics we only need the TTJet results!
    # unfold all above
    
    unfold_and_measure_cross_section(TTJet_fit_results_electron, 'electron')
    unfold_and_measure_cross_section(TTJet_fit_results_electron, 'muon')
    