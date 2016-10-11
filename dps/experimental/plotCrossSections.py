from optparse import OptionParser
import dps.utils.plotting_utilities as plotting
import os
# @BROKEN
from dps.config.variable_binning_8TeV import bin_edges, variable_bins_ROOT, eta_bin_edges
from dps.utils.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from dps.utils.hist_utilities import value_error_tuplelist_to_hist, value_tuplelist_to_hist
from dps.utils.Calculation import calculateTotalUncertainty, symmetriseErrors
import ROOT
from ROOT import TPaveText, kRed, TH1F, Double, TMinuit, Long, kGreen, gROOT, TCanvas, kMagenta, kBlue, TGraphAsymmErrors, TMath
from ROOT import kAzure, kYellow, kViolet, THStack, gStyle
# rootpy
from rootpy.io import File
from rootpy import asrootpy
from rootpy.plotting import Hist, HistStack, Legend, Canvas
from math import sqrt
# import rootpy.plotting.root2matplotlib as rplt
# import matplotlib.pyplot as plt
# from matplotlib.ticker import AutoMinorLocator

b_tag_bins_latex = {'0btag':'0 b-tags', '0orMoreBtag':'#geq 0 b-tags', '1btag':'1 b-tags',
                    '1orMoreBtag':'#geq 1 b-tags',
                    '2btags':'2 b-tags', '2orMoreBtags':'#geq 2 b-tags',
                    '3btags':'3 b-tags', '3orMoreBtags':'#geq 3 b-tags',
                    '4orMoreBtags':'#geq 4 b-tags'}

def read_xsection_measurement_results(category, channel):
    global path_to_JSON, variable, k_value, met_type
    normalised_xsection_unfolded = read_data_from_JSON(path_to_JSON + '/' + variable + '/xsection_measurement_results' + '/kv' + str(k_value) + '/' + category + '/normalised_xsection_' + channel + '_' + met_type + '.txt')
    h_normalised_xsection = value_error_tuplelist_to_hist(normalised_xsection_unfolded['TTJet_measured'], bin_edges[variable])
    h_normalised_xsection_unfolded = value_error_tuplelist_to_hist(normalised_xsection_unfolded['TTJet_unfolded'], bin_edges[variable])
    h_normalised_xsection_MADGRAPH = value_error_tuplelist_to_hist(normalised_xsection_unfolded['MADGRAPH'], bin_edges[variable])
    h_normalised_xsection_POWHEG = value_error_tuplelist_to_hist(normalised_xsection_unfolded['POWHEG'], bin_edges[variable])
    h_normalised_xsection_MCATNLO = value_error_tuplelist_to_hist(normalised_xsection_unfolded['MCATNLO'], bin_edges[variable])
    h_normalised_xsection_mathchingup = value_error_tuplelist_to_hist(normalised_xsection_unfolded['matchingup'], bin_edges[variable])
    h_normalised_xsection_mathchingdown = value_error_tuplelist_to_hist(normalised_xsection_unfolded['matchingdown'], bin_edges[variable])
    h_normalised_xsection_scaleup = value_error_tuplelist_to_hist(normalised_xsection_unfolded['scaleup'], bin_edges[variable])
    h_normalised_xsection_scaledown = value_error_tuplelist_to_hist(normalised_xsection_unfolded['scaledown'], bin_edges[variable])
    
    histograms_normalised_xsection_different_generators = {
                  'measured':h_normalised_xsection,
                  'unfolded':h_normalised_xsection_unfolded,
                  'MADGRAPH':h_normalised_xsection_MADGRAPH,
                  'POWHEG':h_normalised_xsection_POWHEG,
                  'MCATNLO':h_normalised_xsection_MCATNLO
                  }
    
    histograms_normalised_xsection_systematics_shifts = {
                  'measured':h_normalised_xsection,
                  'unfolded':h_normalised_xsection_unfolded,
                  'matchingdown': h_normalised_xsection_mathchingdown,
                  'matchingup': h_normalised_xsection_mathchingup,
                  'scaledown': h_normalised_xsection_scaledown,
                  'scaleup': h_normalised_xsection_scaleup
                  }
    
    return histograms_normalised_xsection_different_generators, histograms_normalised_xsection_systematics_shifts

def read_unfolded_xsections(channel):
    global path_to_JSON, variable, k_value, met_type, b_tag_bin
    TTJet_xsection_unfolded = {}
    for category in categories:
        normalised_xsections = read_data_from_JSON(path_to_JSON + '/' + variable + '/xsection_measurement_results' + '/kv' + str(k_value) + '/' + category + '/normalised_xsection_' + channel + '_' + met_type + '.txt')
        TTJet_xsection_unfolded[category] = normalised_xsections['TTJet_unfolded']
    return TTJet_xsection_unfolded

def read_fit_templates_and_results_as_histograms(category, channel):
    global path_to_JSON, variable, met_type
    templates = read_data_from_JSON(path_to_JSON + '/' + variable + '/fit_results/' + category + '/templates_' + channel + '_' + met_type + '.txt')
    data_values = read_data_from_JSON(path_to_JSON + '/' + variable + '/fit_results/' + category + '/initial_values_' + channel + '_' + met_type + '.txt')['data']
    fit_results = read_data_from_JSON(path_to_JSON + '/' + variable + '/fit_results/' + category + '/fit_results_' + channel + '_' + met_type + '.txt')
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
    global variable, translate_options, b_tag_bin, save_path
    ROOT.TH1.SetDefaultSumw2(False)
    ROOT.gROOT.SetBatch(True)
    ROOT.gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    plotting.setStyle()
    gStyle.SetTitleYOffset(1.4)
    ROOT.gROOT.ForceStyle()
    
    for variable_bin in variable_bins_ROOT[variable]:
        path = save_path + '/' + variable + '/' + category + '/fit_templates/'
        make_folder_if_not_exists(path)
        plotname = path + channel + '_templates_bin_' + variable_bin + '.png'
        # check if template plots exist already
        if os.path.isfile(plotname):
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
        canvas.SaveAs(plotname)
        canvas.SaveAs(plotname.replace('png', 'pdf'))

def plot_fit_results(histograms, category, channel):
    global variable, translate_options, b_tag_bin, save_path
    #ROOT.TH1.SetDefaultSumw2(False)
    ROOT.gROOT.SetBatch(True)
    ROOT.gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    plotting.setStyle()
    gStyle.SetTitleYOffset(1.4)
    ROOT.gROOT.ForceStyle()
    
    for variable_bin in variable_bins_ROOT[variable]:
        path = save_path + '/' + variable + '/' + category + '/fit_results/'
        make_folder_if_not_exists(path)
        plotname = path + channel + '_bin_' + variable_bin + '.png'
        # check if template plots exist already
        if os.path.isfile(plotname):
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
        canvas.SaveAs(plotname)
        canvas.SaveAs(plotname.replace('png', 'pdf'))
         

def make_plots_ROOT(histograms, category, save_path, histname, channel):
    global variable, translateOptions, k_value, b_tag_bin, maximum
    ROOT.TH1.SetDefaultSumw2(False)
    ROOT.gROOT.SetBatch(True)
    ROOT.gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    plotting.setStyle()
    gStyle.SetTitleYOffset(2.)
    ROOT.gROOT.ForceStyle()
    canvas = Canvas(width=700, height=500)
    canvas.SetLeftMargin(0.18)
    canvas.SetBottomMargin(0.15)
    canvas.SetTopMargin(0.05)
    canvas.SetRightMargin(0.05)
    legend = plotting.create_legend(x0=0.6, y1=0.5)
    
    hist_data = histograms['unfolded']
    hist_data.GetXaxis().SetTitle(translate_options[variable] + ' [GeV]')
    hist_data.GetYaxis().SetTitle('#frac{1}{#sigma} #frac{d#sigma}{d' + translate_options[variable] + '} [GeV^{-1}]')
    hist_data.GetXaxis().SetTitleSize(0.05)
    hist_data.GetYaxis().SetTitleSize(0.05)
    hist_data.SetMinimum(0)
    hist_data.SetMaximum(maximum[variable])
    hist_data.SetMarkerSize(1)
    hist_data.SetMarkerStyle(8)
    plotAsym = TGraphAsymmErrors(hist_data)
    plotStatErr = TGraphAsymmErrors(hist_data)
    
    xsections = read_unfolded_xsections(channel)
    bins = variable_bins_ROOT[variable]
    assert(len(bins) == len(xsections['central']))
    
    for bin_i in range(len(bins)):
        scale = 1# / width
        centralresult = xsections['central'][bin_i]
        fit_error = centralresult[1]
        uncertainty = calculateTotalUncertainty(xsections, bin_i)
        uncertainty_total_plus = uncertainty['Total+'][0]
        uncertainty_total_minus = uncertainty['Total-'][0]
        uncertainty_total_plus, uncertainty_total_minus = symmetriseErrors(uncertainty_total_plus, uncertainty_total_minus)
        error_up = sqrt(fit_error ** 2 + uncertainty_total_plus ** 2) * scale
        error_down = sqrt(fit_error ** 2 + uncertainty_total_minus ** 2) * scale
        plotStatErr.SetPointEYhigh(bin_i, fit_error * scale)
        plotStatErr.SetPointEYlow(bin_i, fit_error * scale)
        plotAsym.SetPointEYhigh(bin_i, error_up)
        plotAsym.SetPointEYlow(bin_i, error_down)
        
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
    #hist_measured.Draw('same P')
    #legend.AddEntry(hist_measured, 'measured', 'P')
    
    for key, hist in sorted(histograms.iteritems()):
        if not 'unfolded' in key and not 'measured' in key:
            hist.SetLineStyle(7)
            hist.SetLineWidth(2)
            # setting colours
            if 'POWHEG' in key or 'matchingdown' in key:
                hist.SetLineColor(kBlue)
            elif 'MADGRAPH' in key or 'matchingup' in key:
                hist.SetLineColor(kRed + 1)
            elif 'MCATNLO'  in key or 'scaleup' in key:
                hist.SetLineColor(kGreen - 3)
            elif 'scaledown' in key:
                hist.SetLineColor(kMagenta + 3)
            hist.Draw('hist same')
            legend.AddEntry(hist, translate_options[key], 'l')
            
    
    legend.Draw()
    
    mytext = TPaveText(0.5, 0.97, 1, 1.01, "NDC")
    channelLabel = TPaveText(0.18, 0.97, 0.5, 1.01, "NDC")
    if 'electron' in histname:
        channelLabel.AddText("e, %s, %s, k = %s" % ("#geq 4 jets", b_tag_bins_latex[b_tag_bin], k_value))
    elif 'muon' in histname:
        channelLabel.AddText("#mu, %s, %s, k = %s" % ("#geq 4 jets", b_tag_bins_latex[b_tag_bin], k_value))
    else:
        channelLabel.AddText("combined, %s, %s, k = %s" % ("#geq 4 jets", b_tag_bins_latex[b_tag_bin], k_value))
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
    
    path = save_path + '/' + variable + '/' + category
    make_folder_if_not_exists(path)
    canvas.SaveAs(path + '/' + histname + '_kv' + str(k_value) + '.png')
    canvas.SaveAs(path + '/' + histname + '_kv' + str(k_value) + '.pdf')

def plot_central_and_systematics(channel):
    global variable, translate_options, k_value, b_tag_bin, maximum, categories
    ROOT.TH1.SetDefaultSumw2(False)
    ROOT.gROOT.SetBatch(True)
    ROOT.gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    plotting.setStyle()
    gStyle.SetTitleYOffset(1.4)
    ROOT.gROOT.ForceStyle()
    canvas = Canvas(width=700, height=500)
    canvas.SetLeftMargin(0.15)
    canvas.SetBottomMargin(0.15)
    canvas.SetTopMargin(0.05)
    canvas.SetRightMargin(0.05)
    legend = plotting.create_legend(x0=0.6, y1=0.5)
    
    hist_data_central = read_xsection_measurement_results('central', channel)[0]['unfolded']
    
    hist_data_central.GetXaxis().SetTitle(translate_options[variable] + ' [GeV]')
    hist_data_central.GetYaxis().SetTitle('#frac{1}{#sigma} #frac{d#sigma}{d' + translate_options[variable] + '} [GeV^{-1}]')
    hist_data_central.GetXaxis().SetTitleSize(0.05)
    hist_data_central.GetYaxis().SetTitleSize(0.05)
    hist_data_central.SetMinimum(0)
    hist_data_central.SetMaximum(maximum[variable])
    hist_data_central.SetMarkerSize(1)
    hist_data_central.SetMarkerStyle(20)
#    plotAsym = TGraphAsymmErrors(hist_data)
#    plotStatErr = TGraphAsymmErrors(hist_data)
    gStyle.SetEndErrorSize(20)
    hist_data_central.Draw('P')
#    plotStatErr.Draw('same P')
#    plotAsym.Draw('same P Z')
    legend.AddEntry(hist_data_central, 'measured (unfolded)', 'P')
    
    for systematic in categories:
        if systematic != 'central':
            hist_data_systematic = read_xsection_measurement_results(systematic, channel)[0]['unfolded']
            hist_data_systematic.SetMarkerSize(0.5)
            hist_data_systematic.SetMarkerStyle(20)
            colour_number = categories.index(systematic) + 1
            if colour_number == 10:
                colour_number = 42
            hist_data_systematic.SetMarkerColor(colour_number)
            hist_data_systematic.Draw('same P')
            legend.AddEntry(hist_data_systematic, systematic, 'P')
    
#    for central_generator in ['MADGRAPH', 'POWHEG', 'MCATNLO']:
#        hist_MC = read_xsection_measurement_results('central', channel)[0][central_generator]
#        hist_MC.SetLineStyle(7)
#        hist_MC.SetLineWidth(2)
#        #setting colours
#        if central_generator == 'POWHEG':
#            hist_MC.SetLineColor(kBlue)
#        elif central_generator == 'MADGRAPH':
#            hist_MC.SetLineColor(kRed + 1)
#        elif central_generator == 'MCATNLO':
#            hist_MC.SetLineColor(kMagenta + 3)
#        hist_MC.Draw('hist same')
        #legend.AddEntry(hist_MC, translate_options[central_generator], 'l')
    
    legend.Draw()
    
    mytext = TPaveText(0.5, 0.97, 1, 1.01, "NDC")
    channelLabel = TPaveText(0.18, 0.97, 0.5, 1.01, "NDC")
    if channel == 'electron':
        channelLabel.AddText("e, %s, %s, k_v = %s" % ("#geq 4 jets", b_tag_bins_latex[b_tag_bin], k_value))
    elif channel == 'muon':
        channelLabel.AddText("#mu, %s, %s, k_v = %s" % ("#geq 4 jets", b_tag_bins_latex[b_tag_bin], k_value))
    else:
        channelLabel.AddText("combined, %s, %s, k_v = %s" % ("#geq 4 jets", b_tag_bins_latex[b_tag_bin], k_value))
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
    if not channel == 'combination':
        channelLabel.Draw()
    
    canvas.Modified()
    canvas.Update()
    
    path = save_path + '/' + variable
    make_folder_if_not_exists(path)
    canvas.SaveAs(path + '/normalised_xsection_' + channel + '_altogether_kv' + str(k_value) + '.png')
    canvas.SaveAs(path + '/normalised_xsection_' + channel + '_altogether_kv' + str(k_value) + '.pdf')

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data/',
                  help="set path to JSON files")
    parser.add_option("-s", "--save_path", dest="save_path", default='plots/',
                  help="set path to save plots")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                  help="set variable to plot (MET, HT, ST, MT)")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type used in the analysis of MET, ST or MT")
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                  help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("-k", "--k_value", type='int',
                      dest="k_value", default=6,
                      help="k-value for SVD unfolding, used in histogram names")
    translate_options = {
                        '0':'0btag',
                        '1':'1btag',
                        '2':'2btags',
                        '3':'3btags',
                        '0m':'0orMoreBtag',
                        '1m':'1orMoreBtag',
                        '2m':'2orMoreBtags',
                        '3m':'3orMoreBtags',
                        '4m':'4orMoreBtags',
                        # mettype:
                        'pf':'PFMET',
                        'type1':'patType1CorrectedPFMet',
                        # histnames:
                        'unfolded': 'unfolded',
                        'measured': 'measured',
                        'MADGRAPH': 't#bar{t} (MADGRAPH)',
                        'MCATNLO': 't#bar{t} (MC@NLO)',
                        'POWHEG': 't#bar{t} (POWHEG)',
                        'matchingdown': 't#bar{t} (matching down)',
                        'matchingup': 't#bar{t} (matching up)',
                        'scaledown': 't#bar{t} (Q^{2} down)',
                        'scaleup': 't#bar{t} (Q^{2} up)',
                        'MET': 'E_{T}^{miss}',
                        'HT': 'HT',
                        'ST': 'ST',
                        'MT': 'MT'
                        }
    maximum = {
               'MET': 0.02,
               'HT': 0.005,
               'ST': 0.004,
               'MT': 0.02
               }
    
    (options, args) = parser.parse_args()
    path_to_JSON = options.path
    save_path = options.save_path
    variable = options.variable
    met_type = translate_options[options.metType]
    k_value = options.k_value
    b_tag_bin = translate_options[options.bjetbin]
    
    categories = [ 'central', 'matchingup', 'matchingdown', 'scaleup', 'scaledown', 'BJet_down', 'BJet_up', 'JES_down', 'JES_up', 'LightJet_down', 'LightJet_up', 'PU_down', 'PU_up' ]
    
    for category in categories:
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
        
        make_plots_ROOT(histograms_normalised_xsection_muon_different_generators, category, save_path, 'normalised_xsection_muon_different_generators', 'muon')
        make_plots_ROOT(histograms_normalised_xsection_muon_systematics_shifts, category, save_path, 'normalised_xsection_muon_systematics_shifts', 'muon')
        
        make_plots_ROOT(histograms_normalised_xsection_electron_different_generators, category, save_path, 'normalised_xsection_electron_different_generators', 'electron')
        make_plots_ROOT(histograms_normalised_xsection_electron_systematics_shifts, category, save_path, 'normalised_xsection_electron_systematics_shifts', 'electron')
        
    plot_central_and_systematics('electron')
    plot_central_and_systematics('muon')
    

    
