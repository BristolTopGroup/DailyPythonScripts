# general
from __future__ import division
from optparse import OptionParser
import sys
import ROOT
# rootpy                                                                                                                                                                                                                      
from rootpy.io import File
# DailyPythonScripts
from tools.Calculation import decombine_result
from tools.Fitting import TMinuitFit
from tools.file_utilities import write_data_to_JSON
from config.summations import b_tag_summations

def get_histograms(channel, input_files, variable, met_type, variable_bin, b_tag_bin, rebin=1):
    histograms = {}
    if not variable in measurement_config.histogram_path_templates.keys():
        print 'Fatal Error: unknown variable ', variable
        sys.exit()
    
    abs_eta = ''
    abs_eta_data = ''
    abs_eta_template = measurement_config.histogram_path_templates[variable] 
    if variable == 'HT':
        abs_eta = abs_eta_template % (analysis_type[channel], variable_bin, channel)
        abs_eta_data = abs_eta
    else:
        if measurement_config.centre_of_mass == 8:
            abs_eta = abs_eta_template % (analysis_type[channel], met_type, variable_bin, channel)
        else:  # hot fix for 2011 data. Needs reprocessing for nicer paths
            lepton = channel.title()
            abs_eta = abs_eta_template % (analysis_type[channel], lepton, met_type, variable_bin, channel)
        if 'JetRes' in met_type:
            abs_eta_data = abs_eta.replace('JetResDown', '')
            abs_eta_data = abs_eta_data.replace('JetResUp', '')
            if 'patPFMet' in met_type:
                abs_eta = abs_eta.replace('patPFMet', 'PFMET')
        else:
            abs_eta_data = abs_eta
    
    for sample, file_name in input_files.iteritems():
        h_abs_eta = None
        if sample == 'data':
            h_abs_eta = get_histogram(file_name, abs_eta_data, b_tag_bin)
        else:
            h_abs_eta = get_histogram(file_name, abs_eta, b_tag_bin)
        h_abs_eta.Rebin(rebin)
        histograms[sample] = h_abs_eta
    
    if channel == 'electron':
        # data-driven QCD
        abs_eta = abs_eta_data.replace('Ref selection', 'QCDConversions')
        h_abs_eta = get_histogram(input_files['data'], abs_eta, '0btag')
        h_abs_eta.Rebin(rebin)
        histograms['QCD'] = h_abs_eta
        # scaling to 10% of data (proper implementation: relIso fit)
        qcd_mc_normalisation =  histograms['QCD'].Integral()
        if not qcd_mc_normalisation == 0:
            histograms['QCD'].Scale(0.1 * histograms['data'].Integral() / histograms['QCD'].Integral())
        
    if channel == 'muon':
        # data-driven QCD
        # for now custom file
        global muon_QCD_file, muon_QCD_MC_file

        h_abs_eta_mc = get_histogram(muon_QCD_MC_file, abs_eta, b_tag_bin)
        h_abs_eta_mc.Rebin(rebin)
        
#        abs_eta = measurement_config.special_muon_histogram
#        h_abs_eta = get_histogram(muon_QCD_file, abs_eta, '')
        abs_eta = abs_eta_data.replace('Ref selection', 'QCD non iso mu+jets ge3j')
        h_abs_eta = get_histogram(input_files['data'], abs_eta, '0btag')
        muon_QCD_normalisation_factor = 1
        h_abs_eta.Rebin(rebin)
        if measurement_config.centre_of_mass == 8:
            muon_QCD_normalisation_factor = h_abs_eta_mc.Integral() / h_abs_eta.Integral()
        if measurement_config.centre_of_mass == 7:
            muon_QCD_normalisation_factor = 0.05 * histograms['data'].Integral() / h_abs_eta.Integral()
        
        h_abs_eta.Scale(muon_QCD_normalisation_factor)
        histograms['QCD'] = h_abs_eta
#        histograms['QCD'].Scale(0.05*histograms['data'].Integral()/histograms['QCD'].Integral())
        
    return histograms

def get_histogram(input_file, histogram_path, b_tag_bin=''):
    b_tag_bin_sum_rules = b_tag_summations
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
                                    rebin=measurement_config.rebin
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

        if (N_SingleTop_before_fit != 0):
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
    output_folder = 'data/' + str(measurement_config.centre_of_mass) + 'TeV/' + variable + '/fit_results/' + category + '/'
    
    write_data_to_JSON(fit_results, output_folder + 'fit_results_' + channel + '_' + met_type + '.txt')
    write_data_to_JSON(initial_values, output_folder + 'initial_values_' + channel + '_' + met_type + '.txt')
    write_data_to_JSON(templates, output_folder + 'templates_' + channel + '_' + met_type + '.txt') 
    
    
if __name__ == '__main__':
    # setup
    parser = OptionParser()
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                      help="set the variable to analyse (MET, HT, ST, MT)")
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                      help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type for analysis of MET, ST or MT")
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=8, type=int,
                      help="set the centre of mass energy for analysis. Default = 8 [TeV]")

    translate_options = {
                        '0':'0btag',
                        '1':'1btag',
                        '2':'2btags',
                        '3':'3btags',
                        '0m':'0orMoreBtag',
                        '1m':'1orMoreBtag',
                        '2m':'2orMoreBtags',
                        '3m':'3orMoreBtags',
                        '4m':'4orMoreBtags',
                        # mettype:
                        'pf':'PFMET',
                        'type1':'patType1CorrectedPFMet'
                        }
    
    
    (options, args) = parser.parse_args()
    from config.cross_section_measurement_common import analysis_types, met_systematics_suffixes, translate_options, ttbar_theory_systematic_prefix, vjets_theory_systematic_prefix
    
    if options.CoM == 8:
        from config.variable_binning_8TeV import variable_bins_ROOT
        import config.cross_section_measurement_8TeV as measurement_config
    elif options.CoM == 7:
        from config.variable_binning_7TeV import variable_bins_ROOT
        import config.cross_section_measurement_7TeV as measurement_config
    else:
        sys.exit('Unknown centre of mass energy')
        
    generator_systematics = measurement_config.generator_systematics
    categories_and_prefixes = measurement_config.categories_and_prefixes
    met_systematics_suffixes = met_systematics_suffixes
    analysis_type = analysis_types
    
    variable = options.variable
    met_type = translate_options[options.metType]
    b_tag_bin = translate_options[options.bjetbin]
    path_to_files = measurement_config.path_to_files
    
    # possible options:
    # --continue : continue from saved - skips ROOT files, reads from JSON?
    
    # get data from histograms or JSON files
    # data and muon_QCD file with SFs are the same for central measurement and all systematics 
    data_file_electron = File(measurement_config.data_file_electron)
    data_file_muon = File(measurement_config.data_file_muon)
    muon_QCD_file = File(measurement_config.muon_QCD_file)
    
    SingleTop_file = File(measurement_config.SingleTop_file)
    muon_QCD_MC_file = File(measurement_config.muon_QCD_MC_file)
    TTJet_file = File(measurement_config.ttbar_category_templates['central'])
    # matching/scale up/down systematics for V+Jets
    for systematic in generator_systematics:
#        TTJet_file = File(measurement_config.generator_systematic_ttbar_templates[systematic])
        VJets_file = File(measurement_config.generator_systematic_vjets_templates[systematic])
        
        
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
        
        write_fit_results_and_initial_values('electron', vjets_theory_systematic_prefix + systematic, fit_results_electron, initial_values_electron, templates_electron)
        write_fit_results_and_initial_values('muon', vjets_theory_systematic_prefix + systematic, fit_results_muon, initial_values_muon, templates_muon)
        
    VJets_file = File(measurement_config.VJets_category_templates['central'])
    # matching/scale up/down systematics for ttbar + jets
    for systematic in generator_systematics:
        TTJet_file = File(measurement_config.generator_systematic_ttbar_templates[systematic])
        
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
        
        write_fit_results_and_initial_values('electron', ttbar_theory_systematic_prefix + systematic, fit_results_electron, initial_values_electron, templates_electron)
        write_fit_results_and_initial_values('muon', ttbar_theory_systematic_prefix + systematic, fit_results_muon, initial_values_muon, templates_muon)
    
    # central measurement and the rest of the systematics
    last_systematic = ''
    for category, prefix in categories_and_prefixes.iteritems():
        TTJet_file = File(measurement_config.ttbar_category_templates[category])
        SingleTop_file = File(measurement_config.SingleTop_category_templates[category])
        VJets_file = File(measurement_config.VJets_category_templates[category])
        muon_QCD_MC_file = File(measurement_config.muon_QCD_MC_category_templates[category])
        
        if last_systematic in ['JES_up', 'JES_down'] and not category in ['JES_up', 'JES_down']:
            data_file_electron = File(measurement_config.data_electron_category_templates['central'])
            data_file_muon = File(measurement_config.data_muon_category_templates['central'])
        
        # Setting up systematic MET for JES up/down samples
        met_type = translate_options[options.metType]
        if category in ['JES_up', 'JES_down']:  # these systematics affect the data as well
            data_file_electron = File(measurement_config.data_electron_category_templates[category])
            data_file_muon = File(measurement_config.data_muon_category_templates[category])
            
        if category == 'JES_up':
            met_type += 'JetEnUp'
            if met_type == 'PFMETJetEnUp':
                met_type = 'patPFMetJetEnUp'
        elif category == 'JES_down':
            met_type += 'JetEnDown'
            if met_type == 'PFMETJetEnDown':
                met_type = 'patPFMetJetEnDown'
        
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
        last_systematic = category
    
    # now do PDF uncertainty    
    SingleTop_file = File(measurement_config.SingleTop_category_templates['central'])
    VJets_file = File(measurement_config.VJets_category_templates['central'])
    muon_QCD_MC_file = File(measurement_config.muon_QCD_MC_category_templates['central'])
    data_file_electron = File(measurement_config.data_electron_category_templates['central'])
    data_file_muon = File(measurement_config.data_muon_category_templates['central'])
    
    for index in range(1, 45):
        category = 'PDFWeights_%d' % index
        TTJet_file = File(measurement_config.pdf_uncertainty_template % index)
        
        
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
    
    SingleTop_file = File(measurement_config.SingleTop_category_templates['central'])
    VJets_file = File(measurement_config.VJets_category_templates['central'])
    muon_QCD_MC_file = File(measurement_config.muon_QCD_MC_category_templates['central'])
    data_file_electron = File(measurement_config.data_electron_category_templates['central'])
    data_file_muon = File(measurement_config.data_muon_category_templates['central']) 
    TTJet_file = File(measurement_config.ttbar_category_templates['central'])
       
    for met_systematic in met_systematics_suffixes:
        #all MET uncertainties except JES & JER - as this is already included
        if 'JetEn' in met_systematic or 'JetRes' in met_systematic or variable == 'HT':#HT is not dependent on MET!
            continue
        category = met_type + met_systematic
        if 'PFMET' in met_type:
            category = category.replace('PFMET', 'patPFMet')
        
        
        fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation('electron',
                      input_files={
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_electron,
                                   },
                      variable=variable,
                      met_type=category,
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
                      met_type=category,
                      b_tag_bin=b_tag_bin,
                      )
        write_fit_results_and_initial_values('electron', category, fit_results_electron, initial_values_electron, templates_electron)
        write_fit_results_and_initial_values('muon', category, fit_results_muon, initial_values_muon, templates_muon)
        
