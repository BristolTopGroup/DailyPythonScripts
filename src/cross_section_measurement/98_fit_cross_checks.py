from config import CMS
from optparse import OptionParser
import config.cross_section_measurement_8TeV as measurement_config
from config.latex_labels import b_tag_bins_latex
from config.cross_section_measurement_common import translate_options
from config.variable_binning_8TeV import bin_edges, variable_bins_ROOT
from tools.ROOT_utililities import get_histograms_from_files
from tools.file_utilities import read_data_from_JSON
from tools.plotting import Histogram_properties, make_control_region_comparison
from tools.hist_utilities import prepare_histograms, \
    value_error_tuplelist_to_hist, rebin_asymmetric
from rootpy.plotting import Hist
from ROOT import Double
from uncertainties import ufloat

from matplotlib import pyplot as plt
import rootpy.plotting.root2matplotlib as rplt
from rootpy.plotting import Hist2D
import matplotlib.gridspec as gridspec
import numpy as np
import linecache

def get_fit_results(variable, channel):
    global path_to_JSON, category, met_type
    fit_results = read_data_from_JSON(path_to_JSON + variable + '/fit_results/' + category + '/fit_results_' + channel + '_' + met_type + '.txt')
    return fit_results

def make_correlation_plot_from_file(channel, variable, normalisation, title, x_title, y_title, x_limits, y_limits, rebin=1, save_folder='plots/fitchecks/', save_as = ['pdf', 'png']):

#global b_tag_bin
    x_array = []
    y_array = []
    parameters = ["signal", "vJets", "QCD"]
    
    file=open("plots/fitchecks/correlation_%s.txt" %variable, "r")
    #cycle through the lines in the file 
    for line_number, line in enumerate(file):
        #for now, only make plots for the fits for the central measurement
        if "central" in line:
            break
    file.close()
    
    for variable_bin in variable_bins_ROOT[variable]:
        weights = {}
        if channel == 'electron':
                #matrix we want is 10 lines below the line with the measurement ("central")
            matrix_line = linecache.getline("plots/fitchecks/correlation_%s.txt" %variable, line_number+((variable_bins_ROOT[variable].index(variable_bin)+1)*10))
            weights["QCD_QCD"] = matrix_line.split()[2]
            weights["QCD_vJets"] = matrix_line.split()[3]
            weights["QCD_signal"] = matrix_line.split()[4]
        
            matrix_line = linecache.getline("plots/fitchecks/correlation_%s.txt" %variable, line_number+((variable_bins_ROOT[variable].index(variable_bin)+1)*10)+1)    
            weights["vJets_QCD"] = matrix_line.split()[2]
            weights["vJets_vJets"] = matrix_line.split()[3]
            weights["vJets_signal"] = matrix_line.split()[4]
            
            matrix_line = linecache.getline("plots/fitchecks/correlation_%s.txt" %variable, line_number+((variable_bins_ROOT[variable].index(variable_bin)+1)*10)+2)
            weights["signal_QCD"] = matrix_line.split()[2]
            weights["signal_vJets"] = matrix_line.split()[3]
            weights["signal_signal"] = matrix_line.split()[4]
        
        if channel == 'muon':
            matrix_line = linecache.getline("plots/fitchecks/correlation_%s.txt" %variable, line_number+ (((len(variable_bins_ROOT[variable]))*10) + ((variable_bins_ROOT[variable].index(variable_bin)+1)*10)))
            weights["QCD_QCD"] = matrix_line.split()[2]
            weights["QCD_vJets"] = matrix_line.split()[3]
            weights["QCD_signal"] = matrix_line.split()[4]
        
            matrix_line = linecache.getline("plots/fitchecks/correlation_%s.txt" %variable, line_number+ (((len(variable_bins_ROOT[variable]))*10) + ((variable_bins_ROOT[variable].index(variable_bin)+1)*10))+1)    
            weights["vJets_QCD"] = matrix_line.split()[2]
            weights["vJets_vJets"] = matrix_line.split()[3]
            weights["vJets_signal"] = matrix_line.split()[4]
            
            matrix_line = linecache.getline("plots/fitchecks/correlation_%s.txt" %variable, line_number+ (((len(variable_bins_ROOT[variable]))*10) + ((variable_bins_ROOT[variable].index(variable_bin)+1)*10))+2)
            weights["signal_QCD"] = matrix_line.split()[2]
            weights["signal_vJets"] = matrix_line.split()[3]
            weights["signal_signal"] = matrix_line.split()[4]
        
        histogram_properties=Histogram_properties()
        histogram_properties.title = title
        histogram_properties.name='Correlations_' + channel + '_' + variable + '_' + variable_bin
        histogram_properties.y_axis_title = y_title
        histogram_properties.x_axis_title = x_title
        histogram_properties.y_limits = y_limits
        histogram_properties.x_limits = x_limits
        histogram_properties.mc_error = 0.0
        histogram_properties.legend_location = 'upper right'
     
        a = Hist2D(3, 0, 3, 3, 0, 3)
        for i in range(len(parameters)):
            for j in range(len(parameters)):
                a.fill(float(i), float(j), float(weights["%s_%s" %(parameters[i], parameters[j])]))
        plt.figure(figsize=(16, 16), dpi=200, facecolor='white')
        fig, ax = plt.subplots(nrows=1, ncols=1)
        rplt.hist2d(a)
        plt.subplots_adjust(right=0.8)
       
        plt.ylabel(histogram_properties.y_axis_title)
        plt.xlabel(histogram_properties.x_axis_title)
        plt.title(histogram_properties.title)
        x_limits = histogram_properties.x_limits
        y_limits = histogram_properties.y_limits
        ax.set_xticklabels(parameters)
        ax.set_yticklabels(parameters)
        ax.set_xticks([0.5, 1.5, 2.5])
        ax.set_yticks([0.5, 1.5, 2.5])
        plt.setp(ax.get_xticklabels(), visible=True)
        plt.setp(ax.get_yticklabels(), visible=True)

        im = rplt.imshow(a, axes=ax, vmin=-1.0, vmax=1.0)
        cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
       
        fig.colorbar(im, cax=cbar_ax)

        for xpoint in range(len(parameters)):
           for ypoint in range(len(parameters)):
        #for xpoint, ypoint in zip(x, y):
               ax.annotate('{:.2f}'.format(float(weights["%s_%s" %(parameters[xpoint], parameters[ypoint])])), (xpoint+0.5,ypoint+0.5), ha='center', va='center', bbox=dict(fc='white', ec='none'))
      
        for save in save_as:
           plt.savefig(save_folder + histogram_properties.name + '.' + save)
        plt.close()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data/',
                  help="set path to JSON files")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                  help="set the variable to analyse (MET, HT, ST, MT)")
    parser.add_option("-o", "--output_folder", dest="output_folder", default='plots/fitchecks/',
                  help="set path to save plots")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type used in the analysis of MET-dependent variables")
    parser.add_option("-c", "--category", dest="category", default='central',
                      help="set the category to take the fit results from (default: central)")
    parser.add_option("-n", "--normalise_to_fit", dest="normalise_to_fit", action="store_true",
                  help="normalise the MC to fit results")
#    parser.add_option("-i", "--use_inputs", dest="use_inputs", action="store_true",
#                  help="use fit inputs instead of fit results")
    
    (options, args) = parser.parse_args()
    path_to_JSON = options.path + '/' + '8TeV/'
    output_folder = options.output_folder
    normalise_to_fit = options.normalise_to_fit
    category = options.category
    met_type = translate_options[options.metType]

    CMS.title['fontsize'] = 40
    CMS.x_axis_title['fontsize'] = 50
    CMS.y_axis_title['fontsize'] = 50
    CMS.axis_label_major['labelsize'] = 40
    CMS.axis_label_minor['labelsize'] = 40
    CMS.legend_properties['size'] = 40
    
    histogram_files = {
            'electron' : measurement_config.data_file_electron,
            'muon' : measurement_config.data_file_muon,
            'TTJet': measurement_config.ttbar_category_templates[category],
            'V+Jets': measurement_config.VJets_category_templates[category],
            'QCD': measurement_config.electron_QCD_MC_file,  # this should also be category-dependent, but unimportant and not available atm
            'SingleTop': measurement_config.SingleTop_category_templates[category]
    }

    fit_results_electron = {
            'MET':get_fit_results('MET', 'electron'),
            'HT':get_fit_results('HT', 'electron'),
            'ST':get_fit_results('ST', 'electron'),
            'MT':get_fit_results('MT', 'electron'),
            'WPT':get_fit_results('WPT', 'electron')
            }
    fit_results_muon = {
            'MET':get_fit_results('MET', 'muon'),
            'HT':get_fit_results('HT', 'muon'),
            'ST':get_fit_results('ST', 'muon'),
            'MT':get_fit_results('MT', 'muon'),
            'WPT':get_fit_results('WPT', 'muon')
            }
    normalisations_electron, normalisations_muon = fit_results_electron, fit_results_muon
    
    #make correlation plots for electron and muon channel
    histogram_title = 'CMS Preliminary, $\mathcal{L}$ = 19.7 fb$^{-1}$ at $\sqrt{s}$ = 8 TeV \n e+jets, $\geq$4 jets'
    make_correlation_plot_from_file(channel='electron', variable=options.variable, normalisation=normalisations_electron, title=histogram_title, x_title='', y_title='', x_limits=[0,3], y_limits=[0,3], rebin=1, save_folder='plots/fitchecks/', save_as=['pdf', 'png'])
    histogram_title = 'CMS Preliminary, $\mathcal{L}$ = 19.7 fb$^{-1}$ at $\sqrt{s}$ = 8 TeV \n $\mu$+jets, $\geq$4 jets'
    make_correlation_plot_from_file(channel='muon', variable=options.variable, normalisation=normalisations_electron, title=histogram_title, x_title='', y_title='', x_limits=[0,3], y_limits=[0,3], rebin=1, save_folder='plots/fitchecks/', save_as=['pdf', 'png'])
