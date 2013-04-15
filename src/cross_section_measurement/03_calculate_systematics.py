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
from math import sqrt

from config.cross_section_measurement_common import met_systematics_suffixes, translate_options
from tools.file_utilities import read_data_from_JSON, write_data_to_JSON
from tools.Calculation import calculate_lower_and_upper_PDFuncertainty, \
    calculate_lower_and_upper_systematics, combine_errors_in_quadrature

def read_normalised_xsection_measurement(category, channel):
    global path_to_JSON, met_type
    
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
        systematic, systematic_unfolded = read_normalised_xsection_measurement(systematic_name, 'electron')
        
        systematics[systematic_name] = systematic
        systematics_unfolded[systematic_name] = systematic_unfolded
        
    return systematics, systematics_unfolded

def summarise_systematics(list_of_central_measurements, dictionary_of_systematics, pdf_calculation=False):
    global symmetrise_errors
    
    n_entries = len(list_of_central_measurements)
    down_errors = [0] * n_entries
    up_errors = [0] * n_entries
    
    for index in range(n_entries):
        central_value = list_of_central_measurements[index][0]  # 0 = value, 1 = error
        error_down, error_up = 0, 0
        
        if pdf_calculation:
            pdf_uncertainty_values = {systematic:measurement[index][0] for systematic, measurement in dictionary_of_systematics.iteritems()}
            error_down, error_up = calculate_lower_and_upper_PDFuncertainty(central_value, pdf_uncertainty_values)
            if symmetrise_errors:
                error_down = max(error_down, error_up)
                error_up = max(error_down, error_up)
        else:
            list_of_systematics = [systematic[index][0] for systematic in dictionary_of_systematics.values()]
            print list_of_systematics
            error_down, error_up = calculate_lower_and_upper_systematics(central_value, list_of_systematics, symmetrise_errors)

        down_errors[index] = error_down
        up_errors[index] = error_up
    
    return down_errors, up_errors

def get_measurement_with_lower_and_upper_errors(list_of_central_measurements, lists_of_lower_systematic_errors, lists_of_upper_systematic_errors):
    '''
    Combines a list of systematic errors with the error from the measurement in quadrature.
    @param list_of_central_measurements: A list of measurements - one per bin - of the type (value,error)
    @param lists_of_lower_systematic_errors: Lists of systematic errors - format: [error1, error2, ...] where errorX = [(error), ...] with length = len(list_of_central_measurements)
    '''
    n_entries = len(list_of_central_measurements)
    complete_measurement = [(0,0,0)] * n_entries
    
    for index in range(n_entries):
        central_value, central_error = list_of_central_measurements[index]  # 0 = value, 1 = error
        lower_errors = [error[index] for error in lists_of_lower_systematic_errors]
        upper_errors = [error[index] for error in lists_of_upper_systematic_errors]
        #add central error to the list
        lower_errors.append(central_error)
        upper_errors.append(central_error)
        #calculate total errors
        total_lower_error = combine_errors_in_quadrature(lower_errors)
        total_upper_error = combine_errors_in_quadrature(upper_errors)
        complete_measurement[index] = (central_value, total_lower_error, total_upper_error)
    
    return complete_measurement
        
         
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
                      dest="k_value", default=6,
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
    path_to_JSON = options.path + '/' + variable + '/xsection_measurement_results' + '/kv' + str(k_value) + '/'
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
    # ttbar theory systematics: scale & matching    
    ttbar_theory_uncertainties = []  # not implemented yet
    # 44 PDF uncertainties
    pdf_uncertainties = ['PDFWeights_%d' % index for index in range(1, 45)]
    # all MET uncertainties except JES and JER as this is already included
    met_uncertainties = [met_type + suffix for suffix in met_systematics_suffixes if not 'JetEn' in suffix and not 'JetRes' in suffix]
    # all other uncertainties (including JES and JER)
    other_uncertainties = deepcopy(measurement_config.categories_and_prefixes.keys())
    other_uncertainties.extend(measurement_config.generator_systematics)
    
    # read everything
    electron_central_measurement, electron_central_measurement_unfolded = read_normalised_xsection_measurement('central', 'electron')
    muon_central_measurement, muon_central_measurement_unfolded = read_normalised_xsection_measurement('central', 'muon')
    combined_central_measurement, combined_central_measurement_unfolded = read_normalised_xsection_measurement('central', 'combined')
    
    electron_ttbar_theory_systematics, electron_ttbar_theory_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=ttbar_theory_uncertainties , channel='electron')
    muon_ttbar_theory_systematics, muon_ttbar_theory_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=ttbar_theory_uncertainties , channel='muon')
    combined_ttbar_theory_systematics, combined_ttbar_theory_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=ttbar_theory_uncertainties , channel='combined')

    electron_pdf_systematics, electron_pdf_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=pdf_uncertainties , channel='electron')
    muon_pdf_systematics, muon_pdf_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=pdf_uncertainties , channel='muon')
    combined_pdf_systematics, combined_pdf_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=pdf_uncertainties , channel='combined')
    
    electron_met_systematics, electron_met_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=met_uncertainties , channel='electron')
    muon_met_systematics, muon_met_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=met_uncertainties , channel='muon')
    combined_met_systematics, combined_met_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=met_uncertainties , channel='combined')

    electron_other_systematics, electron_other_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=other_uncertainties , channel='electron')
    muon_other_systematics, muon_other_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=other_uncertainties , channel='muon')
    combined_other_systematics, combined_other_systematics_unfolded = read_normalised_xsection_systematics(list_of_systematics=other_uncertainties , channel='combined')
    
    # summarise
    # PDFs
    electron_pdf_min, electron_pdf_max = summarise_systematics(electron_central_measurement, electron_pdf_systematics, pdf_calculation=True)
    electron_pdf_min_unfolded, electron_pdf_max_unfolded = summarise_systematics(electron_central_measurement_unfolded, electron_pdf_systematics_unfolded, pdf_calculation=True)
    muon_pdf_min, muon_pdf_max = summarise_systematics(muon_central_measurement, muon_pdf_systematics, pdf_calculation=True)
    muon_pdf_min_unfolded, muon_pdf_max_unfolded = summarise_systematics(muon_central_measurement_unfolded, muon_pdf_systematics_unfolded, pdf_calculation=True)
    combined_pdf_min, combined_pdf_max = summarise_systematics(combined_central_measurement, combined_pdf_systematics, pdf_calculation=True)
    combined_pdf_min_unfolded, combined_pdf_max_unfolded = summarise_systematics(combined_central_measurement_unfolded, combined_pdf_systematics_unfolded, pdf_calculation=True)
    # MET
    electron_met_min, electron_met_max = summarise_systematics(electron_central_measurement, electron_met_systematics)
    electron_met_min_unfolded, electron_met_max_unfolded = summarise_systematics(electron_central_measurement_unfolded, electron_met_systematics_unfolded)
    muon_met_min, muon_met_max = summarise_systematics(muon_central_measurement, muon_met_systematics)
    muon_met_min_unfolded, muon_met_max_unfolded = summarise_systematics(muon_central_measurement_unfolded, muon_met_systematics_unfolded)
    combined_met_min, combined_met_max = summarise_systematics(combined_central_measurement, combined_met_systematics)
    combined_met_min_unfolded, combined_met_max_unfolded = summarise_systematics(combined_central_measurement_unfolded, combined_met_systematics_unfolded)
    # other
    electron_other_min, electron_other_max = summarise_systematics(electron_central_measurement, electron_other_systematics)
    electron_other_min_unfolded, electron_other_max_unfolded = summarise_systematics(electron_central_measurement_unfolded, electron_other_systematics_unfolded)
    muon_other_min, muon_other_max = summarise_systematics(muon_central_measurement, muon_other_systematics)
    muon_other_min_unfolded, muon_other_max_unfolded = summarise_systematics(muon_central_measurement_unfolded, muon_other_systematics_unfolded)
    combined_other_min, combined_other_max = summarise_systematics(combined_central_measurement, combined_other_systematics)
    combined_other_min_unfolded, combined_other_max_unfolded = summarise_systematics(combined_central_measurement_unfolded, combined_other_systematics_unfolded)
    
    
    
    electron_central_measurement_with_systematics = get_measurement_with_lower_and_upper_errors(electron_central_measurement, 
                                                                                                [electron_pdf_min, electron_met_min, electron_other_min], 
                                                                                                [electron_pdf_max, electron_met_max, electron_other_max])
    electron_central_measurement_unfolded_with_systematics = get_measurement_with_lower_and_upper_errors(electron_central_measurement_unfolded, 
                                                                                                [electron_pdf_min_unfolded, electron_met_min_unfolded, electron_other_min_unfolded], 
                                                                                                [electron_pdf_max_unfolded, electron_met_max_unfolded, electron_other_max_unfolded])
    
    muon_central_measurement_with_systematics = get_measurement_with_lower_and_upper_errors(muon_central_measurement, 
                                                                                                [muon_pdf_min, muon_met_min, muon_other_min], 
                                                                                                [muon_pdf_max, muon_met_max, muon_other_max])
    muon_central_measurement_unfolded_with_systematics = get_measurement_with_lower_and_upper_errors(muon_central_measurement_unfolded, 
                                                                                                [muon_pdf_min_unfolded, muon_met_min_unfolded, muon_other_min_unfolded], 
                                                                                                [muon_pdf_max_unfolded, muon_met_max_unfolded, muon_other_max_unfolded])
    
    combined_central_measurement_with_systematics = get_measurement_with_lower_and_upper_errors(combined_central_measurement, 
                                                                                                [combined_pdf_min, combined_met_min, combined_other_min], 
                                                                                                [combined_pdf_max, combined_met_max, combined_other_max])
    combined_central_measurement_unfolded_with_systematics = get_measurement_with_lower_and_upper_errors(combined_central_measurement_unfolded, 
                                                                                                [combined_pdf_min_unfolded, combined_met_min_unfolded, combined_other_min_unfolded], 
                                                                                                [combined_pdf_max_unfolded, combined_met_max_unfolded, combined_other_max_unfolded])
    
    write_normalised_xsection_measurement(electron_central_measurement_with_systematics, electron_central_measurement_unfolded_with_systematics, 'electron')
    write_normalised_xsection_measurement(muon_central_measurement_with_systematics, muon_central_measurement_unfolded_with_systematics, 'muon')
    write_normalised_xsection_measurement(combined_central_measurement_with_systematics, combined_central_measurement_unfolded_with_systematics, 'combined')
    
    #create entries in the previous dictionary
    electron_pdf_systematics['total_lower'], electron_pdf_systematics['total_upper'] = electron_pdf_min, electron_pdf_max
    muon_pdf_systematics['total_lower'], muon_pdf_systematics['total_upper'] = muon_pdf_min, muon_pdf_max
    combined_pdf_systematics['total_lower'], combined_pdf_systematics['total_upper'] = combined_pdf_min, combined_pdf_max
    electron_pdf_systematics_unfolded['total_lower'], electron_pdf_systematics_unfolded['total_upper'] = electron_pdf_min_unfolded, electron_pdf_max_unfolded
    muon_pdf_systematics_unfolded['total_lower'], muon_pdf_systematics_unfolded['total_upper'] = muon_pdf_min_unfolded, muon_pdf_max_unfolded
    combined_pdf_systematics_unfolded['total_lower'], combined_pdf_systematics_unfolded['total_upper'] = combined_pdf_min_unfolded, combined_pdf_max_unfolded
    
    electron_met_systematics['total_lower'], electron_met_systematics['total_upper'] = electron_met_min, electron_met_max
    muon_met_systematics['total_lower'], muon_met_systematics['total_upper'] = muon_met_min, muon_met_max
    combined_met_systematics['total_lower'], combined_met_systematics['total_upper'] = combined_met_min, combined_met_max
    electron_met_systematics_unfolded['total_lower'], electron_met_systematics_unfolded['total_upper'] = electron_met_min_unfolded, electron_met_max_unfolded
    muon_met_systematics_unfolded['total_lower'], muon_met_systematics_unfolded['total_upper'] = muon_met_min_unfolded, muon_met_max_unfolded
    combined_met_systematics_unfolded['total_lower'], combined_met_systematics_unfolded['total_upper'] = combined_met_min_unfolded, combined_met_max_unfolded
    
    electron_other_systematics['total_lower'], electron_other_systematics['total_upper'] = electron_other_min, electron_other_max
    muon_other_systematics['total_lower'], muon_other_systematics['total_upper'] = muon_other_min, muon_other_max
    combined_other_systematics['total_lower'], combined_other_systematics['total_upper'] = combined_other_min, combined_other_max
    electron_other_systematics_unfolded['total_lower'], electron_other_systematics_unfolded['total_upper'] = electron_other_min_unfolded, electron_other_max_unfolded
    muon_other_systematics_unfolded['total_lower'], muon_other_systematics_unfolded['total_upper'] = muon_other_min_unfolded, muon_other_max_unfolded
    combined_other_systematics_unfolded['total_lower'], combined_other_systematics_unfolded['total_upper'] = combined_other_min_unfolded, combined_other_max_unfolded
    
    write_normalised_xsection_measurement(electron_pdf_systematics, electron_pdf_systematics_unfolded, 'electron', summary='PDF')
    write_normalised_xsection_measurement(muon_pdf_systematics, muon_pdf_systematics_unfolded, 'muon', summary='PDF')
    write_normalised_xsection_measurement(combined_pdf_systematics, combined_pdf_systematics_unfolded, 'combined', summary='PDF')
    
    write_normalised_xsection_measurement(electron_met_systematics, electron_met_systematics_unfolded, 'electron', summary='MET')
    write_normalised_xsection_measurement(muon_met_systematics, muon_met_systematics_unfolded, 'muon', summary='MET')
    write_normalised_xsection_measurement(combined_met_systematics, combined_met_systematics_unfolded, 'combined', summary='MET')
    
    write_normalised_xsection_measurement(electron_other_systematics, electron_other_systematics_unfolded, 'electron', summary='other')
    write_normalised_xsection_measurement(muon_other_systematics, muon_other_systematics_unfolded, 'muon', summary='other')
    write_normalised_xsection_measurement(combined_other_systematics, combined_other_systematics_unfolded, 'combined', summary='other')
