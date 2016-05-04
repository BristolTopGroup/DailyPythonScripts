from __future__ import division  # the result of the division will be always a float
from optparse import OptionParser
from copy import deepcopy
from config.latex_labels import variables_latex, variables_NonLatex, measurements_latex, samples_latex, typical_systematics_latex, met_systematics_latex
from config.variable_binning import variable_bins_latex, variable_bins_ROOT, variable_bins_visiblePS_ROOT, variable_bins_visiblePS_latex, bin_edges_vis, bin_edges_full
from config import XSectionConfig
from tools.Calculation import getRelativeError
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists, read_xsection_measurement_results_with_errors
from tools.hist_utilities import values_and_errors_to_hist
from lib import read_normalisation, read_initial_normalisation
import math
import os.path
from numpy import median
import matplotlib as mpl
mpl.use( 'agg' )
import matplotlib.pyplot as plt
import rootpy.plotting.root2matplotlib as rplt
from config import CMS
import matplotlib.cm as cm
# use full stpectrum, yet use white for less than vmin=1 events
my_cmap = cm.get_cmap( 'jet' )
my_cmap.set_under( 'w' )
from matplotlib import rc
rc( 'font', **CMS.font )
rc( 'text', usetex = False )

def print_fit_results_table(initial_values, fit_results, channel, toFile = True):
    global output_folder, variable, met_type, phase_space
    bins = None
    bins_latex = None
    if phase_space == 'VisiblePS':
        bins = variable_bins_visiblePS_ROOT[variable]
        bins_latex = variable_bins_visiblePS_latex[variable]
    elif phase_space == 'FullPS':
        bins = variable_bins_ROOT[variable]
        bins_latex = variable_bins_latex[variable]

    printout = '%% ' + '=' * 60
    printout += '\n'
    printout += '%% Fit results for %s variable, %s channel, met type %s \n' % (variable, channel, met_type)
    printout += '%% ' + '=' * 60
    printout += '\n'

    printout += '\\begin{table}[htbp]\n'
    printout += '\\centering\n'
    printout += '\\caption{Fit results for the %s variable\n' % variables_latex[variable]
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
        header += ' & %s' % (bins_latex[variable_bin])
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
        path = output_folder + '/'  + variable
        make_folder_if_not_exists(path)
        file_template = path + '/%s_fit_results_table_%dTeV_%s.tex' % (variable, measurement_config.centre_of_mass_energy, channel)
        output_file = open(file_template, 'w')
        output_file.write(printout)
        output_file.close()
    else:
        print printout

def print_xsections(xsections, channel, toFile = True, print_before_unfolding = False):
    global output_folder, variable, met_type, b_tag_bin, phase_space
    printout = '%% ' + '=' * 60
    printout += '\n'
    printout += '%% Results for %s variable, %s channel, met type %s, %s b-tag region\n' % (variable, channel, met_type, b_tag_bin)
    if print_before_unfolding:
        printout += '%% BEFORE UNFOLDING\n'
    printout += '%% ' + '=' * 60
    printout += '\n'

    printout += '\\begin{table}[htbp]\n'
    printout += '\\setlength{\\tabcolsep}{2pt}\n'
    printout += '\\centering\n'
    printout += '\\caption{Normalised \\ttbar cross section measurement with respect to %s variable\n' % variables_latex[variable]
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
    
    bins = None
    bins_latex = None
    if phase_space == 'VisiblePS':
        bins = variable_bins_visiblePS_ROOT[variable]
        bins_latex = variable_bins_visiblePS_latex[variable]
    elif phase_space == 'FullPS':
        bins = variable_bins_ROOT[variable]
        bins_latex = variable_bins_latex[variable]

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
            printout += '%s & ' % bins_latex[variable_bin] + ' $%.2f$ & $ \pm~ %.2f^\\dagger$ & $ \pm~ %.2f^\\star$ & ' % (value * scale, stat_error * scale, syst_error_up * scale) +\
                    '$(%.2f' % (total_relativeError_up * 100) + '\%)$'
        else:
            printout += '%s & ' % bins_latex[variable_bin] + ' $%.2f$ & $ \pm~ %.2f^\\dagger$ & $ ~^{+%.2f}_{-%.2f}^\\star$ & ' % (value * scale, stat_error * scale, syst_error_up * scale, syst_error_down * scale) +\
                    '$(^{+%.2f}_{-%.2f}' % (total_relativeError_up * 100, total_relativeError_down * 100) + '\%)$'
        printout += '\\\\ \n'

    printout += '\\hline \n'
    printout += '\\end{tabular}\n'
    #printout += '}\n' #for resizebox
    printout += '\\end{table}\n'
    
    if toFile:
        path = output_folder + '/' + variable
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

def make_error_plot( errorHists, bins ):
    global output_folder, variable
    # For each up/down source, reduce to one set of numbers
    symmetricErrorHists = {}
    for source, hist in errorHists.iteritems():
        if ( variable == 'HT' or variable == 'NJets' or variable == 'lepton_pt' or variable == 'abs_lepton_eta'  ) and source in measurement_config.met_systematics and not 'JES' in source and not 'JER' in source:
            continue

        if 'down' in source or '-' in source or 'lower' in source or 'Down' in source:
            # Find up version
            upHist = None
            newSource = ''
            if 'down' in source:
                upHist = errorHists[source.replace('down','up')]
                newSource = source.replace('down','')
            elif 'Down' in source:
                upHist = errorHists[source.replace('Down','Up')]
                newSource = source.replace('Down','')
            elif '-' in source:
                upHist = errorHists[source.replace('-','+')]
                newSource = source.replace('-','')
            elif 'lower' in source:
                upHist = errorHists[source.replace('lower','upper')]
                newSource = source.replace('lower','')

            if newSource[-1] == '_':
                newSource = newSource[:-1]
            # if '_' in newSource:
            #     newSource = newSource.replace('_','')

            symmetricErrorHists[newSource] = []
            for errorup, errordown in zip(hist, upHist):
                newError = max( abs(errorup), abs(errordown) )
                symmetricErrorHists[newSource].append(newError)
        elif 'TTJets_hadronisation' in source or 'QCD_shape' in source or 'TTJets_NLOgenerator' in source:        
            symmetricErrorHists[source] = [ abs(i) for i in hist ]

    x_limits = [bins[0], bins[-1]]
    y_limits = [0,0.6]
    plt.figure( figsize = ( 20, 16 ), dpi = 200, facecolor = 'white' )

    ax0 = plt.axes()
    ax0.minorticks_on()
    ax0.xaxis.labelpad = 12
    ax0.yaxis.labelpad = 12
    ax0.set_xlim( x_limits )
    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )


    statisticalErrorHists = values_and_errors_to_hist( errorHists['statistical'], [], bins )
    for source, hist in symmetricErrorHists.iteritems():
        symmetricErrorHists[source] = values_and_errors_to_hist( hist, [], bins )

    colours = ['silver', 'r', 'tan', 'chartreuse', 'cadetblue', 'dodgerblue', 'pink', 'hotpink', 'coral', 'forestgreen', 'cyan', 'teal', 'crimson', 'darkmagenta', 'olive', 'slateblue', 'deepskyblue', 'orange', 'r' ]
    for source, colour in zip( symmetricErrorHists.keys(), colours):
        hist = symmetricErrorHists[source]
        hist.linewidth = 4
        hist.color = colour
        rplt.hist( hist, stacked=False, axes = ax0, cmap = my_cmap, vmin = 1, label = source )

    statisticalErrorHists.linewidth = 4
    statisticalErrorHists.color = 'black'
    statisticalErrorHists.linestyle = 'dashed'
    rplt.hist( statisticalErrorHists, stacked=False, axes = ax0, cmap = my_cmap, vmin = 1, label = 'stat.' )

    ax0.set_ylim( y_limits )
    leg = plt.legend(loc=1,prop={'size':40},ncol=2)
    leg.draw_frame(False)
    x_title = variables_NonLatex[variable]
    if variable in ['HT', 'MET', 'WPT', 'ST', 'lepton_pt']:
        x_title += ' [GeV]'
    plt.xlabel( x_title, CMS.x_axis_title )
    plt.ylabel( 'Relative Uncertainty', CMS.y_axis_title)
    plt.tight_layout()

    path = output_folder + '/'  + variable + '/'
    make_folder_if_not_exists(path)
    file_template = path + '/%s_systematics_%dTeV_%s.pdf' % (variable, measurement_config.centre_of_mass_energy, channel)
    plt.savefig(file_template)
    pass

def print_error_table(central_values, errors, channel, toFile = True, print_before_unfolding = False):
    global output_folder, variable, met_type, b_tag_bin, all_measurements, phase_space
    bins = None
    bins_latex = None
    binEdges = None
    variable_latex = variables_latex[variable]
    if phase_space == 'VisiblePS':
        bins = variable_bins_visiblePS_ROOT[variable]
        bins_latex = variable_bins_visiblePS_latex[variable]
        binEdges = bin_edges_vis[variable]
    elif phase_space == 'FullPS':
        bins = variable_bins_ROOT[variable]
        bins_latex = variable_bins_latex[variable]
        binEdges = bin_edges_full[variable]
    printout = '%% ' + '=' * 60
    printout += '\n'
    printout += '%% Systematics table for %s variable, %s channel, met type %s, %s b-tag region\n' % (variable, channel, met_type, b_tag_bin)
    if print_before_unfolding:
        printout += '%% BEFORE UNFOLDING\n'
    printout += '%% ' + '=' * 60
    printout += '\n'

    printout += '\\begin{table}[htbp]\n'
    printout += '\\centering\n'
    printout += '\\caption{Systematic uncertainties for the normalised \\ttbar cross section measurement with respect to %s variable\n' % variable_latex
    printout += 'at a centre-of-mass energy of %d TeV ' % measurement_config.centre_of_mass_energy
    if channel == 'combined' or channel == "combinedBeforeUnfolding":
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
    
    errorHists = {}
    errorHists['statistical'] = []
    for source in all_measurements:
        errorHists[source] = []

    for bin_i, variable_bin in enumerate(bins):
        header += '& %s' % (bins_latex[variable_bin])
        if print_before_unfolding:
            central_value = central_values['measured'][bin_i][0]
        else:
            central_value = central_values['unfolded'][bin_i][0]

        for source in all_measurements:
            if ( variable == 'HT' or variable == 'NJets' or variable == 'lepton_pt' or variable == 'abs_lepton_eta'  ) and source in measurement_config.met_systematics and not 'JES' in source and not 'JER' in source:
                continue

            abs_error = errors[source][bin_i]
            relative_error = getRelativeError(central_value, abs_error)

            errorHists[source].append(relative_error)

            text = '%.2f' % (relative_error*100)
            if rows.has_key(source):
                rows[source].append(text)
            elif met_type in source:
                rows[source] = [measurements_latex[source.replace(met_type, '')] + ' (\%)', text]
            else:
                if source in met_systematics_latex.keys():
                    rows[source] = [met_systematics_latex[source] + ' (\%)', text]
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

    #append the total statistical error to the table
    printout += '\\hline \n'
    total_line = 'Total Stat. (\%)'
    for bin_i, variable_bin in enumerate(bins):
        if print_before_unfolding:
            value, error = central_values['measured'][bin_i]
        else:
            value, error = central_values['unfolded'][bin_i]
        relativeError = getRelativeError(value, error)
        errorHists['statistical'].append(relativeError)
        total_line += ' & %.2f ' % (relativeError * 100)
    printout += total_line + '\\\\ \n'

    if not print_before_unfolding:
        make_error_plot( errorHists, binEdges )

    #append the total systematic error to the table
    total_line = 'Total Sys. (\%)'
    for bin_i, variable_bin in enumerate(bins):
        if print_before_unfolding:
            value, error_up, error_down = central_values['measured_with_systematics_only'][bin_i]
        else:
            value, error_up, error_down = central_values['unfolded_with_systematics_only'][bin_i]
        error = max(error_up, error_down)
        relativeError = getRelativeError(value, error)
        total_line += ' & %.2f ' % (relativeError * 100)
    printout += total_line + '\\\\ \n'

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
        path = output_folder + '/'  + variable + '/'
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
    global output_folder, variable, met_type, b_tag_bin, all_measurements, phase_space, measurement_config
    bins = None
    if phase_space == 'VisiblePS':
        bins = variable_bins_visiblePS_ROOT[variable]
    elif phase_space == 'FullPS':
        bins = variable_bins_ROOT[variable]
    if print_before_unfolding:
        measurement = 'measured'
    else:
        measurement = 'unfolded'

    assert(len(bins) == len(errors['central']))
    assert(len(bins) == len(central_values[measurement]))
    typical_systematics = measurement_config.typical_systematics
    for s in typical_systematics:
        assert(errors.has_key(s))
    
    group_errors = {}
    for group in measurement_config.typical_systematics_summary:
        group_errors[group] = []

    for bin_i, _ in enumerate(bins):

        central_value = central_values[measurement][bin_i][0]
        uncertainties = {}
        # calculate all relative errors
        for systematic in typical_systematics:
            abs_error = errors[systematic][bin_i]
            relative_error = getRelativeError(central_value, abs_error)
            uncertainties[systematic] = relative_error
        # add errors in a group in quadrature
        for group, u_list in measurement_config.typical_systematics_summary.items():

            group_error_squared = 0
            for subgroup in u_list:
                # use the biggest of up and down
                subgroup_error = max(uncertainties[subgroup[0]], uncertainties[subgroup[1]])
                group_error_squared += pow(subgroup_error, 2)
            group_errors[group].append(math.sqrt(group_error_squared))

    summarised_typical_systematics = {}
    summarised_max_systematics = {}
    # calculate the median
    # x 100 to be in %
    for group, u_list in group_errors.items():
        summarised_typical_systematics[group] = median(u_list)*100
        summarised_max_systematics[group] = max(u_list) * 100

    for summary, errors in {'median':summarised_typical_systematics,'max':summarised_max_systematics}.iteritems():
        printout = '%% ' + '=' * 60
        printout += '\n'
        printout += '%% Typical systematics table for {0} channel, met type {1}, {2} b-tag region\n'.format(channel, met_type, b_tag_bin)
        if print_before_unfolding:
            printout += '%% BEFORE UNFOLDING\n'
        printout += '%% ' + '=' * 60
        printout += '\n'
        printout += '\\begin{table}[htbp]\n'
        printout += '\\centering\n'
        printout += '\\caption{Typical systematic uncertainties (median values) for the normalised \\ttbar cross section measurement \n'
        printout += 'at a centre-of-mass energy of {0} TeV '.format(measurement_config.centre_of_mass_energy)
        if channel == 'combined' or channel == 'combinedBeforeUnfolding':
            printout += '(combination of electron and muon channels).}\n'
        else:
            printout += '({0} channel).}\n'.format(channel)
        printout += '\\label{{tab:typical_systematics_{0}TeV_{1}}}\n'.format(measurement_config.centre_of_mass_energy, channel)
        printout += '\\resizebox{\\columnwidth}{!} {\n'
        printout += '\\begin{tabular}{l' + 'r'*len(bins) + '}\n'
        printout += '\\hline\n'

        header = 'Uncertainty source '
        header += '& {0}'.format(variables_latex[variable])

        header += ' '
        printout += header
        printout += '\n\\hline\n'
        for group, ts in errors.items():
            printout += group + ' (\\%) & {:.2f} \\\\ \n'.format(ts)
        printout += '\\hline \n'
        printout += '\\hline \n'
        printout += '\\end{tabular}\n'
        printout += '}\n'
        printout += '\\end{table}\n'

        if toFile:
            path = output_folder + '/'
            make_folder_if_not_exists(path)
            file_template = path + '/{0}_systematics_{1}TeV_{2}.tex'.format(summary,measurement_config.centre_of_mass_energy, channel)

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
                            for group, ts in errors.items():
                                if line.startswith(group):
                                    new_line = line.replace('\\\\', '')
                                    new_line = new_line.strip()
                                    lines[line_number] = new_line + '& {:.2f} \\\\ \n'.format(ts)
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
    parser.add_option("-p", "--path", dest="path", default='data/M3_angle_bl',
                  help="set path to JSON files")
    parser.add_option("-o", "--output_folder", dest="output_folder", default='tables/',
                  help="set path to save tables")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                  help="set variable to plot (MET, HT, ST, MT, WPT)")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type used in the analysis of MET-dependent variables")
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                  help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=13, type=int,
                      help="set the centre of mass energy for analysis. Default = 13 [TeV]")
    parser.add_option("-a", "--additional-tables", action="store_true", dest="additional_tables",
                      help="creates a set of tables for each systematic (in addition to central result).")
    parser.add_option( '--visiblePS', dest = "visiblePS", action = "store_true",
                      help = "Unfold to visible phase space" )
    parser.add_option( "-u", "--unfolding_method", dest = "unfolding_method", default = 'TUnfold',
                      help = "Unfolding method: TUnfold (default), RooUnfoldSvd, TSVDUnfold, RooUnfoldTUnfold, RooUnfoldInvert, RooUnfoldBinByBin, RooUnfoldBayes" )

    (options, args) = parser.parse_args()
    measurement_config = XSectionConfig(options.CoM)
    # caching of variables for shorter access
    translate_options = measurement_config.translate_options
    ttbar_theory_systematic_prefix = measurement_config.ttbar_theory_systematic_prefix
    vjets_theory_systematic_prefix = measurement_config.vjets_theory_systematic_prefix
    met_systematics = measurement_config.met_systematics
    typical_systematics = measurement_config.typical_systematics
    method = options.unfolding_method

    variable = options.variable
    output_folder = options.output_folder

    visiblePS = options.visiblePS
    phase_space = 'FullPS'
    if visiblePS:
        phase_space = 'VisiblePS'
    output_folder += '/' + str(measurement_config.centre_of_mass_energy) + 'TeV/' + phase_space + '/'

    met_type = translate_options[options.metType]
    b_tag_bin = translate_options[options.bjetbin]

    path_to_JSON = '{path}/{com}TeV/{variable}/{phase_space}/'
    path_to_JSON = path_to_JSON.format(path = options.path, com = options.CoM,
                                       variable = variable,
                                       phase_space = phase_space,
                                       )

    #remove btag mistagging rate systematic - new btagging method has only one, all-inclusive sytematic
    categories_and_prefixes = measurement_config.categories_and_prefixes
    ### del categories_and_prefixes['LightJet_down']
    ### del categories_and_prefixes['LightJet_up']

    categories = deepcopy(categories_and_prefixes.keys())

    ttbar_generator_systematics = [ttbar_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    ### vjets_generator_systematics = [vjets_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    categories.extend(ttbar_generator_systematics)
    ### categories.extend(vjets_generator_systematics)

    pdf_uncertainties = ['PDF_total_lower', 'PDF_total_upper']

    ### # all MET uncertainties except JES as this is already included
    new_uncertainties = ['QCD_shape']
    rate_changing_systematics = measurement_config.rate_changing_systematics_names
    all_measurements = deepcopy(categories)
    all_measurements.extend(pdf_uncertainties)
    all_measurements.extend(new_uncertainties)

    all_measurements.extend(rate_changing_systematics)

    for channel in ['electron', 'muon', 'combined', 'combinedBeforeUnfolding']:                        
    # for channel in ['combined']:                        
        normalised_xsection_measured_unfolded, normalised_xsection_measured_errors, normalised_xsection_unfolded_errors = read_xsection_measurement_results_with_errors(path_to_JSON, variable, met_type, phase_space, method, channel)

        print_xsections(normalised_xsection_measured_unfolded, channel, toFile = True, print_before_unfolding = False)
        print_xsections(normalised_xsection_measured_unfolded, channel, toFile = True, print_before_unfolding = True)

        print_error_table(normalised_xsection_measured_unfolded, normalised_xsection_unfolded_errors, channel, toFile = True, print_before_unfolding = False)
        print_error_table(normalised_xsection_measured_unfolded, normalised_xsection_measured_errors, channel, toFile = True, print_before_unfolding = True)

        if channel == 'combined':
            print_typical_systematics_table(normalised_xsection_measured_unfolded, normalised_xsection_unfolded_errors, channel, toFile = True, print_before_unfolding = False)
            print_typical_systematics_table(normalised_xsection_measured_unfolded, normalised_xsection_measured_errors, channel, toFile = True, print_before_unfolding = True)

        if not channel == 'combined' and not channel == 'combinedBeforeUnfolding':
            fit_input = read_initial_normalisation(path_to_JSON, variable, 'central', channel, met_type)
            fit_results = read_normalisation(path_to_JSON, variable, 'central', channel, met_type)
            print_fit_results_table(fit_input, fit_results, channel, toFile = True)

    
