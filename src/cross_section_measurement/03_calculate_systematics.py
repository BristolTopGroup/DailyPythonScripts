
'''
Created on 10 April 2013

@author: kreczko

This module produces several results for the three channels (electron, muon, combined):
1) central measurement with error =  sqrt([combined systematic uncertainties]^2 + [unfolding]^2)
2) all systematics evaluated with respect to central: up & down shifts, MET summary, PDF summary, Total up & down
3) additional result for MET systematics
4) additional result for PDF systematics
5) additional result for TTJet theory systematic (so we can compare to them!)

1) + existing result can be used for the final plots
2) can be used to compare systematics (both in tables and plots)
3) + 4) for more fine-grained analysis
'''
from __future__ import division, print_function
from optparse import OptionParser
from copy import deepcopy

from config import XSectionConfig
from tools.file_utilities import read_data_from_JSON, write_data_to_JSON
from tools.Calculation import calculate_lower_and_upper_PDFuncertainty, \
calculate_lower_and_upper_systematics, combine_errors_in_quadrature

def read_normalised_xsection_measurement( category, channel ):
    global path_to_JSON, met_type, met_uncertainties_list, method
    filename = '{path}/{category}/normalised_xsection_{channel}_{method}.txt'
    if category in met_systematics_suffixes and ( variable in measurement_config.variables_no_met ) and not ('JES' in category or 'JER' in category):
        filename = filename.format(
                    path = path_to_JSON,
                    channel = channel,
                    category = 'central',
                    method = method,
                    )
    else:
        filename = filename.format(
                    path = path_to_JSON,
                    channel = channel,
                    category = category,
                    method = method)

    normalised_xsection = read_data_from_JSON( filename )
    
    measurement = normalised_xsection['TTJet_measured']
    measurement_unfolded = normalised_xsection['TTJet_unfolded']
    
    return measurement, measurement_unfolded

def write_normalised_xsection_measurement( measurement, measurement_unfolded, channel, summary = '' ):
    global path_to_JSON, method
    output_file = '{path_to_JSON}/central/normalised_xsection_{channel}_{method}_with_errors.txt'
    output_file = output_file.format(
                    path_to_JSON = path_to_JSON,
                    channel = channel,
                    method = method,
                    )
    
    if not summary == '':
        output_file = output_file.replace( 'with_errors', summary + '_errors' )
    
    output = {'TTJet_measured':measurement, 'TTJet_unfolded': measurement_unfolded}
    
    write_data_to_JSON( output, output_file )

def read_normalised_xsection_systematics( list_of_systematics, channel ):
    systematics = {}
    systematics_unfolded = {}
    
    for systematic_name in list_of_systematics:
        systematic, systematic_unfolded = read_normalised_xsection_measurement( systematic_name, channel )
        
        systematics[systematic_name] = systematic
        systematics_unfolded[systematic_name] = systematic_unfolded
        
    return systematics, systematics_unfolded

def summarise_systematics( list_of_central_measurements, dictionary_of_systematics, pdf_calculation = False, hadronisation_systematic = False, mass_systematic = False, kValueSystematic = False, experimentalUncertainty = False, actualCentralMeasurements = [] ):
    global symmetrise_errors
    # number of bins
    number_of_bins = len( list_of_central_measurements )
    down_errors = [0] * number_of_bins
    up_errors = [0] * number_of_bins

    for bin_i in range( number_of_bins ):
        central_value = list_of_central_measurements[bin_i][0]  # 0 = value, 1 = error
        error_down, error_up = 0, 0
        
        if pdf_calculation:
            pdf_uncertainty_values = {systematic:measurement[bin_i][0] for systematic, measurement in dictionary_of_systematics.iteritems()}
            error_down, error_up = calculate_lower_and_upper_PDFuncertainty( central_value, pdf_uncertainty_values )
            if symmetrise_errors:
                error_down = max( error_down, error_up )
                error_up = max( error_down, error_up )
        elif hadronisation_systematic:
            # always symmetric: absolute value of the difference between powheg_herwig and powheg_pythia
            powheg_herwig = dictionary_of_systematics['TTJets_hadronisation'][bin_i][0]
            powheg_pythia = central_value
            difference = powheg_herwig - powheg_pythia
            difference = abs(difference)
            error_down = difference
            error_up = difference

        elif mass_systematic:
            list_of_systematics = [systematic[bin_i][0] for systematic in dictionary_of_systematics.values()]
            error_down, error_up = calculate_lower_and_upper_systematics( central_value, list_of_systematics, False )
            # Scale errors calculated using very different top masses
            error_down, error_up = scaleTopMassSystematicErrors( [error_down], [error_up] )
            error_down = error_down[0]
            error_up = error_up[0]
        elif kValueSystematic:
            list_of_systematics = [systematic[bin_i][0] for systematic in dictionary_of_systematics.values()]
            error_down, error_up = calculate_lower_and_upper_systematics( central_value, list_of_systematics, True )
        elif experimentalUncertainty:
            list_of_systematics = [systematic[bin_i][0] for systematic in dictionary_of_systematics.values()]
            error_down, error_up = calculate_lower_and_upper_systematics( central_value, list_of_systematics, symmetrise_errors )
            actualCentralValue = actualCentralMeasurements[bin_i][0]
            error_down = error_down / central_value * actualCentralValue
            error_up = error_up / central_value * actualCentralValue
        else:
            list_of_systematics = [systematic[bin_i][0] for systematic in dictionary_of_systematics.values()]
            error_down, error_up = calculate_lower_and_upper_systematics( central_value, list_of_systematics, symmetrise_errors )
        down_errors[bin_i] = error_down
        up_errors[bin_i] = error_up
    
    return down_errors, up_errors

def scaleTopMassSystematicErrors( error_down, error_up ):
    error_down_new, error_up_new = [], []
    for down,up in zip( error_down,error_up ):
        upMassDifference = measurement_config.topMasses[2] - measurement_config.topMasses[1]
        downMassDifference = measurement_config.topMasses[1] - measurement_config.topMasses[0]

        error_down_new.append( down * measurement_config.topMassUncertainty / downMassDifference )
        error_up_new.append( up * measurement_config.topMassUncertainty / upMassDifference )
    return error_down_new, error_up_new

def get_measurement_with_lower_and_upper_errors( list_of_central_measurements, lists_of_lower_systematic_errors, lists_of_upper_systematic_errors, systematicErrorsOnly = False ):
    '''
    Combines a list of systematic errors with the error from the measurement in quadrature.
    @param list_of_central_measurements: A list of measurements - one per bin - of the type (value,error)
    @param lists_of_lower_systematic_errors: Lists of systematic errors - format: [error1, error2, ...] where errorX = [(error), ...] with length = len(list_of_central_measurements)
    '''
    global symmetrise_errors
    
    n_entries = len( list_of_central_measurements )
    complete_measurement = [( 0, 0, 0 )] * n_entries
    
    for index in range( n_entries ):
        central_value, central_error = list_of_central_measurements[index]  # 0 = value, 1 = error
        lower_errors = [error[index] for error in lists_of_lower_systematic_errors]
        upper_errors = [error[index] for error in lists_of_upper_systematic_errors]
        # add central error to the list
        if not systematicErrorsOnly:
            lower_errors.append( central_error )
            upper_errors.append( central_error )

        # calculate total errors
        total_lower_error = combine_errors_in_quadrature( lower_errors )
        total_upper_error = combine_errors_in_quadrature( upper_errors )
        if symmetrise_errors:
            total_lower_error = max( total_lower_error, total_upper_error )
            total_upper_error = max( total_lower_error, total_upper_error )
        complete_measurement[index] = ( central_value, total_lower_error, total_upper_error )
    
    return complete_measurement
        
def replace_measurement_with_deviation_from_central( central_measurement, dictionary_of_systematic_measurements ):
    new_dictionary_of_systematic_measurements = {}
    
    for systematic, systematic_measurement in dictionary_of_systematic_measurements.iteritems():
        new_set_of_values = []
        for ( value, _ ), ( central, _ ) in zip( systematic_measurement, central_measurement ):
            deviation = abs( value ) - abs( central )    
            new_set_of_values.append( deviation )
        new_dictionary_of_systematic_measurements[systematic] = new_set_of_values
    return new_dictionary_of_systematic_measurements

if __name__ == "__main__":
    '''
    1) read all fit results (group by MET, PDF, other)
    2) calculate the difference to central measurement
    3) 
    '''
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data/M3_angle_bl/',
                  help = "set path to JSON files" )
    parser.add_option( "-v", "--variable", dest = "variable", default = 'MET',
                  help = "set variable to plot (MET, HT, ST, MT)" )
    parser.add_option( "-m", "--metType", dest = "metType", default = 'type1',
                      help = "set MET type used in the analysis of MET, ST or MT" )
    parser.add_option( "-b", "--bjetbin", dest = "bjetbin", default = '2m',
                  help = "set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m" )
    parser.add_option( "-c", "--centre-of-mass-energy", dest = "CoM", default = 13, type = int,
                      help = "set the centre of mass energy for analysis. Default = 13 [TeV]" )
    parser.add_option( "-s", "--symmetrise_errors", action = "store_true", dest = "symmetrise_errors",
                      help = "Makes the errors symmetric" )
    parser.add_option( '--visiblePS', dest = "visiblePS", action = "store_true",
                      help = "Unfold to visible phase space" )
    parser.add_option( "-u", "--unfolding_method", dest = "unfolding_method", default = 'TUnfold',
                      help = "Unfolding method:  TUnfold (default), RooUnfoldSvd, TSVDUnfold, RooUnfoldTUnfold, RooUnfoldInvert, RooUnfoldBinByBin, RooUnfoldBayes" )

    ( options, args ) = parser.parse_args()
    measurement_config = XSectionConfig( options.CoM )
    # caching of variables for shorter access
    translate_options = measurement_config.translate_options
    ttbar_theory_systematic_prefix = measurement_config.ttbar_theory_systematic_prefix
    vjets_theory_systematic_prefix = measurement_config.vjets_theory_systematic_prefix
    met_systematics_suffixes = measurement_config.met_systematics_suffixes
    met_systematics = measurement_config.met_systematics
    method = options.unfolding_method

    variable = options.variable

    visiblePS = options.visiblePS

    phase_space = 'FullPS'
    if visiblePS:
        phase_space = 'VisiblePS'

    met_type = translate_options[options.metType]
    b_tag_bin = translate_options[options.bjetbin]
    path_to_JSON = '{path}/{com}TeV/{variable}/{phase_space}/'
#     path_to_JSON += 'xsection_measurement_results/'
    path_to_JSON = path_to_JSON.format(path = options.path, com = options.CoM,
                                       variable = variable,
                                       phase_space = phase_space,
                                       )
#     path_to_JSON = options.path + '/' + str( options.CoM ) + 'TeV/' + variable + '/xsection_measurement_results_%s/' % phase_space
    symmetrise_errors = options.symmetrise_errors
    
    # set up lists for systematics
    ttbar_generator_systematics_list = [ttbar_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    # Remove hadronisation systematic from this list
    ttbar_generator_systematics_list.remove(ttbar_theory_systematic_prefix + 'hadronisation')

    ### vjets_generator_systematics_list = [vjets_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]

    # ttbar theory systematics: ptreweighting, hadronisation systematic (powheg_pythia - powheg_herwig)
    # ttbar_ptreweight_systematic_list = [ttbar_theory_systematic_prefix + 'ptreweight']
    ttbar_hadronisation_systematic_list = ['TTJets_hadronisation', 'TTJets_NLOgenerator']
    # print(ttbar_hadronisation_systematic_list)

    # 100 PDF uncertainties
    pdf_uncertainties = ['PDFWeights_%d' % index for index in range( 0, 100 )]

    # all MET uncertainties except JES and JER as this is already included
    met_uncertainties_list = [met_type + suffix for suffix in met_systematics_suffixes if not 'JetEn' in suffix and not 'JetRes' in suffix]

    # rate changing systematics (luminosity, ttbar/single top cross section uncertainties)
    rate_changing_systematics_list = [systematic for systematic in measurement_config.rate_changing_systematics_names]

    # all other uncertainties (including JES and JER)
    experimental_uncertainties_list = deepcopy( measurement_config.categories_and_prefixes.keys() )

    ### other_uncertainties_list.extend( vjets_generator_systematics_list )
    other_uncertainties_list = [ 'QCD_shape' ]
    other_uncertainties_list.extend( rate_changing_systematics_list )

    for channel in ['electron', 'muon', 'combined', 'combinedBeforeUnfolding']:
#         print("channel = ", channel)
        # read central measurement
        central_measurement, central_measurement_unfolded = read_normalised_xsection_measurement( 'central', channel )
        # central_TTJet_measurement, central_TTJet_measurement_unfolded = read_normalised_xsection_measurement( 'central_TTJet', channel )
        
        # read groups of systematics
        ttbar_generator_systematics, ttbar_generator_systematics_unfolded = read_normalised_xsection_systematics( list_of_systematics = ttbar_generator_systematics_list, channel = channel )
        # ttbar_ptreweight_systematic, ttbar_ptreweight_systematic_unfolded = read_normalised_xsection_systematics( list_of_systematics = ttbar_ptreweight_systematic_list, channel = channel )
        ttbar_hadronisation_systematic, ttbar_hadronisation_systematic_unfolded = read_normalised_xsection_systematics( list_of_systematics = ttbar_hadronisation_systematic_list, channel = channel )
        
        pdf_systematics, pdf_systematics_unfolded = read_normalised_xsection_systematics( list_of_systematics = pdf_uncertainties, channel = channel )
        experimental_systematics, experimental_systematics_unfolded = read_normalised_xsection_systematics( list_of_systematics = experimental_uncertainties_list, channel = channel )
        other_systematics, other_systematics_unfolded = read_normalised_xsection_systematics( list_of_systematics = other_uncertainties_list, channel = channel )

        ### # get the minimal and maximal deviation for each group of systematics
        ### # ttbar generator systematics (factorisation scale and matching threshold)
        ttbar_generator_min, ttbar_generator_max = summarise_systematics( central_measurement, ttbar_generator_systematics )
        ttbar_generator_min_unfolded, ttbar_generator_max_unfolded = summarise_systematics( central_measurement_unfolded, ttbar_generator_systematics_unfolded )

        ### # ttbar theory systematics (pt reweighting and hadronisation)
        ### # ttbar_ptreweight_min, ttbar_ptreweight_max = summarise_systematics( central_measurement, ttbar_ptreweight_systematic )
        ### # ttbar_ptreweight_min_unfolded, ttbar_ptreweight_max_unfolded = summarise_systematics( central_measurement_unfolded, ttbar_ptreweight_systematic_unfolded )
        ttbar_hadronisation_min, ttbar_hadronisation_max = summarise_systematics( central_measurement, ttbar_hadronisation_systematic, hadronisation_systematic = True )
        ttbar_hadronisation_min_unfolded, ttbar_hadronisation_max_unfolded = summarise_systematics( central_measurement_unfolded, ttbar_hadronisation_systematic_unfolded, hadronisation_systematic = True )
       

       # 100 PDFs
        pdf_min, pdf_max = summarise_systematics( central_measurement, pdf_systematics, pdf_calculation = True )
        pdf_min_unfolded, pdf_max_unfolded = summarise_systematics( central_measurement_unfolded, pdf_systematics_unfolded, pdf_calculation = True )

        experimental_min, experimental_max = summarise_systematics( central_measurement, experimental_systematics )
        experimental_min_unfolded, experimental_max_unfolded = summarise_systematics( central_measurement_unfolded, experimental_systematics_unfolded )


        # other
        other_min, other_max = summarise_systematics( central_measurement, other_systematics )
        other_min_unfolded, other_max_unfolded = summarise_systematics( central_measurement_unfolded, other_systematics_unfolded )
        # get the central measurement with fit, unfolding and systematic errors combined
        central_measurement_with_systematics = get_measurement_with_lower_and_upper_errors( central_measurement,
                                                                                                [
                                                                                                ttbar_generator_min, #ttbar_ptreweight_min,
                                                                                                ttbar_hadronisation_min,
                                                                                                ### ttbar_mass_min,
#                                                                                               ###   kValue_min,
                                                                                                pdf_min,
                                                                                                ### met_min,
                                                                                                experimental_min,
                                                                                                other_min],
                                                                                                [
                                                                                                ttbar_generator_max, #ttbar_ptreweight_max,
                                                                                                ttbar_hadronisation_max,
                                                                                                ### ttbar_mass_max,
#                                                                                               ###   kValue_max,
                                                                                                pdf_max,
                                                                                                ### met_max,
                                                                                                experimental_max,
                                                                                                other_max] )

        central_measurement_with_systematics_but_without_generator = get_measurement_with_lower_and_upper_errors( central_measurement,
                                                                                                [
                                                                                                ttbar_hadronisation_min,
                                                                                                ###ttbar_mass_min,
#                                                                                               ###  kValue_min,
                                                                                                pdf_min,
                                                                                                ### met_min,
                                                                                                experimental_min,
                                                                                                other_min],
                                                                                                [
                                                                                                ttbar_hadronisation_max,
                                                                                                ###ttbar_mass_max,
#                                                                                               ###  kValue_max,
                                                                                                pdf_max,
                                                                                                experimental_max,
                                                                                                ### met_max, 
                                                                                                 other_max] )

        central_measurement_with_systematics_only = get_measurement_with_lower_and_upper_errors( central_measurement,
                                                                                                [
                                                                                                ttbar_generator_min,
                                                                                                ttbar_hadronisation_min,
                                                                                                pdf_min,
                                                                                                experimental_min,
                                                                                                other_min,],
                                                                                                [
                                                                                                ttbar_generator_max,
                                                                                                ttbar_hadronisation_max,
                                                                                                pdf_max,
                                                                                                experimental_max,
                                                                                                other_max],
                                                                                                systematicErrorsOnly = True )

        central_measurement_unfolded_with_systematics = get_measurement_with_lower_and_upper_errors( central_measurement_unfolded,
                                                                                                [
                                                                                                ttbar_generator_min_unfolded, 
                                                                                                #ttbar_ptreweight_min_unfolded,
                                                                                                ttbar_hadronisation_min_unfolded,
                                                                                                ###ttbar_mass_min_unfolded,
#                                                                                               ###  kValue_min_unfolded,
                                                                                                pdf_min_unfolded, 
                                                                                                ### met_min_unfolded,
                                                                                                experimental_min_unfolded,
                                                                                                other_min_unfolded],
                                                                                                [
                                                                                                ttbar_generator_max_unfolded, 
                                                                                                #ttbar_ptreweight_max_unfolded,
                                                                                                ttbar_hadronisation_max_unfolded,
                                                                                                ###ttbar_mass_max_unfolded,
#                                                                                               ###  kValue_max_unfolded,
                                                                                                pdf_max_unfolded,
                                                                                                experimental_max_unfolded, 
                                                                                                ### met_max_unfolded,
                                                                                                other_max_unfolded] )
        central_measurement_unfolded_with_systematics_but_without_generator = get_measurement_with_lower_and_upper_errors( central_measurement_unfolded,
                                                                                                [
                                                                                                ttbar_hadronisation_min_unfolded,
                                                                                                ### ttbar_ptreweight_min_unfolded,
                                                                                                ###ttbar_mass_min_unfolded,
#                                                                                               ###  kValue_min_unfolded,
                                                                                                pdf_min_unfolded,
                                                                                                ### met_min_unfolded,
                                                                                                experimental_min_unfolded, 
                                                                                                 other_min_unfolded],
                                                                                                [
                                                                                                ttbar_hadronisation_max_unfolded,
                                                                                                ### ttbar_ptreweight_max_unfolded,
                                                                                                ### ttbar_mass_max_unfolded,
#                                                                                               ###  kValue_max_unfolded,
                                                                                                pdf_max_unfolded,
                                                                                                experimental_max_unfolded,
                                                                                                ### met_max_unfolded, 
                                                                                                 other_max_unfolded] )

        central_measurement_unfolded_with_systematics_only = get_measurement_with_lower_and_upper_errors( central_measurement_unfolded,
                                                                                                [
                                                                                                ttbar_generator_min_unfolded,
                                                                                                pdf_min_unfolded,
                                                                                                experimental_min_unfolded,
                                                                                                other_min_unfolded],
                                                                                                [
                                                                                                ttbar_hadronisation_max_unfolded,
                                                                                                pdf_max_unfolded,
                                                                                                experimental_max_unfolded,
                                                                                                other_max_unfolded],
                                                                                                systematicErrorsOnly = True )

        write_normalised_xsection_measurement( central_measurement_with_systematics,
                                               central_measurement_unfolded_with_systematics,
                                               channel )
        write_normalised_xsection_measurement( central_measurement_with_systematics_but_without_generator,
                                               central_measurement_unfolded_with_systematics_but_without_generator,
                                               channel,
                                               summary = 'with_systematics_but_without_generator' )

        write_normalised_xsection_measurement( central_measurement_with_systematics_only,
                                               central_measurement_unfolded_with_systematics_only,
                                               channel,
                                               summary = 'with_systematics_only' )

        # create entries in the previous dictionary
        # replace measurement with deviation from central
        ttbar_generator_systematics = replace_measurement_with_deviation_from_central( central_measurement, ttbar_generator_systematics )
        pdf_systematics = replace_measurement_with_deviation_from_central( central_measurement, pdf_systematics )
        ttbar_hadronisation_systematic = replace_measurement_with_deviation_from_central( central_measurement, ttbar_hadronisation_systematic )
        other_systematics = replace_measurement_with_deviation_from_central( central_measurement, other_systematics )
        experimental_systematics = replace_measurement_with_deviation_from_central( central_measurement, experimental_systematics )
        
        ttbar_generator_systematics_unfolded = replace_measurement_with_deviation_from_central( central_measurement_unfolded, ttbar_generator_systematics_unfolded )
        pdf_systematics_unfolded = replace_measurement_with_deviation_from_central( central_measurement_unfolded, pdf_systematics_unfolded )
        ttbar_hadronisation_systematic_unfolded = replace_measurement_with_deviation_from_central( central_measurement_unfolded, ttbar_hadronisation_systematic_unfolded )
        other_systematics_unfolded = replace_measurement_with_deviation_from_central( central_measurement_unfolded, other_systematics_unfolded )
        experimental_systematics_unfolded = replace_measurement_with_deviation_from_central( central_measurement_unfolded, experimental_systematics_unfolded )

        #### add total errors
        #### TODO: these are currently still storing the measurement, but should store the difference to the measurement like total_*
        ttbar_generator_systematics['total_lower'], ttbar_generator_systematics['total_upper'] = ttbar_generator_min, ttbar_generator_max
        ttbar_generator_systematics_unfolded['total_lower'], ttbar_generator_systematics_unfolded['total_upper'] = ttbar_generator_min_unfolded, ttbar_generator_max_unfolded

        pdf_systematics['PDF_total_lower'], pdf_systematics['PDF_total_upper'] = pdf_min, pdf_max
        pdf_systematics_unfolded['PDF_total_lower'], pdf_systematics_unfolded['PDF_total_upper'] = pdf_min_unfolded, pdf_max_unfolded

        ttbar_hadronisation_systematic['TTJets_hadronisation'], ttbar_hadronisation_systematic['TTJets_hadronisation'] = ttbar_hadronisation_min, ttbar_hadronisation_max
        ttbar_hadronisation_systematic_unfolded['TTJets_hadronisation'], ttbar_hadronisation_systematic_unfolded['TTJets_hadronisation'] = ttbar_hadronisation_min_unfolded, ttbar_hadronisation_max_unfolded
        
        other_systematics['total_lower'], other_systematics['total_upper'] = other_min, other_max

        other_systematics_unfolded['total_lower'], other_systematics_unfolded['total_upper'] = other_min_unfolded, other_max_unfolded

        experimental_systematics['total_lower'], experimental_systematics['total_upper'] = experimental_min, experimental_max
        experimental_systematics_unfolded['total_lower'], experimental_systematics_unfolded['total_upper'] = experimental_min_unfolded, experimental_max_unfolded

        write_normalised_xsection_measurement( ttbar_generator_systematics, ttbar_generator_systematics_unfolded, channel, summary = 'ttbar_generator' )
        write_normalised_xsection_measurement( pdf_systematics, pdf_systematics_unfolded, channel, summary = 'PDF' )
        write_normalised_xsection_measurement( ttbar_hadronisation_systematic, ttbar_hadronisation_systematic_unfolded, channel, summary = 'hadronisation' )
        write_normalised_xsection_measurement( other_systematics, other_systematics_unfolded, channel, summary = 'other' )
        write_normalised_xsection_measurement( experimental_systematics, experimental_systematics_unfolded, channel, summary = 'experimental' )
        
