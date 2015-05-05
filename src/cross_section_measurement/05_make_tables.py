from __future__ import division  # the result of the division will be always a float
from optparse import OptionParser
from copy import deepcopy
from config.latex_labels import variables_latex, measurements_latex, met_systematics_latex, samples_latex, typical_systematics_latex
from config.variable_binning import variable_bins_latex, variable_bins_ROOT
from config import XSectionConfig
from tools.Calculation import getRelativeError
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from lib import read_fit_results, read_fit_input
import math
import os.path
from numpy import median

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

    file_name = file_template.replace('.txt', '_topMass_errors.txt')
    normalised_xsection_topMass_errors = read_data_from_JSON( file_name )

    file_name = file_template.replace('.txt', '_kValue_errors.txt')
    normalised_xsection_kValue_errors = read_data_from_JSON( file_name )

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
    normalised_xsection_measured_errors.update(normalised_xsection_topMass_errors['TTJet_measured'])
    normalised_xsection_measured_errors.update(normalised_xsection_kValue_errors['TTJet_measured'])
    normalised_xsection_measured_errors.update(normalised_xsection_other_errors['TTJet_measured'])
    normalised_xsection_measured_errors.update(normalised_xsection_new_errors['TTJet_measured'])

    normalised_xsection_unfolded_errors = normalised_xsection_ttbar_generator_errors['TTJet_unfolded']
    normalised_xsection_unfolded_errors.update(normalised_xsection_PDF_errors['TTJet_unfolded'])
    normalised_xsection_unfolded_errors.update(normalised_xsection_MET_errors['TTJet_unfolded'])
    normalised_xsection_unfolded_errors.update(normalised_xsection_topMass_errors['TTJet_unfolded'])
    normalised_xsection_unfolded_errors.update(normalised_xsection_kValue_errors['TTJet_unfolded'])
    normalised_xsection_unfolded_errors.update(normalised_xsection_other_errors['TTJet_unfolded'])
    normalised_xsection_unfolded_errors.update(normalised_xsection_new_errors['TTJet_unfolded'])

    return normalised_xsection_measured_unfolded, normalised_xsection_measured_errors, normalised_xsection_unfolded_errors

def print_fit_results_table(initial_values, fit_results, channel, toFile = True):
    global output_folder, variable, met_type
    bins = variable_bins_ROOT[variable]

    printout = '%% ' + '=' * 60
    printout += '\n'
    printout += '%% Fit results for %s variable, %s channel, met type %s \n' % (variable, channel, met_type)
    printout += '%% ' + '=' * 60
    printout += '\n'

    printout += '\\begin{table}[htbp]\n'
    printout += '\\centering\n'
    printout += '\\caption{Fit results for the \\%s variable\n' % variable
    printout += 'at a centre-of-mass energy of %d TeV (%s channel).}\n' % ( measurement_config.centre_of_mass_energy, channel )
    printout += '\\label{tab:%s_fit_results_%dTeV_%s}\n' % (variable, measurement_config.centre_of_mass_energy, channel)
    printout += '\\resizebox{\\columnwidth}{!} {\n'
    printout += '\\begin{tabular}{l' + 'r'*len(bins) + 'r}\n'
    printout += '\\hline\n'

    header = 'Process'
    template_in = '%s in'
    ttjet_in_line = template_in % samples_latex['TTJet'] 
    singletop_in_line = template_in % samples_latex['SingleTop'] 
    vjets_in_line = template_in % samples_latex['V+Jets'] 
    qcd_in_line = template_in % samples_latex['QCD'] 

    template_fit = '%s fit'
    ttjet_fit_line = template_fit % samples_latex['TTJet'] 
    singletop_fit_line = template_fit % samples_latex['SingleTop'] 
    vjets_fit_line = template_fit % samples_latex['V+Jets'] 
    qcd_fit_line = template_fit % samples_latex['QCD'] 

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
    printout += '\\end{tabular}\n'
    printout += '}\n'
    printout += '\\end{table}\n'

    if toFile:
        path = output_folder + '/'  + str(measurement_config.centre_of_mass_energy) + 'TeV/'  + variable
        make_folder_if_not_exists(path)
        file_template = path + '/%s_fit_results_table_%dTeV_%s.tex' % (variable, measurement_config.centre_of_mass_energy, channel)
        output_file = open(file_template, 'w')
        output_file.write(printout)
        output_file.close()
    else:
        print printout

def print_xsections(xsections, channel, toFile = True, print_before_unfolding = False):
    global output_folder, variable, k_values, met_type, b_tag_bin
    printout = '%% ' + '=' * 60
    printout += '\n'
    printout += '%% Results for %s variable, %s channel, k-value %s, met type %s, %s b-tag region\n' % (variable, channel, str(k_values[channel]), met_type, b_tag_bin)
    if print_before_unfolding:
        printout += '%% BEFORE UNFOLDING\n'
    printout += '%% ' + '=' * 60
    printout += '\n'

    printout += '\\begin{table}[htbp]\n'
    printout += '\\setlength{\\tabcolsep}{2pt}\n'
    printout += '\\centering\n'
    printout += '\\caption{Normalised \\ttbar differential cross section measurements with respect to the \\%s variable\n' % variable
    printout += 'at a centre-of-mass energy of %d TeV ' % measurement_config.centre_of_mass_energy
    if channel == 'combined':
        printout += '(combination of electron and muon channels).'
    else:
        printout += '(%s channel).' % channel
    printout += ' The errors shown are combined statistical, fit and unfolding errors ($^\dagger$) and systematic uncertainty ($^\star$).}\n'
    printout += '\\label{tab:%s_xsections_%dTeV_%s}\n' % (variable, measurement_config.centre_of_mass_energy, channel)
    #printout += '\\resizebox{\\columnwidth}{!} {\n'
    printout += '\\begin{tabular}{lrrrr}\n'
    printout += '\\hline\n'
    printout += '$%s$ bin [\\GeV] & \\multicolumn{4}{c}{$\sigma_{meas} \\left(\\times 10^{3}\\right)$}' % variables_latex[variable]
    printout += '\\\\ \n\hline\n'
    scale = 1000
    
    bins = variable_bins_ROOT[variable]
    assert(len(bins) == len(xsections['unfolded_with_systematics']))
    
    for bin_i, variable_bin in enumerate(bins):
        if print_before_unfolding:
            value, stat_error = xsections['measured'][bin_i]
            _, total_error_up, total_error_down = xsections['measured_with_systematics'][bin_i]
        else:
            value, stat_error = xsections['unfolded'][bin_i]
            _, total_error_up, total_error_down = xsections['unfolded_with_systematics'][bin_i]
        # extracting the systematic error from the total in quadrature
        syst_error_up = math.sqrt(total_error_up**2 - stat_error**2)
        syst_error_down = math.sqrt(total_error_down**2 - stat_error**2)
        #relative errors for percentages
        total_relativeError_up = getRelativeError(value, total_error_up)
        total_relativeError_down = getRelativeError(value, total_error_down)
        if total_error_up == total_error_down:
            printout += '%s & ' % variable_bins_latex[variable_bin] + ' $%.2f$ & $ \pm~ %.2f^\\dagger$ & $ \pm~ %.2f^\\star$ & ' % (value * scale, stat_error * scale, syst_error_up * scale) +\
                    '$(%.2f' % (total_relativeError_up * 100) + '\%)$'
        else:
            printout += '%s & ' % variable_bins_latex[variable_bin] + ' $%.2f$ & $ \pm~ %.2f^\\dagger$ & $ ~^{+%.2f}_{-%.2f}^\\star$ & ' % (value * scale, stat_error * scale, syst_error_up * scale, syst_error_down * scale) +\
                    '$(^{+%.2f}_{-%.2f}' % (total_relativeError_up * 100, total_relativeError_down * 100) + '\%)$'
        printout += '\\\\ \n'

    printout += '\\hline \n'
    printout += '\\end{tabular}\n'
    #printout += '}\n' #for resizebox
    printout += '\\end{table}\n'
    
    if toFile:
        path = output_folder + '/'  + str(measurement_config.centre_of_mass_energy) + 'TeV/'  + variable
        make_folder_if_not_exists(path)
        file_template = path + '/%s_normalised_xsection_%dTeV_%s.tex' % (variable, measurement_config.centre_of_mass_energy, channel)

        if print_before_unfolding:
            make_folder_if_not_exists(path + '/before_unfolding/')
            file_template = file_template.replace(path, path + '/before_unfolding/')
        output_file = open(file_template, 'w')
        output_file.write(printout)
        output_file.close()
    else:
        print printout

def print_error_table(central_values, errors, channel, toFile = True, print_before_unfolding = False):
    global output_folder, variable, k_values, met_type, b_tag_bin, all_measurements
    bins = variable_bins_ROOT[variable]

    printout = '%% ' + '=' * 60
    printout += '\n'
    printout += '%% Systematics table for %s variable, %s channel, k-value %s, met type %s, %s b-tag region\n' % (variable, channel, str(k_values[channel]), met_type, b_tag_bin)
    if print_before_unfolding:
        printout += '%% BEFORE UNFOLDING\n'
    printout += '%% ' + '=' * 60
    printout += '\n'

    printout += '\\begin{table}[htbp]\n'
    printout += '\\centering\n'
    printout += '\\caption{Systematic uncertainties for the normalised \\ttbar cross section measurement with respect to \\%s variable\n' % variable
    printout += 'at a centre-of-mass energy of %d TeV ' % measurement_config.centre_of_mass_energy
    if channel == 'combined':
        printout += '(combination of electron and muon channels).}\n'
    else:
        printout += '(%s channel).}\n' % channel
    printout += '\\label{tab:%s_systematics_%dTeV_%s}\n' % (variable, measurement_config.centre_of_mass_energy, channel)
    if variable == 'MT':
        printout += '\\resizebox*{!}{\\textheight} {\n'
    else:
        printout += '\\resizebox{\\columnwidth}{!} {\n'
    printout += '\\begin{tabular}{l' + 'r'*len(bins) + '}\n'
    printout += '\\hline\n'
    
    header = 'Uncertainty source '
    rows = {}

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
            elif met_type in source:
                rows[source] = [met_systematics_latex[source.replace(met_type, '')] + ' (\%)', text]
            else:
                rows[source] = [measurements_latex[source] + ' (\%)', text]

    header += ' \\\\'
    printout += header
    printout += '\n\\hline\n'

    for source in sorted(rows.keys()):
        if source == 'central':
            continue
        for item in rows[source]:
            printout += item + ' & '
        printout = printout.rstrip('& ')
        printout += ' \\\\ \n'

    #append the total error to the table
    printout += '\\hline \n'
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
    printout += '\\hline \n'
    printout += '\\end{tabular}\n'
    printout += '}\n'
    printout += '\\end{table}\n'
    
    if toFile:
        path = output_folder + '/'  + str(measurement_config.centre_of_mass_energy) + 'TeV/'  + variable
        make_folder_if_not_exists(path)
        file_template = path + '/%s_systematics_%dTeV_%s.tex' % (variable, measurement_config.centre_of_mass_energy, channel)

        if print_before_unfolding:
            make_folder_if_not_exists(path + '/before_unfolding/')
            file_template = file_template.replace(path, path + '/before_unfolding/')
        output_file = open(file_template, 'w')
        output_file.write(printout)
        output_file.close()
    else:
        print printout
        
def print_typical_systematics_table(central_values, errors, channel, toFile = True, print_before_unfolding = False):
    global output_folder, variable, k_values, met_type, b_tag_bin, all_measurements
    bins = variable_bins_ROOT[variable]

    values_for_typical_systematics_table = {}
    
    assert(len(bins) == len(errors['central']))
    if print_before_unfolding:
        assert(len(bins) == len(central_values['measured']))
    else:
        assert(len(bins) == len(central_values['unfolded']))
    
    for bin_i, variable_bin in enumerate(bins):
        if print_before_unfolding:
            central_value = central_values['measured'][bin_i][0]
        else:
            central_value = central_values['unfolded'][bin_i][0]

        for systematic_group in typical_systematics.keys():
            for source in all_measurements:
                if source in typical_systematics[systematic_group]:
                    abs_error = errors[source][bin_i]
                    relative_error = getRelativeError(central_value, abs_error)
                    value = relative_error
                    if values_for_typical_systematics_table.has_key(source):
                        values_for_typical_systematics_table[source].append(value)
                    else:
                        values_for_typical_systematics_table[source] = [typical_systematics_latex[systematic_group] + ' (\%)', value]
    
    rows_for_typical_systematics_table = {}
    
    if variable == "HT":
        del(typical_systematics["typical_systematics_MET"])
    for systematic_group in typical_systematics.keys():
        typical_systematics_row = []
        typical_systematics_row.append(typical_systematics_latex[systematic_group] + ' (\%)')
        for bin_i, variable_bin in enumerate(bins):
            sum = 0.
            
            #if only one systematic in the group, in each bin just use the systematic value (absolute)
            if len(typical_systematics[systematic_group]) == 1:
                sum += abs(values_for_typical_systematics_table[typical_systematics[systematic_group][0]][bin_i+1])
            
            #if two systematics in the group, in each bin use the largest of the two absolute values
            elif len(typical_systematics[systematic_group]) == 2:
                low_syst = abs(values_for_typical_systematics_table[typical_systematics[systematic_group][0]][bin_i+1])
                high_syst = abs(values_for_typical_systematics_table[typical_systematics[systematic_group][1]][bin_i+1])
                sum += max(low_syst, high_syst)
            
            #if more than two systematics in the group, take the maximum of each pair of up/down systematics, and add these maximum values for all systematics in quadrature
            else:
                for systematic in typical_systematics [systematic_group]:
                    index_in_group = typical_systematics[systematic_group].index(systematic)
                    if index_in_group %2 == 1 : #if not 0th, 2nd, 4th etc. element of list, get out of loop
                        continue
                    else:
                        low_syst = abs(values_for_typical_systematics_table[typical_systematics[systematic_group][index_in_group]][bin_i+1])
                        high_syst = abs(values_for_typical_systematics_table[typical_systematics[systematic_group][index_in_group+1]][bin_i+1])
                        largest = max(low_syst, high_syst) #(values_for_typical_systematics_table[systematic][bin_i+1])
                        sum += pow(largest, 2)
                sum = math.sqrt(sum)

            typical_systematics_row.append(sum)
        label = typical_systematics_row.pop(0)
        
        #for each systematic group, take the median of the values across all bins 
        value = median(typical_systematics_row)
        text = '%.2f' % (value*100)
        rows_for_typical_systematics_table[systematic_group] = [label, text]

    printout = '%% ' + '=' * 60
    printout += '\n'
    printout += '%% Typical systematics table for %s channel, k-value %s, met type %s, %s b-tag region\n' % (channel, str(k_values[channel]), met_type, b_tag_bin)
    if print_before_unfolding:
        printout += '%% BEFORE UNFOLDING\n'
    printout += '%% ' + '=' * 60
    printout += '\n'

    printout += '\\begin{table}[htbp]\n'
    printout += '\\centering\n'
    printout += '\\caption{Typical systematic uncertainties (median values) for the normalised \\ttbar cross section measurement \n'
    printout += 'at a centre-of-mass energy of %d TeV ' % measurement_config.centre_of_mass_energy
    if channel == 'combined':
        printout += '(combination of electron and muon channels).}\n'
    else:
        printout += '(%s channel).}\n' % channel
    printout += '\\label{tab:typical_systematics_%dTeV_%s}\n' % (measurement_config.centre_of_mass_energy, channel)
    printout += '\\resizebox{\\columnwidth}{!} {\n'
    printout += '\\begin{tabular}{l' + 'r'*len(variable_bins_ROOT) + '}\n'
    printout += '\\hline\n'
    
    header = 'Uncertainty source '
    header += '& %s' % (variables_latex[variable])

    header += ' '
    printout += header
    printout += '\n\\hline\n'

    for systematic_group in sorted(rows_for_typical_systematics_table.keys()):
        if systematic_group == 'central':
            continue
        for item in rows_for_typical_systematics_table[systematic_group]:
            printout += item + ' & '
        printout = printout.rstrip('& ')
        printout += ' \n'

    printout += '\\hline \n'
    printout += '\\hline \n'
    printout += '\\end{tabular}\n'
    printout += '}\n'
    printout += '\\end{table}\n'

    if toFile:
        path = output_folder + '/'  + str(measurement_config.centre_of_mass_energy) + 'TeV/'
        make_folder_if_not_exists(path)
        file_template = path + '/typical_systematics_%dTeV_%s.tex' % (measurement_config.centre_of_mass_energy, channel)

        if print_before_unfolding:
            make_folder_if_not_exists(path + '/before_unfolding/')
            file_template = file_template.replace(path, path + '/before_unfolding/')
        if os.path.isfile(file_template): 
            with open(file_template, 'r+') as output_file:
                lines = output_file.readlines()
                for line_number, line in enumerate (lines):
                    if line.startswith("Uncertainty source"):
                        lines[line_number] = lines[line_number].strip() + "& " + variables_latex[variable] + "\n"
                    elif variable == "HT" and line.startswith("$E_{T}^{miss}$ uncertainties"):
                        lines[line_number] = lines[line_number].strip() + "& - \n"
                    else:
                        for table_entry in enumerate(typical_systematics_latex):
                            if line.startswith(typical_systematics_latex[table_entry[1]]):
                                lines[line_number] = lines[line_number].strip() + "& "  + rows_for_typical_systematics_table[table_entry[1]][1] + " \n"
                output_file.seek(0)
                for line in lines:
                    output_file.write(line)            
        else:
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
    typical_systematics = measurement_config.typical_systematics

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
    
    #remove btag mistagging rate systematic - new btagging method has only one, all-inclusive sytematic
    categories_and_prefixes = measurement_config.categories_and_prefixes
    del categories_and_prefixes['LightJet_down']
    del categories_and_prefixes['LightJet_up']

    categories = deepcopy(categories_and_prefixes.keys())
    ttbar_generator_systematics = [ttbar_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    vjets_generator_systematics = [vjets_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    categories.extend(ttbar_generator_systematics)
    categories.extend(vjets_generator_systematics)

    # Add mass systematics
    ttbar_mass_systematics = measurement_config.topMass_systematics
    categories.extend( measurement_config.topMass_systematics )

    # Add k value systematic - commented out for now because we have decided to remove the k value systematic from the error tables.
    #kValue_systematics = measurement_config.kValueSystematic
    #categories.extend( measurement_config.kValueSystematic )

    # all MET uncertainties except JES as this is already included, and only if variable is not HT, since MET is not used in HT
    if not variable == "HT":
        met_uncertainties = [met_type + suffix for suffix in met_systematics_suffixes if not 'JetEn' in suffix and not 'JetRes' in suffix]
    
    new_uncertainties = ['hadronisation', 'ptreweight_max', 'QCD_shape', 'PDF_total_lower', 'PDF_total_upper']
    rate_changing_systematics = [systematic + '+' for systematic in measurement_config.rate_changing_systematics.keys()]
    rate_changing_systematics.extend([systematic + '-' for systematic in measurement_config.rate_changing_systematics.keys()])
    all_measurements = deepcopy(categories)
    if not variable == "HT":
        all_measurements.extend(met_uncertainties)
    all_measurements.extend(new_uncertainties)
    all_measurements.extend(rate_changing_systematics)

    for channel in ['electron', 'muon', 'combined']:                        
        normalised_xsection_measured_unfolded, normalised_xsection_measured_errors, normalised_xsection_unfolded_errors = read_xsection_measurement_results_with_errors(channel)

        print_xsections(normalised_xsection_measured_unfolded, channel, toFile = True, print_before_unfolding = False)
        print_xsections(normalised_xsection_measured_unfolded, channel, toFile = True, print_before_unfolding = True)

        print_error_table(normalised_xsection_measured_unfolded, normalised_xsection_unfolded_errors, channel, toFile = True, print_before_unfolding = False)
        print_error_table(normalised_xsection_measured_unfolded, normalised_xsection_measured_errors, channel, toFile = True, print_before_unfolding = True)

        if channel == 'combined':
            print_typical_systematics_table(normalised_xsection_measured_unfolded, normalised_xsection_unfolded_errors, channel, toFile = True, print_before_unfolding = False)
#             print_typical_systematics_table(normalised_xsection_measured_unfolded, normalised_xsection_measured_errors, channel, toFile = True, print_before_unfolding = True)

        if not channel == 'combined':
            fit_input = read_fit_input(path_to_JSON, variable, 'central', channel, met_type)
            fit_results = read_fit_results(path_to_JSON, variable, 'central', channel, met_type)
            print_fit_results_table(fit_input, fit_results, channel, toFile = True)

    
