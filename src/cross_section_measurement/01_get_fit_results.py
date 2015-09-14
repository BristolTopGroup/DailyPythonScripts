# general
from __future__ import division
from optparse import OptionParser
import sys
# rootpy
from rootpy.io import File
# DailyPythonScripts
from config.summations_common import b_tag_summations
from config.variable_binning import variable_bins_ROOT, fit_variable_bin_edges
from config import XSectionConfig

from tools.Calculation import decombine_result, combine_complex_results
from tools.Fitting import Minuit, RooFitFit, FitData, FitDataCollection
from tools.file_utilities import write_data_to_JSON
from tools.ROOT_utils import set_root_defaults, get_histograms_from_trees
from tools.hist_utilities import clean_control_region, adjust_overflow_to_limit, get_data_derived_qcd
from lib import closure_tests

def get_histograms( channel, input_files, variable, met_systematic, met_type, variable_bin,
                   b_tag_bin, 
                   treePrefix, weightBranch,
                   rebin = 1, fit_variable = 'absolute_eta',
                   scale_factors = None ):
    global b_tag_bin_VJets, fit_variables
    global electron_control_region, muon_control_region

    boundaries = measurement_config.fit_boundaries[fit_variable]
    histograms = {}

    tree = measurement_config.tree_path_templates[channel]
    control_tree = measurement_config.tree_path_control_templates[channel]

    # Put together weight
    fullWeight = 'EventWeight'
    if weightBranch != '' :
        fullWeight += ' * %s' % weightBranch

    # Work out bin of variable
    variableForSelection = variable
    minVar = variable_bin.split('-')[0]
    maxVar = variable_bin.split('-')[-1]
    selection = ''
    if maxVar != 'inf' :
        selection = '%s >= %s && %s < %s' % ( variableForSelection, minVar, variableForSelection, maxVar)
    else :
        selection = '%s >= %s' % ( variableForSelection, minVar )

    bins = fit_variable_bin_edges[fit_variable]
    xMin = bins[0]
    xMax = bins[-1]
    nBins = len(bins) -1

    # Get data files here, without any systematic variations
    data_files = { sample : input_files[sample] for sample in ['data'] }
    histograms_data = get_histograms_from_trees( trees = [tree], branch = fit_variable, selection = selection, weightBranch = fullWeight, files = data_files, nBins = nBins, xMin = xMin, xMax = xMax )

    # Now work out tree/variable for MC
    # Identical for data if central, different for systematics
    tree = tree + treePrefix

    if met_systematic:
        if variable == 'MET':
            variableForSelection = 'MET_METUncertainties[%i]' % met_systematics[met_systematic]
        elif variable == 'ST':
            variableForSelection = 'ST_METUncertainties[%i]' % met_systematics[met_systematic]

    # Work out selection again for MC, as variable (e.g. MET) could be different after systematic variation
    if maxVar != 'inf' :
        selection = '%s >= %s && %s < %s' % ( variableForSelection, minVar, variableForSelection, maxVar)
    else :
        selection = '%s >= %s' % ( variableForSelection, minVar )

    # Get exclusive templates for MC
    input_files_exclusive = { sample : input_files[sample] for sample in ['TTJet', 'SingleTop', 'V+Jets', 'QCD'] }
    # Get inclusive template for these (i.e. don't split up fit variable in bins of MET or whatever)
    input_files_inclusive = { sample : input_files[sample] for sample in ['V+Jets'] }
    # # Get control templates for QCD only, and inclusive
    # input_files_control = input_files

    # Get necessary histograms
    # Signal, binned by e.g. MET, HT etc.
    histograms_exclusive = get_histograms_from_trees( trees = [tree], branch = fit_variable, selection = selection, weightBranch = fullWeight, files = input_files_exclusive, nBins = nBins, xMin = xMin, xMax = xMax )
    # Signal, not binned.  For V+Jets template
    histograms_inclusive = get_histograms_from_trees( trees = [tree], branch = fit_variable, weightBranch = fullWeight, files = input_files_inclusive, nBins = nBins, xMin = xMin, xMax = xMax )
    # Control, not binned.  For QCD template
    histograms_control_inclusive = get_histograms_from_trees( trees = [control_tree], branch = fit_variable, weightBranch = fullWeight, files = input_files, nBins = nBins, xMin = xMin, xMax = xMax )

    # Currently needed, as get_histograms_from_trees returns the histograms as part of a more complicated structure
    for histogram in histograms_data:
        for d in histograms_data[histogram]:
            histograms_data[histogram] = histograms_data[histogram][d].Clone()

    for histogram in histograms_exclusive:
        for d in histograms_exclusive[histogram]:
            histograms_exclusive[histogram] = histograms_exclusive[histogram][d].Clone()

    for histogram in histograms_inclusive:
        for d in histograms_inclusive[histogram]:
            histograms_inclusive[histogram] = histograms_inclusive[histogram][d].Clone()

    for histogram in histograms_control_inclusive:
        for d in histograms_control_inclusive[histogram]:
            histograms_control_inclusive[histogram] = histograms_control_inclusive[histogram][d].Clone()

    # Put all histograms into one dictionary
    histograms = {}
    histograms.update(histograms_exclusive)

    # Always use central data sample
    histograms['data'] = histograms_data['data']

    # Get QCD distribution from data
    # histograms['QCD'] = get_data_derived_qcd(histograms_control_inclusive, histograms_exclusive['QCD'])
    # histograms['V+Jets'] = get_inclusive_histogram( histograms_inclusive['V+Jets'], histograms['V+Jets'] )
    
    # normalise histograms
    if not measurement_config.luminosity_scale == 1.0:
        for sample, histogram in histograms.iteritems():
            if sample == 'data':
                continue
            histogram.Scale( measurement_config.luminosity_scale )

    # # apply normalisation scale factors for rate-changing systematics
    if scale_factors:
        for source, factor in scale_factors.iteritems():
            for sample, histogram in histograms.iteritems():
                if 'luminosity' in source:
                    if sample is 'data':
                        # Skip data for luminosity systematic
                        continue
                    else:
                        histogram.Scale( factor )
                # For cross section systematics, only change normalisation of relevant sample
                elif sample in source :
                    histogram.Scale( factor )

    return histograms

def get_inclusive_histogram( inclusive_hist, exclusive_hist ):
    normalisation_exclusive = exclusive_hist.integral( overflow = True )
    normalisation_inclusive = inclusive_hist.integral( overflow = True )

    if inclusive_hist.integral( overflow = True ) == 0. : return inclusive_hist
    if normalisation_exclusive < 0.1 : normalisation_exclusive = 1.
    scale = normalisation_exclusive / normalisation_inclusive
    inclusive_hist.Scale(scale)

    return inclusive_hist

def get_fitted_normalisation_from_ROOT( channel, input_files, variable, met_systematic, met_type, b_tag_bin, treePrefix, weightBranch, scale_factors = None ):
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
                                        met_systematic = met_systematic,
                                        met_type = met_type,
                                        variable_bin = variable_bin,
                                        b_tag_bin = b_tag_bin,
                                        rebin = measurement_config.rebin[fit_variable],
                                        fit_variable = fit_variable,
                                        scale_factors = scale_factors,
                                        treePrefix = treePrefix,
                                        weightBranch = weightBranch,
                                        )
            # create data sets
            h_fit_variable_signal = None
            mc_histograms = None

            # if options.make_combined_signal:
            #     h_fit_variable_signal = histograms['TTJet'] + histograms['SingleTop']
            #     mc_histograms = {
            #                     'signal' : h_fit_variable_signal,
            #                     'V+Jets': histograms['V+Jets'],
            #                     'QCD': histograms['QCD'],
            #                 }
            # else:
            mc_histograms = {
                            'TTJet': histograms['TTJet'],
                            'SingleTop': histograms['SingleTop'],
                            'V+Jets': histograms['V+Jets'],
                            'QCD': histograms['QCD'],
                        }
            h_data = histograms['data']

            # if options.closure_test:
            #     ct_type = options.closure_test_type
            #     ct_norm = closure_tests[ct_type]
            #     h_data = histograms['TTJet'] * ct_norm['TTJet'] + histograms['SingleTop'] * ct_norm['SingleTop'] + histograms['V+Jets'] * ct_norm['V+Jets'] + histograms['QCD'] * ct_norm['QCD'] 
            fit_data = FitData( h_data,
                            mc_histograms,
                            fit_boundaries = measurement_config.fit_boundaries[fit_variable] )
            fit_data_collection.add( fit_data, name = fit_variable )
        # if options.enable_constraints:
        #     fit_data_collection.set_normalisation_constraints( {'QCD': 2.0, 'V+Jets': 0.5} )

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

        # if options.make_combined_signal:
        #     N_ttbar_before_fit = histograms['TTJet'].Integral()
        #     N_SingleTop_before_fit = histograms['SingleTop'].Integral()
        #     N_ttbar_error_before_fit = sum(histograms['TTJet'].yerravg())
        #     N_SingleTop_error_before_fit = sum(histograms['SingleTop'].yerravg())
        #     N_Higgs_before_fit = 0
        #     N_Higgs_error_before_fit = 0
        #     if measurement_config.include_higgs:
        #         N_Higgs_before_fit = histograms['Higgs'].Integral()
        #         N_Higgs_error_before_fit = sum(histograms['Higgs'].yerravg())
     
        #     if (N_SingleTop_before_fit != 0):
        #         TTJet_SingleTop_ratio = (N_ttbar_before_fit + N_Higgs_before_fit) / N_SingleTop_before_fit
        #     else:
        #         print 'Bin ', variable_bin, ': ttbar/singleTop ratio undefined for %s channel! Setting to 0.' % channel
        #         TTJet_SingleTop_ratio = 0
     
        #     N_ttbar_all, N_SingleTop = decombine_result(fit_results['signal'], TTJet_SingleTop_ratio)
        #     if (N_Higgs_before_fit != 0):
        #         TTJet_Higgs_ratio = N_ttbar_before_fit/ N_Higgs_before_fit
        #     else:
        #         TTJet_Higgs_ratio = 0
     
            
        #     N_ttbar, N_Higgs = decombine_result(N_ttbar_all, TTJet_Higgs_ratio)
    
        #     fit_results['TTJet'] = N_ttbar
        #     fit_results['SingleTop'] = N_SingleTop
        #     fit_results['Higgs'] = N_Higgs
    
        #     normalisation['TTJet'] = N_ttbar_before_fit
        #     normalisation['SingleTop'] = N_SingleTop_before_fit
        #     normalisation['Higgs'] = N_Higgs_before_fit
        #     normalisation_errors['TTJet'] = N_ttbar_error_before_fit
        #     normalisation_errors['SingleTop'] = N_SingleTop_error_before_fit
        #     normalisation_errors['Higgs'] = N_Higgs_error_before_fit

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

    # print results
    # print "results = ", results
    # print 'templates = ',templates
    return results, initial_values, templates

def write_fit_results_and_initial_values( channel, category, fit_results, initial_values, templates ):
    global variable, met_type, output_path
    folder_template = '%(path)s/%(fit_vars)s/%(CoM)dTeV/%(variable)s/%(category)s/'
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
    folder_template = '%(path)s/%(fit_vars)s/%(CoM)dTeV/%(variable)s/%(category)s/'
    inputs = {
              'path':output_path,
              'CoM': measurement_config.centre_of_mass_energy,
              'variable': variable,
              'category': category,
              'fit_vars': '_'.join( fit_variables )              
              }
    output_folder = folder_template % inputs

    write_data_to_JSON( fit_results, output_folder + 'normalisation_' + channel + '_' + met_type + '.txt' )


if __name__ == '__main__':
    set_root_defaults()
    # setup
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data',
                  help = "set output path for JSON files" )
    parser.add_option( "-v", "--variable", dest = "variable", default = 'MET',
                      help = "set the variable to analyse (MET, HT, ST, MT)" )
    parser.add_option( "-f", "--fit-variables", dest = "fit_variables", default = 'M3',
                      help = "set the fit variable to use in the minimalisation" + 
                           " (absolute_eta, M3, M_bl, angle_bl) or any" + 
                           " combination separated by commas" )
    parser.add_option( "-b", "--bjetbin", dest = "bjetbin", default = '2m',
                      help = "set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m" )
    parser.add_option( "--bjetbin-vjets", dest = "bjetbin_VJets", default = '2m',
                      help = "set b-jet multiplicity for V+Jets samples. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m" )
    parser.add_option( "-m", "--metType", dest = "metType", default = 'type1',
                      help = "set MET type for analysis of MET, ST or MT" )
    parser.add_option( "-c", "--centre-of-mass-energy", dest = "CoM", default = 13, type = int,
                      help = "set the centre of mass energy for analysis. Default = 13 [TeV]" )
    parser.add_option( '--fitter', dest = "use_fitter", default = 'Minuit',
                      help = 'Fitter to be used: Minuit|RooFit. Default = Minuit.' )
    parser.add_option( '-V', '--verbose', dest = "verbose", action = "store_true",
                      help = "Print the fit info and correlation matrix" )
    parser.add_option( '--closure_test', dest = "closure_test", action = "store_true",
                      help = "Perform fit on data == sum(MC) * scale factor (MC process)" )
    parser.add_option( '--closure_test_type', dest = "closure_test_type", default = 'simple',
                      help = "Type of closure test (relative normalisation):" + '|'.join( closure_tests.keys() ) )
    parser.add_option( '--no_combined_signal', dest = "make_combined_signal", 
                       action = "store_false", default=False,
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
    met_systematics = measurement_config.met_systematics
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
    data_file_electron = measurement_config.data_file_electron_trees
    data_file_muon = measurement_config.data_file_muon_trees


    SingleTop_file = measurement_config.SingleTop_tree_file
    muon_QCD_MC_file = measurement_config.muon_QCD_MC_tree_file
    electron_QCD_MC_file = measurement_config.electron_QCD_MC_tree_file
    TTJet_file = measurement_config.ttbar_category_templates_trees['central']
    VJets_file = measurement_config.VJets_category_templates_trees['central']
    electron_control_region = measurement_config.electron_control_region
    muon_control_region = measurement_config.muon_control_region
    Higgs_file = None
    if measurement_config.include_higgs:
        Higgs_file = measurement_config.higgs_category_templates['central']

    # Using 8 TeV VJets systematic samples for 7 TeV so need to scale:
    # vjets ratio = sigma(7TeV)*lumi(7TeV)/(sigma(8TeV)*lumi(8TeV))
    vjets_ratio = ( 31314 * 5050 ) / ( 36257.2 * 19584 )
    scale_factors = {}
    if measurement_config.centre_of_mass_energy == 7:
        scale_factors['V+Jets'] = vjets_ratio

    # matching/scale up/down systematics for V+Jets
    # for systematic in generator_systematics:
    #     if run_just_central:  # no systematics for closure test
    #         continue
    #     VJets_file = File( measurement_config.generator_systematic_vjets_templates[systematic] )
    #     if verbose:
    #         print "\n" + systematic + "\n"
    #     fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation_from_ROOT( 'electron',
    #                   input_files = {
    #                                'TTJet': TTJet_file,
    #                                'SingleTop': SingleTop_file,
    #                                'V+Jets': VJets_file,
    #                                'data': data_file_electron,
    #                                'Higgs' : Higgs_file,
    #                                },
    #                   variable = variable,
    #                   met_type = met_type,
    #                   b_tag_bin = b_tag_bin,
    #                   scale_factors = scale_factors,
    #                   )

    #     fit_results_muon, initial_values_muon, templates_muon = get_fitted_normalisation_from_ROOT( 'muon',
    #                   input_files = {
    #                                'TTJet': TTJet_file,
    #                                'SingleTop': SingleTop_file,
    #                                'V+Jets': VJets_file,
    #                                'data': data_file_muon,
    #                                'Higgs' : Higgs_file,
    #                                },
    #                   variable = variable,
    #                   met_type = met_type,
    #                   b_tag_bin = b_tag_bin,
    #                   scale_factors = scale_factors,
    #                   )

    #     write_fit_results_and_initial_values( 'electron', vjets_theory_systematic_prefix + systematic, fit_results_electron, initial_values_electron, templates_electron )
    #     write_fit_results_and_initial_values( 'muon', vjets_theory_systematic_prefix + systematic, fit_results_muon, initial_values_muon, templates_muon )
    #     write_fit_results( 'combined', vjets_theory_systematic_prefix + systematic, combine_complex_results( fit_results_electron, fit_results_muon ) )
    #     VJets_file.Close()

    # reset template back to central
    VJets_file = measurement_config.VJets_category_templates_trees['central']
    del scale_factors

    allCategories = categories_and_prefixes
    allCategories.update( measurement_config.rate_changing_systematics )

    # central measurement and the rest of the systematics
    last_systematic = ''
    for category, prefix in allCategories.iteritems():
        if run_just_central and not category == 'central': 
            continue

        if not ( category == 'JES_up' ):
            continue
        print 'Doing category :',category
        # Will want to use central template for rate changing systematic
        categoryForTemplates = category

        # For JES, use different tree
        # For other systematics and central, use different weights
        treePrefix = ''
        weightBranch = ''
        met_systematic = ''
        if category in ['JES_up', 'JES_down', 'JES_up_alphaCorr', 'JES_down_alphaCorr']:

            treePrefix = prefix
            met_systematic = category
            # print variable
            # if 'MET' in variable :
            #     print 'Changing variable from ',variable
            #     variable = 'MET_Uncertainties[2]'
            #     print 'to',variable
        elif category in met_systematics.keys():
            met_systematic = category
        elif category not in measurement_config.rate_changing_systematics:
            weightBranch = prefix

        # Changes for rate changing systematics
        scaleFactor = {}
        if category in ['luminosity_up', 'TTJet_cross_section_up', 'SingleTop_cross_section_up']:
            scaleFactor[category] = 1.0 + prefix
            categoryForTemplates = 'central'
        elif category in ['luminosity_down', 'TTJet_cross_section_down', 'SingleTop_cross_section_down']:
            scaleFactor[category] = 1.0 - prefix
            categoryForTemplates = 'central'

        TTJet_file = measurement_config.ttbar_category_templates_trees[categoryForTemplates]
        SingleTop_file = measurement_config.SingleTop_category_templates_trees[categoryForTemplates]
        VJets_file = measurement_config.VJets_category_templates_trees[categoryForTemplates]
        QCD_muon_file = measurement_config.muon_QCD_MC_category_templates_trees[categoryForTemplates]
        QCD_electron_file = measurement_config.electron_QCD_MC_category_templates_trees[categoryForTemplates]
        data_file_electron = measurement_config.data_electron_category_templates_trees
        data_file_muon = measurement_config.data_muon_category_templates_trees
 
        # # Setting up systematic MET for JES up/down samples
        # met_type = translate_options[options.metType]
        # if category in ['JES_up', 'JES_down']:  # these systematics affect the data as well
        #     data_file_electron.Close()
        #     data_file_muon.Close()
        #     data_file_electron = File( measurement_config.data_electron_category_templates[category] )
        #     data_file_muon = File( measurement_config.data_muon_category_templates[category] )
 
        # if category == 'JES_up':
        #     met_type += 'JetEnUp'
        #     if met_type == 'PFMETJetEnUp':
        #         met_type = 'patPFMetJetEnUp'
        # elif category == 'JES_down':
        #     met_type += 'JetEnDown'
        #     if met_type == 'PFMETJetEnDown':
        #         met_type = 'patPFMetJetEnDown'
 
        if verbose:
            print "\n" + category + "\n"
 
        print 'Electron'
        fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation_from_ROOT( 'electron',
                      input_files = {
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'QCD' : QCD_electron_file,
                                   'data': data_file_electron,
                                   },
                      variable = variable,
                      met_systematic = met_systematic,
                      met_type = met_type,
                      b_tag_bin = b_tag_bin,
                      treePrefix = treePrefix,
                      weightBranch = weightBranch,
                      scale_factors = scaleFactor,
                      )
 
        print 'Muon'
        fit_results_muon, initial_values_muon, templates_muon = get_fitted_normalisation_from_ROOT( 'muon',
                      input_files = {
                                   'TTJet': TTJet_file,
                                   'SingleTop': SingleTop_file,
                                   'V+Jets': VJets_file,
                                   'QCD' : QCD_muon_file,
                                   'data': data_file_muon,
                                   },
                      variable = variable,
                      met_systematic = met_systematic,
                      met_type = met_type,
                      b_tag_bin = b_tag_bin,
                      treePrefix = treePrefix,
                      weightBranch = weightBranch,
                      scale_factors = scaleFactor,
                      )
        write_fit_results_and_initial_values( 'electron', category, fit_results_electron, initial_values_electron, templates_electron )
        write_fit_results_and_initial_values( 'muon', category, fit_results_muon, initial_values_muon, templates_muon )
        fit_results_combined = combine_complex_results( fit_results_electron, fit_results_muon )
        initial_values_combined = combine_complex_results( initial_values_electron, initial_values_muon)
        write_fit_results_and_initial_values( 'combined', category, fit_results_combined, initial_values_combined)
        last_systematic = category
 
        # TTJet_file.Close()
        # SingleTop_file.Close()
        # VJets_file.Close()
        # data_file_electron.Close()
        # data_file_muon.Close()
        # if Higgs_file:
        #     Higgs_file.Close()
 


    # data_file_electron = File( measurement_config.data_electron_category_templates_trees )
    # data_file_muon = File( measurement_config.data_muon_category_templates_trees )
    # TTJet_file = File( measurement_config.ttbar_category_templates_trees['central'] )
    # SingleTop_file = File( measurement_config.SingleTop_category_templates_trees['central'] )
    # VJets_file = File( measurement_config.VJets_category_templates_trees['central'] )
 
    # # QCD systematic
    # if not run_just_central:
    #     electron_control_region = measurement_config.electron_control_region_systematic
     
    #     if verbose:
    #         print "\nQCD shape systematic\n"
     
    #     fit_results_electron, initial_values_electron, templates_electron = get_fitted_normalisation_from_ROOT( 'electron',
    #                       input_files = {
    #                                    'TTJet': TTJet_file,
    #                                    'SingleTop': SingleTop_file,
    #                                    'V+Jets': VJets_file,
    #                                    'data': data_file_electron,
    #                                    'Higgs' : Higgs_file,
    #                                    },
    #                       variable = variable,
    #                       met_type = met_type,
    #                       b_tag_bin = b_tag_bin,
    #                       )
     
    #     muon_control_region = measurement_config.muon_control_region_systematic
    #     fit_results_muon, initial_values_muon, templates_muon = get_fitted_normalisation_from_ROOT( 'muon',
    #                   input_files = {
    #                                'TTJet': TTJet_file,
    #                                'SingleTop': SingleTop_file,
    #                                'V+Jets': VJets_file,
    #                                'data': data_file_muon,
    #                                'Higgs' : Higgs_file,
    #                                },
    #                   variable = variable,
    #                   met_type = met_type,
    #                   b_tag_bin = b_tag_bin,
    #                   )
     
    #     systematic = 'QCD_shape'
    #     write_fit_results_and_initial_values( 'electron', systematic, fit_results_electron, initial_values_electron, templates_electron )
    #     write_fit_results_and_initial_values( 'muon', systematic, fit_results_muon, initial_values_muon, templates_muon )
    #     write_fit_results( 'combined', systematic, combine_complex_results( fit_results_electron, fit_results_muon ) )
 
    # electron_control_region = measurement_config.electron_control_region
    # muon_control_region = measurement_config.muon_control_region
 
    

