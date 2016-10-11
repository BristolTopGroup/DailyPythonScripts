'''
Created on 6 Jun 2014

@author: senkin

Read the BLT ntuple and extract the trigger objects. Match them with reco objects, perform
tag and probe studies to estimate single lepton trigger efficiency.

'''
from dps.config import CMS
from rootpy.io import File
from rootpy import asrootpy, ROOTError
from optparse import OptionParser
from copy import deepcopy
import sys, math
import pickle

import matplotlib
matplotlib.use('AGG')

import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FormatStrFormatter, MultipleLocator
from rootpy.plotting import Hist, Hist2D, Canvas, Efficiency
from dps.utils.ROOT_utils import set_root_defaults
from dps.utils.file_utilities import make_folder_if_not_exists
from dps.utils.plotting import make_plot, Histogram_properties
from ROOT import TLorentzVector, TGraphAsymmErrors, TF1, gPad, gStyle
from ROOT import RooFit, RooDataHist, RooArgList, RooAddPdf, RooRealVar, RooBreitWigner, RooExponential, RooFFTConvPdf, RooCBShape

import numpy
from numpy import frompyfunc
from pylab import plot

from matplotlib import rc
rc( 'font', **CMS.font )
rc( 'text', usetex = True )

class Particle :    
    def __init__(self, px, py, pz, energy) : 
        self.lorentz = TLorentzVector(px, py, pz, energy)
        self.isolation = 99999
        self.ID = 0
        self.dxy = 99999
        self.dz = 99999
        self.passConversionVeto = 0
        self.innerHits = 99999
        self.chi2 = 99999
        self.nValidMuonHits = 0
        self.trackerLayers = 0
        self.validPixelLayers = 0
        self.matchedStations = 0
        self.isGlobalMuon = 0

    def set_isolation(self, isolation):
        self.isolation = isolation

    def set_id(self, ID):
        self.ID = ID

    def set_dxy(self, dxy):
        self.dxy = dxy

    def set_dz(self, dz):
        self.dz = dz

    def set_pass_conversion_veto(self, passConversionVeto):
        self.passConversionVeto = passConversionVeto

    def set_inner_hits(self, innerHits):
        self.innerHits = innerHits

    def set_chi2(self, chi2):
        self.chi2 = chi2

    def set_n_valid_muon_hits(self, nValidMuonHits):
        self.nValidMuonHits = nValidMuonHits

    def set_tracker_layers(self, trackerLayers):
        self.trackerLayers = trackerLayers

    def set_valid_pixel_layers(self, validPixelLayers):
        self.validPixelLayers = validPixelLayers
    
    def set_matched_stations(self, matchedStations):
        self.matchedStations = matchedStations

    def set_is_global_muon(self, isGlobalMuon):
        self.isGlobalMuon = isGlobalMuon

    def Pt(self):
        return self.lorentz.Pt()

    def Eta(self):
        return self.lorentz.Eta()

#for reference (see https://github.com/BristolTopGroup/NTupleProduction/blob/master/python/BristolNTuple_TriggerObjects_cfi.py)
trigger_objects = ['TriggerObjectElectronLeg', 'TriggerObjectElectronIsoLeg', 'TriggerObjectHadronLeg',
                   'TriggerObjectHadronIsoLeg', 'TriggerObjectHadronPFIsoLeg', 'TriggerObjectMuon1',
                   'TriggerObjectMuon2', 'TriggerObjectMuon2p1', 'TriggerObjectQuadJets']

Z_mass = 91.18

pt_bins = [20, 30, 40, 50, 100]
# eta_bins = [-2.5, -0.8, 0.8, 2.5]
eta_bins = [-2.5, -1.478, -0.8, 0, 0.8, 1.478, 2.5]
abs_eta_bins = [0, 0.8, 1.478, 2.5]

# Finer bins for debugging
# abs_eta_bins = [0,0.4,0.8,1.2,1.478,2.0,2.5]
# eta_bins = [-2.5,-2.0,-1.566,-1.4442,-1.2,-0.8,-0.4,0,0.4,0.8,1.2,1.4442,1.566,2.0,2.5]
# pt_bins = [ 20,30,40,50,75,100]

number_of_pt_bin_edges = len( pt_bins )
number_of_eta_bin_edges = len( eta_bins )

# Initialise histograms

pt_eta_bins_Z_peaks_total_data = {}

for i in range( number_of_pt_bin_edges - 1 ):
    lower_edge_pt = pt_bins[i]
    pt_eta_bins_Z_peaks_total_data.update({lower_edge_pt : []})
    for j in range( number_of_eta_bin_edges - 1 ):
        lower_edge_eta = eta_bins[j]
        pt_eta_bins_Z_peaks_total_data[lower_edge_pt].append(Hist(150, 0, 150, name='Z_peak_' + str(lower_edge_pt) + '_' + str(lower_edge_eta)))

pt_eta_bins_Z_peaks_passed_data = deepcopy(pt_eta_bins_Z_peaks_total_data)
pt_eta_bins_Z_peaks_passed_mc = deepcopy(pt_eta_bins_Z_peaks_total_data)
pt_eta_bins_Z_peaks_total_mc = deepcopy(pt_eta_bins_Z_peaks_total_data)

histograms_data = {
                'btag_multiplicity' : Hist(5, 0, 5, name='N btags'),

                'reco_lepton_multiplicity' : Hist(5, 0, 5, name='reco_N_leptons'),
                'reco_lepton_pt' : Hist(30, 0, 150, name='reco_lepton_pt'),
                'reco_lepton_eta' : Hist(30, -3, 3, name='reco_lepton_eta'),

                'mc_lepton_multiplicity' : Hist(15, 0, 15, name='mc_N_leptons'),
                'mc_lepton_pt' : Hist(30, 0, 150, name='mc_lepton_pt'),
                'mc_lepton_eta' : Hist(30, -3, 3, name='mc_lepton_eta'),
                'mc_matched_lepton_isolation' : Hist(30, 0, 2, name='mc_lepton_iso'),
                'mc_matched_lepton_ID' : Hist(10, 0, 2, name='mc_lepton_ID'),

                'hlt_lepton_multiplicity' : Hist(5, 0, 5, name='hlt_N_leptons'),
                'hlt_lepton_pt' : Hist(30, 0, 150, name='hlt_lepton_pt'),
                'hlt_lepton_eta' : Hist(30, -3, 3, name='hlt_lepton_eta'),

                'tag_reco_lepton_pt' : Hist(30, 0, 150, name='tag_reco_lepton_pt'),
                'tag_reco_lepton_eta' : Hist(30, -3, 3, name='tag_reco_lepton_eta'),
                'tag_hlt_lepton_pt' : Hist(30, 0, 150, name='tag_hlt_lepton_pt'),
                'tag_hlt_lepton_eta' : Hist(30, -3, 3, name='tag_hlt_lepton_eta'),

                'probe_total_pt' : Hist(pt_bins, name='probe_total_lepton_pt'),
                'probe_total_eta' : Hist(eta_bins, name='probe_total_lepton_eta'),
                'probe_total_pt_eta' : Hist2D(pt_bins, eta_bins, name='probe_total_pt_eta'),
                'tagProbe_total_Z_peak' : Hist(150, 0, 150, name='tagProbe_total_Z_peak'),

                'probe_passed_pt' : Hist(pt_bins, name='probe_passed_lepton_pt'),
                'probe_passed_eta' : Hist(eta_bins, name='probe_passed_lepton_eta'),
                'probe_passed_pt_eta' : Hist2D(pt_bins, eta_bins, name='probe_passed_pt_eta'),
                'probe_passed_hlt_pt' : Hist(pt_bins, name='probe_passed_hlt_lepton_pt'),
                'probe_passed_hlt_eta' : Hist(eta_bins, name='probe_passed_hlt_lepton_eta'),
                'tagProbe_passed_Z_peak' : Hist(150, 0, 150, name='tagProbe_passed_Z_peak'),
                'tagProbe_passed_hlt_Z_peak' : Hist(150, 0, 150, name='tagProbe_passed_hlt_Z_peak'),
}

histograms_mc = deepcopy(histograms_data)

def get_parameters(trigger_under_study):
    x_limits = [10, 100]
    x_title = '$p_{\mathrm{T}}$(jet) [GeV]'
    #y_title = '$\epsilon$'
    y_title = 'Efficiency'
    fit_function = ''    
    fit_range = [-9999, 9999]
    
    if 'jet_pt' in trigger_under_study:
        x_limits = [20, 100]
        x_title = '$p_{\mathrm{T}}$(jet) [GeV]'
        fit_function = "[0]*exp([1]*exp([2]*x))"
        fit_range = [20, 100]
    elif 'jet_eta' in trigger_under_study:
        x_limits = [-3, 3]
        x_title = '$\eta$(jet)'
        # fit_function = '[0]*x*x + [1]*x + [2]'
        fit_function = '[2]'
        fit_range = [-3, 3]
    elif '_pt' in trigger_under_study:
        x_limits = [20, 100]
        x_title = '$p_{\mathrm{T}}$(l) [GeV]'
        fit_function = "[0]*exp([1]*exp([2]*x))"
        fit_range = [20, 100]
    elif '_eta' in trigger_under_study:
        x_limits = [-3, 3]
        x_title = '$\eta$(l)'
        fit_function = '[0]*x*x + [1]*x + [2]'
        #fit_function = '[2]'
        fit_range = [-3, 3]
    elif '_phi' in trigger_under_study:
        x_limits = [-4., 4.]
        x_title = '$\phi$(l)'
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
    # print function_str
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
    # print function_str
    
    return function_str

def make_efficiency_plot(pass_data, total_data, pass_mc, total_mc, trigger_under_study, channel = 'electron'):
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
    plot_efficiencies(efficiency_data, efficiency_mc, scale_factor,
                        fit_data, fit_mc, fit_SF, fit_function,
                        x_limits, x_title, y_title, save_as_name, channel)

def plot_efficiencies(efficiency_data, efficiency_mc, scale_factor,
                      fit_data, fit_mc, fit_SF, fit_function,
                      x_limits, x_title, y_title, save_as_name, channel):
    global centre_of_mass, output_formats, output_folder
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
    rplt.errorbar(efficiency_mc, xerr=None, emptybins=True, axes=ax0)
    
    ax0.set_xlim(x_limits)
    
    plt.ylabel(y_title, CMS.y_axis_title)
    if channel == 'electron':
        plt.title(r'e+jets, CMS Preliminary at $\sqrt{s}$ = %d TeV' % centre_of_mass, CMS.title)
    else:
        plt.title(r'$\mu$+jets, CMS Preliminary at $\sqrt{s}$ = %d TeV' % centre_of_mass, CMS.title)
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
    
    if 'jet_pt' in save_as_name:
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
        plt.savefig(output_folder + save_as_name + '.' + output_format)

def make_2D_efficiency_plot(hist_passed, hist_total, efficiency, channel = 'electron'):
    global output_folder, output_formats

    # for bin in range( 0, hist_passed.GetSize() ):
    #     if not (hist_passed.IsBinUnderflow( bin ) or hist_passed.IsBinOverflow( bin ) ):
    #         print hist_total.GetBinContent( bin ), hist_passed.GetBinContent( bin )


    plot_efficiency = Efficiency(hist_passed, hist_total)
    canvas = Canvas(width=700, height=500)

    gStyle.SetPaintTextFormat('.3g')
    plot_efficiency.Draw('COLZ TEXT')
    gPad.Update()
    paintedHistogram = plot_efficiency.painted_histogram
    plot_efficiency.painted_histogram.GetXaxis().SetTitle('p_{T}')
    plot_efficiency.painted_histogram.GetYaxis().SetTitle('#eta')
    save_as_name = efficiency
    
    for output_format in output_formats:
        canvas.Print(output_folder + save_as_name + '.' + output_format)

    # Make +/- variation plots
    plot_efficiency_plus = paintedHistogram.Clone('plus')
    plot_efficiency_minus = paintedHistogram.Clone('minus')

    for bin in range( 0, plot_efficiency_plus.GetSize() ):
        if not (plot_efficiency_plus.IsBinUnderflow( bin ) or plot_efficiency_plus.IsBinOverflow( bin ) ):
            newBinContentPlus = plot_efficiency.GetEfficiency( bin ) + plot_efficiency.GetEfficiencyErrorUp( bin )
            newBinContentMinus = plot_efficiency.GetEfficiency( bin ) - plot_efficiency.GetEfficiencyErrorLow( bin )
            plot_efficiency_plus.SetBinContent( bin, newBinContentPlus )
            plot_efficiency_minus.SetBinContent( bin, newBinContentMinus )

    plot_efficiency_plus.Draw('COLZ TEXT')
    gPad.Update()
    for output_format in output_formats:
        canvas.Print(output_folder + save_as_name + '_plus.' + output_format)

    plot_efficiency_minus.Draw('COLZ TEXT')
    gPad.Update()
    for output_format in output_formats:
        canvas.Print(output_folder + save_as_name + '_minus.' + output_format)

def produce_pickle_files(hist_passed_data, hist_total_data, hist_passed_mc, hist_total_mc, channel = 'electron'):
    global suffix, centre_of_mass, output_pickle_folder
    output_pickle = open( output_pickle_folder + '/' + channel + '_' + suffix + '_' + str(centre_of_mass) + 'TeV.pkl', 'wb' )
    dictionary = {}
    
    data_efficiency = Efficiency(hist_passed_data, hist_total_data)
    mc_efficiency = Efficiency(hist_passed_mc, hist_total_mc)

    for i in range( number_of_eta_bin_edges - 1 ):
        lower_edge_eta = eta_bins[i]
        upper_edge_eta = eta_bins[i+1]
        eta_bin_range = 'eta_' + str(lower_edge_eta) + '_' + str(upper_edge_eta)
        dictionary[eta_bin_range] = {}
        for j in range( number_of_pt_bin_edges - 1 ):
            lower_edge_pt = pt_bins[j]
            upper_edge_pt = pt_bins[j+1]
            global_bin = data_efficiency.GetGlobalBin(j+1, i+1)
            global_bin_mc = mc_efficiency.GetGlobalBin(j+1, i+1)
            assert global_bin == global_bin_mc

            data_efficiency_in_bin = data_efficiency.GetEfficiency( global_bin )
            data_efficiency_in_bin_error_up = data_efficiency.GetEfficiencyErrorUp( global_bin )
            data_efficiency_in_bin_error_down = data_efficiency.GetEfficiencyErrorLow( global_bin )

            mc_efficiency_in_bin = mc_efficiency.GetEfficiency( global_bin )
            mc_efficiency_in_bin_error_up = mc_efficiency.GetEfficiencyErrorUp( global_bin )
            mc_efficiency_in_bin_error_down = mc_efficiency.GetEfficiencyErrorLow( global_bin )

            if mc_efficiency_in_bin != 0:
                efficiency_ratio = data_efficiency_in_bin/mc_efficiency_in_bin
            else:
                efficiency_ratio = 0
            efficiency_ratio_error_up = math.sqrt(data_efficiency_in_bin_error_up**2 + mc_efficiency_in_bin_error_up**2)
            efficiency_ratio_error_down = math.sqrt(data_efficiency_in_bin_error_down**2 + mc_efficiency_in_bin_error_down**2)

            dictionary[eta_bin_range]['pt_' + str(lower_edge_pt) + '_' + str(upper_edge_pt)] = {}
            dictionary[eta_bin_range]['pt_' + str(lower_edge_pt) + '_' + str(upper_edge_pt)]['data'] = \
                                                    { 'efficiency' : data_efficiency_in_bin,
                                                      'err_up' : data_efficiency_in_bin_error_up,
                                                      'err_down' : data_efficiency_in_bin_error_down,
                                                    }
            dictionary[eta_bin_range]['pt_' + str(lower_edge_pt) + '_' + str(upper_edge_pt)]['mc'] = \
                                                    { 'efficiency' : mc_efficiency_in_bin,
                                                      'err_up' : mc_efficiency_in_bin_error_up,
                                                      'err_down' : mc_efficiency_in_bin_error_down,
                                                    }
            dictionary[eta_bin_range]['pt_' + str(lower_edge_pt) + '_' + str(upper_edge_pt)]['data/mc'] = \
                                                    { 'efficiency_ratio' : efficiency_ratio,
                                                      'err_up' : efficiency_ratio_error_up,
                                                      'err_down' : efficiency_ratio_error_down,
                                                    }

    pickle.dump( dictionary, output_pickle )

def fit_Z_peak(histogram, save_as_name, channel, run_on = 'data'):
    global output_folder, output_formats, suffix, use_CB_convolution
    if channel == 'electron':
        title_channel = 'e+jets'
    else:
        title_channel = '$\mu$+jets'
    
    if run_on == 'data':
        save_folder = output_folder + '/data/' + suffix + '/'
    else:
        save_folder = output_folder + '/mc/' + suffix + '/'

    make_folder_if_not_exists(save_folder)
    make_folder_if_not_exists(save_folder + '/binned')

    # Invariant mass range and data histogram
    m_range = RooRealVar("m_range", "Z peak", 60.0, 120.0)
    data_hist = RooDataHist( 'data_hist', 'data_hist', RooArgList( m_range ), histogram )

    # Fit Parameters for Breit-Wigner and exponential
    mean = RooRealVar("mean", "Mass", 85.0, 60.0, 120.0)
    bw_sigma = RooRealVar("bw_sigma", "Width", 5.0, 1., 6.0)
    exp_lambda = RooRealVar("lambda", "slope", -0.1, -5., 0.)

    # Optional Crystal Ball
    if use_CB_convolution:
        cb_sigma = RooRealVar("CB_sigma", "CB_sigma", 5.0, 1., 6.0)
        cb_alpha = RooRealVar("CB_alpha", "CB_alpha", 1., 0., 30.)
        cb_N = RooRealVar("CB_n", "CB_n", 5.)

    # Build signal and background PDFs
    breit_wigner = RooBreitWigner("signal", "signal PDF", m_range, mean, bw_sigma)
    background = RooExponential("background", "background PDF", m_range, exp_lambda)

    # Optional convolution of BW and CB
    if use_CB_convolution:
        crystal_ball = RooCBShape("cryBall", "Crystal Ball resolution model", m_range, mean, cb_sigma, cb_alpha, cb_N)
        bw_cb_convolution = RooFFTConvPdf("bwxCryBall", "Convoluted Crystal Ball and BW", m_range, breit_wigner, crystal_ball)

    # Construct the signal and background model
    n_sig = RooRealVar("n_sig", "# signal events", 200, 0., 10000)
    n_bkg = RooRealVar("n_bkg", "# background events", 200, 0., 10000)
    model = RooAddPdf("model", "s+b", RooArgList(breit_wigner, background), RooArgList(n_sig, n_bkg))
    
    # Alternatively, use BW*CB convolution
    if use_CB_convolution:
        model = RooAddPdf("model", "s+b", RooArgList(bw_cb_convolution, background), RooArgList(n_sig, n_bkg))

    # Fit model to data
    model.fitTo( data_hist, RooFit.PrintLevel(-1), RooFit.Verbose(False), RooFit.PrintEvalErrors(-1), RooFit.Warnings(False) )

    # Plot data and composite PDF overlaid
    m_range_frame = m_range.frame()
    data_hist.plotOn(m_range_frame)
    model.plotOn(m_range_frame)
    model.paramOn(m_range_frame, RooFit.Layout( 0.56, 0.95, 0.9 ), RooFit.Format( 'NE', RooFit.AutoPrecision( 2 ) ) )
    canvas = Canvas(width=700, height=500)
    m_range_frame.Draw()

    for output_format in output_formats:
        canvas.Print(save_folder + save_as_name + '.' + output_format)

    return int(n_sig.getValV()), int(n_sig.getError())

def fill_Z_peak_histograms(tag_lepton, probe_lepton, mode = 'data_passed'):
    if 'data' in mode:
        if 'passed' in mode:
            histograms_data['tagProbe_passed_Z_peak'].Fill((probe_lepton.lorentz+tag_lepton.lorentz).M())
            pt_eta_bins_Z_peaks = pt_eta_bins_Z_peaks_passed_data
        else:
            histograms_data['tagProbe_total_Z_peak'].Fill((probe_lepton.lorentz+tag_lepton.lorentz).M())
            pt_eta_bins_Z_peaks = pt_eta_bins_Z_peaks_total_data
    else:
        if 'passed' in mode:
            histograms_mc['tagProbe_passed_Z_peak'].Fill((probe_lepton.lorentz+tag_lepton.lorentz).M())
            pt_eta_bins_Z_peaks = pt_eta_bins_Z_peaks_passed_mc
        else:
            histograms_mc['tagProbe_total_Z_peak'].Fill((probe_lepton.lorentz+tag_lepton.lorentz).M())
            pt_eta_bins_Z_peaks = pt_eta_bins_Z_peaks_total_mc

    for i in range( number_of_pt_bin_edges - 1 ):
        lower_edge_pt = pt_bins[i]
        upper_edge_pt = pt_bins[i+1]
        if probe_lepton.Pt() > lower_edge_pt and probe_lepton.Pt() < upper_edge_pt:
            for j in range( number_of_eta_bin_edges - 1 ):
                lower_edge_eta = eta_bins[j]
                upper_edge_eta = eta_bins[j+1]
                if probe_lepton.Eta() > lower_edge_eta and probe_lepton.Eta() < upper_edge_eta:
                    pt_eta_bins_Z_peaks[lower_edge_pt][j].Fill((probe_lepton.lorentz+tag_lepton.lorentz).M())
                    continue
            continue

def make_Z_peak_plots(run_on = 'data', channel = 'electron'):
    global suffix

    if run_on == 'data':
        histograms = histograms_data
        pt_eta_bins_Z_peaks_total = pt_eta_bins_Z_peaks_total_data
        pt_eta_bins_Z_peaks_passed = pt_eta_bins_Z_peaks_passed_data
    else:
        histograms = histograms_mc
        pt_eta_bins_Z_peaks_total = pt_eta_bins_Z_peaks_total_mc
        pt_eta_bins_Z_peaks_passed = pt_eta_bins_Z_peaks_passed_mc

    # Make inclusive plots
    fit_Z_peak(histograms['tagProbe_total_Z_peak'], 'tagProbe_total_Z_peak', channel, run_on)
    fit_Z_peak(histograms['tagProbe_passed_Z_peak'], 'tagProbe_passed_Z_peak', channel, run_on)
    
    if suffix == 'trigger':
        fit_Z_peak(histograms['tagProbe_passed_hlt_Z_peak'], 'tagProbe_passed_hlt_Z_peak', channel, run_on)

    # Make pt/eta binned plots
    for i in range( number_of_pt_bin_edges - 1 ):
        lower_edge_pt = pt_bins[i]
        upper_edge_pt = pt_bins[i+1]
        for j in range( number_of_eta_bin_edges - 1 ):
            lower_edge_eta = eta_bins[j]
            upper_edge_eta = eta_bins[j+1]
            n_sig_total, n_sig_total_error = fit_Z_peak(pt_eta_bins_Z_peaks_total[lower_edge_pt][j], \
                'binned/tagProbe_total_Z_peak_' + str(i) + '_' + str(j), channel, run_on = run_on)
            n_sig_passed, n_sig_passed_error = fit_Z_peak(pt_eta_bins_Z_peaks_passed[lower_edge_pt][j], \
                'binned/tagProbe_passed_Z_peak_' + str(i) + '_' + str(j), channel, run_on = run_on)

            # fix for bad fits
            if n_sig_passed > n_sig_total:
                n_sig_passed = n_sig_total

            histograms['probe_passed_pt_eta'].SetBinContent(i+1, j+1, n_sig_passed)
            histograms['probe_passed_pt_eta'].SetBinError(i+1, j+1, n_sig_passed_error)
            histograms['probe_total_pt_eta'].SetBinContent(i+1, j+1, n_sig_total)
            histograms['probe_total_pt_eta'].SetBinError(i+1, j+1, n_sig_total_error)

    # Make 1D projections
    histograms['probe_passed_pt'] = asrootpy(histograms['probe_passed_pt_eta'].ProjectionX())
    histograms['probe_passed_eta'] = asrootpy(histograms['probe_passed_pt_eta'].ProjectionY())

    histograms['probe_total_pt'] = asrootpy(histograms['probe_total_pt_eta'].ProjectionX())
    histograms['probe_total_eta'] = asrootpy(histograms['probe_total_pt_eta'].ProjectionY())

def make_other_plots(run_on = 'data', channel = 'electron'):
    global centre_of_mass, output_folder, output_formats, suffix
    if channel == 'electron':
        title_channel = 'e+jets'
    else:
        title_channel = '$\mu$+jets'

    if run_on == 'data':
        histograms = histograms_data
        save_folder = output_folder + '/data/'  + suffix + '/'
    else:
        histograms = histograms_mc
        save_folder = output_folder + '/mc/' + suffix + '/'

    make_folder_if_not_exists(save_folder)

    if run_on == 'mc':
        histogram_properties = Histogram_properties()
        histogram_properties.name = 'mc_leptons_multiplicity'
        histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
        histogram_properties.x_axis_title = 'N MC leptons'
        histogram_properties.y_axis_title = 'Events'
        make_plot(histograms['mc_lepton_multiplicity'], 'mc', histogram_properties, save_folder = save_folder, save_as = output_formats)

        histogram_properties = Histogram_properties()
        histogram_properties.name = 'mc_lepton_pt'
        histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
        histogram_properties.x_axis_title = 'MC lepton pt'
        histogram_properties.y_axis_title = 'Events'
        make_plot(histograms['mc_lepton_pt'], 'mc', histogram_properties, save_folder = save_folder, save_as = output_formats)

        histogram_properties = Histogram_properties()
        histogram_properties.name = 'mc_lepton_eta'
        histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
        histogram_properties.x_axis_title = 'MC lepton eta'
        histogram_properties.y_axis_title = 'Events'
        make_plot(histograms['mc_lepton_eta'], 'mc', histogram_properties, save_folder = save_folder, save_as = output_formats)

        histogram_properties = Histogram_properties()
        histogram_properties.name = 'mc_lepton_isolation'
        histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
        histogram_properties.x_axis_title = 'MC matched lepton isolation'
        histogram_properties.y_axis_title = 'Events'
        make_plot(histograms['mc_matched_lepton_isolation'], 'mc', histogram_properties, save_folder = save_folder, save_as = output_formats)

        histogram_properties = Histogram_properties()
        histogram_properties.name = 'mc_lepton_ID'
        histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
        histogram_properties.x_axis_title = 'MC matched lepton ID'
        histogram_properties.y_axis_title = 'Events'
        make_plot(histograms['mc_matched_lepton_ID'], 'mc', histogram_properties, save_folder = save_folder, save_as = output_formats)
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'btag_multiplicity'
    histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
    histogram_properties.x_axis_title = 'N btags'
    histogram_properties.y_axis_title = 'Events'
    make_plot(histograms['btag_multiplicity'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'reco_leptons_multiplicity'
    histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
    histogram_properties.x_axis_title = 'N reco leptons'
    histogram_properties.y_axis_title = 'Events'
    make_plot(histograms['reco_lepton_multiplicity'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'reco_lepton_pt'
    histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
    histogram_properties.x_axis_title = 'Reco lepton pt'
    histogram_properties.y_axis_title = 'Events'
    make_plot(histograms['reco_lepton_pt'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'reco_lepton_eta'
    histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
    histogram_properties.x_axis_title = 'Reco lepton eta'
    histogram_properties.y_axis_title = 'Events'
    make_plot(histograms['reco_lepton_eta'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'hlt_leptons_multiplicity'
    histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
    histogram_properties.x_axis_title = 'N HLT leptons'
    histogram_properties.y_axis_title = 'Events'
    make_plot(histograms['hlt_lepton_multiplicity'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'hlt_lepton_pt'
    histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
    histogram_properties.x_axis_title = 'HLT lepton pt'
    histogram_properties.y_axis_title = 'Events'
    make_plot(histograms['hlt_lepton_pt'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'hlt_lepton_eta'
    histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
    histogram_properties.x_axis_title = 'HLT lepton eta'
    histogram_properties.y_axis_title = 'Events'
    make_plot(histograms['hlt_lepton_eta'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'tag_reco_lepton_pt'
    histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
    histogram_properties.x_axis_title = 'Tag reco lepton pt'
    histogram_properties.y_axis_title = 'Events'
    make_plot(histograms['tag_reco_lepton_pt'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'tag_reco_lepton_eta'
    histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
    histogram_properties.x_axis_title = 'Tag reco lepton eta'
    histogram_properties.y_axis_title = 'Events'
    make_plot(histograms['tag_reco_lepton_eta'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'probe_total_pt'
    histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
    histogram_properties.x_axis_title = 'All probes reco lepton pt'
    histogram_properties.y_axis_title = 'Events'
    make_plot(histograms['probe_total_pt'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'probe_total_eta'
    histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
    histogram_properties.x_axis_title = 'All probes reco lepton eta'
    histogram_properties.y_axis_title = 'Events'
    make_plot(histograms['probe_total_eta'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'probe_passed_pt'
    histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
    histogram_properties.x_axis_title = 'Passing probes reco lepton pt'
    histogram_properties.y_axis_title = 'Events'
    make_plot(histograms['probe_passed_pt'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)

    histogram_properties = Histogram_properties()
    histogram_properties.name = 'probe_passed_eta'
    histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
    histogram_properties.x_axis_title = 'Passing probes reco lepton eta'
    histogram_properties.y_axis_title = 'Events'
    make_plot(histograms['probe_passed_eta'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)

    if suffix == 'trigger':
        histogram_properties = Histogram_properties()
        histogram_properties.name = 'tag_hlt_lepton_pt'
        histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
        histogram_properties.x_axis_title = 'Tag HLT lepton pt'
        histogram_properties.y_axis_title = 'Events'
        make_plot(histograms['tag_hlt_lepton_pt'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)

        histogram_properties = Histogram_properties()
        histogram_properties.name = 'tag_hlt_lepton_eta'
        histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
        histogram_properties.x_axis_title = 'Tag HLT lepton eta'
        histogram_properties.y_axis_title = 'Events'
        make_plot(histograms['tag_hlt_lepton_eta'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)

        histogram_properties = Histogram_properties()
        histogram_properties.name = 'probe_passed_hlt_pt'
        histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
        histogram_properties.x_axis_title = 'Passing probes HLT lepton pt'
        histogram_properties.y_axis_title = 'Events'
        make_plot(histograms['probe_passed_hlt_pt'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)

        histogram_properties = Histogram_properties()
        histogram_properties.name = 'probe_passed_hlt_eta'
        histogram_properties.title = '%s, CMS Preliminary, $\sqrt{s}$ = %d TeV' % (title_channel, centre_of_mass)
        histogram_properties.x_axis_title = 'Passing probes HLT lepton eta'
        histogram_properties.y_axis_title = 'Events'
        make_plot(histograms['probe_passed_hlt_eta'], 'data', histogram_properties, save_folder = save_folder, save_as = output_formats)


def get_N_bjets(event, channel = 'electron'):
    # Get csv discriminating variable
    # Vector of double
    getVar = event.__getattr__
    if channel == 'electron':
        jetCsvDiscrim = getVar('cleanedJetsPFlowEPlusJets.CombinedSecondaryVertexBJetTag')
    else:
        jetCsvDiscrim = getVar('cleanedJetsPFlowMuPlusJets.CombinedSecondaryVertexBJetTag')
    
    nBJets = 0
    nJets = 0
    for csv in jetCsvDiscrim:
        nJets += 1
        if csv > 0.679 :
            nBJets += 1
            pass
        pass
    
    if nBJets > nJets : 'PANIC'
    
    return nBJets

def match_four_momenta(four_momentum, four_momenta):
    best_index = len(four_momenta)
    matched_delta_R = 9999
    for index in range(len(four_momenta)):
        delta_R = four_momentum.lorentz.DeltaR(four_momenta[index].lorentz)
        if (delta_R < matched_delta_R):
            matched_delta_R = delta_R
            best_index = index
    return best_index, matched_delta_R

def best_Z_peak_probe_index(tag_lepton, probe_leptons):
    #pick the smallest difference of the inv.mass with the Z mass and return the probe index
    best_index = len(probe_leptons)
    best_delta_Z = 99999
    for index in range(len(probe_leptons)):
        probe_lepton = probe_leptons[index]
        if tag_lepton == probe_lepton:
            continue
        inv_mass = (tag_lepton.lorentz+probe_lepton.lorentz).M()
        delta_Z = abs(inv_mass - Z_mass)
        if delta_Z < best_delta_Z:
            best_delta_Z = delta_Z
            best_index = index
    return best_index

def is_Z_event(first_lepton, second_lepton):
    inv_mass = (first_lepton.lorentz+second_lepton.lorentz).M()
    if inv_mass > 60 and inv_mass < 120:
        return True
    else:
        return False

# Tag ID
def get_tag_lepton( reco_leptons, hlt_leptons ):
    for lepton in reco_leptons:
        passes_tag = passes_tag_selection( lepton, hlt_leptons, channel )
        if passes_tag:
            matched_index_signal_lepton, matched_delta_R_signal_lepton = match_four_momenta(lepton, hlt_leptons)
            hlt_lepton = hlt_leptons[matched_index_signal_lepton]
            return lepton, hlt_lepton
    return 0, 0

def passes_tag_selection(lepton, hlt_leptons, match_to_trigger_object = True, channel = 'electron'):
    # see if tag matches the trigger object
    matched_index_signal_lepton, matched_delta_R_signal_lepton = match_four_momenta(lepton, hlt_leptons)
    if channel == 'electron':
        if lepton.Pt() > 30 and abs(lepton.Eta()) < 0.8 and \
           lepton.isolation < 0.1 and lepton.ID > 0.9 and lepton.dxy < 0.02 and lepton.innerHits <= 0 and lepton.passConversionVeto:
            if not match_to_trigger_object:
                return True
            elif matched_delta_R_signal_lepton < 0.3:
                return True
            else:
                return False
        else:
            return False
    else:
        if lepton.Pt() > 26 and abs(lepton.Eta()) < 2.1 and \
           lepton.isolation < 0.12 and lepton.ID != 0 and lepton.dxy < 0.2 and lepton.dz < 0.5 and \
           lepton.nValidMuonHits > 0 and lepton.isGlobalMuon != 0 and \
           lepton.chi2 < 10 and lepton.trackerLayers > 5 and lepton.validPixelLayers > 0 and lepton.matchedStations > 1:
            if not match_to_trigger_object:
                return True
            elif matched_delta_R_signal_lepton < 0.3:
                return True
            else:
                return False
        else:
            return False

# Baseline probe selection
def passes_baseline_probe_selection_trigger(lepton, channel = 'electron'):
    if channel == 'electron':
        if lepton.Pt() > 30 and abs(lepton.Eta()) < 2.5 and not \
           is_in_crack(lepton) and lepton.isolation < 0.1 and lepton.ID > 0.5 and \
           lepton.dxy < 0.02 and lepton.innerHits <= 0 and lepton.passConversionVeto:
            return True
        else:
            return False
    else:
        if lepton.Pt() > 26 and abs(lepton.Eta()) < 2.1 and \
           lepton.isolation < 0.12 and lepton.ID != 0 and lepton.dxy < 0.2 and lepton.dz < 0.5 and \
           lepton.nValidMuonHits > 0 and lepton.isGlobalMuon != 0 and \
           lepton.chi2 < 10 and lepton.trackerLayers > 5 and lepton.validPixelLayers > 0 and lepton.matchedStations > 1:
            return True
        else:
            return False

def passes_baseline_probe_selection_ID_and_iso(lepton, channel = 'electron'):
    if channel == 'electron':
        if lepton.Pt() > 30 and abs(lepton.Eta()) < 2.5 and not is_in_crack(lepton) and lepton.dxy < 0.02 and lepton.passConversionVeto:
            return True
        else:
            return False
    else:
        if lepton.Pt() > 26 and abs(lepton.Eta()) < 2.1:
            return True
        else:
            return False

# Passing probe ID (numerator)
def passes_probe_ID_and_iso( lepton ):
    if channel == 'electron':
        if lepton.ID > 0.5 and lepton.isolation < 0.1:
            return True
        else:
            return False
    else:
        if lepton.isolation < 0.12 and lepton.ID != 0 and lepton.dxy < 0.2 and lepton.dz < 0.5 and \
           lepton.nValidMuonHits > 0 and lepton.isGlobalMuon != 0 and \
           lepton.chi2 < 10 and lepton.trackerLayers > 5 and lepton.validPixelLayers > 0 and lepton.matchedStations > 1:
            return True
        else:
            return False    

def is_in_crack( electron ):
    if abs(electron.Eta()) > 1.4442 and abs(electron.Eta()) < 1.566:
        return True
    else:
        return False

def is_true_lepton(mc_particle, pdg_id, channel):
    if channel == 'electron':
        if abs(pdg_id) == 11:
            return True
        else:
            return False
    elif channel == 'muon':
        if abs(pdg_id) == 13:
            return True
        else:
            return False
    else:
        return False


def read_lepton_collections( event, reco_leptons_collection, mc_genparticles_collection, trigger_object_lepton, mode = 'data', channel = 'electron', doTrigger = 'False' ):
    if mode == 'data':
        histograms = histograms_data
    else:
        histograms = histograms_mc
    reco_leptons = []
    hlt_leptons = []
    mc_leptons = []
    getVar = event.__getattr__
    run_number = getVar('Event.Run')
    # print 'Run number: ', run_number
    histograms['btag_multiplicity'].Fill( get_N_bjets( event, channel ) )
    reco_leptons_px = getVar(reco_leptons_collection + '.Px')
    reco_leptons_py = getVar(reco_leptons_collection + '.Py')
    reco_leptons_pz = getVar(reco_leptons_collection + '.Pz')
    reco_leptons_E  = getVar(reco_leptons_collection + '.Energy')
    reco_leptons_dxy = getVar(reco_leptons_collection + '.PrimaryVertexDXY')

    if channel == 'electron':
        reco_leptons_isolation = getVar(reco_leptons_collection + '.PFRelIso03RhoEA')
        reco_leptons_id = getVar(reco_leptons_collection + '.mvaTrigV0')
        reco_leptons_passConversionVeto = getVar(reco_leptons_collection + '.passConversionVeto')
        reco_leptons_innerHits = getVar(reco_leptons_collection + '.MissingHits')
    else:
        reco_leptons_isolation = getVar(reco_leptons_collection + '.PFRelIso04DeltaBeta')
        reco_leptons_id = getVar(reco_leptons_collection + '.isPFMuon')
        reco_leptons_chi2 = getVar(reco_leptons_collection+'.GlobalTrack.NormalizedChi2')
        reco_leptons_dz = getVar(reco_leptons_collection + '.Vertex.DistZ')
        reco_leptons_nValidMuonHits = getVar(reco_leptons_collection+'.GlobalTrack.NumberOfValidMuonHits')
        reco_leptons_trackerLayers = getVar(reco_leptons_collection+'.InnerTrack.TrackerLayersWithMeasurement')
        reco_leptons_validPixelLayers = getVar(reco_leptons_collection+'.InnerTrack.NumberOfValidPixelHits')
        reco_leptons_matchedStations = getVar(reco_leptons_collection+'.NumberOfMatchedStations')
        reco_leptons_isGlobalMuon = getVar(reco_leptons_collection+'.isGlobalMuon')

    assert reco_leptons_px.size() == reco_leptons_py.size() == reco_leptons_pz.size() == reco_leptons_E.size()

    # Get reco leptons and fill histograms for all reco leptons (not much selection)
    for index in range(reco_leptons_E.size()):
        reco_lepton = Particle(reco_leptons_px[index], reco_leptons_py[index], reco_leptons_pz[index], reco_leptons_E[index])
        reco_lepton.set_isolation(reco_leptons_isolation[index])
        reco_lepton.set_id(reco_leptons_id[index])
        reco_lepton.set_dxy(reco_leptons_dxy[index])
        if channel == 'electron':
            reco_lepton.set_inner_hits(reco_leptons_innerHits[index])
            reco_lepton.set_pass_conversion_veto(reco_leptons_passConversionVeto[index])
        else:
            reco_lepton.set_chi2(reco_leptons_chi2[index])
            reco_lepton.set_dz(reco_leptons_dz[index])
            reco_lepton.set_n_valid_muon_hits(reco_leptons_nValidMuonHits[index])
            reco_lepton.set_tracker_layers(reco_leptons_trackerLayers[index])
            reco_lepton.set_valid_pixel_layers(reco_leptons_validPixelLayers[index])
            reco_lepton.set_matched_stations(reco_leptons_matchedStations[index])
            reco_lepton.set_is_global_muon(reco_leptons_isGlobalMuon[index])
        reco_leptons.append(reco_lepton)
        histograms['reco_lepton_pt'].Fill(reco_lepton.Pt())
        histograms['reco_lepton_eta'].Fill(reco_lepton.Eta())

    # Reco lepton multiplicity
    histograms['reco_lepton_multiplicity'].Fill(len(reco_leptons))

    # Get MC truth lepton collection
    if mode == 'mc':
        mc_particles_px = getVar(mc_genparticles_collection + '.Px')
        mc_particles_py = getVar(mc_genparticles_collection + '.Py')
        mc_particles_pz = getVar(mc_genparticles_collection + '.Pz')
        mc_particles_E =  getVar(mc_genparticles_collection + '.Energy')
        mc_particles_id = getVar(mc_genparticles_collection + '.PdgId')
        assert mc_particles_px.size() == mc_particles_py.size() == mc_particles_pz.size() == mc_particles_E.size()
        for index in range(mc_particles_px.size()):
            mc_particle = Particle(mc_particles_px[index], mc_particles_py[index], mc_particles_pz[index], mc_particles_E[index])
            if is_true_lepton(mc_particle, mc_particles_id[index], channel):
                mc_leptons.append(mc_particle)
                histograms['mc_lepton_pt'].Fill(mc_particle.Pt())
                histograms['mc_lepton_eta'].Fill(mc_particle.Eta())
            else:
                continue
        histograms['mc_lepton_multiplicity'].Fill(len(mc_leptons))

    # Get HLT leptons and fill histograms for all hlt leptons
    if doTrigger:
        hlt_leptons_px = getVar(trigger_object_lepton + '.Px')
        hlt_leptons_py = getVar(trigger_object_lepton + '.Py')
        hlt_leptons_pz = getVar(trigger_object_lepton + '.Pz')
        hlt_leptons_E =  getVar(trigger_object_lepton + '.Energy')
        assert hlt_leptons_px.size() == hlt_leptons_py.size() == hlt_leptons_pz.size() == hlt_leptons_E.size()
        for index in range(hlt_leptons_px.size()):
            hlt_lepton = Particle(hlt_leptons_px[index], hlt_leptons_py[index], hlt_leptons_pz[index], hlt_leptons_E[index])
            hlt_leptons.append(hlt_lepton)
            histograms['hlt_lepton_pt'].Fill(hlt_lepton.Pt())
            histograms['hlt_lepton_eta'].Fill(hlt_lepton.Eta())

        # HLT lepton multiplicity
        histograms['hlt_lepton_multiplicity'].Fill(len(hlt_leptons))

    return reco_leptons, hlt_leptons, mc_leptons

def do_tag_and_probe_analysis( reco_leptons, hlt_leptons, mc_leptons, mode = 'data', channel = 'electron' ):
    global centre_of_mass, nEventsToConsider, nTagEvents, nProbeEvents, nPassingProbeEvents
    if mode == 'data':
        histograms = histograms_data
    else:
        histograms = histograms_mc

    if len(reco_leptons) == 1:
        print 'Just one lepton in event!'
        return

    if len(reco_leptons) >= 2:
        nEventsToConsider += 1
        for tag_lepton in reco_leptons:
            if passes_tag_selection( tag_lepton, hlt_leptons, match_to_trigger_object = options.doTrigger, channel = channel ):
                nTagEvents += 1

                # Fill histograms for tag lepton
                histograms['tag_reco_lepton_pt'].Fill(tag_lepton.Pt())
                histograms['tag_reco_lepton_eta'].Fill(tag_lepton.Eta())

                tag_hlt_lepton = Particle(0, 0, 0, 0)
                if options.doTrigger:
                    matched_index_signal_lepton, matched_delta_R_signal_lepton = match_four_momenta(tag_lepton, hlt_leptons)
                    tag_hlt_lepton = hlt_leptons[matched_index_signal_lepton]
                    histograms['tag_hlt_lepton_pt'].Fill(tag_hlt_lepton.Pt())
                    histograms['tag_hlt_lepton_eta'].Fill(tag_hlt_lepton.Eta())

                # pick the probe yielding best inv.mass with the tag
                probe_lepton = reco_leptons[ best_Z_peak_probe_index(tag_lepton, reco_leptons) ]

                if is_Z_event(tag_lepton, probe_lepton):
                    # All probes
                    passes_baseline_probe_selection = False
                    if options.doTrigger:
                        passes_baseline_probe_selection = passes_baseline_probe_selection_trigger(probe_lepton, channel)
                    elif options.doID:
                        passes_baseline_probe_selection = passes_baseline_probe_selection_ID_and_iso(probe_lepton, channel)

                    if passes_baseline_probe_selection:
                        nProbeEvents += 1
                        # histograms['probe_total_pt'].Fill(probe_lepton.Pt())
                        # histograms['probe_total_eta'].Fill(probe_lepton.Eta())
                        fill_Z_peak_histograms(tag_lepton, probe_lepton, mode = mode + '_total')
                        if mode == 'mc':
                            matched_index_mc_lepton, matched_delta_R_mc_lepton = match_four_momenta(probe_lepton, mc_leptons)
                            if matched_delta_R_mc_lepton < 0.1:
                                matched_mc_lepton = mc_leptons[matched_index_mc_lepton]
                                histograms['mc_matched_lepton_isolation'].Fill(probe_lepton.isolation)
                                histograms['mc_matched_lepton_ID'].Fill(probe_lepton.ID)

                        # Passing probes
                        passProbe = False
                        if options.doTrigger:
                            matched_index_probe_lepton, matched_delta_R_probe_lepton = match_four_momenta(probe_lepton, hlt_leptons)
                            if matched_delta_R_probe_lepton < 0.3:
                                passProbe = True
                        elif options.doID:
                            passProbe = passes_probe_ID_and_iso( probe_lepton )

                        if passProbe:
                            nPassingProbeEvents += 1
                            # histograms['probe_passed_pt'].Fill(probe_lepton.Pt())
                            # histograms['probe_passed_eta'].Fill(probe_lepton.Eta())
                            fill_Z_peak_histograms(tag_lepton, probe_lepton, mode = mode + '_passed')
                            if options.doTrigger:
                                probe_hlt_lepton = hlt_leptons[matched_index_probe_lepton]
                                histograms['probe_passed_hlt_pt'].Fill(probe_hlt_lepton.Pt())
                                histograms['probe_passed_hlt_eta'].Fill(probe_hlt_lepton.Eta())
                                histograms['tagProbe_passed_hlt_Z_peak'].Fill((probe_hlt_lepton.lorentz+tag_hlt_lepton.lorentz).M())

if __name__ == '__main__':
    set_root_defaults( msg_ignore_level = 3001 )
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='/hdfs/TopQuarkGroup/trigger_BLT_ntuples/',
                  help="set path to input BLT ntuples")
    parser.add_option("-o", "--output_folder", dest="output_folder", default='plots/',
                  help="set path to save tables")
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=8, type=int,
                      help="set the centre of mass energy for analysis. Default = 8 [TeV]")
    parser.add_option("--CB", dest="CB", action='store_true', default=False,
                      help="convolute Breit-Wigner with Crystall Ball for the Z signal peak")
    parser.add_option("--channel", dest="channel", default='electron',
                      help="set the lepton channel, default: electron")
    parser.add_option("--trigger", dest="doTrigger", action='store_true', default=False,
                      help="measure trigger efficiencies/scale factors")
    parser.add_option("--id", dest="doID", action='store_true', default=False,
                      help="measure id/isolation efficiencies/scale factors")

    (options, args) = parser.parse_args()
    use_CB_convolution = options.CB
    centre_of_mass = options.CoM
    if centre_of_mass == 7:
        input_path = options.path + '/2011/'
        output_folder = options.output_folder + '/2011/'
    else:
        input_path = options.path + '/2012/'
        output_folder = options.output_folder + '/2012/'

    if ( options.doTrigger and options.doID ) or not ( options.doTrigger or options.doID):
        print 'Choose one of trigger or iso/id scale factors'
        sys.exit(1)
    if options.doTrigger:
        suffix = 'trigger'
    else:
        suffix = 'id_iso'

    channel = options.channel
    if channel == 'electron':
        output_folder += '/electron/'
    else:
        output_folder += '/muon/'

    output_pickle_folder = './pickle_files/'
    make_folder_if_not_exists(output_folder)
    make_folder_if_not_exists(output_pickle_folder)
    output_formats = ['pdf']

    if channel == 'electron':
        data_histFile = input_path + '/SingleElectron_trigger_study.root'
        data_input_file = File(data_histFile)
        data_tree = data_input_file.Get('rootTupleTreeEPlusJets/ePlusJetsTree')
        mc_histFile = input_path + '/DYJetsToLL_M-50.root'
        mc_input_file = File(mc_histFile)
        mc_tree = mc_input_file.Get('rootTupleTreeEPlusJets/ePlusJetsTree')
        mc_genparticles_collection = 'GenParticle'
        reco_leptons_collection = 'selectedPatElectronsLoosePFlow'
        if centre_of_mass == 7:
            trigger_object_lepton = 'TriggerObjectElectronIsoLeg'
        else:
            trigger_object_lepton = 'TriggerObjectSingleElectron'
    else:
        data_histFile = input_path + '/SingleMu_trigger_study.root'
        data_input_file = File(data_histFile)
        data_tree = data_input_file.Get('rootTupleTreeMuPlusJets/muPlusJetsTree')
        mc_histFile = input_path + '/DYJetsToLL_M-50.root'
        mc_input_file = File(mc_histFile)
        mc_tree = mc_input_file.Get('rootTupleTreeMuPlusJets/muPlusJetsTree')
        mc_genparticles_collection = 'GenParticle'
        reco_leptons_collection = 'selectedPatMuonsLoosePFlow'
        if centre_of_mass == 7:
            trigger_object_lepton = 'TriggerObjectMuon2p1'
        else:
            trigger_object_lepton = 'TriggerObjectMuon2012Rho'

    print 'Number of events in data tree: ', data_tree.GetEntries(), ' and MC tree: ', mc_tree.GetEntries()

    for mode in ['data', 'mc']:
        nEvents = 0
        nEventsToConsider = 0
        nTagEvents = 0
        nProbeEvents = 0
        nPassingProbeEvents = 0

        if mode == 'data':
            tree = data_tree
        else:
            tree = mc_tree

        print 'Performing the tag and probe analysis on %s, %d TeV' % (mode, centre_of_mass)
        for event in tree:
            nEvents += 1
            run_number = event.__getattr__('Event.Run')

            if centre_of_mass == 7:
                if channel == 'electron':
                    if run_number >= 160404 and run_number <= 165633:
                        trigger_object_lepton = 'TriggerObjectElectronLeg'
                    elif run_number >= 165970 and run_number <= 178380:
                        trigger_object_lepton = 'TriggerObjectElectronIsoLeg'
                    elif run_number >= 178420 and run_number <= 180252:
                        trigger_object_lepton = 'TriggerObjectElectronIsoLeg'
                elif channel == 'muon':
                    if run_number >= 160404 and run_number <= 167913:
                        trigger_object_lepton = 'TriggerObjectMuon1'
                    elif run_number >= 170249 and run_number <= 173198:
                        trigger_object_lepton = 'TriggerObjectMuon2'
                    elif run_number >= 173236 and run_number < 190456:
                        trigger_object_lepton = 'TriggerObjectMuon2p1'
            if centre_of_mass == 8:
                if channel == 'electron':
                    trigger_object_lepton = 'TriggerObjectSingleElectron'
                elif channel == 'muon':
                    if run_number >= 190456 and run_number <= 193621:
                        trigger_object_lepton = 'TriggerObjectMuon2012'
                    elif run_number >= 193834 and run_number <= 209151:
                        trigger_object_lepton = 'TriggerObjectMuon2012Rho'
            
            reco_leptons, hlt_leptons, mc_leptons = read_lepton_collections( event, reco_leptons_collection,\
                        mc_genparticles_collection, trigger_object_lepton, mode, channel, doTrigger = options.doTrigger )
            do_tag_and_probe_analysis(reco_leptons, hlt_leptons, mc_leptons, mode, channel)
    
        print 'Number of events :', nEvents
        print 'Number of events with at least two reco leptons :', nEventsToConsider
        print 'Number of events with a tag lepton :', nTagEvents
        print 'Number of events with a probe lepton :', nProbeEvents
        print 'Number of events with a passing probe lepton :', nPassingProbeEvents

    
    make_Z_peak_plots('data', channel)
    make_Z_peak_plots('mc', channel)

    make_2D_efficiency_plot(histograms_data['probe_passed_pt_eta'], histograms_data['probe_total_pt_eta'], 'data_efficiency_pt_eta_' + suffix, channel)
    make_2D_efficiency_plot(histograms_mc['probe_passed_pt_eta'], histograms_mc['probe_total_pt_eta'], 'mc_efficiency_pt_eta_' + suffix, channel)

    produce_pickle_files(histograms_data['probe_passed_pt_eta'], histograms_data['probe_total_pt_eta'], histograms_mc['probe_passed_pt_eta'], histograms_mc['probe_total_pt_eta'], channel)

    make_efficiency_plot(histograms_data['probe_passed_pt'], histograms_data['probe_total_pt'], histograms_mc['probe_passed_pt'], histograms_mc['probe_total_pt'], 'efficiency_pt_' + suffix, channel)
    make_efficiency_plot(histograms_data['probe_passed_eta'], histograms_data['probe_total_eta'], histograms_mc['probe_passed_eta'], histograms_mc['probe_total_eta'], 'efficiency_eta_'  + suffix, channel)

    make_other_plots('data', channel)
    make_other_plots('mc', channel)



