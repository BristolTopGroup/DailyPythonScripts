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

met_systematics_suffixes = [
        "ElectronEnUp",
        "ElectronEnDown",
        "MuonEnUp",
        "MuonEnDown",
        "TauEnUp",
        "TauEnDown",
        "JetResUp",
        "JetResDown",
        "JetEnUp",
        "JetEnDown",
        "UnclusteredEnUp",
        "UnclusteredEnDown"
        ]

analysisType = {
                'electron':'EPlusJets',
                'muon':'MuPlusJets'
                }

def get_histograms(channel, input_files, variable, met_type, variable_bin, b_tag_bin, rebin=1):
    histograms = {}
    if variable == 'MET':
        abs_eta = 'TTbar_plus_X_analysis/%s/Ref selection/Binned_MET_Analysis/%s_bin_%s/%s_absolute_eta' % (analysisType[channel], met_type, variable_bin, channel)
    elif variable == 'HT':
        abs_eta = 'TTbar_plus_X_analysis/%s/Ref selection/Binned_HT_Analysis/HT_bin_%s/%s_absolute_eta' % (analysisType[channel], variable_bin, channel)
    elif variable == 'ST':
        abs_eta = 'TTbar_plus_X_analysis/%s/Ref selection/Binned_ST_Analysis/ST_with_%s_bin_%s/%s_absolute_eta' % (analysisType[channel], met_type, variable_bin, channel)
    elif variable == 'MT':
        abs_eta = 'TTbar_plus_X_analysis/%s/Ref selection/Binned_MT_Analysis/MT_with_%s_bin_%s/%s_absolute_eta' % (analysisType[channel], met_type, variable_bin, channel)
    else:
        print 'Fatal Error: unknown variable ', variable
        sys.exit()
    
    for sample, file_name in input_files.iteritems():
        h_abs_eta = get_histogram(file_name, abs_eta, b_tag_bin)
        h_abs_eta.Rebin(rebin)
        histograms[sample] = h_abs_eta
    
    if channel == 'electron':
        # data-driven QCD
        abs_eta = abs_eta.replace('Ref selection', 'QCDConversions')
        h_abs_eta = get_histogram(input_files['data'], abs_eta, '0btag')
        h_abs_eta.Rebin(rebin)
        histograms['QCD'] = h_abs_eta
        #scaling to 10% of data (proper implementation: relIso fit)
        histograms['QCD'].Scale(0.1*histograms['data'].Integral()/histograms['QCD'].Integral())
        
    if channel == 'muon':
        # data-driven QCD
        # for now custom file
        global muon_QCD_file, muon_QCD_MC_file

        h_abs_eta_mc = get_histogram(muon_QCD_MC_file, abs_eta, b_tag_bin)
        h_abs_eta_mc.Rebin(rebin)
        
        abs_eta = 'muon_AbsEta_0btag'
        h_abs_eta = get_histogram(muon_QCD_file, abs_eta, '')
        h_abs_eta.Rebin(rebin)
        muon_QCD_normalisation_factor = h_abs_eta_mc.Integral()/h_abs_eta.Integral()
        h_abs_eta.Scale(muon_QCD_normalisation_factor)
        histograms['QCD'] = h_abs_eta
#        histograms['QCD'].Scale(0.05*histograms['data'].Integral()/histograms['QCD'].Integral())
        
    return histograms

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
        histogram = input_file.Get(histogram_path + '_' + b_tag_bins_to_sum[0]).Clone()
        for bin_i in b_tag_bins_to_sum[1:]:
            histogram += input_file.Get(histogram_path + '_' + bin_i)
    else:
        if b_tag_bin == '':
            histogram = input_file.Get(histogram_path)
        else:
            histogram = input_file.Get(histogram_path + '_' + b_tag_bin)
    
    return histogram.Clone()

def get_fitted_normalisation(channel, input_files, variable, met_type, b_tag_bin, JSON=False):
    if JSON:
        return get_fitted_normalisation_from_JSON(channel, input_files, variable, met_type)  # no b_tag_bin as files are specific
    else:
        return get_fitted_normalisation_from_ROOT(channel, input_files, variable, met_type, b_tag_bin)

def get_fitted_normalisation_from_JSON(channel, input_files, variable, met_type):
    pass

def get_fitted_normalisation_from_ROOT(channel, input_files, variable, met_type, b_tag_bin):
    results = {}
    initial_values = {}
    templates = {}
    for variable_bin in variable_bins_ROOT[variable]:
        histograms = get_histograms(channel,
                                    input_files,
                                    variable=variable,
                                    met_type=met_type,
                                    variable_bin=variable_bin,
                                    b_tag_bin=b_tag_bin,
                                    rebin=2
                                    )
        # prepare histograms
        # normalise histograms
        
        # create signal histograms
        h_eta_signal = histograms['TTJet'] + histograms['SingleTop']
        fitter = TMinuitFit(histograms={
                                      'data':histograms['data'],
                                      'signal':h_eta_signal,
#                                      'background':histograms['V+Jets']+histograms['QCD']
                                      'V+Jets':histograms['V+Jets'],
                                      'QCD':histograms['QCD']
                                      })
        
        fitter.fit()
        fit_results = fitter.readResults()
        normalisation = fitter.normalisation
        
        N_ttbar_before_fit = histograms['TTJet'].Integral()
        N_SingleTop_before_fit = histograms['SingleTop'].Integral()

        if (N_SingleTop_before_fit!=0):
            TTJet_SingleTop_ratio = N_ttbar_before_fit / N_SingleTop_before_fit
        else:
            print 'Bin ', variable_bin, ': ttbar/singleTop ratio undefined for %s channel! Setting to 0.' % channel
            TTJet_SingleTop_ratio = 0

        N_ttbar, N_SingleTop = decombine_result(fit_results['signal'], TTJet_SingleTop_ratio)
        
        
        fit_results['TTJet'] = N_ttbar
        fit_results['SingleTop'] = N_SingleTop
        normalisation['TTJet'] = N_ttbar_before_fit
        normalisation['SingleTop'] = N_SingleTop_before_fit
        
        if results == {}:  # empty
            initial_values['data'] = [normalisation['data']]
            templates['data'] = [fitter.vectors['data']]
            for sample in fit_results.keys():
                results[sample] = [fit_results[sample]]
                initial_values[sample] = [normalisation[sample]]
                if not sample == 'TTJet' and not sample == 'SingleTop':
                    templates[sample] = [fitter.vectors[sample]]
        else:
            initial_values['data'].append(normalisation['data'])
            templates['data'].append(fitter.vectors['data'])
            for sample in fit_results.keys():
                results[sample].append(fit_results[sample])
                initial_values[sample].append(normalisation[sample])
                if not sample == 'TTJet' and not sample == 'SingleTop':
                    templates[sample].append(fitter.vectors[sample])
        
    return results, initial_values, templates
    
def write_fit_results_and_initial_values(channel, category, fit_results, initial_values, templates):
    global variable, met_type
    write_data_to_JSON(fit_results, 'data/' + variable + '/fit_results/' + category + '/fit_results_' + channel + '_' + met_type + '.txt')
    write_data_to_JSON(initial_values, 'data/' + variable + '/fit_results/' + category + '/initial_values_' + channel + '_' + met_type + '.txt')
    write_data_to_JSON(templates, 'data/' + variable + '/fit_results/' + category + '/templates_' + channel + '_' + met_type + '.txt') 
    
if __name__ == '__main__':
    # setup
    parser = OptionParser()
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                      help="set the variable to analyse (MET, HT, ST, MT)")
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                      help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type for analysis of MET, ST or MT")

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
        
        fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation('electron',
                      input_files={
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_electron,
                                   },
                      variable=variable,                                                                                                                        
                      met_type=met_type,
                      b_tag_bin=b_tag_bin,
                      )
        
        fit_results_muon, initial_values_muon, templates_muon = get_fitted_normalisation('muon',
                      input_files={
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_muon,
                                   },
                      variable=variable,                                                                                                                        
                      met_type=met_type,
                      b_tag_bin=b_tag_bin,
                      )
        
        write_fit_results_and_initial_values('electron', systematic, fit_results_electron, initial_values_electron, templates_electron)
        write_fit_results_and_initial_values('muon', systematic, fit_results_muon, initial_values_muon, templates_muon)
    
    #central measurement and the rest of the systematics
    for category, prefix in categories_and_prefixes.iteritems():
        TTJet_file = File(path_to_files + category + '/TTJet_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET' + prefix + '.root')
        SingleTop_file = File(path_to_files + category + '/SingleTop_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET' + prefix + '.root')
        VJets_file = File(path_to_files + category + '/VJets_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET' + prefix + '.root')
        muon_QCD_MC_file = File(path_to_files + category + '/QCD_MuEnrichedPt5_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET' + prefix + '.root')
        
        #Setting up systematic MET for JES up/down samples
        met_type = translateOptions[options.metType]
        if category == 'JES_up':
            data_file_electron = File(path_to_files + category + '/SingleElectron_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET' + prefix + '.root')
            data_file_muon = File(path_to_files + category + '/SingleMu_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET' + prefix + '.root')
            met_type += 'JetEnUp'
        elif category == 'JES_down':
            data_file_electron = File(path_to_files + category + '/SingleElectron_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET' + prefix + '.root')
            data_file_muon = File(path_to_files + category + '/SingleMu_5814pb_PFElectron_PFMuon_PF2PATJets_PFMET' + prefix + '.root')
            met_type += 'JetEnDown'
        
        fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation('electron',
                      input_files={
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_electron,
                                   },
                      variable=variable,                                                                                                                        
                      met_type=met_type,
                      b_tag_bin=b_tag_bin,
                      )
        
        fit_results_muon, initial_values_muon, templates_muon = get_fitted_normalisation('muon',
                      input_files={
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_muon,
                                   },
                      variable=variable,                                                                                                                        
                      met_type=met_type,
                      b_tag_bin=b_tag_bin,
                      )
        write_fit_results_and_initial_values('electron', category, fit_results_electron, initial_values_electron, templates_electron)
        write_fit_results_and_initial_values('muon', category, fit_results_muon, initial_values_muon, templates_muon)
