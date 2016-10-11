from __future__ import division  # the result of the division will be always a float
from optparse import OptionParser
import os, gc
from copy import deepcopy

from config.latex_labels import variables_latex, measurements_latex, \
met_systematics_latex, fit_variables_latex
from config.variable_binning import bin_edges, variable_bins_ROOT, fit_variable_bin_edges
from config import XSectionConfig
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from tools.hist_utilities import value_error_tuplelist_to_hist, spread_x,\
value_tuplelist_to_hist, value_errors_tuplelist_to_graph, graph_to_value_errors_tuplelist
from tools.plotting import adjust_ratio_ticks
from math import sqrt
# rootpy & matplotlib
from ROOT import kRed, kGreen, kMagenta, kBlue, kBlack, kCyan
from tools.ROOT_utils import set_root_defaults
import matplotlib as mpl
from tools.plotting import get_best_max_y
mpl.use( 'agg' )
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator
from config import CMS
from tools.latex import setup_matplotlib
# latex, font, etc
setup_matplotlib()

import matplotlib.patches as mpatches

def read_xsection_measurement_results( category, channel ):
    global path_to_JSON, variable, k_values, met_type
    
    filename = ''
    if category in met_uncertainties and variable == 'HT':
        filename = path_to_JSON + '/xsection_measurement_results/' + channel + '/kv' + str( k_values[channel] ) + '/central/normalised_xsection_' + met_type + '.txt'
    else:
        filename = path_to_JSON + '/xsection_measurement_results/' + channel + '/kv' + str( k_values[channel] ) + '/' + category + '/normalised_xsection_' + met_type + '.txt'

    if channel == 'combined':
        filename = filename.replace( 'kv' + str( k_values[channel] ), '' )

    normalised_xsection_unfolded = read_data_from_JSON( filename )

    h_normalised_xsection = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJet_measured'], bin_edges[variable] )
    h_normalised_xsection_unfolded = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJet_unfolded'], bin_edges[variable] )    
    
    histograms_normalised_xsection_different_generators = {'measured':h_normalised_xsection,
                                                           'unfolded':h_normalised_xsection_unfolded}
    histograms_normalised_xsection_systematics_shifts = {'measured':h_normalised_xsection,
                                                         'unfolded':h_normalised_xsection_unfolded}
    if draw_background_subtraction:
        # filename for background subtraction data
        filename_background_subtraction = filename.replace(path_to_JSON, path_to_JSON_background_subtraction)
        # get normalised differential cross section values from data (JSON) file
        normalised_xsection_unfolded_background_subtraction = read_data_from_JSON( filename_background_subtraction )
        # convert numerical values to histogram
        h_normalised_xsection_background_subtraction_unfolded = value_error_tuplelist_to_hist( normalised_xsection_unfolded_background_subtraction['TTJet_unfolded'], bin_edges[variable] )
        # add background subtraction data histogram to dictionaries to be drawn later
        histograms_normalised_xsection_different_generators.update({'unfolded_background_subtraction':h_normalised_xsection_background_subtraction_unfolded})
        histograms_normalised_xsection_systematics_shifts.update({'unfolded_background_subtraction':h_normalised_xsection_background_subtraction_unfolded})
    
    if category == 'central':
        # true distributions
        h_normalised_xsection_MADGRAPH = value_error_tuplelist_to_hist( normalised_xsection_unfolded['MADGRAPH'], bin_edges[variable] )
        h_normalised_xsection_MADGRAPH_ptreweight = value_error_tuplelist_to_hist( normalised_xsection_unfolded['MADGRAPH_ptreweight'], bin_edges[variable] )
        h_normalised_xsection_POWHEG_V2_PYTHIA = value_error_tuplelist_to_hist( normalised_xsection_unfolded['powheg_v2_pythia'], bin_edges[variable] )
        h_normalised_xsection_POWHEG_V2_HERWIG = value_error_tuplelist_to_hist( normalised_xsection_unfolded['powheg_v2_herwig'], bin_edges[variable] )
        h_normalised_xsection_MCATNLO = None
        h_normalised_xsection_POWHEG_V1_HERWIG = None
        h_normalised_xsection_POWHEG_V1_PYTHIA = None
        if measurement_config.centre_of_mass_energy == 8:
            h_normalised_xsection_MCATNLO = value_error_tuplelist_to_hist( normalised_xsection_unfolded['MCATNLO'], bin_edges[variable] )
            h_normalised_xsection_POWHEG_V1_HERWIG = value_error_tuplelist_to_hist( normalised_xsection_unfolded['powheg_v1_herwig'], bin_edges[variable] )
            h_normalised_xsection_POWHEG_V1_PYTHIA = value_error_tuplelist_to_hist( normalised_xsection_unfolded['powheg_v1_pythia'], bin_edges[variable] )

        h_normalised_xsection_mathchingup = value_error_tuplelist_to_hist( normalised_xsection_unfolded['matchingup'], bin_edges[variable] )
        h_normalised_xsection_mathchingdown = value_error_tuplelist_to_hist( normalised_xsection_unfolded['matchingdown'], bin_edges[variable] )
        h_normalised_xsection_scaleup = value_error_tuplelist_to_hist( normalised_xsection_unfolded['scaleup'], bin_edges[variable] )
        h_normalised_xsection_scaledown = value_error_tuplelist_to_hist( normalised_xsection_unfolded['scaledown'], bin_edges[variable] )
        
        histograms_normalised_xsection_different_generators.update( {'MADGRAPH':h_normalised_xsection_MADGRAPH,
                                                                'MADGRAPH_ptreweight':h_normalised_xsection_MADGRAPH_ptreweight,
                                                                'powheg_v2_pythia':h_normalised_xsection_POWHEG_V2_PYTHIA,
                                                                'powheg_v2_herwig':h_normalised_xsection_POWHEG_V2_HERWIG,
                                                                } )
        if measurement_config.centre_of_mass_energy == 8:
            histograms_normalised_xsection_different_generators.update( {'MCATNLO':h_normalised_xsection_MCATNLO} )
            histograms_normalised_xsection_different_generators.update( {'powheg_v1_herwig':h_normalised_xsection_POWHEG_V1_HERWIG} )
            histograms_normalised_xsection_different_generators.update( {'powheg_v1_pythia':h_normalised_xsection_POWHEG_V1_PYTHIA} )

        
        histograms_normalised_xsection_systematics_shifts.update( {'MADGRAPH':h_normalised_xsection_MADGRAPH,
                                                                  'MADGRAPH_ptreweight':h_normalised_xsection_MADGRAPH_ptreweight,
                                                                  'matchingdown': h_normalised_xsection_mathchingdown,
                                                                  'matchingup': h_normalised_xsection_mathchingup,
                                                                  'scaledown': h_normalised_xsection_scaledown,
                                                                  'scaleup': h_normalised_xsection_scaleup} )
        
        file_template = path_to_JSON + '/xsection_measurement_results/' + channel + '/kv' + str( k_values[channel] ) + '/' + category + '/normalised_xsection_' + met_type
        if channel == 'combined':
            file_template = file_template.replace( 'kv' + str( k_values[channel] ), '' )
#         normalised_xsection_unfolded_with_errors = read_data_from_JSON( file_template + '_with_errors.txt' )
#         normalised_xsection_unfolded_with_errors_with_systematics_but_without_ttbar_theory = read_data_from_JSON( file_template + '_with_systematics_but_without_ttbar_theory_errors.txt' )
#         normalised_xsection_unfolded_with_errors_with_systematics_but_without_generator = read_data_from_JSON( file_template + '_with_systematics_but_without_generator_errors.txt' )
        normalised_xsection_unfolded_with_errors_with_systematics_but_without_ttbar_theory = read_data_from_JSON( file_template + '_with_errors.txt' )
        normalised_xsection_unfolded_with_errors_with_systematics_but_without_generator = read_data_from_JSON( file_template + '_with_errors.txt' )

        # a rootpy.Graph with asymmetric errors!
        h_normalised_xsection_with_systematics_but_without_ttbar_theory = value_errors_tuplelist_to_graph( 
                                                                normalised_xsection_unfolded_with_errors_with_systematics_but_without_ttbar_theory['TTJet_measured'],
                                                                bin_edges[variable] )
        h_normalised_xsection_with_systematics_but_without_ttbar_theory_unfolded = value_errors_tuplelist_to_graph( 
                                                                normalised_xsection_unfolded_with_errors_with_systematics_but_without_ttbar_theory['TTJet_unfolded'],
                                                                bin_edges[variable] )
        
        h_normalised_xsection_with_systematics_but_without_generator = value_errors_tuplelist_to_graph( 
                                                                normalised_xsection_unfolded_with_errors_with_systematics_but_without_generator['TTJet_measured'],
                                                                bin_edges[variable] )
        h_normalised_xsection_with_systematics_but_without_generator_unfolded = value_errors_tuplelist_to_graph( 
                                                                normalised_xsection_unfolded_with_errors_with_systematics_but_without_generator['TTJet_unfolded'],
                                                                bin_edges[variable] )
        
        histograms_normalised_xsection_different_generators['measured_with_systematics'] = h_normalised_xsection_with_systematics_but_without_ttbar_theory
        histograms_normalised_xsection_different_generators['unfolded_with_systematics'] = h_normalised_xsection_with_systematics_but_without_ttbar_theory_unfolded
        
        histograms_normalised_xsection_systematics_shifts['measured_with_systematics'] = h_normalised_xsection_with_systematics_but_without_generator
        histograms_normalised_xsection_systematics_shifts['unfolded_with_systematics'] = h_normalised_xsection_with_systematics_but_without_generator_unfolded
    
        if draw_background_subtraction:
            file_template_background_subtraction = file_template.replace(path_to_JSON, path_to_JSON_background_subtraction)
            normalised_xsection_unfolded_with_errors_with_systematics_but_without_ttbar_theory_background_subtraction = read_data_from_JSON( file_template_background_subtraction + '_with_errors.txt' )
            normalised_xsection_unfolded_with_errors_with_systematics_but_without_generator_background_subtraction = read_data_from_JSON( file_template_background_subtraction + '_with_errors.txt' )
            h_normalised_xsection_with_systematics_but_without_ttbar_theory_unfolded_background_subtraction = value_errors_tuplelist_to_graph( 
                                                                    normalised_xsection_unfolded_with_errors_with_systematics_but_without_ttbar_theory_background_subtraction['TTJet_unfolded'],
                                                                    bin_edges[variable] )
            h_normalised_xsection_with_systematics_but_without_generator_unfolded_background_subtraction = value_errors_tuplelist_to_graph( 
                                                                    normalised_xsection_unfolded_with_errors_with_systematics_but_without_generator_background_subtraction['TTJet_unfolded'],
                                                                    bin_edges[variable] )
            histograms_normalised_xsection_different_generators['unfolded_with_systematics_background_subtraction'] = h_normalised_xsection_with_systematics_but_without_ttbar_theory_unfolded_background_subtraction
            histograms_normalised_xsection_systematics_shifts['unfolded_with_systematics_background_subtraction'] = h_normalised_xsection_with_systematics_but_without_generator_unfolded_background_subtraction
    
    return histograms_normalised_xsection_different_generators, histograms_normalised_xsection_systematics_shifts

def read_fit_templates_and_results_as_histograms( category, channel ):
    global path_to_JSON, variable, met_type
    templates = read_data_from_JSON( path_to_JSON + '/fit_results/' + category + '/templates_' + channel + '_' + met_type + '.txt' )
    data_values = read_data_from_JSON( path_to_JSON + '/fit_results/' + category + '/initial_normalisation_' + channel + '_' + met_type + '.txt' )['data']
    fit_results = read_data_from_JSON( path_to_JSON + '/fit_results/' + category + '/fit_results_' + channel + '_' + met_type + '.txt' )
    fit_variables = templates.keys()
    template_histograms = {fit_variable: {} for fit_variable in fit_variables}
    fit_results_histograms = {fit_variable: {} for fit_variable in fit_variables}
    for bin_i, variable_bin in enumerate( variable_bins_ROOT[variable] ):
        for fit_variable in fit_variables:
            h_template_data = value_tuplelist_to_hist( templates[fit_variable]['data'][bin_i], fit_variable_bin_edges[fit_variable] )
            h_template_ttjet =  value_tuplelist_to_hist( templates[fit_variable]['TTJet'][bin_i], fit_variable_bin_edges[fit_variable] )
            h_template_singletop =  value_tuplelist_to_hist( templates[fit_variable]['SingleTop'][bin_i], fit_variable_bin_edges[fit_variable] )
            h_template_VJets = value_tuplelist_to_hist( templates[fit_variable]['V+Jets'][bin_i], fit_variable_bin_edges[fit_variable] )
            h_template_QCD = value_tuplelist_to_hist( templates[fit_variable]['QCD'][bin_i], fit_variable_bin_edges[fit_variable] )
            template_histograms[fit_variable][variable_bin] = {
                                        'TTJet' : h_template_ttjet,
                                        'SingleTop' : h_template_singletop,
                                        'V+Jets':h_template_VJets,
                                        'QCD':h_template_QCD
                                        }
            h_data = h_template_data.Clone()
            h_ttjet = h_template_ttjet.Clone()
            h_singletop = h_template_singletop.Clone()
            h_VJets = h_template_VJets.Clone()
            h_QCD = h_template_QCD.Clone()
            
            data_normalisation = data_values[bin_i][0]
            n_ttjet = fit_results['TTJet'][bin_i][0]
            n_singletop = fit_results['SingleTop'][bin_i][0]
            VJets_normalisation = fit_results['V+Jets'][bin_i][0]
            QCD_normalisation = fit_results['QCD'][bin_i][0]
            
            h_data.Scale( data_normalisation )
            h_ttjet.Scale( n_ttjet )
            h_singletop.Scale( n_singletop )
            h_VJets.Scale( VJets_normalisation )
            h_QCD.Scale( QCD_normalisation )
            h_background = h_VJets + h_QCD + h_singletop
            
            for bin_i_data in range( len( h_data ) ):
                h_data.SetBinError( bin_i_data + 1, sqrt( h_data.GetBinContent( bin_i_data + 1 ) ) )
            
            fit_results_histograms[fit_variable][variable_bin] = {
                                                    'data' : h_data,
                                                    'signal' : h_ttjet,
                                                    'background' : h_background
                                                    }
        
    return template_histograms, fit_results_histograms

def make_template_plots( histograms, category, channel ):
    global variable, output_folder
    fit_variables = histograms.keys()
    for variable_bin in variable_bins_ROOT[variable]:
        path = output_folder + str( measurement_config.centre_of_mass_energy ) + 'TeV/' + variable + '/' + category + '/fit_templates/'
        make_folder_if_not_exists( path )
        for fit_variable in fit_variables:
            plotname = path + channel + '_' + fit_variable + '_template_bin_' + variable_bin 
        
            # check if template plots exist already
            for output_format in output_formats:
                if os.path.isfile( plotname + '.' + output_format ):
                    continue
            
            # plot with matplotlib
            h_ttjet = histograms[fit_variable][variable_bin]['TTJet']
            h_single_top = histograms[fit_variable][variable_bin]['SingleTop']
            h_VJets = histograms[fit_variable][variable_bin]['V+Jets']
            h_QCD = histograms[fit_variable][variable_bin]['QCD']
            
            h_ttjet.linecolor = 'red'
            h_single_top.linecolor = 'magenta'
            h_VJets.linecolor = 'green'
            h_QCD.linecolor = 'gray'
            h_VJets.linestyle = 'dashed'
            h_QCD.linestyle = 'dotted'  # currently not working
            # bug report: http://trac.sagemath.org/sage_trac/ticket/13834
            
            h_ttjet.linewidth = 5
            h_single_top.linewidth = 5
            h_VJets.linewidth = 5
            h_QCD.linewidth = 5
        
            plt.figure( figsize = ( 16, 16 ), dpi = 200, facecolor = 'white' )
            axes = plt.axes()
            axes.minorticks_on()
            
            plt.xlabel( fit_variables_latex[fit_variable], CMS.x_axis_title )
            plt.ylabel( 'normalised to unit area/(%s)' % get_unit_string(fit_variable), CMS.y_axis_title )
            plt.tick_params( **CMS.axis_label_major )
            plt.tick_params( **CMS.axis_label_minor )
    
            rplt.hist( h_ttjet, axes = axes, label = 'signal' )
            rplt.hist( h_single_top, axes = axes, label = 'Single Top' )
            
            if ( h_VJets.Integral() != 0 ):
                rplt.hist( h_VJets, axes = axes, label = 'V+Jets' )
            else:
                print "WARNING: in %s bin %s, %s category, %s channel, V+Jets template is empty: not plotting." % ( variable, variable_bin, category, channel )
            if ( h_QCD.Integral() != 0 ):
                rplt.hist( h_QCD, axes = axes, label = 'QCD' )
            else:
                print "WARNING: in %s bin %s, %s category, %s channel, QCD template is empty: not plotting." % ( variable, variable_bin, category, channel )
            y_max = get_best_max_y([h_ttjet, h_single_top, h_VJets, h_QCD])
            axes.set_ylim( [0, y_max * 1.1] )
            axes.set_xlim( measurement_config.fit_boundaries[fit_variable] )
            
            plt.legend( numpoints = 1, loc = 'upper right', prop = CMS.legend_properties )
            label, channel_label = get_cms_labels( channel )
            plt.title( label, CMS.title )
            # CMS text
            # note: fontweight/weight does not change anything as we use Latex text!!!
            plt.text(0.95, 0.95, r"\textbf{CMS}", transform=axes.transAxes, fontsize=42,
                     verticalalignment='top',horizontalalignment='right')
            # channel text
            plt.text(0.95, 0.90, r"\emph{%s}" %channel_label, transform=axes.transAxes, fontsize=42,
                      verticalalignment='top',horizontalalignment='right')
            plt.tight_layout()
        
            for output_format in output_formats:
                plt.savefig( plotname + '.' + output_format )
            
            plt.close()
            gc.collect()


def plot_fit_results( histograms, category, channel ):
    global variable, b_tag_bin, output_folder
    from tools.plotting import Histogram_properties, make_data_mc_comparison_plot
    fit_variables = histograms.keys()
    for variable_bin in variable_bins_ROOT[variable]:
        path = output_folder + str( measurement_config.centre_of_mass_energy ) + 'TeV/' + variable + '/' + category + '/fit_results/'
        make_folder_if_not_exists( path )
        for fit_variable in fit_variables:
            plotname = channel + '_' + fit_variable + '_bin_' + variable_bin
            # check if template plots exist already
            for output_format in output_formats:
                if os.path.isfile( plotname + '.' + output_format ):
                    continue
                
            # plot with matplotlib
            h_data = histograms[fit_variable][variable_bin]['data']
            h_signal = histograms[fit_variable][variable_bin]['signal']
            h_background = histograms[fit_variable][variable_bin]['background']
            
            histogram_properties = Histogram_properties()
            histogram_properties.name = plotname
            histogram_properties.x_axis_title = fit_variables_latex[fit_variable]
            histogram_properties.y_axis_title = 'Events/(%s)' % get_unit_string(fit_variable)
            label, channel_label = get_cms_labels( channel )
            histogram_properties.title = label
            histogram_properties.x_limits = measurement_config.fit_boundaries[fit_variable]
            
            make_data_mc_comparison_plot( [h_data, h_background, h_signal],
                                         ['data', 'background', 'signal'],
                                         ['black', 'green', 'red'], histogram_properties,
                                         save_folder = path, save_as = output_formats )    

def get_cms_labels( channel ):
    global b_tag_bin
    lepton = 'e'
    if channel == 'electron':
        lepton = 'e + jets'
    elif channel == 'muon':
        lepton = '$\mu$ + jets'
    else:
        lepton = 'e, $\mu$ + jets combined'
#     channel_label = '%s, $\geq$ 4 jets, %s' % ( lepton, b_tag_bins_latex[b_tag_bin] )
    channel_label = lepton
    template = '%.1f fb$^{-1}$ (%d TeV)'
    label = template % ( measurement_config.new_luminosity / 1000., measurement_config.centre_of_mass_energy)
    return label, channel_label
    
    
def make_plots( histograms, category, output_folder, histname, show_ratio = True, show_before_unfolding = False ):
    global variable, k_values
    
    channel = 'electron'
    if 'electron' in histname:
        channel = 'electron'
    elif 'muon' in histname:
        channel = 'muon'
    else:
        channel = 'combined'
        
    # plot with matplotlib
    hist_data = histograms['unfolded']
    
    if draw_background_subtraction:
        hist_data_background_subtraction = histograms['unfolded_background_subtraction']

    if category == 'central':
        hist_data_with_systematics = histograms['unfolded_with_systematics']
        if draw_background_subtraction:
            hist_data_with_systematics_background_subtraction = histograms['unfolded_with_systematics_background_subtraction']

    hist_measured = histograms['measured']
    
    hist_data.markersize = 2
    hist_data.marker = 'o'
    
    if draw_background_subtraction:
        # background subtraction data point style 
        hist_data_background_subtraction.markersize = 2
        hist_data_background_subtraction.markerstyle = '^'
        hist_data_background_subtraction.color = 'darkturquoise'

    if category == 'central':
        hist_data_with_systematics.markersize = 2
        hist_data_with_systematics.marker = 'o'
        
        if draw_background_subtraction:
            # background subtraction data point style 
            hist_data_with_systematics_background_subtraction.markersize = 2
            hist_data_with_systematics_background_subtraction.markerstyle = '^'
            hist_data_with_systematics_background_subtraction.color = 'darkturquoise'
    
    hist_measured.markersize = 2
    hist_measured.markerstyle = 'o'
    hist_measured.color = 'red'

    plt.figure( figsize = CMS.figsize, dpi = CMS.dpi, facecolor = CMS.facecolor )
    if show_ratio:
        gs = gridspec.GridSpec( 2, 1, height_ratios = [5, 1] ) 
        axes = plt.subplot( gs[0] )
    else:
        axes = plt.axes()
        plt.xlabel( '$%s$ [GeV]' % variables_latex[variable], CMS.x_axis_title )

    axes.minorticks_on()
    
    plt.ylabel( r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + variables_latex[variable] + '} \left[\mathrm{GeV}^{-1}\\right]$', CMS.y_axis_title )
    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )

    hist_data.visible = True
    if draw_background_subtraction:
        hist_data_background_subtraction.visible = True
        
    if category == 'central':
        hist_data_with_systematics.visible = True
        # first draw data points with full vertical error bars
        if not draw_background_subtraction:
            rplt.errorbar( hist_data_with_systematics, axes = axes, label = 'do_not_show', xerr = None, capsize = 0, elinewidth = 2, zorder = len( histograms ) + 1 )
        elif draw_background_subtraction:
            hist_data_with_systematics_background_subtraction.visible = True
            # first draw data points with full vertical error bars 
            data_histograms_to_plot = [hist_data_with_systematics, hist_data_with_systematics_background_subtraction]
            graphs = spread_x(data_histograms_to_plot, bin_edges[variable])
            for data_histogram_to_plot in graphs:
                rplt.errorbar( data_histogram_to_plot, axes = axes, label = 'do_not_show', xerr = None, capsize = 0, elinewidth = 2, zorder = len(histograms) + 1)

    # now draw data points with only statistical error bars with caps
    if not draw_background_subtraction:
        rplt.errorbar( hist_data, axes = axes, label = 'do_not_show', xerr = None, capsize = 15, capthick = 3, elinewidth = 2, zorder = len( histograms ) + 2 )    
    elif draw_background_subtraction:
        data_histograms_only_stat_error_to_plot = [hist_data, hist_data_background_subtraction]
        graphs = spread_x(data_histograms_only_stat_error_to_plot, bin_edges[variable])
        for data_histogram_only_stat_error_to_plot in graphs:
            rplt.errorbar( data_histogram_only_stat_error_to_plot, axes = axes, label = 'do_not_show', xerr = None, capsize = 15, capthick = 3, elinewidth = 2, zorder = len(histograms) + 2)
        
    # now make the legend entry
    if not draw_background_subtraction:
        rplt.errorbar( hist_data, axes = axes, label = 'data', xerr = None, yerr = False, zorder = len( histograms ) + 3 )  # this makes a nicer legend entry
    elif draw_background_subtraction:
        legend_entries = [hist_data, hist_data_background_subtraction]
        graphs = spread_x(legend_entries, bin_edges[variable])
        rplt.errorbar( graphs[0], axes = axes, label = 'data', xerr = None, yerr = False, zorder = len( histograms ) + 3 )  # this makes a nicer legend entry
        rplt.errorbar( graphs[1], axes = axes, label = 'unfolded data (bkgd subtr.)', xerr = None, yerr = False, zorder = len( histograms ) + 3 )  # this makes a nicer legend entry
        
#     rplt.errorbar( hist_data, axes = axes, label = 'data', xerr = None, yerr = False, zorder = len( histograms ) + 3 )  # this makes a nicer legend entry
#     if draw_background_subtraction:
#         rplt.errorbar( hist_data_background_subtraction, axes = axes, label = 'data (bkgd subtraction)', xerr = None, yerr = False, zorder = len( histograms ) + 3 )

    if show_before_unfolding:
        rplt.errorbar( hist_measured, axes = axes, label = 'data (before unfolding)', xerr = None, zorder = len( histograms ) )
    
    dashes = {}
    for key, hist in sorted( histograms.iteritems() ):
        zorder = sorted( histograms, reverse = False ).index( key )
        if key == 'MADGRAPH' and zorder != len(histograms) - 3:
            zorder = len(histograms) - 3
        elif key != 'MADGRAPH' and not 'unfolded' in key:
            while zorder >= len(histograms) - 3:
                zorder = zorder - 1 

        if not 'unfolded' in key and not 'measured' in key:
            hist.linewidth = 4
            linestyle = None
            # setting colours
            if 'powheg_v2_pythia' in key or 'matchingdown' in key:
                dashes[key] = [25,5,5,5,5,5,5,5]
                hist.SetLineColor( kCyan + 2 )
            elif 'powheg_v1_pythia' in key:
                dashes[key] = [10,5,5,10,5,5]
                hist.SetLineColor( kBlue )
            elif key == 'powheg_v1_herwig'  or 'scaledown' in key:
                dashes[key] = [5,5]
                hist.SetLineColor( kGreen )
            elif 'MADGRAPH_ptreweight' in key:
                dashes[key] = [20,5]
                hist.SetLineColor( kRed + 3 )
            elif 'MADGRAPH' in key:
                linestyle = 'solid'
                dashes[key] = None
                hist.SetLineColor( kRed + 1 )
            elif 'matchingup' in key or 'powheg_v2_herwig' in key:
                dashes[key] = [25,5,5,5,25,5,5,5]
                hist.SetLineColor( kMagenta + 1 )
            elif 'MCATNLO'  in key or 'scaleup' in key:
                dashes[key] = [5,5,10,5]
                hist.linecolor = 'orange'

            if linestyle != None:
                hist.linestyle = linestyle
            line, h = rplt.hist( hist, axes = axes, label = measurements_latex[key], zorder = zorder )
            if dashes[key] != None:
                line.set_dashes(dashes[key])
                h.set_dashes(dashes[key])
    handles, labels = axes.get_legend_handles_labels()
    # making data first in the list
    data_label_index = labels.index( 'data' )
    data_handle = handles[data_label_index]
    labels.remove( 'data' )
    handles.remove( data_handle )
    labels.insert( 0, 'Unfolded data' )
    handles.insert( 0, data_handle )
    
    new_handles, new_labels = [], []
    for handle, label in zip( handles, labels ):
        if not label == 'do_not_show':
            new_handles.append( handle )
            new_labels.append( label )
    
    legend_location = (0.98, 0.88)
    if variable == 'MT':
        legend_location = (0.9, 0.6) # 0.98, 0.88
        CMS.legend_properties['size'] = 27
#     elif variable == 'ST':
#         legend_location = (0.95, 0.88)
    plt.legend( new_handles, new_labels, numpoints = 1, prop = CMS.legend_properties, frameon = False, bbox_to_anchor=legend_location,
                bbox_transform=plt.gcf().transFigure )
    label, channel_label = get_cms_labels( channel )
    # title
    plt.title( label,loc='right', **CMS.title )
    # CMS text
    # note: fontweight/weight does not change anything as we use Latex text!!!
    plt.text(0.05, 0.98, r"\textbf{CMS}", transform=axes.transAxes, fontsize=42,
        verticalalignment='top',horizontalalignment='left')
    # channel text     plt.text(0.95, 0.98
    axes.text(0.95, 0.98, r"%s" %channel_label, transform=axes.transAxes, fontsize=42,
        verticalalignment='top',horizontalalignment='right')

    if show_ratio:
        plt.setp( axes.get_xticklabels(), visible = False )
        ax1 = plt.subplot( gs[1] )
        ax1.minorticks_on()
        #ax1.grid( True, 'major', linewidth = 1 )
        # setting the x_limits identical to the main plot
        x_limits = axes.get_xlim()
        ax1.set_xlim(x_limits)
        ax1.yaxis.set_major_locator( MultipleLocator( 0.5 ) )
        ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )

        plt.xlabel( '$%s$ [GeV]' % variables_latex[variable], CMS.x_axis_title )
        ax1.xaxis.labelpad = 20
        plt.tick_params( **CMS.axis_label_major )
        plt.tick_params( **CMS.axis_label_minor ) 
        plt.ylabel( '$\\frac{\\mathrm{pred.}}{\\mathrm{data}}$', CMS.y_axis_title )
        ax1.yaxis.set_label_coords(-0.115, 0.8)
        #draw a horizontal line at y=1 for data
        plt.axhline(y = 1, color = 'black', linewidth = 2)

        for key, hist in sorted( histograms.iteritems() ):
            if not 'unfolded' in key and not 'measured' in key:
                ratio = hist.Clone()
                ratio.Divide( hist_data ) #divide by data
                line, h = rplt.hist( ratio, axes = ax1, label = 'do_not_show' )
                if dashes[key] != None:
                    line.set_dashes(dashes[key])
                    h.set_dashes(dashes[key])

        stat_lower = hist_data.Clone()
        stat_upper = hist_data.Clone()
        syst_lower = hist_data.Clone()
        syst_upper = hist_data.Clone()

        # plot error bands on data in the ratio plot
        for bin_i in range( 1, hist_data.GetNbinsX() + 1 ):
            stat_errors = graph_to_value_errors_tuplelist(hist_data)
            stat_lower.SetBinContent( bin_i, 1 - stat_errors[bin_i-1][1]/stat_errors[bin_i-1][0] )
            stat_upper.SetBinContent( bin_i, 1 + stat_errors[bin_i-1][2]/stat_errors[bin_i-1][0] )
            if category == 'central':
                syst_errors = graph_to_value_errors_tuplelist(hist_data_with_systematics)
                syst_lower.SetBinContent( bin_i, 1 - syst_errors[bin_i-1][1]/syst_errors[bin_i-1][0] )
                syst_upper.SetBinContent( bin_i, 1 + syst_errors[bin_i-1][2]/syst_errors[bin_i-1][0] )
        if category == 'central':
            rplt.fill_between( syst_lower, syst_upper, ax1,
                               color = 'yellow' )

        rplt.fill_between( stat_upper, stat_lower, ax1, color = '0.75' )
        # legend for ratio plot
        p_stat = mpatches.Patch(facecolor='0.75', label='Stat.', edgecolor='black' )
        p_stat_and_syst = mpatches.Patch(facecolor='yellow', label=r'Stat. $\oplus$ Syst.', edgecolor='black' )

        ratioLegendLocation = 'best'
        if variable == 'MET':
            ax1.set_ylim( ymin = 0.6, ymax = 1.4 )
            # ax1.yaxis.set_major_locator( MultipleLocator( 0.3 ) )
            # ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
            if measurement_config.centre_of_mass_energy == 7:
                ratioLegendLocation = 'upper left'
            elif measurement_config.centre_of_mass_energy == 8:
                ratioLegendLocation = 'upper left'

        if variable == 'MT':
            ax1.set_ylim( ymin = 0.8, ymax = 1.2 )
            # ax1.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            # ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'ST':
            ax1.set_ylim( ymin = 0.6, ymax = 1.4 )
            # ax1.yaxis.set_major_locator( MultipleLocator( 0.3 ) )
            # ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
            if measurement_config.centre_of_mass_energy == 7:
                ratioLegendLocation = 'lower center'
            elif measurement_config.centre_of_mass_energy == 8:
                ratioLegendLocation = 'lower left'
        elif variable == 'HT':
            ax1.set_ylim( ymin = 0.6, ymax = 1.4 )
            # ax1.yaxis.set_major_locator( MultipleLocator( 0.3 ) )
            # ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
            if measurement_config.centre_of_mass_energy == 7:
                ratioLegendLocation = 'lower center'
            elif measurement_config.centre_of_mass_energy == 8:
                ratioLegendLocation = 'upper left'
        elif variable == 'WPT':
            ax1.set_ylim( ymin = 0.6, ymax = 1.4 )
            # ax1.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            # ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
            if measurement_config.centre_of_mass_energy == 7:
                ratioLegendLocation = 'upper left'
            elif measurement_config.centre_of_mass_energy == 8:
                ratioLegendLocation = 'upper left'
        adjust_ratio_ticks(ax1.yaxis, n_ticks = 3, y_limits = ax1.get_ylim() )

        l1 = ax1.legend(handles = [p_stat, p_stat_and_syst], loc = ratioLegendLocation,
                     frameon = False, prop = {'size':26}, ncol = 2)
        ax1.add_artist(l1)

    if CMS.tight_layout:
        plt.tight_layout()

    path = output_folder + str( measurement_config.centre_of_mass_energy ) + 'TeV/' + variable + '/' + category
    if draw_background_subtraction:
        histname = histname + '_with_bkgd_subtraction_results'
    make_folder_if_not_exists( path )
    for output_format in output_formats:
        filename = path + '/' + histname + '_kv' + str( k_values[channel] ) + '.' + output_format
        if channel == 'combined':
            filename = filename.replace( '_kv' + str( k_values[channel] ), '' )
        plt.savefig( filename )

    del hist_data, hist_measured
    plt.close()
    gc.collect()

def plot_central_and_systematics( channel, systematics, exclude = [], suffix = 'altogether' ):
    global variable, k_values, b_tag_bin, met_type

    plt.figure( figsize = ( 16, 16 ), dpi = 200, facecolor = 'white' )
    axes = plt.axes()
    axes.minorticks_on()
    
    hist_data_central = read_xsection_measurement_results( 'central', channel )[0]['unfolded_with_systematics']
    hist_data_central.markersize = 2  # points. Imagine, tangible units!
    hist_data_central.marker = 'o'
    
    
    plt.xlabel( '$%s$ [GeV]' % variables_latex[variable], CMS.x_axis_title )
    plt.ylabel( r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + variables_latex[variable] + '} \left[\mathrm{GeV}^{-1}\\right]$', CMS.y_axis_title )
    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )

    rplt.errorbar( hist_data_central, axes = axes, label = 'data', xerr = True )

    for systematic in sorted( systematics ):
        if systematic in exclude or systematic == 'central':
            continue

        hist_data_systematic = read_xsection_measurement_results( systematic, channel )[0]['unfolded']
        hist_data_systematic.markersize = 2
        hist_data_systematic.marker = 'o'
        colour_number = systematics.index( systematic ) + 2
        if colour_number == 10:
            colour_number = 42
        hist_data_systematic.SetMarkerColor( colour_number )
        if 'PDF' in systematic:
            rplt.errorbar( hist_data_systematic, axes = axes, label = systematic.replace( 'Weights_', ' ' ), xerr = None )
        elif met_type in systematic:
            rplt.errorbar( hist_data_systematic, axes = axes, label = met_systematics_latex[systematic.replace( met_type, '' )], xerr = None )
        else:
            rplt.errorbar( hist_data_systematic, axes = axes, label = measurements_latex[systematic], xerr = None )
            
    plt.legend( numpoints = 1, loc = 'center right', prop = {'size':25}, ncol = 2 )
    label, channel_label = get_cms_labels( channel )
    plt.title( label, CMS.title )
    # CMS text
    # note: fontweight/weight does not change anything as we use Latex text!!!
    plt.text(0.95, 0.95, r"\textbf{CMS}", transform=axes.transAxes, fontsize=42,
        verticalalignment='top',horizontalalignment='right')
    # channel text
    plt.text(0.95, 0.90, r"\emph{%s}" %channel_label, transform=axes.transAxes, fontsize=42,
        verticalalignment='top',horizontalalignment='right')
    plt.tight_layout()

    
    path = output_folder + str( measurement_config.centre_of_mass_energy ) + 'TeV/' + variable
    make_folder_if_not_exists( path )
    for output_format in output_formats:
        filename = path + '/normalised_xsection_' + channel + '_' + suffix + '_kv' + str( k_values[channel] ) + '.' + output_format
        if channel == 'combined':
            filename = filename.replace( '_kv' + str( k_values[channel] ), '' )
        plt.savefig( filename ) 

    plt.close()
    gc.collect()

def get_unit_string(fit_variable):
    unit = measurement_config.fit_variable_unit[fit_variable]
    fit_variable_bin_width = measurement_config.fit_variable_bin_width[fit_variable]
    unit_string = ''
    if unit == '':
        unit_string = fit_variable_bin_width
    else:
        unit_string = '%f %s' % (fit_variable_bin_width, unit)
        
    return unit_string

if __name__ == '__main__':
    set_root_defaults()
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data/',
                  help = "set path to JSON files" )
    parser.add_option( "-o", "--output_folder", dest = "output_folder", default = 'plots/',
                  help = "set path to save plots" )
    parser.add_option( "-v", "--variable", dest = "variable", default = 'MET',
                  help = "set variable to plot (MET, HT, ST, MT)" )
    parser.add_option( "-m", "--metType", dest = "metType", default = 'type1',
                      help = "set MET type used in the analysis of MET, ST or MT" )
    parser.add_option( "-b", "--bjetbin", dest = "bjetbin", default = '2m',
                  help = "set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m" )
    parser.add_option( "-c", "--centre-of-mass-energy", dest = "CoM", default = 8, type = int,
                      help = "set the centre of mass energy for analysis. Default = 8 [TeV]" )
    parser.add_option( "-a", "--additional-plots", action = "store_true", dest = "additional_plots",
                      help = """Draws additional plots like the comparison of different 
                      systematics to the central result.""" )
    parser.add_option("--draw-systematics", action = "store_true", dest = "draw_systematics",
                      help = "creates a set of plots for each systematic (in addition to central result)." )
    parser.add_option("-s", "--draw-background-subtraction", action = "store_true", dest = "draw_background_subtraction", 
                      default = False, help = "draw the central data points from background subtraction method on results plots.")
    
    output_formats = ['png', 'pdf']
    ( options, args ) = parser.parse_args()
    
    measurement_config = XSectionConfig( options.CoM )
    # caching of variables for shorter access
    translate_options = measurement_config.translate_options
    ttbar_theory_systematic_prefix = measurement_config.ttbar_theory_systematic_prefix
    vjets_theory_systematic_prefix = measurement_config.vjets_theory_systematic_prefix
    met_systematics_suffixes = measurement_config.met_systematics_suffixes
    
    variable = options.variable
    output_folder = options.output_folder
    if not output_folder.endswith( '/' ):
        output_folder += '/'
    k_values = {'electron' : measurement_config.k_values_electron[variable],
                'muon' : measurement_config.k_values_muon[variable],
                'combined' : 'None'
                }
    met_type = translate_options[options.metType]
    b_tag_bin = translate_options[options.bjetbin]
    path_to_JSON = options.path + '/' + str( measurement_config.centre_of_mass_energy ) + 'TeV/' + variable + '/'

    draw_background_subtraction = options.draw_background_subtraction
    if draw_background_subtraction:
        path_to_JSON_background_subtraction = path_to_JSON.replace("absolute_eta_M3_angle_bl", "normalisation/background_subtraction")
    
    categories = deepcopy( measurement_config.categories_and_prefixes.keys() )
    ttbar_generator_systematics = [ttbar_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    vjets_generator_systematics = [vjets_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    categories.extend( ttbar_generator_systematics )
    categories.extend( vjets_generator_systematics )

    # Add mass systematics
    ttbar_mass_systematics = measurement_config.topMass_systematics
    categories.extend( measurement_config.topMass_systematics )

    # Add k value systematic
    kValue_systematics = measurement_config.kValueSystematic
    categories.extend( measurement_config.kValueSystematic )
    
    pdf_uncertainties = ['PDFWeights_%d' % index for index in range( 1, 45 )]
    pdf_uncertainties_1_to_11 = ['PDFWeights_%d' % index for index in range( 1, 12 )]
    pdf_uncertainties_12_to_22 = ['PDFWeights_%d' % index for index in range( 12, 23 )]
    pdf_uncertainties_23_to_33 = ['PDFWeights_%d' % index for index in range( 23, 34 )]
    pdf_uncertainties_34_to_45 = ['PDFWeights_%d' % index for index in range( 34, 45 )]
    # all MET uncertainties except JES as this is already included
    met_uncertainties = [met_type + suffix for suffix in met_systematics_suffixes if not 'JetEn' in suffix and not 'JetRes' in suffix]
    new_uncertainties = ['QCD_shape']
    rate_changing_systematics = [systematic + '+' for systematic in measurement_config.rate_changing_systematics.keys()]
    rate_changing_systematics.extend( [systematic + '-' for systematic in measurement_config.rate_changing_systematics.keys()] )

    all_measurements = deepcopy( categories )
    all_measurements.extend( pdf_uncertainties )
    all_measurements.extend( met_uncertainties )
    all_measurements.extend( new_uncertainties )
    all_measurements.extend( rate_changing_systematics )
    # for channel in ['electron', 'muon', 'combined']:
    for channel in ['combined']:
        for category in all_measurements:
            if not category == 'central' and not options.draw_systematics:
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
            
            if not channel == 'combined' and options.additional_plots:
                #Don't make additional plots for e.g. generator systematics, mass systematics, k value systematics and pdf systematics because they are now done \
                #in the unfolding process with BLT unfolding files.
                if category in ttbar_generator_systematics or category in ttbar_mass_systematics or category in kValue_systematics or category in pdf_uncertainties:
                    continue
                fit_templates, fit_results = read_fit_templates_and_results_as_histograms( category, channel )
                make_template_plots( fit_templates, category, channel )
                plot_fit_results( fit_results, category, channel )

            # change back to original MET type
            met_type = translate_options[options.metType]
            if met_type == 'PFMET':
                met_type = 'patMETsPFlow'
            
            histograms_normalised_xsection_different_generators, histograms_normalised_xsection_systematics_shifts = read_xsection_measurement_results( category, channel )
            make_plots( histograms_normalised_xsection_different_generators, category, output_folder, 'normalised_xsection_' + channel + '_different_generators' )
            make_plots( histograms_normalised_xsection_systematics_shifts, category, output_folder, 'normalised_xsection_' + channel + '_systematics_shifts' )

            del histograms_normalised_xsection_different_generators, histograms_normalised_xsection_systematics_shifts
    
        if options.additional_plots:
            plot_central_and_systematics( channel, categories, exclude = ttbar_generator_systematics )
            
            plot_central_and_systematics( channel, ttbar_generator_systematics, suffix = 'ttbar_generator_only' )
              
            exclude = set( pdf_uncertainties ).difference( set( pdf_uncertainties_1_to_11 ) )
            plot_central_and_systematics( channel, pdf_uncertainties_1_to_11, exclude = exclude, suffix = 'PDF_1_to_11' )
              
            exclude = set( pdf_uncertainties ).difference( set( pdf_uncertainties_12_to_22 ) )
            plot_central_and_systematics( channel, pdf_uncertainties_12_to_22, exclude = exclude, suffix = 'PDF_12_to_22' )
              
            exclude = set( pdf_uncertainties ).difference( set( pdf_uncertainties_23_to_33 ) )
            plot_central_and_systematics( channel, pdf_uncertainties_23_to_33, exclude = exclude, suffix = 'PDF_23_to_33' )
              
            exclude = set( pdf_uncertainties ).difference( set( pdf_uncertainties_34_to_45 ) )
            plot_central_and_systematics( channel, pdf_uncertainties_34_to_45, exclude = exclude, suffix = 'PDF_34_to_45' )
              
            plot_central_and_systematics( channel, met_uncertainties, suffix = 'MET_only' )
            plot_central_and_systematics( channel, new_uncertainties, suffix = 'new_only' )
            plot_central_and_systematics( channel, rate_changing_systematics, suffix = 'rate_changing_only' )
