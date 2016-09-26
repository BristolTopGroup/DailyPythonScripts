'''
Created on 3 May 2013

@author: kreczko
'''
import matplotlib as mpl
from tools.file_utilities import make_folder_if_not_exists
from tools.file_utilities import saveHistogramsToROOTFile
from tools.hist_utilities import spread_x, graph_to_value_errors_tuplelist
from tools.hist_utilities import get_histogram_ratios
mpl.use('agg')
import matplotlib.pyplot as plt
import rootpy.plotting.root2matplotlib as rplt
from rootpy.plotting import HistStack, Hist, Graph
from config import CMS
from matplotlib.patches import Rectangle
from copy import deepcopy
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator, FixedLocator
from itertools import cycle, combinations
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
    xerr = False
    integerXVariable = False
    #If True (the default) then plot bins with zero content otherwise only
    #    show bins with nonzero content.
    emptybins = False
    formats = ['png', 'pdf']
    path = ''
    fix_to_zero = False

    
    def __init__( self, dictionary = {}, **kwargs ):
        dictionary.update(kwargs)
        for name, value in dictionary.iteritems():
            if hasattr( self, name ):
                setattr( self, name, value )

# prototype
class PlotConfig:
    '''
        Class to read a JSON file and extract information from it.
        It creates HistSets and plot_options, essential replacing the main
        functionality of the bin/plot script.
    '''
    general_options = ['files', 'histograms', 'labels', 'plot_type', 'output_folder',
                  'output_format', 'command', 'data_index', 'normalise',
                  'show_ratio', 'show_stat_errors_on_mc', 'colours', 'name_prefix']
    
    def __init__( self, config_file, **kwargs ):
        self.config_file = config_file

class Plot(object):
    '''
        A class to define a plot
    '''
    delegate_attr = attribute_names=['name', 'title', 'formats']
    def __init__(self, histograms, properties, **kwargs):
        self.__draw_method = 'errorbar'
        self.__properties = properties
        self._path = properties.path
        self.__histograms = histograms
        if self._path != '' and not self._path.endswith('/'):
            self._path += '/'
        self.__errorbands = []
        if kwargs.has_key('errorbands'):
            self.__errorbands = kwargs.pop('errorbands')

    def add_error_band(self, errorband):
        self.__errorbands.append(errorband)

    @property
    def errorbands(self):
        return self.__errorbands

    @property
    def properties(self):
        return self.__properties

    def save(self):
        make_folder_if_not_exists(self._path)
        for f in self.__properties.formats:
            file_name = '{path}{name}.{format}'
            file_name = file_name.format(
                            path = self._path,
                            name = self.__properties.name,
                            format = f,
                            )
            plt.savefig(file_name)

    def cleanup(self):
        # clear current figure and axes
        plt.clf()
        plt.cla()
        plt.close()

    def __enter__(self):
        self.cleanup()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()

    @property
    def draw_method(self):
        return self.__draw_method

    @draw_method.setter
    def draw_method(self, method):
        if method in rplt.__dict__.keys():
            self.__draw_method = method
        else:
            raise ValueError('Invalid draw method')

    @property
    def histograms(self):
        return self.__histograms

    @property
    def show_ratios(self):
        return self.__properties.has_ratio and len(self.__histograms) > 1

    @property
    def fix_to_zero(self):
        return self.__properties.fix_to_zero

#     def __getattr__(self, name):
#         print name
#         if name in Plot.delegate_attr:
#             return getattr(self.__properties, name)

class ErrorBand(object):

    def __init__(self, name, lower, upper):
        self.__name = name
        self.__lower = lower
        self.__upper = upper
        self.__zorder = 999

    @property
    def name(self):
        return self.__name

    def draw(self, axes,
             facecolor = '0.75', # grey
             alpha = 0.5,
             hatch = '/',
             zorder = 999,):
        rplt.fill_between( self.__upper,
                           self.__lower, axes, facecolor = facecolor,
                           alpha = alpha, hatch = hatch,
                           zorder = zorder )


def make_data_mc_comparison_plot( histograms = [],
                                 histogram_lables = [],
                                 histogram_colors = [],
                                 histogram_properties = Histogram_properties(),
                                 data_index = 0,
                                 save_folder = 'plots/',
                                 save_as = ['pdf'],
                                 normalise = False,
                                 show_ratio = False,
                                 show_stat_errors_on_mc = False,
                                 draw_vertical_line = 0,
                                 systematics_for_ratio = None
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
    axes=None
    if show_ratio:
        ratio = data.Clone( 'ratio' )
        sumHists = sum( stack.GetHists() )
        for bin_i in range(1,sumHists.GetNbinsX()):
            sumHists.SetBinError(bin_i,0)
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
    rplt.errorbar( data, emptybins = histogram_properties.emptybins, axes = axes,
                   xerr = histogram_properties.xerr,
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

    if len( x_limits ) >= 2:
        axes.set_xlim( xmin = x_limits[0], xmax = x_limits[-1] )
    if len( y_limits ) >= 2:
        axes.set_ylim( ymin = y_limits[0], ymax = y_limits[-1] )
    else:
        y_max = get_best_max_y(histograms_, x_limits=x_limits) * histogram_properties.y_max_scale
        print ("Chosen limits : ",0,y_max)
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
        ax1.axhline(y=1, linewidth = 1)
        set_labels( plt, histogram_properties, show_x_label = True, show_title = False )
        plt.ylabel( r'$\frac{\mathrm{data}}{\mathrm{pred.}}$', CMS.y_axis_title )
        ax1.yaxis.set_label_coords(-0.115, 0.8)
        rplt.errorbar( ratio, emptybins = histogram_properties.emptybins, axes = ax1,
                       xerr = histogram_properties.xerr,
                       elinewidth = 1.5, capsize = 5, capthick = 1.5 )
        if len( x_limits ) >= 2:
            ax1.set_xlim( xmin = x_limits[0], xmax = x_limits[-1] )
        if len( histogram_properties.ratio_y_limits ) >= 2:
            ax1.set_ylim( ymin = histogram_properties.ratio_y_limits[0],
                      ymax = histogram_properties.ratio_y_limits[-1] )

        # dynamic tick placement
        adjust_ratio_ticks(ax1.yaxis, n_ticks = 3, y_limits = histogram_properties.ratio_y_limits)

        if histogram_properties.integerXVariable :
            ax1.tick_params(axis='x',which='minor',bottom='off',top='off')

        if systematics_for_ratio != None:
            plusErrors = [x+1 for x in systematics_for_ratio]
            minusErrors = [1-x for x in systematics_for_ratio]
            print plusErrors
            print minusErrors

            ratioPlusError = ratio.Clone( 'plus' )
            ratioMinusError = ratio.Clone( 'minus' )
            for bin_i in range( 1, ratioPlusError.GetNbinsX()+1 ):
                ratioPlusError.SetBinContent( bin_i, plusErrors[bin_i-1] )
                ratioMinusError.SetBinContent( bin_i, minusErrors[bin_i-1] )
            rplt.fill_between( ratioPlusError, ratioMinusError, axes,
                               alpha = 0.3, hatch = '//',
                               facecolor = 'Black',
                               zorder = len(histograms_) + 1 )

    if CMS.tight_layout:
        plt.tight_layout()
    
    for save in save_as:
        if save == 'root':
            saveHistogramsToROOTFile( data, stack,save_folder + histogram_properties.name + '.' + save )
        else:
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
    rplt.errorbar( ratio, xerr = True,
                   emptybins = histogram_properties.emptybins,
                   axes = ax1 )
    if len( x_limits ) == 2:
        ax1.set_xlim( xmin = x_limits[0], xmax = x_limits[1] )
    if len( histogram_properties.ratio_y_limits ) == 2:
            ax1.set_ylim( ymin = histogram_properties.ratio_y_limits[0],
                      ymax = histogram_properties.ratio_y_limits[1] )
    else:
        ax1.set_ylim( ymin = -0.5, ymax = 4 )
    # dynamic tick placement
    adjust_ratio_ticks(ax1.yaxis, n_ticks = 3)
    ax1.set_ylim( ymin = -0.5, ymax = 4 )
    
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
        if fill_area:
            shape.fillcolor = colour
            shape.fillstyle = 'solid'
            shape.legendstyle = 'F'
        else:
            shape.linecolor = colour
            shape.legendstyle = 'F'
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
        rplt.errorbar( graph, axes = axes )

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
            rplt.errorbar( ratio, xerr = True,
                           emptybins = histogram_properties.emptybins,
                           axes = ax1 )
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

def make_plot( histogram, histogram_properties = Histogram_properties(),
                                 save_folder = 'plots/',
                                 save_as = ['pdf', 'png'],
                                 normalise = False,
                                 draw_errorbar = False,
                                 draw_legend = True
                                 ):
    save_folder = check_save_folder(save_folder)
    histogram.SetTitle(histogram_properties.title)
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
        rplt.errorbar( histogram, emptybins = histogram_properties.emptybins,
                       axes = axes, elinewidth = 2, capsize = 10, capthick = 2 )
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
                            save_as = ['pdf', 'png'],
                            match_models_to_measurements = False ):
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
    markers = [20, 21, 22, 33, 23, 29]
    markercycler = cycle( markers )
    # matplotlib
#     lines = ["-", "--", "-.", ":"]
    # rootpy
    lines = ["dashed"]
    linecycler = cycle( lines )
    
    for label, histogram in models.iteritems():
        if not histogram: # skip empty ones
            continue
        histogram.linewidth = 2 
        histogram.color = next( colorcycler )
        histogram.linestyle = next( linecycler ) 
        rplt.hist( histogram, axex = axes, label = label )
    
    if match_models_to_measurements:
        colorcycler = cycle( colors )
        markercycler = cycle( markers )
        linecycler = cycle( lines )

    for label, histogram in measurements.iteritems():
        histogram.markersize = 2
        histogram.markerstyle = next( markercycler )
        histogram.color = next( colorcycler )
        rplt.errorbar( histogram, axes = axes, label = label ,
                        elinewidth = 2,
                       yerr = show_measurement_errors,
                       xerr = histogram_properties.xerr )
    
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
    elif loc == 'left':
        logo_location = (0.05, 0.98)
        prelim_location = (0.05, 0.92)
        additional_location = (0.05, 0.86)      
        
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
              horizontalalignment=loc)

def adjust_axis_limits( axes, histogram_properties, histograms = [], adjust_y = True ):
    x_limits = histogram_properties.x_limits
    if len( x_limits ) == 2:
        axes.set_xlim( xmin = x_limits[0], xmax = x_limits[1] )
        
    y_limits = histogram_properties.y_limits
    if adjust_y:
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
            ys = [y+yerr for x,y,yerr in zip(histogram.x(), histogram.y(), histogram.yerrh()) if x > x_min and x < x_max]
            add_y(ys)
        max_y = max(all_y)
    return max_y

def __max__(plotable, include_error = True):
    if plotable is None:
        return 0
    if plotable.__class__.__name__ == 'Hist':
        return plotable.max(include_error = include_error)
    if plotable.__class__.__name__ == 'Graph':
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

def adjust_ratio_ticks( axis, n_ticks = 3, y_limits = None ):
    # dynamic tick placement
    ticks = axis.get_ticklocs()
    tick_min, tick_max = ticks[0], ticks[-1]

    # Check if these are outside of the y_limits.  Use those instead if so.
    if y_limits != None:
        if tick_min < y_limits[0] and tick_max > y_limits[-1]:
            tick_min = y_limits[0]
            tick_max = y_limits[-1]

    # limit to 3 ticks
    tick_distance = abs( tick_max - tick_min ) / ( n_ticks + 1 )
    includes_one = tick_max > 1 and tick_min < 1
    if includes_one:
        axis.set_major_locator( FixedLocator( [round(tick_min + tick_distance/2,1), 1, round(tick_max - tick_distance/2,1)] ) )
    else:
        axis.set_major_locator( MultipleLocator( tick_distance ) )
        axis.set_minor_locator( MultipleLocator( tick_distance / 2 ) )

def compare_histograms(plot):
    histograms = plot.histograms
    properties = plot.properties
    # the cycling needs to be better
    colors = ['green', 'red', 'blue', 'magenta']
    colorcycler = cycle( colors )
    markers = [20, 23, 22, 33, 21, 29]
    markercycler = cycle( markers )

    plt.figure( figsize = CMS.figsize, dpi = CMS.dpi, facecolor = CMS.facecolor )
    axes = plt.axes()
    if plot.show_ratios:
        gs = gridspec.GridSpec( 2, 1, height_ratios = [5, 1] )
        axes = plt.subplot( gs[0] )
    plot_function = rplt.__dict__[plot.draw_method]
    for label, histogram in histograms.items():
        histogram.markersize = 2
        histogram.markerstyle = next( markercycler )
        histogram.color = next( colorcycler )
        plot_function( histogram, axes = axes, label = label,
                       emptybins = properties.emptybins,
                       yerr = True,
                       xerr = properties.xerr, elinewidth = 2 )

    set_labels( plt, properties, show_x_label = not plot.show_ratios, axes = axes )
    errorbands = plot.errorbands
    handles, labels = axes.get_legend_handles_labels()
    for band in errorbands:
        band.draw(axes)
        p1 = Rectangle( ( 0, 0 ), 1, 1, fc = "0.75", alpha = 0.5, hatch = '/' ,
                        label = band.name)
        handles.append( p1 )
        labels.append( band.name )
    adjust_axis_limits( axes, properties, histograms.values() )

    # or sort legend by labels
    import operator
    hl = sorted(zip(handles, labels),
            key=operator.itemgetter(1))
    handles2, labels2 = zip(*hl)
    l1 = axes.legend(
        handles2, labels2, numpoints = 1,
        frameon = properties.legend_color,
        bbox_to_anchor = properties.legend_location,
        bbox_transform=plt.gcf().transFigure,
        prop = CMS.legend_properties,
        ncol = properties.legend_columns,
        )
    l1.set_zorder(102)

    ratios = {}
    if plot.show_ratios:
        for (l1, l2) in combinations(histograms.keys(), 2):
            label = '{0}/{1}'.format(l1, l2)
            h = histograms[l1].clone()
            h.Divide(histograms[l2])
            h.SetName(label)
            ratios[label] = h
        plt.setp( axes.get_xticklabels(), visible = False )
        axes_ratio = plt.subplot( gs[1] )
        axes_ratio.minorticks_on()
        axes_ratio.grid( True, 'major', linewidth = 1)
        axes_ratio.axhline(y=1, linewidth = 1, linestyle = 'dashed', color = 'black')
        set_labels( plt, properties, show_x_label = True, show_title = False )
        plt.ylabel('ratio')
        axes_ratio.yaxis.set_label_coords(-0.115, 0.8)
        for label, ratio in ratios.items():
            plot_function( ratio, xerr = properties.xerr,
                   emptybins = properties.emptybins,
                   axes = axes_ratio, elinewidth = 2 )
        adjust_ratio_ticks(axes_ratio.yaxis, n_ticks = 3)
        adjust_axis_limits( axes_ratio, properties, ratios.values(), adjust_y = False )

    if CMS.tight_layout:
        plt.tight_layout()

    plot.save()
    plt.close()
