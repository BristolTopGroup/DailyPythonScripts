'''
Our results are in the form of
data/<centre-of-mass-energy>/<variable>/fit_results/central/fit_results_electron_patType1CorrectedPFMet.txt
data/<centre-of-mass-energy>/<variable>/fit_results/central/fit_results_muon_patType1CorrectedPFMet.txt
for the central results and
data/<centre-of-mass-energy>/<variable>/fit_results/<systematic>/fit_results_electron_patType1CorrectedPFMet.txt
data/<centre-of-mass-energy>/<variable>/fit_results/<systematic>/fit_results_muon_patType1CorrectedPFMet.txt
for the systematics

We have also unfolded data:
data/<centre-of-mass-energy>/<variable>/xsection_measurement_results/kv4/central/normalisation_combined_patType1CorrectedPFMet.txt
and similarily for systematics


This needs to be converted into a ROOT file containing the histograms.
This root file is expected to contain all the templates of the model adhering to a certain naming scheme:
    <observable>__<process> for the "nominal" templates (=not affect by any uncertainty) and
    <observable>__<process>__<uncertainty>__(plus,minus) for the "shifted" templates to be used for template morphing. 

Steps:
1. Get measured data from JSON files (electron, muon, combined)
2. sort them into the new scheme
'''

from uncertainties import ufloat
from math import sqrt
from rootpy.io import root_open

from dps.utils.file_utilities import read_data_from_JSON
from dps.utils.hist_utilities import value_error_tuplelist_to_hist
from dps.config.xsection import XSectionConfig

def get_variable_from(variable='MET', path_to_JSON='data/8TeV', category='central', signal='Higgs', measurement_type='unfolded'):
    global met_type
    
    channel = 'electron'
    electron_results = read_data_from_JSON(path_to_JSON + '/' + variable + '/xsection_measurement_results/kv4/' + category + '/normalisation_' + channel + '_' + met_type + '.txt')
    electron_results_signal = read_data_from_JSON(path_to_JSON + '/' + variable + '/xsection_measurement_results/kv4/' + category + '/normalisation_' + channel + '_' + met_type + '_' + signal + '.txt')
    channel = 'muon'
    muon_results = read_data_from_JSON(path_to_JSON + '/' + variable + '/xsection_measurement_results/kv4/' + category + '/normalisation_' + channel + '_' + met_type + '.txt')
    muon_results_signal = read_data_from_JSON(path_to_JSON + '/' + variable + '/xsection_measurement_results/kv4/' + category + '/normalisation_' + channel + '_' + met_type + '_' + signal + '.txt')
    channel = 'combined'
    combined_results = read_data_from_JSON(path_to_JSON + '/' + variable + '/xsection_measurement_results/kv4/' + category + '/normalisation_' + channel + '_' + met_type + '.txt')
    combined_results_signal = read_data_from_JSON(path_to_JSON + '/' + variable + '/xsection_measurement_results/kv4/' + category + '/normalisation_' + channel + '_' + met_type + '_' + signal + '.txt')
    
    # we are only interested in the measured ttbar, unfolded TTbar for all categories 
    # for_all_categories = ['TTJet_unfolded', 'TTJet_measured']
    # and the scale_up/down, matching up/down and the generators for central (all)
    electron_results_selected = {'Higgs_125':electron_results_signal['TTJet_' + measurement_type],
                                 }
    muon_results_selected = {'Higgs_125':muon_results_signal['TTJet_' + measurement_type],
                                 }
    combined_results_selected = {'Higgs_125':combined_results_signal['TTJet_' + measurement_type],
                                 }
    
    # note on systematics:
    # theta does not understand DATA systematics so they have to be migrated to MADGRAPH
    # there are two ways of doing so:
    # 1. calculate a scale factor based on data central measurement and MADPGRAPH
    # 2. calculate a scale factor based on data central and systematic measurement
    # then apply the scale factor (1- [a-b]/a) to MADGRAPH
    # The second approach seems more right as it takes into account the effect of the systematic instead of the difference between data and Madgraph
    # A way to test this is to calculate the scale factor for ttjet_matching up/down and compare it to the existing distributions
    if measurement_type == 'unfolded':
        electron_results_selected['TTJet'] = electron_results['MADGRAPH']
        muon_results_selected['TTJet'] = muon_results['MADGRAPH']
        combined_results_selected['TTJet'] = combined_results['MADGRAPH']
        
        # theta does not understand DATA with systematics
        if category == 'central':
            electron_results_selected['DATA'] = electron_results['TTJet_unfolded']
            muon_results_selected['DATA'] = muon_results['TTJet_unfolded']
            combined_results_selected['DATA'] = combined_results['TTJet_unfolded']
        else:  # now let's do the systematics
            # read central results
            channel = 'electron'
            tmp_category = 'central'
            tmp_electron_results = read_data_from_JSON(path_to_JSON + '/' + variable + '/xsection_measurement_results/kv4/' + tmp_category + '/normalisation_' + channel + '_' + met_type + '.txt')
            channel = 'muon'
            tmp_muon_results = read_data_from_JSON(path_to_JSON + '/' + variable + '/xsection_measurement_results/kv4/' + tmp_category + '/normalisation_' + channel + '_' + met_type + '.txt')
            channel = 'combined'
            tmp_combined_results = read_data_from_JSON(path_to_JSON + '/' + variable + '/xsection_measurement_results/kv4/' + tmp_category + '/normalisation_' + channel + '_' + met_type + '.txt')
            
            electron_central = tmp_electron_results['TTJet_unfolded']
            muon_central = tmp_muon_results['TTJet_unfolded']
            combined_central = tmp_combined_results['TTJet_unfolded']
            # set systematics
            electron_systematic = electron_results['TTJet_unfolded']
            muon_systematic = muon_results['TTJet_unfolded']
            combined_systematic = combined_results['TTJet_unfolded']
            # calculate scale factors
            electron_results_selected['TTJet'] = morph_systematic(electron_central, electron_systematic, electron_results_selected['TTJet'])
            muon_results_selected['TTJet'] = morph_systematic(muon_central, muon_systematic, muon_results_selected['TTJet'])
            combined_results_selected['TTJet'] = morph_systematic(combined_central, combined_systematic, combined_results_selected['TTJet'])
            
    else:
        if category == 'JES_up':
            met_type += 'JetEnUp'
        elif category == 'JES_down':
            met_type += 'JetEnDown'
        # read initial values
        channel = 'electron'
        electron_initial = read_data_from_JSON(path_to_JSON + '/' + variable + '/fit_results/' + category + '/initial_values_' + channel + '_' + met_type + '.txt')
        electron_fit = read_data_from_JSON(path_to_JSON + '/' + variable + '/fit_results/' + category + '/fit_results_' + channel + '_' + met_type + '.txt')
        channel = 'muon'
        muon_initial = read_data_from_JSON(path_to_JSON + '/' + variable + '/fit_results/' + category + '/initial_values_' + channel + '_' + met_type + '.txt')
        muon_fit = read_data_from_JSON(path_to_JSON + '/' + variable + '/fit_results/' + category + '/fit_results_' + channel + '_' + met_type + '.txt')
        
        electron_results_selected['TTJet'] = electron_results['TTJet_measured']
        muon_results_selected['TTJet'] = muon_results['TTJet_measured']
        
        electron_results_selected['SingleTop'] = electron_fit['SingleTop']
        muon_results_selected['SingleTop'] = muon_fit['SingleTop']
        
        electron_results_selected['QCD'] = electron_fit['QCD']
        muon_results_selected['QCD'] = muon_fit['QCD']
        # theta does not understand DATA with systematics
        if category == 'central':
            electron_results_selected['DATA'] = electron_initial['data']
            muon_results_selected['DATA'] = muon_initial['data']
        
        electron_results_selected['VJets'] = electron_fit['V+Jets']
        muon_results_selected['VJets'] = muon_fit['V+Jets']
        
        # reset met for JES
        if category == 'JES_up':
            met_type = met_type.replace('JetEnUp', '')
        elif category == 'JES_down':
            met_type = met_type.replace('JetEnDown', '')
    
    return electron_results_selected, muon_results_selected, combined_results_selected

def json_to_histograms(results, channel, variable, category):
    global bin_edges
    histograms = {}
    
    for measurement, result in results.iteritems():
        histograms[measurement] = value_error_tuplelist_to_hist(result, bin_edges[variable])
        name = get_name(channel, variable, measurement, category)
        histograms[measurement].SetName(name)
    return histograms

def get_name(channel, variable, sample, category):
    '''
    This function creates names into a format that theta understands
    <channel>_<variable>_<sample>
    and for the systematics
    <channel>_<variable>__<sample>__<systematic>__minus
    <channel>_<variable>__<sample>__<systematic>__plus
    @param channel: the name of the channel (electron, muon, combined)
    @param variable: the name of the variable (MET, HT, ST, MT, WPT)
    @param sample: the name of the sample (ttbar, data, benchmark model)
    @param category: the category, either central or a systematic
    '''
    global vjets_systematics, ttbar_systematics
    # 1. figure out if it is a systematic
    systematic = None
    variation = 'plus'
    if category != 'central':
        if not 'PDFWeights' in category:
            # this is not valid for PDFWeights!
            systematic, variation = category.split('_')
            if category in vjets_systematics or category in ttbar_systematics:
                # take care of the oddities
                # these systematics are of the form VJets_matchingup
                # and need to become VJetsMatching_up
                tmp = category.replace('Jets_m', 'JetsM')  # VJetsMatchingup
                tmp = tmp.replace('Jets_s', 'JetsS')
                tmp = tmp.replace('down', '_down')
                tmp = tmp.replace('up', '_up')  # VJetsMatching_up
                systematic, variation = tmp.split('_')
                
            variation = variation.replace('up', 'plus')
            variation = variation.replace('down', 'minus')
        else:
            # mark up or down, but retain number?
            pass
    # 2. create the name
    name = ''
    if systematic:
        name = '%s_%s__%s__%s__%s' % (channel, variable, sample, systematic, variation)
    else:
        name = '%s_%s__%s' % (channel, variable, sample)
    # Shall we apply any fixes? i.e. add 'data' as a sample instead of TTJet_*
    return name

def morph_systematic(central, systematic, to_be_morphed):
    for i, _ in enumerate(central):
        value_central = ufloat(central[i][0], central[i][1]) 
        value_systematic = ufloat(systematic[i][0], systematic[i][1])
        scale_factor = (1 - (value_central - value_systematic) / value_central)
        to_be_morphed[i][0] *= scale_factor.nominal_value  # change value
        to_be_morphed[i][1] = sqrt(pow(to_be_morphed[i][1] * scale_factor.nominal_value, 2) + scale_factor.std_dev ** 2)  # change error
    return to_be_morphed
                
if __name__ == '__main__':
    measurement_config = XSectionConfig(8)
    generator_systematics = measurement_config.generator_systematics
    categories_and_prefixes = measurement_config.categories_and_prefixes
    met_type = 'patType1CorrectedPFMet'
    measurement_type = 'unfolded'
    signal = 'Higgs'
    variables = bin_edges.keys()
    variables = ['MET']
    category = 'central'
    output_file = root_open('test_' + measurement_type + '.root', 'recreate')
    # TODO: mix in signal
    variable = 'MET'
    category = 'central'
    output_file = root_open('test.root', 'recreate')
    # TODO: mix in signal
    
    vjets_systematics = ['VJets_' + systematic for systematic in generator_systematics]
    ttbar_systematics = ['TTJets_' + systematic for systematic in generator_systematics]
    
    categories = []
    categories.extend(categories_and_prefixes.keys())
    categories.extend(vjets_systematics)
    categories.extend(ttbar_systematics)
    all_histograms = []
    for variable in variables:
        for category in categories:
            electron, muon, combined = get_variable_from(variable,
                                  '/storage/Workspace/Analysis/DailyPythonScripts/src/cross_section_measurement/data/8TeV',
                                  category,
                                  signal=signal,
                                  measurement_type=measurement_type)
            electron_histograms = json_to_histograms(electron, 'electron', variable, category)
            muon_histograms = json_to_histograms(muon, 'muon', variable, category)
            combined_histograms = json_to_histograms(combined, 'combined', variable, category)
            
            all_histograms.extend(electron_histograms.itervalues())
            all_histograms.extend(muon_histograms.itervalues())
            if measurement_type == 'unfolded':
                all_histograms.extend(combined_histograms.itervalues())
    for histogram in all_histograms:
        histogram.Write()
    output_file.close()
    
