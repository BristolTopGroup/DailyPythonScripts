from rootpy.io import File
from rootpy import asrootpy
# Most verbose log level

import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
# from matplotlib.ticker import AutoMinorLocator
# import config.summations as summations
from ROOT import TEfficiency, TGraphAsymmErrors, TF1, TLegend, TLatex
from array import array
from config import CMS
from tools.ROOT_utils import set_root_defaults
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

import numpy
from numpy import frompyfunc
from pylab import plot

from matplotlib import rc
rc('text', usetex=True)
            
def make_efficiency_plot(pass_data, total_data, pass_mc, total_mc, trigger_under_study):
    global output_folder, output_formats
    
    efficiency_data = asrootpy(TGraphAsymmErrors()) 
    efficiency_mc = asrootpy(TGraphAsymmErrors())
    
    efficiency_data.Divide(pass_data, total_data, "cl=0.683 b(1,1) mode")
    efficiency_mc.Divide(pass_mc, total_mc, "cl=0.683 b(1,1) mode")
    
    scale_factor = pass_data.Clone("pass_mc")
    scale_factor.Multiply(total_mc)
    scale_factor.Divide(total_data)
    scale_factor.Divide(pass_mc)
    scale_factor.linewidth = 6
    scale_factor.SetMarkerSize(3)
    scale_factor.linecolor = 'green'
    scale_factor.SetMarkerColor('green')
    
    x_limits, x_title, y_title, fit_function, fit_range = get_parameters(trigger_under_study)
    
    fit_data = TF1("fit_data", fit_function, fit_range[0], fit_range[1])
    fit_mc = TF1("fit_mc", fit_function, fit_range[0], fit_range[1])
    fit_SF = TF1("fit_SF", fit_function, fit_range[0], fit_range[1])
    set_parameter_limits(trigger_under_study, fit_data)
    set_parameter_limits(trigger_under_study, fit_mc)
    set_parameter_limits(trigger_under_study, fit_SF)
    
    efficiency_data.Fit(fit_data, 'FECQ')
    efficiency_mc.Fit(fit_mc, 'FECQ')
    scale_factor.Fit(fit_SF, 'FECQ')
    
    set_plot_styles(efficiency_data, efficiency_mc)
    
    save_as_name = trigger_under_study 
    save_as_name = save_as_name.replace('Jet30/', 'Jet30_')
    plot_efficiencies(efficiency_data, efficiency_mc, scale_factor,
                      fit_data, fit_mc, fit_SF, fit_function,
                      x_limits, x_title, y_title, save_as_name)

def plot_efficiencies(efficiency_data, efficiency_mc, scale_factor,
                      fit_data, fit_mc, fit_SF, fit_function,
                      x_limits, x_title, y_title, save_as_name):    
    # plot with matplotlib
    plt.figure(figsize=(16, 16), dpi=200, facecolor='white')
    gs = gridspec.GridSpec(2, 1, height_ratios=[5, 1]) 

    ax0 = plt.subplot(gs[0])
    ax0.minorticks_on()
    ax0.grid(True, 'major', linewidth=2)
    ax0.grid(True, 'minor')
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    
    ax0.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    
    rplt.errorbar(efficiency_data, xerr=True, emptybins=True, axes=ax0)
    rplt.errorbar(efficiency_mc, xerr=False, emptybins=True, axes=ax0)
    
    ax0.set_xlim(x_limits)
    
    plt.ylabel(y_title, CMS.y_axis_title)
    
    plt.title(r'e+jets, CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV', CMS.title)
    plt.legend(['data', r'$\mathrm{t}\bar{\mathrm{t}}$ MC'], numpoints=1, loc='lower right', prop=CMS.legend_properties)
    
    #add fits
    x = numpy.linspace(fit_data.GetXmin(), fit_data.GetXmax(), fit_data.GetNpx())
    function_data = frompyfunc(fit_data.Eval, 1, 1)
    plot(x, function_data(x), axes=ax0, color = 'black', linewidth = 2)
    
    x = numpy.linspace(fit_mc.GetXmin(), fit_mc.GetXmax(), fit_mc.GetNpx())
    function_mc = frompyfunc(fit_mc.Eval, 1, 1)
    plot(x, function_mc(x), axes=ax0, color = 'red', linewidth = 2)
    
    ax1 = plt.subplot(gs[1])
    #disable labels for plot 1
    plt.setp(ax0.get_xticklabels(minor = True), visible=False)
    plt.setp(ax0.get_xticklabels(), visible=False)
    
    ax1.minorticks_on()
    ax1.grid(True, 'major', linewidth=2)
    ax1.grid(True, 'minor')

    ax1.yaxis.set_major_locator(MultipleLocator(1.))
    ax1.yaxis.set_minor_locator(MultipleLocator(0.5))
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

    ax1.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)

    plt.xlabel(x_title, CMS.x_axis_title)
    plt.ylabel('data/MC', CMS.y_axis_title)
    
    rplt.errorbar(scale_factor, xerr=True, emptybins=False, axes=ax1)
    
    ax1.set_xlim(x_limits)
    #add fit formulas
    ax0.text(0.1, 0.15, '$\epsilon$ = ' + get_fitted_function_str(fit_data, fit_function),
        verticalalignment='bottom', horizontalalignment='left',
        transform=ax0.transAxes,
        color='black', fontsize=60, bbox = dict(facecolor = 'white', edgecolor = 'none', alpha = 0.5))
    ax0.text(0.1, 0.05, '$\epsilon$ = ' + get_fitted_function_str(fit_mc, fit_function),
        verticalalignment='bottom', horizontalalignment='left',
        transform=ax0.transAxes,
        color='red', fontsize=60, bbox = dict(facecolor = 'white', edgecolor = 'none', alpha = 0.5))
    
    ax1.text(0.1, 0.10, '$\epsilon$ = ' + get_fitted_function_str(fit_SF, fit_function),
        verticalalignment='bottom', horizontalalignment='left',
        transform=ax1.transAxes,
        color='green', fontsize=60, bbox = dict(facecolor = 'white', edgecolor = 'none', alpha = 0.5))
    
    #add scale factor fit
    x = numpy.linspace(fit_SF.GetXmin(), fit_SF.GetXmax(), fit_SF.GetNpx())
    function_SF = frompyfunc(fit_SF.Eval, 1, 1)
    plot(x, function_SF(x), axes=ax1, color = 'green', linewidth = 2)
    
    if 'jet_pt' in trigger_under_study:
        ax1.xaxis.set_minor_formatter(FormatStrFormatter('%d'))
        plt.draw()
        labels = [item.get_text() for item in ax1.get_xmajorticklabels()]
        minor_labels = [item.get_text() for item in ax1.get_xminorticklabels()]
        new_labels, new_minor_labels = [], []
        keep_labels = ['20','50','100','150','200']
        for label in labels:
            if not label in keep_labels:
                label = ''
            new_labels.append(label)
        for label in minor_labels:
            if not label in keep_labels:
                label = ''
            new_minor_labels.append(label)
        ax1.set_xticklabels(new_labels)
        ax1.set_xticklabels(new_minor_labels, minor = True)
        
    plt.tight_layout()
    
    for output_format in output_formats:
        plt.savefig(output_folder + save_as_name + '_efficiency_matplot.' + output_format)  
       
def get_parameters(trigger_under_study):
    x_limits = [10, 200]
    x_title = '$p_{\mathrm{T}}$(jet) [GeV]'
    y_title = 'Efficiency'
    fit_function = ''    
    fit_range = [-9999, 9999]
    
    if 'jet_pt' in trigger_under_study:
        x_limits = [10, 200]
        x_title = '$p_{\mathrm{T}}$(jet) [GeV]'
        fit_function = "[0]*exp([1]*exp([2]*x))"
        fit_range = [20, 200]
    elif 'jet_eta' in trigger_under_study:
        x_limits = [-3, 3]
        x_title = '$\eta$(jet)'
        fit_function = '[0]*x*x + [1]*x + [2]'
        fit_range = [-3, 3]
    elif 'jet_phi' in trigger_under_study:
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
    if 'jet_pt' in trigger_under_study:
        fit.SetParLimits(0,0.0,1.0);
        fit.SetParLimits(1,-100,-1);
        fit.SetParLimits(2,-1,-0.01);
                
    if 'jet_eta' in trigger_under_study:
        fit.SetParLimits(0,-0.2,0.0);
        fit.SetParLimits(1,-1,-1);
        fit.SetParLimits(2, 0.2,1.1);
        
def get_binning(trigger_under_study):
    bin_edges = [0, 20, 25, 35, 45, 70, 100, 200]
    
    if 'jet_pt' in trigger_under_study:
        bin_edges = [0, 20, 25, 35, 45, 70, 200]
    elif 'jet_eta' in trigger_under_study:
        bin_edges = [-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]
        bin_edges = [-3, -2, -1, 0, 1, 2, 3]
        bin_edges = [-3, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 3]
    elif 'jet_phi' in trigger_under_study:
        bin_edges = [-3.5, -3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5]
        
    bin_edge_array = array('d', bin_edges)
    
    return bin_edge_array

def get_fitted_function_str(fit, fit_function):
    decimals = 2
    function_str = fit_function
    function_str = function_str.replace('x*x', 'x^{2}')
    function_str = function_str.replace('[0]', str(round(fit.GetParameter(0), decimals)))
    function_str = function_str.replace('[1]', str(round(fit.GetParameter(1), decimals)))
    function_str = function_str.replace('[2]', str(round(fit.GetParameter(2), decimals)))
    function_str = function_str.replace('[3]', str(round(fit.GetParameter(3), decimals)))
    function_str = function_str.replace('[4]', str(round(fit.GetParameter(4), decimals)))
    function_str = function_str.replace('+ -', '-')
    function_str = function_str.replace('- -', '+')
    function_str = function_str.replace('*', ' \\times ')
    function_str = function_str.replace('-0.0', '0.0')
    function_str = function_str.replace('0.0 \\times x^{2}', '')
    function_str = function_str.replace('+ 0.0 \\times x', '')
    function_str = function_str.strip()#remove whitespace
    if function_str.startswith('+'):
        function_str = function_str[1:]
            
    if '+ 0.98' in function_str:
        print function_str
        print len(function_str)
        
    if 'exp' in function_str:
        function_str = function_str.replace('exp(', 'e^{\left(')
        function_str = function_str.replace(')', '\\right)}')
        
    function_str = '$' + function_str + '$'
    return function_str


def get_input_plots(data_file, mc_file, trigger_under_study):
    plot_data_total = data_file.Get(trigger_under_study % 'visited')
    plot_data_passed = data_file.Get(trigger_under_study % 'fired')
    
    mc_trigger = trigger_under_study
    if 'CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT' in trigger_under_study:
        #no isolated trigger available (bug!) in analysed MC, use non-iso instead.
        mc_trigger = trigger_under_study.replace('CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT', 'CaloIdVT_TrkIdT')
        
    plot_ttbar_total = ttbar_file.Get(mc_trigger % 'visited')
    plot_ttbar_passed = ttbar_file.Get(mc_trigger % 'fired')
    
    plot_data_passed.Sumw2()
    plot_data_total.Sumw2()
    plot_ttbar_passed.Sumw2()
    plot_ttbar_total.Sumw2()
    
    bin_edge_array = get_binning(trigger_under_study)
    n_bins = len(bin_edge_array) - 1
    
    plot_data_passed = asrootpy(plot_data_passed.Rebin(n_bins, 'truth', bin_edge_array))
    plot_data_total = asrootpy(plot_data_total.Rebin(n_bins, 'truth', bin_edge_array))
    plot_ttbar_passed = asrootpy(plot_ttbar_passed.Rebin(n_bins, 'truth', bin_edge_array))
    plot_ttbar_total = asrootpy(plot_ttbar_total.Rebin(n_bins, 'truth', bin_edge_array))
    
    return plot_data_passed, plot_data_total, plot_ttbar_passed, plot_ttbar_total

if __name__ == '__main__':
    set_root_defaults()
    
    CMS.title['fontsize'] = 40
    CMS.x_axis_title['fontsize'] = 50
    CMS.y_axis_title['fontsize'] = 50
    CMS.axis_label_major['labelsize'] = 40
    CMS.axis_label_minor['labelsize'] = 40
    CMS.legend_properties['size'] = 40
    
    output_formats = ['png', 'pdf']
    output_folder = '/storage/TopQuarkGroup/results/plots/Trigger/'
    
    triggers = [
                'HLT_Ele25_CaloIdVT_TrkIdT_TriCentralJet30',
                'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralJet30',
                'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralPFJet30',
                    ]
        
    trigger_variables = ['jet_pt',
                        'jet_eta_PtGT30',
                        'jet_phi_PtGT30',
                        'jet_eta_PtGT45',
                        'jet_phi_PtGT45'
                        ]
    
    trigger_modifiers = [
                         '_%s_3jets',
                         '_%s_4orMoreJets']
    
    
    hltFiles = {}
    
    hltFiles['data'] = '/storage/TopQuarkGroup/results/histogramfiles/HLT_V1/ElectronHad_4692.36pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'
    hltFiles['ttbar'] = '/storage/TopQuarkGroup/results/histogramfiles/HLT_V1/TTJetsFall11_4692.36pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'
    
    triggerPlots = ['HLTStudy/' + trigger + '/' + variable + modifier 
                    for trigger in triggers 
                    for variable in trigger_variables 
                    for modifier in trigger_modifiers]
    data_file = File(hltFiles['data'])
    ttbar_file = File(hltFiles['ttbar'])

    for trigger_under_study in triggerPlots:

        plot_data_passed, plot_data_total, plot_ttbar_passed, plot_ttbar_total = get_input_plots(data_file, 
                                                                                                 ttbar_file, 
                                                                                                 trigger_under_study)
        
        make_efficiency_plot(plot_data_passed, plot_data_total, plot_ttbar_passed, plot_ttbar_total,
                             trigger_under_study % '')
    
