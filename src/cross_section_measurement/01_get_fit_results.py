#
#    Run this script writing the output to a file: plots/fitchecks/correlation_<variable>.txt where variable=MET/HT/ST/MT/WPT.
#    This output .txt file is then be used by the 98_fit_cross_checks.py script to extract the correlation coefficients from the fit.

# general
from __future__ import division
from optparse import OptionParser
import sys
# rootpy                                                                                                                                                                                                                      
from rootpy.io import File
# DailyPythonScripts
from tools.Calculation import decombine_result, combine_complex_results
from tools.Fitting import TMinuitFit, RooFitFit
from tools.file_utilities import write_data_to_JSON
from tools.ROOT import set_root_defaults

def get_histograms(channel, input_files, variable, met_type, variable_bin, b_tag_bin, rebin=1):
    global b_tag_bin_VJets
    global electron_control_region, muon_control_region

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
        abs_eta = abs_eta_template % (analysis_type[channel], met_type, variable_bin, channel)

        if 'JetRes' in met_type:
            abs_eta_data = abs_eta.replace('JetResDown', '')
            abs_eta_data = abs_eta_data.replace('JetResUp', '')
            if 'patPFMet' in met_type:
                abs_eta = abs_eta.replace('patPFMet', 'PFMET')
        else:
            abs_eta_data = abs_eta
    
    for sample, file_name in input_files.iteritems():
        if not file_name:
            continue
        h_abs_eta = None
        if sample == 'data':
            h_abs_eta = get_histogram(file_name, abs_eta_data, b_tag_bin)
        elif sample == 'V+Jets':
            #extracting the V+Jets template from its specific b-tag bin (>=0 by default) and scaling it to analysis b-tag bin
            h_abs_eta = get_histogram(file_name, abs_eta, b_tag_bin)
            h_abs_eta_VJets_specific_b_tag_bin = get_histogram(file_name, abs_eta, b_tag_bin_VJets)
            try:
                h_abs_eta_VJets_specific_b_tag_bin.Scale(h_abs_eta.Integral()/h_abs_eta_VJets_specific_b_tag_bin.Integral())
                h_abs_eta = h_abs_eta_VJets_specific_b_tag_bin
            except:
                print 'WARNING: V+Jets template from ' + str(file_name) + ', histogram ' + abs_eta + ' in ' + b_tag_bin_VJets +\
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
        abs_eta = 'TTbar_plus_X_analysis/%s/Ref selection/Electron/electron_AbsEta' % (analysis_type[channel])
        abs_eta = abs_eta.replace('Ref selection', electron_control_region)
        h_abs_eta = get_histogram(input_files['data'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['V+Jets'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['TTJet'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['SingleTop'], abs_eta, '0btag')
        electron_QCD_normalisation_factor = 1
        h_abs_eta.Rebin(20)
        if measurement_config.centre_of_mass == 8:
            electron_QCD_normalisation_factor = h_abs_eta_mc.Integral() / h_abs_eta.Integral()
            if electron_QCD_normalisation_factor == 0:
                electron_QCD_normalisation_factor = 1 / h_abs_eta.Integral()
        if measurement_config.centre_of_mass == 7:
            # scaling to 10% of data
            electron_QCD_normalisation_factor = 0.1 * histograms['data'].Integral() / h_abs_eta.Integral()

        h_abs_eta.Scale(electron_QCD_normalisation_factor)
        histograms['QCD'] = h_abs_eta
        
    if channel == 'muon':
        # data-driven QCD template extracted from all-inclusive eta distributions
        global muon_QCD_MC_file
        h_abs_eta_mc = get_histogram(muon_QCD_MC_file, abs_eta, b_tag_bin)
        h_abs_eta_mc.Rebin(rebin)
        abs_eta = 'TTbar_plus_X_analysis/%s/Ref selection/Muon/muon_AbsEta' % (analysis_type[channel])
        abs_eta = abs_eta.replace('Ref selection', muon_control_region)
#        abs_eta = measurement_config.special_muon_histogram
#        h_abs_eta = get_histogram(muon_QCD_file, abs_eta, '')
        h_abs_eta = get_histogram(input_files['data'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['TTJet'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['V+Jets'], abs_eta, '0btag')
        h_abs_eta = h_abs_eta - get_histogram(input_files['SingleTop'], abs_eta, '0btag')
        muon_QCD_normalisation_factor = 1
        h_abs_eta.Rebin(20)
        if measurement_config.centre_of_mass == 8:
            muon_QCD_normalisation_factor = h_abs_eta_mc.Integral() / h_abs_eta.Integral()
            if muon_QCD_normalisation_factor == 0:
                muon_QCD_normalisation_factor = 1 / h_abs_eta.Integral()
        if measurement_config.centre_of_mass == 7:
            muon_QCD_normalisation_factor = 0.05 * histograms['data'].Integral() / h_abs_eta.Integral()
        
        h_abs_eta.Scale(muon_QCD_normalisation_factor)
        histograms['QCD'] = h_abs_eta
        
    return histograms

def get_histogram(input_file, histogram_path, b_tag_bin=''):
    if not input_file:
        return None
    
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

def get_fitted_normalisation(channel, input_files, variable, met_type, b_tag_bin, JSON=False, scale_factors = None):
    if JSON:
        return get_fitted_normalisation_from_JSON(channel, input_files, variable, met_type)  # no b_tag_bin as files are specific
    else:
        return get_fitted_normalisation_from_ROOT(channel, input_files, variable, met_type, b_tag_bin, scale_factors)

def get_fitted_normalisation_from_JSON(channel, input_files, variable, met_type):
    pass

def get_fitted_normalisation_from_ROOT(channel, input_files, variable, met_type, b_tag_bin, scale_factors):
    global use_fitter, measurement_config, verbose
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
        if not measurement_config.luminosity_scale == 1.0:
            for sample, histogram in histograms.iteritems():
                if sample == 'data':
                    continue
                histogram.Scale(measurement_config.luminosity_scale)
        
        # apply normalisation scale factors for rate-changing systematics
        if scale_factors:
            for source, factor in scale_factors.iteritems():
                if 'luminosity' in source:
                    for sample, histogram in histograms.iteritems():
                        if sample == 'data':
                            continue
                        histogram.Scale(factor)
                for sample, histogram in histograms.iteritems():
                    if sample in source:
                        histogram.Scale(factor)
        
        # create signal histograms
        h_eta_signal = None
        if measurement_config.include_higgs:
            h_eta_signal = histograms['TTJet'] + histograms['SingleTop'] + histograms['Higgs']
        else:
            h_eta_signal = histograms['TTJet'] + histograms['SingleTop']
        fit_histograms = {
                                      'data':histograms['data'],
                                      'signal':h_eta_signal,
#                                      'background':histograms['V+Jets']+histograms['QCD']
                                      'V+Jets':histograms['V+Jets'],
                                      'QCD':histograms['QCD'],
                                      }
        fitter = None
        if use_fitter == 'TMinuit':
            fitter = TMinuitFit( histograms = fit_histograms, verbose = verbose )
        elif use_fitter == 'RooFit':
            fitter = RooFitFit( histograms = fit_histograms, fit_boundries = (0., 2.4) )
        else: #not recognised
            sys.stderr.write('Do not recognise fitter "%s". Using default (TMinuit).\n' % fitter)
            fitter = TMinuitFit ( histograms=fit_histograms, verbose = verbose )
        
        fitter.set_fit_constraints({'QCD': 2.0, 'V+Jets': 0.5})

        if verbose:
            print "FITTING: " + channel + '_' + variable + '_' + variable_bin + '_' + met_type + '_' + b_tag_bin

        fitter.fit()
        fit_results = fitter.readResults()
        normalisation = fitter.normalisation
        normalisation_errors = fitter.normalisation_errors
        
        N_ttbar_before_fit = histograms['TTJet'].Integral()
        N_SingleTop_before_fit = histograms['SingleTop'].Integral()
        N_ttbar_error_before_fit = sum(histograms['TTJet'].yerravg())
        N_SingleTop_error_before_fit = sum(histograms['SingleTop'].yerravg())
        N_Higgs_before_fit = 0
        N_Higgs_error_before_fit = 0
        if measurement_config.include_higgs:
            N_Higgs_before_fit = histograms['Higgs'].Integral()
            N_Higgs_error_before_fit = sum(histograms['Higgs'].yerravg())

        if (N_SingleTop_before_fit != 0):
            TTJet_SingleTop_ratio = (N_ttbar_before_fit + N_Higgs_before_fit) / N_SingleTop_before_fit
        else:
            print 'Bin ', variable_bin, ': ttbar/singleTop ratio undefined for %s channel! Setting to 0.' % channel
            TTJet_SingleTop_ratio = 0

        N_ttbar_all, N_SingleTop = decombine_result(fit_results['signal'], TTJet_SingleTop_ratio)
        if (N_Higgs_before_fit != 0):
            TTJet_Higgs_ratio = N_ttbar_before_fit/ N_Higgs_before_fit
        else:
#             print 'Bin ', variable_bin, ': ttbar/higgs ratio undefined for %s channel! Setting to 0.' % channel
            TTJet_Higgs_ratio = 0
        
        N_ttbar, N_Higgs = decombine_result(N_ttbar_all, TTJet_Higgs_ratio)
        
        fit_results['TTJet'] = N_ttbar
        fit_results['SingleTop'] = N_SingleTop
        fit_results['Higgs'] = N_Higgs
        
        normalisation['TTJet'] = N_ttbar_before_fit
        normalisation['SingleTop'] = N_SingleTop_before_fit
        normalisation['Higgs'] = N_Higgs_before_fit
        normalisation_errors['TTJet'] = N_ttbar_error_before_fit
        normalisation_errors['SingleTop'] = N_SingleTop_error_before_fit
        normalisation_errors['Higgs'] = N_Higgs_error_before_fit
        
        if results == {}:  # empty
            initial_values['data'] = [(normalisation['data'], normalisation_errors['data'])]
            templates['data'] = [fitter.vectors['data']]
            for sample in fit_results.keys():
                results[sample] = [fit_results[sample]]
                initial_values[sample] = [(normalisation[sample], normalisation_errors[sample])]
                if not sample in ['TTJet', 'SingleTop', 'Higgs']:
                    templates[sample] = [fitter.vectors[sample]]
        else:
            initial_values['data'].append([normalisation['data'], normalisation_errors['data']])
            templates['data'].append(fitter.vectors['data'])
            for sample in fit_results.keys():
                results[sample].append(fit_results[sample])
                initial_values[sample].append([normalisation[sample], normalisation_errors[sample]])
                if not sample in ['TTJet', 'SingleTop', 'Higgs']:
                    templates[sample].append(fitter.vectors[sample])
                    
    return results, initial_values, templates
    
def write_fit_results_and_initial_values(channel, category, fit_results, initial_values, templates):
    global variable, met_type, output_path
    output_folder = output_path + '/' + str(measurement_config.centre_of_mass) + 'TeV/' + variable + '/fit_results/' + category + '/'
    
    write_data_to_JSON(fit_results, output_folder + 'fit_results_' + channel + '_' + met_type + '.txt')
    write_data_to_JSON(initial_values, output_folder + 'initial_values_' + channel + '_' + met_type + '.txt')
    write_data_to_JSON(templates, output_folder + 'templates_' + channel + '_' + met_type + '.txt')

def write_fit_results(channel, category, fit_results):
    global variable, met_type, output_path
    output_folder = output_path + '/' + str(measurement_config.centre_of_mass) + 'TeV/' + variable + '/fit_results/' + category + '/'
    
    write_data_to_JSON(fit_results, output_folder + 'fit_results_' + channel + '_' + met_type + '.txt')
    
    
if __name__ == '__main__':
    set_root_defaults()
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
    parser.add_option('--fitter', dest = "use_fitter", default='TMinuit', 
                      help = 'Fitter to be used: TMinuit|RooFit. Default = TMinuit.')
    parser.add_option('-V', dest = "verbose", action="store_true",
                      help="Print the fit info and correlation matrix")

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
    
    from config.variable_binning import variable_bins_ROOT
    if options.CoM == 8:
        import config.cross_section_measurement_8TeV as measurement_config
    elif options.CoM == 7:
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
    
    use_fitter = options.use_fitter
    verbose = options.verbose
    
    # possible options:
    # --continue : continue from saved - skips ROOT files, reads from JSON?
    
    # get data from histograms or JSON files
    # data and muon_QCD file with SFs are the same for central measurement and all systematics 
    data_file_electron = File(measurement_config.data_file_electron)
    data_file_muon = File(measurement_config.data_file_muon)
    
    SingleTop_file = File(measurement_config.SingleTop_file)
    muon_QCD_MC_file = File(measurement_config.muon_QCD_MC_file)
    electron_QCD_MC_file = File(measurement_config.electron_QCD_MC_file)
    TTJet_file = File(measurement_config.ttbar_category_templates['central'])
    VJets_file = File(measurement_config.VJets_category_templates['central'])
    electron_control_region = measurement_config.electron_control_region
    muon_control_region = measurement_config.muon_control_region
    Higgs_file = None
    if measurement_config.include_higgs:
        Higgs_file = File(measurement_config.higgs_category_templates['central'])
    # matching/scale up/down systematics for ttbar + jets
    for systematic, filename in measurement_config.generator_systematic_ttbar_templates.iteritems():
        TTJet_file = File(filename)
        if verbose:
            print "\n" + systematic + "\n"
        fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation('electron',
                      input_files={
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_electron,
                                   'Higgs' : Higgs_file,
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
                                   'Higgs' : Higgs_file,
                                   },
                      variable=variable,
                      met_type=met_type,
                      b_tag_bin=b_tag_bin,
                      )
        
        write_fit_results_and_initial_values('electron', ttbar_theory_systematic_prefix + systematic, fit_results_electron, initial_values_electron, templates_electron)
        write_fit_results_and_initial_values('muon', ttbar_theory_systematic_prefix + systematic, fit_results_muon, initial_values_muon, templates_muon)
        write_fit_results( 'combined', ttbar_theory_systematic_prefix + systematic, combine_complex_results( fit_results_electron, fit_results_muon ) )
        TTJet_file.Close()
    
    TTJet_file = File(measurement_config.ttbar_category_templates['central'])    
    # matching/scale up/down systematics for V+Jets
    for systematic in generator_systematics:
        VJets_file = File(measurement_config.generator_systematic_vjets_templates[systematic])
        if verbose:
            print "\n" + systematic + "\n"
        fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation('electron',
                      input_files={
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_electron,
                                   'Higgs' : Higgs_file,
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
                                   'Higgs' : Higgs_file,
                                   },
                      variable=variable,
                      met_type=met_type,
                      b_tag_bin=b_tag_bin,
                      )
        
        write_fit_results_and_initial_values('electron', vjets_theory_systematic_prefix + systematic, fit_results_electron, initial_values_electron, templates_electron)
        write_fit_results_and_initial_values('muon', vjets_theory_systematic_prefix + systematic, fit_results_muon, initial_values_muon, templates_muon)
        write_fit_results( 'combined', vjets_theory_systematic_prefix + systematic, combine_complex_results( fit_results_electron, fit_results_muon ) )
        VJets_file.Close()
    
    VJets_file = File(measurement_config.VJets_category_templates['central'])    
    
    # central measurement and the rest of the systematics

    last_systematic = ''
    for category, prefix in categories_and_prefixes.iteritems():
        TTJet_file = File(measurement_config.ttbar_category_templates[category])
        SingleTop_file = File(measurement_config.SingleTop_category_templates[category])
        VJets_file = File(measurement_config.VJets_category_templates[category])
        muon_QCD_MC_file = File(measurement_config.muon_QCD_MC_category_templates[category])
        data_file_electron = File(measurement_config.data_electron_category_templates['central'])
        data_file_muon = File(measurement_config.data_muon_category_templates['central'])
        if measurement_config.include_higgs:
            Higgs_file = File(measurement_config.higgs_category_templates[category])
        
        # Setting up systematic MET for JES up/down samples
        met_type = translate_options[options.metType]
        if category in ['JES_up', 'JES_down']:  # these systematics affect the data as well
            data_file_electron.Close()
            data_file_muon.Close()
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

        if verbose:
            print "\n" + category + "\n"

        fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation('electron',
                      input_files={
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_electron,
                                   'Higgs' : Higgs_file,
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
                                   'Higgs' : Higgs_file,
                                   },
                      variable=variable,
                      met_type=met_type,
                      b_tag_bin=b_tag_bin,
                      )
        write_fit_results_and_initial_values('electron', category, fit_results_electron, initial_values_electron, templates_electron)
        write_fit_results_and_initial_values('muon', category, fit_results_muon, initial_values_muon, templates_muon)
        write_fit_results( 'combined', category, combine_complex_results( fit_results_electron, fit_results_muon ) )
        last_systematic = category
        
        TTJet_file.Close()
        SingleTop_file.Close()
        VJets_file.Close()
        muon_QCD_MC_file.Close()
        data_file_electron.Close()
        data_file_muon.Close()
        if Higgs_file:
            Higgs_file.Close()
    
    # now do PDF uncertainty
    data_file_electron = File(measurement_config.data_electron_category_templates['central'])
    data_file_muon = File(measurement_config.data_muon_category_templates['central'])
    SingleTop_file = File(measurement_config.SingleTop_category_templates['central'])
    VJets_file = File(measurement_config.VJets_category_templates['central'])
    muon_QCD_MC_file = File(measurement_config.muon_QCD_MC_category_templates['central'])
    data_file_electron = File(measurement_config.data_electron_category_templates['central'])
    data_file_muon = File(measurement_config.data_muon_category_templates['central'])
    if measurement_config.include_higgs:
        Higgs_file = File(measurement_config.higgs_category_templates['central'])
    
    for index in range(1, 45):
        category = 'PDFWeights_%d' % index
        TTJet_file = File(measurement_config.pdf_uncertainty_template % index)

        if verbose:
            print "\nPDF_" + str(index) + "\n"

        fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation('electron',
                      input_files={
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_electron,
                                   'Higgs' : Higgs_file,
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
                                   'Higgs' : Higgs_file,
                                   },
                      variable=variable,
                      met_type=met_type,
                      b_tag_bin=b_tag_bin,
                      )
        write_fit_results_and_initial_values('electron', category, fit_results_electron, initial_values_electron, templates_electron)
        write_fit_results_and_initial_values('muon', category, fit_results_muon, initial_values_muon, templates_muon)
        write_fit_results( 'combined', category, combine_complex_results( fit_results_electron, fit_results_muon ) )
        TTJet_file.Close()

    TTJet_file = File(measurement_config.ttbar_category_templates['central'])
    
    for met_systematic in met_systematics_suffixes:
        #all MET uncertainties except JES & JER - as this is already included
        if 'JetEn' in met_systematic or 'JetRes' in met_systematic or variable == 'HT':#HT is not dependent on MET!
            continue
        category = met_type + met_systematic
        if 'PFMET' in met_type:
            category = category.replace('PFMET', 'patPFMet')
        
        if verbose:
            print "\n" + met_systematic + "\n"

        fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation('electron',
                      input_files={
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_electron,
                                   'Higgs' : Higgs_file,
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
                                   'Higgs' : Higgs_file,
                                   },
                      variable=variable,
                      met_type=category,
                      b_tag_bin=b_tag_bin,
                      )
        write_fit_results_and_initial_values('electron', category, fit_results_electron, initial_values_electron, templates_electron)
        write_fit_results_and_initial_values('muon', category, fit_results_muon, initial_values_muon, templates_muon)
        write_fit_results( 'combined', category, combine_complex_results( fit_results_electron, fit_results_muon ) )
    
    #QCD systematic
    
    electron_control_region = measurement_config.electron_control_region_systematic

    if verbose:
        print "\nQCD shape systematic\n"

    fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation('electron',
                      input_files={
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_electron,
                                   'Higgs' : Higgs_file,
                                   },
                      variable=variable,
                      met_type=met_type,
                      b_tag_bin=b_tag_bin,
                      )
    
    muon_control_region = measurement_config.muon_control_region_systematic    
    fit_results_muon, initial_values_muon, templates_muon = get_fitted_normalisation('muon',
                  input_files={
                               'TTJet': TTJet_file,
                               'SingleTop': SingleTop_file,
                               'V+Jets': VJets_file,
                               'data': data_file_muon,
                               'Higgs' : Higgs_file,
                               },
                  variable=variable,
                  met_type=met_type,
                  b_tag_bin=b_tag_bin,
                  )
    
    systematic = 'QCD_shape'
    write_fit_results_and_initial_values('electron', systematic, fit_results_electron, initial_values_electron, templates_electron)
    write_fit_results_and_initial_values('muon', systematic, fit_results_muon, initial_values_muon, templates_muon)
    write_fit_results( 'combined', systematic, combine_complex_results( fit_results_electron, fit_results_muon ) )

    electron_control_region = measurement_config.electron_control_region
    muon_control_region = measurement_config.muon_control_region

    #rate-changing systematics
    for systematic, shift in measurement_config.rate_changing_systematics.iteritems():
        factor = 1.0
        for variation in ['+', '-']:
            if variation == '+':
                factor = 1.0 + shift
            else:
                factor = 1.0 - shift

            if verbose:
                print "\n" + systematic + variation + "\n"

            scale_factors = {}
            scale_factors[systematic + variation] = factor
            fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation('electron',
                              input_files={
                                           'TTJet': TTJet_file,
                                           'SingleTop': SingleTop_file,
                                           'V+Jets': VJets_file,
                                           'data': data_file_electron,
                                           'Higgs' : Higgs_file,
                                           },
                              variable=variable,
                              met_type=met_type,
                              b_tag_bin=b_tag_bin,
                              scale_factors = scale_factors
                              )
            
            fit_results_muon, initial_values_muon, templates_muon = get_fitted_normalisation('muon',
                          input_files={
                                       'TTJet': TTJet_file,
                                       'SingleTop': SingleTop_file,
                                       'V+Jets': VJets_file,
                                       'data': data_file_muon,
                                       'Higgs' : Higgs_file,
                                       },
                          variable=variable,
                          met_type=met_type,
                          b_tag_bin=b_tag_bin,
                          scale_factors = scale_factors
                          )

            write_fit_results_and_initial_values('electron', systematic + variation, fit_results_electron, initial_values_electron, templates_electron)
            write_fit_results_and_initial_values('muon', systematic + variation, fit_results_muon, initial_values_muon, templates_muon)
            write_fit_results( 'combined', systematic + variation, combine_complex_results( fit_results_electron, fit_results_muon ) )



