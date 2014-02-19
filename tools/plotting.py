'''
Created on 3 May 2013

@author: kreczko
'''
import matplotlib.pyplot as plt
import rootpy.plotting.root2matplotlib as rplt
from rootpy.plotting import HistStack
from config import CMS
from matplotlib.patches import Rectangle
from copy import deepcopy
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator
from itertools import cycle

from matplotlib import rc
rc( 'text', usetex = True )

class Histogram_properties:
    name = 'Test'
    title = "Test"
    x_axis_title = "I am the x-axis"
    y_axis_title = "I am the y-axis"
    x_limits = []
    y_limits = []
    mc_error = 0.
    mc_errors_label = 'MC uncertainty'
    normalise = False
    legend_location = 'best'
    set_log_y = False
    legend_columns = 1
    
    def __init__( self ):
        pass

# prototype
class Control_plot:
    lumi = 5050
    rebin = 1
    histogram_properties = Histogram_properties()
    channel = 'combined'
    b_tag_bin = '2orMoreBtags'
    
    def __init__( self, control_region, qcd_control_region, histogram_files, **kwargs ):
        self.control_region = control_region
        self.qcd_control_region = qcd_control_region
        self.histogram_files = histogram_files
        
        self.b_tag_bin = kwargs.pop( 'b_tag_bin', self.b_tag_bin )
        self.lumi = kwargs.pop( 'lumi', self.lumi )
        self.rebin = kwargs.pop( 'rebin', self.rebin )
        self.histogram_properties = kwargs.pop( 'histogram_properties', self.histogram_properties )
        self.channel = kwargs.pop( 'channel', self.channel )


def make_data_mc_comparison_plot( histograms = [],
                                 histogram_lables = [],
                                 histogram_colors = [],
                                 histogram_properties = Histogram_properties(),
                                 data_index = 0,
                                 save_folder = 'plots/',
                                 save_as = ['pdf', 'png'],
                                 normalise = False,
                                 show_ratio = False,
                                 show_stat_errors_on_mc = False,
                                 ):
        
    stack = HistStack()
    add_mc = stack.Add
    for index, histogram in enumerate( histograms ):
        label = histogram_lables[index]
        color = histogram_colors[index]
        
        histogram.SetTitle( label )
        if normalise:
            histogram.Sumw2()
        
        if not index == data_index:
            histogram.fillstyle = 'solid'
            histogram.fillcolor = color
            histogram.legendstyle = 'F'
            add_mc( histogram )
            
    data = histograms[data_index]
    data.SetMarkerSize( CMS.data_marker_size )
    if normalise:
        n_events_data = data.Integral()
        n_events_mc = stack.Integral()
        data.Scale( 1 / n_events_data )
        stack.Scale( 1 / n_events_mc )
    
    # plot with matplotlib
    plt.figure( figsize = CMS.figsize, dpi = CMS.dpi, facecolor = CMS.facecolor )
    if show_ratio:
        ratio = data.Clone( 'ratio' )
        ratio.Divide( sum( stack.GetHists() ) )
        ratio.SetMarkerSize( 3 )
        gs = gridspec.GridSpec( 2, 1, height_ratios = [5, 1] ) 
        axes = plt.subplot( gs[0] )
    else:
        axes = plt.axes()

    if histogram_properties.set_log_y:
        axes.set_yscale( 'log', nonposy = "clip" )
        axes.set_ylim( ymin = 1e-2 )
    mc_error = histogram_properties.mc_error
    if mc_error > 0:
        stack_lower = sum( stack.GetHists() )
        stack_upper = stack_lower.Clone( 'upper' )
        stack_lower.Scale( 1 - mc_error )
        stack_upper.Scale( 1 + mc_error )
        rplt.fill_between( stack_upper, stack_lower, axes, facecolor = '0.75', alpha = 0.5, hatch = '/', zorder = 2 )
    if not mc_error > 0 and show_stat_errors_on_mc:
        stack_lower = sum( stack.GetHists() )
        mc_errors = list( stack_lower.errors() )
        stack_upper = stack_lower.Clone( 'upper' )
        for bin_i in range( 1, stack_lower.GetNbinsX() ):
            stack_lower.SetBinContent( bin_i, stack_lower.GetBinContent( bin_i ) - mc_errors[bin_i - 1] )
            stack_upper.SetBinContent( bin_i, stack_upper.GetBinContent( bin_i ) + mc_errors[bin_i - 1] )
        rplt.fill_between( stack_upper, stack_lower, axes, facecolor = '0.75', alpha = 0.5, hatch = '/', zorder = 2 )
    # a comment on zorder: the MC stack should be always at the very back (z=1), 
    # then the MC error (z=2) and finally the data (z=4)
    rplt.hist( stack, stacked = True, axes = axes, zorder = 1 )
#    rplt.errorbar(data, xerr=False, emptybins=False, axes=axes, elinewidth=2, capsize=10, capthick=2, zorder=3)
#    rplt.errorbar(data, xerr=False, emptybins=False, axes=axes, elinewidth=2, capsize=10, capthick=2, snap_zero = False)
    rplt.errorbar( data, xerr = False, emptybins = False, axes = axes, elinewidth = 2, capsize = 10, capthick = 2, zorder = 4 )
    
    set_labels( plt, histogram_properties, show_x_label = not show_ratio )
    
    # put legend into the correct order (data is always first!)
    handles, labels = axes.get_legend_handles_labels()
    data_label_index = labels.index( 'data' )
    data_handle = handles[data_label_index]
    labels.remove( 'data' )
    handles.remove( data_handle )
    labels.insert( 0, 'data' )
    handles.insert( 0, data_handle )
    if mc_error > 0 or ( not mc_error > 0 and show_stat_errors_on_mc ):
        p1 = Rectangle( ( 0, 0 ), 1, 1, fc = "0.75", alpha = 0.5, hatch = '/' )
        handles.append( p1 )
        labels.append( histogram_properties.mc_errors_label )
    
    plt.legend( handles, labels, numpoints = 1, loc = histogram_properties.legend_location,
               prop = CMS.legend_properties, ncol = histogram_properties.legend_columns )
    
    x_limits = histogram_properties.x_limits
    y_limits = histogram_properties.y_limits
    if len( x_limits ) == 2:
        axes.set_xlim( xmin = x_limits[0], xmax = x_limits[1] )
    if len( y_limits ) == 2:
        axes.set_ylim( ymin = y_limits[0], ymax = y_limits[1] )
    else:
        axes.set_ylim( ymin = 0 )
    if histogram_properties.set_log_y:
        if not len( y_limits ) == 2:  # if not user set y-limits, set default
            axes.set_ylim( ymin = 1e-1 )

    if show_ratio:
        plt.setp( axes.get_xticklabels(), visible = False )
        ax1 = plt.subplot( gs[1] )
        ax1.minorticks_on()
        ax1.grid( True, 'major', linewidth = 1 )
        ax1.yaxis.set_major_locator( MultipleLocator( 1.0 ) )
        ax1.yaxis.set_minor_locator( MultipleLocator( 0.5 ) )
        plt.tick_params( **CMS.axis_label_major )
        plt.tick_params( **CMS.axis_label_minor )
        plt.xlabel( histogram_properties.x_axis_title, CMS.x_axis_title )
        plt.ylabel( 'data/MC', CMS.y_axis_title )
        rplt.errorbar( ratio, xerr = True, emptybins = False, axes = ax1 )
        if len( x_limits ) == 2:
            ax1.set_xlim( xmin = x_limits[0], xmax = x_limits[1] )
        ax1.set_ylim( ymin = 0, ymax = 2 )

    plt.tight_layout()
    
    for save in save_as:
        plt.savefig( save_folder + histogram_properties.name + '.' + save )

    plt.close()
        
def make_control_region_comparison( control_region_1, control_region_2,
                                   name_region_1, name_region_2,
                                   histogram_properties = Histogram_properties(),
#                                   show_ratio = True,
                                   save_folder = 'plots/',
                                   save_as = ['pdf', 'png'] ):
    # make copies in order not to mess with existing histograms
    control_region_1 = deepcopy( control_region_1 )
    control_region_2 = deepcopy( control_region_2 )
    # normalise as we are comparing shapes
    control_region_1.Scale( 1 / control_region_1.Integral() )
    control_region_2.Scale( 1 / control_region_2.Integral() )
    
    ratio = control_region_1.Clone( 'ratio' )
    ratio.Divide( control_region_2 )
    ratio.SetMarkerSize( 3 )
    
    control_region_1.fillcolor = 'yellow'
    control_region_2.fillcolor = 'red'
    control_region_1.fillstyle = 'solid'
    control_region_2.fillstyle = 'solid'
    
    # plot with matplotlib
    plt.figure( figsize = ( 16, 16 ), dpi = 200, facecolor = 'white' )
    gs = gridspec.GridSpec( 2, 1, height_ratios = [5, 1] ) 
    ax0 = plt.subplot( gs[0] )
    ax0.minorticks_on()
    
    rplt.hist( control_region_1, axes = ax0 )
    rplt.hist( control_region_2, axes = ax0, alpha = 0.5 )
    
    set_labels( plt, histogram_properties, show_x_label = False )
    
    plt.legend( [name_region_1 + ' (1)', name_region_2 + ' (2)'], numpoints = 1, loc = 'upper right', prop = CMS.legend_properties )
    x_limits = histogram_properties.x_limits
    y_limits = histogram_properties.y_limits
    if len( x_limits ) == 2:
        ax0.set_xlim( xmin = x_limits[0], xmax = x_limits[1] )
    if len( y_limits ) == 2:
        ax0.set_ylim( ymin = y_limits[0], ymax = y_limits[1] )
    plt.setp( ax0.get_xticklabels(), visible = False )
    
    ax1 = plt.subplot( gs[1] )
    ax1.minorticks_on()
    ax1.grid( True, 'major', linewidth = 1 )
    ax1.yaxis.set_major_locator( MultipleLocator( 1.0 ) )
    ax1.yaxis.set_minor_locator( MultipleLocator( 0.5 ) )
    set_labels( plt, histogram_properties, show_x_label = True )
    plt.ylabel( '(1)/(2)', CMS.y_axis_title )
    rplt.errorbar( ratio, xerr = True, emptybins = False, axes = ax1 )
    if len( x_limits ) == 2:
        ax1.set_xlim( xmin = x_limits[0], xmax = x_limits[1] )
    ax1.set_ylim( ymin = -0.5, ymax = 4 )
    plt.tight_layout()
    for save in save_as:
        plt.savefig( save_folder + histogram_properties.name + '.' + save ) 
    plt.close()

def make_plot( histogram, histogram_label, histogram_properties = Histogram_properties(),
                                 save_folder = 'plots/',
                                 save_as = ['pdf', 'png'],
                                 normalise = False
                                 ):
    
    histogram.SetTitle( histogram_label )
#    histogram.SetMarkerSize(CMS.data_marker_size)
    # to be changed
    histogram.fillcolor = '0.75'
    histogram.fillstyle = 'solid'
    if normalise:
        histogram.Scale( 1 / histogram.Integral() )
    
    # plot with matplotlib
    plt.figure( figsize = CMS.figsize, dpi = CMS.dpi, facecolor = CMS.facecolor )
    axes = plt.axes()
    
    rplt.hist( histogram )
    
    set_labels( plt, histogram_properties )
    
    plt.legend( numpoints = 1, loc = histogram_properties.legend_location, prop = CMS.legend_properties )
    
    adjust_axis_limits( axes, histogram_properties )
    plt.tight_layout()    
    
    for save in save_as:
        plt.savefig( save_folder + histogram_properties.name + '.' + save )
    plt.close()
    
def compare_measurements( models = {}, measurements = {},
                            show_measurement_errors = True,
                            histogram_properties = Histogram_properties(),
                            save_folder = 'plots/',
                            save_as = ['pdf', 'png'] ):
    """
        This function takes one or more models and compares it to a set of measurements.
        Models and measurements are supplied as dictionaries in the form of {'label': histogram}
        @param models: a dictionary of one or more model input, i.e 
            theories = {'model1' : histogram1, 'model2' : histogram_2
            where histogram_1(2) is a root (or rootpy/matplotlib) histogram object.
        @param measurements: a dictionary of one or more measurement. Follows the same
            prescription as the models parameter.
        @param histogram_properties: a Histogram_properties object to describe the look of the histogram
    """
    # plot with matplotlib
    plt.figure( figsize = CMS.figsize, dpi = CMS.dpi, facecolor = CMS.facecolor )
    axes = plt.axes()
    # Set default color cycle to rgby
    # matplotlib
    # plt.rc( 'axes', color_cycle = ['r', 'g', 'b', 'y'] )
    # rootpy
    colors = ['green', 'red', 'blue', 'magenta']
    colorcycler = cycle( colors )
    
#     markers = ['circle', 'triangledown', 'triangleup', 'diamond', 'square', 'star']
    markers = [20, 23, 22, 33, 21, 29]
    markercycler = cycle( markers )
    # matplotlib
#     lines = ["-", "--", "-.", ":"]
    # rootpy
    lines = ["dashed", "solid", "dashdot", "dotted"]
    linecycler = cycle( lines )
    
    for label, histogram in models.iteritems():
        histogram.linewidth = 2 
        histogram.color = next( colorcycler )
        histogram.linestyle = next( linecycler ) 
        rplt.hist( histogram, axex = axes, label = label )
        
    for label, histogram in measurements.iteritems():
        histogram.markersize = 2 
        histogram.markerstyle = next( markercycler )
        histogram.color = next( colorcycler )
        rplt.errorbar( histogram, axes = axes, label = label ,
                       yerr = show_measurement_errors, xerr = False )
    
    set_labels( plt, histogram_properties )

    plt.legend( numpoints = 1, loc = histogram_properties.legend_location,
                prop = CMS.legend_properties )
    adjust_axis_limits( axes, histogram_properties )
    
    plt.tight_layout()    
    
    for save in save_as:
        plt.savefig( save_folder + histogram_properties.name + '.' + save )
    plt.close()

def set_labels( plt, histogram_properties, show_x_label = True ):
    if show_x_label:
        plt.xlabel( histogram_properties.x_axis_title, CMS.x_axis_title )
    plt.ylabel( histogram_properties.y_axis_title, CMS.y_axis_title )
    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )
    plt.title( histogram_properties.title, CMS.title )
    
def adjust_axis_limits( axes, histogram_properties ):
    x_limits = histogram_properties.x_limits
    if len( x_limits ) == 2:
        axes.set_xlim( xmin = x_limits[0], xmax = x_limits[1] )
        
    y_limits = histogram_properties.y_limits
    if len( y_limits ) == 2:
        axes.set_ylim( ymin = y_limits[0], ymax = y_limits[1] )
    else:
        axes.set_ylim( ymin = 0 )
