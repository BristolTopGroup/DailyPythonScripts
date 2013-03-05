from optparse import OptionParser
import tools.plotting_utilities as plotting
import sys
import numpy
from config.variable_binning_8TeV import bin_edges
from tools.file_utilities import read_data_from_JSON
from tools.hist_utilities import value_error_tuplelist_to_hist
from math import sqrt
import ROOT
from ROOT import *
from ROOT import TPaveText, kRed, TH1F, Double, TMinuit, Long, kGreen, gROOT, TCanvas, kMagenta, kBlue, TGraphAsymmErrors, TMath
from ROOT import kAzure, kYellow, kViolet, THStack, gStyle
# rootpy
from rootpy.io import File
from rootpy import asrootpy
from rootpy.plotting import Hist, HistStack, Legend, Canvas
#import rootpy.plotting.root2matplotlib as rplt
#import matplotlib.pyplot as plt
#from matplotlib.ticker import AutoMinorLocator

BjetBinsLatex = {'0btag':'0 b-tags', '0orMoreBtag':'#geq 0 b-tags', '1btag':'1 b-tags',
                    '1orMoreBtag':'#geq 1 b-tags',
                    '2btags':'2 b-tags', '2orMoreBtags':'#geq 2 b-tags',
                    '3btags':'3 b-tags', '3orMoreBtags':'#geq 3 b-tags',
                    '4orMoreBtags':'#geq 4 b-tags'}

def make_plots_ROOT(histograms, savePath, histname):
    global variable, translateOptions, analysis, k_value, b_tag_bin, maximum
    ROOT.TH1.SetDefaultSumw2(False)
    ROOT.gROOT.SetBatch(True)
    ROOT.gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    plotting.setStyle()
    gStyle.SetTitleYOffset(2)
    canvas = Canvas(width=700, height=500)
    canvas.SetLeftMargin(0.15)
    canvas.SetBottomMargin(0.15)
    canvas.SetTopMargin(0.05)
    canvas.SetRightMargin(0.05)
    legend = plotting.create_legend(x0=0.6, y1=0.5)
    
    hist_data = histograms['data'] 
    hist_data.GetXaxis().SetTitle(translateOptions[variable] + ' [GeV]')
    hist_data.GetYaxis().SetTitle('#frac{1}{#sigma} #frac{d#sigma}{d' + translateOptions[variable] + '} [GeV^{-1}]')
    hist_data.GetXaxis().SetTitleSize(0.05)
    hist_data.GetYaxis().SetTitleSize(0.05)
    hist_data.SetMinimum(0)
    hist_data.SetMaximum(maximum[variable])
    hist_data.SetMarkerSize(1)
    hist_data.SetMarkerStyle(20)
#    plotAsym = TGraphAsymmErrors(hist_data)
#    plotStatErr = TGraphAsymmErrors(hist_data)
    gStyle.SetEndErrorSize(20)
    hist_data.Draw('P')
#    plotStatErr.Draw('same P')
#    plotAsym.Draw('same P Z')
    legend.AddEntry(hist_data, 'measured (unfolded)', 'P')
    
    for key, hist in histograms.iteritems():
        if not 'data' in key:
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
            legend.AddEntry(hist, translateOptions[key], 'l')
            
    
    legend.Draw()
    
    mytext = TPaveText(0.5, 0.97, 1, 1.01, "NDC")
    channelLabel = TPaveText(0.18, 0.97, 0.5, 1.01, "NDC")
    if analysis == 'EPlusJets':
        channelLabel.AddText("e, %s, %s" % ("#geq 4 jets", BjetBinsLatex[b_tag_bin]))
    elif analysis == 'MuPlusJets':
        channelLabel.AddText("#mu, %s, %s" % ("#geq 4 jets", BjetBinsLatex[b_tag_bin]))
    elif analysis == 'Combination':
        channelLabel.AddText("combined, %s, %s" % ("#geq 4 jets", BjetBinsLatex[b_tag_bin]))
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
    if not analysis == 'Combination':
        channelLabel.Draw()
    
    canvas.Modified()
    canvas.Update()
    canvas.SaveAs(savePath + variable + '/' + histname + '_kv' + str(k_value) + '.png')
    canvas.SaveAs(savePath + variable + '/' + histname + '_kv' + str(k_value) + '.pdf')

def read_histograms_ROOT(channel):
    global path_to_JSON, variable, met_type, k_value
    normalised_xsection_unfolded = read_data_from_JSON(path_to_JSON + variable + '/xsection_measurement_results' + '/kv' + str(k_value) + '/central/' + 'normalised_xsection_' + channel + '_' + met_type + '_unfolded.txt')
    h_normalised_xsection_unfolded = value_error_tuplelist_to_hist(normalised_xsection_unfolded['TTJet'], bin_edges[variable])
    h_normalised_xsection_MADGRAPH = value_error_tuplelist_to_hist(normalised_xsection_unfolded['MADGRAPH'], bin_edges[variable])
    h_normalised_xsection_POWHEG = value_error_tuplelist_to_hist(normalised_xsection_unfolded['POWHEG'], bin_edges[variable])
    h_normalised_xsection_MCATNLO = value_error_tuplelist_to_hist(normalised_xsection_unfolded['MCATNLO'], bin_edges[variable])
    h_normalised_xsection_mathchingup = value_error_tuplelist_to_hist(normalised_xsection_unfolded['matchingup'], bin_edges[variable])
    h_normalised_xsection_mathchingdown = value_error_tuplelist_to_hist(normalised_xsection_unfolded['matchingdown'], bin_edges[variable])
    h_normalised_xsection_scaleup = value_error_tuplelist_to_hist(normalised_xsection_unfolded['scaleup'], bin_edges[variable])
    h_normalised_xsection_scaledown = value_error_tuplelist_to_hist(normalised_xsection_unfolded['scaledown'], bin_edges[variable])
    
    histograms_normalised_xsection_different_generators = {
                  'data':h_normalised_xsection_unfolded,
                  'MADGRAPH':h_normalised_xsection_MADGRAPH,
                  'POWHEG':h_normalised_xsection_POWHEG,
                  'MCATNLO':h_normalised_xsection_MCATNLO
                  }
    
    histograms_normalised_xsection_systematics_shifts = {
                  'data':h_normalised_xsection_unfolded,
                  'matchingdown': h_normalised_xsection_mathchingdown,
                  'matchingup': h_normalised_xsection_mathchingup,
                  'scaledown': h_normalised_xsection_scaledown,
                  'scaleup': h_normalised_xsection_scaleup
                  }
    
    return histograms_normalised_xsection_different_generators, histograms_normalised_xsection_systematics_shifts


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data/',
                  help="set path to JSON files")
    parser.add_option("-s", "--savePath", dest="savePath", default='plots/',
                  help="set path to save plots")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                  help="set variable to plot (MET, HT, ST, MT)")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type used in the analysis of MET, ST or MT")
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                  help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("-a", "--analysisType", dest="analysisType", default='EPlusJets',
                  help="set analysis type: EPlusJets or MuPlusJets")
    parser.add_option("-k", "--k_value", type='int',
                      dest="k_value", default=6,
                      help="k-value for SVD unfolding, used in histogram names")
    translateOptions = {
                        '0':'0btag',
                        '1':'1btag',
                        '2':'2btags',
                        '3':'3btags',
                        '0m':'0orMoreBtag',
                        '1m':'1orMoreBtag',
                        '2m':'2orMoreBtags',
                        '3m':'3orMoreBtags',
                        '4m':'4orMoreBtags',
                        #mettype:
                        'pf':'patMETsPFlow',
                        'type1':'patType1CorrectedPFMet',
                        #histnames:
                        'data': 'measured (unfolded)',
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
    savePath = options.savePath
    variable = options.variable
    met_type = translateOptions[options.metType]
    analysis = options.analysisType
    k_value = options.k_value
    b_tag_bin = translateOptions[options.bjetbin]
    
    histograms_normalised_xsection_electron_different_generators, histograms_normalised_xsection_electron_systematics_shifts = read_histograms_ROOT('electron')
    histograms_normalised_xsection_muon_different_generators, histograms_normalised_xsection_muon_systematics_shifts = read_histograms_ROOT('muon')
    
    make_plots_ROOT(histograms_normalised_xsection_muon_different_generators, savePath, 'normalised_xsection_muon_different_generators')
    make_plots_ROOT(histograms_normalised_xsection_muon_systematics_shifts, savePath, 'normalised_xsection_muon_systematics_shifts')
    
    make_plots_ROOT(histograms_normalised_xsection_electron_different_generators, savePath, 'normalised_xsection_electron_different_generators')
    make_plots_ROOT(histograms_normalised_xsection_electron_systematics_shifts, savePath, 'normalised_xsection_electron_systematics_shifts')

    