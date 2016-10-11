from __future__ import division
from ROOT import *
from ROOT import TPaveText, kRed, TH1F, Double, TMinuit, Long, kGreen, gROOT, TCanvas, kMagenta, kBlue, TGraphAsymmErrors, TMath
from ROOT import kAzure, kYellow, kViolet, THStack, gStyle
from math import sqrt
from ROOT import RooRealVar, RooDataHist, RooArgList, RooHistPdf, RooArgSet, RooAddPdf, RooMCStudy, RooFit, RooMsgService
import ROOT
import FILES
import dps.utils.ROOTFileReader as FileReader
from array import array
from dps.utils import plotting
from dps.utils import file_utilities
#import QCDRateEstimation
from copy import deepcopy
import numpy
from dps.utils.Timer import Timer
import QCDRateEstimation
from optparse import OptionParser
from dps.utils.ColorPrinter import colorstr
import json
from dps.config.sampleSummations import qcd_samples, muon_qcd_samples, singleTop_samples, wplusjets_samples, zplusjets_samples, allMC_samples, signal_samples, vplusjets_samples
from sets import Set
import sys
correctionFactors = None
acceptanceFactors = None
contaminationFactors = None
savePath = "/storage/TopQuarkGroup/results/AN-13-015_V2/DiffXSectionMeasurement/unfolding/"
outputFormat_tables = 'latex' #other option: twiki
outputFormat_plots = ['png', 'pdf']

#analysisType = 'EPlusJets'
used_data = 'SingleElectron'
data_label = {'EPlusJets':'SingleElectron', 'MuPlusJets':'SingleMu', 'Combination': 'Combination'}
#analysis_folder = 'TTbar_plus_X_analysis/EPlusJets'
rebin = 20
qcdLabel = 'QCDFromData'
metType = 'patMETsPFlow'
normalisation = None
vectors = None
N_Events = {}
N_ttbar_by_source = {}
DEBUG = False
use_RooFit = False
constrains = {
              qcdLabel: {'enabled':False, 'value': 1},
              'ratio_Z_W': {'enabled':False, 'value': 0.05},
              'W+Jets': {'enabled':False, 'value': 0.3},
              'DYJetsToLL': {'enabled':False, 'value': 0.3},
#              'Di-Boson': {'enabled':False, 'value': 0.3},
              }
fit_index = 0

scale_factors = {
                 'luminosity':1,
                 'SingleTop':1,
                 'TTJet':1,
                 'W+Jets':1,
                 'DYJetsToLL':1,
#                 'POWHEG':7483496 / 3393627,
                 'POWHEG':6920475 / 21666179,
#                 'PYTHIA6':7483496 / 1089625,
#                 'MCatNLO':7483496 / 3437894,
                 'MCatNLO':6920475 / 32739786
                 }

metbins = [
           '0-25',
           '25-45',
           '45-70',
           '70-100',
           '100-150',
           '150-inf'
            ]
metbin_widths = {
               '0-25':25,
               '25-45':20,
               '45-70':25,
               '70-100':30,
               '100-150':50,
               '150-inf':50
               }  
MET_LATEX = "E_{T}^{miss}"
metbin_latex = {
               '0-25':'0 #leq %s < 25 GeV' % MET_LATEX,
               '25-45':'25 #leq %s < 45 GeV' % MET_LATEX,
               '45-70':'45 #leq %s < 70 GeV' % MET_LATEX,
               '70-100':'70 #leq %s < 100 GeV' % MET_LATEX,
               '100-150':'100 #leq %s < 150 GeV' % MET_LATEX,
               '150-inf':'%s #geq 150 GeV' % MET_LATEX,
               }  

metbin_latex_tables = {
               '0-25':'0--25~\GeV',
               '25-45':'25--45~\GeV',
               '45-70':'45--70~\GeV',
               '70-100':'70--100~\GeV',
               '100-150':'100--150~\GeV',
               '150-inf':'$\\geq 150$~\GeV'
               }

doBinByBinUnfolding = False
    
metsystematics_sources = [
        "patType1p2CorrectedPFMetElectronEnUp",
        "patType1p2CorrectedPFMetElectronEnDown",
        "patType1p2CorrectedPFMetMuonEnUp",
        "patType1p2CorrectedPFMetMuonEnDown",
        "patType1p2CorrectedPFMetTauEnUp",
        "patType1p2CorrectedPFMetTauEnDown",
        "patType1p2CorrectedPFMetJetResUp",
        "patType1p2CorrectedPFMetJetResDown",
        "patType1p2CorrectedPFMetJetEnUp",
        "patType1p2CorrectedPFMetJetEnDown",
        "patType1p2CorrectedPFMetUnclusteredEnUp",
        "patType1p2CorrectedPFMetUnclusteredEnDown"
                      ]

metsystematics_sources_latex = {
        "patType1p2CorrectedPFMetElectronEnUp":'Electron energy $+1\sigma$',
        "patType1p2CorrectedPFMetElectronEnDown":'Electron energy $-1\sigma$',
        "patType1p2CorrectedPFMetMuonEnUp":'Muon energy $+1\sigma$',
        "patType1p2CorrectedPFMetMuonEnDown":'Muon energy $-1\sigma$',
        "patType1p2CorrectedPFMetTauEnUp":'Tau energy $+1\sigma$',
        "patType1p2CorrectedPFMetTauEnDown":'Tau energy $-1\sigma$',
        "patType1p2CorrectedPFMetJetResUp":'Jet resolution $+1\sigma$',
        "patType1p2CorrectedPFMetJetResDown":'Jet resolution $-1\sigma$',
        "patType1p2CorrectedPFMetJetEnUp":'Jet energy $+1\sigma$',
        "patType1p2CorrectedPFMetJetEnDown":'Jet energy $-1\sigma$',
        "patType1p2CorrectedPFMetUnclusteredEnUp":'Unclustered energy $+1\sigma$',
        "patType1p2CorrectedPFMetUnclusteredEnDown":'Unclustered energy $-1\sigma$'
                      }

BjetBinsLatex = {'0btag':'0 b-tags', '0orMoreBtag':'#geq 0 b-tags', '1btag':'1 b-tags',
                    '1orMoreBtag':'#geq 1 b-tags',
                    '2btags':'2 b-tags', '2orMoreBtags':'#geq 2 b-tags',
                    '3btags':'3 b-tags', '3orMoreBtags':'#geq 3 b-tags',
                    '4orMoreBtags':'#geq 4 b-tags'}

doSymmetricErrors = True
N_QCD = 14856
bjetbin = '0orMoreBtag'
metbin = metbins[0]
current_source = 'None'

def MinuitFitFunction(nParameters, gin, f, par, iflag):
    global normalisation, vectors, qcdLabel
    lnL = 0.0
    input_vectors = zip(vectors[used_data],
                vectors['Signal'],
                vectors['V+Jets'],
#                vectors['W+Jets'],
#                vectors['DYJetsToLL'],
                vectors[qcdLabel],
#                vectors['Di-Boson']
                )
    
#    for data, signal, wjets, zjets, qcd, diBoson in input:
#    for data, signal, wjets, zjets, qcd in input_vectors:
    for data, signal, vjets, qcd in input_vectors:
        #signal = ttjet + singleTop
        x_i = par[0] * signal + par[1] * vjets + par[2] * qcd# + par[4] * diBoson#expected number of events in each bin
        data = data * normalisation[used_data]
        if (data != 0) and (x_i != 0):
            L = TMath.Poisson(data, x_i)
            lnL += TMath.log(L)
    f[0] = -2.0 * lnL
    
    #constrains
#    ratio of Z/W to 5%
#    if constrains['ratio_Z_W']['enabled']:
#        ratio_Z_W = normalisation['DYJetsToLL'] / normalisation['W+Jets']
#        if ratio_Z_W == 0 or par[1] == 0:
#            f[0] += 1
#        else:
#            f[0] += ((par[2] / par[1] - ratio_Z_W) / (constrains['ratio_Z_W']['value'] * ratio_Z_W)) ** 2
#    if constrains['W+Jets']['enabled']:
#        f[0] += ((par[1] - normalisation['W+Jets']) / (constrains['W+Jets']['value'] * normalisation['W+Jets'])) ** 2
#    if constrains['DYJetsToLL']['enabled']:
#        f[0] += ((par[2] - normalisation['DYJetsToLL']) / (constrains['DYJetsToLL']['value'] * normalisation['DYJetsToLL'])) ** 2
    if constrains[qcdLabel]['enabled']:
        f[0] += ((par[2] - N_QCD) / (constrains[qcdLabel]['value'] * N_QCD)) ** 2
#    if constrains['Di-Boson']['enabled']:
#        f[0] += ((par[4] - normalisation['Di-Boson']) / (constrains['Di-Boson']['value'] * normalisation['Di-Boson'])) ** 2
        
def createFitHistogram(fitvalues, fiterrors, templates):
    global fit_index
    fit = TH1F('fit_' + str(fit_index), 'fit', len(templates['Signal']), 0, 3)
    fit_index += 1
    bin_i = 1
    input_vectors = zip(vectors['Signal'],
                        vectors['V+Jets'],
                vectors[qcdLabel],
                )
    for signal, vjets, qcd in input_vectors:
        value = fitvalues[0] * signal + fitvalues[1] * vjets + fitvalues[2] * qcd #+ fitvalues[4] * diBoson
        error = sqrt((fiterrors[0] * signal) ** 2 + (fiterrors[1] * vjets) ** 2 + (fiterrors[2] * qcd) ** 2)
        fit.SetBinContent(bin_i, value)
        fit.SetBinError(bin_i, error)
        bin_i += 1
    return fit.Clone()

def getFittedNormalisation(vectors_={}, normalisation_={}):
    global normalisation, vectors, bjetbin
    normalisation = normalisation_
    vectors = vectors_
        
    #setup minuit
    numberOfParameters = 3#4#5
    gMinuit = TMinuit(numberOfParameters)
    gMinuit.SetFCN(MinuitFitFunction)
    gMinuit.SetPrintLevel(-1)
    #Error definition: 1 for chi-squared, 0.5 for negative log likelihood
    gMinuit.SetErrorDef(1)
    #error flag for functions passed as reference.set to as 0 is no error
    errorFlag = Long(2)
    
    N_total = normalisation[used_data] * 2
    N_min = 0
#    N_total = 1e6
#    N_min = -N_total
    
    N_QCD = normalisation[qcdLabel]
#    N_QCD = normalisation['QCD']
    if DEBUG:
        print len(vectors[used_data]), len(vectors['Signal']), len(vectors['W+Jets']), len(vectors['DYJetsToLL']), len(vectors['QCDFromData'])
        print "Total number of data events before the fit: ", N_total
    N_signal = normalisation['TTJet'] + normalisation['SingleTop']
    gMinuit.mnparm(0, "N_signal(ttbar+single_top)", N_signal, 10.0, N_min, N_total, errorFlag)
    gMinuit.mnparm(1, "V+Jets", normalisation['V+Jets'], 10.0, N_min, N_total, errorFlag)
#    gMinuit.mnparm(1, "W+Jets", normalisation['W+Jets'], 10.0, N_min, N_total, errorFlag)
#    gMinuit.mnparm(2, "DYJetsToLL", normalisation['DYJetsToLL'], 10.0, N_min, N_total, errorFlag)
    gMinuit.mnparm(2, "QCD", N_QCD, 10.0, N_min, N_total, errorFlag)
#    gMinuit.mnparm(4, "Di-Boson", normalisation['Di-Boson'], 10.0, 0, N_total, errorFlag)
    
    arglist = array('d', 10 * [0.])
    #minimisation strategy: 1 standard, 2 try to improve minimum (a bit slower)
    arglist[0] = 2
    #minimisation itself
    gMinuit.mnexcm("SET STR", arglist, 1, errorFlag)
    gMinuit.Migrad()
    
    fitvalues, fiterrors = [], []
    for index in range(numberOfParameters):
        temp_par = Double(0)
        temp_err = Double(0)
        gMinuit.GetParameter(index, temp_par, temp_err)
        fitvalues.append(temp_par)
        fiterrors.append(temp_err)
    
    N_ttbar = fitvalues[0] - normalisation['SingleTop'] 
    N_ttbar_err = (fitvalues[0] - normalisation['SingleTop']) * fiterrors[0] / fitvalues[0]
    if (normalisation['V+Jets'] != 0):
        N_ZPlusJets = fitvalues[1] - (fitvalues[1] * normalisation['W+Jets'] / normalisation['V+Jets'])
    else:
        N_ZPlusJets = fitvalues[1]
    #the error appears twice in the above calculation -> E(N_Z) = E(N_V)*sqrt(2)
    N_ZPlusJets_err = fiterrors[0] / fitvalues[1] * N_ZPlusJets
    if (normalisation['V+Jets'] != 0):
        N_WPlusJets = fitvalues[1] - (fitvalues[1] * normalisation['DYJetsToLL'] / normalisation['V+Jets'])
    else:
        N_WPlusJets = fitvalues[1]
    N_WPlusJets_err = fiterrors[0] / fitvalues[1] * N_WPlusJets
    
    N_SingleTop = fitvalues[0] - (fitvalues[0] * normalisation['TTJet'] / normalisation['Signal'])
    N_SingleTop_err = fiterrors[0] / fitvalues[0] * N_SingleTop * sqrt(2)
    result = {'Signal': {'value': fitvalues[0], 'error':fiterrors[0]},
              'Signal Before Fit': {'value': N_signal, 'error':0},
              'V+Jets': {'value': fitvalues[1], 'error':fiterrors[0]},
              'W+Jets': {'value': N_WPlusJets, 'error':N_WPlusJets_err},
              'DYJetsToLL': {'value': N_ZPlusJets, 'error':N_ZPlusJets_err},
              qcdLabel: {'value': fitvalues[2], 'error':fiterrors[2]},
#              'Di-Boson': {'value': fitvalues[4], 'error':fiterrors[4]},
              'TTJet': {'value': N_ttbar, 'error' : N_ttbar_err},
              used_data: {'value': normalisation[used_data], 'error':0},
              'SingleTop': {'value': N_SingleTop, 'error':N_SingleTop_err},
              'SingleTop Before Fit': {'value': normalisation['SingleTop'], 'error':0},
              'TTJet Before Fit': {'value': normalisation['TTJet'], 'error':0},
              'QCD Before Fit': {'value': normalisation[qcdLabel], 'error':0},
              'V+Jets BeforeFit': {'value': normalisation['V+Jets'], 'error':0},
              'W+Jets BeforeFit': {'value': normalisation['W+Jets'], 'error':0},
              'DYJetsToLL Before Fit': {'value': normalisation['DYJetsToLL'], 'error':0},
              'SumMC': {'value': sum(fitvalues), 'error':sqrt(fiterrors[0] ** 2 + fiterrors[1] ** 2 + fiterrors[2] ** 2)},
              'SumMC Before Fit': {'value': normalisation['V+Jets'] + normalisation[qcdLabel] + N_signal, 'error':0},
              'fit': createFitHistogram(fitvalues, fiterrors, vectors),
              'vectors':vectors}
    if current_source == 'central':
        result.update({
              #other generators
              'POWHEG': {'value': normalisation['POWHEG'] * scale_factors['POWHEG'], 'error':0},
#              'PYTHIA6': {'value': normalisation['PYTHIA6'] * scale_factors['PYTHIA6'], 'error':0},
              'MCatNLO': {'value': normalisation['MCatNLO'] * scale_factors['MCatNLO'], 'error':0},
              })
    return result

def normaliseHistograms(histograms, normalisation):
    for histogramName, histogram in histograms.iteritems():
        histogram = plotting.normalise(histogram)
        histogram.Scale(normalisation[histogramName])
    return histograms

def getPDFs(histograms):
    h_data = histograms[used_data]
    temp_tt = histograms['TTJet']
    temp_wj = histograms['W+Jets']
#    temp_wj.Add(histograms['W2Jets'])
#    temp_wj.Add(histograms['W3Jets'])
#    temp_wj.Add(histograms['W4Jets'])
    temp_zj = histograms['DYJetsToLL']
    temp_qcd = histograms[qcdLabel]
    temp_stop = histograms['SingleTop']
    temp_signal = temp_tt.Clone('Signal')
    temp_signal.Add(temp_stop)
    temp_VPlusJets = temp_zj.Clone('V+jets')
    temp_VPlusJets.Add(temp_wj)
    
    leptonAbsEta = RooRealVar("leptonAbsEta", "leptonAbsEta", 0., 3.)
    variables = RooArgList()
    variables.add(leptonAbsEta)
    vars_set = RooArgSet()
    vars_set.add(leptonAbsEta)

    data = RooDataHist("data", "dataset with leptonAbsEta", variables, h_data)
    rh_tt = RooDataHist("rh_tt", "tt", variables, temp_tt);
    rh_wj = RooDataHist("rh_wj", "wj", variables, temp_wj);
    rh_zj = RooDataHist("rh_zj", "zj", variables, temp_zj);
    rh_VJ = RooDataHist("rh_VJ", "VJ", variables, temp_VPlusJets);
    rh_qcd = RooDataHist("rh_qcd", "qcd", variables, temp_qcd);
    rh_stop = RooDataHist("rh_stop", "singletop", variables, temp_stop);
    rh_signal = RooDataHist("rh_signal", "signal", variables, temp_signal);
    roodatahists = [data, rh_VJ, rh_qcd, rh_signal]
    
    pdfs = {}
    pdfs[used_data] = data
    pdfs['TTJet'] = RooHistPdf("pdf_tt", "Signal pdf", vars_set, rh_tt, 0);
    pdfs['W+Jets'] = RooHistPdf ("pdf_wj", "W+jets pdf", vars_set, rh_wj, 0);
    pdfs['DYJetsToLL'] = RooHistPdf ("pdf_zj", "Z+jets pdf", vars_set, rh_zj, 0);
    pdfs['V+Jets'] = RooHistPdf ("pdf_VJ", "Z+jets pdf", vars_set, rh_VJ, 0);
    pdfs['QCD'] = RooHistPdf("pdf_qcd", "QCD pdf ", vars_set, rh_qcd, 0);
    pdfs['SingleTop'] = RooHistPdf("pdf_stop", "single top pdf", vars_set, rh_stop, 0);
    pdfs['Signal'] = RooHistPdf("pdf_signal", "single top pdf", vars_set, rh_signal, 0);
    return pdfs, leptonAbsEta, variables, vars_set, roodatahists


def getFittedNormalisation_RooFit(histograms, normalisation_={}, vectors_={}):
    global used_data, normalisation, vectors
    normalisation = normalisation_
    vectors = vectors_
    histograms = normaliseHistograms(histograms, normalisation)
    histograms['V+Jets'] = histograms['W+Jets'].Clone('VPlusJets')
    histograms['V+Jets'].Add(histograms['DYJetsToLL'])
    normalisation['V+Jets'] = normalisation['W+Jets'] + normalisation['DYJetsToLL']
    normalisation['Signal'] = normalisation['TTJet'] + normalisation['SingleTop']
    pdfs, leptonAbsEta, variables, vars_set, roodatahists = getPDFs(histograms)
    N_total = normalisation[used_data]
    N_total = 2 * N_total
    N_min = 0
    #variables to be fitted
    N_VPlusJets = RooRealVar  ("nVJ", "number of Z+jets bgnd events", normalisation['V+Jets'], N_min, N_total, "event");
    N_QCD = RooRealVar("nqcd", "number of QCD bgnd events", normalisation[qcdLabel], N_min, normalisation[qcdLabel] * 2, "event");
    N_Signal = RooRealVar("nSignal", "number of single top + ttbar events", normalisation['Signal'], N_min, N_total, "event");

    model = RooAddPdf("model", "Signal + V+Jets + QCD",
            RooArgList(pdfs['Signal'], pdfs['V+Jets'], pdfs['QCD']),
            RooArgList(N_Signal, N_VPlusJets, N_QCD)) 
    fitResult = model.fitTo(pdfs[used_data], RooFit.Minimizer("Minuit2", "Migrad"), RooFit.NumCPU(2), RooFit.Extended(True),
                        RooFit.SumW2Error(False), RooFit.Strategy(2),
                        #verbosity
                        RooFit.PrintLevel(-1), RooFit.Warnings(DEBUG), RooFit.Verbose(DEBUG))            
#    if DEBUG:
#        print len(vectors[used_data]), len(vectors['Signal']), len(vectors['W+Jets']), len(vectors['DYJetsToLL']), len(vectors['QCDFromData'])
#        print "Total number of data events before the fit: ", N_total
    
    
    N_ttbar = N_Signal.getVal() - normalisation['SingleTop'] 
    N_ttbar_err = (N_Signal.getVal() - normalisation['SingleTop']) * N_Signal.getError() / N_Signal.getVal()
    N_ZPlusJets = N_VPlusJets.getVal() - (N_VPlusJets.getVal() * normalisation['W+Jets'] / normalisation['V+Jets'])
    N_ZPlusJets_err = N_VPlusJets.getError() / N_VPlusJets.getVal() * N_ZPlusJets
    N_WPlusJets = N_VPlusJets.getVal() - (N_VPlusJets.getVal() * normalisation['DYJetsToLL'] / normalisation['V+Jets'])
    N_WPlusJets_err = N_VPlusJets.getError() / N_VPlusJets.getVal() * N_WPlusJets
    
    N_SingleTop = N_Signal.getVal() - (N_Signal.getVal() * normalisation['TTJet'] / normalisation['Signal'])
    N_SingleTop_err = N_Signal.getError() / N_Signal.getVal() * N_SingleTop * sqrt(2)
    result = {'Signal': {'value': N_Signal.getVal(), 'error':N_Signal.getError()},
              'Signal Before Fit': {'value': normalisation['Signal'], 'error':0},
              'V+Jets': {'value': N_VPlusJets.getVal(), 'error':N_VPlusJets.getError()},
              'W+Jets': {'value': N_WPlusJets, 'error':N_WPlusJets_err},
              'DYJetsToLL': {'value': N_ZPlusJets, 'error':N_ZPlusJets_err},
              qcdLabel: {'value': N_QCD.getVal(), 'error':N_QCD.getError()},
#              'Di-Boson': {'value': fitvalues[4], 'error':fiterrors[4]},
              'TTJet': {'value': N_ttbar, 'error' : N_ttbar_err},
              used_data: {'value': normalisation[used_data], 'error':0},
              'SingleTop': {'value': N_SingleTop, 'error':N_SingleTop_err},
              'SingleTop Before Fit': {'value': normalisation['SingleTop'], 'error':0},
              'TTJet Before Fit': {'value': normalisation['TTJet'], 'error':0},
              'QCD Before Fit': {'value': normalisation[qcdLabel], 'error':0},
              'V+Jets BeforeFit': {'value': normalisation['V+Jets'], 'error':0},
              'W+Jets BeforeFit': {'value': normalisation['W+Jets'], 'error':0},
              'DYJetsToLL Before Fit': {'value': normalisation['DYJetsToLL'], 'error':0},
              'SumMC': {'value': N_Signal.getVal() + N_VPlusJets.getVal() + N_QCD.getVal() , 'error':sqrt(N_Signal.getError() ** 2 + N_VPlusJets.getError() ** 2 + N_QCD.getError() ** 2)},
              'SumMC Before Fit': {'value': normalisation['V+Jets'] + normalisation[qcdLabel] + normalisation['Signal'], 'error':0},
              'fit': createFitHistogram_RooFit(histograms, normalisation, N_Signal, N_VPlusJets, N_QCD),
              'vectors':vectors}
    if current_source == 'central':
        result.update({
              #other generators
              'POWHEG': {'value': normalisation['POWHEG'] * scale_factors['POWHEG'], 'error':0},
#              'PYTHIA6': {'value': normalisation['PYTHIA6'] * scale_factors['PYTHIA6'], 'error':0},
              'MCatNLO': {'value': normalisation['MCatNLO'] * scale_factors['MCatNLO'], 'error':0},
              })
    return result

def createFitHistogram_RooFit(histograms, normalisation, N_Signal, N_VPlusJets, N_QCD):
    global fit_index
    nBins = histograms[used_data].GetNbinsX()
    hists = normaliseHistograms({'Signal':histograms['Signal'], 'V+Jets':histograms['V+Jets'], qcdLabel:histograms[qcdLabel]},
                                {'Signal':N_Signal.getVal(), 'V+Jets':N_VPlusJets.getVal(), qcdLabel:N_QCD.getVal()})
    h_signal = hists['Signal']
    h_VPlusJets = hists['V+Jets']
    h_QCD = hists[qcdLabel]
    
    fit = TH1F('fit_' + str(fit_index), 'fit', nBins, 0, 3)
    fit_index += 1
    
    for bin_i in range(1, nBins):
        nSignal = h_signal.GetBinContent(bin_i)
        nVPlusJets = h_VPlusJets.GetBinContent(bin_i)
        nQCD = h_QCD.GetBinContent(bin_i)
        value = nSignal + nVPlusJets + nQCD
        #bin-by-bin error
        relErrorSignal = getRelativeError(N_Signal.getVal(), N_Signal.getError()) 
        relErrorVPlusJets = getRelativeError(N_VPlusJets.getVal(), N_VPlusJets.getError())
        relErrorQCD = getRelativeError(N_QCD.getVal(), N_QCD.getError())
        error = sqrt((relErrorSignal * nSignal) ** 2 + (relErrorVPlusJets * nVPlusJets) ** 2 + (relErrorQCD * nQCD) ** 2)
        fit.SetBinContent(bin_i, value)
        fit.SetBinError(bin_i, error)
    return fit.Clone()

def measureNormalisationIn(histogram, analysis):
    global bjetbin, used_data
    used_data = data_label[analysis]
    normalisation = getNormalisation(histogram)
    if DEBUG:
        print current_source, ':', normalisation['W+Jets']
    templates = getTemplates(histogram)
    vectors = vectorise(templates)
    if analysis == 'EPlusJets':
        qcdHistForEstimation = 'TTbar_plus_X_analysis/' + analysis + '/QCD e+jets PFRelIso/Binned_MET_Analysis/patType1CorrectedPFMet_bin_%s/electron_pfIsolation_03_%s'
        qcdHistForEstimation = qcdHistForEstimation % (metbin, bjetbin)
        qcdResult = QCDRateEstimation.estimateQCDWithRelIso(FILES.files, qcdHistForEstimation)
        normalisation[qcdLabel] = qcdResult['estimate']
    else:
        normalisation[qcdLabel] = normalisation['QCD_Pt-15to20_MuEnrichedPt5'] * 1.21
#        print 'MuQCD normalisation:', normalisation[qcdLabel]
#        normalisation[qcdLabel] = normalisation[qcdLabel]*1.21
    
    if DEBUG:
        printNormalisation(normalisation)
    fitted_result = None
    if use_RooFit:
        fitted_result = getFittedNormalisation_RooFit(histogram, normalisation, vectors)
    else:
        fitted_result = getFittedNormalisation(vectors, normalisation)
    if DEBUG:
        printFittedResult(fitted_result)
    return fitted_result

def measureNormalisationIncludingSystematics(histograms, analysis):
    global current_source, used_data
    fitted_results = {}
    print 'Performing central measurement'
    timer = Timer()
    current_source = 'central'
    histogram = histograms['central']
    use_QCDFromData = 'QCDFromData_Conversions'
    if analysis == 'MuPlusJets':
        use_QCDFromData = 'QCDFromData_AntiIsolated'
    histogram['QCDFromData'] = histogram[use_QCDFromData]
    fitted_results['central'] = measureNormalisationIn(histogram, analysis)
    print '>' * 80, 'completed in %.2fs' % timer.elapsedTime()
    timer.restart()
    print 'Performing measurement of systematic uncertainties (lumi, electron efficiency, single top cross-section)'
    
    if analysis == 'EPlusJets':
        #electron efficiency += 3%
        current_source = 'Electron Efficiency'
        scale_factors['luminosity'] = 1. + 0.03
        fitted_results['Electron Efficiency +'] = measureNormalisationIn(histogram, analysis)
        scale_factors['luminosity'] = 1. - 0.03
        fitted_results['Electron Efficiency -'] = measureNormalisationIn(histogram, analysis)
    else:
        #Muon efficiency += 3% TODO: change number
        current_source = 'Muon Efficiency'
        scale_factors['luminosity'] = 1. + 0.03
        fitted_results['Muon Efficiency +'] = measureNormalisationIn(histogram, analysis)
        scale_factors['luminosity'] = 1. - 0.03
        fitted_results['Muon Efficiency -'] = measureNormalisationIn(histogram, analysis)
    #luminosity uncertainty +- 2.2%
    current_source = 'luminosity'
    scale_factors['luminosity'] = 1. + 0.022
    fitted_results['Luminosity +'] = measureNormalisationIn(histogram, analysis)
    scale_factors['luminosity'] = 1. - 0.022
    fitted_results['Luminosity -'] = measureNormalisationIn(histogram, analysis)
    scale_factors['luminosity'] = 1.#reset
    #single top cross-section: +-30%
    current_source = 'singleTop'
    scale_factors['SingleTop'] = 1. + 0.3
    fitted_results['SingleTop +'] = measureNormalisationIn(histogram, analysis)
    scale_factors['SingleTop'] = 1. - 0.3
    fitted_results['SingleTop -'] = measureNormalisationIn(histogram, analysis)
    scale_factors['SingleTop'] = 1.#reset
    print '>' * 80, 'completed in %.2fs' % timer.elapsedTime()
    timer.restart()
    print 'Performing measurement of QCD shape uncertainty, JES and PU uncertainties'
    if analysis == 'EPlusJets':
        #QCD shape
        current_source = 'QCD shape'
        histogram['QCDFromData'] = histogram['QCDFromData_AntiIsolated']
        fitted_results['QCD shape'] = measureNormalisationIn(histogram, analysis)
        timer.restart()
        print '>' * 80, 'completed in %.2fs' % timer.elapsedTime()
    #jet energy scale
    current_source = 'JES'
    histogram = histograms['JES+']
    histogram['QCDFromData'] = histogram[use_QCDFromData]
    fitted_results['JES+'] = measureNormalisationIn(histogram, analysis)
    histogram = histograms['JES-']
    histogram['QCDFromData'] = histogram[use_QCDFromData]
    fitted_results['JES-'] = measureNormalisationIn(histogram, analysis)
    #inelastic cross-section for pile-up calculation +- 5%
    current_source = 'PileUp'
    histogram = histograms['PileUp+']
    histogram['QCDFromData'] = histogram[use_QCDFromData]
    fitted_results['PileUp+'] = measureNormalisationIn(histogram, analysis)
    histogram = histograms['PileUp-']
    histogram['QCDFromData'] = histogram[use_QCDFromData]
    fitted_results['PileUp-'] = measureNormalisationIn(histogram, analysis)
    print '>' * 60, 'completed in %.2fs' % timer.elapsedTime()
    timer.restart()
    
    print 'Performing measurement of B-tag and light jet uncertainties'
    current_source = 'BJets'
    histogram = histograms['BJet+']
    histogram['QCDFromData'] = histogram[use_QCDFromData]
    fitted_results['BJet+'] = measureNormalisationIn(histogram, analysis)
    histogram = histograms['BJet-']
    histogram['QCDFromData'] = histogram[use_QCDFromData]
    fitted_results['BJet-'] = measureNormalisationIn(histogram, analysis)
    current_source = 'LightJets'
    histogram = histograms['LightJet+']
    histogram['QCDFromData'] = histogram[use_QCDFromData]
    fitted_results['LightJet+'] = measureNormalisationIn(histogram, analysis)
    histogram = histograms['LightJet-']
    histogram['QCDFromData'] = histogram[use_QCDFromData]
    fitted_results['LightJet-'] = measureNormalisationIn(histogram, analysis)
    print '>' * 60, 'completed in %.2fs' % timer.elapsedTime()
    timer.restart()
    
    print 'Performing measurement of matching and scale systematic uncertainties'
    #matching threshold ttbar: 20 GeV -> 10 GeV & 40GeV
    current_source = 'TTJet matching'
    histogram = histograms['central']
    histogram['QCDFromData'] = histogram[use_QCDFromData]
    ttjet_temp = deepcopy(histogram['TTJet'])
    histogram['TTJet'] = histogram['TTJets-matchingup']
    scale_factors['TTJet'] = N_Events[analysis]['TTJet'] / N_Events[analysis]['TTJets-matchingup']
    fitted_results['TTJet matching +'] = measureNormalisationIn(histogram, analysis)
    histogram['TTJet'] = histogram['TTJets-matchingdown']
    scale_factors['TTJet'] = N_Events[analysis]['TTJet'] / N_Events[analysis]['TTJets-matchingdown']
    fitted_results['TTJet matching -'] = measureNormalisationIn(histogram, analysis)
    #Q^2 scale ttbar
    current_source = 'TTJet scale'
    histogram['TTJet'] = histogram['TTJets-scaleup']
    scale_factors['TTJet'] = N_Events[analysis]['TTJet'] / N_Events[analysis]['TTJets-scaleup']
    fitted_results['TTJet scale +'] = measureNormalisationIn(histogram, analysis)
    histogram['TTJet'] = histogram['TTJets-scaledown']
    scale_factors['TTJet'] = N_Events[analysis]['TTJet'] / N_Events[analysis]['TTJets-scaledown']
    fitted_results['TTJet scale -'] = measureNormalisationIn(histogram, analysis)
    #reset
    scale_factors['TTJet'] = 1
    histogram['TTJet'] = ttjet_temp
    #matching threshold W+Jets
    current_source = 'V+Jets matching'
    zjets_temp = deepcopy(histogram['DYJetsToLL'])
    wjets_temp = deepcopy(histogram['W+Jets'])
    vjets_temp = deepcopy(histogram['V+Jets'])
    
    histogram['W+Jets'] = histogram['WJets-matchingup']
    histogram['DYJetsToLL'] = histogram['ZJets-matchingup']
    histogram['V+Jets'] = histogram['W+Jets']
    histogram['V+Jets'].Add(histogram['DYJetsToLL'])
    scale_factors['W+Jets'] = N_Events[analysis]['W+Jets'] / N_Events[analysis]['WJets-matchingup']
    scale_factors['DYJetsToLL'] = N_Events[analysis]['DYJetsToLL'] / N_Events[analysis]['ZJets-matchingup']
    fitted_results['V+Jets matching +'] = measureNormalisationIn(histogram, analysis)
    
    histogram['W+Jets'] = histogram['WJets-matchingdown']
    histogram['DYJetsToLL'] = histogram['ZJets-matchingdown']
    histogram['V+Jets'] = histogram['W+Jets']
    histogram['V+Jets'].Add(histogram['DYJetsToLL'])
    scale_factors['W+Jets'] = N_Events[analysis]['W+Jets'] / N_Events[analysis]['WJets-matchingdown']
    scale_factors['DYJetsToLL'] = N_Events[analysis]['DYJetsToLL'] / N_Events[analysis]['ZJets-matchingdown']
    fitted_results['V+Jets matching -'] = measureNormalisationIn(histogram, analysis)
    #Q^2 scale W+Jets
    current_source = 'V+Jets scale'
    histogram['W+Jets'] = histogram['WJets-scaleup']
    histogram['DYJetsToLL'] = histogram['ZJets-scaleup']
    histogram['V+Jets'] = histogram['W+Jets']
    histogram['V+Jets'].Add(histogram['DYJetsToLL'])
    scale_factors['W+Jets'] = N_Events[analysis]['W+Jets'] / N_Events[analysis]['WJets-scaleup']
    scale_factors['DYJetsToLL'] = N_Events[analysis]['DYJetsToLL'] / N_Events[analysis]['ZJets-scaleup']
    fitted_results['V+Jets scale +'] = measureNormalisationIn(histogram, analysis)

    histogram['W+Jets'] = histogram['WJets-scaledown']
    histogram['DYJetsToLL'] = histogram['ZJets-scaledown']
    histogram['V+Jets'] = histogram['W+Jets']
    histogram['V+Jets'].Add(histogram['DYJetsToLL'])
    scale_factors['W+Jets'] = N_Events[analysis]['W+Jets'] / N_Events[analysis]['WJets-scaledown']
    scale_factors['DYJetsToLL'] = N_Events[analysis]['DYJetsToLL'] / N_Events[analysis]['ZJets-scaledown']
    fitted_results['V+Jets scale -'] = measureNormalisationIn(histogram, analysis)
    #reset
    scale_factors['W+Jets'] = 1
    scale_factors['DYJetsToLL'] = 1
    histogram['W+Jets'] = wjets_temp
    histogram['DYJetsToLL'] = zjets_temp
    histogram['V+Jets'] = vjets_temp
    print '>' * 60, 'completed in %.2fs' % timer.elapsedTime()
    timer.restart()
    print 'Performing measurement of MET systematic uncertainties'
    for source in metsystematics_sources:
        current_source = source
        histogram = histograms[source]
        histogram['QCDFromData'] = histogram[use_QCDFromData]
        if 'JetRes' in source:
            histogram['QCDFromData'] = histograms['central'][use_QCDFromData]
            histogram[used_data] = histograms['central'][used_data]
        fitted_results[source] = measureNormalisationIn(histogram, analysis)
    print '>' * 60, 'completed in %.2fs' % timer.elapsedTime()
    timer.restart()
        
    print 'Performing measurement of PDF uncertainties'
    histogram_pdf = histograms['PDFWeights']
    histogram = histograms['central']
    histogram['QCDFromData'] = histograms['central'][use_QCDFromData]
    ttjet_temp = deepcopy(histogram['TTJet'])
    #scale_factors['TTJet'] = 7490162 / 6093274
    for index in range(1, 45):
        pdf = 'TTJet_%d' % index
        current_source = pdf
        histogram['TTJet'] = histogram_pdf[pdf]
        fitted_results['PDFWeights_%d' % index] = measureNormalisationIn(histogram, analysis)
    #reset
    scale_factors['TTJet'] = 1.   
    histogram['TTJet'] = ttjet_temp
    print '>' * 60, 'completed in %.2fs' % timer.elapsedTime()
    return fitted_results
    histogram = None


def combineResults(result_A, result_B):
    combination = {}
    measurements = result_A.keys()
    measurements.extend(result_B.keys())
    measurements = Set(measurements)
    for measurement in measurements:
        value_A = None
        value_B = None
        #get the measurement if it exists
        #if it doesn't use central result
        if result_A.has_key(measurement):
            value_A = result_A[measurement]
        else:
            value_A = result_A['central']
            
        if result_B.has_key(measurement):
            value_B = result_B[measurement]
        else:
            value_B = result_B['central']
        result = combineValues(value_A, value_B)
        combination[measurement] = result
        #entries of each result are showin in 
        #getFittedNormalisation
    return combination
        

def combineValues(value_A, value_B):  
    global qcdLabel
    measurements = value_A.keys()
    measurements.extend(value_A.keys())
    measurements = Set(measurements)
    
    result = {}
    for measurement in measurements:
        combination_function = combineMeasurements
        if measurement == 'fit':
            combination_function = combineFits
        elif measurement == 'vectors':
            combination_function = combineVectors
        if measurement in value_A.keys() and measurement in value_B.keys():
            result[measurement] = combination_function(value_A[measurement], value_B[measurement])
        elif measurement in value_A.keys() and not measurement in value_B.keys():
            result[measurement] = value_A[measurement]
        else:
            result[measurement] = value_B[measurement]
                                              
#    result = {'Signal': combineMeasurements(value_A['Signal'], value_B['Signal']),
#              'Signal Before Fit': combineMeasurements(value_A['Signal Before Fit'], value_B['Signal Before Fit']),
#              'V+Jets': combineMeasurements(value_A['V+Jets'], value_B['V+Jets']),
#              'W+Jets': combineMeasurements(value_A['W+Jets'], value_B['W+Jets']),
#              'DYJetsToLL': combineMeasurements(value_A['DYJetsToLL'], value_B['DYJetsToLL']),
#              qcdLabel: combineMeasurements(value_A[qcdLabel], value_B[qcdLabel]),
#              'TTJet': combineMeasurements(value_A['TTJet'], value_B['TTJet']),
#              #TODO
#              'Combination': combineMeasurements(value_A['Signal'], value_B['Signal']),
#              'SingleTop':combineMeasurements(value_A['SingleTop'], value_B['SingleTop']),
#              'SingleTop Before Fit': combineMeasurements(value_A['SingleTop Before Fit'], value_B['SingleTop Before Fit']),
#              'TTJet Before Fit': combineMeasurements(value_A['TTJet Before Fit'], value_B['TTJet Before Fit']),
#              'QCD Before Fit': combineMeasurements(value_A['QCD Before Fit'], value_B['QCD Before Fit']),
#              'V+Jets BeforeFit': combineMeasurements(value_A['V+Jets BeforeFit'], value_B['V+Jets BeforeFit']),
#              'W+Jets BeforeFit': combineMeasurements(value_A['W+Jets BeforeFit'], value_B['W+Jets BeforeFit']),
#              'DYJetsToLL Before Fit': combineMeasurements(value_A['DYJetsToLL Before Fit'], value_B['DYJetsToLL Before Fit']),
#              'SumMC': combineMeasurements(value_A['SumMC'], value_B['SumMC']),
#              'SumMC Before Fit': combineMeasurements(value_A['SumMC Before Fit'], value_B['SumMC Before Fit']),
#              'fit': combineFits(value_A['fit'], value_B['fit']),
#              'vectors':combineVectors(value_A['vectors'], value_B['vectors'])}  
    return result
    
def combineMeasurements(measurement_A, measurement_B):
    value_A = measurement_A['value']
    value_B = measurement_B['value']
    error_A = measurement_A['error']
    error_B = measurement_B['error']
    combined_value = value_A + value_B
#    relError_A = 0
#    if not value_A == 0:
#        relError_A = error_A/value_A
#    relError_B = 0
#    if not value_B == 0:
#        relError_B = error_B/value_B
#    combined_error = sqrt(relError_A**2 + relError_B**2)*combined_value
    combined_error = sqrt(error_A ** 2 + error_B ** 2)
    return {'value': combined_value, 'error':combined_error}
    
def combineFits(measurement_A, measurement_B):
    combined_fit = measurement_A.Clone('combined_fit' + str(fit_index))
    combined_fit.Add(measurement_B)
    return combined_fit
        
def combineVectors(measurement_A, measurement_B):
    combined_vector = {}
    for sample in measurement_A.keys():
        sum_entries = 0
        combined_vector[sample] = []
        for entry_A, entry_B in zip(measurement_A[sample], measurement_B[sample]):
            sum_entries += entry_A
            sum_entries += entry_B
            combined_vector[sample].append(entry_A + entry_B)
    #normalise to 1 (template)
        for entry in combined_vector[sample]:
            if not sum_entries == 0:
                entry = entry / sum_entries
    return combined_vector

def NormalisationAnalysis():
    global metbins, metsystematics_sources, N_Events, metbin, doBinByBinUnfolding, metType, used_data
    analysisTimer = Timer()
    
    setNEvents(bjetbin, 'EPlusJets')
    setNTtbar(bjetbin, 'EPlusJets')
    setNEvents(bjetbin, 'MuPlusJets')
    setNTtbar(bjetbin, 'MuPlusJets')
    
    result_electrons = {}
    result_muons = {}
    result_combined = {}
    result_simultaniousFit = {}
    for metbin in metbins:
        metbinTimer = Timer()
        #loadfiles
        histogramCollection = getHistograms(bjetbin, metbin, 'EPlusJets')
        histogramCollection_muons = getHistograms(bjetbin, metbin, 'MuPlusJets')
        
        #sum samples
        histogramCollection['central'] = sumSamples(histogramCollection['central'])
        histogramCollection['JES-'] = sumSamples(histogramCollection['JES-'])
        histogramCollection['JES+'] = sumSamples(histogramCollection['JES+'])
        histogramCollection['PileUp-'] = sumSamples(histogramCollection['PileUp-'])
        histogramCollection['PileUp+'] = sumSamples(histogramCollection['PileUp+'])
        histogramCollection['BJet-'] = sumSamples(histogramCollection['BJet-'])
        histogramCollection['BJet+'] = sumSamples(histogramCollection['BJet+'])
        histogramCollection['LightJet-'] = sumSamples(histogramCollection['LightJet-'])
        histogramCollection['LightJet+'] = sumSamples(histogramCollection['LightJet+'])
        histogramCollection_muons['central'] = sumSamples(histogramCollection_muons['central'])
        histogramCollection_muons['JES-'] = sumSamples(histogramCollection_muons['JES-'])
        histogramCollection_muons['JES+'] = sumSamples(histogramCollection_muons['JES+'])
        histogramCollection_muons['PileUp-'] = sumSamples(histogramCollection_muons['PileUp-'])
        histogramCollection_muons['PileUp+'] = sumSamples(histogramCollection_muons['PileUp+'])
        histogramCollection_muons['BJet-'] = sumSamples(histogramCollection_muons['BJet-'])
        histogramCollection_muons['BJet+'] = sumSamples(histogramCollection_muons['BJet+'])
        histogramCollection_muons['LightJet-'] = sumSamples(histogramCollection_muons['LightJet-'])
        histogramCollection_muons['LightJet+'] = sumSamples(histogramCollection_muons['LightJet+'])
        for source in metsystematics_sources:
            histogramCollection[source] = sumSamples(histogramCollection[source])
            histogramCollection_muons[source] = sumSamples(histogramCollection_muons[source])
        print 'Getting fitted normalisation for metbin=', metbin, 'electron channel'
        result_electrons[metbin] = measureNormalisationIncludingSystematics(histogramCollection, 'EPlusJets')
        print 'Getting fitted normalisation for metbin=', metbin, 'muon channel'
        result_muons[metbin] = measureNormalisationIncludingSystematics(histogramCollection_muons, 'MuPlusJets')
        
        if doBinByBinUnfolding:
            print 'Performing unfolding'
            result_electrons[metbin] = performUnfolding(result_electrons[metbin], metbin, 'EPlusJets')
            result_muons[metbin] = performUnfolding(result_muons[metbin], metbin, 'MuPlusJets')
        #combineResults the numbers
        result_combined[metbin] = combineResults(result_electrons[metbin], result_muons[metbin])
        print 'Result for metbin=', metbin, 'completed in %.2fs' % metbinTimer.elapsedTime()
    print 'Analysis in bjetbin=', bjetbin, 'finished in %.2fs' % analysisTimer.elapsedTime()
    return result_electrons, result_muons, result_combined, result_simultaniousFit

def performUnfolding(results, metbin, analysis):
    global correctionFactors, acceptanceFactors, contaminationFactors
    #corrections for bin migration
    correctionFactor_POWHEG = correctionFactors[analysis]['POWHEG'][metType][metbin]
#    correctionFactor_PYTHIA = correctionFactors[analysis]['PYTHIA6'][metType][metbin]
    correctionFactor_MCATNLO = correctionFactors[analysis]['MCatNLO'][metType][metbin]
    acceptanceFactor_POWHEG = acceptanceFactors[analysis]['POWHEG'][metbin]
#    acceptanceFactor_PYTHIA = acceptanceFactors[analysis]['PYTHIA6'][metbin]
    acceptanceFactor_MCATNLO = acceptanceFactors[analysis]['MCatNLO'][metbin]
    contaminationFactor_POWHEG = contaminationFactors[analysis]['POWHEG'][metbin]
#    contaminationFactor_PYTHIA = contaminationFactors[analysis]['PYTHIA6'][metbin]
    contaminationFactor_MCATNLO = contaminationFactors[analysis]['MCatNLO'][metbin]
    corrections_POWHEG = correctionFactor_POWHEG * acceptanceFactor_POWHEG * contaminationFactor_POWHEG
#    corrections_PYTHIA = correctionFactor_PYTHIA * acceptanceFactor_PYTHIA * contaminationFactor_PYTHIA
    corrections_MCATNLO = correctionFactor_MCATNLO * acceptanceFactor_MCATNLO * contaminationFactor_MCATNLO
    for measurement in results.keys():
        correctionFactor_MADGRAPH = correctionFactors[analysis]['TTJet'][metType][metbin]
        acceptanceFactor_MADGRAPH = acceptanceFactors[analysis]['TTJet'][metbin]
        contaminationFactor_MADGRAPH = contaminationFactors[analysis]['TTJet'][metbin]
        if measurement in metsystematics_sources:
            correctionFactor_MADGRAPH = correctionFactors[analysis]['TTJet'][measurement][metbin]
        if 'TTJets-' in measurement:
            correctionFactor_MADGRAPH = correctionFactors[analysis][measurement][metType][metbin]
            acceptanceFactor_MADGRAPH = acceptanceFactors[analysis][measurement][metbin]
            contaminationFactor_MADGRAPH = contaminationFactors[analysis][measurement][metbin]
        corrections_MADGRAPH = correctionFactor_MADGRAPH * acceptanceFactor_MADGRAPH * contaminationFactor_MADGRAPH
        results[measurement]['TTJet corrected'] = deepcopy(results[measurement]['TTJet'])
        results[measurement]['TTJet Before Fit corrected'] = deepcopy(results[measurement]['TTJet Before Fit'])
        results[measurement]['TTJet corrected']['value'] = results[measurement]['TTJet']['value'] * corrections_MADGRAPH
        results[measurement]['TTJet corrected']['error'] = results[measurement]['TTJet']['error'] * corrections_MADGRAPH
        results[measurement]['TTJet Before Fit corrected']['value'] = results[measurement]['TTJet Before Fit']['value'] * corrections_MADGRAPH
        if measurement == 'central':
            results[measurement]['POWHEG corrected'] = deepcopy(results[measurement]['POWHEG'])
#            results[measurement]['PYTHIA6 corrected'] = deepcopy(results[measurement]['PYTHIA6'])
            results[measurement]['MCatNLO corrected'] = deepcopy(results[measurement]['MCatNLO'])
            results[measurement]['POWHEG corrected']['value'] = results[measurement]['POWHEG']['value'] * corrections_POWHEG
#            results[measurement]['PYTHIA6 corrected']['value'] = results[measurement]['PYTHIA6']['value'] * corrections_PYTHIA
            results[measurement]['MCatNLO corrected']['value'] = results[measurement]['MCatNLO']['value'] * corrections_MCATNLO
    return results

def CrossSectionAnalysis(input_results, analysis):
    global N_ttbar_by_source
    result = {}
    theoryXsection = 157.5
    suffix = ''
    if doBinByBinUnfolding:
        suffix = ' corrected'
    for metbin in metbins:
        result[metbin] = {}
#        width = metbin_widths[metbin]
        for measurement in input_results[metbin].keys():
            result_ttbar = input_results[metbin][measurement]['TTJet' + suffix]
            madgraph_ttbar = input_results[metbin][measurement]['TTJet Before Fit' + suffix]['value']
            value, error = result_ttbar['value'], result_ttbar['error']
            if not analysis == 'Combination':
                n_ttbar = N_ttbar_by_source[analysis][measurement]
            else:
                n_ttbar = N_ttbar_by_source['EPlusJets'][measurement] + N_ttbar_by_source['MuPlusJets'][measurement]
            scale = theoryXsection / n_ttbar
            result[metbin][measurement] = {'value': value * scale,
                                           'error':error * scale,
                                           #replace these with GenMET
                                           'MADGRAPH':madgraph_ttbar * scale}
            if measurement == 'central':
                result[metbin][measurement].update(
                                            {'POWHEG':input_results[metbin][measurement]['POWHEG' + suffix]['value'] * scale,
#                                           'PYTHIA6':input_results[metbin][measurement]['PYTHIA6' + suffix]['value'] * scale,
                                           'MCatNLO':input_results[metbin][measurement]['POWHEG' + suffix]['value'] * scale})
    return result
        

def NormalisedCrossSectionAnalysis(input_results):
    global doBinByBinUnfolding
    result = {}
    sums = {'central':{}, 'MADGRAPH':{}, 'POWHEG':{}, 'MCatNLO':{} }  #'PYTHIA6':{}, 'MCatNLO':{} }
    if doBinByBinUnfolding:
        suffix = ' corrected'
    else:
        suffix = ''
    for metbin in metbins:
        result[metbin] = {}
        for measurement in input_results[metbin].keys():
            if not sums['central'].has_key(measurement):
                sums['central'][measurement] = input_results[metbin][measurement]['TTJet' + suffix]['value']
                sums['MADGRAPH'][measurement] = input_results[metbin][measurement]['TTJet Before Fit' + suffix]['value']
                if measurement == 'central':
                    sums['POWHEG'][measurement] = input_results[metbin][measurement]['POWHEG' + suffix]['value']
#                    sums['PYTHIA6'][measurement] = input_results[metbin][measurement]['PYTHIA6' + suffix]['value']
                    sums['MCatNLO'][measurement] = input_results[metbin][measurement]['MCatNLO' + suffix]['value']
            else:
                sums['central'][measurement] += input_results[metbin][measurement]['TTJet' + suffix]['value']
                sums['MADGRAPH'][measurement] += input_results[metbin][measurement]['TTJet Before Fit' + suffix]['value']
                if measurement == 'central':
                    sums['POWHEG'][measurement] += input_results[metbin][measurement]['POWHEG' + suffix]['value']
 #                   sums['PYTHIA6'][measurement] += input_results[metbin][measurement]['PYTHIA6' + suffix]['value']
                    sums['MCatNLO'][measurement] += input_results[metbin][measurement]['MCatNLO' + suffix]['value']
    
    for metbin in metbins:
        result[metbin] = {}
        width = metbin_widths[metbin]
        scale = 1 / width
        for measurement in input_results[metbin].keys():            
            result_ttbar = input_results[metbin][measurement]['TTJet' + suffix]
            madgraph_ttbar = input_results[metbin][measurement]['TTJet Before Fit' + suffix]['value'] * scale
            value, error = result_ttbar['value'] * scale, result_ttbar['error'] * scale
            
            result[metbin][measurement] = {'value': value / sums['central'][measurement],
                                           'error':error / sums['central'][measurement],
                                           'MADGRAPH':madgraph_ttbar / sums['MADGRAPH'][measurement]}
            if measurement == 'central':
                result[metbin][measurement].update(
                                           {'POWHEG':input_results[metbin][measurement]['POWHEG' + suffix]['value'] / sums['POWHEG'][measurement] * scale,
#                                           'PYTHIA6':input_results[metbin][measurement]['PYTHIA6' + suffix]['value'] / sums['PYTHIA6'][measurement] * scale,
                                           'MCatNLO':input_results[metbin][measurement]['MCatNLO' + suffix]['value'] / sums['MCatNLO'][measurement] * scale})
    return result

def getHistograms(bjetbin, metbin, analysis):
    print 'Getting histograms for bjetbin =', bjetbin, 'metbin=', metbin, 'and analysis=', analysis
    global metsystematics_sources, rebin, metType
    base = 'TTbar_plus_X_analysis/' + analysis + '/'
    
    distribution = base + 'Ref selection/Binned_MET_Analysis/%s_bin_%s/electron_absolute_eta_%s' % (metType, metbin, bjetbin)
    qcdDistribution = base + 'QCDConversions/Binned_MET_Analysis/%s_bin_%s/electron_absolute_eta_0btag' % (metType, metbin)
    qcdDistribution2 = base + 'QCD non iso e+jets/Binned_MET_Analysis/%s_bin_%s/electron_absolute_eta_0btag' % (metType, metbin)
    if analysis == "MuPlusJets":
        distribution = base + 'Ref selection/Binned_MET_Analysis/%s_bin_%s/muon_absolute_eta_%s' % (metType, metbin, bjetbin)
        qcdDistribution = base + 'QCD non iso mu+jets/Binned_MET_Analysis/%s_bin_%s/muon_absolute_eta_0btag' % (metType, metbin)
        qcdDistribution2 = base + 'QCD non iso mu+jets/Binned_MET_Analysis/%s_bin_%s/muon_absolute_eta_0btag' % (metType, metbin)
        
    used_data = data_label[analysis]
    histogramCollection = {}
    histogramCollection['central'] = FileReader.getHistogramDictionary(distribution, FILES.files)
    histogramCollection['central']['QCDFromData_Conversions'] = FileReader.getHistogramFromFile(qcdDistribution, FILES.files[used_data])
    histogramCollection['central']['QCDFromData_AntiIsolated'] = FileReader.getHistogramFromFile(qcdDistribution2, FILES.files[used_data])
    histogramCollection['JES-'] = FileReader.getHistogramDictionary(distribution, FILES.files_JES_down)
    histogramCollection['JES-']['QCDFromData_Conversions'] = FileReader.getHistogramFromFile(qcdDistribution, FILES.files_JES_down[used_data])
    histogramCollection['JES-']['QCDFromData_AntiIsolated'] = FileReader.getHistogramFromFile(qcdDistribution2, FILES.files_JES_down[used_data])
    histogramCollection['JES+'] = FileReader.getHistogramDictionary(distribution, FILES.files_JES_up)
    histogramCollection['JES+']['QCDFromData_Conversions'] = FileReader.getHistogramFromFile(qcdDistribution, FILES.files_JES_up[used_data])
    histogramCollection['JES+']['QCDFromData_AntiIsolated'] = FileReader.getHistogramFromFile(qcdDistribution2, FILES.files_JES_up[used_data])
    histogramCollection['PileUp-'] = FileReader.getHistogramDictionary(distribution, FILES.files_PU_down)
    histogramCollection['PileUp-']['QCDFromData_Conversions'] = deepcopy(histogramCollection['central']['QCDFromData_Conversions'])
    histogramCollection['PileUp-']['QCDFromData_AntiIsolated'] = deepcopy(histogramCollection['central']['QCDFromData_AntiIsolated'])
    histogramCollection['PileUp+'] = FileReader.getHistogramDictionary(distribution, FILES.files_PU_up)
    histogramCollection['PileUp+']['QCDFromData_Conversions'] = deepcopy(histogramCollection['central']['QCDFromData_Conversions'])
    histogramCollection['PileUp+']['QCDFromData_AntiIsolated'] = deepcopy(histogramCollection['central']['QCDFromData_AntiIsolated'])
    histogramCollection['PDFWeights'] = FileReader.getHistogramDictionary(distribution, FILES.files_PDF_weights)
    histogramCollection['BJet-'] = FileReader.getHistogramDictionary(distribution, FILES.files_BJet_down)
    histogramCollection['BJet-']['QCDFromData_Conversions'] = deepcopy(histogramCollection['central']['QCDFromData_Conversions']) 
    histogramCollection['BJet-']['QCDFromData_AntiIsolated'] = deepcopy(histogramCollection['central']['QCDFromData_AntiIsolated']) 
    histogramCollection['BJet+'] = FileReader.getHistogramDictionary(distribution, FILES.files_BJet_up)
    histogramCollection['BJet+']['QCDFromData_Conversions'] = deepcopy(histogramCollection['central']['QCDFromData_Conversions'])
    histogramCollection['BJet+']['QCDFromData_AntiIsolated'] = deepcopy(histogramCollection['central']['QCDFromData_AntiIsolated']) 
    histogramCollection['LightJet-'] = FileReader.getHistogramDictionary(distribution, FILES.files_LightJet_down)
    histogramCollection['LightJet-']['QCDFromData_Conversions'] = deepcopy(histogramCollection['central']['QCDFromData_Conversions']) 
    histogramCollection['LightJet-']['QCDFromData_AntiIsolated'] = deepcopy(histogramCollection['central']['QCDFromData_AntiIsolated'])
    histogramCollection['LightJet+'] = FileReader.getHistogramDictionary(distribution, FILES.files_LightJet_up)
    histogramCollection['LightJet+']['QCDFromData_Conversions'] = deepcopy(histogramCollection['central']['QCDFromData_Conversions'])
    histogramCollection['LightJet+']['QCDFromData_AntiIsolated'] = deepcopy(histogramCollection['central']['QCDFromData_AntiIsolated'])
    
    for source in metsystematics_sources:
        distribution = base + 'Ref selection/Binned_MET_Analysis/%s_bin_%s/electron_absolute_eta_%s' % (source, metbin, bjetbin)
        qcdDistribution = base + 'QCDConversions/Binned_MET_Analysis/%s_bin_%s/electron_absolute_eta_0btag' % (source, metbin)
        if analysis == "MuPlusJets":
            distribution = base + 'Ref selection/Binned_MET_Analysis/%s_bin_%s/muon_absolute_eta_%s' % (source, metbin, bjetbin)
            qcdDistribution = base + 'QCD non iso mu+jets/Binned_MET_Analysis/%s_bin_%s/muon_absolute_eta_0btag' % (source, metbin)
            qcdDistribution2 = base + 'QCD non iso mu+jets/Binned_MET_Analysis/%s_bin_%s/muon_absolute_eta_0btag' % (source, metbin)
        if not 'JER' in source:
            histogramCollection[source] = FileReader.getHistogramDictionary(distribution, FILES.files)
            histogramCollection[source]['QCDFromData_Conversions'] = FileReader.getHistogramFromFile(qcdDistribution, FILES.files[used_data])
            histogramCollection[source]['QCDFromData_AntiIsolated'] = FileReader.getHistogramFromFile(qcdDistribution2, FILES.files[used_data])
        else:
            mcFiles = deepcopy(FILES.files)
            mcFiles.pop('SingleElectron')#removes data
            mcFiles.pop('SingleMu')#removes data
            histogramCollection[source] = FileReader.getHistogramDictionary(distribution, FILES.files)
            histogramCollection[source]['QCDFromData_Conversions'] = deepcopy(histogramCollection['central']['QCDFromData_Conversions'])
            histogramCollection[source]['QCDFromData_AntiIsolated'] = deepcopy(histogramCollection['central']['QCDFromData_AntiIsolated'])
    
    muonQCD_corrections = FileReader.getHistogramFromFile('etaAbs_ge2j_tight', 'data/etaAbs_ge2j_tight.root')
    #initial binning 0.05, target: 0.2
    muonQCD_corrections.Rebin(4)
    muQCD = FileReader.getHistogramFromFile('etaAbs_ge2j_data', 'data/QCD_data_mu.root')
    for source in histogramCollection.keys():
        hists = histogramCollection[source]
        hists = plotting.rebin(hists, rebin)#rebin to 200 bins
        hists = plotting.setYTitle(hists, title="Events/%.2f" % (0.02 * rebin))
        
        if analysis == "MuPlusJets" and not source in ['PDFWeights']:
            hists['QCDFromData_Conversions'] = muQCD.Clone()
            hists['QCDFromData_AntiIsolated'] = muQCD.Clone()
        #correction for muon QCD
#        if analysis == "MuPlusJets" and not source in ['PDFWeights']:
#            
#            muQCD = hists['QCDFromData_AntiIsolated']#both plots are identical
#            nbins = muQCD.GetNbinsX()
#
#            for bin_i in range(1, nbins + 1):
#                correction = muonQCD_corrections.GetBinContent(bin_i)
#                value = muQCD.GetBinContent(bin_i)
#                muQCD.SetBinContent(bin_i, value * correction)
#            
#            hists['QCDFromData_Conversions'] = muQCD
#            hists['QCDFromData_AntiIsolated'] = muQCD
        
    #sum samples
    histogramCollection['central'] = sumSamples(histogramCollection['central'])
    histogramCollection['JES-'] = sumSamples(histogramCollection['JES-'])
    histogramCollection['JES+'] = sumSamples(histogramCollection['JES+'])
    histogramCollection['PileUp-'] = sumSamples(histogramCollection['PileUp-'])
    histogramCollection['PileUp+'] = sumSamples(histogramCollection['PileUp+'])
    histogramCollection['BJet-'] = sumSamples(histogramCollection['BJet-'])
    histogramCollection['BJet+'] = sumSamples(histogramCollection['BJet+'])
    histogramCollection['LightJet-'] = sumSamples(histogramCollection['LightJet-'])
    histogramCollection['LightJet+'] = sumSamples(histogramCollection['LightJet+'])
    for source in metsystematics_sources:
        histogramCollection[source] = sumSamples(histogramCollection[source])
    return histogramCollection

def setNEvents(bjetbin, analysis):
    global N_Events, metType

    histname = 'TTbar_plus_X_analysis/' + analysis + '/Ref selection/Electron/electron_AbsEta_' + bjetbin
    if analysis == 'MuPlusJets':
        histname = 'TTbar_plus_X_analysis/' + analysis + '/Ref selection/Muon/muon_AbsEta_' + bjetbin
        
#    unbinnedHist = FileReader.getHistogramDictionary('TTbar_plus_X_analysis/'+ analysis + '/Ref selection/MET/' + met + '/MET_' + bjetbin,
#                                                     FILES.files)
    unbinnedHist = FileReader.getHistogramDictionary(histname, FILES.files)
    unbinnedHist['W+Jets'] = plotting.sumSamples(unbinnedHist, wplusjets_samples)
    unbinnedHist['DYJetsToLL'] = plotting.sumSamples(unbinnedHist, zplusjets_samples)
    unbinnedHist['V+Jets'] = plotting.sumSamples(unbinnedHist, vplusjets_samples)
    N_Events[analysis] = {}
    
    N_Events[analysis]['TTJet'] = unbinnedHist['TTJet'].Integral()
    N_Events[analysis]['W+Jets'] = unbinnedHist['W+Jets'].Integral()
    N_Events[analysis]['DYJetsToLL'] = unbinnedHist['DYJetsToLL'].Integral()
    #remove V+Jets
    N_Events[analysis]['V+Jets'] = unbinnedHist['V+Jets'].Integral()
    
    N_Events[analysis]['TTJets-matchingup'] = unbinnedHist['TTJets-matchingup'].Integral()
    N_Events[analysis]['TTJets-matchingdown'] = unbinnedHist['TTJets-matchingdown'].Integral()
    N_Events[analysis]['TTJets-scaleup'] = unbinnedHist['TTJets-scaleup'].Integral()
    N_Events[analysis]['TTJets-scaledown'] = unbinnedHist['TTJets-scaledown'].Integral()
    
    N_Events[analysis]['WJets-matchingup'] = unbinnedHist['WJets-matchingup'].Integral()
    N_Events[analysis]['WJets-matchingdown'] = unbinnedHist['WJets-matchingdown'].Integral()
    N_Events[analysis]['WJets-scaleup'] = unbinnedHist['WJets-scaleup'].Integral()
    N_Events[analysis]['WJets-scaledown'] = unbinnedHist['WJets-scaledown'].Integral()
    
    N_Events[analysis]['ZJets-matchingup'] = unbinnedHist['ZJets-matchingup'].Integral()
    N_Events[analysis]['ZJets-matchingdown'] = unbinnedHist['ZJets-matchingdown'].Integral()
    N_Events[analysis]['ZJets-scaleup'] = unbinnedHist['ZJets-scaleup'].Integral()
    N_Events[analysis]['ZJets-scaledown'] = unbinnedHist['ZJets-scaledown'].Integral()
    
def setNTtbar(bjetbin, analysis):
    global N_ttbar_by_source, metType
    N_ttbar_by_source[analysis] = {}
    histname = 'TTbar_plus_X_analysis/' + analysis + '/Ref selection/Electron/electron_AbsEta_' + bjetbin
    if analysis == 'MuPlusJets':
        histname = 'TTbar_plus_X_analysis/' + analysis + '/Ref selection/Muon/muon_AbsEta_' + bjetbin
        
    getHist = FileReader.getHistogramFromFile
    central = getHist(histname, FILES.files['TTJet']).Integral()
    sameAsCentral = ['central', 'SingleTop +', 'SingleTop -', 'QCD shape', 'TTJet matching +', 'TTJet matching -',
                     'TTJet scale +', 'TTJet scale -', 'W+Jets matching +', 'W+Jets matching -', 'W+Jets scale +',
                     'W+Jets scale -', 'Z+Jets matching +', 'Z+Jets matching -', 'Z+Jets scale +', 'Z+Jets scale -',
                     'V+Jets matching +', 'V+Jets matching -', 'V+Jets scale +', 'V+Jets scale -']
    for source in sameAsCentral:
        N_ttbar_by_source[analysis][source] = central
    
    N_ttbar_by_source[analysis]['Electron Efficiency +'] = central * (1. + 0.03)
    N_ttbar_by_source[analysis]['Electron Efficiency -'] = central * (1. - 0.03)
    N_ttbar_by_source[analysis]['Muon Efficiency +'] = central * (1. + 0.03)
    N_ttbar_by_source[analysis]['Muon Efficiency -'] = central * (1. - 0.03)
    N_ttbar_by_source[analysis]['Luminosity +'] = central * (1. + 0.022)
    N_ttbar_by_source[analysis]['Luminosity -'] = central * (1. - 0.022)
    N_ttbar_by_source[analysis]['JES-'] = getHist(histname, FILES.files_JES_down['TTJet']).Integral()
    N_ttbar_by_source[analysis]['JES+'] = getHist(histname, FILES.files_JES_up['TTJet']).Integral()
    N_ttbar_by_source[analysis]['PileUp-'] = getHist(histname, FILES.files_PU_down['TTJet']).Integral()
    N_ttbar_by_source[analysis]['PileUp+'] = getHist(histname, FILES.files_PU_up['TTJet']).Integral()
    N_ttbar_by_source[analysis]['BJet-'] = getHist(histname, FILES.files_BJet_down['TTJet']).Integral()
    N_ttbar_by_source[analysis]['BJet+'] = getHist(histname, FILES.files_BJet_up['TTJet']).Integral()
    N_ttbar_by_source[analysis]['LightJet-'] = getHist(histname, FILES.files_LightJet_down['TTJet']).Integral()
    N_ttbar_by_source[analysis]['LightJet+'] = getHist(histname, FILES.files_LightJet_up['TTJet']).Integral()
    
    
    for index in range(1, 45):
        filename = 'TTJet_%d' % index
        pdf = 'PDFWeights_%d' % index
        N_ttbar_by_source[analysis][pdf] = getHist(histname, FILES.files_PDF_weights[filename]).Integral()
    
    
    for source in metsystematics_sources:
#        histname = 'TTbar_plus_X_analysis/'+ analysis + '/Ref selection/MET/%s/MET_%s' % (source, bjetbin)
        N_ttbar_by_source[analysis][source] = central#getHist(histname, FILES.files['TTJet']).Integral()
    
def prepareHistogramCollections(histogramCollection):
    global metsystematics_sources
    
def printNormalisation(normalisation_):
    global qcdLabel, metbin, current_source
    sumMC = normalisation_['SumMC'] - normalisation_['QCD'] + normalisation_[qcdLabel]
    print '*' * 120
    print 'MET bin: ', metbin
    print 'source:', current_source
    print "Input parameters:"
    print 'signal (ttbar+single top):', normalisation_['TTJet'] + normalisation_['SingleTop']
    print 'W+Jets:', normalisation_['W+Jets']
    print 'Z+Jets:', normalisation_['DYJetsToLL'] 
    print qcdLabel, ':', normalisation_[qcdLabel]
    print 'SingleTop :', normalisation_['SingleTop'] 
    print 'TTJet :', normalisation_['TTJet']  
#    print 'Di-Boson:', normalisation_['Di-Boson']
    print 'SumMC:', sumMC
    print 'Total data', normalisation_[used_data]
    if not normalisation_[used_data] == 0:
        print '(N_{data} - N_{SumMC})/N_{data}', (normalisation_[used_data] - sumMC) / normalisation_[used_data]
    print '*' * 120
    
def printFittedResult(fitted_result):
    global current_source
    sumMC = sum([fitted_result['Signal']['value'],
                 fitted_result['W+Jets']['value'],
                 fitted_result['DYJetsToLL']['value'],
                 fitted_result[qcdLabel]['value'],
#                 fitted_result['Di-Boson']
                ]
                )
    print '*' * 120
    print 'MET bin: ', metbin
    print 'source:', current_source
    print "Fit values:"
    print 'signal (ttbar+single top):', fitted_result['Signal']['value'], '+-', fitted_result['Signal']['error']
    print 'W+Jets:', fitted_result['W+Jets']['value'], '+-', fitted_result['W+Jets']['error']
    print 'Z+Jets:', fitted_result['DYJetsToLL']['value'], '+-', fitted_result['DYJetsToLL']['error']
    print 'QCD:', fitted_result[qcdLabel]['value'], '+-', fitted_result[qcdLabel]['error']
    print 'SingleTop (no fit):', fitted_result['SingleTop']['value'], '+-', fitted_result['SingleTop']['error']
    print 'TTJet (signal fit - SingleTop):', fitted_result['TTJet']['value'], '+-', fitted_result['TTJet']['error']
#    print 'Di-Boson:', fitted_result['Di-Boson']['value'], '+-', fitted_result['Di-Boson']['error']
    print 'SumMC:', sumMC
    N_data = fitted_result[used_data]['value']
    print 'Total data:', N_data
    print '(N_{data} - N_{SumMC})/N_{data}:', (N_data - sumMC) / N_data
    print '*' * 120
    
def getNormalisation(histograms):
    global scale_factors
    normalisation_ = {}
    for sample in histograms.keys():
#        if sample == 'W+Jets':
#            print histograms[sample].Integral(), histograms[sample].GetName()
        normalisation_[sample] = histograms[sample].Integral()
        if not sample in ['SingleElectron', 'SingleMu', 'QCDFromData']:
            normalisation_[sample] = normalisation_[sample] * scale_factors['luminosity']
        if sample in scale_factors.keys():
            normalisation_[sample] = normalisation_[sample] * scale_factors[sample]
    return normalisation_

def getTemplates(histograms):
    templates = {}
    for sample in histograms.keys():
        hist = deepcopy(histograms[sample].Clone())
#        hist.Sumw2()
        templates[sample] = plotting.normalise(hist)
    return templates 

def vectorise(histograms):
    values = {}
#    errors = {}
    for sample in histograms.keys():
        hist = histograms[sample]
        nBins = hist.GetNbinsX()
        for bin_i in range(1, nBins + 1):
            if not values.has_key(sample):
                values[sample] = []
            values[sample].append(hist.GetBinContent(bin_i))
    return values

def printNormalisationResult(result, analysis, toFile=True):
    global metbins
    printout = '\n'
    printout += '=' * 60
    printout = '\n'
    printout += 'Results for %s region\n' % bjetbin
    printout += '=' * 60
    printout += '\n'
    rows = {}
    header = 'Sample'
    for metbin in metbins:
        header += '& N_{events}^(fit) \met bin %s~\GeV' % metbin
        for source in result[metbin].keys():
            results = result[metbin][source]
            if not rows.has_key(source):
                rows[source] = {}
            
            for sample in results.keys():
                if sample == 'fit' or sample == 'vectors':
                    continue
                fitresult = results[sample]
                if DEBUG:
                    print fitresult
                row = rows[source]
                text = ' $%(value)f \pm %(error)f$' % fitresult + '(%.2f' % (getRelativeError(fitresult['value'], fitresult['error']) * 100) + '\%)'
                if row.has_key(sample): 
                    row[sample].append(text)
                else:
                    row[sample] = [sample, text]
    header += '\\\\ \n'
    printout += 'Central measurement \n\n'
    printout += header
    printout += '\hline\n'
    for sample in sorted(rows['central'].keys()):
        results = rows['central'][sample]
        for result in results:
            printout += result + '&'
        printout = printout.rstrip('&')
        printout += '\\\\ \n'
    printout += '\hline\n\n'
    if DEBUG:
        print printout
    
    for source in sorted(rows.keys()):
        if source == 'central':
            continue
        printout += source + ' measurement \n\n'
        printout += header
        printout += '\hline \n'
        for sample in sorted(rows[source].keys()):
            results = rows[source][sample]
            for result in results:
                printout += result + '&'
            printout = printout.rstrip('&')
            printout += '\\\\ \n'
        printout += '\hline \n\n'
    if toFile:
        unfolding = '_unfolded'
        if not doBinByBinUnfolding:
            unfolding = ''
            
        fileutils.writeStringToFile(printout, savePath + analysis + '_normalisation_result' + unfolding + '_' + bjetbin + '.tex')
#        output_file = open(savePath + analysis + '_normalisation_result' + unfolding + '_' + bjetbin + '.tex', 'w')
#        output_file.write(printout)
#        output_file.close()
    else:
        print printout

def getRelativeError(value, error):
    relativeError = 0
    if not value == 0:
        relativeError = error / value
    return relativeError
        
def sumSamples(hists):
    hists['QCD'] = plotting.sumSamples(hists, qcd_samples)
    hists['SingleTop'] = plotting.sumSamples(hists, singleTop_samples)
#    hists['Di-Boson'] = plotting.sumSamples(hists, diboson_samples)
    hists['W+Jets'] = plotting.sumSamples(hists, wplusjets_samples)
    hists['DYJetsToLL'] = plotting.sumSamples(hists, zplusjets_samples)
    #TODO: DO NOT SUM W/Z- bosons and signal here as it will be impossible to vary them for the fit!!
    hists['V+Jets'] = plotting.sumSamples(hists, vplusjets_samples)
    hists['SumMC'] = plotting.sumSamples(hists, allMC_samples)
    hists['Signal'] = plotting.sumSamples(hists, signal_samples)
    return hists

#change to calculate uncertainties
def calculateTotalUncertainty(results, ommitTTJetsSystematics=False):
    pdf_min, pdf_max = calculatePDFErrors(results)
    pdf_min, pdf_max = 0, 0
    centralResult = results['central']
    if centralResult.has_key('TTJet'):
        centralResult = results['central']['TTJet']
    centralvalue, centralerror = centralResult['value'], centralResult['error']
    totalMinus, totalPlus = pdf_min ** 2 , pdf_max ** 2
    totalMinus_err, totalPlus_err = 0, 0
    totalMETMinus, totalMETPlus = 0, 0
    totalMETMinus_err, totalMETPlus_err = 0, 0
    uncertainty = {}
    for source in results.keys():
        if source == 'central' or 'PDFWeights_' in source:
            continue
        if ommitTTJetsSystematics and source in ['TTJet scale -', 'TTJet scale +', 'TTJet matching -', 'TTJet matching +']:
            continue
        result = results[source]
        if result.has_key('TTJet'):
            result = results['central']['TTJet']
        value, error = result['value'], result['error']
        diff = abs(value) - abs(centralvalue)
        diff_error = sqrt((centralerror / centralvalue) ** 2 + (error / value) ** 2) * abs(diff)
        uncertainty[source] = {'value':diff, 'error':diff_error}
        if diff > 0:
            totalPlus += diff ** 2
            totalPlus_err += diff_error ** 2
        else:
            totalMinus += diff ** 2
            totalMinus_err += diff_error ** 2
            
        if source in metsystematics_sources:
            if diff > 0:
                totalMETPlus += diff ** 2
                totalMETPlus_err += diff_error ** 2
            else:
                totalMETMinus += diff ** 2
                totalMETMinus_err += diff_error ** 2
        
    total = sqrt(totalPlus + totalMinus)
    total_error = sqrt(totalPlus_err + totalMinus_err)
    totalPlus, totalMinus, totalPlus_err, totalMinus_err = (sqrt(totalPlus), sqrt(totalMinus),
                                                             sqrt(totalPlus_err), sqrt(totalMinus_err))
    
    totalMETPlus, totalMETMinus, totalMETPlus_err, totalMETMinus_err = (sqrt(totalMETPlus), sqrt(totalMETMinus),
                                                             sqrt(totalMETPlus_err), sqrt(totalMETMinus_err))
    uncertainty['Total+'] = {'value':totalPlus, 'error':totalPlus_err}
    uncertainty['Total-'] = {'value':totalMinus, 'error':totalMinus_err}
    uncertainty['Total'] = {'value':total, 'error':total_error}
    uncertainty['TotalMETUnc+'] = {'value':totalMETPlus, 'error':totalMETPlus_err}
    uncertainty['TotalMETUnc-'] = {'value':totalMETMinus, 'error':totalMETMinus_err}
    uncertainty['PDFWeights+'] = {'value':pdf_max, 'error':0}
    uncertainty['PDFWeights-'] = {'value':pdf_min, 'error':0}
    
    return uncertainty
    #uncertainty = {total, totalMinu, totalPlus, PDFs ....}
    #keys = sources + total, totalMinu, totalPlus, PDFs - central
#    return total, totalMinus, totalPlus
    
def printNormalisationResultsForTTJetWithUncertanties(result, analysis, toFile=True):
    global metbins
    printout = '\n'
    printout += '=' * 60
    printout = '\n'
    printout += 'Results for %s region\n' % bjetbin
    printout += '=' * 60
    printout += '\n'
#    rows = {}
    printout += '\met bin & N_{t\\bar{t}}^{fit} \\\\ \n'
    printout += '\hline\n'
    uncertainties = {}
    for metbin in metbins:
        centralresult = result[metbin]['central']['TTJet']
        uncertainty = calculateTotalUncertainty(result[metbin])
        uncertainty['Total+']['value'], uncertainty['Total-']['value'] = symmetriseErrors(uncertainty['Total+']['value'], uncertainty['Total-']['value'])
        formatting = (metbin, centralresult['value'], centralresult['error'], uncertainty['Total+']['value'], uncertainty['Total-']['value'])
        text = '%s~\GeV & $%f \pm %.f (fit)^{+%f}_{-%.f} (sys)$ \\\\ \n' % formatting
        printout += text
        
        for source, value in uncertainty.iteritems():
            unc_result = value
            if not uncertainties.has_key(source):
                uncertainties[source] = '\n'
                uncertainties[source] += '=' * 60
                uncertainties[source] = '\n'
                uncertainties[source] += 'Results for %s region, source = %s\n' % (bjetbin, source)
                uncertainties[source] += '=' * 60
                uncertainties[source] += '\n'
            formatting = (metbin,
                          unc_result['value'],
                          unc_result['error'],
                          ('%.2f' % (unc_result['value'] / centralresult['value'] * 100)) + '\%')
            text = '%s~\GeV & $%f \pm %f (fit) (%s of central result)$ \\\\ \n' % formatting
            uncertainties[source] += text
        
    if toFile:
        unfolding = '_unfolded'
        if not doBinByBinUnfolding:
            unfolding = ''
        for source, value in uncertainties.iteritems():
            printout += value
#        output_file = open(savePath + analysis + '_normalisation_TTJet_result' + unfolding + '_' + bjetbin + '.tex', 'w')
#        output_file.write(printout)
#        output_file.close()
        fileutils.writeStringToFile(printout, savePath + analysis + '_normalisation_TTJet_result' + unfolding + '_' + bjetbin + '.tex')
    else:
        print printout

def printCrossSectionResult(result, analysis, toFile=True):    
    global metbins
    printout = '\n'
    printout += '=' * 60
    printout = '\n'
    printout += 'Results for %s region\n' % bjetbin
    printout += '=' * 60
    printout += '\n'
    rows = {}
    header = 'Measurement'
    for metbin in metbins:
#        width = metbin_widths[metbin]
        scale = 1# / width
        header += '& $\sigma_{meas}$ \met bin %s~\GeV' % metbin
        for source in result[metbin].keys():
            fitresult = result[metbin][source]
            relativeError = getRelativeError(fitresult['value'], fitresult['error'])
            text = ' $%.2f \pm %.2f$  pb' % (fitresult['value'] * scale, fitresult['error'] * scale) + '(%.2f' % (relativeError * 100) + '\%)'
            if rows.has_key(source):
                rows[source].append(text)
            else:
                rows[source] = [source, text]
            
    header += '\\\\ \n'
    printout += header
    printout += '\hline\n'
    for item in rows['central']:
        printout += item + '&'
    printout = printout.rstrip('&')
    printout += '\\\\ \n'
    
    for source in sorted(rows.keys()):
        if source == 'central':
            continue
        for item in rows[source]:
            printout += item + '&'
        printout = printout.rstrip('&')
        printout += '\\\\ \n'
    printout += '\hline \n\n'
        
    if toFile:
        unfolding = '_unfolded'
        if not doBinByBinUnfolding:
            unfolding = ''
        fileutils.writeStringToFile(printout, savePath + analysis + '_crosssection_result' + unfolding + '_' + bjetbin + '.tex')
#        output_file = open(savePath + analysis + '_crosssection_result' + unfolding + '_' + bjetbin + '.tex', 'w')
#        output_file.write(printout)
#        output_file.close()
    else:
        print printout

def printCrossSectionResultsForTTJetWithUncertanties(result, analysis, toFile=True):
    global metbins
    printout = '\n'
    printout += '=' * 60
    printout = '\n'
    printout += 'Results for %s region\n' % bjetbin
    printout += '=' * 60
    printout += '\n'
#    rows = {}
    printout += '\met bin & $\sigma{meas}$ \\\\ \n'
    printout += '\hline\n'
    uncertainties = {}
    for metbin in metbins:
#        width = metbin_widths[metbin]
        scale = 1# / width
        centralresult = result[metbin]['central']
        uncertainty = calculateTotalUncertainty(result[metbin])
        uncertainty['Total+']['value'], uncertainty['Total-']['value'] = symmetriseErrors(uncertainty['Total+']['value'], uncertainty['Total-']['value'])
        formatting = (metbin, centralresult['value'] * scale, centralresult['error'] * scale,
                      uncertainty['Total+']['value'] * scale, uncertainty['Total-']['value'] * scale)
        text = '%s~\GeV & $%.2f \pm %.2f (fit)^{+%.2f}_{-%.2f} (sys)$ pb \\\\ \n' % formatting
        printout += text
        
        for source, value in uncertainty.iteritems():
            unc_result = value
            if not uncertainties.has_key(source):
                uncertainties[source] = '\n'
                uncertainties[source] += '=' * 60
                uncertainties[source] = '\n'
                uncertainties[source] += 'Results for %s region, source = %s\n' % (bjetbin, source)
                uncertainties[source] += '=' * 60
                uncertainties[source] += '\n'
            formatting = (metbin,
                          unc_result['value'] * scale,
                          unc_result['error'] * scale,
                          ('%.2f' % (unc_result['value'] / centralresult['value'] * 100)) + '\%')
            text = '%s~\GeV & $%.2f \pm %.2f (fit) (%s of central result)$ \\\\ \n' % formatting
            uncertainties[source] += text
        
    if toFile:
        unfolding = '_unfolded'
        if not doBinByBinUnfolding:
            unfolding = ''
        for source, value in uncertainties.iteritems():
            printout += value
        fileutils.writeStringToFile(printout, savePath + analysis + '_crosssection_main_result' + unfolding + '_' + bjetbin + '.tex')
    else:
        print printout
        
def calculatePDFErrors(results):
    centralResult = results['central']
    if centralResult.has_key('TTJet'):
        centralResult = results['central']['TTJet']
    centralvalue = centralResult['value']
    negative = []
    positive = []
    
    for index in range(1, 45):
        weight = 'PDFWeights_%d' % index
        result = results[weight]
        if result.has_key('TTJet'):
            result = results[weight]['TTJet']
        value = result['value']
        if index % 2 == 0: #even == negative
            negative.append(value)
        else:
            positive.append(value)
    pdf_max = numpy.sqrt(sum(max(x - centralvalue, y - centralvalue, 0) ** 2 for x, y in zip(negative, positive)))
    pdf_min = numpy.sqrt(sum(max(centralvalue - x, centralvalue - y, 0) ** 2 for x, y in zip(negative, positive)))
    return pdf_min, pdf_max   
    
    
def plotNormalisationResults(results, analysis):
    global metbins
    for metbin in metbins:
        for measurement, result in results[metbin].iteritems():
            if not measurement == 'central' and not measurement == 'QCD shape':
                continue
#        result = results[metbin]['central']
#            fit = result['fit']
    #        fitvalues = result['fitvalues']
            templates = result['vectors']
            plots = {}
            plot_templates = {}
            
            used_data = data_label[analysis]
            samples = [
                       used_data,
                       'V+Jets',
#                       'W+Jets',
#                       'DYJetsToLL',
                       qcdLabel,
    #                   'Di-Boson',
                        'Signal'
#                       'TTJet',
#                       'SingleTop'
                       ]
            colors = {
                      used_data:0,
                      'V+Jets':kGreen - 3,
#                       'W+Jets':kGreen - 3,
#                       'DYJetsToLL':kAzure - 2,
                       qcdLabel:kYellow,
    #                   'Di-Boson':kWhite,
                        'Signal':kRed + 1,
#                       'TTJet':kRed + 1,
#                       'SingleTop': kMagenta
                      }
            for sample in samples:
                template = templates[sample]
                plot = TH1F(sample + metbin + bjetbin + measurement + analysis, sample, 13, 0, 2.6)
                plot_template = TH1F(sample + metbin + bjetbin + measurement + analysis + '_template', sample, 13, 0, 2.6)
                bin_i = 1
                for value in template:
                    plot.SetBinContent(bin_i, value)
                    plot_template.SetBinContent(bin_i, value)
                    bin_i += 1
                plot.Scale(result[sample]['value'])
    #            plot.Rebin(rebin)
                plot.SetYTitle('Events/0.2')
                plot_template.SetYTitle('normalised to unit area/0.2')
                if analysis == 'EPlusJets':
                    plot.SetXTitle('|#eta(e)|')
                    plot_template.SetXTitle('|#eta(e)|')
                else:
                    plot.SetXTitle('|#eta(#mu)|')
                    plot_template.SetXTitle('|#eta(#mu)|')
                plot.SetMarkerStyle(20)
                
                
                if not sample == used_data:
                    plot.SetFillColor(colors[sample])
#                    plot.SetLineColor(colors[sample])
                    plot_template.SetLineColor(colors[sample])
                    plot_template.SetLineWidth(5)
                plots[sample] = plot
                plot_templates[sample] = plot_template
            plots['Background'] = plots['V+Jets'].Clone()
            plots['Background'] += plots[qcdLabel]
            c = TCanvas("Fit_" + metbin + bjetbin + measurement + analysis, "Differential cross section", 1600, 1200)
            max_y = plots[used_data].GetMaximum()
            plots[used_data].SetMaximum(max_y * 1.5)
            plots[used_data].Draw('error')
            mcStack = THStack("MC", "MC")
    #        mcStack.Add(plots['Di-Boson']);
#            mcStack.Add(plots[qcdLabel]);
#            mcStack.Add(plots['V+Jets']);
            mcStack.Add(plots['Background']);
            mcStack.Add(plots['Signal']);
#            mcStack.Add(plots['DYJetsToLL']);
#            mcStack.Add(plots['W+Jets']);
#            mcStack.Add(plots['SingleTop']);
#            mcStack.Add(plots['TTJet']);
            mcStack.Draw('hist same')
#            fit.Draw('same')
            plots[used_data].Draw('error same')
            
            legend = plotting.create_legend(x0=0.65, y0 = 0.95, x1=0.94, y1=0.55)
            legend.AddEntry(plots[used_data], "data", 'P')
            legend.AddEntry(plots['Signal'], 't#bar{t} + Single-Top', 'F')
#            legend.AddEntry(plots['TTJet'], 't#bar{t}', 'F')
#            legend.AddEntry(plots['SingleTop'], 'Single-Top', 'F')
            legend.AddEntry(plots['Background'], 'background', 'F')
#            legend.AddEntry(plots['V+Jets'], 'V+Jets', 'F')
#            legend.AddEntry(plots['W+Jets'], 'W#rightarrowl#nu', 'F')
#            legend.AddEntry(plots['DYJetsToLL'], 'Z/#gamma*#rightarrowl^{+}l^{-}', 'F')
#            legend.AddEntry(plots[qcdLabel], 'QCD/#gamma + jets', 'F')
            
    #        legend.AddEntry(plots['Di-Boson'], 'VV + X', 'F')
            legend.Draw()
            metLabel = TPaveText(0.2, 0.8, 0.6, 0.95, "NDC")
            mytext = TPaveText(0.5, 0.97, 1, 1.01, "NDC")
            channelLabel = TPaveText(0.18, 0.97, 0.5, 1.01, "NDC")
            if analysis == 'EPlusJets':
                channelLabel.AddText("e, %s, %s" % ("#geq 4 jets", BjetBinsLatex[bjetbin]))
            elif analysis == 'MuPlusJets':
                channelLabel.AddText("#mu, %s, %s" % ("#geq 4 jets", BjetBinsLatex[bjetbin]))
            elif analysis == 'Combination':
                channelLabel.AddText("combined, %s, %s" % ("#geq 4 jets", BjetBinsLatex[bjetbin]))
            
            mytext.AddText("CMS Preliminary, L = %.1f fb^{-1} @ #sqrt{s} = 8 TeV" % (5.8));
            metLabel.AddText(metbin_latex[metbin])         
            mytext.SetFillStyle(0)
            mytext.SetBorderSize(0)
            mytext.SetTextFont(42)
            mytext.SetTextAlign(13)
            
            metLabel.SetFillStyle(0)
            metLabel.SetBorderSize(0)
            metLabel.SetTextFont(42)
            metLabel.SetTextAlign(13)
            
            channelLabel.SetFillStyle(0)
            channelLabel.SetBorderSize(0)
            channelLabel.SetTextFont(42)
            channelLabel.SetTextAlign(13)
            mytext.Draw()
            metLabel.Draw()
            channelLabel.Draw()
            
            prefix = 'EPlusJets_electron'
            if analysis == 'MuPlusJets':
                prefix = 'MuPlusJets_muon'
            elif analysis == 'EPlusJets':
                prefix = 'EPlusJets_electron'
            else:
                prefix = analysis
            plotting.saveAs(c, prefix + '_AbsEta_fit_' + measurement + '_' + metbin + '_' + bjetbin,
                            outputFormat_plots,
                            savePath + measurement)
            c = TCanvas(prefix + '_AbsEta_templates_' + metbin + bjetbin + measurement, "Differential cross section", 1600, 1200)
#            max_y = plot_templates['TTJet'].GetMaximum()
#            plot_templates['TTJet'].SetMaximum(max_y * 1.5)
#            plot_templates['TTJet'].Draw('hist')
            max_y = plot_templates['Signal'].GetMaximum()
            plot_templates['Signal'].SetMaximum(max_y * 1.5)
            plot_templates['Signal'].Draw('hist')
            plot_templates[qcdLabel].Draw('hist same')
#            plot_templates['DYJetsToLL'].Draw('hist same')
#            plot_templates['W+Jets'].Draw('hist same')
            plot_templates['V+Jets'].Draw('hist same')
#            plot_templates['SingleTop'].Draw('hist same')
            
            legend = plotting.create_legend(x0=0.696, y0 = 0.95, x1=0.94, y1=0.65)
            legend.AddEntry(plot_templates['Signal'], 't#bar{t} + Single-Top', 'L')
#            legend.AddEntry(plot_templates['TTJet'], 't#bar{t}', 'L')
#            legend.AddEntry(plot_templates['SingleTop'], 'Single-Top', 'L')
            legend.AddEntry(plot_templates['V+Jets'], 'V+Jets', 'L')
#            legend.AddEntry(plot_templates['W+Jets'], 'W#rightarrowl#nu', 'L')
#            legend.AddEntry(plot_templates['DYJetsToLL'], 'Z/#gamma*#rightarrowl^{+}l^{-}', 'L')
            legend.AddEntry(plot_templates[qcdLabel], 'QCD/#gamma + jets', 'L')
            
    #        legend.AddEntry(plots['Di-Boson'], 'VV + X', 'F')
            legend.Draw()
            mytext.Draw()
            metLabel.Draw()
            channelLabel.Draw()
    
            plotting.saveAs(c, prefix + '_AbsEta_templates_' + measurement + '_' + metbin + '_' + bjetbin,
                            outputFormat_plots,
                            savePath + measurement)

def plotCrossSectionResults(result, analysis, compareToSystematic=False):
    
    arglist = array('d', [0, 25, 45, 70, 100, 150, 200])
    c = TCanvas("test", "Differential cross section", 1600, 1200)
    plot = TH1F("measurement_" + bjetbin, 'Differential cross section; E_{T}^{miss} [GeV];#frac{#partial#sigma}{dE_{T}^{miss}} [pb GeV^{-1}]', len(arglist) - 1, arglist)
    plotMADGRAPH = TH1F("measurement_MC_MADGRAPH" + bjetbin, 'Differential cross section; E_{T}^{miss} [GeV];#frac{#partial#sigma}{dE_{T}^{miss}}', len(arglist) - 1, arglist)
    plotPOWHEG = TH1F("measurement_MC_POWHEG" + bjetbin, 'Differential cross section; E_{T}^{miss} [GeV];#frac{#partial#sigma}{dE_{T}^{miss}}', len(arglist) - 1, arglist)
#    plotPYTHIA6 = TH1F("measurement_MC_PYTHIA6" + bjetbin, 'Differential cross section; E_{T}^{miss} [GeV];#frac{#partial#sigma}{dE_{T}^{miss}}', len(arglist) - 1, arglist)
    plotnoCorr_mcatnlo = TH1F("measurement_MC_MCatNLO" + bjetbin, 'Differential cross section; E_{T}^{miss} [GeV];#frac{#partial#sigma}{dE_{T}^{miss}}', len(arglist) - 1, arglist)
    plot.GetXaxis().SetTitleSize(0.05)
    plot.GetYaxis().SetTitleSize(0.05)
    plot.SetMinimum(0)
    plot.SetMaximum(80)
    plot.SetMarkerSize(2)
    plot.SetMarkerStyle(20)
    plotMADGRAPH.SetLineColor(kRed + 1)
    plotMADGRAPH.SetLineStyle(7)
    plotPOWHEG.SetLineColor(kBlue)
    plotPOWHEG.SetLineStyle(7)
#    plotPYTHIA6.SetLineColor(kGreen + 4)
#    plotPYTHIA6.SetLineStyle(7)
    plotnoCorr_mcatnlo.SetLineColor(kMagenta + 3)
    plotnoCorr_mcatnlo.SetLineStyle(7)
    
    legend = plotting.create_legend()
    legend.AddEntry(plot, 'data', 'P')
    if compareToSystematic:
        legend.AddEntry(plotMADGRAPH, 't#bar{t} (Q^{2} down)', 'l')
        legend.AddEntry(plotPOWHEG, 't#bar{t} (Q^{2} up)', 'l')
#        legend.AddEntry(plotPYTHIA6, 't#bar{t} (matching down)', 'l')
        legend.AddEntry(plotnoCorr_mcatnlo, 't#bar{t} (matching up)', 'l')
    else:
        legend.AddEntry(plotMADGRAPH, 't#bar{t} (MADGRAPH)', 'l')
        legend.AddEntry(plotPOWHEG, 't#bar{t} (POWHEG)', 'l')
#        legend.AddEntry(plotPYTHIA6, 't#bar{t} (PYTHIA6)', 'l')
        legend.AddEntry(plotnoCorr_mcatnlo, 't#bar{t} (MC@NLO)', 'l')
    
    bin_i = 1
    for metbin in metbins:
#        width = metbin_widths[metbin]
        scale = 1# / width
        centralresult = result[metbin]['central']
        plot.SetBinContent(bin_i, centralresult['value'] * scale)
        if compareToSystematic:
            plotMADGRAPH.SetBinContent(bin_i, result[metbin]['TTJet scale -']['MADGRAPH'] * scale)
            plotPOWHEG.SetBinContent(bin_i, result[metbin]['TTJet scale +']['MADGRAPH'] * scale)
#            plotPYTHIA6.SetBinContent(bin_i, result[metbin]['TTJet matching -']['MADGRAPH'] * scale)
            plotnoCorr_mcatnlo.SetBinContent(bin_i, result[metbin]['TTJet matching +']['MADGRAPH'] * scale)
        else:
            plotMADGRAPH.SetBinContent(bin_i, centralresult['MADGRAPH'] * scale)
            plotPOWHEG.SetBinContent(bin_i, centralresult['POWHEG'] * scale)
#            plotPYTHIA6.SetBinContent(bin_i, centralresult['PYTHIA6'] * scale)
            plotnoCorr_mcatnlo.SetBinContent(bin_i, centralresult['MCatNLO'] * scale)
        bin_i += 1
    plotAsym = TGraphAsymmErrors(plot)
    plotStatErr = TGraphAsymmErrors(plot)      
    bin_i = 0
    for metbin in metbins:
#        width = metbin_widths[metbin]
        scale = 1# / width
        centralresult = result[metbin]['central']
        uncertainty = calculateTotalUncertainty(result[metbin], compareToSystematic)
        uncertainty['Total+']['value'], uncertainty['Total-']['value'] = symmetriseErrors(uncertainty['Total+']['value'], uncertainty['Total-']['value'])
        error_up = sqrt(centralresult['error'] ** 2 + uncertainty['Total+']['value'] ** 2) * scale
        error_down = sqrt(centralresult['error'] ** 2 + uncertainty['Total-']['value'] ** 2) * scale
        plotAsym.SetPointEYhigh(bin_i, error_up)
        plotAsym.SetPointEYlow(bin_i, error_down)
        plotStatErr.SetPointEYhigh(bin_i, centralresult['error'])
        plotStatErr.SetPointEYlow(bin_i, centralresult['error'])
        bin_i += 1
    plotAsym.SetLineWidth(3)
#    plotStatErr.SetLineStyle(2)
    plotStatErr.SetLineWidth(3)
#    plotAsym.SetMarkerSize(2)
#    plotAsym.SetMarkerStyle(20)
    plot.Draw('P')
#    gStyle.SetErrorX(0.4)
    plotMADGRAPH.Draw('hist same')
    plotPOWHEG.Draw('hist same')
#    plotPYTHIA6.Draw('hist same')
    plotnoCorr_mcatnlo.Draw('hist same')
    gStyle.SetEndErrorSize(20)
    plotStatErr.Draw('same P')
#    gStyle.SetEndErrorSize(0)
    plotAsym.Draw('same P Z')
    legend.Draw()
    mytext = TPaveText(0.5, 0.97, 1, 1.01, "NDC")
    channelLabel = TPaveText(0.18, 0.97, 0.5, 1.01, "NDC")
    if analysis == 'EPlusJets':
        channelLabel.AddText("e, %s, %s" % ("#geq 4 jets", BjetBinsLatex[bjetbin]))
    elif analysis == 'MuPlusJets':
        channelLabel.AddText("#mu, %s, %s" % ("#geq 4 jets", BjetBinsLatex[bjetbin]))
    elif analysis == 'Combination':
        channelLabel.AddText("combined, %s, %s" % ("#geq 4 jets", BjetBinsLatex[bjetbin]))
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
    
    unfolding = '_unfolded'
    if not doBinByBinUnfolding:
        unfolding = ''
    prefix = analysis
    if compareToSystematic:
        plotting.saveAs(c, prefix + '_diff_MET_xsection_compareSystematics' + unfolding + '_' + bjetbin, outputFormat_plots, savePath)
    else:
        plotting.saveAs(c, prefix + '_diff_MET_xsection' + unfolding + '_' + bjetbin, outputFormat_plots, savePath)
        
def printNormalisedCrossSectionResult(result, analysis, toFile=True):
    global metbins
    printout = '\n'
    printout += '=' * 60
    printout = '\n'
    printout += 'Results for %s region\n' % bjetbin
    printout += '=' * 60
    printout += '\n'
    rows = {}
    header = 'Measurement'
    for metbin in metbins:
        header += '& $\sigma_{meas}$ \met bin %s~\GeV' % metbin_latex_tables[metbin]
#        width = metbin_widths[metbin]
        for source in result[metbin].keys():
            fitresult = result[metbin][source]
            scale = 100
            relativeError = getRelativeError(fitresult['value'], fitresult['error'])
#            0--25~\GeV & $\left(0.61 \pm 0.03 \text{ (fit)} \pm 0.06 \text{ (syst.)}\right) \times 10^{-2}\, \GeV^{-1}$\\ 
            text = ' $(%.2f \pm %.2f) \cdot 10^{-2}$ ' % (fitresult['value'] * scale, fitresult['error'] * scale) + '(%.2f' % (relativeError * 100) + '\%)'
#            text = ' $%.2f \pm %.2f $ ' % (fitresult['value']*scale,fitresult['error']*scale) + '(%.2f' % (relativeError * 100) + '\%)'
            if rows.has_key(source):
                rows[source].append(text)
            else:
                rows[source] = [source, text]
            
    header += '\\\\ \n'
    printout += header
    printout += '\hline\n'
    for item in rows['central']:
        printout += item + '&'
    printout = printout.rstrip('&')
    printout += '\\\\ \n'
    
    for source in sorted(rows.keys()):
        if source == 'central':
            continue
        for item in rows[source]:
            printout += item + '&'
        printout = printout.rstrip('&')
        printout += '\\\\ \n'
    printout += '\hline \n\n'
        
    if toFile:
        unfolding = '_unfolded'
        if not doBinByBinUnfolding:
            unfolding = ''
        output_file = open(savePath + analysis + '_normalised_crosssection_result' + unfolding + '_' + bjetbin + '.tex', 'w')
        output_file.write(printout)
        output_file.close()
    else:
        print printout
        
def printNormalisedCrossSectionResultsForTTJetWithUncertanties(result, analysis, toFile=True):
    global metbins, doBinByBinUnfolding
    printout = '\n'
    printout += '=' * 60
    printout = '\n'
    printout += 'Results for %s region\n' % bjetbin
    printout += '=' * 60
    printout += '\n'
#    rows = {}
    printout += '\met bin & $\sigma{meas}$ \\\\ \n'
    printout += '\hline\n'
    uncertainties = {}
    header = 'Uncertainty'
    for metbin in metbins:
        header += '&\met bin %s' %  metbin_latex_tables[metbin]
#        width = metbin_widths[metbin]
        centralresult = result[metbin]['central']
        uncertainty = calculateTotalUncertainty(result[metbin])
        uncertainty['Total+']['value'], uncertainty['Total-']['value'] = symmetriseErrors(uncertainty['Total+']['value'], uncertainty['Total-']['value'])
        scale = 100# / width
        formatting = (metbin_latex_tables[metbin], centralresult['value'] * scale,
                      centralresult['error'] * scale, uncertainty['Total+']['value'] * scale,
                      uncertainty['Total-']['value'] * scale)
        text = '%s & $%.2f \pm %.2f (fit)^{+%.2f}_{-%.2f} (sys) \cdot 10^{-2}$\\\\ \n' % formatting
        if doSymmetricErrors:
            formatting = (metbin_latex_tables[metbin], centralresult['value'] * scale,
                      centralresult['error'] * scale, uncertainty['Total+']['value'] * scale)
            text = '%s & $\\left(%.2f \\pm %.2f \\text{ (fit)} \pm %.2f \\text{ (syst.)}\\right) \\times 10^{-2}\, \\GeV^{-1}$\\\\ \n' % formatting
            #0--25~\GeV & $\left(0.61 \pm 0.03 \text{ (fit)} \pm 0.06 \text{ (syst.)}\right) \times 10^{-2}\, \GeV^{-1}$\\ 
        printout += text
        for source in uncertainty.keys():
            unc_result = uncertainty[source]
            if not uncertainties.has_key(source):
                if source in metsystematics_sources:
                    uncertainties[source] = metsystematics_sources_latex[source] + ' & '
                else:
                    uncertainties[source] = source + ' & '
            relativeError = getRelativeError(centralresult['value'], unc_result['value'])
#            text = ' $(%.2f \pm %.2f) \cdot 10^{-2} $ ' % (unc_result['value']*scale,unc_result['error']*scale) + '(%.2f' % (relativeError * 100) + '\%) &'
            text = '%.2f' % (relativeError * 100) + '\% &'
#            text = ' $%.2f \pm %.2f $ ' % (unc_result['value']*scale,unc_result['error']*scale) + '(%.2f' % (relativeError * 100) + '\%) &'
            uncertainties[source] += text
        
    if toFile:
        unfolding = '_unfolded'
        if not doBinByBinUnfolding:
            unfolding = ''
        output_file = open(savePath + analysis + '_normalised_crosssection_main_result' + unfolding + '_' + bjetbin + '.tex', 'w')
        output_file.write(printout)
        header += '\\\\ \n'
        output_file.write(header)
        for source in sorted(uncertainties.keys()):
            value = uncertainties[source]
            value = value.rstrip('&')
            value += '\\\\ \n'
            output_file.write(value)
        output_file.close()
    else:
        print printout
        
def plotNormalisedCrossSectionResults(result, analysis, compareToSystematic=False):
    
    arglist = array('d', [0, 25, 45, 70, 100, 150, 200])
    c = TCanvas("test", "Differential cross section", 1600, 1200)
    plot = TH1F("measurement_" + bjetbin, 'Differential cross section; E_{T}^{miss} [GeV];#frac{1}{#sigma} #frac{d#sigma}{dE_{T}^{miss}} [GeV^{-1}]', len(arglist) - 1, arglist)
    plotMADGRAPH = TH1F("measurement_MC_MADGRAPH" + bjetbin, 'Differential cross section; E_{T}^{miss} [GeV];#frac{1}{#sigma} #frac{d#sigma}{dE_{T}^{miss}} [GeV^{-1}]', len(arglist) - 1, arglist)
    plotPOWHEG = TH1F("measurement_MC_POWHEG" + bjetbin, 'Differential cross section; E_{T}^{miss} [GeV];#frac{1}{#sigma} #frac{d#sigma}{dE_{T}^{miss}} [GeV^{-1}]', len(arglist) - 1, arglist)
#    plotPYTHIA6 = TH1F("measurement_MC_PYTHIA6" + bjetbin, 'Differential cross section; E_{T}^{miss} [GeV];#frac{1}{#sigma} #frac{d#sigma}{dE_{T}^{miss}} [GeV^{-1}]', len(arglist) - 1, arglist)
    plotnoCorr_mcatnlo = TH1F("measurement_MC_MCatNLO" + bjetbin, 'Differential cross section; E_{T}^{miss} [GeV];#frac{1}{#sigma} #frac{d#sigma}{dE_{T}^{miss}} [GeV^{-1}]', len(arglist) - 1, arglist)
    plot.GetXaxis().SetTitleSize(0.05)
    plot.GetYaxis().SetTitleSize(0.05)
    plot.SetMinimum(0)
    plot.SetMaximum(0.02)
    plot.SetMarkerSize(2)
    plot.SetMarkerStyle(20)
    plotMADGRAPH.SetLineColor(kRed + 1)
#    plotMADGRAPH.SetLineWidth(2)
    plotMADGRAPH.SetLineStyle(7)
    plotPOWHEG.SetLineColor(kBlue)
    plotPOWHEG.SetLineStyle(7)
#    plotPOWHEG.SetLineWidth(2)
#    plotPYTHIA6.SetLineColor(kGreen + 4)
#    plotPYTHIA6.SetLineStyle(7)
#    plotPYTHIA6.SetLineWidth(2)
    plotnoCorr_mcatnlo.SetLineColor(kMagenta + 3)
#    plotnoCorr_mcatnlo.SetLineWidth(2)
    plotnoCorr_mcatnlo.SetLineStyle(7)
    legend = plotting.create_legend(x0=0.6, y1=0.5)
    legend.AddEntry(plot, 'data', 'P')
    if compareToSystematic:
        legend.AddEntry(plotMADGRAPH, 't#bar{t} (Q^{2} down)', 'l')
        legend.AddEntry(plotPOWHEG, 't#bar{t} (Q^{2} up)', 'l')
#        legend.AddEntry(plotPYTHIA6, 't#bar{t} (matching down)', 'l')
        legend.AddEntry(plotnoCorr_mcatnlo, 't#bar{t} (matching up)', 'l')
    else:
        legend.AddEntry(plotMADGRAPH, 't#bar{t} (MADGRAPH)', 'l')
        legend.AddEntry(plotPOWHEG, 't#bar{t} (POWHEG)', 'l')
#        legend.AddEntry(plotPYTHIA6, 't#bar{t} (PYTHIA6)', 'l')
        legend.AddEntry(plotnoCorr_mcatnlo, 't#bar{t} (MC@NLO)', 'l')
    bin_i = 1
    for metbin in metbins:
#        width = metbin_widths[metbin]
        scale = 1# / width
        centralresult = result[metbin]['central']
        plot.SetBinContent(bin_i, centralresult['value'] * scale)
        if compareToSystematic:
            plotMADGRAPH.SetBinContent(bin_i, result[metbin]['TTJet scale -']['MADGRAPH'] * scale)
            plotPOWHEG.SetBinContent(bin_i, result[metbin]['TTJet scale +']['MADGRAPH'] * scale)
#            plotPYTHIA6.SetBinContent(bin_i, result[metbin]['TTJet matching -']['MADGRAPH'] * scale)
            plotnoCorr_mcatnlo.SetBinContent(bin_i, result[metbin]['TTJet matching +']['MADGRAPH'] * scale)
        else:
            plotMADGRAPH.SetBinContent(bin_i, centralresult['MADGRAPH'] * scale)
            plotPOWHEG.SetBinContent(bin_i, centralresult['POWHEG'] * scale)
#            plotPYTHIA6.SetBinContent(bin_i, centralresult['PYTHIA6'] * scale)
            plotnoCorr_mcatnlo.SetBinContent(bin_i, centralresult['MCatNLO'] * scale)
        bin_i += 1    
    plotAsym = TGraphAsymmErrors(plot)
    plotStatErr = TGraphAsymmErrors(plot)
    bin_i = 0
    for metbin in metbins:
#        width = metbin_widths[metbin]
        scale = 1# / width
        centralresult = result[metbin]['central']
        uncertainty = calculateTotalUncertainty(result[metbin], compareToSystematic)
        uncertainty['Total+']['value'], uncertainty['Total-']['value'] = symmetriseErrors(uncertainty['Total+']['value'], uncertainty['Total-']['value'])
        error_up = sqrt(centralresult['error'] ** 2 + uncertainty['Total+']['value'] ** 2) * scale
        error_down = sqrt(centralresult['error'] ** 2 + uncertainty['Total-']['value'] ** 2) * scale
        if DEBUG:
            print centralresult['error'], uncertainty['Total+']['value'], error_up
            print centralresult['error'], uncertainty['Total-']['value'], error_down
        plotStatErr.SetPointEYhigh(bin_i, centralresult['error'])
        plotStatErr.SetPointEYlow(bin_i, centralresult['error'])
        plotAsym.SetPointEYhigh(bin_i, error_up)
        plotAsym.SetPointEYlow(bin_i, error_down)
        bin_i += 1 
    plotAsym.SetLineWidth(3)
#    plotStatErr.SetLineStyle(2)
    plotStatErr.SetLineWidth(3)
    
    plot.Draw('P')
#    gStyle.SetErrorX(0.4)
    plotMADGRAPH.Draw('hist same')
    plotPOWHEG.Draw('hist same')
#    plotPYTHIA6.Draw('hist same')
    plotnoCorr_mcatnlo.Draw('hist same')
    gStyle.SetEndErrorSize(20)
    plotStatErr.Draw('same P')
#    gStyle.SetEndErrorSize(0)
    plotAsym.Draw('same P Z')
    legend.Draw()
    mytext = TPaveText(0.5, 0.97, 1, 1.01, "NDC")
    channelLabel = TPaveText(0.18, 0.97, 0.5, 1.01, "NDC")
    if analysis == 'EPlusJets':
        channelLabel.AddText("e, %s, %s" % ("#geq 4 jets", BjetBinsLatex[bjetbin]))
    elif analysis == 'MuPlusJets':
        channelLabel.AddText("#mu, %s, %s" % ("#geq 4 jets", BjetBinsLatex[bjetbin]))
    elif analysis == 'Combination':
        channelLabel.AddText("combined, %s, %s" % ("#geq 4 jets", BjetBinsLatex[bjetbin]))
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
    unfolding = '_unfolded'
    if not doBinByBinUnfolding:
        unfolding = ''
    if compareToSystematic:
        plotting.saveAs(c, analysis + '_diff_MET_norm_xsection_compareSystematics' + unfolding + '_' + bjetbin, outputFormat_plots, savePath)
    else:
        plotting.saveAs(c, analysis + '_diff_MET_norm_xsection' + unfolding + '_' + bjetbin, outputFormat_plots, savePath)

def plotNormalisedCrossSectionResultsAllChannels(result_electron, result_muon, result_combined):
    arglist_electron = array('d', [0, 15, 45, 60, 100, 140, 180])
    arglist_muon = array('d', [0, 35, 45, 80, 100, 160, 200])
    arglist_combined = array('d', [0, 25, 45, 70, 100, 150, 200])
    c = TCanvas("test", "Differential cross section", 1600, 1200)
    plot_electron = TH1F("electron_measurement_" + bjetbin, 'Differential cross section; E_{T}^{miss} [GeV];#frac{1}{#sigma} #frac{d#sigma}{dE_{T}^{miss}} [GeV^{-1}]', len(arglist_electron) - 1, arglist_electron)
    plot_muon = TH1F("muon_measurement_" + bjetbin, 'Differential cross section; E_{T}^{miss} [GeV];#frac{1}{#sigma} #frac{d#sigma}{dE_{T}^{miss}} [GeV^{-1}]', len(arglist_muon) - 1, arglist_muon)
    plot_combined = TH1F("combined_measurement_" + bjetbin, 'Differential cross section; E_{T}^{miss} [GeV];#frac{1}{#sigma} #frac{d#sigma}{dE_{T}^{miss}} [GeV^{-1}]', len(arglist_combined) - 1, arglist_combined)
    plotMADGRAPH = TH1F("measurement_MC_MADGRAPH" + bjetbin, 'Differential cross section; E_{T}^{miss} [GeV];#frac{#partial#sigma}{dE_{T}^{miss}}', len(arglist_combined) - 1, arglist_combined)
    plot_combined.GetXaxis().SetTitleSize(0.05)
    plot_combined.GetYaxis().SetTitleSize(0.05)
    plot_combined.SetMinimum(0)
    plot_combined.SetMaximum(0.02)
    plot_combined.SetMarkerSize(2)
    plot_combined.SetMarkerStyle(20)
    
    plot_electron.SetMarkerStyle(21);
    plot_electron.SetMarkerColor(4)
    plot_electron.SetLineColor(4)
    plot_electron.SetMarkerSize(2)
    
    plot_muon.SetMarkerStyle(22);
    plot_muon.SetMarkerColor(kAzure - 9)
    plot_muon.SetLineColor(7)
    plot_muon.SetMarkerSize(2)

    plotMADGRAPH.SetLineColor(kRed + 1)

    legend = plotting.create_legend(x0=0.6, y1=0.5)
    legend.AddEntry(plot_electron, 'e+jets', 'P')
    legend.AddEntry(plot_muon, '#mu+jets', 'P')
    legend.AddEntry(plot_combined, 'combined', 'P')
    legend.AddEntry(plotMADGRAPH, 'MADGRAPH', 'l')
    bin_i = 1
    for metbin in metbins:
#        width = metbin_widths[metbin]
        scale = 1# / width
        centralresult_electron = result_electron[metbin]['central']
        centralresult_muon = result_muon[metbin]['central']
        centralresult_combined = result_combined[metbin]['central']
        plot_electron.SetBinContent(bin_i, centralresult_electron['value'] * scale)
        plot_muon.SetBinContent(bin_i, centralresult_muon['value'] * scale)
        plot_combined.SetBinContent(bin_i, centralresult_combined['value'] * scale)
        plotMADGRAPH.SetBinContent(bin_i, centralresult_combined['MADGRAPH'] * scale)
        bin_i += 1    
    plotAsym_electron = TGraphAsymmErrors(plot_electron)
    plotStatErr_electron = TGraphAsymmErrors(plot_electron)
    plotAsym_muon = TGraphAsymmErrors(plot_muon)
    plotStatErr_muon = TGraphAsymmErrors(plot_muon)
    plotAsym_combined = TGraphAsymmErrors(plot_combined)
    plotStatErr_combined = TGraphAsymmErrors(plot_combined)
    
    plotAsym_electron.SetLineColor(4)
    plotAsym_muon.SetLineColor(kAzure - 9)
    
#    plotStatErr_electron.SetLineStyle(2)
#    plotStatErr_muon.SetLineStyle(2)
#    plotStatErr_combined.SetLineStyle(2)
    
    plotAsym_electron.SetLineWidth(3)
    plotStatErr_electron.SetLineWidth(3)
    plotAsym_muon.SetLineWidth(3)
    plotStatErr_muon.SetLineWidth(3)
    plotAsym_combined.SetLineWidth(3)
    plotStatErr_combined.SetLineWidth(3)
    bin_i = 0
    for metbin in metbins:
#        width = metbin_widths[metbin]
        scale = 1# / width
        centralresult_electron = result_electron[metbin]['central']
        centralresult_muon = result_muon[metbin]['central']
        centralresult_combined = result_combined[metbin]['central']
        
        uncertainty_electron = calculateTotalUncertainty(result_electron[metbin])
        uncertainty_electron['Total+']['value'], uncertainty_electron['Total-']['value'] = symmetriseErrors(uncertainty_electron['Total+']['value'], uncertainty_electron['Total-']['value'])
        error_up_electron = sqrt(centralresult_electron['error'] ** 2 + uncertainty_electron['Total+']['value'] ** 2) * scale
        error_down_electron = sqrt(centralresult_electron['error'] ** 2 + uncertainty_electron['Total-']['value'] ** 2) * scale
        
        uncertainty_muon = calculateTotalUncertainty(result_muon[metbin])
        uncertainty_muon['Total+']['value'], uncertainty_muon['Total-']['value'] = symmetriseErrors(uncertainty_muon['Total+']['value'], uncertainty_muon['Total-']['value'])
        error_up_muon = sqrt(centralresult_muon['error'] ** 2 + uncertainty_muon['Total+']['value'] ** 2) * scale
        error_down_muon = sqrt(centralresult_muon['error'] ** 2 + uncertainty_muon['Total-']['value'] ** 2) * scale
        
        uncertainty_combined = calculateTotalUncertainty(result_combined[metbin])
        uncertainty_combined['Total+']['value'], uncertainty_combined['Total-']['value'] = symmetriseErrors(uncertainty_combined['Total+']['value'], uncertainty_combined['Total-']['value'])
        error_up_combined = sqrt(centralresult_combined['error'] ** 2 + uncertainty_combined['Total+']['value'] ** 2) * scale
        error_down_combined = sqrt(centralresult_combined['error'] ** 2 + uncertainty_combined['Total-']['value'] ** 2) * scale

        plotAsym_electron.SetPointEYhigh(bin_i, error_up_electron)
        plotAsym_electron.SetPointEYlow(bin_i, error_down_electron)
        
        plotAsym_muon.SetPointEYhigh(bin_i, error_up_muon)
        plotAsym_muon.SetPointEYlow(bin_i, error_down_muon)
        
        plotAsym_combined.SetPointEYhigh(bin_i, error_up_combined)
        plotAsym_combined.SetPointEYlow(bin_i, error_down_combined)
        
        plotStatErr_electron.SetPointEYhigh(bin_i, centralresult_electron['error'])
        plotStatErr_electron.SetPointEYlow(bin_i, centralresult_electron['error'])
        
        plotStatErr_muon.SetPointEYhigh(bin_i, centralresult_muon['error'])
        plotStatErr_muon.SetPointEYlow(bin_i, centralresult_muon['error'])
        
        plotStatErr_combined.SetPointEYhigh(bin_i, centralresult_combined['error'])
        plotStatErr_combined.SetPointEYlow(bin_i, centralresult_combined['error'])
        
        
        bin_i += 1 
    plot_combined.Draw('P')
#    gStyle.SetErrorX(0.4)
    plotMADGRAPH.Draw('hist same')
    gStyle.SetEndErrorSize(20)
    plotStatErr_electron.Draw('same P')
    plotStatErr_muon.Draw('same P')
    plotStatErr_combined.Draw('same P')
#    gStyle.SetEndErrorSize(0)
    plotAsym_electron.Draw('same P Z')
    plotAsym_muon.Draw('same P Z')
    plotAsym_combined.Draw('same P Z')
    legend.Draw()
    mytext = TPaveText(0.5, 0.97, 1, 1.01, "NDC")
    channelLabel = TPaveText(0.18, 0.97, 0.5, 1.01, "NDC")
    channelLabel.AddText("combined, %s, %s" % ("#geq 4 jets", BjetBinsLatex[bjetbin]))
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
    #channelLabel.Draw()
    unfolding = '_unfolded'
    if not doBinByBinUnfolding:
        unfolding = ''
    plotting.saveAs(c, 'AllChannels_diff_MET_norm_xsection' + unfolding + '_' + bjetbin, outputFormat_plots, savePath)
    
def getMeasurementAndErrors(input_result):
    result = {}
#    skipErrors = ['PDFWeights_%d' % index for index in range(1, 45)]
#    skipErrors.append('central')#skip central value!
    for metbin in metbins:
        result[metbin] = {}
        current = input_result[metbin]
        central = current['central']
        result[metbin]['measurement'] = central
        uncertainties = calculateTotalUncertainty(current)
        result[metbin].update(uncertainties)    
        
    return result
        
def saveAsJSON(result, filename):
    unfolding = '_unfolded'
    if not doBinByBinUnfolding:
        unfolding = ''
    #remove fit from list
    for metbin in metbins:
        result[metbin]['measurement']['fit'] = 'cannot encode'
    output_file = open(savePath + filename + unfolding + '_' + bjetbin + '_JSON.txt', 'w')
    output_file.write(json.dumps(result, indent=4, skipkeys=True))
    output_file.close()

def getCorrections(analysis):
    from purityAndStability_METbins import fileTemplate
    inputFileName = fileTemplate % (analysis, bjetbin)
    print 'Loading correction factors from:'
    print inputFileName
    return fileutils.readJSONFile(inputFileName)

def loadAcceptanceCorrections(analysis):
    temp = 'data/acceptanceFactors/acceptanceFactors_%s_2orMoreBtags_JSON.txt'
    inputFileName = temp % analysis
    print 'Loading acceptance correction factors from:'
    print inputFileName
    return fileutils.readJSONFile(inputFileName)

def loadContaminationCorrections(analysis):
    temp = 'data/contaminationFactors/contaminationFactors_%s_2orMoreBtags_JSON.txt'
    inputFileName = temp % analysis
    print 'Loading contamination correction factors from:'
    print inputFileName
    return fileutils.readJSONFile(inputFileName)

def setMETSystematics(metType):
    global metsystematics_sources, metsystematics_sources_latex
    prefix = ''
    if metType == 'patMETsPFlow':
        prefix = 'patPFMet'
    elif metType == 'patType1CorrectedPFMet':
        prefix = 'patType1CorrectedPFMet'
    else:
        prefix = 'patType1p2CorrectedPFMet'
    metsystematics_sources = [
                              prefix + "ElectronEnUp",
        prefix + "ElectronEnDown",
        prefix + "MuonEnUp",
        prefix + "MuonEnDown",
        prefix + "TauEnUp",
        prefix + "TauEnDown",
        prefix + "JetResUp",
        prefix + "JetResDown",
        prefix + "JetEnUp",
        prefix + "JetEnDown",
        prefix + "UnclusteredEnUp",
        prefix + "UnclusteredEnDown"
                      ]

    metsystematics_sources_latex = {
                prefix + "ElectronEnUp":'Electron energy $+1\sigma$',
                prefix + "ElectronEnDown":'Electron energy $-1\sigma$',
                prefix + "MuonEnUp":'Muon energy $+1\sigma$',
                prefix + "MuonEnDown":'Muon energy $-1\sigma$',
                prefix + "TauEnUp":'Tau energy $+1\sigma$',
                prefix + "TauEnDown":'Tau energy $-1\sigma$',
                prefix + "JetResUp":'Jet resolution $+1\sigma$',
                prefix + "JetResDown":'Jet resolution $-1\sigma$',
                prefix + "JetEnUp":'Jet energy $+1\sigma$',
                prefix + "JetEnDown":'Jet energy $-1\sigma$',
                prefix + "UnclusteredEnUp":'Unclustered energy $+1\sigma$',
                prefix + "UnclusteredEnDown":'Unclustered energy $-1\sigma$'
                      }  
    
def symmetriseErrors(error1, error2):
    if not doSymmetricErrors:
        return error1, error2
    
    error1, error2 = abs(error1), abs(error2)
    if error1 > error2:
        return error1, error1
    
    return error2, error2
      
if __name__ == '__main__':
    DEBUG = False
    completeAnalysisTimer = Timer()
    gROOT.SetBatch(True)
    gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    RooMsgService.instance().setGlobalKillBelow(RooFit.FATAL)
    
    plotting.setStyle()
    
    parser = OptionParser()
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                  help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                  help="set MET input for analysis.")
    parser.add_option("-u", "--unfolding",
                  action="store_false", dest="unfolding", default=True,
                  help="use unfolding of MET")
    parser.add_option("-r", "--rooFit",
                  action="store_true", dest="useRooFit", default=False,
                  help="Use RooFit for fitting")
    parser.add_option("-t", "--test",
                  action="store_true", dest="test", default=False,
                  help="Test analysis on first met bin only")
    parser.add_option("-c", "--constrain", dest="constrain", default=' ', #default='QCD,Z/W',
                  help="Sets which constrains to use. Constrains separated by commas: QCD, Z/W, ZJets, WJets, VV")
    parser.add_option("-a", "--analysisType", dest="analysisType", default='EPlusJets',
                  help="set analysis type: EPlusJets or MuPlusJets")
    #more for: plot templates, plot fits
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
                        'type1p2':'patType1p2CorrectedPFMet'
                        }
    
    (options, args) = parser.parse_args()
    bjetbin = translateOptions[options.bjetbin]
    metType = translateOptions[options.metType]
    doBinByBinUnfolding = options.unfolding
    use_RooFit = options.useRooFit
    
    setMETSystematics(metType)

    from purityAndStability_METbins import fileTemplate
    inputFileName = fileTemplate % ('EPlusJets', bjetbin)
    correctionFactors, acceptanceFactors, contaminationFactors = {}, {}, {}
#    correctionFactors['EPlusJets'] = getCorrections('EPlusJets')
#    correctionFactors['MuPlusJets'] = getCorrections('MuPlusJets')
#    acceptanceFactors['EPlusJets'] = loadAcceptanceCorrections('EPlusJets')
#    acceptanceFactors['MuPlusJets'] = loadAcceptanceCorrections('MuPlusJets')
#    contaminationFactors['EPlusJets'] = loadContaminationCorrections('EPlusJets')
#    contaminationFactors['MuPlusJets'] = loadContaminationCorrections('MuPlusJets')
    test = options.test
    constrains[qcdLabel]['enabled'] = ('QCD' in options.constrain)
    constrains['ratio_Z_W']['enabled'] = ('Z/W' in options.constrain)
    constrains['W+Jets']['enabled'] = ('WJets' in options.constrain)
    constrains['DYJetsToLL']['enabled'] = ('ZJets' in options.constrain)
#    constrains['Di-Boson']['enabled'] = ('VV' in options.constrain)

    savePath = "/storage/results/plots/AN-13-015_V1/DiffMETMeasurement/unfolding/%s/" % metType    
    if test:
        metbins = ['25-45']
        savePath = "/storage/results/plots/testing2/%s/" % metType    
        if use_RooFit:
            savePath = "/storage/results/plots/testing/%s/" % metType
#    savePath = "/storage/results/plots/testing2/%s/" % metType
#    doBinByBinUnfolding = True
    print colorstr('Analysis options:', 'DARK_RED')
    print colorstr('B-tag bin:', 'RED'), bjetbin
    print colorstr('MET type:', 'RED'), metType
    print colorstr('Use unfolding:', 'RED'), doBinByBinUnfolding
    print colorstr('Test only:', 'RED'), test
    print colorstr('Using RooFit:', 'RED'), use_RooFit
    print 'Constrains on fit:', options.constrain
    for sample, constrain in constrains.iteritems():
        print sample, ': enabled = ' + str(constrain['enabled']) + ', value = ' + str(constrain['value'] * 100) + '%'
    print 'Results will be saved to:'
    print savePath
    
    normalisation_result_electron, normalisation_result_muon, normalisation_result_combined, normalisation_result_simultaniousFit = NormalisationAnalysis()
    
    printNormalisationResult(normalisation_result_electron, 'EPlusJets')
    printNormalisationResultsForTTJetWithUncertanties(normalisation_result_electron, 'EPlusJets')
    plotNormalisationResults(normalisation_result_electron, 'EPlusJets')
    
    printNormalisationResult(normalisation_result_muon, 'MuPlusJets')
    printNormalisationResultsForTTJetWithUncertanties(normalisation_result_muon, 'MuPlusJets')
    plotNormalisationResults(normalisation_result_muon, 'MuPlusJets')
    
    printNormalisationResult(normalisation_result_combined, 'Combination')
    printNormalisationResultsForTTJetWithUncertanties(normalisation_result_combined, 'Combination')
#    plotNormalisationResults(normalisation_result_combined, 'Combination')
    
    crosssection_result_electron = CrossSectionAnalysis(normalisation_result_electron, 'EPlusJets')
    printCrossSectionResult(crosssection_result_electron, 'EPlusJets')
    printCrossSectionResultsForTTJetWithUncertanties(crosssection_result_electron, 'EPlusJets')
    plotCrossSectionResults(crosssection_result_electron, 'EPlusJets')
    plotCrossSectionResults(crosssection_result_electron, 'EPlusJets', compareToSystematic=True)
    
    crosssection_result_muon = CrossSectionAnalysis(normalisation_result_muon, 'MuPlusJets')
    printCrossSectionResult(crosssection_result_muon, 'MuPlusJets')
    printCrossSectionResultsForTTJetWithUncertanties(crosssection_result_muon, 'MuPlusJets')
    plotCrossSectionResults(crosssection_result_muon, 'MuPlusJets')
    plotCrossSectionResults(crosssection_result_muon, 'MuPlusJets', compareToSystematic=True)
    
    crosssection_result_combined = CrossSectionAnalysis(normalisation_result_combined, 'Combination')
    printCrossSectionResult(crosssection_result_combined, 'Combination')
    printCrossSectionResultsForTTJetWithUncertanties(crosssection_result_combined, 'Combination')
    plotCrossSectionResults(crosssection_result_combined, 'Combination')
    plotCrossSectionResults(crosssection_result_combined, 'Combination', compareToSystematic=True)
#    
    gStyle.SetTitleYOffset(1.6)
    gStyle.SetPadLeftMargin(0.18)
    gStyle.SetTitleXOffset(1.0)
    normalised_crosssection_result_electron = NormalisedCrossSectionAnalysis(normalisation_result_electron)
    printNormalisedCrossSectionResult(normalised_crosssection_result_electron, 'EPlusJets')
    printNormalisedCrossSectionResultsForTTJetWithUncertanties(normalised_crosssection_result_electron, 'EPlusJets')
    plotNormalisedCrossSectionResults(normalised_crosssection_result_electron, 'EPlusJets')
    plotNormalisedCrossSectionResults(normalised_crosssection_result_electron, 'EPlusJets', compareToSystematic=True)
#    
    normalised_crosssection_result_muon = NormalisedCrossSectionAnalysis(normalisation_result_muon)
    printNormalisedCrossSectionResult(normalised_crosssection_result_muon, 'MuPlusJets')
    printNormalisedCrossSectionResultsForTTJetWithUncertanties(normalised_crosssection_result_muon, 'MuPlusJets')
    plotNormalisedCrossSectionResults(normalised_crosssection_result_muon, 'MuPlusJets')
    plotNormalisedCrossSectionResults(normalised_crosssection_result_muon, 'MuPlusJets', compareToSystematic=True)
    
    normalised_crosssection_result_combined = NormalisedCrossSectionAnalysis(normalisation_result_combined)
    printNormalisedCrossSectionResult(normalised_crosssection_result_combined, 'Combination')
    printNormalisedCrossSectionResultsForTTJetWithUncertanties(normalised_crosssection_result_combined, 'Combination')
    plotNormalisedCrossSectionResults(normalised_crosssection_result_combined, 'Combination')
    plotNormalisedCrossSectionResults(normalised_crosssection_result_combined, 'Combination', compareToSystematic=True)
    
    plotNormalisedCrossSectionResultsAllChannels(normalised_crosssection_result_electron, normalised_crosssection_result_muon, normalised_crosssection_result_combined)
    
    saveAsJSON(result=getMeasurementAndErrors(normalisation_result_electron), filename="EPlusJets_normalisation_result")
    saveAsJSON(result=getMeasurementAndErrors(crosssection_result_electron), filename="EPlusJets_crosssection_result")
    saveAsJSON(result=getMeasurementAndErrors(normalised_crosssection_result_electron), filename="EPlusJets_normalised_crosssection_result")
    
    saveAsJSON(result=getMeasurementAndErrors(normalisation_result_muon), filename="MuPlusJets_normalisation_result")
    saveAsJSON(result=getMeasurementAndErrors(crosssection_result_muon), filename="MuPlusJets_crosssection_result")
    saveAsJSON(result=getMeasurementAndErrors(normalised_crosssection_result_muon), filename="MuPlusJets_normalised_crosssection_result")
    print 'Complete Analysis in bjetbin=', bjetbin, 'finished in %.2fs' % completeAnalysisTimer.elapsedTime()
    
    
