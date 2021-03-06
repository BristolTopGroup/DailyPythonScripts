# the result of the division will be always a float
from __future__ import division, print_function
from argparse import ArgumentParser
import os, gc
import sys
from copy import deepcopy

from dps.config.latex_labels import variables_latex, measurements_latex
from dps.config.variable_binning import bin_edges_full, bin_edges_vis
from dps.config.xsection import XSectionConfig
from dps.utils.file_utilities import make_folder_if_not_exists
from dps.utils.pandas_utilities import read_tuple_from_file, file_to_df, tupleise_cols
from dps.utils.hist_utilities import value_error_tuplelist_to_hist, value_tuplelist_to_hist, \
value_errors_tuplelist_to_graph, graph_to_value_errors_tuplelist
from dps.utils.systematic import get_scale_envelope, scaleFSR
# rootpy & matplotlib
from ROOT import kBlue
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

from dps.utils.logger import log
xsec_04_log = log["src/cross_section_measurement/04_make_plots_matplotlib"]

@xsec_04_log.trace()
def read_xsection_measurement_results( category, channel, unc_type, scale_uncertanties=False ):
    '''
    Reading the unfolded xsection results from DFs into graphs
    '''
    global path_to_DF, variable, phase_space, method

    file_template = '{path}/{category}/xsection_{name}_{channel}_{method}{suffix}.txt'

    filename = file_template.format(
        path = path_to_DF,
        category = category,
        name = unc_type,
        channel = channel,
        method = method,
        suffix = '',
    )

    xsec_04_log.debug('Reading file {0}'.format(filename))

    edges = bin_edges_full[variable]
    if phase_space == 'VisiblePS':
        edges = bin_edges_vis[variable]

    # Collect the cross section measured/unfolded results from dataframes
    normalised_xsection_unfolded    = read_tuple_from_file( filename )

    # Create TTJets_Scale
    d_scale_syst = {}
    partonShower_uncertainties = measurement_config.list_of_systematics['TTJets_scale']
    for psUnc in partonShower_uncertainties:
        normalised_xsection_unfolded[psUnc] = [value for value, error in normalised_xsection_unfolded[psUnc]]
        d_scale_syst[psUnc] = normalised_xsection_unfolded[psUnc]

    normalised_xsection_unfolded['TTJets_scaledown'], normalised_xsection_unfolded['TTJets_scaleup'] = get_scale_envelope(
        d_scale_syst, 
        normalised_xsection_unfolded['TTJets_powhegPythia8'],
    )

    # Need to strip errors from central before passing to scaleFSR()
    central = [c[0] for c in normalised_xsection_unfolded['TTJets_powhegPythia8']]
    # Scale FSR
    if scale_uncertanties:
        normalised_xsection_unfolded['TTJets_fsrdown'] = scaleFSR(
            normalised_xsection_unfolded['TTJets_fsrdown'],
            central,
        )
        normalised_xsection_unfolded['TTJets_fsrup'] = scaleFSR(
            normalised_xsection_unfolded['TTJets_fsrup'], 
            central,
        )

    # h_normalised_xsection           = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_measured'], edges )
    h_normalised_xsection_unfolded  = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_unfolded'], edges )

    histograms_normalised_xsection_different_generators = {
        # 'measured':h_normalised_xsection,
        'unfolded':h_normalised_xsection_unfolded,
    }
    histograms_normalised_xsection_different_systematics = {
        'unfolded':h_normalised_xsection_unfolded,
    }

    if category == 'central':
        # Add in distributions for the different MC to be shown
        h_normalised_xsection_powhegPythia8     = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_powhegPythia8'], edges )
        h_normalised_xsection_amcatnlo          = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_amcatnloPythia8'], edges )
        h_normalised_xsection_madgraphMLM       = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_madgraphMLM'], edges )
        h_normalised_xsection_powhegHerwigpp    = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_powhegHerwig'], edges )
        # SCALE BREAKDOWN
        h_normalised_xsection_fsrup             = value_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_fsrup'], edges )
        h_normalised_xsection_fsrdown           = value_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_fsrdown'], edges )
        h_normalised_xsection_isrdown           = value_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_isrdown'], edges )
        h_normalised_xsection_isrup             = value_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_isrup'], edges )
        h_normalised_xsection_factorisationup   = value_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_factorisationup'], edges )
        h_normalised_xsection_factorisationdown = value_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_factorisationdown'], edges )
        h_normalised_xsection_renormalisationup = value_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_renormalisationup'], edges )
        h_normalised_xsection_renormalisationdown   = value_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_renormalisationdown'], edges )
        h_normalised_xsection_combinedup        = value_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_combinedup'], edges )
        h_normalised_xsection_combineddown      = value_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_combineddown'], edges )
        # PARTON SHOWER
        h_normalised_xsection_scaleup           = value_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_scaleup'], edges )
        h_normalised_xsection_scaledown         = value_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_scaledown'], edges )
        h_normalised_xsection_massup            = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_massup'], edges )
        h_normalised_xsection_massdown          = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_massdown'], edges )
        h_normalised_xsection_ueup              = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_ueup'], edges )
        h_normalised_xsection_uedown            = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_uedown'], edges )
        h_normalised_xsection_hdampup           = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_hdampup'], edges )
        h_normalised_xsection_hdampdown         = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_hdampdown'], edges )
        h_normalised_xsection_erdOn             = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_erdOn'], edges )
        h_normalised_xsection_QCDbased_erdOn    = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_QCDbased_erdOn'], edges )
        # h_normalised_xsection_GluonMove         = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_GluonMove'], edges )
        h_normalised_xsection_semiLepBrup       = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_semiLepBrup'], edges )
        h_normalised_xsection_semiLepBrdown     = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_semiLepBrdown'], edges )
        h_normalised_xsection_fragup            = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_fragup'], edges )
        h_normalised_xsection_fragdown          = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_fragdown'], edges )
        h_normalised_xsection_petersonFrag      = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_petersonFrag'], edges )
        # OTHER
        # h_normalised_xsection_alphaSup          = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_alphaSup'], edges )
        # h_normalised_xsection_alphaSdown        = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_alphaSdown'], edges )
        h_normalised_xsection_topPt             = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJets_topPt'], edges )

        # And update
        histograms_normalised_xsection_different_generators.update( 
            {
                'TTJets_powhegPythia8'   : h_normalised_xsection_powhegPythia8,
                'TTJets_amcatnloPythia8' : h_normalised_xsection_amcatnlo,
                'TTJets_madgraphMLM'     : h_normalised_xsection_madgraphMLM,
                'TTJets_powhegHerwig'    : h_normalised_xsection_powhegHerwigpp,
            }
        )

        if scale_uncertanties:
            histograms_normalised_xsection_different_systematics.update( 
                {
                    'TTJets_powhegPythia8'  : h_normalised_xsection_powhegPythia8,
                    'TTJets_fsrup'          : h_normalised_xsection_fsrup,
                    'TTJets_fsrdown'        : h_normalised_xsection_fsrdown,
                    'TTJets_isrdown'        : h_normalised_xsection_isrdown,
                    'TTJets_isrup'          : h_normalised_xsection_isrup,
                    'TTJets_factorisationup'    : h_normalised_xsection_factorisationup,
                    'TTJets_factorisationdown'  : h_normalised_xsection_factorisationdown,
                    'TTJets_renormalisationup'  : h_normalised_xsection_renormalisationup,
                    'TTJets_renormalisationdown'    : h_normalised_xsection_renormalisationdown,
                    'TTJets_combinedup'     : h_normalised_xsection_combinedup,
                    'TTJets_combineddown'   : h_normalised_xsection_combineddown,
                }
            )
        else:
            histograms_normalised_xsection_different_systematics.update( 
                {
                    'TTJets_powhegPythia8'  : h_normalised_xsection_powhegPythia8,
                    'TTJets_scaleup'        : h_normalised_xsection_scaleup,
                    'TTJets_scaledown'      : h_normalised_xsection_scaledown,
                    # 'TTJets_massup'         : h_normalised_xsection_massup,
                    # 'TTJets_massdown'       : h_normalised_xsection_massdown,
                    # 'TTJets_ueup'           : h_normalised_xsection_ueup,
                    # 'TTJets_uedown'         : h_normalised_xsection_uedown,
                    'TTJets_hdampup'        : h_normalised_xsection_hdampup,
                    'TTJets_hdampdown'      : h_normalised_xsection_hdampdown,
                    # 'TTJets_erdOn'          : h_normalised_xsection_erdOn,
                    # 'TTJets_QCDbased_erdOn' : h_normalised_xsection_QCDbased_erdOn,
                    # 'TTJets_GluonMove'      : h_normalised_xsection_GluonMove,

                    # 'TTJets_semiLepBrup'    : h_normalised_xsection_semiLepBrup,
                    # 'TTJets_semiLepBrdown'  : h_normalised_xsection_semiLepBrdown,
                    # 'TTJets_fragup'         : h_normalised_xsection_fragup,
                    # 'TTJets_fragdown'       : h_normalised_xsection_fragdown,
                    # 'TTJets_petersonFrag'   : h_normalised_xsection_petersonFrag,

                    'TTJets_topPt'          : h_normalised_xsection_topPt,
                }
            )

        filename = file_template.format(
            path = path_to_DF,
            category = category,
            name = unc_type,
            channel = channel,
            method = method,
            suffix = '_summary_absolute',
        )

        # Now for the systematic uncertainties
        normalised_xsection_unfolded_with_errors = file_to_df( filename )
        normalised_xsection_unfolded_with_errors['TTJets_unfolded'] = tupleise_cols(
            normalised_xsection_unfolded_with_errors['central'], 
            normalised_xsection_unfolded_with_errors['systematic'],
        )

        xsec_04_log.debug('Reading file {0}'.format(filename))

        # Transform unfolded data into graph form
        h_normalised_xsection_unfolded_with_errors_unfolded = value_errors_tuplelist_to_graph(
            normalised_xsection_unfolded_with_errors['TTJets_unfolded'],
            edges, 
            is_symmetric_errors=True
        )

        # Add to list of histograms
        histograms_normalised_xsection_different_generators['unfolded_with_systematics'] = h_normalised_xsection_unfolded_with_errors_unfolded
        histograms_normalised_xsection_different_systematics['unfolded_with_systematics'] = h_normalised_xsection_unfolded_with_errors_unfolded

    return histograms_normalised_xsection_different_generators, histograms_normalised_xsection_different_systematics

@xsec_04_log.trace()
def get_cms_labels( channel ):
    lepton = 'e'
    if channel == 'electron':
        lepton = 'e + jets'
    elif channel == 'muon':
        lepton = '$\mu$ + jets'
    else:
        lepton = 'e, $\mu$ + jets combined'
    channel_label = lepton
    template = '%.1f fb$^{-1}$ (%d TeV)'
    label = template % ( measurement_config.new_luminosity/1000., measurement_config.centre_of_mass_energy)
    return label, channel_label

@xsec_04_log.trace()
def make_plots( histograms, category, output_folder, histname, show_ratio = False, show_generator_ratio = False, show_before_unfolding = False, utype = 'normalised', preliminary=True ):
    global variable, phase_space

    channel = ''
    if 'electron' in histname:
        channel = 'electron'
    elif 'muon' in histname:
        channel = 'muon'
    else:
        channel = 'combined'

    # Initailise data histograms
    hist_data = histograms['unfolded']
    hist_data.markersize = 2
    hist_data.marker = 'o'
    if category == 'central':
        hist_data_with_systematics = histograms['unfolded_with_systematics']
        hist_data_with_systematics.markersize = 2
        hist_data_with_systematics.marker = 'o'

    # Create base figure to be plotted
    plt.figure( figsize = CMS.figsize, dpi = CMS.dpi, facecolor = CMS.facecolor )

    # Split into 3 for MC/Data ratio and generator ratio and plot
    if show_ratio and show_generator_ratio:
        gs = gridspec.GridSpec( 3, 1, height_ratios = [5, 1, 1] )
        axes = plt.subplot( gs[0] )
    # Split into 2 for MC/Data ratio or generator Ratio and plot
    elif show_ratio or show_generator_ratio:
        gs = gridspec.GridSpec( 2, 1, height_ratios = [4, 1] )
        axes = plt.subplot( gs[0] )
    # Just 1 for plot and setup x axis labels
    else:
        axes = plt.axes()
        x_label = '${}$'.format(variables_latex[variable])
        if variable in ['HT', 'ST', 'MET', 'WPT', 'lepton_pt']:
            x_label += ' [GeV]'
        plt.xlabel( x_label, CMS.x_axis_title )

    # set y axis x-section labels
    y_label = ''
    xsectionUnit = ''
    if utype == 'absolute':
        y_label = r'$\frac{d\sigma}{d' + variables_latex[variable] + '}\ '
        xsectionUnit = 'pb'
    else :
        y_label = r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + variables_latex[variable] + '}\ '

    if variable in ['HT', 'ST', 'MET', 'WPT', 'lepton_pt']:
        if xsectionUnit is '':
            y_label += '\scriptstyle(\mathrm{GeV}^{-1})$'
            pass
        else:
            y_label += '\scriptstyle(\mathrm{'
            y_label += xsectionUnit
            y_label += '}\ \mathrm{GeV}^{-1})$'
    elif xsectionUnit is not '':
        y_label += '\scriptstyle(\mathrm{'
        y_label += xsectionUnit
        y_label += '})$'
    plt.ylabel( y_label, CMS.y_axis_title )

    # Set up ticks on axis. Minor ticks on axis for non NJet variables
    plt.tick_params( **CMS.axis_label_major )
    if not variable in ['NJets']:
        axes.minorticks_on()
        plt.tick_params( **CMS.axis_label_minor )

    # Set raw unfolded data with stat+unfolding uncertianty to be visible
    hist_data.visible = True
    # axes.set_yscale('log')
    # Set raw unfolded data with systematic uncertianty to be visible
    # label = 'do_not_show' = do not show in legend
    if category == 'central':
        hist_data_with_systematics.visible = True
        rplt.errorbar( 
            hist_data_with_systematics, 
            axes = axes, 
            label = 'do_not_show', 
            xerr = None, 
            capsize = 0, 
            elinewidth = 2, 
            zorder = len( histograms ) + 1 
        )
    
    # Show stat+unf uncertainty on plot
    rplt.errorbar( hist_data, 
        axes = axes, 
        label = 'do_not_show', 
        xerr = None, 
        capsize = 15, 
        capthick = 3, 
        elinewidth = 2, 
        zorder = len( histograms ) + 2 
    )
    # And one for a nice legend entry
    rplt.errorbar( hist_data, 
        axes = axes, 
        label = 'data', 
        xerr = None, 
        yerr = False, 
        capsize = 0, 
        elinewidth = 2, 
        zorder = len( histograms ) + 3 
    )

    dashes = {}
    for key, hist in sorted( histograms.items() ):
        zorder = sorted( histograms, reverse = False ).index( key )

        # Ordering such that systematic uncertainties are plotted first then central powhegPythia then data
        if key == 'TTJets_powhegPythia8' and zorder != len(histograms) - 3:
            zorder = len(histograms) - 3
        elif key != 'TTJets_powhegPythia8' and not 'unfolded' in key:
            while zorder >= len(histograms) - 3:
                zorder = zorder - 1 

        # Colour and style of MC hists
        if not 'unfolded' in key and not 'measured' in key:
            hist.linewidth = 4
            linestyle = None

            if 'powhegPythia8' in key:
                linestyle = 'solid'
                dashes[key] = None
                hist.SetLineColor( 633 )
            elif 'powhegHerwig' in key or 'isr' in key or 'hdamp' in key:
                hist.SetLineColor( kBlue )
                dashes[key] = [25,5,5,5,5,5,5,5]
            elif 'amcatnloPythia8' in key or 'fsr' in key or 'scale' in key:
                hist.SetLineColor( 807 )
                dashes[key] = [20,5]
            elif 'madgraphMLM' in key or 'renormalisation' in key or 'topPt' in key:
                hist.SetLineColor( 417 )
                dashes[key] = [5,5]
            elif 'factorisation' in key or 'ue' in key:
                hist.SetLineColor( 100 )
                dashes[key] = [10,10]
            elif 'combined' in key or 'semiLepBr' in key:
                hist.SetLineColor( 200 )
                dashes[key] = [20,10]
            elif 'semiLepBr' in key or 'mass' in key:
                hist.SetLineColor( 300 )
                dashes[key] = [20,10,10,10]
            elif 'frag' in key or 'Frag' in key:
                hist.SetLineColor( 400 )
                dashes[key] = [10,10,5,5]
            elif 'erdOn' in key:
                hist.SetLineColor( 500 )
                dashes[key] = [10,10,5,5,5,5]

            if linestyle != None:
                hist.linestyle = linestyle

            # Add hist to plot
            line, h = rplt.hist( hist, axes = axes, label = measurements_latex[key], zorder = zorder )

            # Set the dashes and lines
            if dashes[key] != None:
                line.set_dashes(dashes[key])
                h.set_dashes(dashes[key])

    handles, labels = axes.get_legend_handles_labels()
    
    # Making data first in the legend
    data_label_index = labels.index( 'data' )
    data_handle = handles[data_label_index]
    labels.remove( 'data' )
    handles.remove( data_handle )
    labels.insert( 0, 'data' )
    handles.insert( 0, data_handle )

    # Order the rest of the labels in the legend
    new_handles, new_labels = [], []
    zipped = dict( zip( labels, handles ) )
    labelOrder = ['data', 
        measurements_latex['TTJets_powhegPythia8'],
        measurements_latex['TTJets_amcatnloPythia8'],
        measurements_latex['TTJets_powhegHerwig'],
        measurements_latex['TTJets_madgraphMLM'],
        measurements_latex['TTJets_scaleup'], 
        measurements_latex['TTJets_scaledown'],
        measurements_latex['TTJets_massup'],
        measurements_latex['TTJets_massdown'],
        measurements_latex['TTJets_ueup'],
        measurements_latex['TTJets_uedown'],
        measurements_latex['TTJets_fsrup'],
        measurements_latex['TTJets_fsrdown'],
        measurements_latex['TTJets_isrdown'],
        measurements_latex['TTJets_isrup'],
        # measurements_latex['TTJets_alphaSup'],
        # measurements_latex['TTJets_alphaSdown'],
        measurements_latex['TTJets_topPt'],
        measurements_latex['TTJets_factorisationup'],
        measurements_latex['TTJets_factorisationdown'],
        measurements_latex['TTJets_renormalisationup'],
        measurements_latex['TTJets_renormalisationdown'],
        measurements_latex['TTJets_combinedup'],
        measurements_latex['TTJets_combineddown'],
        measurements_latex['TTJets_hdampup'],
        measurements_latex['TTJets_hdampdown'],
        measurements_latex['TTJets_erdOn'],
        measurements_latex['TTJets_QCDbased_erdOn'],
        measurements_latex['TTJets_GluonMove'],
        measurements_latex['TTJets_semiLepBrup'],
        measurements_latex['TTJets_semiLepBrdown'],
        measurements_latex['TTJets_fragup'],
        measurements_latex['TTJets_fragdown'],
        measurements_latex['TTJets_petersonFrag'],
    ]
    for label in labelOrder:
        if label in labels:
            new_handles.append(zipped[label])
            if label == 'data':
                new_labels.append(measurements_latex['data'])
            else:
                new_labels.append(label)

    # Location of the legend
    legend_location = (0.95, 0.82)
    prop = CMS.legend_properties
    if variable == 'MT':
        legend_location = (0.05, 0.82)
    elif variable == 'ST':
        legend_location = (0.97, 0.82)
    elif variable == 'WPT':
        legend_location = (1.0, 0.84)
    elif variable == 'abs_lepton_eta' or variable =='abs_lepton_eta_coarse':
        legend_location = (0.97, 0.87)
    elif variable == 'NJets':
        # Reduce size of NJets legend
        prop = {'size':30}

    # Add legend to plot
    plt.legend( new_handles, new_labels, 
        numpoints = 1, 
        prop = prop, 
        frameon = False, 
        bbox_to_anchor=legend_location,
        bbox_transform=plt.gcf().transFigure 
    )

    # Title and CMS labels
    # note: fontweight/weight does not change anything as we use Latex text!!!
    label, channel_label = get_cms_labels( channel )
    plt.title( label,loc='right', **CMS.title )

    # Locations of labels
    logo_location = (0.05, 0.97)
    channel_location = ( 0.05, 0.9)
    if preliminary:
        prelim_location = (0.05, 0.9)
        channel_location = ( 0.5, 0.97)
        # preliminary
        plt.text(prelim_location[0], prelim_location[1], 
            r"\emph{Preliminary}",
            transform=axes.transAxes, 
            fontsize=42,
            verticalalignment='top',
            horizontalalignment='left'
        )

    # if variable == 'WPT':
    #     logo_location = (0.05, 0.97)
    #     prelim_location = (0.05, 0.9)
    #     channel_location = (0.5, 0.97)
    # elif variable == 'abs_lepton_eta':
    #     logo_location = (0.05, 0.97)
    #     prelim_location = (0.05, 0.9)
    #     channel_location = ( 0.5, 0.97)

    # Add labels to plot
    plt.text(logo_location[0], logo_location[1], 
        r"\textbf{CMS}", 
        transform=axes.transAxes, 
        fontsize=42,
        verticalalignment='top',
        horizontalalignment='left'
    )


    # channel text
    plt.text(channel_location[0], channel_location[1], 
        r"%s"%channel_label, 
        transform=axes.transAxes, 
        fontsize=40,
        verticalalignment='top',
        horizontalalignment='left'
    )

    # Set y limits on plot
    ylim = axes.get_ylim()
    if ylim[0] < 0:
        axes.set_ylim( ymin = 0.)
    axes.set_ylim(ymax = ylim[1]*1.1)
    if variable == 'abs_lepton_eta' or variable == 'abs_lepton_eta_coarse':
        axes.set_ylim(ymax = ylim[1]*1.6)

    # Now to show either of the ratio plots
    if show_ratio:
        # Set previous x axis ticks and labels to invisible
        plt.setp( axes.get_xticklabels(), visible = False )
        # Go to ratio subplot
        ax1 = plt.subplot( gs[1] )

        # setting the x_limits identical to the main plot
        x_limits = axes.get_xlim()
        ax1.set_xlim(x_limits)

        # Setting tick marks
        ax1.yaxis.set_major_locator( MultipleLocator( 0.5 ) )
        plt.tick_params( **CMS.axis_label_major )
        # if not variable in ['NJets']:
        #     ax1.minorticks_on()
        #     ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        #     plt.tick_params( **CMS.axis_label_minor )

        # x axis labels as before
        x_label = '${}$'.format(variables_latex[variable])
        if variable in ['HT', 'ST', 'MET', 'WPT', 'lepton_pt']:
            x_label += ' (GeV)'

        if not show_generator_ratio:
            plt.xlabel( x_label, CMS.x_axis_title )

        y_label = '$\\displaystyle\\frac{\\mathrm{pred.}}{\\mathrm{data}}$'
        plt.ylabel( y_label, CMS.y_axis_title_small )
        ax1.yaxis.set_label_coords(-0.115, 0.7)

        # Draw a horizontal line at y=1 for data
        plt.axhline(y = 1, color = 'black', linewidth = 2)

        # Create ratios and plot to subplot
        for key, hist in sorted( histograms.iteritems() ):
            if not 'unfolded' in key and not 'measured' in key:
                ratio = hist.Clone()
                ratio.Divide( hist_data )
                line, h = rplt.hist( ratio, axes = ax1, label = 'do_not_show' )
                if dashes[key] != None:
                    line.set_dashes(dashes[key])
                    h.set_dashes(dashes[key])

        # Now for the error bands
        stat_lower = hist_data.Clone()
        stat_upper = hist_data.Clone()
        syst_lower = hist_data.Clone()
        syst_upper = hist_data.Clone()

        # Plot relative error bands on data in the ratio plot
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

        # Colour
        if category == 'central':
            rplt.fill_between( 
                syst_lower, 
                syst_upper, 
                ax1,
                color = 'gold' 
            )
        rplt.fill_between(
            stat_upper, 
            stat_lower, 
            ax1, 
            color = '0.75',
        )

        # Add legend
        loc = 'upper left'
        if variable == 'MET':
            loc = 'lower left'
        elif variable == 'HT':
            loc = 'lower center'
        elif variable == 'ST':
            loc = 'lower center'
        elif variable == 'WPT':
            loc = 'lower left'
        elif variable == 'NJets':
            loc = 'lower left'
        elif variable == 'abs_lepton_eta' or variable == 'abs_lepton_eta_coarse':
            loc = 'upper left'
        elif variable == 'lepton_pt':
            loc = 'lower left'

        # legend for ratio plot
        p_stat = mpatches.Patch(facecolor='0.75', label='Stat.', edgecolor='black' )
        p_stat_and_syst = mpatches.Patch(facecolor='gold', label=r'Stat. $\oplus$ Syst.', edgecolor='black' )
        l1 = ax1.legend(
            handles = [p_stat, p_stat_and_syst], 
            loc = loc,
            frameon = False, 
            prop = {'size':26},
            ncol = 2
        )
        ax1.add_artist(l1)

        # Setting y limits and tick parameters
        if variable == 'MET':
            ax1.set_ylim( ymin = 0.6, ymax = 1.4 )
            ax1.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        if variable == 'MT':
            ax1.set_ylim( ymin = 0.8, ymax = 1.2 )
            ax1.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'HT':
            ax1.set_ylim( ymin = 0.6, ymax = 1.4 )
            ax1.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'ST':
            ax1.set_ylim( ymin = 0.6, ymax = 1.4 )
            ax1.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'WPT':
            ax1.set_ylim( ymin = 0.6, ymax = 1.4 )
            ax1.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'NJets':
            ax1.set_ylim( ymin = 0.6, ymax = 1.4 )
            ax1.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'abs_lepton_eta' or variable == 'abs_lepton_eta_coarse':
            ax1.set_ylim( ymin = 0.6, ymax = 1.4 )
            ax1.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'lepton_pt':
            ax1.set_ylim( ymin = 0.6, ymax = 1.4 )
            ax1.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )


    if show_generator_ratio:

        ax2 = None

        # Remove Data/MC Ratio Axis
        if show_ratio:
            plt.setp( ax1.get_xticklabels(), visible = False ) 
            ax2 = plt.subplot( gs[2] )
        else:
            plt.setp( axes.get_xticklabels(), visible = False )
            ax2 = plt.subplot( gs[1] )

        # setting the x_limits identical to the main plot
        x_limits = axes.get_xlim()
        ax2.set_xlim(x_limits)

        # Setting ticks
        ax2.yaxis.set_major_locator( MultipleLocator( 0.5 ) )
        plt.tick_params( **CMS.axis_label_major )
        if not variable in ['NJets']:
            ax2.minorticks_on()
            ax2.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
            plt.tick_params( **CMS.axis_label_minor )

        # x axis labels as before
        x_label = '${}$'.format(variables_latex[variable])
        if variable in ['HT', 'ST', 'MET', 'WPT', 'lepton_pt']:
            x_label += ' [GeV]'
        plt.xlabel( x_label, CMS.x_axis_title )

        y_label = 'Ratio to \n$' + measurements_latex['TTJets_powhegPythia8'] + '$'
        plt.ylabel( y_label, CMS.y_axis_title_tiny )

        #draw a horizontal line at y=1 for central MC
        plt.axhline(y = 1, color = 'black', linewidth = 2)

        central_mc = histograms['TTJets_powhegPythia8']
        for key, hist in sorted( histograms.iteritems() ):

            if not 'measured' in key:

                ratio = None
                if not 'unfolded_with_systematics' in key:
                    ratio = hist.Clone()
                    ratio.Divide( central_mc ) #divide by central mc sample
                else:
                    ratio = central_mc.Clone()
                    syst_errors = graph_to_value_errors_tuplelist(hist)
                    for bin_i in range( 1, ratio.GetNbinsX() + 1 ):
                        syst_value, syst_error_down, syst_error_up  = syst_errors[bin_i-1]

                        mc = central_mc.GetBinContent(bin_i)
                        data = list(hist.y())[bin_i-1]

                        ratio.SetBinContent( bin_i, data / mc)
                        ratio.SetBinError( bin_i, syst_error_down / mc )

                if not 'unfolded' in key:
                    line, h = rplt.hist( ratio, axes = ax2, label = 'do_not_show' )
                    if dashes[key] != None:
                        line.set_dashes(dashes[key])
                        h.set_dashes(dashes[key])
                elif 'unfolded_with_systematics' in key:
                        ratio.markersize = 2
                        ratio.marker = 'o'
                        ratio.color = 'black'
                        rplt.errorbar( 
                            ratio, 
                            axes = ax2, 
                            label = 'do_not_show', 
                            xerr = None, 
                            capsize = 0, 
                            elinewidth = 2, 
                            zorder = len( histograms ) + 10
                        )
                else:
                    ratio.markersize = 2
                    ratio.marker = 'o'

                    rplt.errorbar( ratio, 
                        axes = ax2, 
                        label = 'do_not_show', 
                        xerr = None, 
                        capsize = 15, 
                        capthick = 3, 
                        elinewidth = 2, 
                        zorder = len( histograms ) + 9
                    )


        if variable == 'MET':
            ax2.set_ylim( ymin = 0.8, ymax = 1.2 )
            ax2.yaxis.set_major_locator( MultipleLocator( 0.5 ) )
            ax2.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        if variable == 'MT':
            ax2.set_ylim( ymin = 0.8, ymax = 1.2 )
            ax2.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax2.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'HT':
            ax2.set_ylim( ymin = 0.7, ymax = 1.3 )
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
        elif variable == 'abs_lepton_eta' or variable == 'abs_lepton_eta_coarse':
            ax2.set_ylim( ymin = 0.8, ymax = 1.2 )
            ax2.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax2.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
        elif variable == 'lepton_pt':
            ax2.set_ylim( ymin = 0.8, ymax = 1.3 )
            ax2.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
            ax2.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )


    if CMS.tight_layout:
        plt.tight_layout()

    # Save the plots
    path = '{output_folder}/xsections/{phaseSpace}/{variable}/'
    path = path.format(
        output_folder = output_folder,
        phaseSpace = phase_space,
        variable = variable
    )
    make_folder_if_not_exists( path )
    for output_format in output_formats:
        filename = path + '/' + histname + '.' + output_format
        plt.savefig( filename )

    del hist_data
    if 'central' in category: del hist_data_with_systematics
    plt.close()
    gc.collect()
    return

# @xsec_04_log.trace()
# def plot_central_and_systematics( channel, systematics, exclude = [], suffix = 'altogether' ):
#     global variable

#     plt.figure( figsize = ( 16, 16 ), dpi = 200, facecolor = 'white' )
#     axes = plt.axes()
#     if not variable in ['NJets']:
#         axes.minorticks_on()

#     hist_data_central = read_xsection_measurement_results( 'central', channel )[0]['unfolded_with_systematics']
#     hist_data_central.markersize = 2  # points. Imagine, tangible units!
#     hist_data_central.marker = 'o'

#     if variable in ['NJets', 'abs_lepton_eta', 'lepton_eta']:
#         plt.xlabel( '$%s$' % variables_latex[variable], CMS.x_axis_title )
#         plt.ylabel( r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + variables_latex[variable] + '}$', CMS.y_axis_title )
#     else:
#         plt.xlabel( '$%s$ [GeV]' % variables_latex[variable], CMS.x_axis_title )
#         plt.ylabel( r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + variables_latex[variable] + '} \left[\mathrm{GeV}^{-1}\\right]$', CMS.y_axis_title )
#     plt.tick_params( **CMS.axis_label_major )
#     if not variable in ['NJets']:
#         plt.tick_params( **CMS.axis_label_minor )

#     rplt.errorbar( hist_data_central, axes = axes, label = 'data', xerr = True )

#     for systematic in sorted( systematics ):
#         if systematic in exclude or systematic == 'central':
#             continue

#         hist_data_systematic = read_xsection_measurement_results( systematic, channel )[0]['unfolded']
#         hist_data_systematic.markersize = 2
#         hist_data_systematic.marker = 'o'
#         colour_number = systematics.index( systematic ) + 2
#         if colour_number == 10:
#             colour_number = 42
#         hist_data_systematic.SetMarkerColor( colour_number )
#         if 'PDF' in systematic:
#             rplt.errorbar( hist_data_systematic, axes = axes, label = systematic.replace( 'Weights_', ' ' ), xerr = None )tranelse:
#             rplt.errorbar( hist_data_systematic, axes = axes, label = measurements_latex[systematic], xerr = None )

#     plt.legend( numpoints = 1, loc = 'center right', prop = {'size':25}, ncol = 2 )
#     label, channel_label = get_cms_labels( channel )
#     plt.title( label, CMS.title )
#     # CMS text
#     # note: fontweight/weight does not change anything as we use Latex text!!!
#     plt.text(0.95, 0.95, r"\textbf{CMS}", transform=axes.transAxes, fontsize=42,
#         verticalalignment='top',horizontalalignment='right')
#     # channel text
#     axes.text(0.95, 0.90, r"\emph{%s}" %channel_label, transform=axes.transAxes, fontsize=40,
#         verticalalignment='top',horizontalalignment='right')
#     plt.tight_layout()


#     path = output_folder + str( measurement_config.centre_of_mass_energy ) + 'TeV/' + variable
#     make_folder_if_not_exists( path )
#     for output_format in output_formats:
#         filename = path + '/normalised_xsection_' + channel + '_' + suffix + '.' + output_format

#         plt.savefig( filename )

#     plt.close()
#     gc.collect()

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
    parser.add_argument( "-r", "--show-ratio", 
        action  = "store_true", 
        dest    = "show_ratio",
        help    = "Show the ratio of different generators to central" 
    )
    parser.add_argument( "-g", "--show-generator-ratio", 
        action  = "store_true", 
        dest    = "show_generator_ratio",
        help    = "Show the ratio of generator variations to central" 
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
    parser.add_argument( "-s", "--show_scales", 
        dest    = "plot_scale_uncertainties", 
        action  = "store_true",
        help    = "Show parton shower scale uncertainties" 
    )
    parser.add_argument( "--final", 
        dest    = "is_final", 
        action  = "store_true",
        help    = "Preliminary plot or not" 
    )

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    set_root_defaults()
    args = parse_arguments()

    if args.debug:
        log.setLevel(log.DEBUG)

    output_formats          = ['pdf']
    measurement_config      = XSectionConfig( args.CoM )

    # caching of variables for shorter access
    method                  = args.unfolding_method
    variable                = args.variable
    show_ratio              = args.show_ratio
    show_generator_ratio    = args.show_generator_ratio
    visiblePS               = args.visiblePS
    output_folder           = args.output_folder
    plot_scale_uncertainties= args.plot_scale_uncertainties
    is_preliminary          = not args.is_final

    if not output_folder.endswith( '/' ):
        output_folder += '/'

    phase_space = 'FullPS'
    if visiblePS:
        phase_space = 'VisiblePS'

    path_to_DF = '{path}/{com}TeV/{variable}/{phase_space}/'
    path_to_DF = path_to_DF.format(
        path = args.path, 
        com = args.CoM,
        variable = variable,
        phase_space = phase_space,
    )

    all_measurements = deepcopy( measurement_config.measurements )
    pdf_uncertainties = ['PDFWeights_%d' % index for index in range( measurement_config.pdfWeightMin, measurement_config.pdfWeightMax )]
    all_measurements.extend( pdf_uncertainties )

    channel = [
        'electron', 
        'muon', 
        'combined', 
        # 'combinedBeforeUnfolding',
    ]

    unc_type = [
        'normalised',
        'absolute',
    ]

    partonShower = ''
    if plot_scale_uncertainties:
        partonShower = '_partonShower'

    for ch in channel:
        for utype in unc_type:
            for category in all_measurements:

                # Show central only. TODO Add in additional systematic comparison plots
                if not category == 'central' and not args.additional_plots: continue
                if variable in measurement_config.variables_no_met and category in measurement_config.met_specific_systematics: continue

                # Read the xsection results from dataframe
                histograms_normalised_xsection_different_generators, histograms_normalised_xsection_different_systematics = read_xsection_measurement_results( category, ch, utype, scale_uncertanties=plot_scale_uncertainties )
                
                histname = '{variable}_{utype}_xsection_{ch}_{phase_space}_{method}'.format(
                    variable = variable, 
                    utype = utype,
                    ch = ch,
                    phase_space = phase_space,
                    method = method
                )
                make_plots( 
                    histograms_normalised_xsection_different_generators, 
                    category, 
                    output_folder, 
                    histname + '_different_generators', 
                    show_ratio = show_ratio,
                    show_generator_ratio = show_generator_ratio ,
                    utype = utype,
                    preliminary = is_preliminary,
                )

                make_plots( 
                    histograms_normalised_xsection_different_systematics, 
                    category, 
                    output_folder, 
                    histname + '_different_systematics'+partonShower, 
                    show_ratio = show_ratio,
                    show_generator_ratio = show_generator_ratio ,
                    utype = utype,
                    preliminary = is_preliminary,
                )

                del histograms_normalised_xsection_different_generators

            # if args.additional_plots:
                # TODO
                # Generator Only
                # PDF Only
                # MET Only
                # Rate Changing Only
                # etc...
                # plot_central_and_systematics( ch, measurements, exclude = ttbar_generator_systematics )
                # plot_central_and_systematics( ch, ttbar_generator_systematics, suffix = 'ttbar_generator_only' )
                # plot_central_and_systematics( ch, rate_changing_systematics, suffix = 'rate_changing_only' )
