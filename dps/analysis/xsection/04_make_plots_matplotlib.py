# the result of the division will be always a float
from __future__ import division, print_function
from argparse import ArgumentParser
import os, gc
from copy import deepcopy

from dps.config.latex_labels import variables_latex, measurements_latex
from dps.config.variable_binning import bin_edges_full, bin_edges_vis
from dps.config.xsection import XSectionConfig
from dps.utils.file_utilities import make_folder_if_not_exists
from dps.utils.pandas_utilities import read_tuple_from_file, file_to_df, tupleise_cols
from dps.utils.hist_utilities import value_error_tuplelist_to_hist, \
value_tuplelist_to_hist, value_errors_tuplelist_to_graph, graph_to_value_errors_tuplelist
from math import sqrt
# rootpy & matplotlib
from ROOT import kRed, kGreen, kMagenta, kBlue, kBlack
from dps.utils.ROOT_utils import set_root_defaults
import matplotlib as mpl
from matplotlib import rc

mpl.use( 'agg' )
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator
from dps.config import CMS
from dps.utils.latex import setup_matplotlib
# latex, font, etc
setup_matplotlib()

import matplotlib.patches as mpatches
import latexcodec

from dps.utils.logger import log
xsec_04_log = log["src/cross_section_measurement/04_make_plots_matplotlib"]

@xsec_04_log.trace()
def read_xsection_measurement_results( category, channel ):
    global path_to_DF, variable, met_type, phase_space, method

    file_template = 'TESTING/{path}/{category}/{name}_{channel}_{method}{suffix}.txt'
    filename = file_template.format(
                path = path_to_DF,
                category = category,
                name = 'xsection_normalised',
                channel = channel,
                method = method,
                suffix = '',
                )

    xsec_04_log.debug('Reading file {0}'.format(filename))
    normalised_xsection_unfolded = read_tuple_from_file( filename )
    edges = bin_edges_full[variable]
    if phase_space == 'VisiblePS':
        edges = bin_edges_vis[variable]

    h_normalised_xsection = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJet_measured'], edges )
    h_normalised_xsection_unfolded = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJet_unfolded'], edges )

    histograms_normalised_xsection_different_generators = {'measured':h_normalised_xsection,
                                                           'unfolded':h_normalised_xsection_unfolded}

    histograms_normalised_xsection_systematics_shifts = {'measured':h_normalised_xsection,
                                                         'unfolded':h_normalised_xsection_unfolded}

    if category == 'central':
        # true distributions
        h_normalised_xsection_powhegPythia8     = value_error_tuplelist_to_hist( normalised_xsection_unfolded['powhegPythia8'], edges )
        h_normalised_xsection_amcatnlo          = value_error_tuplelist_to_hist( normalised_xsection_unfolded['amcatnlo'], edges )
        h_normalised_xsection_madgraphMLM       = value_error_tuplelist_to_hist( normalised_xsection_unfolded['madgraphMLM'], edges )
        h_normalised_xsection_powhegHerwigpp    = value_error_tuplelist_to_hist( normalised_xsection_unfolded['powhegHerwig'], edges )
        # h_normalised_xsection_amcatnloHerwigpp = value_error_tuplelist_to_hist( normalised_xsection_unfolded['amcatnloHerwig'], edges )

        # h_normalised_xsection_scaleup         = value_error_tuplelist_to_hist( normalised_xsection_unfolded['scaleup'], edges )
        # h_normalised_xsection_scaledown       = value_error_tuplelist_to_hist( normalised_xsection_unfolded['scaledown'], edges )
        h_normalised_xsection_massup            = value_error_tuplelist_to_hist( normalised_xsection_unfolded['massup'], edges )
        h_normalised_xsection_massdown          = value_error_tuplelist_to_hist( normalised_xsection_unfolded['massdown'], edges )

        histograms_normalised_xsection_different_generators.update( 
            {
                'powhegPythia8':h_normalised_xsection_powhegPythia8,
                'amcatnloPythia8':h_normalised_xsection_amcatnlo,
                'madgraphMLM':h_normalised_xsection_madgraphMLM,
                'powhegHerwig':h_normalised_xsection_powhegHerwigpp,
                # 'amcatnloHerwig':h_normalised_xsection_amcatnloHerwigpp,
            }
        )

        histograms_normalised_xsection_systematics_shifts.update( 
            {
                'powhegPythia8':h_normalised_xsection_powhegPythia8,
                # 'scaledown': h_normalised_xsection_scaledown,
                # 'scaleup': h_normalised_xsection_scaleup,
                'massdown': h_normalised_xsection_massdown,
                'massup': h_normalised_xsection_massup
            }
        )

        filename = file_template.format(
            path = path_to_DF,
            category = category,
            name = 'xsection_normalised',
            channel = channel,
            method = method,
            suffix = '_summary_absolute',
        )

        normalised_xsection_unfolded_with_errors = file_to_df( filename )
        normalised_xsection_unfolded_with_errors['TTJet_unfolded'] = tupleise_cols(
            normalised_xsection_unfolded_with_errors['central'], 
            normalised_xsection_unfolded_with_errors['systematic'],
        )
        print(normalised_xsection_unfolded_with_errors['TTJet_unfolded'])



        xsec_04_log.debug('Reading file {0}'.format(filename))
#         filename = file_template.format(
#                 path = path_to_DF,
#                 category = category,
#                 name = 'normalised_xsection',
#                 channel = channel,
#                 method = method,
#                 suffix = '_with_systematics_but_without_generator_errors',
#                 )
        ### normalised_xsection_unfolded_with_errors_with_systematics_but_without_ttbar_theory = read_tuple_from_file( file_template + '_with_systematics_but_without_ttbar_theory_errors.txt' )
#         normalised_xsection_unfolded_with_errors_with_systematics_but_without_generator = normalised_xsection_unfolded_with_errors

        # a rootpy.Graph with asymmetric errors!
        ### h_normalised_xsection_with_systematics_but_without_ttbar_theory = value_errors_tuplelist_to_graph(
        ###                                                         normalised_xsection_unfolded_with_errors_with_systematics_but_without_ttbar_theory['TTJet_measured'],
        ###                                                         edges )
        ### h_normalised_xsection_with_systematics_but_without_ttbar_theory_unfolded = value_errors_tuplelist_to_graph(
        ###                                                         normalised_xsection_unfolded_with_errors_with_systematics_but_without_ttbar_theory['TTJet_unfolded'],
        ###                                                         edges )

        # h_normalised_xsection_unfolded_with_errors = value_errors_tuplelist_to_graph(
        #                                                         normalised_xsection_unfolded_with_errors['TTJet_measured'],
        #                                                         edges )
        h_normalised_xsection_unfolded_with_errors_unfolded = value_errors_tuplelist_to_graph(
            normalised_xsection_unfolded_with_errors['TTJet_unfolded'],
            edges, 
            is_symmetric_errors=True
        )


        # histograms_normalised_xsection_different_generators['measured_with_systematics'] = h_normalised_xsection_with_systematics_but_without_ttbar_theory
        # histograms_normalised_xsection_different_generators['unfolded_with_systematics'] = h_normalised_xsection_with_systematics_but_without_ttbar_theory_unfolded
        # histograms_normalised_xsection_different_generators['measured_with_systematics'] = h_normalised_xsection_unfolded_with_errors
        histograms_normalised_xsection_different_generators['unfolded_with_systematics'] = h_normalised_xsection_unfolded_with_errors_unfolded

        # histograms_normalised_xsection_systematics_shifts['measured_with_systematics'] = h_normalised_xsection_unfolded_with_errors
        histograms_normalised_xsection_systematics_shifts['unfolded_with_systematics'] = h_normalised_xsection_unfolded_with_errors_unfolded

    return histograms_normalised_xsection_different_generators, histograms_normalised_xsection_systematics_shifts

@xsec_04_log.trace()
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
    label = template % ( measurement_config.new_luminosity/1000, measurement_config.centre_of_mass_energy)
    return label, channel_label

@xsec_04_log.trace()
def make_plots( histograms, category, output_folder, histname, show_ratio = True, show_generator_ratio = False, show_before_unfolding = False ):
    global variable, phase_space

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

    plt.figure( figsize = CMS.figsize, dpi = CMS.dpi, facecolor = CMS.facecolor )

    if show_ratio and show_generator_ratio:
        gs = gridspec.GridSpec( 3, 1, height_ratios = [5, 1, 1] )
        axes = plt.subplot( gs[0] )
    elif show_ratio or show_generator_ratio:
        gs = gridspec.GridSpec( 2, 1, height_ratios = [5, 1] )
        axes = plt.subplot( gs[0] )
    else:
        axes = plt.axes()
        if variable in ['NJets', 'abs_lepton_eta', 'lepton_eta']:
            plt.xlabel( '$%s$' % variables_latex[variable], CMS.x_axis_title )
        else:
            plt.xlabel( '$%s$ [GeV]' % variables_latex[variable], CMS.x_axis_title )

    if not variable in ['NJets']:
        axes.minorticks_on()
    if variable in ['NJets', 'abs_lepton_eta', 'lepton_eta']:
        plt.ylabel( r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + variables_latex[variable] + '}$', CMS.y_axis_title )
    else:
        plt.ylabel( r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + variables_latex[variable] + '} \left[\mathrm{GeV}^{-1}\\right]$', CMS.y_axis_title )
    plt.tick_params( **CMS.axis_label_major )
    if not variable in ['NJets']:
        plt.tick_params( **CMS.axis_label_minor )

    hist_data.visible = True

    if category == 'central':
        hist_data_with_systematics.visible = True
        rplt.errorbar( hist_data_with_systematics, axes = axes, label = 'do_not_show', xerr = None, capsize = 0, elinewidth = 2, zorder = len( histograms ) + 1 )
    rplt.errorbar( hist_data, axes = axes, label = 'do_not_show', xerr = None, capsize = 15, capthick = 3, elinewidth = 2, zorder = len( histograms ) + 2 )
    rplt.errorbar( hist_data, axes = axes, label = 'data', xerr = None, yerr = False, zorder = len( histograms ) + 3 )  # this makes a nicer legend entry

    if show_before_unfolding:
        rplt.errorbar( hist_measured, axes = axes, label = 'data (before unfolding)', xerr = None, zorder = len( histograms ) )

    dashes = {}
    for key, hist in sorted( histograms.items() ):
        zorder = sorted( histograms, reverse = False ).index( key )
        print (key)
        if key == 'powhegPythia8' and zorder != len(histograms) - 3:
            zorder = len(histograms) - 3
        elif key != 'powhegPythia8' and not 'unfolded' in key:
            while zorder >= len(histograms) - 3:
                zorder = zorder - 1 

        if not 'unfolded' in key and not 'measured' in key:
            hist.linewidth = 4
            # setting colours
            linestyle = None
            if 'powhegHerwig' in key or 'massdown' in key:
                hist.SetLineColor( kBlue )
                dashes[key] = [25,5,5,5,5,5,5,5]
            elif 'madgraphMLM' in key or 'scaledown' in key:
                hist.SetLineColor( 417 )
                dashes[key] = [5,5]
            elif 'MADGRAPH_ptreweight' in key:
                hist.SetLineColor( kBlack )
            elif 'powhegPythia8' in key:
                linestyle = 'solid'
                dashes[key] = None
                hist.SetLineColor( 633 )
            elif 'amcatnloPythia8' in key or 'massup' in key:
                hist.SetLineColor( 807 )
                dashes[key] = [20,5]
            # elif 'amcatnloHerwig' in key:
            #     hist.SetLineColor( 734 )
            #     dashes[key] = [15,5]
            elif 'MCATNLO' in key or 'scaleup' in key:
                hist.SetLineColor( 619 )
                dashes[key] = [5,5,10,5]

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
    labels.insert( 0, 'data' )
    handles.insert( 0, data_handle )

    new_handles, new_labels = [], []
    zipped = dict( zip( labels, handles ) )
    labelOrder = ['data', 
        measurements_latex['powhegPythia8'],
        measurements_latex['amcatnloPythia8'],
        measurements_latex['powhegHerwig'],
        measurements_latex['amcatnloHerwig'],
        measurements_latex['madgraphMLM'],
        measurements_latex['scaleup'], 
        measurements_latex['scaledown'],
        measurements_latex['massup'],
        measurements_latex['massdown']
    ]
    for label in labelOrder:
        if label in labels:
            new_handles.append(zipped[label])
            new_labels.append(label)

    legend_location = (0.97, 0.82)
    if variable == 'MT':
        legend_location = (0.05, 0.82)
    elif variable == 'ST':
        legend_location = (0.97, 0.82)
    elif variable == 'WPT':
        legend_location = (1.0, 0.84)
    elif variable == 'abs_lepton_eta':
        legend_location = (1.0, 0.94)
    plt.legend( new_handles, new_labels, numpoints = 1, prop = CMS.legend_properties, frameon = False, bbox_to_anchor=legend_location,
                bbox_transform=plt.gcf().transFigure )
    label, channel_label = get_cms_labels( channel )
    # title
    plt.title( label,loc='right', **CMS.title )
    # CMS text
    # note: fontweight/weight does not change anything as we use Latex text!!!
    logo_location = (0.05, 0.98)
    prelim_location = (0.05, 0.92)
    channel_location = ( 0.05, 0.86)
    if variable == 'WPT':
        logo_location = (0.03, 0.98)
        prelim_location = (0.03, 0.92)
        channel_location = (0.03, 0.86)
    elif variable == 'abs_lepton_eta':
        logo_location = (0.03, 0.98)
        prelim_location = (0.03, 0.92)
        channel_location = (0.03, 0.86)
    plt.text(logo_location[0], logo_location[1], r"\textbf{CMS}", transform=axes.transAxes, fontsize=42,
        verticalalignment='top',horizontalalignment='left')
    # preliminary
    plt.text(prelim_location[0], prelim_location[1], r"\emph{Preliminary}",
                 transform=axes.transAxes, fontsize=42,
                 verticalalignment='top',horizontalalignment='left')
    # channel text
    plt.text(channel_location[0], channel_location[1], r"\emph{%s}" %channel_label, transform=axes.transAxes, fontsize=40,
        verticalalignment='top',horizontalalignment='left')
    ylim = axes.get_ylim()
    if ylim[0] < 0:
        axes.set_ylim( ymin = 0.)
    if variable == 'WPT':
        axes.set_ylim(ymax = ylim[1]*1.3)
    elif variable == 'abs_lepton_eta':
        axes.set_ylim(ymax = ylim[1]*1.3)
    else :
        axes.set_ylim(ymax = ylim[1]*1.2)


    if show_ratio or show_generator_ratio:
        plt.setp( axes.get_xticklabels(), visible = False )
        ax1 = plt.subplot( gs[1] )
        if not variable in ['NJets']:
            ax1.minorticks_on()
        #ax1.grid( True, 'major', linewidth = 1 )
        # setting the x_limits identical to the main plot
        x_limits = axes.get_xlim()
        ax1.set_xlim(x_limits)
        ax1.yaxis.set_major_locator( MultipleLocator( 0.5 ) )
        if not variable in ['NJets']:
            ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )

        if not show_ratio or not show_generator_ratio:
            if variable in ['NJets', 'abs_lepton_eta', 'lepton_eta']:
                plt.xlabel('$%s$' % variables_latex[variable], CMS.x_axis_title )
            else:
                plt.xlabel( '$%s$ [GeV]' % variables_latex[variable], CMS.x_axis_title )

        plt.tick_params( **CMS.axis_label_major )
        if not variable in ['NJets']:
            plt.tick_params( **CMS.axis_label_minor )
        plt.ylabel( '$\\frac{\\textrm{pred.}}{\\textrm{data}}$', CMS.y_axis_title )
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
        stat_errors = graph_to_value_errors_tuplelist(hist_data)
        if category == 'central':
            syst_errors = graph_to_value_errors_tuplelist(hist_data_with_systematics)
        for bin_i in range( 1, hist_data.GetNbinsX() + 1 ):
            stat_value, stat_error, _ = stat_errors[bin_i-1]
            stat_rel_error = stat_error/stat_value
            stat_lower.SetBinContent( bin_i, 1 - stat_rel_error )
            stat_upper.SetBinContent( bin_i, 1 + stat_rel_error )
            if category == 'central':
                syst_value, syst_error_down, syst_error_up  = syst_errors[bin_i-1]
                syst_rel_error_down = syst_error_down/syst_value
                syst_rel_error_up = syst_error_up/syst_value
                syst_lower.SetBinContent( bin_i, 1 - syst_rel_error_down )
                syst_upper.SetBinContent( bin_i, 1 + syst_rel_error_up )
        if category == 'central':
            rplt.fill_between( syst_lower, syst_upper, ax1,
                               color = 'yellow' )

        rplt.fill_between( stat_upper, stat_lower, ax1, color = '0.75',
                            )

        loc = 'upper left'
        # if variable in ['ST']:
        #     loc = 'upper right'
        # legend for ratio plot
        p_stat = mpatches.Patch(facecolor='0.75', label='Stat.', edgecolor='black' )
        p_stat_and_syst = mpatches.Patch(facecolor='yellow', label=r'Stat. $\oplus$ Syst.', edgecolor='black' )
        l1 = ax1.legend(handles = [p_stat, p_stat_and_syst], loc = loc,
                     frameon = False, prop = {'size':26}, ncol = 2)

        # ax1.legend(handles = [p_stat_and_syst], loc = 'lower left',
        #              frameon = False, prop = {'size':30})
        ax1.add_artist(l1)

        if variable == 'MET':
            ax1.set_ylim( ymin = 0.8, ymax = 1.2 )
            ax1.yaxis.set_major_locator( MultipleLocator( 0.5 ) )
#             ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        if variable == 'MT':
            ax1.set_ylim( ymin = 0.8, ymax = 1.2 )
            ax1.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'HT':
            ax1.set_ylim( ymin = 0.8, ymax = 1.37 )
            ax1.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'ST':
            ax1.set_ylim( ymin = 0.7, ymax = 1.5 )
            ax1.yaxis.set_major_locator( MultipleLocator( 0.5 ) )
            ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'WPT':
            ax1.set_ylim( ymin = 0.8, ymax = 1.2 )
            ax1.yaxis.set_major_locator( MultipleLocator( 0.5 ) )
            ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'NJets':
            ax1.set_ylim( ymin = 0.7, ymax = 1.5 )
        elif variable == 'abs_lepton_eta':
            ax1.set_ylim( ymin = 0.8, ymax = 1.2 )
            ax1.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'lepton_pt':
            ax1.set_ylim( ymin = 0.8, ymax = 1.3 )
            ax1.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )


    if show_ratio and show_generator_ratio:

        plt.setp( axes.get_xticklabels(), visible = False ) #Remove DataMC Comparision Axis
        plt.setp( ax1.get_xticklabels(), visible = False ) # Remove Ratio Axis

        ax2 = plt.subplot( gs[2] )
        if not variable in ['NJets']:
            ax2.minorticks_on()
        #ax2.grid( True, 'major', linewidth = 1 )
        # setting the x_limits identical to the main plot
        x_limits = axes.get_xlim()
        ax2.set_xlim(x_limits)

        ax2.yaxis.set_major_locator( MultipleLocator( 0.5 ) )
        if not variable in ['NJets']:
            ax2.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )

        if variable in ['NJets', 'abs_lepton_eta', 'lepton_eta']:
            plt.xlabel('$%s$' % variables_latex[variable], CMS.x_axis_title )
        else:
            plt.xlabel( '$%s$ [GeV]' % variables_latex[variable], CMS.x_axis_title )

        plt.tick_params( **CMS.axis_label_major )
        if not variable in ['NJets']:
            plt.tick_params( **CMS.axis_label_minor )
        plt.ylabel( '$\\frac{\\textrm{generator}}{\\textrm{central}}$', CMS.y_axis_title )
        ax2.yaxis.set_label_coords(-0.115, 0.8)
        #draw a horizontal line at y=1 for data
        plt.axhline(y = 1, color = 'black', linewidth = 2)

        central_mc = histograms['powhegPythia8']
        for key, hist in sorted( histograms.iteritems() ):
            if not 'unfolded' in key and not 'measured' in key:
                ratio = hist.Clone()
                ratio.Divide( central_mc ) #divide by data
                line, h = rplt.hist( ratio, axes = ax2, label = 'do_not_show' )
                if dashes[key] != None:
                    line.set_dashes(dashes[key])
                    h.set_dashes(dashes[key])

        if variable == 'MET':
            ax2.set_ylim( ymin = 0.8, ymax = 1.2 )
            ax2.yaxis.set_major_locator( MultipleLocator( 0.5 ) )
#             ax2.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        if variable == 'MT':
            ax2.set_ylim( ymin = 0.8, ymax = 1.2 )
            ax2.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax2.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'HT':
            ax2.set_ylim( ymin = 0.8, ymax = 1.37 )
            ax2.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax2.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'ST':
            ax2.set_ylim( ymin = 0.7, ymax = 1.5 )
            ax2.yaxis.set_major_locator( MultipleLocator( 0.5 ) )
            ax2.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'WPT':
            ax2.set_ylim( ymin = 0.8, ymax = 1.2 )
            ax2.yaxis.set_major_locator( MultipleLocator( 0.5 ) )
            ax2.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'NJets':
            ax2.set_ylim( ymin = 0.7, ymax = 1.5 )
        elif variable == 'abs_lepton_eta':
            ax2.set_ylim( ymin = 0.8, ymax = 1.2 )
            ax2.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax2.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'lepton_pt':
            ax2.set_ylim( ymin = 0.8, ymax = 1.3 )
            ax2.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax2.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )



    if CMS.tight_layout:
        plt.tight_layout()

    path = '{output_folder}/{centre_of_mass_energy}TeV/{phaseSpace}/{variable}/'
    path = path.format(
            output_folder = output_folder,
            centre_of_mass_energy = measurement_config.centre_of_mass_energy,
            phaseSpace = phase_space,
            variable = variable
            )
    make_folder_if_not_exists( path )
    for output_format in output_formats:
        filename = path + '/' + histname + '.' + output_format
        plt.savefig( filename )

    del hist_data, hist_measured
    plt.close()
    gc.collect()

@xsec_04_log.trace()
def plot_central_and_systematics( channel, systematics, exclude = [], suffix = 'altogether' ):
    global variable, b_tag_bin, met_type

    plt.figure( figsize = ( 16, 16 ), dpi = 200, facecolor = 'white' )
    axes = plt.axes()
    if not variable in ['NJets']:
        axes.minorticks_on()

    hist_data_central = read_xsection_measurement_results( 'central', channel )[0]['unfolded_with_systematics']
    hist_data_central.markersize = 2  # points. Imagine, tangible units!
    hist_data_central.marker = 'o'

    if variable in ['NJets', 'abs_lepton_eta', 'lepton_eta']:
        plt.xlabel( '$%s$' % variables_latex[variable], CMS.x_axis_title )
        plt.ylabel( r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + variables_latex[variable] + '}$', CMS.y_axis_title )
    else:
        plt.xlabel( '$%s$ [GeV]' % variables_latex[variable], CMS.x_axis_title )
        plt.ylabel( r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + variables_latex[variable] + '} \left[\mathrm{GeV}^{-1}\\right]$', CMS.y_axis_title )
    plt.tick_params( **CMS.axis_label_major )
    if not variable in ['NJets']:
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
            rplt.errorbar( hist_data_systematic, axes = axes, label = measurements_latex[systematic.replace( met_type, '' )], xerr = None )
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
    axes.text(0.95, 0.90, r"\emph{%s}" %channel_label, transform=axes.transAxes, fontsize=40,
        verticalalignment='top',horizontalalignment='right')
    plt.tight_layout()


    path = output_folder + str( measurement_config.centre_of_mass_energy ) + 'TeV/' + variable
    make_folder_if_not_exists( path )
    for output_format in output_formats:
        filename = path + '/normalised_xsection_' + channel + '_' + suffix + '.' + output_format

        plt.savefig( filename )

    plt.close()
    gc.collect()

@xsec_04_log.trace()
def get_unit_string(fit_variable):
    unit = measurement_config.fit_variable_unit[fit_variable]
    fit_variable_bin_width = measurement_config.fit_variable_bin_width[fit_variable]
    unit_string = ''
    if unit == '':
        unit_string = fit_variable_bin_width
    else:
        unit_string = '%f %s' % (fit_variable_bin_width, unit)

    return unit_string


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument( "-p", "--path", 
        dest    = "path", 
        default = 'data/normalisation/background_subtraction/',
        help    = "set path to files containing dataframes" 
    )
    parser.add_argument( "-o", "--output_folder", 
        dest    = "output_folder", 
        default = 'plots/',
        help    = "set path to save plots" 
    )
    parser.add_argument( "-v", "--variable", 
        dest    = "variable", 
        default = 'MET',
        help    = "set variable to plot (MET, HT, ST, WPT, NJets, lepton_pt, abs_lepton_eta )" 
    )
    parser.add_argument( "-m", "--metType", 
        dest    = "metType", 
        default = 'type1',
        help    = "set MET type used in the analysis of MET, ST or MT" 
    )
    parser.add_argument( "-b", "--bjetbin", 
        dest    = "bjetbin", 
        default = '2m',
        help    = "set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m" 
    )
    parser.add_argument( "-c", "--centre-of-mass-energy", 
        dest    = "CoM", 
        default = 13, 
        type    = int,
        help    = "set the centre of mass energy for analysis. Default = 13 [TeV]" 
    )
    parser.add_argument( "-a", "--additional-plots", 
        action  = "store_true", 
        dest    = "additional_plots",
        help    = "Draws additional plots like the comparison of different systematics to the central result."
    )
    parser.add_argument( "-g", "--show-generator-ratio", 
        action  = "store_true", 
        dest    = "show_generator_ratio",
        help    = "Show the ratio of generators to central" 
    )
    parser.add_argument( "-d", "--debug", 
        action  = "store_true", 
        dest    = "debug",
        help    = "Enables debugging output"
    )
    parser.add_argument( '--visiblePS', 
        dest    = "visiblePS", 
        action  = "store_true",
        help    = "Unfold to visible phase space" 
    )
    parser.add_argument( "-u", "--unfolding_method", 
        dest    = "unfolding_method", 
        default = 'TUnfold',
        help    = "Unfolding method: TUnfold (default)" 
    )

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    set_root_defaults()
    args = parse_arguments()

    if args.debug:
        log.setLevel(log.DEBUG)

    output_formats = ['pdf']
    measurement_config = XSectionConfig( args.CoM )
    # caching of variables for shorter access
    method = args.unfolding_method
    translate_options = measurement_config.translate_options
    variable = args.variable
    show_generator_ratio = args.show_generator_ratio
    visiblePS = args.visiblePS
    phase_space = 'FullPS'
    if visiblePS:
        phase_space = 'VisiblePS'

    output_folder = args.output_folder
    if not output_folder.endswith( '/' ):
        output_folder += '/'
    met_type = translate_options[args.metType]
    b_tag_bin = translate_options[args.bjetbin]
    path_to_DF = '{path}/{com}TeV/{variable}/{phase_space}/'
    path_to_DF = path_to_DF.format(path = args.path, com = args.CoM,
                                       variable = variable,
                                       phase_space = phase_space,
                                       )
#     path_to_DF = args.path + '/' + str( measurement_config.centre_of_mass_energy ) + 'TeV/' + variable + '/'

    all_measurements = deepcopy( measurement_config.measurements )
    pdf_uncertainties = ['PDFWeights_%d' % index for index in range( 1, 45 )]
    all_measurements.extend( pdf_uncertainties )

    # for channel in ['electron', 'muon', 'combined', 'combinedBeforeUnfolding']:
    for channel in ['muon']:
        for category in all_measurements:

            if not category == 'central' and not args.additional_plots: continue

            # if variable == 'HT' and category in met_uncertainties:
            #     continue
            # setting up systematic MET for JES up/down samples for reading fit templates
            met_type = translate_options[args.metType]
            if category == 'JES_up':
                met_type += 'JetEnUp'
            elif category == 'JES_down':
                met_type += 'JetEnDown'

            # if not channel == 'combined':
            #     #Don't make additional plots for e.g. generator systematics, mass systematics, k value systematics and pdf systematics because they are now done \
            #     #in the unfolding process with BLT unfolding files.
            #     if category in ttbar_generator_systematics or category in ttbar_mass_systematics or category in kValue_systematics or category in pdf_uncertainties:
            #         continue
            #     fit_templates, fit_results = read_fit_templates_and_results_as_histograms( category, channel )
            #     make_template_plots( fit_templates, category, channel )
            #     plot_fit_results( fit_results, category, channel )

            # change back to original MET type
            met_type = translate_options[args.metType]
            if met_type == 'PFMET':
                met_type = 'patMETsPFlow'

            histograms_normalised_xsection_different_generators, histograms_normalised_xsection_systematics_shifts = read_xsection_measurement_results( category, channel )
            histname = '{variable}_normalised_xsection_{channel}_{phase_space}_{method}'
            histname = histname.format(
                variable = variable, 
                channel = channel,
                phase_space = phase_space,
                method = method
            )

            make_plots( 
                histograms_normalised_xsection_different_generators, 
                category, 
                output_folder, 
                histname + '_different_generators', 
                show_generator_ratio = show_generator_ratio 
            )
            make_plots( 
                histograms_normalised_xsection_systematics_shifts, 
                category, 
                output_folder, 
                histname + '_systematics_shifts' 
            )

            del histograms_normalised_xsection_different_generators, histograms_normalised_xsection_systematics_shifts

        # if args.additional_plots:
            # TODO
            # Generator Only
            # PDF Only
            # MET Only
            # Rate Changing Only
            # etc...
            # plot_central_and_systematics( channel, measurements, exclude = ttbar_generator_systematics )
            # plot_central_and_systematics( channel, ttbar_generator_systematics, suffix = 'ttbar_generator_only' )
            # plot_central_and_systematics( channel, rate_changing_systematics, suffix = 'rate_changing_only' )
