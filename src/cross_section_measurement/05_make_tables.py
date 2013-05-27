from __future__ import division  # the result of the division will be always a float
from optparse import OptionParser
import os
from copy import deepcopy
import ROOT
from config.cross_section_measurement_common import met_systematics_suffixes, translate_options, ttbar_theory_systematic_prefix, vjets_theory_systematic_prefix
from config.latex_labels import b_tag_bins_latex, variables_latex, measurements_latex, met_systematics_latex
from tools.Calculation import getRelativeError
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from math import sqrt

def read_xsection_measurement_results_with_errors(channel):
    global path_to_JSON, variable, k_value, met_type
    category = 'central'

    normalised_xsection_unfolded = read_data_from_JSON(path_to_JSON + '/xsection_measurement_results' + '/kv' + str(k_value) + '/' 
                                                       + category + '/normalised_xsection_' + channel + '_' + met_type + '.txt')
    
    normalised_xsection_measured_unfolded = {'measured':normalised_xsection_unfolded['TTJet_measured'],
                                            'unfolded':normalised_xsection_unfolded['TTJet_unfolded']}
    
    normalised_xsection_unfolded_with_errors = read_data_from_JSON(path_to_JSON + '/xsection_measurement_results' + '/kv' + 
                                                                str(k_value) + '/' + category + '/normalised_xsection_' + 
                                                                channel + '_' + met_type + '_with_errors.txt')
    normalised_xsection_ttbar_theory_errors = read_data_from_JSON(path_to_JSON + '/xsection_measurement_results' + '/kv' + 
                                                                str(k_value) + '/' + category + '/normalised_xsection_' + 
                                                                channel + '_' + met_type + '_ttbar_theory_errors.txt')
    normalised_xsection_MET_errors = read_data_from_JSON(path_to_JSON + '/xsection_measurement_results' + '/kv' + 
                                                                str(k_value) + '/' + category + '/normalised_xsection_' + 
                                                                channel + '_' + met_type + '_MET_errors.txt')
    normalised_xsection_PDF_errors = read_data_from_JSON(path_to_JSON + '/xsection_measurement_results' + '/kv' + 
                                                                str(k_value) + '/' + category + '/normalised_xsection_' + 
                                                                channel + '_' + met_type + '_PDF_errors.txt')
    normalised_xsection_other_errors = read_data_from_JSON(path_to_JSON + '/xsection_measurement_results' + '/kv' + 
                                                                str(k_value) + '/' + category + '/normalised_xsection_' + 
                                                                channel + '_' + met_type + '_other_errors.txt')
    
    normalised_xsection_measured_unfolded.update({'measured_with_systematics':normalised_xsection_unfolded_with_errors['TTJet_measured'],
                                                'unfolded_with_systematics':normalised_xsection_unfolded_with_errors['TTJet_unfolded']})
    
    normalised_xsection_measured_errors = normalised_xsection_ttbar_theory_errors['TTJet_measured']
    normalised_xsection_measured_errors.update(normalised_xsection_PDF_errors['TTJet_measured'])
    normalised_xsection_measured_errors.update(normalised_xsection_MET_errors['TTJet_measured'])
    normalised_xsection_measured_errors.update(normalised_xsection_other_errors['TTJet_measured'])

    normalised_xsection_unfolded_errors = normalised_xsection_ttbar_theory_errors['TTJet_unfolded']
    normalised_xsection_unfolded_errors.update(normalised_xsection_PDF_errors['TTJet_unfolded'])
    normalised_xsection_unfolded_errors.update(normalised_xsection_MET_errors['TTJet_unfolded'])
    normalised_xsection_unfolded_errors.update(normalised_xsection_other_errors['TTJet_unfolded'])
    
    return normalised_xsection_measured_unfolded, normalised_xsection_measured_errors, normalised_xsection_unfolded_errors

def print_xsections(xsections, channel, toFile = True, print_before_unfolding = False):
    global output_folder, variable, k_value, met_type, b_tag_bin
    printout = '=' * 60
    printout += '\n'
    printout += 'Results for %s variable, %s channel, k-value %s, met type %s, %s b-tag region\n' % (variable, channel, k_value, met_type, b_tag_bin)
    if print_before_unfolding:
        printout += 'BEFORE UNFOLDING\n'
    printout += '=' * 60
    printout += '\n'
    printout += '$%s$ bin & $\sigma_{meas}$' % variables_latex[variable]
    printout += '\\\\ \n\hline\n'
    scale = 100
    
    bins = variable_bins_ROOT[variable]
    assert(len(bins) == len(xsections['unfolded_with_systematics']))
    
    for bin_i, variable_bin in enumerate(bins):
        if print_before_unfolding:
            value, error_up, error_down = xsections['measured_with_systematics'][bin_i]
        else:
            value, error_up, error_down = xsections['unfolded_with_systematics'][bin_i]
        relativeError_up = getRelativeError(value, error_up)
        relativeError_down = getRelativeError(value, error_down)
        if error_up == error_down:
            printout += '%s & ' % variable_bins_latex[variable_bin] + ' $(%.2f \pm %.2f ) \cdot 10^{-2} ' % (value * scale, error_up * scale) +\
                    '(%.2f' % (relativeError_up * 100) + '\%)$'
        else:
            printout += '%s & ' % variable_bins_latex[variable_bin] + ' $(%.2f^{+%.2f}_{-%.2f)} \cdot 10^{-2} ' % (value * scale, error_up * scale, error_down * scale) +\
                    '(^{+%.2f}_{-%.2f}' % (relativeError_up * 100, relativeError_down * 100) + '\%)$'
        printout += '\\\\ \n'

    printout += '\hline \n\n'
    
    if toFile:
        path = output_folder + '/'  + str(measurement_config.centre_of_mass) + 'TeV/'  + variable
        make_folder_if_not_exists(path)
        if print_before_unfolding:
            output_file = open(path + '/normalised_xsection_result_' + channel + '_' + met_type + '_kv' + str(k_value) + '_measured.tex', 'w')
        else:
            output_file = open(path + '/normalised_xsection_result_' + channel + '_' + met_type + '_kv' + str(k_value) + '_unfolded.tex', 'w')
        output_file.write(printout)
        output_file.close()
    else:
        print printout

def print_error_table(central_values, errors, channel, toFile = True, print_before_unfolding = False):
    global output_folder, variable, k_value, met_type, b_tag_bin, all_measurements
    printout = '=' * 60
    printout += '\n'
    printout += 'Errors for %s variable, %s channel, k-value %s, met type %s, %s b-tag region\n' % (variable, channel, k_value, met_type, b_tag_bin)
    if print_before_unfolding:
        printout += 'BEFORE UNFOLDING\n'
    printout += '=' * 60
    printout += '\n\hline\n'
    
    header = 'Systematic'
    scale = 100
    rows = {}
    
    bins = variable_bins_ROOT[variable]
    assert(len(bins) == len(errors['central']))
    if print_before_unfolding:
        assert(len(bins) == len(central_values['measured']))
    else:
        assert(len(bins) == len(central_values['unfolded']))
    
    for bin_i, variable_bin in enumerate(bins):
        header += '& %s' % (variable_bins_latex[variable_bin])
        if print_before_unfolding:
            central_value = central_values['measured'][bin_i][0]
        else:
            central_value = central_values['unfolded'][bin_i][0]
        for source in all_measurements:
            abs_error = errors[source][bin_i]
            relative_error = getRelativeError(central_value, abs_error)
            text = '%.2f' % (relative_error*100)
            if rows.has_key(source):
                rows[source].append(text)
            elif 'PDF' in source:
                continue
            elif met_type in source:
                rows[source] = [met_systematics_latex[source.replace(met_type, '')], text]
            else:
                rows[source] = [measurements_latex[source], text]

    header += ' \\\\'
    printout += header
    printout += '\n\hline\n'
    
    for source in sorted(rows.keys()):
        if source == 'central':
            continue
        for item in rows[source]:
            printout += item + ' & '
        printout = printout.rstrip('& ')
        printout += '\\\\ \n'

    printout += '\hline \n\n'
    
    if toFile:
        path = output_folder + '/'  + str(measurement_config.centre_of_mass) + 'TeV/'  + variable
        make_folder_if_not_exists(path)
        if print_before_unfolding:
            output_file = open(path + '/error_table_' + channel + '_' + met_type + '_kv' + str(k_value) + '_measured.tex', 'w')
        else:
            output_file = open(path + '/error_table_' + channel + '_' + met_type + '_kv' + str(k_value) + '_unfolded.tex', 'w')
        output_file.write(printout)
        output_file.close()
    else:
        print printout

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data/',
                  help="set path to JSON files")
    parser.add_option("-o", "--output_folder", dest="output_folder", default='tables/',
                  help="set path to save plots")
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
    parser.add_option("-a", "--additional-tables", action="store_true", dest="additional_tables",
                      help="creates a set of tables for each systematic (in addition to central result).")

    (options, args) = parser.parse_args()
    if options.CoM == 8:
        from config.variable_binning_8TeV import variable_bins_latex, variable_bins_ROOT
        import config.cross_section_measurement_8TeV as measurement_config
    elif options.CoM == 7:
        from config.variable_binning_7TeV import variable_bins_latex, variable_bins_ROOT
        import config.cross_section_measurement_7TeV as measurement_config
    else:
        import sys
        sys.exit('Unknown centre of mass energy')

    variable = options.variable
    output_folder = options.output_folder
    if not output_folder.endswith('/'):
        output_folder += '/'
    k_value = options.k_value
    met_type = translate_options[options.metType]
    b_tag_bin = translate_options[options.bjetbin]
    path_to_JSON = options.path + '/' + str(measurement_config.centre_of_mass) + 'TeV/' + variable + '/'
    
    categories = deepcopy(measurement_config.categories_and_prefixes.keys())
    ttbar_generator_systematics = [ttbar_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    vjets_generator_systematics = [vjets_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    categories.extend(ttbar_generator_systematics)
    categories.extend(vjets_generator_systematics)
    
    pdf_uncertainties = ['PDFWeights_%d' % index for index in range(1, 45)]
    pdf_uncertainties_1_to_11 = ['PDFWeights_%d' % index for index in range(1, 12)]
    pdf_uncertainties_12_to_22 = ['PDFWeights_%d' % index for index in range(12, 23)]
    pdf_uncertainties_23_to_33 = ['PDFWeights_%d' % index for index in range(23, 34)]
    pdf_uncertainties_34_to_44 = ['PDFWeights_%d' % index for index in range(34, 45)]
    # all MET uncertainties except JES as this is already included
    met_uncertainties = [met_type + suffix for suffix in met_systematics_suffixes if not 'JetEn' in suffix and not 'JetRes' in suffix]
    all_measurements = deepcopy(categories)
    all_measurements.extend(pdf_uncertainties)
    all_measurements.extend(met_uncertainties)

    for channel in ['electron', 'muon', 'combined']:                        
        normalised_xsection_measured_unfolded, normalised_xsection_measured_errors, normalised_xsection_unfolded_errors = read_xsection_measurement_results_with_errors(channel)

        print_xsections(normalised_xsection_measured_unfolded, channel, toFile = True, print_before_unfolding = False)
        print_xsections(normalised_xsection_measured_unfolded, channel, toFile = True, print_before_unfolding = True)

        print_error_table(normalised_xsection_measured_unfolded, normalised_xsection_unfolded_errors, channel, toFile = True, print_before_unfolding = False)
        print_error_table(normalised_xsection_measured_unfolded, normalised_xsection_measured_errors, channel, toFile = True, print_before_unfolding = True)

    