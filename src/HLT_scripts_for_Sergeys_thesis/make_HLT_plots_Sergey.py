from rootpy.io import File
from rootpy import asrootpy
# Most verbose log level

# import matplotlib
# matplotlib.use('AGG')

import rootpy.plotting.root2matplotlib as rplt
from rootpy import ROOTError

import matplotlib.pyplot as plt
# from matplotlib.ticker import AutoMinorLocator
# import config.summations as summations
from ROOT import TGraphAsymmErrors, TF1, TLegend, TLatex
from array import array
from config import CMS
from tools.ROOT_utils import set_root_defaults
import matplotlib.cm as cm
from matplotlib.ticker import FormatStrFormatter

import numpy
from numpy import frompyfunc
from pylab import plot

from matplotlib import rc
rc('text', usetex=True)

def make_jet_response_plot(input_file, response):
    global output_folder, output_formats, suffix
    jet_response_plot = asrootpy(input_file.Get(response))

    x_limits = [0, 200]
    y_limits = [0.8, 1.2]
    if '_eta' in response:
        x_limits = [-3, 3]
        x_title = '$\eta$(reco jet)'
    else:
        x_title = '$p_{\mathrm{T}}$(reco jet) [GeV]'

    y_title = '$p_{\mathrm{T}}$(reco jet)/$p_{\mathrm{T}}$(HLT jet)'
    save_as_name = response

    plt.figure(figsize=(20, 16), dpi=200, facecolor='white')

    ax0 = plt.axes()
    ax0.minorticks_on()
    ax0.grid(True, 'major', linewidth=2)
    ax0.grid(True, 'minor')
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    ax0.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax0.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax0.xaxis.labelpad = 12
    ax0.yaxis.labelpad = 12

    if '_prof' in response:
        rplt.errorbar(jet_response_plot, xerr=True, emptybins=True, axes=ax0, marker = 'o', ms = 15, mew=3, lw = 2)
    else:
        im = rplt.imshow(jet_response_plot, axes=ax0, cmap = cm.Blues)
        #plt.colorbar(im)
    ax0.set_xlim(x_limits)
    ax0.set_ylim(y_limits)

    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)

    plt.xlabel(x_title, CMS.x_axis_title)
    plt.ylabel(y_title, CMS.y_axis_title)
    plt.title(r'e+jets, CMS Preliminary, $\sqrt{s}$ = 8 TeV', CMS.title)
    if '_prof' in response:
        plt.legend(['data'], numpoints=1, loc='lower right', prop=CMS.legend_properties)

    plt.tight_layout()
    
    for output_format in output_formats:
        plt.savefig(output_folder + save_as_name + '_' + suffix + '.' + output_format)  

def make_jet_response_comparison_plot(input_files, response):
    global output_folder, output_formats, suffix
    
    if not '_prof' in response:
        print 'Can\'t make comparison scatter plots!'
        return
    
    jet_responses = {}
    for jet_response_name, file_name in input_files.iteritems():
        jet_responses.update({jet_response_name : asrootpy(file_name.Get(response))})

    x_limits = [0, 200]
    y_limits = [0.7, 1.3]
    if '_eta' in response:
        x_limits = [-3, 3]
        x_title = '$\eta$(reco jet)'
    else:
        x_title = '$p_{\mathrm{T}}$(reco jet) [GeV]'

    y_title = '$p_{\mathrm{T}}$(reco jet)/$p_{\mathrm{T}}$(HLT jet)'
    save_as_name = response

    plt.figure(figsize=(20, 16), dpi=200, facecolor='white')

    ax0 = plt.axes()
    ax0.minorticks_on()
    ax0.grid(True, 'major', linewidth=2)
    ax0.grid(True, 'minor')
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    ax0.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax0.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax0.xaxis.labelpad = 12
    ax0.yaxis.labelpad = 12
    jet_response_name_list = []
    
    marker_face_colours = {
                0 : 'black',
                1 : 'red',
                2 : 'blue',
                3 : 'none',
                4 : 'yellow'
                }
    marker_edge_colours = {
                0 : 'black',
                1 : 'red',
                2 : 'blue',
                3 : 'green',
                4 : 'yellow'
                }
    markers = {
                0 : 'o',
                1 : 'v',
                2 : '^',
                3 : 's',
                4 : '*'
    }
    fill_styles = {
                0 : 'full',
                1 : 'full',
                2 : 'full',
                3 : 'none',
                4 : 'full'
    }
    counter = 0
    for jet_response_name, jet_response in sorted(jet_responses.iteritems()):
        rplt.errorbar(jet_response, xerr=None, emptybins=True, axes=ax0, marker = markers[counter], fillstyle = fill_styles[counter],
            markerfacecolor = marker_face_colours[counter], markeredgecolor = marker_edge_colours[counter], ecolor = marker_edge_colours[counter], ms=15, mew=3, lw = 2)
        jet_response_name_list.append(jet_response_name)
        counter += 1

    ax0.set_xlim(x_limits)
    ax0.set_ylim(y_limits)

    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)

    plt.xlabel(x_title, CMS.x_axis_title)
    plt.ylabel(y_title, CMS.y_axis_title)
    plt.title(r'e+jets, CMS Preliminary, $\sqrt{s}$ = 8 TeV', CMS.title)
    plt.legend(jet_response_name_list, numpoints=1, loc='lower right', prop=CMS.legend_properties)

    plt.tight_layout()
    
    for output_format in output_formats:
        plt.savefig(output_folder + save_as_name + '_' + suffix + '.' + output_format)  

def make_single_efficiency_plot(hist_passed, hist_total, efficiency):
    global output_folder, output_formats, suffix

    x_limits, x_title, y_title, fit_function, fit_range = get_parameters(efficiency)

    plot_efficiency = asrootpy(TGraphAsymmErrors())
    plot_efficiency.Divide(hist_passed, hist_total, "cl=0.683 b(1,1) mode")

    fit_data = TF1("fit_data", fit_function, fit_range[0], fit_range[1])
    set_parameter_limits(efficiency, fit_data)
    try:
        plot_efficiency.Fit(fit_data, 'FECQ')
    except ROOTError, e:
        print e.msg
        pass
    plot_efficiency.SetMarkerSize(2)

    save_as_name = efficiency

    # plot with matplotlib
    plt.figure(figsize=(20, 16), dpi=200, facecolor='white')

    ax0 = plt.axes()
    ax0.minorticks_on()
    ax0.grid(True, 'major', linewidth=2)
    ax0.grid(True, 'minor')
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    
    ax0.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax0.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax0.xaxis.labelpad = 11
    #ax0.yaxis.labelpad = 20
    
    rplt.errorbar(plot_efficiency, xerr=True, emptybins=True, axes=ax0, marker = 'o', ms = 15, mew=3, lw = 2)
    
    ax0.set_xlim(x_limits)
    ax0.set_ylim([0.0,1.1])
    
    #add fits
    x = numpy.linspace(fit_data.GetXmin(), fit_data.GetXmax(), fit_data.GetNpx())
    function_data = frompyfunc(fit_data.Eval, 1, 1)
    plot(x, function_data(x), axes=ax0, color = 'red', linewidth = 2)
    
    
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)

    plt.xlabel(x_title, CMS.x_axis_title)
    plt.ylabel(y_title, CMS.y_axis_title)
    plt.title(r'e+jets, CMS Preliminary, $\sqrt{s}$ = 8 TeV', CMS.title)
    plt.legend(['data', 'fit'], numpoints=1, loc='lower right', prop=CMS.legend_properties)

    
    #add fit formulas
    ax0.text(0.2, 0.15, '$\epsilon$ = ' + get_fitted_function_str(fit_data, fit_function),
        verticalalignment='bottom', horizontalalignment='left',
        transform=ax0.transAxes,
        color='red', fontsize=60, bbox = dict(facecolor = 'white', edgecolor = 'none', alpha = 0.5))

    plt.tight_layout()
    
    for output_format in output_formats:
        plt.savefig(output_folder + save_as_name + '_' + suffix + '.' + output_format)  

      
def get_parameters(trigger_under_study):
    x_limits = [10, 100]
    x_title = '$p_{\mathrm{T}}$(jet) [GeV]'
    #y_title = '$\epsilon$'
    y_title = 'Efficiency'
    fit_function = ''    
    fit_range = [-9999, 9999]
    
    if '_pt' in trigger_under_study:
        x_limits = [20, 100]
        x_title = '$p_{\mathrm{T}}$(jet) [GeV]'
        fit_function = "[0]*exp([1]*exp([2]*x))"
        fit_range = [27, 100]
    elif '_eta' in trigger_under_study:
        x_limits = [-3, 3]
        x_title = '$\eta$(jet)'
        fit_function = '[0]*x*x + [1]*x + [2]'
        #fit_function = '[2]'
        fit_range = [-3, 3]
    elif '_phi' in trigger_under_study:
        x_limits = [-4., 4.]
        x_title = '$\phi$(jet)'
        fit_function = '[0]'
        fit_range = [-3.1, 3.1]
        
    return x_limits, x_title, y_title, fit_function, fit_range
    
def set_plot_styles(data_plot, mc_plot):
    mc_plot.SetMarkerColor(2)
    mc_plot.SetMarkerStyle(22)
    mc_plot.SetMarkerSize(3)

    mc_plot.SetLineWidth(6)
    mc_plot.SetLineColor(2)
    
    data_plot.SetMarkerSize(3)

def set_parameter_limits(trigger_under_study, fit):
    if '_pt' in trigger_under_study:
        fit.SetParLimits(0, 0.0, 1.0)
        fit.SetParLimits(1, -100000.0, -1.0)
        fit.SetParLimits(2, -2.0, -0.01)

    if '_eta' in trigger_under_study:
        fit.SetParLimits(0, -0.2, 0.0)
        fit.SetParLimits(1, -1.0, -1.0)
        fit.SetParLimits(2, 0.2, 1.1)
        
def get_binning(trigger_under_study):
    bin_edges = [0, 30, 35, 40, 45, 50, 70, 100]
    
    if '_pt' in trigger_under_study:
        bin_edges = [0, 30, 35, 40, 45, 50, 70, 100]
    elif '_eta' in trigger_under_study:
        bin_edges = [-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]
        bin_edges = [-3, -2, -1, 0, 1, 2, 3]
        bin_edges = [-3, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 3]
    elif '_phi' in trigger_under_study:
        bin_edges = [-3.5, -3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5]
        
    bin_edge_array = array('d', bin_edges)
    
    return bin_edge_array

def get_fitted_function_str(fit, fit_function):
    decimals = 3
    function_str = fit_function
    function_str = function_str.replace('x*x', 'x^{2}')
    function_str = function_str.replace('[0]', str('%.2g' % fit.GetParameter(0)))
    #function_str = function_str.replace('[1]', str(round(fit.GetParameter(1), decimals)))
    function_str = function_str.replace('[1]', str('%.2g' % fit.GetParameter(1)))
    function_str = function_str.replace('[2]', str('%.2g' % fit.GetParameter(2)))
    function_str = function_str.replace('[3]', str('%.2g' % fit.GetParameter(3)))
    function_str = function_str.replace('[4]', str('%.2g' % fit.GetParameter(4)))
    print function_str
    function_str = function_str.replace('*', ' \\times ')
    function_str = function_str.replace('0 \\times x^{2}', '')
    function_str = function_str.replace('0 \\times x', '')
    function_str = function_str.strip()#remove whitespace 
    function_str = function_str.replace('+ -', '-')
    function_str = function_str.replace('- +', '-')
    function_str = function_str.replace('- -', '+')
    function_str = function_str.replace('+  +', '+')
    function_str = function_str.replace('1 \\times', '1.0 \\times')
    function_str = function_str.replace('e+0', '\\times 10^')
    function_str = function_str.replace('(1\\times', '(')
    function_str = function_str.replace('(-1\\times', '(-')
    if function_str.startswith('+'):
        function_str = function_str[1:]
            
    if 'exp' in function_str:
        function_str = function_str.replace('exp(', 'e^{\left(')
        function_str = function_str.replace(')', '\\right)}')
        
    function_str = '$' + function_str + '$'
    print function_str
    
    return function_str


def get_input_efficiency(file, efficiency_instance):
    efficiency = file.Get(efficiency_instance)
    
    hist_passed = efficiency.GetPassedHistogram()
    hist_total = efficiency.GetTotalHistogram()   

    bin_edge_array = get_binning(efficiency_instance)
    n_bins = len(bin_edge_array) - 1
    
    #hist_passed = asrootpy(hist_passed.Rebin(n_bins, 'truth', bin_edge_array))
    #hist_total = asrootpy(hist_total.Rebin(n_bins, 'truth', bin_edge_array))

    hist_passed = asrootpy(hist_passed)
    hist_total = asrootpy(hist_total)

    return hist_passed, hist_total


if __name__ == '__main__':
    set_root_defaults()
    
    CMS.title['fontsize'] = 40
    CMS.x_axis_title['fontsize'] = 50
    CMS.y_axis_title['fontsize'] = 50
    CMS.axis_label_major['labelsize'] = 40
    CMS.axis_label_minor['labelsize'] = 40
    CMS.legend_properties['size'] = 40
    
    output_formats = ['pdf']
    output_folder = './HLT_plots/'
    
    histFile = 'hists_JEC_3rd_jet_30.root'
    #histFile = 'hists_JEC_4th_jet_30.root'
    #histFile = 'hists_JEC_3rd_jet_45.root'

    #histFile = 'hists_uncorr_3rd_jet_30.root'
    #histFile = 'hists_uncorr_4th_jet_30.root'
    #histFile = 'hists_uncorr_3rd_jet_45.root'

    #histFile = 'hists_JEC_PFnoPU_3rd_jet_30.root'
    #histFile = 'hists_JEC_PFnoPU_4th_jet_30.root'
    #histFile = 'hists_JEC_PFnoPU_3rd_jet_45.root'


    suffix = 'JEC_3rd_30'
        
    input_file = File(histFile)


    efficiencyPlots = ['trigger_eff_pt', 'trigger_eff_eta']

    for efficiency in efficiencyPlots:
        hist_passed, hist_total = get_input_efficiency(input_file, efficiency)
        make_single_efficiency_plot(hist_passed, hist_total, efficiency)

    #ptRatioPlots = ['ptRatio_eta_prof'] #, 'ptRatio_pt_prof'] #, 'ptRatio_eta', 'ptRatio_pt']

    #for ptRatio in ptRatioPlots:
        #make_jet_response_plot(input_file, ptRatio)
        #make_jet_response_comparison_plot(input_files, ptRatio)

    
