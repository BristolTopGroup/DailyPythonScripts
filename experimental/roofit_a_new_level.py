from __future__ import division
from optparse import OptionParser
from math import sqrt
import ROOT
# rootpy                                                                                                                                                                                                                      
from rootpy.io import File
from ROOT import RooFit, RooRealVar, RooDataHist, RooArgList, RooHistPdf, RooArgSet, RooAddPdf
from ROOT import RooChi2Var, RooFormulaVar, RooMinuit, TCanvas, RooPlot, RooGaussian, RooProdPdf, RooLinkedList
from config.variable_binning_8TeV import variable_bins_ROOT
import config.cross_section_measurement_8TeV as measurement_config
from tools.Calculation import decombine_result
from uncertainties import ufloat
from tools.Fitting import RooFitFit
        
# copied from 01_get_fit_results.py
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

def get_histograms(channel, input_files, variable, met_type, b_tag_bin, rebin=1):
    global b_tag_bin_VJets
    global electron_control_region, muon_control_region

    histograms = {}
    if not variable in measurement_config.histogram_path_templates.keys():
        print 'Fatal Error: unknown variable ', variable
        sys.exit()
    
    abs_eta = ''
    abs_eta_data = ''
    abs_eta_template = 'TTbar_plus_X_analysis/%s/Ref selection/MET/%s/%s'
    abs_eta = abs_eta_template % (analysis_type[channel], met_type, variable)
    
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
        elif sample == 'V+Jets':
            # extracting the V+Jets template from its specific b-tag bin (>=0 by default) and scaling it to analysis b-tag bin
            h_abs_eta = get_histogram(file_name, abs_eta, b_tag_bin)
            h_abs_eta_VJets_specific_b_tag_bin = get_histogram(file_name, abs_eta, b_tag_bin_VJets)
            try:
                h_abs_eta_VJets_specific_b_tag_bin.Scale(h_abs_eta.Integral() / h_abs_eta_VJets_specific_b_tag_bin.Integral())
                h_abs_eta = h_abs_eta_VJets_specific_b_tag_bin
            except:
                print 'WARNING: V+Jets template from ' + str(file_name) + ', histogram ' + abs_eta + ' in ' + b_tag_bin_VJets + \
                    ' b-tag bin is empty. Using central bin (' + b_tag_bin + '), integral = ' + str(h_abs_eta.Integral())
        else:
            h_abs_eta = get_histogram(file_name, abs_eta, b_tag_bin)
        h_abs_eta.Rebin(rebin)
        histograms[sample] = h_abs_eta
    
    if channel == 'electron':
        global electron_QCD_MC_file
        h_abs_eta_mc = get_histogram(electron_QCD_MC_file, abs_eta, b_tag_bin)
        h_abs_eta_mc.Rebin(rebin)
        # data-driven QCD template extracted from all-inclusive eta distributions
        abs_eta = abs_eta.replace('Ref selection', electron_control_region)
        h_abs_eta = get_histogram(input_files['data'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['V+Jets'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['TTJet'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['SingleTop'], abs_eta, '0btag')
        electron_QCD_normalisation_factor = 1
        h_abs_eta.Rebin(20)

        electron_QCD_normalisation_factor = h_abs_eta_mc.Integral() / h_abs_eta.Integral()
        if electron_QCD_normalisation_factor == 0:
            electron_QCD_normalisation_factor = 1 / h_abs_eta.Integral()

        h_abs_eta.Scale(electron_QCD_normalisation_factor)
        histograms['QCD'] = h_abs_eta
        
    if channel == 'muon':
        # data-driven QCD template extracted from all-inclusive eta distributions
        global muon_QCD_file, muon_QCD_MC_file
        h_abs_eta_mc = get_histogram(muon_QCD_MC_file, abs_eta, b_tag_bin)
        h_abs_eta_mc.Rebin(rebin)
        abs_eta = abs_eta.replace('Ref selection', muon_control_region)
#        abs_eta = measurement_config.special_muon_histogram
#        h_abs_eta = get_histogram(muon_QCD_file, abs_eta, '')
        h_abs_eta = get_histogram(input_files['data'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['TTJet'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['V+Jets'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['SingleTop'], abs_eta, '0btag')
        muon_QCD_normalisation_factor = 1
        h_abs_eta.Rebin(20)
        
        muon_QCD_normalisation_factor = h_abs_eta_mc.Integral() / h_abs_eta.Integral()
        if muon_QCD_normalisation_factor == 0:
            muon_QCD_normalisation_factor = 1 / h_abs_eta.Integral()
        
        h_abs_eta.Scale(muon_QCD_normalisation_factor)
        histograms['QCD'] = h_abs_eta
        
    return histograms

def get_fitted_normalisation_from_ROOT(channel, input_files, variable, met_type, b_tag_bin):
    results = {}
    initial_values = {}
    templates = {}
    
    histograms = get_histograms(channel,
                                    input_files,
                                    variable=variable,
                                    met_type=met_type,
                                    b_tag_bin=b_tag_bin,
                                    rebin=1
                                    )
    # create signal histograms
    h_signal = histograms['TTJet'] + histograms['V+Jets'] + histograms['SingleTop']
    
    N_ttbar_before_fit = histograms['TTJet'].Integral()
    N_SingleTop_before_fit = histograms['SingleTop'].Integral()
    N_vjets_before_fit = histograms['V+Jets'].Integral()
    N_qcd_before_fit = histograms['QCD'].Integral()
    N_signal_before_fit = N_ttbar_before_fit + N_SingleTop_before_fit
    
    N_ttbar_error_before_fit = sum(histograms['TTJet'].errors())
    N_SingleTop_error_before_fit = sum(histograms['SingleTop'].errors())
    N_vjets_error_before_fit = sum(histograms['V+Jets'].errors())
    N_QCD_error_before_fit = sum(histograms['QCD'].errors())
    
#     if (N_SingleTop_before_fit != 0):
#         TTJet_SingleTop_ratio = N_ttbar_before_fit / N_SingleTop_before_fit
#     else:
#         print 'Bin ', variable_bin, ': ttbar/singleTop ratio undefined for %s channel! Setting to 0.' % channel
#         TTJet_SingleTop_ratio = 0
        
    if (N_vjets_before_fit + N_SingleTop_before_fit) != 0:
        TTJet_vjets_ratio = N_ttbar_before_fit / (N_vjets_before_fit + N_SingleTop_before_fit)
    else:
        print 'Bin ', variable_bin, ': ttbar/singleTop ratio undefined for %s channel! Setting to 0.' % channel
        TTJet_vjets_ratio = 0
        
    if (N_SingleTop_before_fit) != 0:
        VJets_SingleTop_ratio = N_vjets_before_fit / N_SingleTop_before_fit
    else:
        print 'Bin ', variable_bin, ': vjets/singleTop ratio undefined for %s channel! Setting to 0.' % channel
        VJets_SingleTop_ratio = 0
    
    fit_histograms = {
                                      'data':histograms['data'],
                                      'signal':h_signal,
#                                       'SingleTop': histograms['SingleTop'],
#                                      'background':histograms['V+Jets']+histograms['QCD']
#                                       'V+Jets':histograms['V+Jets'],
                                      'QCD':histograms['QCD']
                                      }
    
    fitter = RooFitFit(histograms=fit_histograms, fit_boundries=(0., 1000.))
    
#     fitter.set_fit_constraints({'QCD': 2.0, 'V+Jets': 0.5})
    print "FITTING: " + channel + '_' + variable + '_' + met_type + '_' + b_tag_bin
    fitter.fit()    

    fit_results = fitter.readResults()
    normalisation = fitter.normalisation
    normalisation_errors = fitter.normalisation_errors
#     N_ttbar, N_SingleTop = decombine_result(fit_results['signal'], TTJet_SingleTop_ratio)
    N_ttbar, N_vjets_singletop = decombine_result(fit_results['signal'], TTJet_vjets_ratio)
    N_vjets, N_SingleTop = decombine_result(N_vjets_singletop, VJets_SingleTop_ratio)
    
    fit_results['TTJet'] = N_ttbar
    fit_results['V+Jets'] = N_vjets
    fit_results['SingleTop'] = N_SingleTop
#     fit_results['SingleTop'] = N_SingleTop
    normalisation['TTJet'] = N_ttbar_before_fit
    normalisation['SingleTop'] = N_SingleTop_before_fit
    normalisation['V+Jets'] = N_vjets_before_fit
    normalisation_errors['TTJet'] = N_ttbar_error_before_fit
    normalisation_errors['SingleTop'] = N_SingleTop_error_before_fit
    normalisation_errors['V+Jets'] = N_vjets_error_before_fit
    
    results = fit_results
    for variable_bin in variable_bins_ROOT[variable]:
        pass
        
    return results, normalisation, None

if __name__ == '__main__':
    # setup
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data',
                  help="set output path for JSON files")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                      help="set the variable to analyse (MET, HT, ST, MT)")
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                      help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("--bjetbin-vjets", dest="bjetbin_VJets", default='0m',
                      help="set b-jet multiplicity for V+Jets samples. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
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
    from config.summations_common import b_tag_summations

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
    b_tag_bin_VJets = translate_options[options.bjetbin_VJets]
    path_to_files = measurement_config.path_to_files
    output_path = options.path
    
    # possible options:
    # --continue : continue from saved - skips ROOT files, reads from JSON?
    
    # get data from histograms or JSON files
    # data and muon_QCD file with SFs are the same for central measurement and all systematics 
    data_file_electron = File(measurement_config.data_file_electron)
    data_file_muon = File(measurement_config.data_file_muon)
    muon_QCD_file = File(measurement_config.muon_QCD_file)
    
    SingleTop_file = File(measurement_config.SingleTop_file)
    muon_QCD_MC_file = File(measurement_config.muon_QCD_MC_file)
    electron_QCD_MC_file = File(measurement_config.electron_QCD_MC_file)
    TTJet_file = File(measurement_config.ttbar_category_templates['central'])
    VJets_file = File(measurement_config.VJets_category_templates['central'])
    electron_control_region = measurement_config.electron_control_region
    muon_control_region = measurement_config.muon_control_region
    
    input_files = {
                   'TTJet': TTJet_file,
                   'SingleTop': SingleTop_file,
                   'V+Jets': VJets_file,
                   'data': data_file_electron,
                   }
    fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation_from_ROOT('electron',
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
    
    print 'TTJet:', fit_results_electron['TTJet'], '(',initial_values_electron['TTJet'], ')'
    print 'Sum = {:10.2f}'.format(sum(fit_results_electron['TTJet']))
    print
    print 'SingleTop:', fit_results_electron['SingleTop'], '(',initial_values_electron['SingleTop'], ')'
    print 'Sum = {:10.2f}'.format(sum(fit_results_electron['SingleTop']))
    print
    print 'V+Jets:', fit_results_electron['V+Jets'], '(',initial_values_electron['V+Jets'], ')'
    print 'Sum = {:10.2f}'.format(sum(fit_results_electron['V+Jets']))
    print
    print 'QCD:', fit_results_electron['QCD'], '(',initial_values_electron['QCD'], ')'
    print 'Sum = {:10.2f}'.format(sum(fit_results_electron['QCD']))
