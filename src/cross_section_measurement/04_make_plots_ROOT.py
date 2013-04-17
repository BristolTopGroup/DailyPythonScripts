from __future__ import division#the result of the division will be always a float
from optparse import OptionParser
import tools.plotting_utilities as plotting
import os
from copy import deepcopy

from config.cross_section_measurement_common import met_systematics_suffixes, translate_options, ttbar_theory_systematic_prefix, vjets_theory_systematic_prefix
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from tools.hist_utilities import value_error_tuplelist_to_hist, value_tuplelist_to_hist,\
    value_errors_tuplelist_to_graph
from math import sqrt
import ROOT
from ROOT import TPaveText, kRed, TH1F, kGreen, gROOT, kMagenta, kBlue, TGraphAsymmErrors
from ROOT import kAzure, kYellow, kViolet, THStack, gStyle
# rootpy
from rootpy.io import File
from rootpy import asrootpy
from rootpy.plotting import Hist, HistStack, Legend, Canvas
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from config import CMS
from matplotlib import rc
rc('text', usetex=True)
    
def read_xsection_measurement_results(category, channel):
    global path_to_JSON, variable, k_value, met_type
    
    normalised_xsection_unfolded = read_data_from_JSON(path_to_JSON  + '/xsection_measurement_results' + '/kv' + str(k_value) + '/' 
                                                       + category + '/normalised_xsection_' + channel + '_' + met_type + '.txt')
    h_normalised_xsection = value_error_tuplelist_to_hist(normalised_xsection_unfolded['TTJet_measured'], bin_edges[variable])
    h_normalised_xsection_unfolded = value_error_tuplelist_to_hist(normalised_xsection_unfolded['TTJet_unfolded'], bin_edges[variable])
    
    
    histograms_normalised_xsection_different_generators = {'measured':h_normalised_xsection,
                                                           'unfolded':h_normalised_xsection_unfolded}
    
    histograms_normalised_xsection_systematics_shifts = {'measured':h_normalised_xsection,
                                                         'unfolded':h_normalised_xsection_unfolded}
    
    if category == 'central':
        #true distributions
        h_normalised_xsection_MADGRAPH = value_error_tuplelist_to_hist(normalised_xsection_unfolded['MADGRAPH'], bin_edges[variable])
        h_normalised_xsection_POWHEG = value_error_tuplelist_to_hist(normalised_xsection_unfolded['POWHEG'], bin_edges[variable])
        h_normalised_xsection_MCATNLO = value_error_tuplelist_to_hist(normalised_xsection_unfolded['MCATNLO'], bin_edges[variable])
        h_normalised_xsection_mathchingup = value_error_tuplelist_to_hist(normalised_xsection_unfolded['matchingup'], bin_edges[variable])
        h_normalised_xsection_mathchingdown = value_error_tuplelist_to_hist(normalised_xsection_unfolded['matchingdown'], bin_edges[variable])
        h_normalised_xsection_scaleup = value_error_tuplelist_to_hist(normalised_xsection_unfolded['scaleup'], bin_edges[variable])
        h_normalised_xsection_scaledown = value_error_tuplelist_to_hist(normalised_xsection_unfolded['scaledown'], bin_edges[variable])
        
        histograms_normalised_xsection_different_generators.update({'MADGRAPH':h_normalised_xsection_MADGRAPH,
                                                                    'POWHEG':h_normalised_xsection_POWHEG,
                                                                    'MCATNLO':h_normalised_xsection_MCATNLO})
        
        histograms_normalised_xsection_systematics_shifts.update({'matchingdown': h_normalised_xsection_mathchingdown,
                                                                  'matchingup': h_normalised_xsection_mathchingup,
                                                                  'scaledown': h_normalised_xsection_scaledown,
                                                                  'scaleup': h_normalised_xsection_scaleup})
        
        normalised_xsection_unfolded_with_errors = read_data_from_JSON(path_to_JSON  + '/xsection_measurement_results' + '/kv' + 
                                                                   str(k_value) + '/' + category + '/normalised_xsection_' + 
                                                                   channel + '_' + met_type + '_with_errors.txt')
        #a rootpy.Graph with asymmetric errors!
        h_normalised_xsection_with_systematics = value_errors_tuplelist_to_graph(normalised_xsection_unfolded_with_errors['TTJet_measured'], bin_edges[variable])
        h_normalised_xsection_with_systematics_unfolded = value_errors_tuplelist_to_graph(normalised_xsection_unfolded_with_errors['TTJet_unfolded'], bin_edges[variable])
        
        histograms_normalised_xsection_different_generators['measured_with_systematics'] = h_normalised_xsection_with_systematics
        histograms_normalised_xsection_different_generators['unfolded_with_systematics']  = h_normalised_xsection_with_systematics_unfolded
        
        histograms_normalised_xsection_systematics_shifts['measured_with_systematics'] = h_normalised_xsection_with_systematics
        histograms_normalised_xsection_systematics_shifts['unfolded_with_systematics']  = h_normalised_xsection_with_systematics_unfolded
    
    return histograms_normalised_xsection_different_generators, histograms_normalised_xsection_systematics_shifts

def read_unfolded_xsections(channel):
    global path_to_JSON, variable, k_value, met_type, b_tag_bin
    TTJet_xsection_unfolded = {}
    for category in categories:
        normalised_xsections = read_data_from_JSON(path_to_JSON  + '/xsection_measurement_results' + '/kv' + str(k_value) + '/' + category + '/normalised_xsection_' + channel + '_' + met_type + '.txt')
        TTJet_xsection_unfolded[category] = normalised_xsections['TTJet_unfolded']
    return TTJet_xsection_unfolded

def read_fit_templates_and_results_as_histograms(category, channel):
    global path_to_JSON, variable, met_type
    templates = read_data_from_JSON(path_to_JSON  + '/fit_results/' + category + '/templates_' + channel + '_' + met_type + '.txt')
    data_values = read_data_from_JSON(path_to_JSON  + '/fit_results/' + category + '/initial_values_' + channel + '_' + met_type + '.txt')['data']
    fit_results = read_data_from_JSON(path_to_JSON  + '/fit_results/' + category + '/fit_results_' + channel + '_' + met_type + '.txt')
    template_histograms = {}
    fit_results_histograms = {}
    for bin_i, variable_bin in enumerate(variable_bins_ROOT[variable]):
        h_template_data = value_tuplelist_to_hist(templates['data'][bin_i], eta_bin_edges)
        h_template_signal = value_tuplelist_to_hist(templates['signal'][bin_i], eta_bin_edges)
        h_template_VJets = value_tuplelist_to_hist(templates['V+Jets'][bin_i], eta_bin_edges)
        h_template_QCD = value_tuplelist_to_hist(templates['QCD'][bin_i], eta_bin_edges)
        template_histograms[variable_bin] = {
                                    'signal':h_template_signal,
                                    'V+Jets':h_template_VJets,
                                    'QCD':h_template_QCD
                                    }
        h_data = h_template_data.Clone()
        h_signal = h_template_signal.Clone()
        h_VJets = h_template_VJets.Clone()
        h_QCD = h_template_QCD.Clone()
        
        data_normalisation = data_values[bin_i]
        signal_normalisation = fit_results['signal'][bin_i][0]
        VJets_normalisation = fit_results['V+Jets'][bin_i][0]
        QCD_normalisation = fit_results['QCD'][bin_i][0]
        
        h_data.Scale(data_normalisation)
        h_signal.Scale(signal_normalisation)
        h_VJets.Scale(VJets_normalisation)
        h_QCD.Scale(QCD_normalisation)
        h_background = h_VJets + h_QCD
        
        for bin_i in range(len(h_data)):
            h_data.SetBinError(bin_i+1, sqrt(h_data.GetBinContent(bin_i+1)))
        
        fit_results_histograms[variable_bin] = {
                                                'data':h_data,
                                                'signal':h_signal,
                                                'background':h_background
                                                }
        
    return template_histograms, fit_results_histograms

def make_template_plots(histograms, category, channel):
    global variable, output_folder
    
    for variable_bin in variable_bins_ROOT[variable]:
        path = output_folder + str(measurement_config.centre_of_mass) + 'TeV/' + variable + '/' + category + '/fit_templates/'
        make_folder_if_not_exists(path)
        plotname = path + channel + '_templates_bin_' + variable_bin
        #check if template plots exist already
        for output_format in output_formats:
            if os.path.isfile(plotname + '.' + output_format):
                continue
        canvas = Canvas(width=700, height=500)
        canvas.SetLeftMargin(0.15)
        canvas.SetBottomMargin(0.15)
        canvas.SetTopMargin(0.05)
        canvas.SetRightMargin(0.05)
        legend = plotting.create_legend(x0=0.7, y1=0.8)
        h_signal = histograms[variable_bin]['signal']
        h_VJets = histograms[variable_bin]['V+Jets']
        h_QCD = histograms[variable_bin]['QCD']
        
        h_signal.GetXaxis().SetTitle('Lepton #eta')
        h_signal.GetYaxis().SetTitle('Normalised Events')
        h_signal.GetXaxis().SetTitleSize(0.05)
        h_signal.GetYaxis().SetTitleSize(0.05)
        h_signal.SetMinimum(0)
        h_signal.SetMaximum(0.2)
        h_signal.SetLineWidth(2)
        h_VJets.SetLineWidth(2)
        h_QCD.SetLineWidth(2)
        h_signal.SetLineColor(kRed + 1)
        h_VJets.SetLineColor(kBlue)
        h_QCD.SetLineColor(kYellow)
        h_signal.Draw('hist')
        h_VJets.Draw('hist same')
        h_QCD.Draw('hist same')
        legend.AddEntry(h_signal, 'signal', 'l')
        legend.AddEntry(h_VJets, 'V+Jets', 'l')
        legend.AddEntry(h_QCD, 'QCD', 'l')
        legend.Draw()
        
        cms_label, channel_label = get_cms_labels(channel)
        cms_label.Draw()
        channel_label.Draw()
        
        canvas.Modified()
        canvas.Update()
        for output_format in output_formats:
            canvas.SaveAs(plotname + '.' + output_format)
        
def plot_fit_results(histograms, category, channel):
    global variable, translate_options, b_tag_bin, output_folder
    #ROOT.TH1.SetDefaultSumw2(False)
    
    for variable_bin in variable_bins_ROOT[variable]:
        path = output_folder + str(measurement_config.centre_of_mass) + 'TeV/' + variable + '/' + category + '/fit_results/'
        make_folder_if_not_exists(path)
        plotname = path + channel + '_bin_' + variable_bin
        # check if template plots exist already
        for output_format in output_formats:
            if os.path.isfile(plotname + '.' + output_format):
                continue
        canvas = Canvas(width=700, height=500)
        canvas.SetLeftMargin(0.15)
        canvas.SetBottomMargin(0.15)
        canvas.SetTopMargin(0.05)
        canvas.SetRightMargin(0.05)
        legend = plotting.create_legend(x0=0.7, y1=0.8)
        h_data = histograms[variable_bin]['data']
        h_signal = histograms[variable_bin]['signal']
        h_background = histograms[variable_bin]['background']
        
        h_data.GetXaxis().SetTitle('Lepton #eta')
        h_data.GetYaxis().SetTitle('Number of Events')
        h_data.GetXaxis().SetTitleSize(0.05)
        h_data.GetYaxis().SetTitleSize(0.05)
        h_data.SetMinimum(0)
        h_data.SetMarkerSize(1)
        h_data.SetMarkerStyle(20)
        gStyle.SetEndErrorSize(20)
        h_data.Draw('P')
        
        h_signal.SetFillColor(kRed + 1)
        h_background.SetFillColor(kGreen-3)
        h_signal.SetLineWidth(2)
        h_background.SetLineWidth(2)
        h_signal.SetFillStyle(1001)
        h_background.SetFillStyle(1001)
        
        mcStack = THStack("MC", "MC")
        mcStack.Add(h_background)
        mcStack.Add(h_signal)
        
        mcStack.Draw('hist same')
        h_data.Draw('error P same')
        legend.AddEntry(h_data, 'data', 'P')
        legend.AddEntry(h_signal, 'signal', 'F')
        legend.AddEntry(h_background, 'background', 'F')
        legend.Draw()
        
        mytext = TPaveText(0.5, 0.97, 1, 1.01, "NDC")
        channelLabel = TPaveText(0.18, 0.97, 0.5, 1.01, "NDC")
        if channel == 'electron':
            channelLabel.AddText("e, %s, %s" % ("#geq 4 jets", b_tag_bins_latex[b_tag_bin]))
        elif channel == 'muon':
            channelLabel.AddText("#mu, %s, %s" % ("#geq 4 jets", b_tag_bins_latex[b_tag_bin]))
        else:
            channelLabel.AddText("combined, %s, %s" % ("#geq 4 jets", b_tag_bins_latex[b_tag_bin]))
        mytext.AddText("CMS Preliminary, L = %.1f fb^{-1} at #sqrt{s} = 8 TeV" % (5.8));
             
        mytext.SetFillStyle(0)
        mytext.SetBorderSize(0)
        mytext.SetTextFont(42)
        mytext.SetTextAlign(13)
        
        channelLabel.SetFillStyle(0)
        channelLabel.SetBorderSize(0)
        channelLabel.SetTextFont(42)
        channelLabel.SetTextAlign(13)
        mytext.Draw()
        channelLabel.Draw()
        
        canvas.Modified()
        canvas.Update()
        for output_format in output_formats:
            canvas.SaveAs(plotname + '.' + output_format)

def get_cms_labels(channel):     
    global b_tag_bin,  b_tag_bins_latex  
    
    cms_label = TPaveText(0.5, 0.97, 1, 1.01, "NDC")
    channel_label = TPaveText(0.18, 0.97, 0.5, 1.01, "NDC")
    
    if channel == 'electron':
        channel_label.AddText("e, %s, %s" % ("#geq 4 jets", b_tag_bins_latex[b_tag_bin]))
    elif channel == 'muon':
        channel_label.AddText("#mu, %s, %s" % ("#geq 4 jets", b_tag_bins_latex[b_tag_bin]))
    else:
        channel_label.AddText("combined, %s, %s" % ("#geq 4 jets", b_tag_bins_latex[b_tag_bin]))
        
    cms_label.AddText("CMS Preliminary, L = %.1f fb^{-1} at #sqrt{s} = %d TeV" % (measurement_config.luminosity/1000, measurement_config.centre_of_mass));
             
    cms_label.SetFillStyle(0)
    cms_label.SetBorderSize(0)
    cms_label.SetTextFont(42)
    cms_label.SetTextAlign(13)
    
    channel_label.SetFillStyle(0)
    channel_label.SetBorderSize(0)
    channel_label.SetTextFont(42)
    channel_label.SetTextAlign(13)
    
    return cms_label, channel_label

    
def make_plots(histograms, category, output_folder, histname):
    global variable, variables_latex, measurements_latex, k_value, b_tag_bin, maximum
    
    channel = 'electron'
    if 'electron' in histname:
        channel = 'electron'
    elif 'muon' in histname:
        channel = 'muon'
    else:
        channel = 'combined'

    canvas = Canvas(width=700, height=500)
    canvas.SetLeftMargin(0.15)
    canvas.SetBottomMargin(0.15)
    canvas.SetTopMargin(0.05)
    canvas.SetRightMargin(0.05)
    legend = plotting.create_legend(x0=0.6, y1=0.5)
    
    
    hist_data = histograms['unfolded']
    hist_data.GetXaxis().SetTitle(variables_latex[variable] + ' [GeV]')
    hist_data.GetYaxis().SetTitle('#frac{1}{#sigma} #frac{d#sigma}{d' + variables_latex[variable] + '} [GeV^{-1}]')
    hist_data.GetXaxis().SetTitleSize(0.05)
    hist_data.GetYaxis().SetTitleSize(0.05)
    hist_data.SetMinimum(0)
    hist_data.SetMaximum(maximum[variable])
    hist_data.SetMarkerSize(1)
    hist_data.SetMarkerStyle(8)
    
    hist_data_with_systematics = histograms['unfolded_with_systematics']
    hist_data_with_systematics.GetXaxis().SetTitle(variables_latex[variable] + ' [GeV]')
    hist_data_with_systematics.GetYaxis().SetTitle('#frac{1}{#sigma} #frac{d#sigma}{d' + variables_latex[variable] + '} [GeV^{-1}]')
    hist_data_with_systematics.GetXaxis().SetTitleSize(0.05)
    hist_data_with_systematics.GetYaxis().SetTitleSize(0.05)
    hist_data_with_systematics.SetMinimum(0)
    hist_data_with_systematics.SetMaximum(maximum[variable])
    hist_data_with_systematics.SetMarkerSize(1)
    hist_data_with_systematics.SetMarkerStyle(8)
    
    plotAsym = TGraphAsymmErrors(hist_data_with_systematics)
    plotStatErr = TGraphAsymmErrors(hist_data)
    
    xsections = read_unfolded_xsections(channel)
    bins = variable_bins_ROOT[variable]
    assert(len(bins) == len(xsections['central']))
    
    gStyle.SetEndErrorSize(20)
    plotAsym.SetLineWidth(2)
    plotStatErr.SetLineWidth(2)
    hist_data.Draw('P')
    plotStatErr.Draw('same P')
    plotAsym.Draw('same P Z')
    legend.AddEntry(hist_data, 'unfolded', 'P')
    
    hist_measured = histograms['measured']
    hist_measured.SetMarkerSize(1)
    hist_measured.SetMarkerStyle(20)
    hist_measured.SetMarkerColor(2)
    hist_measured.Draw('same P')
    legend.AddEntry(hist_measured, 'measured', 'P')
    
    for key, hist in histograms.iteritems():
        if not 'unfolded' in key and not 'measured' in key:
            hist.SetLineStyle(7)
            hist.SetLineWidth(2)
            #setting colours
            if 'POWHEG' in key or 'matchingdown' in key:
                hist.SetLineColor(kBlue)
            elif 'MADGRAPH' in key or 'matchingup' in key:
                hist.SetLineColor(kRed + 1)
            elif 'MCATNLO'  in key or 'scaleup' in key:
                hist.SetLineColor(kMagenta + 3)
            elif 'scaledown' in key:
                hist.SetLineColor(kGreen)
            hist.Draw('hist same')
            legend.AddEntry(hist, measurements_latex[key], 'l')
            
    
    legend.Draw()
             
    cms_label, channel_label = get_cms_labels(channel)
    cms_label.Draw()
    channel_label.Draw()
    
    canvas.Modified()
    canvas.Update()
    
    path = output_folder + str(measurement_config.centre_of_mass) + 'TeV/' + variable + '/' + category
    make_folder_if_not_exists(path)
    
    for output_format in output_formats:
        canvas.SaveAs(path + '/' + histname + '_kv' + str(k_value) + '.' + output_format)



def plot_central_and_systematics(channel, systematics, exclude=[], suffix='altogether'):
    global variable, variables_latex, k_value, b_tag_bin, maximum, ttbar_generator_systematics

    canvas = Canvas(width=700, height=500)
    canvas.SetLeftMargin(0.15)
    canvas.SetBottomMargin(0.15)
    canvas.SetTopMargin(0.05)
    canvas.SetRightMargin(0.05)
    legend = plotting.create_legend(x0=0.6, y1=0.5)
    
    hist_data_central = read_xsection_measurement_results('central', channel)[0]['unfolded']
    
    hist_data_central.GetXaxis().SetTitle(variables_latex[variable] + ' [GeV]')
    hist_data_central.GetYaxis().SetTitle('#frac{1}{#sigma} #frac{d#sigma}{d' + variables_latex[variable] + '} [GeV^{-1}]')
    hist_data_central.GetXaxis().SetTitleSize(0.05)
    hist_data_central.GetYaxis().SetTitleSize(0.05)
    hist_data_central.SetMinimum(0)
    hist_data_central.SetMaximum(maximum[variable])
    hist_data_central.SetMarkerSize(1)
    hist_data_central.SetMarkerStyle(20)

    gStyle.SetEndErrorSize(20)
    hist_data_central.Draw('P')
    legend.AddEntry(hist_data_central, 'measured (unfolded)', 'P')
    
    for systematic in systematics:
        if systematic in exclude or systematic == 'central':
            continue

        hist_data_systematic = read_xsection_measurement_results(systematic, channel)[0]['unfolded']
        hist_data_systematic.SetMarkerSize(0.5)
        hist_data_systematic.SetMarkerStyle(20)
        colour_number = systematics.index(systematic)+1
        if colour_number == 10:
            colour_number = 42
        hist_data_systematic.SetMarkerColor(colour_number)
        hist_data_systematic.Draw('same P')
        legend.AddEntry(hist_data_systematic, systematic, 'P')
    
    legend.Draw()
    
    cms_label, channel_label = get_cms_labels(channel)
    cms_label.Draw()
    
    channel_label.Draw()
    
    canvas.Modified()
    canvas.Update()
    
    path = output_folder + str(measurement_config.centre_of_mass) + 'TeV/' + variable
    make_folder_if_not_exists(path)
    
    for output_format in output_formats:
        canvas.SaveAs(path + '/normalised_xsection_' + channel + '_' + suffix + '_kv' + str(k_value) + '.' + output_format)

def plot_templates():
    pass
if __name__ == '__main__':
    ROOT.TH1.SetDefaultSumw2(False)
    ROOT.gROOT.SetBatch(True)
    ROOT.gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    plotting.setStyle()
    gStyle.SetTitleYOffset(1.4)
    ROOT.gROOT.ForceStyle()
    
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data/',
                  help="set path to JSON files")
    parser.add_option("-o", "--output_folder", dest="output_folder", default='plots/',
                  help="set path to save plots")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                  help="set variable to plot (MET, HT, ST, MT)")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type used in the analysis of MET, ST or MT")
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                  help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("-k", "--k_value", type='int',
                      dest="k_value", default=4,
                      help="k-value for SVD unfolding, used in histogram names")
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=8, type=int,
                      help="set the centre of mass energy for analysis. Default = 8 [TeV]")
    parser.add_option("-a", "--additional-plots", action="store_true", dest="additional_plots",
                      help="creates a set of plots for each systematic (in addition to central result).")
    
    maximum = {
               'MET': 0.02,
               'HT': 0.005,
               'ST': 0.004,
               'MT': 0.02
               }
    
    b_tag_bins_latex = {'0btag':'0 b-tags', '0orMoreBtag':'#geq 0 b-tags', '1btag':'1 b-tags',
                    '1orMoreBtag':'#geq 1 b-tags',
                    '2btags':'2 b-tags', '2orMoreBtags':'#geq 2 b-tags',
                    '3btags':'3 b-tags', '3orMoreBtags':'#geq 3 b-tags',
                    '4orMoreBtags':'#geq 4 b-tags'}
    
    variables_latex = {
                       'MET': 'E_{T}^{miss}',
                        'HT': 'H_{T}',
                        'ST': 'S_{T}',
                        'MT': 'M_{T}'}
    
    measurements_latex = {'unfolded': 'unfolded',
                        'measured': 'measured',
                        'MADGRAPH': 't#bar{t} (MADGRAPH)',
                        'MCATNLO': 't#bar{t} (MC@NLO)',
                        'POWHEG': 't#bar{t} (POWHEG)',
                        'matchingdown': 't#bar{t} (matching down)',
                        'matchingup': 't#bar{t} (matching up)',
                        'scaledown': 't#bar{t} (Q^{2} down)',
                        'scaleup': 't#bar{t} (Q^{2} up)',
                        'TTJets_matchingdown': 't#bar{t} (matching down)',
                        'TTJets_matchingup': 't#bar{t} (matching up)',
                        'TTJets_scaledown': 't#bar{t} (Q^{2} down)',
                        'TTJets_scaleup': 't#bar{t} (Q^{2} up)',
                        'VJets_matchingdown': 'V+jets (matching down)',
                        'VJets_matchingup': 'V+jets (matching up)',
                        'VJets_scaledown': 'V+jets (Q^{2} down)',
                        'VJets_scaleup': 'V+jets(Q^{2} up)',
                          }
    output_formats = ['png', 'pdf']
    (options, args) = parser.parse_args()
    if options.CoM == 8:
        from config.variable_binning_8TeV import bin_edges, variable_bins_ROOT, eta_bin_edges
        import config.cross_section_measurement_8TeV as measurement_config
    elif options.CoM == 7:
        from config.variable_binning_7TeV import bin_edges, variable_bins_ROOT, eta_bin_edges
        import config.cross_section_measurement_7TeV as measurement_config
    else:
        import sys
        sys.exit('Unknown centre of mass energy')
    
    variable = options.variable
    output_folder = options.output_folder
    if not output_folder.endswith('/'):
        output_folder += '/'
    k_value = options.k_value
    met_type = translate_options[options.metType]
    b_tag_bin = translate_options[options.bjetbin]
    path_to_JSON = options.path + '/' + str(measurement_config.centre_of_mass) + 'TeV/' + variable + '/'
    
    categories = deepcopy(measurement_config.categories_and_prefixes.keys())
    ttbar_generator_systematics = [ttbar_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    vjets_generator_systematics = [vjets_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    categories.extend(ttbar_generator_systematics)
    categories.extend(vjets_generator_systematics)
    
    pdf_uncertainties = ['PDFWeights_%d' % index for index in range(1,45)]
    pdf_uncertainties_1_to_11 = ['PDFWeights_%d' % index for index in range(1,12)]
    pdf_uncertainties_12_to_22 = ['PDFWeights_%d' % index for index in range(12,23)]
    pdf_uncertainties_23_to_33 = ['PDFWeights_%d' % index for index in range(23,34)]
    pdf_uncertainties_34_to_44 = ['PDFWeights_%d' % index for index in range(34,45)]
    #all MET uncertainties except JES as this is already included
    met_uncertainties = [met_type + suffix for suffix in met_systematics_suffixes if not 'JetEn' in suffix and not 'JetRes' in suffix]
    all_measurements = deepcopy(categories)
    all_measurements.extend(pdf_uncertainties)
    all_measurements.extend(met_uncertainties)
    
    for category in all_measurements:
        if not category == 'central' and not options.additional_plots:
            continue
        #setting up systematic MET for JES up/down samples for reading fit templates
        met_type = translate_options[options.metType]
        if category == 'JES_up':
            met_type += 'JetEnUp'
            if met_type == 'PFMETJetEnUp':
                met_type = 'patPFMetJetEnUp'
        elif category == 'JES_down':
            met_type += 'JetEnDown'
            if met_type == 'PFMETJetEnDown':
                met_type = 'patPFMetJetEnDown'
        
        electron_fit_templates, electron_fit_results = read_fit_templates_and_results_as_histograms(category, 'electron')
        muon_fit_templates, muon_fit_results = read_fit_templates_and_results_as_histograms(category, 'muon')
        
        #change back to original MET type
        met_type = translate_options[options.metType]
        if met_type == 'PFMET':
            met_type = 'patMETsPFlow'
        
        make_template_plots(electron_fit_templates, category, 'electron')
        make_template_plots(muon_fit_templates, category, 'muon')
        plot_fit_results(electron_fit_results, category, 'electron')
        plot_fit_results(muon_fit_results, category, 'muon')
        
        histograms_normalised_xsection_electron_different_generators, histograms_normalised_xsection_electron_systematics_shifts = read_xsection_measurement_results(category, 'electron')
        histograms_normalised_xsection_muon_different_generators, histograms_normalised_xsection_muon_systematics_shifts = read_xsection_measurement_results(category, 'muon')

        make_plots(histograms_normalised_xsection_muon_different_generators, category, output_folder, 'normalised_xsection_muon_different_generators')
        make_plots(histograms_normalised_xsection_muon_systematics_shifts, category, output_folder, 'normalised_xsection_muon_systematics_shifts')
    
        make_plots(histograms_normalised_xsection_electron_different_generators, category, output_folder, 'normalised_xsection_electron_different_generators')
        make_plots(histograms_normalised_xsection_electron_systematics_shifts, category, output_folder, 'normalised_xsection_electron_systematics_shifts')

    plot_central_and_systematics('electron', categories, exclude=ttbar_generator_systematics)
    plot_central_and_systematics('muon', categories, exclude=ttbar_generator_systematics)
    
    plot_central_and_systematics('electron', ttbar_generator_systematics, suffix='ttbar_theory_only')
    plot_central_and_systematics('muon', ttbar_generator_systematics, suffix='ttbar_theory_only')
    
    exclude = set(pdf_uncertainties).difference(set(pdf_uncertainties_1_to_11))
    plot_central_and_systematics('electron', pdf_uncertainties_1_to_11, exclude=exclude, suffix='PDF_1_to_11')
    plot_central_and_systematics('muon', pdf_uncertainties_1_to_11, exclude=exclude, suffix='PDF_1_to_11')
    
    exclude = set(pdf_uncertainties).difference(set(pdf_uncertainties_12_to_22))
    plot_central_and_systematics('electron', pdf_uncertainties_12_to_22, exclude=exclude, suffix='PDF_12_to_22')
    plot_central_and_systematics('muon', pdf_uncertainties_12_to_22, exclude=exclude, suffix='PDF_12_to_22')
    
    exclude = set(pdf_uncertainties).difference(set(pdf_uncertainties_23_to_33))
    plot_central_and_systematics('electron', pdf_uncertainties_23_to_33, exclude=exclude, suffix='PDF_23_to_33')
    plot_central_and_systematics('muon', pdf_uncertainties_23_to_33, exclude=exclude, suffix='PDF_23_to_33')
    
    exclude = set(pdf_uncertainties).difference(set(pdf_uncertainties_34_to_44))
    plot_central_and_systematics('electron', pdf_uncertainties_34_to_44, exclude=exclude, suffix='PDF_34_to_44')
    plot_central_and_systematics('muon', pdf_uncertainties_34_to_44, exclude=exclude, suffix='PDF_34_to_44')
    
    plot_central_and_systematics('electron', met_uncertainties, suffix='MET_only')
    plot_central_and_systematics('muon', met_uncertainties, suffix='MET_only')
