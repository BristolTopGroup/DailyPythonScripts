# general
from __future__ import division
from optparse import OptionParser
import sys
# rootpy
from rootpy.io import File
# DailyPythonScripts
from config.summations_common import b_tag_summations
from config.variable_binning import variable_bins_ROOT
from config import XSectionConfig

from tools.Calculation import decombine_result, combine_complex_results
from tools.Fitting import Minuit, RooFitFit, FitData, FitDataCollection
from tools.file_utilities import write_data_to_JSON
from tools.ROOT_utils import set_root_defaults
from tools.hist_utilities import clean_control_region, adjust_overflow_to_limit
from lib import closure_tests

def get_histograms( channel, input_files, variable, met_type, variable_bin,
                   b_tag_bin, rebin = 1, fit_variable = 'absolute_eta',
                   scale_factors = None ):
    global b_tag_bin_VJets, fit_variables
    global electron_control_region, muon_control_region

    boundaries = measurement_config.fit_boundaries[fit_variable]
    histograms = {}
    if not variable in measurement_config.histogram_path_templates.keys():
        print 'Fatal Error: unknown variable ', variable
        sys.exit()

    fit_variable_name = ''
    fit_variable_name_data = ''
    fit_variable_template = measurement_config.histogram_path_templates[variable]
    ht_fill_list, other_fill_list = None, None
    if fit_variable == 'absolute_eta':
        ht_fill_list = ( analysis_type[channel], variable_bin, channel + '_' + fit_variable )
        other_fill_list = ( analysis_type[channel], met_type, variable_bin, channel + '_' + fit_variable )
    else:
        ht_fill_list = ( analysis_type[channel], variable_bin, fit_variable )
        other_fill_list = ( analysis_type[channel], met_type, variable_bin, fit_variable )
    if variable == 'HT':
        fit_variable_name = fit_variable_template % ht_fill_list
        fit_variable_name_data = fit_variable_name
    else:
        fit_variable_name = fit_variable_template % other_fill_list

        if 'JetRes' in met_type:
            fit_variable_name_data = fit_variable_name.replace( 'JetResDown', '' )
            fit_variable_name_data = fit_variable_name_data.replace( 'JetResUp', '' )
            if 'patPFMet' in met_type:
                fit_variable_name = fit_variable_name.replace( 'patPFMet', 'PFMET' )
        else:
            fit_variable_name_data = fit_variable_name

    for sample, file_name in input_files.iteritems():
        if not file_name:
            continue
        h_fit_variable = None
        if sample == 'data':
            h_fit_variable = get_histogram( file_name, fit_variable_name_data, b_tag_bin )
        elif sample == 'V+Jets':
            # extracting the inclusive V+Jets template across all bins from its specific b-tag bin (>=0 by default) and scaling it to analysis b-tag bin
            for var_bin in variable_bins_ROOT[variable]:
                temp_variable_name = fit_variable_name.replace(variable_bin, var_bin)
                if h_fit_variable == None:
                    h_fit_variable = get_histogram( file_name, temp_variable_name, b_tag_bin )
                else:
                    h_fit_variable += get_histogram( file_name, temp_variable_name, b_tag_bin )
                    
            h_fit_variable_for_scaling = get_histogram(file_name, fit_variable_name, b_tag_bin)
            scale = h_fit_variable_for_scaling.integral (overflow = True ) / h_fit_variable.integral( overflow = True )
            h_fit_variable.Scale(scale)
        else:
            h_fit_variable = get_histogram( file_name, fit_variable_name, b_tag_bin )
        h_fit_variable.Rebin( rebin )
        h_fit_variable = adjust_overflow_to_limit( h_fit_variable, boundaries[0], boundaries[1] )
        histograms[sample] = h_fit_variable

    h_qcd = get_qcd_histograms( input_files, variable, variable_bin,
                                           channel, fit_variable_name, rebin )

    if h_qcd.Integral() < 0.1:
        h_qcd.Scale( 0.1/h_qcd.Integral() )
        pass
    
    histograms['QCD'] = adjust_overflow_to_limit( h_qcd,
                                                 boundaries[0], boundaries[1] )
    
    # normalise histograms
    if not measurement_config.luminosity_scale == 1.0:
        for sample, histogram in histograms.iteritems():
            if sample == 'data':
                continue
            histogram.Scale( measurement_config.luminosity_scale )

    # apply normalisation scale factors for rate-changing systematics
    if scale_factors:
        for source, factor in scale_factors.iteritems():
            if 'luminosity' in source:
                for sample, histogram in histograms.iteritems():
                    if sample == 'data':
                        continue
                    histogram.Scale( factor )
            for sample, histogram in histograms.iteritems():
                if sample in source:
                    histogram.Scale( factor )
    return histograms

def get_qcd_histograms( input_files, variable, variable_bin, channel,
                                            fit_variable_hist_name, rebin = 1 ):
    '''
    Retrieves the data-driven QCD template and normalises it to MC prediction.
    It uses the inclusive template (across all variable bins) and removes other processes
    before normalising the QCD template.
    '''
    global electron_QCD_MC_file, muon_QCD_MC_file, analysis_type, \
           electron_control_region, muon_control_region, b_tag_bin

    control_region = ''
    control_region_btag = '0btag'
    if 'M_bl' in fit_variable_hist_name or 'angle_bl' in fit_variable_hist_name:
        control_region_btag = '1orMoreBtag'
    qcd_file = ''
    samples = ['data', 'V+Jets', 'SingleTop', 'TTJet']

    if channel == 'electron':
        control_region = electron_control_region
        qcd_file = electron_QCD_MC_file
    if channel == 'muon':
        control_region = muon_control_region
        qcd_file = muon_QCD_MC_file
    inclusive_control_region_hists = {}

    for var_bin in variable_bins_ROOT[variable]:
        hist_name = fit_variable_hist_name.replace( variable_bin, var_bin )

        control_region_hist_name = hist_name.replace( 'Ref selection',
                                                            control_region )
        for sample in samples:
            if not inclusive_control_region_hists.has_key( sample ):
                inclusive_control_region_hists[sample] = get_histogram( 
                                                        input_files[sample],
                                                        control_region_hist_name,
                                                        control_region_btag,
                                                                   )
            else:
                inclusive_control_region_hists[sample] += get_histogram( 
                                                        input_files[sample],
                                                        control_region_hist_name,
                                                        control_region_btag,
                                                                   )
    for sample in samples:
        inclusive_control_region_hists[sample].Rebin( rebin )

    inclusive_control_region_hists['data'] = clean_control_region( inclusive_control_region_hists,
                          subtract = ['TTJet', 'V+Jets', 'SingleTop'] )
    # now apply proper normalisation
    QCD_normalisation_factor = 1
    signal_region_mc = get_histogram( qcd_file, fit_variable_hist_name, b_tag_bin )
    n_mc = signal_region_mc.Integral()
    n_control = inclusive_control_region_hists['data'].Integral()
    if not n_control == 0:  # scale to MC prediction
        if not n_mc == 0:
            QCD_normalisation_factor = 1 / n_control * n_mc
        else:
            QCD_normalisation_factor = 1 / n_control
    inclusive_control_region_hists['data'].Scale( QCD_normalisation_factor )

    return inclusive_control_region_hists['data']

def get_histogram( input_file, histogram_path, b_tag_bin = '' ):
    if not input_file:
        return None

    b_tag_bin_sum_rules = b_tag_summations
    histogram = None
    if b_tag_bin in b_tag_bin_sum_rules.keys():  # summing needed
        b_tag_bins_to_sum = b_tag_bin_sum_rules[b_tag_bin]
        histogram = input_file.Get( histogram_path + '_' + b_tag_bins_to_sum[0] ).Clone()
        for bin_i in b_tag_bins_to_sum[1:]:
            histogram += input_file.Get( histogram_path + '_' + bin_i )
    else:
        if b_tag_bin == '':
            histogram = input_file.Get( histogram_path )
        else:
            histogram = input_file.Get( histogram_path + '_' + b_tag_bin )
    return histogram.Clone()

def get_fitted_normalisation_from_ROOT( channel, input_files, variable, met_type, b_tag_bin, scale_factors = None ):
    '''
    Retrieves the number of ttbar events from fits to one or more distribution
    (fit_variables) for each bin in the variable.
    ''' 
    global use_fitter, measurement_config, verbose, fit_variables, options
    # results and initial values are the same across different fit variables
    # templates are not
    results = {}
    initial_values = {}
    templates = {fit_variable: {} for fit_variable in fit_variables}

    for variable_bin in variable_bins_ROOT[variable]:
        fitter = None
        fit_data_collection = FitDataCollection()
        
        for fit_variable in fit_variables:
            
            histograms = get_histograms( channel,
                                        input_files,
                                        variable = variable,
                                        met_type = met_type,
                                        variable_bin = variable_bin,
                                        b_tag_bin = b_tag_bin,
                                        rebin = measurement_config.rebin[fit_variable],
                                        fit_variable = fit_variable,
                                        scale_factors = scale_factors,
                                        )
            # create data sets
            h_fit_variable_signal = None
            mc_histograms = None
            if options.make_combined_signal:
                if measurement_config.include_higgs:
                    h_fit_variable_signal = histograms['TTJet'] + histograms['SingleTop'] + histograms['Higgs']
                else:
                    h_fit_variable_signal = histograms['TTJet'] + histograms['SingleTop']
                mc_histograms = {
                                'signal' : h_fit_variable_signal,
                                'V+Jets': histograms['V+Jets'],
                                'QCD': histograms['QCD'],
                            }
            else:
                mc_histograms = {
                                'TTJet': histograms['TTJet'],
                                'SingleTop': histograms['SingleTop'],
                                'V+Jets': histograms['V+Jets'],
                                'QCD': histograms['QCD'],
                            }
            h_data = histograms['data']
            if options.closure_test:
                ct_type = options.closure_test_type
                ct_norm = closure_tests[ct_type]
                h_data = histograms['TTJet'] * ct_norm['TTJet'] + histograms['SingleTop'] * ct_norm['SingleTop'] + histograms['V+Jets'] * ct_norm['V+Jets'] + histograms['QCD'] * ct_norm['QCD'] 
            fit_data = FitData( h_data,
                            mc_histograms,
                            fit_boundaries = measurement_config.fit_boundaries[fit_variable] )
            fit_data_collection.add( fit_data, name = fit_variable )
        if options.enable_constraints:
            fit_data_collection.set_normalisation_constraints( {'QCD': 2.0, 'V+Jets': 0.5} )

#         print "fit_data_collection = ", fit_data_collection
#         print "fit_data = ", fit_data
# #         print "len(fit_data) = ", len(fit_data)
#         print "fit_data_collection.fit_variable = ", fit_data_collection.fit_data
        if use_fitter == 'RooFit':
            fitter = RooFitFit( fit_data_collection )
        elif use_fitter == 'Minuit':
            fitter = Minuit( fit_data_collection, verbose = verbose )
        else:  # not recognised
            sys.stderr.write( 'Do not recognise fitter "%s". Using default (Minuit).\n' % fitter )
            fitter = Minuit ( fit_data_collection )

        if verbose:
            print "FITTING: " + channel + '_' + variable + '_' + variable_bin + '_' + met_type + '_' + b_tag_bin

        fitter.fit()
        fit_results = fitter.readResults()
        
        normalisation = fit_data_collection.mc_normalisation( fit_variables[0] )
        normalisation_errors = fit_data_collection.mc_normalisation_errors( fit_variables[0] )
        if options.make_combined_signal:
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
            initial_values['data'] = [( normalisation['data'], normalisation_errors['data'] )]
            for fit_variable in fit_variables:
                templates[fit_variable]['data'] = [fit_data_collection.vectors( fit_variable )['data']]
            for sample in fit_results.keys():
                results[sample] = [fit_results[sample]]
                initial_values[sample] = [( normalisation[sample], normalisation_errors[sample] )]
                if sample in ['TTJet', 'SingleTop', 'Higgs'] and options.make_combined_signal:
                    continue
                for fit_variable in fit_variables:
                    templates[fit_variable][sample] = [fit_data_collection.vectors( fit_variable )[sample]]
        else:
            initial_values['data'].append( [normalisation['data'], normalisation_errors['data']] )
            for fit_variable in fit_variables:
                templates[fit_variable]['data'].append( fit_data_collection.vectors( fit_variable )['data'] )
            for sample in fit_results.keys():
                results[sample].append( fit_results[sample] )
                initial_values[sample].append( [normalisation[sample], normalisation_errors[sample]] )
                if sample in ['TTJet', 'SingleTop', 'Higgs'] and options.make_combined_signal:
                    continue
                for fit_variable in fit_variables:
                    templates[fit_variable][sample].append( fit_data_collection.vectors( fit_variable )[sample] )

#     print "results = ", results
        del fit_data_collection
        del fitter
    return results, initial_values, templates

def write_fit_results_and_initial_values( channel, category, fit_results, initial_values, templates ):
    global variable, met_type, output_path
    folder_template = '%(path)s/%(fit_vars)s/%(CoM)dTeV/%(variable)s/fit_results/%(category)s/'
    inputs = {
              'path':output_path,
              'CoM': measurement_config.centre_of_mass_energy,
              'variable': variable,
              'category': category,
              'fit_vars': '_'.join( fit_variables )              
              }
    output_folder = folder_template % inputs

    write_data_to_JSON( fit_results, output_folder + 'fit_results_' + channel + '_' + met_type + '.txt' )
    write_data_to_JSON( initial_values, output_folder + 'initial_values_' + channel + '_' + met_type + '.txt' )
    write_data_to_JSON( templates, output_folder + 'templates_' + channel + '_' + met_type + '.txt' )

def write_fit_results( channel, category, fit_results ):
    global variable, met_type, output_path
    folder_template = '%(path)s/%(fit_vars)s/%(CoM)dTeV/%(variable)s/fit_results/%(category)s/'
    inputs = {
              'path':output_path,
              'CoM': measurement_config.centre_of_mass_energy,
              'variable': variable,
              'category': category,
              'fit_vars': '_'.join( fit_variables )              
              }
    output_folder = folder_template % inputs

    write_data_to_JSON( fit_results, output_folder + 'fit_results_' + channel + '_' + met_type + '.txt' )


if __name__ == '__main__':
    set_root_defaults()
    # setup
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data',
                  help = "set output path for JSON files" )
    parser.add_option( "-v", "--variable", dest = "variable", default = 'MET',
                      help = "set the variable to analyse (MET, HT, ST, MT)" )
    parser.add_option( "-f", "--fit-variables", dest = "fit_variables", default = 'absolute_eta',
                      help = "set the fit variable to use in the minimalisation" + 
                           " (absolute_eta, M3, M_bl, angle_bl) or any" + 
                           " combination separated by commas" )
    parser.add_option( "-b", "--bjetbin", dest = "bjetbin", default = '2m',
                      help = "set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m" )
    parser.add_option( "--bjetbin-vjets", dest = "bjetbin_VJets", default = '2m',
                      help = "set b-jet multiplicity for V+Jets samples. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m" )
    parser.add_option( "-m", "--metType", dest = "metType", default = 'type1',
                      help = "set MET type for analysis of MET, ST or MT" )
    parser.add_option( "-c", "--centre-of-mass-energy", dest = "CoM", default = 8, type = int,
                      help = "set the centre of mass energy for analysis. Default = 8 [TeV]" )
    parser.add_option( '--fitter', dest = "use_fitter", default = 'Minuit',
                      help = 'Fitter to be used: Minuit|RooFit. Default = Minuit.' )
    parser.add_option( '-V', '--verbose', dest = "verbose", action = "store_true",
                      help = "Print the fit info and correlation matrix" )
    parser.add_option( '--closure_test', dest = "closure_test", action = "store_true",
                      help = "Perform fit on data == sum(MC) * scale factor (MC process)" )
    parser.add_option( '--closure_test_type', dest = "closure_test_type", default = 'simple',
                      help = "Type of closure test (relative normalisation):" + '|'.join( closure_tests.keys() ) )
    parser.add_option( '--no_combined_signal', dest = "make_combined_signal", 
                       action = "store_false", default=True,
                       help = "Do not make a combined template from TTbar and single top" )
    parser.add_option( '--test', dest = "test", action = "store_true",
                      help = "Just run the central measurement" )
    parser.add_option( '--disable-constraints', dest = "enable_constraints", 
                       action = "store_false", default=True,
                       help = "Do not constrain QCD and VJets templates." )

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


    ( options, args ) = parser.parse_args()

    measurement_config = XSectionConfig( options.CoM )
    # caching of variables for shorter access
    ttbar_theory_systematic_prefix = measurement_config.ttbar_theory_systematic_prefix
    vjets_theory_systematic_prefix = measurement_config.vjets_theory_systematic_prefix
    generator_systematics = measurement_config.generator_systematics
    categories_and_prefixes = measurement_config.categories_and_prefixes
    met_systematics_suffixes = measurement_config.met_systematics_suffixes
    analysis_type = measurement_config.analysis_types
    run_just_central = options.closure_test or options.test

    variable = options.variable
    met_type = translate_options[options.metType]
    b_tag_bin = translate_options[options.bjetbin]
    b_tag_bin_VJets = translate_options[options.bjetbin_VJets]
    path_to_files = measurement_config.path_to_files
    output_path = options.path
    if options.closure_test:
        output_path += '/closure_test/'
        output_path += options.closure_test_type+'/'
    use_fitter = options.use_fitter
    verbose = options.verbose
    fit_variables = options.fit_variables.split( ',' )

    # possible options:
    # --continue : continue from saved - skips ROOT files, reads from JSON?

    # get data from histograms or JSON files
    # data and muon_QCD file with SFs are the same for central measurement and all systematics
    data_file_electron = File( measurement_config.data_file_electron )
    data_file_muon = File( measurement_config.data_file_muon )

    SingleTop_file = File( measurement_config.SingleTop_file )
    muon_QCD_MC_file = File( measurement_config.muon_QCD_MC_file )
    electron_QCD_MC_file = File( measurement_config.electron_QCD_MC_file )
    TTJet_file = File( measurement_config.ttbar_category_templates['central'] )
    VJets_file = File( measurement_config.VJets_category_templates['central'] )
    electron_control_region = measurement_config.electron_control_region
    muon_control_region = measurement_config.muon_control_region
    Higgs_file = None
    if measurement_config.include_higgs:
        Higgs_file = File( measurement_config.higgs_category_templates['central'] )

    TTJet_file = File( measurement_config.ttbar_category_templates['central'] )

    #Using 8 TeV VJets systematic samples for 7 TeV so need to scale: 
    #vjets ratio = sigma(7TeV)*lumi(7TeV)/(sigma(8TeV)*lumi(8TeV))
    vjets_ratio = ( 31314 * 5050 ) / ( 36257.2 * 19584 )
    scale_factors = {}
    if measurement_config.centre_of_mass_energy == 7:
        scale_factors['V+Jets'] = vjets_ratio
    
    # matching/scale up/down systematics for V+Jets
    for systematic in generator_systematics:
        if run_just_central:  # no systematics for closure test
            continue
        VJets_file = File( measurement_config.generator_systematic_vjets_templates[systematic] )
        if verbose:
            print "\n" + systematic + "\n"
        fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation_from_ROOT( 'electron',
                      input_files = {
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_electron,
                                   'Higgs' : Higgs_file,
                                   },
                      variable = variable,
                      met_type = met_type,
                      b_tag_bin = b_tag_bin,
                      scale_factors = scale_factors,
                      )

#         fit_results_muon, initial_values_muon, templates_muon = get_fitted_normalisation_from_ROOT( 'muon',
#                       input_files = {
#                                    'TTJet': TTJet_file,
#                                    'SingleTop': SingleTop_file,
#                                    'V+Jets': VJets_file,
#                                    'data': data_file_muon,
#                                    'Higgs' : Higgs_file,
#                                    },
#                       variable = variable,
#                       met_type = met_type,
#                       b_tag_bin = b_tag_bin,
#                       scale_factors = scale_factors,
#                       )

        write_fit_results_and_initial_values( 'electron', vjets_theory_systematic_prefix + systematic, fit_results_electron, initial_values_electron, templates_electron )
#         write_fit_results_and_initial_values( 'muon', vjets_theory_systematic_prefix + systematic, fit_results_muon, initial_values_muon, templates_muon )
#         write_fit_results( 'combined', vjets_theory_systematic_prefix + systematic, combine_complex_results( fit_results_electron, fit_results_muon ) )
        VJets_file.Close()

    #reset template back to central
    VJets_file = File( measurement_config.VJets_category_templates['central'] )
    del scale_factors
    import sys
    sys.exit()

    # central measurement and the rest of the systematics
    last_systematic = ''
    for category, prefix in categories_and_prefixes.iteritems():
        if run_just_central and not category == 'central': 
            continue
        TTJet_file = File( measurement_config.ttbar_category_templates[category] )
        SingleTop_file = File( measurement_config.SingleTop_category_templates[category] )
        VJets_file = File( measurement_config.VJets_category_templates[category] )
        data_file_electron = File( measurement_config.data_electron_category_templates['central'] )
        data_file_muon = File( measurement_config.data_muon_category_templates['central'] )
        if measurement_config.include_higgs:
            Higgs_file = File( measurement_config.higgs_category_templates[category] )
 
        # Setting up systematic MET for JES up/down samples
        met_type = translate_options[options.metType]
        if category in ['JES_up', 'JES_down']:  # these systematics affect the data as well
            data_file_electron.Close()
            data_file_muon.Close()
            data_file_electron = File( measurement_config.data_electron_category_templates[category] )
            data_file_muon = File( measurement_config.data_muon_category_templates[category] )
 
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
 
        fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation_from_ROOT( 'electron',
                      input_files = {
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_electron,
                                   'Higgs' : Higgs_file,
                                   },
                      variable = variable,
                      met_type = met_type,
                      b_tag_bin = b_tag_bin,
                      )
 
        fit_results_muon, initial_values_muon, templates_muon = get_fitted_normalisation_from_ROOT( 'muon',
                      input_files = {
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_muon,
                                   'Higgs' : Higgs_file,
                                   },
                      variable = variable,
                      met_type = met_type,
                      b_tag_bin = b_tag_bin,
                      )
        write_fit_results_and_initial_values( 'electron', category, fit_results_electron, initial_values_electron, templates_electron )
        write_fit_results_and_initial_values( 'muon', category, fit_results_muon, initial_values_muon, templates_muon )
        write_fit_results( 'combined', category, combine_complex_results( fit_results_electron, fit_results_muon ) )
        last_systematic = category
 
        TTJet_file.Close()
        SingleTop_file.Close()
        VJets_file.Close()
        data_file_electron.Close()
        data_file_muon.Close()
        if Higgs_file:
            Higgs_file.Close()
 
    data_file_electron = File( measurement_config.data_electron_category_templates['central'] )
    data_file_muon = File( measurement_config.data_muon_category_templates['central'] )
    TTJet_file = File( measurement_config.ttbar_category_templates['central'] )
    SingleTop_file = File( measurement_config.SingleTop_category_templates['central'] )
    VJets_file = File( measurement_config.VJets_category_templates['central'] )
    if measurement_config.include_higgs:
        Higgs_file = File( measurement_config.higgs_category_templates['central'] )
 
    for met_systematic in met_systematics_suffixes:
        if run_just_central: 
            continue
        # all MET uncertainties except JES & JER - as this is already included
        if 'JetEn' in met_systematic or 'JetRes' in met_systematic or variable == 'HT':  # HT is not dependent on MET!
            continue
        category = met_type + met_systematic
        if 'PFMET' in met_type:
            category = category.replace( 'PFMET', 'patPFMet' )
 
        if verbose:
            print "\n" + met_systematic + "\n"
 
        fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation_from_ROOT( 'electron',
                      input_files = {
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_electron,
                                   'Higgs' : Higgs_file,
                                   },
                      variable = variable,
                      met_type = category,
                      b_tag_bin = b_tag_bin,
                      )
 
        fit_results_muon, initial_values_muon, templates_muon = get_fitted_normalisation_from_ROOT( 'muon',
                      input_files = {
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_muon,
                                   'Higgs' : Higgs_file,
                                   },
                      variable = variable,
                      met_type = category,
                      b_tag_bin = b_tag_bin,
                      )
        write_fit_results_and_initial_values( 'electron', category, fit_results_electron, initial_values_electron, templates_electron )
        write_fit_results_and_initial_values( 'muon', category, fit_results_muon, initial_values_muon, templates_muon )
        write_fit_results( 'combined', category, combine_complex_results( fit_results_electron, fit_results_muon ) )
 
    # QCD systematic
    if not run_just_central:
        electron_control_region = measurement_config.electron_control_region_systematic
     
        if verbose:
            print "\nQCD shape systematic\n"
     
        fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation_from_ROOT( 'electron',
                          input_files = {
                                       'TTJet': TTJet_file,
                                       'SingleTop': SingleTop_file,
                                       'V+Jets': VJets_file,
                                       'data': data_file_electron,
                                       'Higgs' : Higgs_file,
                                       },
                          variable = variable,
                          met_type = met_type,
                          b_tag_bin = b_tag_bin,
                          )
     
        muon_control_region = measurement_config.muon_control_region_systematic
        fit_results_muon, initial_values_muon, templates_muon = get_fitted_normalisation_from_ROOT( 'muon',
                      input_files = {
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'data': data_file_muon,
                                   'Higgs' : Higgs_file,
                                   },
                      variable = variable,
                      met_type = met_type,
                      b_tag_bin = b_tag_bin,
                      )
     
        systematic = 'QCD_shape'
        write_fit_results_and_initial_values( 'electron', systematic, fit_results_electron, initial_values_electron, templates_electron )
        write_fit_results_and_initial_values( 'muon', systematic, fit_results_muon, initial_values_muon, templates_muon )
        write_fit_results( 'combined', systematic, combine_complex_results( fit_results_electron, fit_results_muon ) )
 
    electron_control_region = measurement_config.electron_control_region
    muon_control_region = measurement_config.muon_control_region
 
    # rate-changing systematics
    for systematic, shift in measurement_config.rate_changing_systematics.iteritems():
        if run_just_central:  # no systematics for closure test
            continue
        factor = 1.0
        for variation in ['+', '-']:
            if variation == '+':
                factor = 1.0 + shift
            else:
                factor = 1.0 - shift
 
            if verbose:
                print "\n" + systematic + variation, factor, "\n"
 
            scale_factors = {}
            scale_factors[systematic + variation] = factor
            fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation_from_ROOT( 'electron',
                              input_files = {
                                           'TTJet': TTJet_file,
                                           'SingleTop': SingleTop_file,
                                           'V+Jets': VJets_file,
                                           'data': data_file_electron,
                                           'Higgs' : Higgs_file,
                                           },
                              variable = variable,
                              met_type = met_type,
                              b_tag_bin = b_tag_bin,
                              scale_factors = scale_factors
                              )
 
            fit_results_muon, initial_values_muon, templates_muon = get_fitted_normalisation_from_ROOT( 'muon',
                          input_files = {
                                       'TTJet': TTJet_file,
                                       'SingleTop': SingleTop_file,
                                       'V+Jets': VJets_file,
                                       'data': data_file_muon,
                                       'Higgs' : Higgs_file,
                                       },
                          variable = variable,
                          met_type = met_type,
                          b_tag_bin = b_tag_bin,
                          scale_factors = scale_factors
                          )
 
            write_fit_results_and_initial_values( 'electron', systematic + variation, fit_results_electron, initial_values_electron, templates_electron )
            write_fit_results_and_initial_values( 'muon', systematic + variation, fit_results_muon, initial_values_muon, templates_muon )
            write_fit_results( 'combined', systematic + variation, combine_complex_results( fit_results_electron, fit_results_muon ) )
    