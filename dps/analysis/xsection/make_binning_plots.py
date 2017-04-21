'''
Created on 26 Feb 2014

@author: senkin
'''

from optparse import OptionParser
import matplotlib as mpl
mpl.use( 'agg' )
import matplotlib.pyplot as plt
import rootpy.plotting.root2matplotlib as rplt
from dps.config import CMS
import matplotlib.cm as cm
import numpy as np
import gc
# from itertools import cycle
from dps.config.latex_labels import b_tag_bins_latex, variables_latex
from dps.config.variable_binning import bin_edges_full, bin_edges_vis
from dps.config.xsection import XSectionConfig
from dps.utils.ROOT_utils import get_histogram_from_file
from dps.utils.file_utilities import make_folder_if_not_exists
from dps.utils.hist_utilities import value_tuplelist_to_hist
from dps.utils.Calculation import calculate_purities, calculate_stabilities
from dps.utils.hist_utilities import rebin_2d

from matplotlib import rc
rc( 'font', **CMS.font )
rc( 'text', usetex = True )

# use full stpectrum, yet use white for less than vmin=1 events
my_cmap = cm.get_cmap( 'jet' )
my_cmap.set_under( 'w' )

def make_scatter_plot( input_file, histogram, bin_edges, channel, variable, title ):
    global output_folder
    scatter_plot = get_histogram_from_file( histogram, input_file )

    response_hist = rebin_2d( scatter_plot, bin_edges[variable], bin_edges[variable] ).Clone( 'response' )

    # Finding max value in scatterplot for colourmap normalisation
    max_bin = response_hist.GetMaximumBin()
    max_bin_content = response_hist.GetBinContent(max_bin)
    norm = mpl.colors.LogNorm(vmin = 1, vmax = int(max_bin_content+1))

    # Axis Titles
    x_title = 'Reconstructed $' + variables_latex[variable] + '$ [GeV]'
    y_title = 'Generated $' + variables_latex[variable] + '$ [GeV]'
    save_as_name = 'response_'+channel + '_' + variable

    x_limits = [bin_edges[variable][0], bin_edges[variable][-1]]
    y_limits = x_limits

    fig = plt.figure()
    ax0 = fig.add_subplot(1, 1, 1)

    # fig.subplots_adjust(bottom = 0)
    # fig.subplots_adjust(top = 1)
    # fig.subplots_adjust(right = 1)
    # fig.subplots_adjust(left = 0)

    h = rplt.hist2d( response_hist, axes = ax0, colorbar=True, cmap = my_cmap, norm=norm )

    plt.xlabel( x_title, CMS.x_axis_title )
    plt.ylabel( y_title, CMS.y_axis_title )
    # plt.title( title, CMS.title )

    ax0.minorticks_on()
    ax0.xaxis.labelpad = 12
    ax0.yaxis.labelpad = 12
    ax0.set_xlim( x_limits )
    ax0.set_ylim( y_limits )

    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )

    plt.tight_layout()

    # Save and release memory
    plt.savefig( output_folder + save_as_name + '.pdf' )
    fig.clf()
    plt.close()
    gc.collect()
    return

# def makePurityStabilityPlots(input_file, histogram, bin_edges, channel, variable, isVisiblePhaseSpace):
#     global output_folder, output_formats
 
#     hist = get_histogram_from_file( histogram, input_file )
#     print "bin edges contents   : ", bin_edges
#     new_hist = rebin_2d( hist, bin_edges, bin_edges ).Clone()

#     # get_bin_content = hist.ProjectionX().GetBinContent
#     purities = calculate_purities( new_hist.Clone() )
#     stabilities = calculate_stabilities( new_hist.Clone() )
#     # n_events = [int( get_bin_content( i ) ) for i in range( 1, len( bin_edges ) )]
#     print "purities contents    : ", purities
#     print "stabilities contents : ", stabilities

#     hist_stability = value_tuplelist_to_hist(stabilities, bin_edges)
#     hist_purity = value_tuplelist_to_hist(purities, bin_edges)

#     hist_purity.color = 'red'
#     hist_stability.color = 'blue'

#     hist_stability.linewidth = 4
#     hist_purity.linewidth = 4

#     x_limits = [bin_edges[0], bin_edges[-1]]
#     y_limits = [0,1]
#     plt.figure( figsize = ( 20, 16 ), dpi = 200, facecolor = 'white' )

#     ax0 = plt.axes()
#     ax0.minorticks_on()
# #     ax0.grid( True, 'major', linewidth = 2 )
# #     ax0.grid( True, 'minor' )
#     plt.tick_params( **CMS.axis_label_major )
#     plt.tick_params( **CMS.axis_label_minor )
#     ax0.xaxis.labelpad = 12
#     ax0.yaxis.labelpad = 12
#     rplt.hist( hist_stability , stacked=False, axes = ax0, cmap = my_cmap, vmin = 1, label = 'Stability' )
#     rplt.hist( hist_purity, stacked=False, axes = ax0, cmap = my_cmap, vmin = 1, label = 'Purity' )

#     ax0.set_xlim( x_limits )
#     ax0.set_ylim( y_limits )

#     plt.tick_params( **CMS.axis_label_major )
#     plt.tick_params( **CMS.axis_label_minor )

#     x_title = '$' + variables_latex[variable] + '$ [GeV]'
#     plt.xlabel( x_title, CMS.x_axis_title )

#     leg = plt.legend(loc=4,prop={'size':40})

#     plt.tight_layout()

#     plt.savefig('test.pdf')
#     save_as_name = 'purityStability_'+channel + '_' + variable + '_' + str(options.CoM) + 'TeV'
#     for output_format in output_formats:
#         plt.savefig( output_folder + save_as_name + '.' + output_format )

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option( "-o", "--output_folder", dest = "output_folder", default = 'plots/binning/',
                      help = "set path to save plots" )
    parser.add_option( "-p", dest = "input_path", default = 'unfolding/13TeV/',
                      help = "set input path of purity and stability" )
    parser.add_option( "-c", "--centre-of-mass-energy", dest = "CoM", default = 13, type = int,
                      help = "set the centre of mass energy for analysis. Default = 13 [TeV]" )
    parser.add_option( '-v', dest = "visiblePhaseSpace", action = "store_true",
                      help = "Consider visible phase space or not" )

    ( options, args ) = parser.parse_args()
    measurement_config = XSectionConfig(options.CoM)

    output_formats = ['pdf']
    output_folder = options.output_folder + '/fullPhaseSpace/'
    if options.visiblePhaseSpace:
        output_folder = options.output_folder + '/visiblePhaseSpace/'
    make_folder_if_not_exists( output_folder )

    #hist_file = measurement_config.central_general_template % ( 'TTJet' )
    hist_file = measurement_config.unfolding_central_raw
    
    histogram_name = ''
    bin_edges_to_use = []
    if options.visiblePhaseSpace:
        histogram_name = 'responseVis_without_fakes'
        bin_edges_to_use = bin_edges_vis
    else :
        histogram_name = 'response_without_fakes'
        bin_edges_to_use = bin_edges_full

    channels = ['electron', 'muon', 'combined']
    channels_latex = { 'electron':'e+jets', 'muon':'$\mu$+jets', 'combined':'e+$\mu$+jets combined' }

    b_tag_bin = '2orMoreBtags'
    title_template = 'CMS Simulation, $\sqrt{s}$ = %d TeV, %s, %s, %s'

    for channel in channels:
        print 'Channel', channel
        title = title_template % ( measurement_config.centre_of_mass_energy, channels_latex[channel], '$\geq$ 4 jets', b_tag_bins_latex[b_tag_bin] )
        for variable in bin_edges_to_use.keys():
            print '--- ',variable
            histogram_path = '%s_%s/%s' % (variable, channel, histogram_name)
            
            make_scatter_plot( hist_file, histogram_path, bin_edges_to_use, channel, variable, title )

            # makePurityStabilityPlots( measurement_config.unfolding_central_raw, histogram_path, bin_edges_to_use[variable], channel, variable, options.visiblePhaseSpace)
