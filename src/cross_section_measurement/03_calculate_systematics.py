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
from optparse import OptionParser
from copy import deepcopy

from config.cross_section_measurement_common import met_systematics_suffixes, translate_options, ttbar_theory_systematic_prefix, vjets_theory_systematic_prefix
from tools.file_utilities import read_data_from_JSON, write_data_to_JSON
from tools.Calculation import calculate_lower_and_upper_PDFuncertainty, \
    calculate_lower_and_upper_systematics, combine_errors_in_quadrature

def read_normalised_xsection_measurement(category, channel):
    global path_to_JSON, met_type, met_uncertainties
    normalised_xsection = None
    
    if category in met_uncertainties and variable == 'HT':
        normalised_xsection = read_data_from_JSON(path_to_JSON + 'central' + '/normalised_xsection_' + channel + '_' + met_type + '.txt')
    else:
        normalised_xsection = read_data_from_JSON(path_to_JSON + category + '/normalised_xsection_' + channel + '_' + met_type + '.txt')
    
    measurement = normalised_xsection['TTJet_measured']
    measurement_unfolded = normalised_xsection['TTJet_unfolded']
    
    return measurement, measurement_unfolded

def write_normalised_xsection_measurement(measurement, measurement_unfolded, channel, summary=''):
    global path_to_JSON, met_type
    output_file = path_to_JSON + 'central/normalised_xsection_' + channel + '_' + met_type + '_with_errors.txt'
    
    if not summary == '':
        output_file = output_file.replace('with_errors', summary + '_errors')
    
    output = {'TTJet_measured':measurement, 'TTJet_unfolded': measurement_unfolded}
    
    write_data_to_JSON(output, output_file)

def read_normalised_xsection_systematics(list_of_systematics, channel):
    systematics = {}
    systematics_unfolded = {}
    
    for systematic_name in list_of_systematics:
        systematic, systematic_unfolded = read_normalised_xsection_measurement(systematic_name, channel)
        
        systematics[systematic_name] = systematic
        systematics_unfolded[systematic_name] = systematic_unfolded
        
    return systematics, systematics_unfolded

def summarise_systematics(list_of_central_measurements, dictionary_of_systematics, pdf_calculation=False):
    global symmetrise_errors
    #number of bins
    number_of_bins = len(list_of_central_measurements)
    down_errors = [0] * number_of_bins
    up_errors = [0] * number_of_bins
    
    for bin_i in range(number_of_bins):
        central_value = list_of_central_measurements[bin_i][0]  # 0 = value, 1 = error
        error_down, error_up = 0, 0
        
        if pdf_calculation:
            pdf_uncertainty_values = {systematic:measurement[bin_i][0] for systematic, measurement in dictionary_of_systematics.iteritems()}
            error_down, error_up = calculate_lower_and_upper_PDFuncertainty(central_value, pdf_uncertainty_values)
            if symmetrise_errors:
                error_down = max(error_down, error_up)
                error_up = max(error_down, error_up)
        else:
            list_of_systematics = [systematic[bin_i][0] for systematic in dictionary_of_systematics.values()]
            error_down, error_up = calculate_lower_and_upper_systematics(central_value, list_of_systematics, symmetrise_errors)

        down_errors[bin_i] = error_down
        up_errors[bin_i] = error_up
    
    return down_errors, up_errors

def get_measurement_with_lower_and_upper_errors(list_of_central_measurements, lists_of_lower_systematic_errors, lists_of_upper_systematic_errors):
    '''
    Combines a list of systematic errors with the error from the measurement in quadrature.
    @param list_of_central_measurements: A list of measurements - one per bin - of the type (value,error)
    @param lists_of_lower_systematic_errors: Lists of systematic errors - format: [error1, error2, ...] where errorX = [(error), ...] with length = len(list_of_central_measurements)
    '''
    global symmetrise_errors
    
    n_entries = len(list_of_central_measurements)
    complete_measurement = [(0, 0, 0)] * n_entries
    
    for index in range(n_entries):
        central_value, central_error = list_of_central_measurements[index]  # 0 = value, 1 = error
        lower_errors = [error[index] for error in lists_of_lower_systematic_errors]
        upper_errors = [error[index] for error in lists_of_upper_systematic_errors]
        # add central error to the list
        lower_errors.append(central_error)
        upper_errors.append(central_error)
        # calculate total errors
        total_lower_error = combine_errors_in_quadrature(lower_errors)
        total_upper_error = combine_errors_in_quadrature(upper_errors)
        if symmetrise_errors:
            total_lower_error = max(total_lower_error, total_upper_error)
            total_upper_error = max(total_lower_error, total_upper_error)
        complete_measurement[index] = (central_value, total_lower_error, total_upper_error)
    
    return complete_measurement
        
def replace_measurement_with_deviation_from_central(central_measurement, dictionary_of_systematic_measurements):
    new_dictionary_of_systematic_measurements = {}
    
    for systematic, systematic_measurement in dictionary_of_systematic_measurements.iteritems():
        new_set_of_values = []
        for (value, _), (central, _) in zip(systematic_measurement, central_measurement):
            deviation = abs(value) - abs(central)    
            new_set_of_values.append(deviation)
        new_dictionary_of_systematic_measurements[systematic] = new_set_of_values
    return new_dictionary_of_systematic_measurements

if __name__ == "__main__":
    '''
    1) read all fit results (group by MET, PDF, other)
    2) calculate the difference to central measurement
    3) 
    '''
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data/',
                  help="set path to JSON files")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                  help="set variable to plot (MET, HT, ST, MT)")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type used in the analysis of MET, ST or MT")
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                  help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("-k", "--k_value", type='int',
                      dest="k_value", default=4,
                      help="k-value for SVD unfolding, used in histogram names")
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=8, type=int,
                      help="set the centre of mass energy for analysis. Default = 8 [TeV]")
    
    parser.add_option("-s", "--symmetrise_errors", action="store_true", dest="symmetrise_errors",
                      help="Makes the errors symmetric")
    
    (options, args) = parser.parse_args()
    variable = options.variable
    met_type = translate_options[options.metType]
    b_tag_bin = translate_options[options.bjetbin]
    k_value = options.k_value
    path_to_JSON = options.path + '/' + str(options.CoM) + 'TeV/' + variable + '/xsection_measurement_results' + '/kv' + str(k_value) + '/'
    symmetrise_errors = options.symmetrise_errors
    
    if options.CoM == 8:
        from config.variable_binning_8TeV import bin_widths, bin_edges
        import config.cross_section_measurement_8TeV as measurement_config
    elif options.CoM == 7:
        from config.variable_binning_7TeV import bin_widths, bin_edges
        import config.cross_section_measurement_7TeV as measurement_config
    else:
        import sys
        sys.exit('Unknown centre of mass energy')
    
    
    # set up lists for systematics
    ttbar_generator_systematics = [ttbar_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    vjets_generator_systematics = [vjets_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    # ttbar theory systematics: scale & matching    
    ttbar_theory_uncertainties = ttbar_generator_systematics  # not implemented yet
    # 44 PDF uncertainties
    pdf_uncertainties = ['PDFWeights_%d' % index for index in range(1, 45)]
    # all MET uncertainties except JES and JER as this is already included
    met_uncertainties = [met_type + suffix for suffix in met_systematics_suffixes if not 'JetEn' in suffix and not 'JetRes' in suffix]
    # all other uncertainties (including JES and JER)
    other_uncertainties = deepcopy(measurement_config.categories_and_prefixes.keys())
    other_uncertainties.extend(vjets_generator_systematics)
    new_uncertainties = [ttbar_theory_systematic_prefix + 'ptreweight', ttbar_theory_systematic_prefix + 'mcatnlo', ttbar_theory_systematic_prefix + 'mcatnlo_matrix']
    
    for channel in ['electron', 'muon', 'combined']:
        # read central measurement
        central_measurement, central_measurement_unfolded = read_normalised_xsection_measurement('central', channel)
        # read groups of systematics
        ttbar_theory_systematics, ttbar_theory_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=ttbar_theory_uncertainties, channel=channel)
        pdf_systematics, pdf_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=pdf_uncertainties, channel=channel)
        met_systematics, met_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=met_uncertainties, channel=channel)
        other_systematics, other_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=other_uncertainties, channel=channel)
        new_systematics, new_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=new_uncertainties, channel=channel)
        # get the minimal and maximal deviation for each group of systematics
        # ttbar theory (factorisation scale and matching threshold)
        ttbar_theory_min, ttbar_theory_max = summarise_systematics(central_measurement, ttbar_theory_systematics)
        ttbar_theory_min_unfolded, ttbar_theory_max_unfolded = summarise_systematics(central_measurement_unfolded, ttbar_theory_systematics_unfolded)
        # 44 PDFs
        pdf_min, pdf_max = summarise_systematics(central_measurement, pdf_systematics, pdf_calculation=True)
        pdf_min_unfolded, pdf_max_unfolded = summarise_systematics(central_measurement_unfolded, pdf_systematics_unfolded, pdf_calculation=True)
        # MET
        met_min, met_max = summarise_systematics(central_measurement, met_systematics)
        met_min_unfolded, met_max_unfolded = summarise_systematics(central_measurement_unfolded, met_systematics_unfolded)
        # other
        other_min, other_max = summarise_systematics(central_measurement, other_systematics)
        other_min_unfolded, other_max_unfolded = summarise_systematics(central_measurement_unfolded, other_systematics_unfolded)
        #new ones
        ptreweight_min, ptreweight_max = summarise_systematics(central_measurement, {'ptreweight':new_systematics[ttbar_theory_systematic_prefix + 'ptreweight']})
        ptreweight_min_unfolded, ptreweight_max_unfolded = summarise_systematics(central_measurement_unfolded, {'ptreweight':new_systematics_unfolded[ttbar_theory_systematic_prefix + 'ptreweight']})
        mcatnlo_min, mcatnlo_max =  summarise_systematics(central_measurement, {'mcatnlo_matrix':new_systematics[ttbar_theory_systematic_prefix + 'mcatnlo_matrix']})
        mcatnlo_min_unfolded, mcatnlo_max_unfolded =  summarise_systematics(central_measurement_unfolded, {'mcatnlo_matrix':new_systematics_unfolded[ttbar_theory_systematic_prefix + 'mcatnlo_matrix']})
        
        # get the central measurement with fit, unfolding and systematic errors combined
        central_measurement_with_systematics = get_measurement_with_lower_and_upper_errors(central_measurement,
                                                                                                [ttbar_theory_min, pdf_min, met_min, other_min, 
                                                                                                 ptreweight_min, mcatnlo_min],
                                                                                                [ttbar_theory_max, pdf_max, met_max, other_max, 
                                                                                                 ptreweight_max, mcatnlo_max])
        central_measurement_unfolded_with_systematics = get_measurement_with_lower_and_upper_errors(central_measurement_unfolded,
                                                                                                [ttbar_theory_min_unfolded, pdf_min_unfolded, met_min_unfolded, 
                                                                                                 other_min_unfolded, ptreweight_min_unfolded, mcatnlo_min_unfolded],
                                                                                                [ttbar_theory_max_unfolded, pdf_max_unfolded, met_max_unfolded, 
                                                                                                 other_max_unfolded, ptreweight_max_unfolded, mcatnlo_max_unfolded])
        
        write_normalised_xsection_measurement(central_measurement_with_systematics, central_measurement_unfolded_with_systematics, channel)
        
        # create entries in the previous dictionary
        # replace measurement with deviation from central
        ttbar_theory_systematics = replace_measurement_with_deviation_from_central(central_measurement, ttbar_theory_systematics)
        pdf_systematics = replace_measurement_with_deviation_from_central(central_measurement, pdf_systematics)
        met_systematics = replace_measurement_with_deviation_from_central(central_measurement, met_systematics)
        other_systematics = replace_measurement_with_deviation_from_central(central_measurement, other_systematics)
        new_systematics = replace_measurement_with_deviation_from_central(central_measurement, new_systematics)
#        ptreweight_systematics = replace_measurement_with_deviation_from_central(central_measurement, {'ptreweight':new_systematics[ttbar_theory_systematic_prefix + 'ptreweight']})
        
        ttbar_theory_systematics_unfolded = replace_measurement_with_deviation_from_central(central_measurement_unfolded, ttbar_theory_systematics_unfolded)
        pdf_systematics_unfolded = replace_measurement_with_deviation_from_central(central_measurement_unfolded, pdf_systematics_unfolded)
        met_systematics_unfolded = replace_measurement_with_deviation_from_central(central_measurement_unfolded, met_systematics_unfolded)
        other_systematics_unfolded = replace_measurement_with_deviation_from_central(central_measurement_unfolded, other_systematics_unfolded)
        new_systematics_unfolded = replace_measurement_with_deviation_from_central(central_measurement_unfolded, new_systematics_unfolded)
#        ptreweight_systematics_unfolded = replace_measurement_with_deviation_from_central(central_measurement_unfolded, {'ptreweight':new_systematics_unfolded[ttbar_theory_systematic_prefix + 'ptreweight']})
        # add total errors
        # TODO: these are currently still storing the measurement, but should store the difference to the measurement like total_*
        ttbar_theory_systematics['total_lower'], ttbar_theory_systematics['total_upper'] = ttbar_theory_min, ttbar_theory_max
        ttbar_theory_systematics_unfolded['total_lower'], ttbar_theory_systematics_unfolded['total_upper'] = ttbar_theory_min_unfolded, ttbar_theory_max_unfolded
        pdf_systematics['total_lower'], pdf_systematics['total_upper'] = pdf_min, pdf_max
        pdf_systematics_unfolded['total_lower'], pdf_systematics_unfolded['total_upper'] = pdf_min_unfolded, pdf_max_unfolded
        met_systematics['total_lower'], met_systematics['total_upper'] = met_min, met_max
        met_systematics_unfolded['total_lower'], met_systematics_unfolded['total_upper'] = met_min_unfolded, met_max_unfolded
        other_systematics['total_lower'], other_systematics['total_upper'] = other_min, other_max
        other_systematics_unfolded['total_lower'], other_systematics_unfolded['total_upper'] = other_min_unfolded, other_max_unfolded
        new_systematics['mcatnlo_min'], new_systematics['mcatnlo_max'] = mcatnlo_min, mcatnlo_max
        new_systematics_unfolded['mcatnlo_min'], new_systematics_unfolded['mcatnlo_max'] = mcatnlo_min_unfolded, mcatnlo_max_unfolded
        new_systematics['ptreweight_min'], new_systematics['ptreweight_max'] = ptreweight_min, ptreweight_max
        new_systematics_unfolded['ptreweight_min'], new_systematics_unfolded['ptreweight_max'] = ptreweight_min_unfolded, ptreweight_max_unfolded
        
        write_normalised_xsection_measurement(ttbar_theory_systematics, ttbar_theory_systematics_unfolded, channel, summary='ttbar_theory')
        write_normalised_xsection_measurement(pdf_systematics, pdf_systematics_unfolded, channel, summary='PDF')
        write_normalised_xsection_measurement(met_systematics, met_systematics_unfolded, channel, summary='MET')
        write_normalised_xsection_measurement(other_systematics, other_systematics_unfolded, channel, summary='other')
        write_normalised_xsection_measurement(new_systematics, new_systematics_unfolded, channel, summary='new')
        
