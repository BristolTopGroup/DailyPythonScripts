'''
Created on 3 Mar 2013

@author: kreczko
'''
# take input folder
# read all *.txt
# but the fit is not saved :(
# I could save the fit using EVAL ...
from __future__ import division
from ROOT import gROOT
from optparse import OptionParser
from glob import glob
import sys

import numpy
from numpy import frompyfunc
from pylab import plot
from array import array

from rootpy.plotting import Hist
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt


from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from tools.hist_utilities import hist_to_value_error_tuplelist
from tools.hist_utilities import value_error_tuplelist_to_hist
from config import CMS

from matplotlib import rc
rc('font',**CMS.font)
rc('text', usetex=True)

def get_data(files, subset = ''): 
    # this takes a LOT of memory, please use subset!!
    all_data = []
    extend = all_data.extend
    read = read_data_from_JSON
    for f in files:
        data = read(f)
        
        if subset:
            for entry in data:  # loop over all data entries
                extend(entry[subset])
        else:
            extend(data)
                
    return all_data

def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step
        
def plot_pull(pulls, bin_index = None, n_bins = 1):
    min_x, max_x = min(pulls), max(pulls)
    abs_max = int(max(abs(min_x), max_x))
    n_x_bins = 2 * abs_max * 10  # bin width = 0.1
#    print n_x_bins, -abs_max, abs_max
    h_pull = Hist(n_x_bins, -abs_max, abs_max)
    filling = h_pull.Fill
    
    for pull_index, pull in enumerate(pulls):
            
        if not bin_index is None:
            matches_bin = (pull_index - bin_index) %(n_bins) == 0
            if pull_index < n_bins:#first set correction
                matches_bin = pull_index == bin_index
            if not matches_bin:
                continue
        filling(pull)
    
    stats = len(pulls)
#    print stats
#    h_list = hist_to_value_error_tuplelist(h_pull)
#    print h_list
#    print len(hist_data), min(hist_data), max(hist_data)
    if bin_index is None:
        plot_h_pull(h_pull, stats = stats, name = 'pull_from_files_all_bins_stats_%d' % stats)
    else:
        plot_h_pull(h_pull, stats = stats, name = 'pull_from_files_bin_%d_stats_%d' % (bin_index, stats))
    
def plot_pull_from_list():
    stats = 19596500
    bin_width = (2.0 * hist_max_x) / hist_n_bins
    print hist_n_bins, bin_width
    bin_edges = list(drange(hist_min_x, hist_max_x, bin_width))
    print bin_edges
    print len(bin_edges)
    h_pull = value_error_tuplelist_to_hist(hist_data, bin_edges)
    plot_h_pull(h_pull, stats = stats, name = 'pull_from_list' )    

def plot_h_pull(h_pull, stats = 19596500, name = 'pull_test'):
    global output_folder, output_formats
    h_pull.Fit('gaus', 'WWSQ')
    fit_pull = h_pull.GetFunction('gaus')
    mean = (fit_pull.GetParameter(1), fit_pull.GetParError(1))
    sigma = (fit_pull.GetParameter(2), fit_pull.GetParError(2))
    print 'Fit data for "' + name + '"'
    print 'A:', fit_pull.GetParameter(0), '+-', fit_pull.GetParError(0)
    print 'mean:', fit_pull.GetParameter(1), '+-', fit_pull.GetParError(1)
    print 'sigma:', fit_pull.GetParameter(2), '+-', fit_pull.GetParError(2)
    
    plt.figure(figsize=(16, 16), dpi=200, facecolor='white')
    axes = plt.axes()
    h_pull.SetMarkerSize(CMS.data_marker_size)
    rplt.errorbar(h_pull, xerr=True, emptybins=True, axes=axes)
    
    x = numpy.linspace(fit_pull.GetXmin(), fit_pull.GetXmax(), fit_pull.GetNpx()*4)#*4 for a very smooth curve
    function_data = frompyfunc(fit_pull.Eval, 1, 1)
    plot(x, function_data(x), axes=axes, color='red', linewidth=2)
    
    
    plt.xlabel('$\\frac{\mathrm{unfolded} - \mathrm{true}}{\sigma}$', CMS.x_axis_title)
    plt.ylabel('number of toy experiments', CMS.y_axis_title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    plt.title('Pull distribution for SVD unfolding', CMS.title)
    text = 'entries = %d \n mean = $%.2f \pm %.2f$ \n $\sigma = %.2f \pm %.2f$' % (stats, mean[0], mean[1], sigma[0], sigma[1])
    axes.text(0.6, 0.8, text,
        verticalalignment='bottom', horizontalalignment='left',
        transform=axes.transAxes,
        color='black', fontsize=40, bbox=dict(facecolor='white', edgecolor='none', alpha=0.5))
    plt.tight_layout()  
    
    for save in output_formats:
        plt.savefig(output_folder + name + '.' + save)        

def plot_difference(difference):
    global output_folder, output_formats
    stats = len(difference)    
    values, errors = [],[]
    add_value = values.append
    add_error = errors.append
    for value, error in difference:
        add_value(value)
        add_error(error)
    min_x, max_x = min(values), max(values)
    abs_max = int(max(abs(min_x), max_x))
#    n_x_bins = 2 * abs_max * 10    
    h_values = Hist(100, -abs_max, abs_max)
    fill_value = h_values.Fill
    for value in values:
        fill_value(value)
        
    plt.figure(figsize=(16, 16), dpi=200, facecolor='white')
    axes = plt.axes()
    h_values.SetMarkerSize(CMS.data_marker_size)
    rplt.errorbar(h_values, xerr=True, emptybins=True, axes=axes)
    
    plt.xlabel('$\mathrm{unfolded} - \mathrm{true}$', CMS.x_axis_title)
    plt.ylabel('number of toy experiments', CMS.y_axis_title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    plt.title('SVD unfolding performance', CMS.title)
    plt.tight_layout()  
    
    for save in output_formats:
        plt.savefig(output_folder + 'difference_stats_' + str(stats) + '.' + save)   
        
    min_x, max_x = min(errors), max(errors)
    h_errors = Hist(1000, min_x, max_x)
    fill_value = h_errors.Fill
    for error in errors:
        fill_value(error)  
        
    plt.figure(figsize=(16, 16), dpi=200, facecolor='white')
    axes = plt.axes()
    h_errors.SetMarkerSize(CMS.data_marker_size)
    rplt.errorbar(h_errors, xerr=True, emptybins=True, axes=axes)
    
    plt.xlabel('$\sigma(\mathrm{unfolded} - \mathrm{true})$', CMS.x_axis_title)
    plt.ylabel('number of toy experiments', CMS.y_axis_title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    plt.title('SVD unfolding performance', CMS.title)
    plt.tight_layout()  
    
    for save in output_formats:
        plt.savefig(output_folder + 'difference_errors_stats_' + str(stats) + '.' + save)  
        
if __name__ == "__main__":
    gROOT.SetBatch(True)
    gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    parser = OptionParser()
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                      help="set the variable to analyse (MET, HT, ST, MT, WPT)")
    parser.add_option("-s", "--centre-of-mass-energy", dest="CoM", default=8,
                      help="set the centre of mass energy for analysis. Default = 8 [TeV]", type=int)
    parser.add_option("-i", "--input-folder", type='string',
                      dest="input_folder", help="location of the pull data")
    parser.add_option("-o", "--output",
                      dest="output_folder", default='plots_unfolding_pull',
                      help="output folder for unfolding pull plots")
    parser.add_option("-c", "--channel", type='string',
                      dest="channel", default='electron',
                      help="channel to be analysed: electron|muon|both")

    (options, args) = parser.parse_args()
    
    if not options.input_folder:
        sys.exit('No input folder specified. Please do so manually using -i option.')

    if options.CoM == 8:
        from config.variable_binning_8TeV import bin_edges
        import config.cross_section_measurement_8TeV as measurement_config
    elif options.CoM == 7:
        from config.variable_binning_7TeV import bin_edges
        import config.cross_section_measurement_7TeV as measurement_config
    else:
        sys.exit( 'Unknown centre of mass energy' )

    centre_of_mass = options.CoM
    variable = options.variable
    output_folder = options.output_folder + '/' + variable + '/' + options.channel + '/'
    make_folder_if_not_exists(output_folder)
    output_formats = ['pdf']

    bins = array('d', bin_edges[variable])
    nbins = len(bins) - 1

    print 'Producing unfolding pull plots for %s variable, channel: %s. \nOutput folder: %s' % (variable, options.channel, output_folder)
    
    files = glob(options.input_folder + '/*_' + options.channel + '*_*.txt')
    if not files:
        sys.exit('No *.txt files found in input directory.')
    
    pulls = get_data(files, subset='pull')

    for bin_i, bin in enumerate(bins):
        plot_pull(pulls, bin_index = bin_i, n_bins = nbins)

    plot_pull(pulls)
    del pulls #deleting to make space in memory
#    plot_pull_from_list()

    difference = get_data(files, subset='difference')
    plot_difference(difference)
