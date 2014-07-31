from __future__ import division  # the result of the division will be always a float
from optparse import OptionParser
from copy import deepcopy
from config.latex_labels import variables_latex, measurements_latex, met_systematics_latex, samples_latex
from config.variable_binning import variable_bins_latex, variable_bins_ROOT
from config import XSectionConfig
from tools.Calculation import getRelativeError
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from lib import read_fit_results, read_fit_input

def read_xsection_measurement_results_with_errors(channel):
    global path_to_JSON, variable, k_values, met_type
    category = 'central'

    file_template = path_to_JSON + '/' + variable +  '/xsection_measurement_results/' + channel + '/kv' + str(k_values[channel]) + '/' + category + '/normalised_xsection_' + met_type + '.txt' 
    if channel == 'combined':
        file_template = file_template.replace('kv' + str(k_values[channel]), '')

    file_name = file_template
    normalised_xsection_unfolded = read_data_from_JSON( file_name )
    
    normalised_xsection_measured_unfolded = {'measured':normalised_xsection_unfolded['TTJet_measured'],
                                            'unfolded':normalised_xsection_unfolded['TTJet_unfolded']}
    
    file_name = file_template.replace('.txt', '_with_errors.txt')
    normalised_xsection_unfolded_with_errors = read_data_from_JSON( file_name )

    file_name = file_template.replace('.txt', '_ttbar_generator_errors.txt')
    normalised_xsection_ttbar_generator_errors = read_data_from_JSON( file_name )

    file_name = file_template.replace('.txt', '_MET_errors.txt')
    normalised_xsection_MET_errors = read_data_from_JSON( file_name )

    file_name = file_template.replace('.txt', '_PDF_errors.txt')
    normalised_xsection_PDF_errors = read_data_from_JSON( file_name )

    file_name = file_template.replace('.txt', '_other_errors.txt')
    normalised_xsection_other_errors = read_data_from_JSON( file_name )

    file_name = file_template.replace('.txt', '_new_errors.txt')
    normalised_xsection_new_errors = read_data_from_JSON( file_name )
    
    normalised_xsection_measured_unfolded.update({'measured_with_systematics':normalised_xsection_unfolded_with_errors['TTJet_measured'],
                                                'unfolded_with_systematics':normalised_xsection_unfolded_with_errors['TTJet_unfolded']})
    
    normalised_xsection_measured_errors = normalised_xsection_ttbar_generator_errors['TTJet_measured']
    normalised_xsection_measured_errors.update(normalised_xsection_PDF_errors['TTJet_measured'])
    normalised_xsection_measured_errors.update(normalised_xsection_MET_errors['TTJet_measured'])
    normalised_xsection_measured_errors.update(normalised_xsection_other_errors['TTJet_measured'])
    normalised_xsection_measured_errors.update(normalised_xsection_new_errors['TTJet_measured'])

    normalised_xsection_unfolded_errors = normalised_xsection_ttbar_generator_errors['TTJet_unfolded']
    normalised_xsection_unfolded_errors.update(normalised_xsection_PDF_errors['TTJet_unfolded'])
    normalised_xsection_unfolded_errors.update(normalised_xsection_MET_errors['TTJet_unfolded'])
    normalised_xsection_unfolded_errors.update(normalised_xsection_other_errors['TTJet_unfolded'])
    normalised_xsection_unfolded_errors.update(normalised_xsection_new_errors['TTJet_unfolded'])
    
    return normalised_xsection_measured_unfolded, normalised_xsection_measured_errors, normalised_xsection_unfolded_errors

# def read_fit_results(channel):
#     global path_to_JSON, variable, met_type
#     category = 'central'
#     fit_results = read_data_from_JSON(path_to_JSON + '/fit_results/' + category + '/fit_results_' + channel + '_' + met_type + '.txt')
#     return fit_results
# 
# def read_initial_values(channel):
#     global path_to_JSON, variable, met_type
#     category = 'central'
#     initial_values = read_data_from_JSON(path_to_JSON + '/fit_results/' + category + '/initial_values_' + channel + '_' + met_type + '.txt')
#     return initial_values

def print_fit_results_table(initial_values, fit_results, channel, toFile = True):
    global output_folder, variable, met_type
    printout = '=' * 60
    printout += '\n'
    printout += 'Results for %s variable, %s channel, met type %s\n' % (variables_latex[variable], channel, met_type)
    printout += '=' * 60
    printout += '\n'
    printout += '\\\\ \n\hline\n'
    header = 'Process'
    template_in = '%s in'
    ttjet_in_line = template_in % samples_latex['TTJet'] 
    singletop_in_line = template_in % samples_latex['SingleTop'] 
    vjets_in_line = template_in % samples_latex['V+Jets'] 
    qcd_in_line = template_in % samples_latex['QCD'] 

    template_fit = '%s fit'
    ttjet_fit_line = template_in % samples_latex['TTJet'] 
    singletop_fit_line = template_in % samples_latex['SingleTop'] 
    vjets_fit_line = template_in % samples_latex['V+Jets'] 
    qcd_fit_line = template_in % samples_latex['QCD'] 

    sum_MC_in_line = 'Sum MC in'
    sum_MC_fit_line = 'Sum MC fit'
    sum_data_line = 'Data'

    N_initial_ttjet = 0
    N_initial_singletop = 0
    N_initial_vjets = 0
    N_initial_qcd = 0
    N_initial_sum_MC = 0
    N_initial_ttjet_error = 0
    N_initial_singletop_error = 0
    N_initial_vjets_error = 0
    N_initial_qcd_error = 0
    N_initial_sum_MC_error = 0
    N_data = 0
    N_data_error = 0

    N_fit_ttjet = 0
    N_fit_singletop = 0
    N_fit_vjets = 0
    N_fit_qcd = 0
    N_fit_sum_MC = 0
    N_fit_ttjet_error = 0
    N_fit_singletop_error = 0
    N_fit_vjets_error = 0
    N_fit_qcd_error = 0
    N_fit_sum_MC_error = 0

    bins = variable_bins_ROOT[variable]
    for bin_i, variable_bin in enumerate(bins):
        header += ' & %s' % (variable_bins_latex[variable_bin])
        ttjet_in_line += ' & %.1f $\pm$ %.1f' % (initial_values['TTJet'][bin_i][0], initial_values['TTJet'][bin_i][1])
        N_initial_ttjet += initial_values['TTJet'][bin_i][0]
        N_initial_ttjet_error += initial_values['TTJet'][bin_i][1]
        
        singletop_in_line += ' & %.1f $\pm$ %.1f' % (initial_values['SingleTop'][bin_i][0], initial_values['SingleTop'][bin_i][1])
        N_initial_singletop += initial_values['SingleTop'][bin_i][0]
        N_initial_singletop_error += initial_values['SingleTop'][bin_i][1]

        vjets_in_line += ' & %.1f $\pm$ %.1f' % (initial_values['V+Jets'][bin_i][0], initial_values['V+Jets'][bin_i][1])
        N_initial_vjets += initial_values['V+Jets'][bin_i][0]
        N_initial_vjets_error += initial_values['V+Jets'][bin_i][1]

        qcd_in_line += ' & %.1f $\pm$ %.1f' % (initial_values['QCD'][bin_i][0], initial_values['QCD'][bin_i][1])
        N_initial_qcd += initial_values['QCD'][bin_i][0]
        N_initial_qcd_error += initial_values['QCD'][bin_i][1]

        sumMCin = initial_values['TTJet'][bin_i][0] + initial_values['SingleTop'][bin_i][0] + initial_values['V+Jets'][bin_i][0] + initial_values['QCD'][bin_i][0]
        sumMCinerror = initial_values['TTJet'][bin_i][1] + initial_values['SingleTop'][bin_i][1] + initial_values['V+Jets'][bin_i][1] + initial_values['QCD'][bin_i][1]

        sum_MC_in_line += ' & %.1f $\pm$ %.1f' % (sumMCin, sumMCinerror)
        N_initial_sum_MC += sumMCin
        N_initial_sum_MC_error += sumMCinerror

        ttjet_fit_line += ' & %.1f $\pm$ %.1f' % (fit_results['TTJet'][bin_i][0], fit_results['TTJet'][bin_i][1])
        N_fit_ttjet += fit_results['TTJet'][bin_i][0]
        N_fit_ttjet_error += fit_results['TTJet'][bin_i][1]
        
        singletop_fit_line += ' & %.1f $\pm$ %.1f' % (fit_results['SingleTop'][bin_i][0], fit_results['SingleTop'][bin_i][1])
        N_fit_singletop += fit_results['SingleTop'][bin_i][0]
        N_fit_singletop_error += fit_results['SingleTop'][bin_i][1]

        vjets_fit_line += ' & %.1f $\pm$ %.1f' % (fit_results['V+Jets'][bin_i][0], fit_results['V+Jets'][bin_i][1])
        N_fit_vjets += fit_results['V+Jets'][bin_i][0]
        N_fit_vjets_error += fit_results['V+Jets'][bin_i][1]

        qcd_fit_line += ' & %.1f $\pm$ %.1f' % (fit_results['QCD'][bin_i][0], fit_results['QCD'][bin_i][1])
        N_fit_qcd += fit_results['QCD'][bin_i][0]
        N_fit_qcd_error += fit_results['QCD'][bin_i][1]
        
        sumMCfit = fit_results['TTJet'][bin_i][0] + fit_results['SingleTop'][bin_i][0] + fit_results['V+Jets'][bin_i][0] + fit_results['QCD'][bin_i][0]
        sumMCfiterror = fit_results['TTJet'][bin_i][1] + fit_results['SingleTop'][bin_i][1] + fit_results['V+Jets'][bin_i][1] + fit_results['QCD'][bin_i][1]

        sum_MC_fit_line += ' & %.1f $\pm$ %.1f' % (sumMCfit, sumMCfiterror)
        N_fit_sum_MC += sumMCfit
        N_fit_sum_MC_error += sumMCfiterror

        sum_data_line += ' & %.1f $\pm$ %.1f' % (initial_values['data'][bin_i][0], initial_values['data'][bin_i][1])
        N_data += initial_values['data'][bin_i][0]
        N_data_error += initial_values['data'][bin_i][1]

    header += '& Total \\\\'
    ttjet_in_line += ' & %.1f $\pm$ %.1f \\\\' % (N_initial_ttjet, N_initial_ttjet_error)
    singletop_in_line += ' & %.1f $\pm$ %.1f \\\\' % (N_initial_singletop, N_initial_singletop_error)
    vjets_in_line += ' & %.1f $\pm$ %.1f \\\\' % (N_initial_vjets, N_initial_vjets_error)
    qcd_in_line += ' & %.1f $\pm$ %.1f \\\\' % (N_initial_qcd, N_initial_qcd_error)
    sum_MC_in_line += '& %.1f $\pm$ %.1f \\\\' % (N_initial_sum_MC, N_initial_sum_MC_error)
    ttjet_fit_line += ' & %.1f $\pm$ %.1f \\\\' % (N_fit_ttjet, N_fit_ttjet_error)
    singletop_fit_line += ' & %.1f $\pm$ %.1f \\\\' % (N_fit_singletop, N_fit_singletop_error)
    vjets_fit_line += ' & %.1f $\pm$ %.1f \\\\' % (N_fit_vjets, N_fit_vjets_error)
    qcd_fit_line += ' & %.1f $\pm$ %.1f \\\\' % (N_fit_qcd, N_fit_qcd_error)
    sum_MC_fit_line += ' & %.1f $\pm$ %.1f \\\\' % (N_fit_sum_MC, N_fit_sum_MC_error)
    sum_data_line += ' & %.1f $\pm$ %.1f \\\\' % (N_data, N_data_error)

    printout += header
    printout += '\n\hline\n'
    printout += ttjet_in_line
    printout += '\n'
    printout += ttjet_fit_line
    printout += '\n\hline\n'
    printout += singletop_in_line
    printout += '\n'
    printout += singletop_fit_line
    printout += '\n\hline\n'
    printout += vjets_in_line
    printout += '\n'
    printout += vjets_fit_line
    printout += '\n\hline\n'
    printout += qcd_in_line
    printout += '\n'
    printout += qcd_fit_line
    printout += '\n\hline\n'
    printout += sum_MC_in_line
    printout += '\n'
    printout += sum_MC_fit_line
    printout += '\n\hline\n'
    printout += sum_data_line
    printout += '\n\hline\n'
    printout += '\hline\n'

    if toFile:
        path = output_folder + '/'  + str(measurement_config.centre_of_mass_energy) + 'TeV/'  + variable
        make_folder_if_not_exists(path)
        output_file = open(path + '/fit_results_table_' + channel + '_' + met_type + '.tex', 'w')
        output_file.write(printout)
        output_file.close()
    else:
        print printout

def print_xsections(xsections, channel, toFile = True, print_before_unfolding = False):
    global output_folder, variable, k_values, met_type, b_tag_bin
    printout = '=' * 60
    printout += '\n'
    printout += 'Results for %s variable, %s channel, k-value %s, met type %s, %s b-tag region\n' % (variable, channel, str(k_values[channel]), met_type, b_tag_bin)
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
        path = output_folder + '/'  + str(measurement_config.centre_of_mass_energy) + 'TeV/'  + variable
        make_folder_if_not_exists(path)
        if channel == 'combined':
            file_template = path + '/normalised_xsection_result_' + channel + '_' + met_type
        else:
            file_template = path + '/normalised_xsection_result_' + channel + '_' + met_type + '_kv' + str(k_values[channel])

        if print_before_unfolding:
            file_template += '_measured.tex'
        else:
            file_template += '_unfolded.tex'
        output_file = open(file_template, 'w')
        output_file.write(printout)
        output_file.close()
    else:
        print printout

def print_error_table(central_values, errors, channel, toFile = True, print_before_unfolding = False):
    global output_folder, variable, k_values, met_type, b_tag_bin, all_measurements
    printout = '=' * 60
    printout += '\n'
    printout += 'Errors for %s variable, %s channel, k-value %s, met type %s, %s b-tag region\n' % (variable, channel, str(k_values[channel]), met_type, b_tag_bin)
    if print_before_unfolding:
        printout += 'BEFORE UNFOLDING\n'
    printout += '=' * 60
    printout += '\n\hline\n'
    
    header = 'Systematic'
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
                rows[source] = [met_systematics_latex[source.replace(met_type, '')] + ' (\%)', text]
            else:
                rows[source] = [measurements_latex[source] + ' (\%)', text]


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

    #append the total error to the table
    printout += '\hline \n'
    total_line = 'Total (\%)'
    for bin_i, variable_bin in enumerate(bins):
        if print_before_unfolding:
            value, error_up, error_down = central_values['measured_with_systematics'][bin_i]
        else:
            value, error_up, error_down = central_values['unfolded_with_systematics'][bin_i]
        error = max(error_up, error_down)
        relativeError = getRelativeError(value, error)
        total_line += ' & %.2f ' % (relativeError * 100)
    printout += total_line + '\\\\ \n'
    printout += '\hline \n\n'
    
    if toFile:
        path = output_folder + '/'  + str(measurement_config.centre_of_mass_energy) + 'TeV/'  + variable
        make_folder_if_not_exists(path)
        if channel == 'combined':
            file_template = path + '/error_table_' + channel + '_' + met_type
        else:
            file_template = path + '/error_table_' + channel + '_' + met_type + '_kv' + str(k_values[channel])

        if print_before_unfolding:
            file_template += '_measured.tex'
        else:
            file_template += '_unfolded.tex'
        output_file = open(file_template, 'w')
        output_file.write(printout)
        output_file.close()
    else:
        print printout

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data/',
                  help="set path to JSON files")
    parser.add_option("-o", "--output_folder", dest="output_folder", default='tables/',
                  help="set path to save tables")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                  help="set variable to plot (MET, HT, ST, MT, WPT)")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type used in the analysis of MET-dependent variables")
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                  help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=8, type=int,
                      help="set the centre of mass energy for analysis. Default = 8 [TeV]")
    parser.add_option("-a", "--additional-tables", action="store_true", dest="additional_tables",
                      help="creates a set of tables for each systematic (in addition to central result).")

    (options, args) = parser.parse_args()
    measurement_config = XSectionConfig(options.CoM)
    # caching of variables for shorter access
    translate_options = measurement_config.translate_options
    ttbar_theory_systematic_prefix = measurement_config.ttbar_theory_systematic_prefix
    vjets_theory_systematic_prefix = measurement_config.vjets_theory_systematic_prefix
    met_systematics_suffixes = measurement_config.met_systematics_suffixes

    variable = options.variable
    output_folder = options.output_folder
    if not output_folder.endswith('/'):
        output_folder += '/'
    k_values = {'electron' : measurement_config.k_values_electron[variable],
                'muon' : measurement_config.k_values_muon[variable],
                'combined' : 'None'
                }
    met_type = translate_options[options.metType]
    b_tag_bin = translate_options[options.bjetbin]
    path_to_JSON = options.path + '/' + str(measurement_config.centre_of_mass_energy) + 'TeV/'
    
    categories = deepcopy(measurement_config.categories_and_prefixes.keys())
    ttbar_generator_systematics = [ttbar_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    vjets_generator_systematics = [vjets_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    categories.extend(ttbar_generator_systematics)
    categories.extend(vjets_generator_systematics)
    
    pdf_uncertainties = ['PDFWeights_%d' % index for index in range(1, 46)]
    pdf_uncertainties_1_to_11 = ['PDFWeights_%d' % index for index in range(1, 12)]
    pdf_uncertainties_12_to_22 = ['PDFWeights_%d' % index for index in range(12, 23)]
    pdf_uncertainties_23_to_33 = ['PDFWeights_%d' % index for index in range(23, 34)]
    pdf_uncertainties_34_to_45 = ['PDFWeights_%d' % index for index in range(34, 46)]
    # all MET uncertainties except JES as this is already included
    met_uncertainties = [met_type + suffix for suffix in met_systematics_suffixes if not 'JetEn' in suffix and not 'JetRes' in suffix]
    new_uncertainties = ['hadronisation', 'QCD_shape']
    rate_changing_systematics = [systematic + '+' for systematic in measurement_config.rate_changing_systematics.keys()]
    rate_changing_systematics.extend([systematic + '-' for systematic in measurement_config.rate_changing_systematics.keys()])
    all_measurements = deepcopy(categories)
    all_measurements.extend(pdf_uncertainties)
    all_measurements.extend(met_uncertainties)
    all_measurements.extend(new_uncertainties)
    all_measurements.extend(rate_changing_systematics)

    for channel in ['electron', 'muon', 'combined']:                        
        normalised_xsection_measured_unfolded, normalised_xsection_measured_errors, normalised_xsection_unfolded_errors = read_xsection_measurement_results_with_errors(channel)

        print_xsections(normalised_xsection_measured_unfolded, channel, toFile = True, print_before_unfolding = False)
        print_xsections(normalised_xsection_measured_unfolded, channel, toFile = True, print_before_unfolding = True)

        print_error_table(normalised_xsection_measured_unfolded, normalised_xsection_unfolded_errors, channel, toFile = True, print_before_unfolding = False)
        print_error_table(normalised_xsection_measured_unfolded, normalised_xsection_measured_errors, channel, toFile = True, print_before_unfolding = True)

        if not channel == 'combined':
            fit_input = read_fit_input(path_to_JSON, variable, 'central', channel, met_type)
            fit_results = read_fit_results(path_to_JSON, variable, 'central', channel, met_type)
            print_fit_results_table(fit_input, fit_results, channel, toFile = True)

    