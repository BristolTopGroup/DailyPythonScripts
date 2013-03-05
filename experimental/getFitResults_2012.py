# general
from __future__ import division
from optparse import OptionParser
import sys
# rootpy                                                                                                                                                                                                                      
from rootpy.io import File
# DailyPythonScripts
from config.variable_binning_8TeV import variable_bins_ROOT
from tools.Calculation import decombine_result
from tools.Fitting import TMinuitFit
from tools.file_utilities import write_data_to_JSON


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
    electron_results = {}
    electron_initial_values = {}
    muon_results = {}
    muon_initial_values = {}
    for variable_bin in variable_bins_ROOT[variable]:
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
    
def write_fit_results_and_initial_values(category, fit_results_electron, fit_results_muon, initial_values_electron, initial_values_muon):
    global variable, met_type, k_value
    write_data_to_JSON(fit_results_electron, 'data/' + variable + '/fit_results/' + '/kv' + str(k_value) + '/' + category + '/fit_results_electron_' + met_type + '.txt')
    write_data_to_JSON(fit_results_muon, 'data/' + variable + '/fit_results/' + '/kv' + str(k_value) + '/' + category + '/fit_results_muon_' + met_type + '.txt')
    write_data_to_JSON(initial_values_electron, 'data/' + variable + '/fit_results/' + '/kv' + str(k_value) + '/' + category + '/initial_values_electron_' + met_type + '.txt')
    write_data_to_JSON(initial_values_muon, 'data/' + variable + '/fit_results/' + '/kv' + str(k_value) + '/' + category + '/initial_values_muon_' + met_type + '.txt')
    
if __name__ == '__main__':
    # setup
    parser = OptionParser()
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
    
    generator_systematics = [ 'matchingup', 'matchingdown', 'scaleup', 'scaledown' ]
    
    categories_and_prefixes = {
                 'central':'',
                 'BJet_down':'_minusBJet',
                 'BJet_up':'_plusBjet',
                 'JES_down':'_minusJES',
                 'JES_up':'_plusJES',
                 'LightJet_down':'_minusLightJet',
                 'LightJet_up':'_plusLightJet',
                 'PU_down':'_PU_65835mb',
                 'PU_up':'_PU_72765mb'
                 }
    
    (options, args) = parser.parse_args()
    variable = options.variable
    k_value = options.k_value
    met_type = translateOptions[options.metType]
    b_tag_bin = translateOptions[options.bjetbin]
    path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-13-015_V3/'
    
    # possible options:
    # --continue : continue from saved - skips ROOT files, reads from JSON?
    
    # get data from histograms or JSON files
    # data and muon_QCD file with SFs are the same for central measurement and all systematics 
    data_file_electron = File(path_to_files + 'central/SingleElectron_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    data_file_muon = File(path_to_files + 'central/SingleMu_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    muon_QCD_file = File(path_to_files + 'QCD_data_mu.root')
    
    #matching/scale up/down systematics
    for systematic in generator_systematics:
        TTJet_file = File(path_to_files + 'central/TTJets-' + systematic + '_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
        VJets_file = File(path_to_files + 'central/VJets-' + systematic + '_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
        SingleTop_file = File(path_to_files + 'central/SingleTop_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
        muon_QCD_MC_file = File(path_to_files + 'central/QCD_MuEnrichedPt5_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
        
        fit_results_electron, fit_results_muon, initial_values_electron, initial_values_muon = get_fitted_normalisation(
                      input_files={
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data_electron': data_file_electron,
                                   'data_muon': data_file_muon
                                   },
                      variable=variable,                                                                                                                        
                      met_type=met_type,
                      b_tag_bin=b_tag_bin,
                      )
        write_fit_results_and_initial_values(systematic, fit_results_electron, fit_results_muon, initial_values_electron, initial_values_muon)
    
    #central measurement and the rest of the systematics
    for category, prefix in categories_and_prefixes.iteritems():
            TTJet_file = File(path_to_files + category + '/TTJet_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET' + prefix + '.root')
            SingleTop_file = File(path_to_files + category + '/SingleTop_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET' + prefix + '.root')
            VJets_file = File(path_to_files + category + '/VJets_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET' + prefix + '.root')
            muon_QCD_MC_file = File(path_to_files + category + '/QCD_MuEnrichedPt5_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET' + prefix + '.root')
            
            fit_results_electron, fit_results_muon, initial_values_electron, initial_values_muon = get_fitted_normalisation(
                      input_files={
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data_electron': data_file_electron,
                                   'data_muon': data_file_muon
                                   },
                      variable=variable,                                                                                                                        
                      met_type=met_type,
                      b_tag_bin=b_tag_bin,
                      )
            write_fit_results_and_initial_values(category, fit_results_electron, fit_results_muon, initial_values_electron, initial_values_muon)
    
        