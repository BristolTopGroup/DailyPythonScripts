'''
Created on 26 Feb 2014

@author: senkin
'''

from optparse import OptionParser
import matplotlib as mpl
mpl.use( 'agg' )
import matplotlib.pyplot as plt
import rootpy.plotting.root2matplotlib as rplt
from config import CMS
import matplotlib.cm as cm
# from itertools import cycle
from config.latex_labels import b_tag_bins_latex, variables_latex
from config.variable_binning import bin_edges, bin_edges_vis
from config import XSectionConfig
from tools.ROOT_utils import get_histogram_from_file
from tools.file_utilities import make_folder_if_not_exists
from tools.file_utilities import read_data_from_JSON
from tools.hist_utilities import value_tuplelist_to_hist
from tools.Calculation import calculate_purities, calculate_stabilities
from tools.hist_utilities import rebin_2d

from matplotlib import rc
rc( 'font', **CMS.font )
rc( 'text', usetex = True )

# use full stpectrum, yet use white for less than vmin=1 events
my_cmap = cm.get_cmap( 'jet' )
my_cmap.set_under( 'w' )

def make_scatter_plot( input_file, histogram, bin_edges, channel, variable, title ):
    global output_folder, output_formats, options
    scatter_plot = get_histogram_from_file( histogram, input_file )
#     scatter_plot.Rebin2D( 5, 5 )

    x_limits = [bin_edges[variable][0], bin_edges[variable][-1]]
    y_limits = x_limits

    x_title = 'Reconstructed $' + variables_latex[variable] + '$ [GeV]'
    y_title = 'Generated $' + variables_latex[variable] + '$ [GeV]'
    save_as_name = channel + '_' + variable + '_' + str(options.CoM) + 'TeV'

    plt.figure( figsize = ( 20, 16 ), dpi = 200, facecolor = 'white' )

    ax0 = plt.axes()
    ax0.minorticks_on()
#     ax0.grid( True, 'major', linewidth = 2 )
#     ax0.grid( True, 'minor' )
    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )
    ax0.xaxis.labelpad = 12
    ax0.yaxis.labelpad = 12
    im = rplt.imshow( scatter_plot, axes = ax0, cmap = my_cmap, vmin = 0.001 )
    colorbar = plt.colorbar( im )
    colorbar.ax.tick_params( **CMS.axis_label_major )

    # draw lines at bin edges values
    for edge in bin_edges[variable]:
        # do not inclue first and last values
        if ( edge != bin_edges[variable][0] ) and ( edge != bin_edges[variable][-1] ):
            plt.axvline( x = edge, color = 'red', linewidth = 4, alpha = 0.5 )
            plt.axhline( y = edge, color = 'red', linewidth = 4, alpha = 0.5 )

    ax0.set_xlim( x_limits )
    ax0.set_ylim( y_limits )

    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )

    plt.xlabel( x_title, CMS.x_axis_title )
    plt.ylabel( y_title, CMS.y_axis_title )
    plt.title( title, CMS.title )

    plt.tight_layout()

    for output_format in output_formats:
        plt.savefig( output_folder + save_as_name + '.' + output_format )

def makePurityStabilityPlots(input_file, histogram, bin_edges, channel, variable, isVisiblePhaseSpace):
    global output_folder, output_formats
 
    hist = get_histogram_from_file( histogram, input_file )

    # get_bin_content = hist.ProjectionX().GetBinContent
    purities = calculate_purities( hist.Clone() )
    stabilities = calculate_stabilities( hist.Clone() )
    # n_events = [int( get_bin_content( i ) ) for i in range( 1, len( bin_edges ) )]

    hist_stability = value_tuplelist_to_hist(stabilities, bin_edges)
    hist_purity = value_tuplelist_to_hist(purities, bin_edges)

    hist_purity.color = 'red'
    hist_stability.color = 'blue'

    hist_stability.linewidth = 4
    hist_purity.linewidth = 4

    x_limits = [bin_edges[0], bin_edges[-1]]
    y_limits = [0,1]
    plt.figure( figsize = ( 20, 16 ), dpi = 200, facecolor = 'white' )

    ax0 = plt.axes()
    ax0.minorticks_on()
#     ax0.grid( True, 'major', linewidth = 2 )
#     ax0.grid( True, 'minor' )
    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )
    ax0.xaxis.labelpad = 12
    ax0.yaxis.labelpad = 12
    rplt.hist( hist_stability , stacked=False, axes = ax0, cmap = my_cmap, vmin = 1, label = 'Stability' )
    rplt.hist( hist_purity, stacked=False, axes = ax0, cmap = my_cmap, vmin = 1, label = 'Purity' )

    ax0.set_xlim( x_limits )
    ax0.set_ylim( y_limits )

    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )

    x_title = '$' + variables_latex[variable] + '$ [GeV]'
    plt.xlabel( x_title, CMS.x_axis_title )

    leg = plt.legend(loc=4,prop={'size':40})

    plt.tight_layout()

    plt.savefig('test.pdf')
    save_as_name = 'purityStability_'+channel + '_' + variable + '_' + str(options.CoM) + 'TeV'
    for output_format in output_formats:
        plt.savefig( output_folder + save_as_name + '.' + output_format )

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
        bin_edges_to_use = bin_edges

    channels = ['electron', 'muon', 'COMBINED']
    channels_latex = { 'electron':'e+jets', 'muon':'$\mu$+jets', 'COMBINED':'e+$\mu$+jets combined' }

    b_tag_bin = '2orMoreBtags'
    title_template = 'CMS Simulation, $\sqrt{s}$ = %d TeV, %s, %s, %s'

    for channel in channels:
        print 'Channel', channel
        title = title_template % ( measurement_config.centre_of_mass_energy, channels_latex[channel], '$\geq$ 4 jets', b_tag_bins_latex[b_tag_bin] )
        for variable in bin_edges_to_use.keys():
            print '--- ',variable
            histogram_path = '%s_%s/%s' % (variable, channel, histogram_name)
            
            make_scatter_plot( hist_file, histogram_path, bin_edges_to_use, channel, variable, title )

            makePurityStabilityPlots( measurement_config.unfolding_central, histogram_path, bin_edges_to_use[variable], channel, variable, options.visiblePhaseSpace)
