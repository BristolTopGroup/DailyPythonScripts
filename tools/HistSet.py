'''
Created on 8 Jan 2015

@author: kreczko
'''
import sys
from tools.plotting import Histogram_properties, make_shape_comparison_plot,\
    make_data_mc_comparison_plot
from ROOT_utils import get_histogram_from_file
import types
from tools.hist_utilities import conditional_rebin

class HistSet():
    '''
    Class to compile sets of histograms for plotting
    '''
    def __init__( self, name, hist_inputs, output_hist_labels ):
        self.name = name
        self.inputs = hist_inputs
        self.stored_inputs = False
        self.histograms = []
        self.labels = output_hist_labels
        
        self.__store_inputs__()
        
    def plot( self, plot_options = {} ):
        '''
            Plots the stored histograms based on the plot options
        '''
        # defaults
        file_name = self.name
        alpha = 0.5
        fill_area = True
        if plot_options.has_key('output_file'):
            file_name = plot_options['output_file']
        output_format = plot_options['output_format'] 
        output_folder = plot_options['output_folder']
        
        plot_type = plot_options['plot_type']
        
        if plot_options.has_key('fill_area'):
            fill_area = plot_options['fill_area']
        if plot_options.has_key('alpha'):
            alpha = plot_options['alpha']
        
        histogram_properties = Histogram_properties(plot_options)
        histogram_properties.name = file_name
        if plot_options.has_key('rebin') and plot_options['rebin'] > 1:
            rebin = plot_options['rebin']
            is_list = isinstance(rebin, types.ListType)
            for i,hist in enumerate(self.histograms):
                if is_list:
                    self.histograms[i] = conditional_rebin(hist, rebin)
                else:
                    hist.rebin(rebin)
        
        colours = ['green', 'yellow', 'magenta', 'red', 'black']
        if plot_options.has_key('colours'):
            colours = plot_options['colours']
        
        if plot_type == 'shape_comparison':
            make_shape_comparison_plot( shapes = self.histograms,
                                       names = self.labels,
                                       colours = colours,
                                       histogram_properties = histogram_properties,
                                       fill_area = fill_area,
                                       make_ratio = True,
                                       alpha = alpha,
                                       save_folder = output_folder,
                                       save_as = output_format )
        elif plot_type == 'data_mc_comparison':
            make_data_mc_comparison_plot( histograms = self.histograms,
                                         histogram_lables = self.labels,
                                         histogram_colors = colours,
                                         histogram_properties = histogram_properties,
                                         data_index = 0,
                                         save_folder = output_folder,
                                         save_as = output_format,
                                         normalise = False,
                                         show_ratio = True,
                                         show_stat_errors_on_mc = True,
                                         draw_vertical_line = 0 )
        else:
            print 'Plot type "%s" not known, exiting.' % plot_type
            sys.exit()
    
    def __store_inputs__( self ):
        ''' 
            Read the inputs and get the histograms from the files
        '''
        if self.stored_inputs:  # do not repeat reads
            return
        for i in self.inputs:
            hist = get_histogram_from_file( histogram_path = i[1],
                                           input_file = i[0] )
            self.histograms.append( hist )
        self.stored_inputs = True
