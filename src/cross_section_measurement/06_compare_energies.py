'''
Created on Mar 12, 2014

@author: Luke Kreczko

github: kreczko
'''
from optparse import OptionParser
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import rootpy.plotting.root2matplotlib as rplt

from src.cross_section_measurement.lib import read_xsection_measurement_results
from config import XSectionConfig
from config.variable_binning import bin_edges_full
from config.latex_labels import variables_latex
from config import CMS
from rootpy.plotting import Graph
from ROOT import kRed, kMagenta, kBlue
from matplotlib.ticker import MultipleLocator
from tools.ROOT_utils import set_root_defaults

output_formats = ['pdf', 'png']

def main():
    set_root_defaults()
    options, _ = parse_arguments()
    variable = 'ST'
    config_7TeV = XSectionConfig(7)
    config_8TeV = XSectionConfig(8)
    path_to_JSON_7TeV = options.path + '/7TeV/' + variable + '/'
    path_to_JSON_8TeV = options.path + '/8TeV/' + variable + '/'
    # we need the generators
    # and the central samples + errors
    results_7TeV, _ = read_xsection_measurement_results( path_to_JSON_7TeV,
                                                     variable,
                                                     bin_edges_full,
                                                     category = 'central',
                                                     channel = 'combined',
                                                     k_values = {
                                                                 'combined': config_7TeV.k_values_combined}
                                                     )
    results_8TeV, _ = read_xsection_measurement_results( path_to_JSON_8TeV,
                                                     variable,
                                                     bin_edges_full,
                                                     category = 'central',
                                                     channel = 'combined',
                                                     k_values = {
                                                                 'combined': config_8TeV.k_values_combined}
                                                     )
    plot_results(results_7TeV, results_8TeV, variable)

def parse_arguments():
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data/',
                  help = "set path to JSON files" )
    parser.add_option( "-o", "--output_folder", dest = "output_folder", default = 'plots/',
                  help = "set path to save plots" )
    parser.add_option( "-v", "--variable", dest = "variable", default = 'MET',
                  help = "set variable to plot (MET, HT, ST, MT, WPT)" )
    ( options, args ) = parser.parse_args()
    return options, args

def plot_results( results_7TeV, results_8TeV, variable ):
    # first we need the central graphs
    # the results are
    # unfolded_with_systematics, MADGRAPH, POWHEG, MCATNLO
    plt.figure( figsize = (16,32), dpi = CMS.dpi, facecolor = CMS.facecolor )
    
    gs = gridspec.GridSpec( 3, 1, height_ratios = [7, 7, 1] )
    axes = plt.subplot( gs[0] )
    plt.setp( axes.get_xticklabels(), visible = False )
    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )
    plt.ylabel( r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + variables_latex[variable] + '} \left[\mathrm{GeV}^{-1}\\right]$', CMS.y_axis_title )
    draw_result( results_7TeV, axes )
    plt.legend(numpoints = 1, loc = 'upper right', prop = CMS.legend_properties )
    axes = plt.subplot( gs[1] )
    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )
    plt.ylabel( r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + variables_latex[variable] + '} \left[\mathrm{GeV}^{-1}\\right]$', CMS.y_axis_title )
    plt.setp( axes.get_xticklabels(), visible = False )
    draw_result( results_8TeV, axes )
    plt.legend(numpoints = 1, loc = 'upper right', prop = CMS.legend_properties )
    ratios = get_ratios(results_7TeV, results_8TeV)
    axes = plt.subplot( gs[2] )
    plt.xlabel( '$%s$ [GeV]' % variables_latex[variable], CMS.x_axis_title )
    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )
    axes.yaxis.set_major_locator( MultipleLocator( 0.2 ) )
    axes.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )
    plt.ylabel( r'$\frac{7\, TeV}{8\, TeV}$', CMS.y_axis_title )
#     axes.grid( True, 'major', linewidth = 1 )
    draw_result( ratios, axes )
    axes.set_ylim( ymin = 0.8, ymax = 1.2 )
    plt.tight_layout()
    path = 'plots/'
    histname = variable + '_comparison'
    for output_format in output_formats:
        filename = path + '/' + histname + '.' + output_format
        plt.savefig( filename )
    
def draw_result( result, axes ):
    graph = result['unfolded']
    graph_with_systematics = result['unfolded_with_systematics']
    madgraph = result['MADGRAPH']
    powheg = result['POWHEG']
    mcatnlo = result['MCATNLO']
    # styles
    graph.markersize = 2
    graph.marker = 'o'
    graph_with_systematics.markersize = 2
    graph_with_systematics.marker = 'o'
    powheg.linestyle = 'longdashdot'
    powheg.SetLineColor( kBlue )
    madgraph.linestyle = 'solid'
    madgraph.SetLineColor( kRed + 1 )
    mcatnlo.linestyle = 'dotted'
    mcatnlo.SetLineColor( kMagenta + 3 )
    
    
    rplt.errorbar( graph, xerr = None, emptybins = False, axes = axes, elinewidth = 2, capsize = 10, capthick = 2, zorder = 6)
    rplt.errorbar( graph_with_systematics, xerr = None, emptybins = False, axes = axes, elinewidth = 2, capsize = 0, zorder = 5, label = 'unfolded data')
    rplt.hist( madgraph, axes = axes, label = 'MADGRAPH', zorder = 1 )
    rplt.hist( powheg, axes = axes, label = 'POWHEG', zorder = 2 )
    rplt.hist( mcatnlo, axes = axes, label = 'MCATNLO', zorder = 3 )

def get_ratios(results_7TeV, results_8TeV):
    ratios = {}
    for key in results_7TeV.keys():
        ratio = None
        if 'Graph' in str(type(results_7TeV[key])):
            ratio = Graph.divide(results_7TeV[key], results_8TeV[key], False)
        else:
            ratio = results_7TeV[key].Clone( 'ratio_' + key )
            ratio.Divide(results_8TeV[key])
        ratios[key] = ratio
    return ratios
if __name__ == '__main__':
    main()
