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
from tools.ROOT_utililities import get_histogram_from_file
from tools.file_utilities import make_folder_if_not_exists

from matplotlib import rc
rc( 'font', **CMS.font )
rc( 'text', usetex = True )

# use full stpectrum, yet use white for less than vmin=1 events
my_cmap = cm.get_cmap( 'jet' )
my_cmap.set_under( 'w' )

def make_scatter_plot( input_file, histogram, channel, variable, title ):
    global output_folder, output_formats
    scatter_plot = get_histogram_from_file( histogram, input_file )
    scatter_plot.Rebin2D( 5, 5 )

    x_limits = [0, bin_edges[variable][-1]]
    y_limits = x_limits

    x_title = 'Generated $' + variables_latex[variable] + '$ [GeV]'
    y_title = 'Reconstructed $' + variables_latex[variable] + '$ [GeV]'
    save_as_name = channel + '_' + variable

    plt.figure( figsize = ( 20, 16 ), dpi = 200, facecolor = 'white' )

    ax0 = plt.axes()
    ax0.minorticks_on()
    ax0.grid( True, 'major', linewidth = 2 )
    ax0.grid( True, 'minor' )
    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )
    ax0.xaxis.labelpad = 12
    ax0.yaxis.labelpad = 12
    im = rplt.imshow( scatter_plot, axes = ax0, cmap = my_cmap, vmin = 1 )
    colorbar = plt.colorbar( im )
    colorbar.ax.tick_params( **CMS.axis_label_major )

    # draw lines at bin edges values
    for edge in bin_edges[variable]:
        # do not inclue first and last values
        if ( edge != bin_edges[variable][0] ) and ( edge != bin_edges[variable][-1] ):
            plt.axvline( x = edge, color = 'red', linewidth = 4 )
            plt.axhline( y = edge, color = 'red', linewidth = 4 )

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

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option( "-o", "--output_folder", dest = "output_folder", default = 'plots/binning/',
                      help = "set path to save plots" )
    parser.add_option( "-c", "--centre-of-mass-energy", dest = "CoM", default = 8, type = int,
                      help = "set the centre of mass energy for analysis. Default = 8 [TeV]" )

    ( options, args ) = parser.parse_args()

    output_formats = ['png', 'pdf']
    output_folder = options.output_folder
    make_folder_if_not_exists( options.output_folder )
    from config.variable_binning import bin_edges
    if options.CoM == 8:
        import config.cross_section_measurement_8TeV as measurement_config
    elif options.CoM == 7:
        import config.cross_section_measurement_7TeV as measurement_config
    else:
        import sys
        sys.exit( 'Unknown centre of mass energy' )

    hist_file = measurement_config.central_general_template % ( 'TTJet' )
#     hist_file = '/storage/Workspace/Analysis/AnalysisSoftware/TTJet_19584pb_PFElectron_PFMuon_PF2PATJets_PFMET_TEST.root'
    
    histograms = ['MET_gen_nu_vs_reco', 'HT_genJet_vs_reco', 'ST_gen_vs_reco', 'MT_gen_vs_reco', 'WPT_gen_vs_reco']
    variables_translation = {'MET_gen_nu_vs_reco':'MET', 'HT_genJet_vs_reco':'HT', 'ST_gen_vs_reco':'ST',
    						'MT_gen_vs_reco':'MT', 'WPT_gen_vs_reco':'WPT'}

    channels = ['EPlusJets', 'MuPlusJets']
    channels_latex = { 'EPlusJets':'e+jets', 'MuPlusJets':'$\mu$+jets' }

    b_tag_bin = '2orMoreBtags'
    title_template = 'CMS Simulation, $\sqrt{s}$ = %d TeV, %s, %s, %s'

    for channel in channels:
        title = title_template % ( measurement_config.centre_of_mass, channels_latex[channel], '$\geq$ 4 jets', b_tag_bins_latex[b_tag_bin] )
        for histogram in histograms:
            histogram_path = 'Binning/' + channel + '/' + histogram# + '_' + b_tag_bin
            variable = variables_translation[histogram]
            make_scatter_plot( hist_file, histogram_path, channel, variable, title )



