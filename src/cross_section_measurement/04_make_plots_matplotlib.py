from __future__ import division  # the result of the division will be always a float
from optparse import OptionParser
import os, gc
from copy import deepcopy

from config.cross_section_measurement_common import met_systematics_suffixes, translate_options, ttbar_theory_systematic_prefix, vjets_theory_systematic_prefix
from config.latex_labels import b_tag_bins_latex, variables_latex, measurements_latex, met_systematics_latex
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from tools.hist_utilities import value_error_tuplelist_to_hist, value_tuplelist_to_hist, value_errors_tuplelist_to_graph
from math import sqrt
# rootpy
from ROOT import kRed, kGreen, kMagenta, kBlue, kAzure, kYellow, kViolet
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from config import CMS
from matplotlib import rc
rc('text', usetex=True)
# this does not work because of global variables. They need to be parameters
# make_plots_ROOT = __import__('04_make_plots_ROOT')
# read_xsection_measurement_results = make_plots_ROOT.read_xsection_measurement_results
# read_unfolded_xsections = make_plots_ROOT.read_unfolded_xsections

def read_xsection_measurement_results(category, channel):
    global path_to_JSON, variable, k_value, met_type
    
    normalised_xsection_unfolded = None
    if category in met_uncertainties and variable == 'HT':
        normalised_xsection_unfolded = read_data_from_JSON(path_to_JSON + '/xsection_measurement_results' + '/kv' + str(k_value) + '/' 
                                                       + 'central' + '/normalised_xsection_' + channel + '_' + met_type + '.txt')
    else:
        normalised_xsection_unfolded = read_data_from_JSON(path_to_JSON + '/xsection_measurement_results' + '/kv' + str(k_value) + '/' 
                                                       + category + '/normalised_xsection_' + channel + '_' + met_type + '.txt')
        
    h_normalised_xsection = value_error_tuplelist_to_hist(normalised_xsection_unfolded['TTJet_measured'], bin_edges[variable])
    h_normalised_xsection_unfolded = value_error_tuplelist_to_hist(normalised_xsection_unfolded['TTJet_unfolded'], bin_edges[variable])
    
    
    histograms_normalised_xsection_different_generators = {'measured':h_normalised_xsection,
                                                           'unfolded':h_normalised_xsection_unfolded}
    
    histograms_normalised_xsection_systematics_shifts = {'measured':h_normalised_xsection,
                                                         'unfolded':h_normalised_xsection_unfolded}
    
    if category == 'central':
        # true distributions
        h_normalised_xsection_MADGRAPH = value_error_tuplelist_to_hist(normalised_xsection_unfolded['MADGRAPH'], bin_edges[variable])
        h_normalised_xsection_POWHEG = value_error_tuplelist_to_hist(normalised_xsection_unfolded['POWHEG'], bin_edges[variable])
        h_normalised_xsection_MCATNLO = value_error_tuplelist_to_hist(normalised_xsection_unfolded['MCATNLO'], bin_edges[variable])
        h_normalised_xsection_mathchingup = value_error_tuplelist_to_hist(normalised_xsection_unfolded['matchingup'], bin_edges[variable])
        h_normalised_xsection_mathchingdown = value_error_tuplelist_to_hist(normalised_xsection_unfolded['matchingdown'], bin_edges[variable])
        h_normalised_xsection_scaleup = value_error_tuplelist_to_hist(normalised_xsection_unfolded['scaleup'], bin_edges[variable])
        h_normalised_xsection_scaledown = value_error_tuplelist_to_hist(normalised_xsection_unfolded['scaledown'], bin_edges[variable])
        
        histograms_normalised_xsection_different_generators.update({'MADGRAPH':h_normalised_xsection_MADGRAPH,
                                                                    'POWHEG':h_normalised_xsection_POWHEG,
                                                                    'MCATNLO':h_normalised_xsection_MCATNLO})
        
        histograms_normalised_xsection_systematics_shifts.update({'MADGRAPH':h_normalised_xsection_MADGRAPH,
                                                                  'matchingdown': h_normalised_xsection_mathchingdown,
                                                                  'matchingup': h_normalised_xsection_mathchingup,
                                                                  'scaledown': h_normalised_xsection_scaledown,
                                                                  'scaleup': h_normalised_xsection_scaleup})
        
        normalised_xsection_unfolded_with_errors = read_data_from_JSON(path_to_JSON + '/xsection_measurement_results' + '/kv' + 
                                                                   str(k_value) + '/' + category + '/normalised_xsection_' + 
                                                                   channel + '_' + met_type + '_with_errors.txt')
        # a rootpy.Graph with asymmetric errors!
        h_normalised_xsection_with_systematics = value_errors_tuplelist_to_graph(normalised_xsection_unfolded_with_errors['TTJet_measured'], bin_edges[variable])
        h_normalised_xsection_with_systematics_unfolded = value_errors_tuplelist_to_graph(normalised_xsection_unfolded_with_errors['TTJet_unfolded'], bin_edges[variable])
        
        histograms_normalised_xsection_different_generators['measured_with_systematics'] = h_normalised_xsection_with_systematics
        histograms_normalised_xsection_different_generators['unfolded_with_systematics'] = h_normalised_xsection_with_systematics_unfolded
        
        histograms_normalised_xsection_systematics_shifts['measured_with_systematics'] = h_normalised_xsection_with_systematics
        histograms_normalised_xsection_systematics_shifts['unfolded_with_systematics'] = h_normalised_xsection_with_systematics_unfolded
    
    return histograms_normalised_xsection_different_generators, histograms_normalised_xsection_systematics_shifts

def read_unfolded_xsections(channel):
    global path_to_JSON, variable, k_value, met_type, b_tag_bin
    TTJet_xsection_unfolded = {}
    for category in categories:
        normalised_xsections = read_data_from_JSON(path_to_JSON + '/xsection_measurement_results' + '/kv' + str(k_value) + '/' + category + '/normalised_xsection_' + channel + '_' + met_type + '.txt')
        TTJet_xsection_unfolded[category] = normalised_xsections['TTJet_unfolded']
    return TTJet_xsection_unfolded

def read_fit_templates_and_results_as_histograms(category, channel):
    global path_to_JSON, variable, met_type
    templates = read_data_from_JSON(path_to_JSON + '/fit_results/' + category + '/templates_' + channel + '_' + met_type + '.txt')
    data_values = read_data_from_JSON(path_to_JSON + '/fit_results/' + category + '/initial_values_' + channel + '_' + met_type + '.txt')['data']
    fit_results = read_data_from_JSON(path_to_JSON + '/fit_results/' + category + '/fit_results_' + channel + '_' + met_type + '.txt')
    template_histograms = {}
    fit_results_histograms = {}
    for bin_i, variable_bin in enumerate(variable_bins_ROOT[variable]):
        h_template_data = value_tuplelist_to_hist(templates['data'][bin_i], eta_bin_edges)
        h_template_signal = value_tuplelist_to_hist(templates['signal'][bin_i], eta_bin_edges)
        h_template_VJets = value_tuplelist_to_hist(templates['V+Jets'][bin_i], eta_bin_edges)
        h_template_QCD = value_tuplelist_to_hist(templates['QCD'][bin_i], eta_bin_edges)
        template_histograms[variable_bin] = {
                                    'signal':h_template_signal,
                                    'V+Jets':h_template_VJets,
                                    'QCD':h_template_QCD
                                    }
        h_data = h_template_data.Clone()
        h_signal = h_template_signal.Clone()
        h_VJets = h_template_VJets.Clone()
        h_QCD = h_template_QCD.Clone()
        
        data_normalisation = data_values[bin_i]
        signal_normalisation = fit_results['signal'][bin_i][0]
        VJets_normalisation = fit_results['V+Jets'][bin_i][0]
        QCD_normalisation = fit_results['QCD'][bin_i][0]
        
        h_data.Scale(data_normalisation)
        h_signal.Scale(signal_normalisation)
        h_VJets.Scale(VJets_normalisation)
        h_QCD.Scale(QCD_normalisation)
        h_background = h_VJets + h_QCD
        
        for bin_i in range(len(h_data)):
            h_data.SetBinError(bin_i + 1, sqrt(h_data.GetBinContent(bin_i + 1)))
        
        fit_results_histograms[variable_bin] = {
                                                'data':h_data,
                                                'signal':h_signal,
                                                'background':h_background
                                                }
        
    return template_histograms, fit_results_histograms

def make_template_plots(histograms, category, channel):
    global variable, output_folder
    
    for variable_bin in variable_bins_ROOT[variable]:
        path = output_folder + str(measurement_config.centre_of_mass) + 'TeV/' + variable + '/' + category + '/fit_templates/'
        make_folder_if_not_exists(path)
        plotname = path + channel + '_templates_bin_' + variable_bin 
        
        # check if template plots exist already
        for output_format in output_formats:
            if os.path.isfile(plotname + '.' + output_format):
                continue
        
        # plot with matplotlib
        h_signal = histograms[variable_bin]['signal']
        h_VJets = histograms[variable_bin]['V+Jets']
        h_QCD = histograms[variable_bin]['QCD']
        
        h_signal.linecolor = 'red'
        h_VJets.linecolor = 'green'
        h_QCD.linecolor = 'gray'
        h_VJets.linestyle = 'dashed'
        h_QCD.linestyle = 'dotted'# currently not working
        #bug report: http://trac.sagemath.org/sage_trac/ticket/13834
        
        h_signal.linewidth = 5
        h_VJets.linewidth = 5
        h_QCD.linewidth = 5
    
        plt.figure(figsize=(16, 16), dpi=200, facecolor='white')
        axes = plt.axes()
        axes.minorticks_on()
        
        plt.xlabel(r'lepton $|\eta|$', CMS.x_axis_title)
        plt.ylabel('normalised to unit area/0.2', CMS.y_axis_title)
        plt.tick_params(**CMS.axis_label_major)
        plt.tick_params(**CMS.axis_label_minor)

        rplt.hist(h_signal, axes=axes, label='signal')
        if (h_VJets.Integral() != 0):
            rplt.hist(h_VJets, axes=axes, label='V+Jets')
        else:
            print "WARNING: in %s bin %s, %s category, %s channel, V+Jets template is empty: not plotting." % (variable, variable_bin, category, channel)
        if (h_QCD.Integral() != 0):
            rplt.hist(h_QCD, axes=axes, label='QCD')
        else:
            print "WARNING: in %s bin %s, %s category, %s channel, QCD template is empty: not plotting." % (variable, variable_bin, category, channel)
        axes.set_ylim([0, 0.2])
        
        plt.legend(numpoints=1, loc='upper right', prop=CMS.legend_properties)
        plt.title(get_cms_labels(channel), CMS.title)
        plt.tight_layout()
    
        for output_format in output_formats:
            plt.savefig(plotname + '.' + output_format)
        
        plt.close()
        gc.collect()


def plot_fit_results(histograms, category, channel):
    global variable, b_tag_bin, output_folder
    from tools.plotting import Histogram_properties, make_data_mc_comparison_plot
    
    for variable_bin in variable_bins_ROOT[variable]:
        path = output_folder + str(measurement_config.centre_of_mass) + 'TeV/' + variable + '/' + category + '/fit_results/'
        make_folder_if_not_exists(path)
        plotname = channel + '_bin_' + variable_bin
        # check if template plots exist already
        for output_format in output_formats:
            if os.path.isfile(plotname + '.' + output_format):
                continue
            
        # plot with matplotlib
        h_data = histograms[variable_bin]['data']
        h_signal = histograms[variable_bin]['signal']
        h_background = histograms[variable_bin]['background']
        
        histogram_properties = Histogram_properties()
        histogram_properties.name = plotname
        histogram_properties.x_axis_title = channel + ' $\left|\eta\\right|$'
        histogram_properties.y_axis_title = 'events/0.2'
        histogram_properties.title = get_cms_labels(channel)
        
        make_data_mc_comparison_plot([h_data, h_background, h_signal], 
                                     ['data', 'background', 'signal'], 
                                     ['black', 'green', 'red'], histogram_properties, 
                                     save_folder = path, save_as = output_formats)    

def get_cms_labels(channel):
    global b_tag_bin, b_tag_bins_latex
    lepton = 'e'
    if channel == 'electron':
        lepton = 'e + jets'
    elif channel == 'muon':
        lepton = '$\mu$ + jets'
    else:
        lepton = 'e, $\mu$ + jets combined'
    channel_label = '%s, $\geq$ 4 jets, %s' % (lepton, b_tag_bins_latex[b_tag_bin])
    template = 'CMS Preliminary, $\mathcal{L} = %.1f$ fb$^{-1}$  at $\sqrt{s}$ = %d TeV \n %s'
    label = template % (measurement_config.luminosity / 1000., measurement_config.centre_of_mass, channel_label)
    return label
    
    
def make_plots(histograms, category, output_folder, histname, show_before_unfolding=False):
    global variable, k_value
    
    channel = 'electron'
    if 'electron' in histname:
        channel = 'electron'
    elif 'muon' in histname:
        channel = 'muon'
    else:
        channel = 'combined'
        
    # plot with matplotlib
    hist_data = histograms['unfolded']
    if category == 'central':
        hist_data_with_systematics = histograms['unfolded_with_systematics']
    hist_measured = histograms['measured']
    
    hist_data.markersize = 2
    hist_data.marker = 'o'

    if category == 'central':
        hist_data_with_systematics.markersize = 2
        hist_data_with_systematics.marker = 'o'
    
    hist_measured.markersize = 2
    hist_measured.marker = 'o'
    hist_measured.color = 'red'

    plt.figure(figsize=(16, 16), dpi=200, facecolor='white')
    axes = plt.axes()
    axes.minorticks_on()
    
    plt.xlabel('$%s$ [GeV]' % variables_latex[variable], CMS.x_axis_title)
    plt.ylabel(r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + variables_latex[variable] + '} \left[\mathrm{GeV}^{-1}\\right]$', CMS.y_axis_title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)

    hist_data.visible = True
    if category == 'central':
        hist_data_with_systematics.visible = True
        rplt.errorbar(hist_data_with_systematics, axes=axes, label='do_not_show', xerr=None, capsize=0, elinewidth=2)
    rplt.errorbar(hist_data, axes=axes, label='do_not_show', xerr=None, capsize=15, capthick=3, elinewidth=2)
    rplt.errorbar(hist_data, axes=axes, label='data', xerr=False, yerr= False)#this makes a nicer legend entry

    if show_before_unfolding:
        rplt.errorbar(hist_measured, axes=axes, label='data (before unfolding)', xerr=None)
    
    for key, hist in sorted(histograms.iteritems()):
        if not 'unfolded' in key and not 'measured' in key:
            hist.linewidth = 2
            # setting colours
            if 'POWHEG' in key or 'matchingdown' in key:
                hist.linestyle = 'longdashdot'
                hist.SetLineColor(kBlue)
            elif 'MADGRAPH' in key:
                hist.linestyle = 'solid'
                hist.SetLineColor(kRed + 1)
            elif 'matchingup' in key:
                hist.linestyle = 'solid'
                hist.linecolor = 'orange'
            elif 'MCATNLO'  in key or 'scaleup' in key:
                hist.linestyle = 'dotted'
                hist.SetLineColor(kMagenta + 3)
            elif 'scaledown' in key:
                hist.linestyle = 'dashed'
                hist.SetLineColor(kGreen)
            rplt.hist(hist, axes=axes, label=measurements_latex[key])
            
    handles, labels = axes.get_legend_handles_labels()
    # making data first in the list
    data_label_index = labels.index('data')
    data_handle = handles[data_label_index]
    labels.remove('data')
    handles.remove(data_handle)
    labels.insert(0, 'unfolded data')
    handles.insert(0, data_handle)
    
    new_handles, new_labels = [], []
    for handle, label in zip(handles, labels):
        if not label == 'do_not_show':
            new_handles.append(handle)
            new_labels.append(label)
    
    plt.legend(new_handles, new_labels, numpoints=1, loc='upper right', prop=CMS.legend_properties)
    plt.title(get_cms_labels(channel), CMS.title)
    plt.tight_layout()

    path = output_folder + str(measurement_config.centre_of_mass) + 'TeV/' + variable + '/' + category
    make_folder_if_not_exists(path)
    for output_format in output_formats:
        plt.savefig(path + '/' + histname + '_kv' + str(k_value) + '.' + output_format)

    del hist_data, hist_measured
    plt.close()
    gc.collect()

def plot_central_and_systematics(channel, systematics, exclude=[], suffix='altogether'):
    global variable, k_value, b_tag_bin, met_type

    plt.figure(figsize=(16, 16), dpi=200, facecolor='white')
    axes = plt.axes()
    axes.minorticks_on()
    
    hist_data_central = read_xsection_measurement_results('central', channel)[0]['unfolded_with_systematics']
    hist_data_central.markersize = 2  # points. Imagine, tangible units!
    hist_data_central.marker = 'o'
    
    
    plt.xlabel('$%s$ [GeV]' % variables_latex[variable], CMS.x_axis_title)
    plt.ylabel(r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + variables_latex[variable] + '} \left[\mathrm{GeV}^{-1}\\right]$', CMS.y_axis_title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)

    rplt.errorbar(hist_data_central, axes=axes, label='data', xerr=True)

    for systematic in sorted(systematics):
        if systematic in exclude or systematic == 'central':
            continue

        hist_data_systematic = read_xsection_measurement_results(systematic, channel)[0]['unfolded']
        hist_data_systematic.markersize = 2
        hist_data_systematic.marker = 'o'
        colour_number = systematics.index(systematic) + 2
        if colour_number == 10:
            colour_number = 42
        hist_data_systematic.SetMarkerColor(colour_number)
        if 'PDF' in systematic:
            rplt.errorbar(hist_data_systematic, axes=axes, label=systematic.replace('Weights_', ' '), xerr=False)
        elif met_type in systematic:
            rplt.errorbar(hist_data_systematic, axes=axes, label=met_systematics_latex[systematic.replace(met_type, '')], xerr=False)
        else:
            rplt.errorbar(hist_data_systematic, axes=axes, label=measurements_latex[systematic], xerr=False)
            
    plt.legend(numpoints=1, loc='upper right', prop={'size':25}, ncol=2)
    plt.title(get_cms_labels(channel), CMS.title)
    plt.tight_layout()

    
    path = output_folder + str(measurement_config.centre_of_mass) + 'TeV/' + variable
    make_folder_if_not_exists(path)
    for output_format in output_formats:
        plt.savefig(path + '/normalised_xsection_' + channel + '_' + suffix + '_kv' + str(k_value) + '.' + output_format) 

    plt.close()
    gc.collect()

if __name__ == '__main__':
    from ROOT import gROOT
    gROOT.SetBatch(True)
    gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data/',
                  help="set path to JSON files")
    parser.add_option("-o", "--output_folder", dest="output_folder", default='plots/',
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
    parser.add_option("-a", "--additional-plots", action="store_true", dest="additional_plots",
                      help="creates a set of plots for each systematic (in addition to central result).")
    
    maximum = {
               'MET': 0.02,
               'HT': 0.005,
               'ST': 0.004,
               'MT': 0.02
               }

    output_formats = ['png', 'pdf']
    (options, args) = parser.parse_args()
    if options.CoM == 8:
        from config.variable_binning_8TeV import bin_edges, variable_bins_ROOT, eta_bin_edges
        import config.cross_section_measurement_8TeV as measurement_config
    elif options.CoM == 7:
        from config.variable_binning_7TeV import bin_edges, variable_bins_ROOT, eta_bin_edges
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
    new_uncertainties = [ttbar_theory_systematic_prefix + 'ptreweight', ttbar_theory_systematic_prefix + 'mcatnlo_matrix']
    all_measurements = deepcopy(categories)
    all_measurements.extend(pdf_uncertainties)
    all_measurements.extend(met_uncertainties)
    all_measurements.extend(new_uncertainties)
    for channel in ['electron', 'muon', 'combined']:
        for category in all_measurements:
            if not category == 'central' and not options.additional_plots:
                continue
            if variable == 'HT' and category in met_uncertainties:
                continue
            # setting up systematic MET for JES up/down samples for reading fit templates
            met_type = translate_options[options.metType]
            if category == 'JES_up':
                met_type += 'JetEnUp'
                if met_type == 'PFMETJetEnUp':
                    met_type = 'patPFMetJetEnUp'
            elif category == 'JES_down':
                met_type += 'JetEnDown'
                if met_type == 'PFMETJetEnDown':
                    met_type = 'patPFMetJetEnDown'
            
            if not channel == 'combined':
                fit_templates, fit_results = read_fit_templates_and_results_as_histograms(category, channel)
                make_template_plots(fit_templates, category, channel)
                plot_fit_results(fit_results, category, channel)

            # change back to original MET type
            met_type = translate_options[options.metType]
            if met_type == 'PFMET':
                met_type = 'patMETsPFlow'
            
            histograms_normalised_xsection_different_generators, histograms_normalised_xsection_systematics_shifts = read_xsection_measurement_results(category, channel)
    
            make_plots(histograms_normalised_xsection_different_generators, category, output_folder, 'normalised_xsection_' + channel + '_different_generators')
            make_plots(histograms_normalised_xsection_systematics_shifts, category, output_folder, 'normalised_xsection_' + channel + '_systematics_shifts')

            del histograms_normalised_xsection_different_generators, histograms_normalised_xsection_systematics_shifts
    
        plot_central_and_systematics(channel, categories, exclude=ttbar_generator_systematics)
        
        plot_central_and_systematics(channel, ttbar_generator_systematics, suffix='ttbar_theory_only')
        
        exclude = set(pdf_uncertainties).difference(set(pdf_uncertainties_1_to_11))
        plot_central_and_systematics(channel, pdf_uncertainties_1_to_11, exclude=exclude, suffix='PDF_1_to_11')
        
        exclude = set(pdf_uncertainties).difference(set(pdf_uncertainties_12_to_22))
        plot_central_and_systematics(channel, pdf_uncertainties_12_to_22, exclude=exclude, suffix='PDF_12_to_22')
        
        exclude = set(pdf_uncertainties).difference(set(pdf_uncertainties_23_to_33))
        plot_central_and_systematics(channel, pdf_uncertainties_23_to_33, exclude=exclude, suffix='PDF_23_to_33')
        
        exclude = set(pdf_uncertainties).difference(set(pdf_uncertainties_34_to_44))
        plot_central_and_systematics(channel, pdf_uncertainties_34_to_44, exclude=exclude, suffix='PDF_34_to_44')
        
        plot_central_and_systematics(channel, met_uncertainties, suffix='MET_only')
        plot_central_and_systematics(channel, new_uncertainties, suffix='new_only')
