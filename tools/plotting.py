'''
Created on 3 May 2013

@author: kreczko
'''
import matplotlib as mpl
from tools.file_utilities import make_folder_if_not_exists
from tools.hist_utilities import get_histogram_ratios, spread_x,\
    graph_to_value_errors_tuplelist
mpl.use('agg')
import matplotlib.pyplot as plt
import rootpy.plotting.root2matplotlib as rplt
from rootpy.plotting import HistStack, Hist, Graph
from config import CMS
from matplotlib.patches import Rectangle
from copy import deepcopy
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator, FixedLocator
from itertools import cycle
from tools.latex import setup_matplotlib

setup_matplotlib()

class Histogram_properties:
    name = 'Test'
    title = "Test"
    x_axis_title = "I am the x-axis"
    y_axis_title = "I am the y-axis"
    x_limits = [] #[min, max]
    y_limits = [] #[min, max]
    mc_error = 0.
    mc_errors_label = 'MC uncertainty'
    normalise = False
    legend_location = (0.98, 0.88)
    set_log_y = False
    legend_columns = 1
    has_ratio = False
    ratio_y_limits = [0.7, 1.3] #[min, max]
    rebin = 1
    additional_text = ''
    preliminary = True
    cms_logo_location = 'left' # left|right
    ratio_y_title = 'I am the ratio'
    legend_color = False
    y_max_scale = 1.2
    
    
    def __init__( self, dictionary = {} ):
        for name, value in dictionary.iteritems():
            if hasattr( self, name ):
                setattr( self, name, value )

# prototype
class PlotConfig:
    '''
        Class to read a JSON file and extract information from it.
        It creates HistSets and plot_options, essentiall replacing the main
        functionality of the bin/plot script.
    '''
    general_options = ['files', 'histograms', 'labels', 'plot_type', 'output_folder',
                  'output_format', 'command', 'data_index', 'normalise',
                  'show_ratio', 'show_stat_errors_on_mc', 'colours', 'name_prefix']
    
    def __init__( self, config_file, **kwargs ):
        self.config_file = config_file

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
                                 draw_vertical_line = 0,
                                 ):
    save_folder = check_save_folder(save_folder)
    # make copies in order not to mess with existing histograms
    histograms_ = deepcopy(histograms)     
    stack = HistStack()
    add_mc = stack.Add
    for index, histogram in enumerate( histograms_ ):
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
            
    data = histograms_[data_index]
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
        rplt.fill_between( stack_upper, 
                           stack_lower, axes, facecolor = '0.75', 
                           alpha = 0.5, hatch = '/', 
                           zorder = len(histograms_) + 1 )
    if not mc_error > 0 and show_stat_errors_on_mc:
        stack_lower = sum( stack.GetHists() )
        mc_errors = list( stack_lower.yerravg() )
        stack_upper = stack_lower.Clone( 'upper' )
        for bin_i in range( 1, stack_lower.GetNbinsX() ):
            stack_lower.SetBinContent( bin_i, stack_lower.GetBinContent( bin_i ) - mc_errors[bin_i - 1] )
            stack_upper.SetBinContent( bin_i, stack_upper.GetBinContent( bin_i ) + mc_errors[bin_i - 1] )
        rplt.fill_between( stack_upper, stack_lower, axes, facecolor = '0.75', 
                           alpha = 0.5, hatch = '/', 
                           zorder = len(histograms_) + 1 )

    # a comment on zorder: the MC stack should be always at the very back (z = 1), 
    # then the MC error (z = len(histograms_) + 1) and finally the data 
    # (z = len(histograms_) + 2)
    rplt.hist( stack, stacked = True, axes = axes, zorder = 1 )
    rplt.errorbar( data, xerr = False, emptybins = False, axes = axes, 
                   elinewidth = 2, capsize = 10, capthick = 2, 
                   zorder = len(histograms_) + 2 )
    
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

    l1 = axes.legend( handles, labels, numpoints = 1,
                     frameon = histogram_properties.legend_color,
                bbox_to_anchor = histogram_properties.legend_location,
                bbox_transform=plt.gcf().transFigure,
                prop = CMS.legend_properties,
                ncol = histogram_properties.legend_columns )
    l1.set_zorder(102)

    set_labels( plt, histogram_properties, show_x_label = not show_ratio, axes = axes )

    x_limits = histogram_properties.x_limits
    y_limits = histogram_properties.y_limits
    if len( x_limits ) == 2:
        axes.set_xlim( xmin = x_limits[0], xmax = x_limits[1] )
    if len( y_limits ) == 2:
        axes.set_ylim( ymin = y_limits[0], ymax = y_limits[1] )
    else:
        y_max = get_best_max_y(histograms_, x_limits=x_limits) * histogram_properties.y_max_scale
        axes.set_ylim( ymin = 0, ymax = y_max )
    if histogram_properties.set_log_y:
        if not len( y_limits ) == 2:  # if not user set y-limits, set default
            axes.set_ylim( ymin = 1e-1 )

    #draw a red vertical line if needed:
    if draw_vertical_line != 0:
        plt.axvline(x = draw_vertical_line, color = 'red', linewidth = 3)

    if show_ratio:
        plt.setp( axes.get_xticklabels(), visible = False )
        ax1 = plt.subplot( gs[1] )
        ax1.minorticks_on()
        ax1.grid( True, 'major', linewidth = 1 )
        # Add horizontal line at y=1 on ratio plot
        ax1.axhline(y=1, linewidth = 1)
        set_labels( plt, histogram_properties, show_x_label = True, show_title = False )
        plt.ylabel( r'$\frac{\mathrm{data}}{\mathrm{pred.}}$', CMS.y_axis_title )
        ax1.yaxis.set_label_coords(-0.115, 0.8)
        rplt.errorbar( ratio, xerr = True, emptybins = False, axes = ax1 )
        if len( x_limits ) == 2:
            ax1.set_xlim( xmin = x_limits[0], xmax = x_limits[1] )
        if len( histogram_properties.ratio_y_limits ) == 2:
            ax1.set_ylim( ymin = histogram_properties.ratio_y_limits[0],
                      ymax = histogram_properties.ratio_y_limits[1] )

        # dynamic tick placement
        adjust_ratio_ticks(ax1.yaxis, n_ticks = 3)

    if CMS.tight_layout:
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
    save_folder = check_save_folder(save_folder)
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
    control_region_1.legendstyle = 'F'
    control_region_2.legendstyle = 'F'
    
    # plot with matplotlib
    plt.figure( figsize = CMS.figsize, dpi = CMS.dpi, facecolor = CMS.facecolor )
    gs = gridspec.GridSpec( 2, 1, height_ratios = [5, 1] ) 
    axes = plt.subplot( gs[0] )
    axes.minorticks_on()
    
    rplt.hist( control_region_1, axes = axes, alpha = 0.5 )
    rplt.hist( control_region_2, axes = axes, alpha = 0.5 )
    
    set_labels( plt, histogram_properties, show_x_label = False, axes = axes)

    handles, labels = axes.get_legend_handles_labels()

    labels.insert( 0, name_region_1 + ' (1)' )
    labels.insert( 1, name_region_2 + ' (2)' )

    l1 = axes.legend( handles, labels, numpoints = 1,
                     frameon = histogram_properties.legend_color,
                bbox_to_anchor = histogram_properties.legend_location,
                bbox_transform=plt.gcf().transFigure,
                prop = CMS.legend_properties,
                ncol = histogram_properties.legend_columns )
    l1.set_zorder(102)

    x_limits = histogram_properties.x_limits
    y_limits = histogram_properties.y_limits
    if len( x_limits ) == 2:
        axes.set_xlim( xmin = x_limits[0], xmax = x_limits[1] )
    if len( y_limits ) == 2:
        axes.set_ylim( ymin = y_limits[0], ymax = y_limits[1] )
    else:
        y_max = get_best_max_y([control_region_1, control_region_2], x_limits=x_limits) * histogram_properties.y_max_scale
        axes.set_ylim( ymin = 0, ymax = y_max )
    plt.setp( axes.get_xticklabels(), visible = False )
    
    ax1 = plt.subplot( gs[1] )
    ax1.minorticks_on()
    ax1.grid( True, 'major', linewidth = 1 )
    # dynamic tick placement
    adjust_ratio_ticks(ax1.yaxis, n_ticks = 3)
    set_labels( plt, histogram_properties, show_x_label = True, show_title = False )
    plt.ylabel( '(1)/(2)', CMS.y_axis_title )
    rplt.errorbar( ratio, xerr = True, emptybins = False, axes = ax1 )
    if len( x_limits ) == 2:
        ax1.set_xlim( xmin = x_limits[0], xmax = x_limits[1] )
    if len( histogram_properties.ratio_y_limits ) == 2:
            ax1.set_ylim( ymin = histogram_properties.ratio_y_limits[0],
                      ymax = histogram_properties.ratio_y_limits[1] )
    else:
        ax1.set_ylim( ymin = -0.5, ymax = 4 )
    # dynamic tick placement
    adjust_ratio_ticks(ax1.yaxis, n_ticks = 3)
    
    if CMS.tight_layout:
        plt.tight_layout()
    
    for save in save_as:
        plt.savefig( save_folder + histogram_properties.name + '.' + save ) 
    plt.close()
    
def make_shape_comparison_plot( shapes = [],
                                   names = [],
                                   colours = [],
                                   histogram_properties = Histogram_properties(),
                                   fill_area = True,
                                   make_ratio = False,
                                   alpha = 0.5,
                                   save_folder = 'plots/',
                                   save_as = ['pdf', 'png'],
                                   normalise_ratio_to_errors = False ):
    save_folder = check_save_folder(save_folder)
    # make copies in order not to mess with existing histograms
    shapes_ = deepcopy(shapes)
    # normalise as we are comparing shapes
    for shape, colour, label in zip(shapes_, colours, names):
        shape.SetTitle(label)
        integral = shape.Integral()
        if integral > 0:
            shape.Sumw2()
            shape.Scale( 1 / integral )
        shape.fillcolor = colour
        shape.linecolor = colour
        shape.markercolor = colour
        shape.legendstyle = 'F'
        if fill_area:
            shape.fillstyle = 'solid'
        else:
            shape.linewidth = 5
            
    if not histogram_properties.y_limits:
        histogram_properties.y_limits = [0, get_best_max_y(shapes_, False)]
    # plot with matplotlib
    plt.figure( figsize = CMS.figsize, dpi = CMS.dpi, facecolor = CMS.facecolor )
    gs = gridspec.GridSpec( 2, 1, height_ratios = [5, 1] )
    axes = None
    if make_ratio: 
        axes = plt.subplot( gs[0] )
    else:
        axes = plt.axes()
    axes.minorticks_on()
    
    for shape in shapes_:
        rplt.hist( shape, axes = axes, alpha = alpha )
    
    set_labels( plt, histogram_properties, show_x_label = not make_ratio, axes = axes )
    handles, labels = axes.get_legend_handles_labels()
    for i,name in enumerate(names):
        labels.insert(i, name)
        
    # always fill legends
    if not fill_area:
        for handle in handles:
            handle.set_fill(True)
            handle.set_facecolor(handle.get_edgecolor())

    l1 = axes.legend( handles, labels, numpoints = 1,
                     frameon = histogram_properties.legend_color,
                bbox_to_anchor = histogram_properties.legend_location,
                bbox_transform=plt.gcf().transFigure,
                prop = CMS.legend_properties,
                ncol = histogram_properties.legend_columns )
    l1.set_zorder(102)
    #add error bars
    graphs = spread_x(shapes_, list(shapes_[0].xedges()))
    for graph in graphs:
        rplt.errorbar( graph, axes = axes, xerr = False,)

    adjust_axis_limits(axes, histogram_properties, shapes_)
    if make_ratio:
        plt.setp( axes.get_xticklabels(), visible = False )
        ratios = get_histogram_ratios(shapes_[0], shapes_[1:], normalise_ratio_to_errors)
        ax1 = plt.subplot( gs[1] )
        ax1.minorticks_on()
        ax1.grid( True, 'major', linewidth = 1 )
        set_labels( plt, histogram_properties, show_x_label = True, show_title = False )
        if normalise_ratio_to_errors:
            plt.ylabel( r'$\frac{1-2}{\sqrt{(\sigma_1)^2 + (\sigma_2)^2}}$', CMS.y_axis_title )
        else:
            plt.ylabel( '(1)/(2)', CMS.y_axis_title )
        for ratio in ratios:
            ratio.SetMarkerSize( 2 )
            rplt.errorbar( ratio, xerr = True, emptybins = False, axes = ax1 )
        if len( histogram_properties.x_limits ) == 2:
            ax1.set_xlim( xmin = histogram_properties.x_limits[0], 
                          xmax = histogram_properties.x_limits[1] )
        if len( histogram_properties.ratio_y_limits ) == 2:
            ax1.set_ylim( ymin = histogram_properties.ratio_y_limits[0],
                      ymax = histogram_properties.ratio_y_limits[1] )
        # dynamic tick placement
        adjust_ratio_ticks(ax1.yaxis, n_ticks = 3)
    
    if CMS.tight_layout:
        plt.tight_layout()
    
    for save in save_as:
        plt.savefig( save_folder + histogram_properties.name + '.' + save ) 
    plt.close()

def make_plot( histogram, histogram_label, histogram_properties = Histogram_properties(),
                                 save_folder = 'plots/',
                                 save_as = ['pdf', 'png'],
                                 normalise = False,
                                 draw_errorbar = False,
                                 draw_legend = True
                                 ):
    save_folder = check_save_folder(save_folder)
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
    
    if draw_errorbar:
        rplt.errorbar( histogram, xerr = False, emptybins = False, axes = axes, elinewidth = 2, capsize = 10, capthick = 2 )
    else:
        rplt.hist( histogram )
    

    if draw_legend:
        l1 = axes.legend(numpoints = 1,
                     frameon = histogram_properties.legend_color,
                bbox_to_anchor = histogram_properties.legend_location,
                bbox_transform=plt.gcf().transFigure,
                prop = CMS.legend_properties,
                ncol = histogram_properties.legend_columns )
        l1.set_zorder(102)
    
    adjust_axis_limits( axes, histogram_properties, [histogram] )

    x_limits = histogram_properties.x_limits
    y_limits = histogram_properties.y_limits
    if len( x_limits ) == 2:
        axes.set_xlim( xmin = x_limits[0], xmax = x_limits[1] )
    if len( y_limits ) == 2:
        axes.set_ylim( ymin = y_limits[0], ymax = y_limits[1] )
    
    if histogram_properties.set_log_y:
        axes.set_yscale( 'log', nonposy = "clip" )
        if not len( histogram_properties.y_limits ) == 2:  # if not user set y-limits, calculate the limits from the tuple values
            value_range = sorted( list( histogram.y() ) )
            for i, value in enumerate(value_range):
                if value == 0:
                    del value_range[i]
            axes.set_ylim( ymin = min(value_range)/10, ymax = max(value_range)*10 )

    set_labels( plt, histogram_properties )

    if CMS.tight_layout:
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
    save_folder = check_save_folder(save_folder)
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
        if not histogram: # skip empty ones
            continue
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
    
    set_labels( plt, histogram_properties, axes = axes )

    l1 = axes.legend(numpoints = 1,
                     frameon = histogram_properties.legend_color,
                bbox_to_anchor = histogram_properties.legend_location,
                bbox_transform=plt.gcf().transFigure,
                prop = CMS.legend_properties,
                ncol = histogram_properties.legend_columns)
    l1.set_zorder(102)
    
    all_hists = []
    all_hists.extend(models.values())
    all_hists.extend(measurements.values())
    adjust_axis_limits( axes, histogram_properties, all_hists )

    x_limits = histogram_properties.x_limits
    y_limits = histogram_properties.y_limits
    if len( x_limits ) == 2:
        axes.set_xlim( xmin = x_limits[0], xmax = x_limits[1] )
    if len( y_limits ) == 2:
        axes.set_ylim( ymin = y_limits[0], ymax = y_limits[1] )
    
    if histogram_properties.set_log_y:
        axes.set_yscale( 'log', nonposy = "clip" )
        if not len( histogram_properties.y_limits ) == 2:  # if not user set y-limits, calculate the limits from the tuple values
            value_range = sorted( list( histogram.y() ) )
            for i, value in enumerate(value_range):
                if value == 0:
                    del value_range[i]
            axes.set_ylim( ymin = min(value_range)/10, ymax = max(value_range)*10 )
    
    if CMS.tight_layout:
        plt.tight_layout()
    
    for save in save_as:
        plt.savefig( save_folder + histogram_properties.name + '.' + save )
    plt.close()

def set_labels( plt, histogram_properties, show_x_label = True, 
                show_title = True, axes = None ):
    if show_x_label:
        plt.xlabel( histogram_properties.x_axis_title, CMS.x_axis_title )
    plt.ylabel( histogram_properties.y_axis_title, CMS.y_axis_title )
    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )
    if show_title:
        plt.title( histogram_properties.title, CMS.title, loc='right', )
        
    if not axes:
        return
    # CMS text
    # note: fontweight/weight does not change anything as we use Latex text!!!
    logo_location = (0.05, 0.98)
    prelim_location = (0.05, 0.92)
    additional_location = (0.95, 0.98)
    loc = histogram_properties.cms_logo_location
    if loc == 'right':
        logo_location = (0.95, 0.98)
        prelim_location = (0.95, 0.92)
        additional_location = (0.95, 0.86)
        
    plt.text(logo_location[0], logo_location[1], r"\textbf{CMS}", 
             transform=axes.transAxes, fontsize=42,
             verticalalignment='top',horizontalalignment=loc)
    if histogram_properties.preliminary:
        plt.text(prelim_location[0], prelim_location[1], r"\emph{Preliminary}", 
                 transform=axes.transAxes, fontsize=42,
                 verticalalignment='top',horizontalalignment=loc)
    # channel text
    axes.text(additional_location[0], additional_location[1], 
              r"\emph{%s}" %histogram_properties.additional_text, 
              transform=axes.transAxes, fontsize=40, verticalalignment='top',
              horizontalalignment='right')
    
def adjust_axis_limits( axes, histogram_properties, histograms = [] ):
    x_limits = histogram_properties.x_limits
    if len( x_limits ) == 2:
        axes.set_xlim( xmin = x_limits[0], xmax = x_limits[1] )
        
    y_limits = histogram_properties.y_limits
    if len( y_limits ) == 2:
        axes.set_ylim( ymin = y_limits[0], ymax = y_limits[1] )
    else:
        y_max = get_best_max_y(histograms, x_limits=x_limits) * histogram_properties.y_max_scale
        axes.set_ylim( ymin = 0, ymax = y_max )
        
def get_best_max_y(histograms, include_error = True, x_limits = None):
    max_y =  max([__max__(histogram, include_error) for histogram in histograms])
    if x_limits and len(x_limits) == 2:
        x_min, x_max = x_limits
        all_y = []
        add_y = all_y.extend
        for histogram in histograms:
            ys = [y for x,y in zip(histogram.x(), histogram.y()) if x > x_min and x < x_max]
            add_y(ys)
        max_y = max(all_y)
    return max_y

def __max__(plotable, include_error = True):
    if isinstance(plotable, Hist):
        return plotable.max(include_error = include_error)
    if isinstance(plotable, Graph):
        ve = graph_to_value_errors_tuplelist(plotable)
        if not include_error:
            return max([v for v,_,_ in ve])
        return max( [v + err_high for v, _, err_high in ve] )

def get_best_min_y(histograms, include_error = True, x_limits = None):
    return min([histogram.min(include_error = include_error) for histogram in histograms])

def check_save_folder(save_folder):
    '''
        Checks and fixes (if necessary) the save folder
    '''
    # save_folder should end with an '/'
    if not save_folder.endswith('/'):
        save_folder += '/'
    # save_folder should exist
    make_folder_if_not_exists(save_folder)
    
    return save_folder

def adjust_ratio_ticks( axis, n_ticks = 3 ):
    # dynamic tick placement
    ticks = axis.get_ticklocs()
    tick_min, tick_max = ticks[0], ticks[-1]
    # limit to 3 ticks
    tick_distance = abs( tick_max - tick_min ) / ( n_ticks + 1 )
    includes_one = tick_max > 1 and tick_min < 1
    if includes_one:
        axis.set_major_locator( FixedLocator( [tick_min + tick_distance/2, 1, tick_max - tick_distance/2] ) )
    else:
        axis.set_major_locator( MultipleLocator( tick_distance ) )
        axis.set_minor_locator( MultipleLocator( tick_distance / 2 ) )

