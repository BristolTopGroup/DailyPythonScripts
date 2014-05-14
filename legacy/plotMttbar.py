from __future__ import division
from numpy import arange
from tdrStyle import *
from ROOT import *
from ROOT import kAzure, kYellow, kViolet, kRed, gROOT, kMagenta, kGreen, TLegend, THStack, TCanvas, gStyle, kGray, TH1F, gPad
#from QCDEstimation import getQCDEstimate#, estimateQCDFor
import QCDEstimation
import sys
sys.path.insert(0, '../python/')
from DataSetInfo_8TeV import *

import HistPlotter
import HistGetter
import inputFiles

from optparse import OptionParser
canvases = []
scanvases = []
setLogY = False
normalise = False
drawQCDError = False
custom_suffix = ''
#custom_suffix = '68000mb'
#custom_suffix = '64600mb'
#custom_suffix = '71400mb'
used_data = 'SingleMuon'
def plotMttbar():
    global used_data
    saveAs = HistPlotter.saveAs
    savePath = "/storage/TopQuarkGroup/results/plots/2012_v9a"
    
    performRescale = False
    HistPlotter.setStyle()
    lumi = 5814#5050.0#1959.75#1611.95
    oldLumi = 10000#5050#/(0.95**2)
#    scale = 0.15#lumi / oldLumi;
    
    outputFormats = [
                     'pdf'
                    ]
    reverseMCOrder = False
#    qcdFromData = 'topReconstruction/backgroundShape/mttbar_conversions_withMETAndAsymJets_0orMoreBtag'
    
    hists = [];
    ttbarUncertainty = 0.1
    

    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/Electron/electron_AbsEta')
    hists.append('TTbarPlusMetAnalysis/EPlusJets/QCDConversions/Electron/electron_AbsEta')
    hists.append('TTbarPlusMetAnalysis/EPlusJets/QCD non iso e+jets/Electron/electron_AbsEta')
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/QCD non iso e+jets, non iso trigger/Electron/electron_AbsEta')
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/QCDAntiID/Electron/electron_AbsEta')
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/QCDNoIsoNoID/Electron/electron_AbsEta')
#    
    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/Electron/electron_pT')
    hists.append('TTbarPlusMetAnalysis/EPlusJets/QCDConversions/Electron/electron_pT')
    hists.append('TTbarPlusMetAnalysis/EPlusJets/QCD non iso e+jets/Electron/electron_pT')
#
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/QCD non iso e+jets/Electron/electron_pfIsolation_03')
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/QCD e+jets PFRelIso/Electron/electron_pfIsolation_03')
#    
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_patType1CorrectedPFMet_bin_0-25/electron_AbsEta')
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_patType1CorrectedPFMet_bin_25-45/electron_AbsEta')
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_patType1CorrectedPFMet_bin_45-70/electron_AbsEta')
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_patType1CorrectedPFMet_bin_70-100/electron_AbsEta')
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_patType1CorrectedPFMet_bin_100-inf/electron_AbsEta')
#    
#
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/bjet_invariant_mass')
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET')
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_phi')
#
    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/MET/patMETsPFlow/MET')
    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/MET/patMETsPFlow/MET_phi')
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/MET/patType1p2CorrectedPFMet/MET')
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/MET/patType1p2CorrectedPFMet/MET_phi')
#
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/QCDConversions/MET/patType1CorrectedPFMet/MET')
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/QCD non iso e+jets/MET/patType1CorrectedPFMet/MET')
##    
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/Transverse_Mass')
#    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/Angle_lepton_MET')
#    
#    hists.append('MttbarAnalysis/ElectronPlusJets/Ref selection/FourJetChi2/m3')
#    hists.append('MttbarAnalysis/ElectronPlusJets/Ref selection/FourJetChi2/hadronicTopMass')
#    hists.append('MttbarAnalysis/ElectronPlusJets/Ref selection/FourJetChi2/hadronicWMass')
    
    hists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/Jets/N_Jets')
    
    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/Muon/muon_AbsEta')
    hists.append('TTbarPlusMetAnalysis/MuPlusJets/QCD non iso mu+jets/Muon/muon_AbsEta')
##
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/BinnedMETAnalysis/Muon_patType1CorrectedPFMet_bin_0-25/muon_AbsEta')
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/BinnedMETAnalysis/Muon_patType1CorrectedPFMet_bin_25-45/muon_AbsEta')
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/BinnedMETAnalysis/Muon_patType1CorrectedPFMet_bin_45-70/muon_AbsEta')
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/BinnedMETAnalysis/Muon_patType1CorrectedPFMet_bin_70-100/muon_AbsEta')
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/BinnedMETAnalysis/Muon_patType1CorrectedPFMet_bin_100-inf/muon_AbsEta')
###    
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/bjet_invariant_mass')
    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/MET/patMETsPFlow/MET')
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET')
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/MET/patType1p2CorrectedPFMet/MET')
    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/MET/patMETsPFlow/MET_phi')
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_phi')
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/MET/patType1p2CorrectedPFMet/MET_phi')
#    
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/QCD non iso mu+jets/MET/patMETsPFlow/MET')
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/QCD non iso mu+jets/MET/patType1CorrectedPFMet/MET')
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/QCD non iso mu+jets/MET/patType1p2CorrectedPFMet/MET')
##    
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/QCD non iso mu+jets/Muon/muon_pfIsolation_04')
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/QCD mu+jets PFRelIso/Muon/muon_pfIsolation_04')
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/Transverse_Mass')
#    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/Angle_lepton_MET')
#    
#    hists.append('MttbarAnalysis/MuonPlusJets/Ref selection/FourJetChi2/m3')
#    hists.append('MttbarAnalysis/MuonPlusJets/Ref selection/FourJetChi2/hadronicTopMass')
#    hists.append('MttbarAnalysis/MuonPlusJets/Ref selection/FourJetChi2/hadronicWMass')
    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/Jets/N_Jets')
    hists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/Muon/muon_pT')
    
    
    files = inputFiles.files
    hists = HistGetter.getHistsFromFiles(hists, files, bJetBins=[
#                                                                 '0orMoreBtag',
#                                                                 '0btag', 
#                                                                 '1btag', 
                                                                 '2orMoreBtags',
#                                                                 '4orMoreBtags'
                                                                 ])
    otherHists = []
    otherHists.append('EventCount/TTbarMuPlusJetsRefSelection')
    otherHists.append('EventCount/TTbarEplusJetsRefSelection')
    otherHists.append('EventCount/TTbarMuPlusJetsRefSelectionUnweighted')
    otherHists.append('EventCount/TTbarEplusJetsRefSelectionUnweighted')
#    otherHists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/Vertices/nVertex')
#    otherHists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/Vertices/nVertex_reweighted')
#    
#    otherHists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/N_BJets')
#    otherHists.append('TTbarPlusMetAnalysis/EPlusJets/Ref selection/N_BJets_reweighted')
    
    
#    otherHists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/Vertices/nVertex')
#    otherHists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/Vertices/nVertex_reweighted')
#    
#    otherHists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/N_BJets')
#    otherHists.append('TTbarPlusMetAnalysis/MuPlusJets/Ref selection/N_BJets_reweighted')

    
    if len(otherHists) > 0:
        otherHists = HistGetter.getHistsFromFiles(otherHists, files)
        hists = HistGetter.joinHistogramDictionaries([hists,
                                                  otherHists])
    gcd = gROOT.cd

    reverseMCOrdertmp = reverseMCOrder
    for histname in hists[hists.keys()[0]]:
        reverseMCOrder = reverseMCOrdertmp
        print '=' * 70
        print 'Plotting:', histname
        gcd()
        if 'MuPlusJets' in histname or 'Muon' in histname:
            used_data = 'SingleMu'
        else:
            used_data = 'SingleElectron'
        hist_data = hists[used_data][histname]
        
        for dataset in hists:
            if not 'Single' in dataset:
                scale = lumi * datasetInfo[dataset]['cross-section']/datasetInfo[dataset]['NumberOfProcessedEvents']
#                print dataset, '[', histname, '] is scaled by ', scale
                hists[dataset][histname].Scale(scale)

        hist_ttbar = hists['TTJet'][histname]
        #hist_wjets = hists['WJetsToLNu'][histname]
        hist_wjets = hists['W1Jet'][histname]
        hist_wjets += hists['W2Jets'][histname] 
        hist_wjets += hists['W3Jets'][histname] 
        hist_wjets += hists['W4Jets'][histname]
        #hist_zjets = hists['DYJetsToLL'][histname]
        hist_zjets = hists['DY1JetsToLL'][histname]
        hist_zjets += hists['DY2JetsToLL'][histname]
        hist_zjets += hists['DY3JetsToLL'][histname]
        hist_zjets += hists['DY4JetsToLL'][histname]

#        hist_muQCD = hists['QCD_Pt-20_MuEnrichedPt-15'][histname]
        hist_muQCD = hists['QCD_Pt-15to20_MuEnrichedPt5'][histname]
        hist_muQCD += hists['QCD_Pt-20to30_MuEnrichedPt5'][histname]
        hist_muQCD += hists['QCD_Pt-30to50_MuEnrichedPt5'][histname]
        hist_muQCD += hists['QCD_Pt-50to80_MuEnrichedPt5'][histname]
        hist_muQCD += hists['QCD_Pt-80to120_MuEnrichedPt5'][histname]
        hist_muQCD += hists['QCD_Pt-120to170_MuEnrichedPt5'][histname]
        hist_muQCD += hists['QCD_Pt-170to300_MuEnrichedPt5'][histname]
        hist_muQCD += hists['QCD_Pt-300to470_MuEnrichedPt5'][histname]
        hist_muQCD += hists['QCD_Pt-470to600_MuEnrichedPt5'][histname]
#        hist_muQCD += hists['QCD_Pt-600to800_MuEnrichedPt5'][histname]
        hist_muQCD += hists['QCD_Pt-800to1000_MuEnrichedPt5'][histname]
        hist_muQCD += hists['QCD_Pt-1000_MuEnrichedPt5'][histname]
        hist_bce1 = hists['QCD_Pt_20_30_BCtoE'][histname]
        hist_bce2 = hists['QCD_Pt_30_80_BCtoE'][histname]
        hist_bce3 = hists['QCD_Pt_80_170_BCtoE'][histname]
        hist_bce4 = hists['QCD_Pt_170_250_BCtoE'][histname]
        hist_bce5 = hists['QCD_Pt_250_350_BCtoE'][histname]
        hist_bce6 = hists['QCD_Pt_350_BCtoE'][histname]        
        hist_enri1 = hists['QCD_Pt_20_30_EMEnriched'][histname]
        hist_enri2 = hists['QCD_Pt_30_80_EMEnriched'][histname]
        hist_enri3 = hists['QCD_Pt_80_170_EMEnriched'][histname]
        hist_enri4 = hists['QCD_Pt_170_250_EMEnriched'][histname]
        hist_enri5 = hists['QCD_Pt_250_350_EMEnriched'][histname]
        hist_enri6 = hists['QCD_Pt_350_EMEnriched'][histname]        
        hist_pj4 = hists['GJets_HT-200To400'][histname]
        hist_pj5 = hists['GJets_HT-400ToInf'][histname]
        hist_singleTop = hists['T_tW-channel'][histname] + hists['T_t-channel'][histname] + hists['T_s-channel'][histname]
        hist_singleTop += hists['Tbar_t-channel'][histname] + hists['Tbar_s-channel'][histname] + hists['Tbar_tW-channel'][histname]
        
        #hist_diboson = hists['ww'][histname] + hists['wz'][histname] + hists['zz'][histname]
        
#        hist_ttbarZ = hists['TTbarZIncl'][histname]
#        hist_ttbarW = hists['TTbarInclWIncl'][histname]

        hist_qcd = hist_bce1 + hist_bce2 + hist_bce3 + hist_bce4 + hist_bce5 + hist_bce6
        hist_qcd += hist_enri1 + hist_enri2 + hist_enri3 + hist_enri4 + hist_enri5 + hist_enri6
        hist_qcd += hist_pj4 + hist_pj5
                
        nqcd = hist_qcd.Integral();
        shapeErrorHist = None 
        errorHist = None
        relativeQCDEstimationError = 0
        #TODO: fix this for muon+jets
        if 'EPlusJets' in histname or 'Electron' in histname:
            qcdFromMCPlots = 'QCD' in histname or 'Vertices' in histname or 'jets' in histname.split('/')[-1].lower() or  'bjet_invariant_mass' in histname      
            if ('MttbarAnalysis' in histname or 'TTbarPlusMetAnalysis' in histname):
                qcdRateEstimate = 'TTbarPlusMetAnalysis/EPlusJets/QCD e+jets PFRelIso/Electron/electron_pfIsolation_03'
                currentBin = HistPlotter.getBjetBin(histname)
                estimate, err = QCDEstimation.getQCDEstimate(files[used_data],
                                                             bjetBin=currentBin,
                                                             histogramForEstimation=qcdRateEstimate,
                                                             function='expo')
                if not estimate == 0:
                    relativeQCDEstimationError = err / estimate
                print 'Estimated QCD background: %.1f +- %.1f' % (estimate, err)
                if(hist_qcd.Integral() > 0 and estimate >= 0):
                    hist_qcd.Scale(estimate / hist_qcd.Integral())

                if not qcdFromMCPlots:#take QCD shape from data
                    currentBin = HistPlotter.getBjetBin(histname)
                    qcdShapeFromData = histname.replace('Ref selection', 'QCDConversions')
                    qcdShapeFromData = qcdShapeFromData.replace(currentBin, '0btag')
                    qcdShapeComparison = histname.replace('Ref selection', 'QCD non iso e+jets')
                    qcdShapeComparison = qcdShapeComparison.replace(currentBin, '0btag')
                    
                    print "Taking QCD shape from DATA (%s)" % qcdShapeFromData
                    qcdHists = HistGetter.getHistsFromFiles([qcdShapeFromData], {'data':files[used_data]})
                    
                    nQCD = hist_qcd.Integral()
                    hist_qcd = qcdHists['data'][qcdShapeFromData]
                    nShape = hist_qcd.Integral()
                    if nShape > 0:
                        hist_qcd.Scale(nQCD / nShape)
                    files['data'] = files['SingleElectron']
                    shapeErrorHist = QCDEstimation.getShapeErrorHistogram(files,
                                                                      histogramForShape=qcdShapeFromData,
                                                                      histogramForComparison=qcdShapeComparison)
                    
            
                
        if 'MuPlusJets' in histname or 'Muon' in histname:
            nQCD = hist_muQCD.Integral()
            #scale by factor, TODO: implement on-the-fly scale factor
            nMuQCD = nQCD*1.21
            print 'Estimated QCD background: %.1f' % nMuQCD
            #get template from anti-isolated region
            qcdFromMCPlots = 'QCD' in histname or 'Vertices' in histname or 'jets' in histname.split('/')[-1].lower() or 'bjet_invariant_mass' in histname 
                    
            if ('MttbarAnalysis' in histname or 'TTbarPlusMetAnalysis' in histname) and not qcdFromMCPlots:
                qcdShapeFromData = histname.replace('Ref selection', 'QCD non iso mu+jets')
                currentBin = HistPlotter.getBjetBin(histname)
                qcdShapeFromData = qcdShapeFromData.replace(currentBin, '0btag')
                print 'QCD shape from Data:', qcdShapeFromData
                qcdHists = HistGetter.getHistsFromFiles([qcdShapeFromData], {'data':files[used_data]})
                hist_muQCD = qcdHists['data'][qcdShapeFromData]
                
            nShape = hist_muQCD.Integral()
            if nShape > 0:
                hist_muQCD.Scale(nMuQCD / nShape)
                
        if performRescale:        
            print '=' * 100
            print '"best" rescaling for', histname
            rescales = rescaleMC(hist_data, hist_ttbar, hist_wjets, hist_qcd)
            print rescales
            print '=' * 100
            topScale = rescales[1]['ttbar']
            wjetScale = rescales[1]['wjets']
            qcdScale2 = rescales[1]['qcd']

            hist_ttbar.Scale(topScale)
            hist_wjets.Scale(wjetScale)
            hist_qcd.Scale(qcdScale2) 
        
        

        rebin = 1;
        Urange = (0, 5000)
        if ("mttbar" in histname):
            hist_data.SetXTitle("m(t#bar{t}) [GeV]");
            rebin = 50;
            hist_data.SetYTitle("Events/(%f GeV)" % hist_data.GetBinWidth(1) * rebin);
            if setLogY:
                Urange = (300, 3000)
            else:
                Urange = (300, 1500)
        if "All_Electron_mvaTrigV0" in histname:
            hist_data.SetXTitle("mva disc");
            hist_data.SetYTitle("Events/(0.01)");
            rebin = 1;
            Urange = (-1.1, 1.1)
        elif ("m3" in histname):
            hist_data.SetXTitle("M3 [GeV]");
            hist_data.SetYTitle("Events/(5 GeV)");
            rebin = 5;
            Urange = (0, 500)
        elif (histname == "electron_et"):
            hist_data.SetXTitle("electron p_{T} [GeV]");
            hist_data.SetYTitle("Events/(5 GeV)");
            rebin = 5;
        elif ("ttbar_pt" in histname):
            hist_data.SetXTitle("p_{T} of t#bar{t} system [GeV]");
            hist_data.SetYTitle("Events/(10 GeV)");
            rebin = 10;
            if setLogY:
                Urange = (0, 700)
            else:
                Urange = (0, 300)
        elif ("ttbar_px" in histname):
            hist_data.SetXTitle("p_{x} of t#bar{t} system [GeV]");
            hist_data.SetYTitle("Events/(10 GeV)");
            rebin = 10;
            Urange = (0, 1000)
        elif ("ttbar_py" in histname):
            hist_data.SetXTitle("p_{y} of t#bar{t} system [GeV]");
            hist_data.SetYTitle("Events/(10 GeV)");
            rebin = 10;
            Urange = (0, 1000)
        elif ("ttbar_pz" in histname):
            hist_data.SetXTitle("p_{z} of t#bar{t} system [GeV]");
            hist_data.SetYTitle("Events/(50 GeV)");
            rebin = 50;
            Urange = (0, 2500)
        elif ("HT" in histname):
            hist_data.SetXTitle("#Sigma p_{T} [GeV]");
            hist_data.SetYTitle("Events/(50 GeV)");
            rebin = 50;
            Urange = (0, 2500)
        elif (histname == "numberOfJets"):
            hist_data.SetXTitle("number of jets");
            hist_data.SetYTitle("Events");
        elif (histname == "numberOfBJets"):
            hist_data.SetXTitle("number of b-tagged jets (SSVHE medium)");
            hist_data.SetYTitle("Events");
        elif ('MET_' in histname and not 'phi' in histname and not 'Angle_lepton_MET' in histname):
            hist_data.SetXTitle("E_{T}^{miss} [GeV]");
            hist_data.SetYTitle("Events/(5 GeV)");
            rebin = 5
            if setLogY:
                Urange = (200, 590)
                rebin = 10
                hist_data.SetYTitle("Events/(10 GeV)")
            else:
                Urange = (0, 195)
        elif ('MET_phi' in histname):
            hist_data.SetXTitle("#phi(E_{T}^{miss})");
            hist_data.SetYTitle("Events/(0.1)");
            rebin = 1;
            Urange = (-4, 4)
        elif 'Angle_lepton_MET' in histname:
            hist_data.SetXTitle("angle(l,E_{T}^{miss})");
            hist_data.SetYTitle("Events/0.05");
            rebin = 5;
            Urange = (0, 3.2)
        elif 'METsignificance' in histname:
            hist_data.SetXTitle("METsignificance [GeV]");
            hist_data.SetYTitle("Events/(5 GeV)");
            rebin = 5;
            Urange = (0, 200)
        elif ("mtW" in histname or 'Transverse_Mass' in histname):
            hist_data.SetXTitle("transverse W-boson mass [GeV]");
            
            if setLogY:
                Urange = (0, 500)
                hist_data.SetYTitle("Events/(10 GeV)");
                rebin = 10;
            else:
                Urange = (0, 200)
                hist_data.SetYTitle("Events/(5 GeV)");
                rebin = 5;
        elif ("electronD0" in histname):
            hist_data.SetXTitle("electron d_{0} / cm");
            hist_data.SetYTitle("Events/(0.001 cm)");
            rebin = 10;
        elif ("angleTops" in histname):
            hist_data.SetXTitle("angle between top quarks");
            hist_data.SetYTitle("Events/(0.1 rad)");
            rebin = 20;
        elif ("neutrino_pz" in histname):
            hist_data.SetXTitle("neutrino p_{Z} [GeV]");
            hist_data.SetYTitle("Events/(10 GeV)");
            rebin = 10;
            Urange = (-500, 500)
        elif ('hadronicTopMass' in histname or 'leptonicTopMass' in histname or 'mAllTop' in histname):
            hist_data.SetXTitle("top mass [GeV]");
            if setLogY:
                Urange = (0, 1000)
                rebin = 10
                hist_data.SetYTitle("Events/(10 GeV)")
            else:
                rebin = 5
                hist_data.SetYTitle("Events/(5 GeV)")
                Urange = (0, 500)
        elif 'hadronicWMass' in histname:
            hist_data.SetXTitle("W mass [GeV]");
            hist_data.SetYTitle("Events/(5 GeV)");
            rebin = 5;
            if setLogY:
                Urange = (0, 350)
            else:
                Urange = (0, 200)
        elif ('pt_leadingTop' in histname or 'pt_NextToLeadingTop' in histname):
            hist_data.SetXTitle("top p_{T} [GeV]");
            hist_data.SetYTitle("Events/(20 GeV)");
            rebin = 20;
        elif('QCDest_CombRelIso' in histname):
            hist_data.SetXTitle("relative isolation");
            hist_data.SetYTitle("Events/(0.1)");
            rebin = 10;
            Urange = (0, 2)
        elif('pfisolation' in histname.lower()):
            hist_data.SetXTitle("Relative isolation");
            hist_data.SetYTitle("Events/(0.1)");
            rebin = 10
            Urange = (0, 2)
            reverseMCOrder = False
        elif 'DirectionalIsolation' in histname:
            hist_data.SetXTitle("directional isolation");
            hist_data.SetYTitle("Events/(0.01)");
            rebin = 10
            Urange = (0, 2)
        elif 'DirectionalIsolationWithGaussianFallOff' in histname:
            hist_data.SetXTitle("directional isolation");
            hist_data.SetYTitle("Events/(0.01)");
            rebin = 10
            Urange = (0, 2)
        elif('diElectron' in histname):
            hist_data.SetXTitle("m(ee)");
            hist_data.SetYTitle("Events/(10 GeV)");
            rebin = 10
            Urange = (50, 2000)
        elif 'JetMass' in histname:
            hist_data.SetXTitle("m(jet)");
            hist_data.SetYTitle("Events/(5 GeV)");
            rebin = 5
            Urange = (0, 200)
        elif 'nVertex' in histname:
            Urange = (0, 21)
        elif 'electron_pT' in histname:
            hist_data.SetXTitle("p_{T}(e)");
            hist_data.SetYTitle("Events/(5 GeV)");
            rebin = 5
            if setLogY:
                Urange = (0, 500)
            else:
                print 'electron_pt, 200'
                Urange = (0, 200)
        elif 'muon_pT' in histname:
            hist_data.SetXTitle("p_{T}(#mu)");
            hist_data.SetYTitle("Events/(5 GeV)");
            rebin = 5
            if setLogY:
                Urange = (0, 500)
            else:
                print 'electron_pt, 200'
                Urange = (0, 200)
        elif 'electron_eta' in histname:
            hist_data.SetYTitle("Events/(0.2)");
            rebin = 10
            Urange = (-3, 3)
        elif 'N_BJets' in histname:
            Urange = (0, 5)
            hist_data.SetXTitle("B-tag Multiplicity");
            hist_data.SetYTitle("Events")
        elif 'N_Jets' in histname:
            hist_data.SetYTitle("Events");
            hist_data.SetXTitle("Jet Multiplicity");
            Urange = (4, 14)
        elif 'bjet_invariant_mass' in histname:
            Urange = (0, 600)
            rebin = 20
            hist_data.SetYTitle("Events/(20 GeV)");
            hist_data.SetXTitle("m(b,b)");
        if 'electron_AbsEta' in histname:
            hist_data.SetYTitle("Events/(0.1)");
            hist_data.SetXTitle("|#eta(e)|");
            rebin = 10
            Urange = (0, 2.5)
        if 'muon_AbsEta' in histname:
            hist_data.SetYTitle("Events/(0.1)");
            hist_data.SetXTitle("|#eta(#mu)|");
            rebin = 10
            Urange = (0, 2.5)
        if normalise:
            title = hist_data.GetYaxis().GetTitle()
            title = title.replace('Events', 'normalised to unit area')
            title = title.replace('events', 'normalised to unit area')
            hist_data.SetYTitle(title);
        hist_data.Rebin(rebin);
        hist_ttbar.Rebin(rebin);
        hist_wjets.Rebin(rebin);
        hist_zjets.Rebin(rebin);
        hist_qcd.Rebin(rebin);
#        hist_ttbarW.Rebin(rebin)
#        hist_ttbarZ.Rebin(rebin)
        hist_muQCD.Rebin(rebin);
        hist_singleTop.Rebin(rebin)
#        hist_diboson.Rebin(rebin)
        hist_data.SetAxisRange(Urange[0], Urange[1]);
        hist_ttbar.SetAxisRange(Urange[0], Urange[1]);
        hist_wjets.SetAxisRange(Urange[0], Urange[1]);
        hist_zjets.SetAxisRange(Urange[0], Urange[1]);
        hist_qcd.SetAxisRange(Urange[0], Urange[1]);
        hist_muQCD.SetAxisRange(Urange[0], Urange[1]);
        hist_singleTop.SetAxisRange(Urange[0], Urange[1]);
#        hist_diboson.SetAxisRange(Urange[0], Urange[1]);

        if shapeErrorHist:
            shapeErrorHist.Rebin(rebin)
            shapeErrorHist.SetAxisRange(Urange[0], Urange[1])
        hist_data.SetMarkerStyle(8);
        
        hist_ttbar.SetFillStyle(1001);
        hist_ttbar.SetFillColor(kRed + 1);
#        hist_ttbar.SetLineColor(kRed + 1);
        hist_wjets.SetFillStyle(1001);
        hist_wjets.SetFillColor(kGreen - 3);
#        hist_wjets.SetLineColor(kGreen - 3);
        hist_zjets.SetFillStyle(1001);
        hist_zjets.SetFillColor(kAzure - 2);
#        hist_zjets.SetLineColor(kAzure - 2);
        hist_qcd.SetFillStyle(1001);
        hist_qcd.SetFillColor(kYellow);
#        hist_qcd.SetLineColor(kYellow);
        hist_muQCD.SetFillStyle(1001);
        hist_muQCD.SetFillColor(kYellow);
        hist_singleTop.SetFillStyle(1001);
        hist_singleTop.SetFillColor(kMagenta)
#        hist_singleTop.SetLineColor(kMagenta)
        
#        hist_diboson.SetFillStyle(1001);
#        hist_diboson.SetFillColor(kWhite)
#        hist_diboson.SetLineColor(kWhite)
        
#        hist_ttbarZ.SetLineColor(kCyan-4)
#        hist_ttbarZ.SetFillStyle(4000)
#        hist_ttbarZ.SetLineWidth(3)
#        hist_ttbarZ.SetLineStyle(4);
#        hist_ttbarW.SetLineColor(kBlue +2)
#        hist_ttbarW.SetFillStyle(4000)
#        hist_ttbarW.SetLineWidth(3)
#        hist_ttbarW.SetLineStyle(4);
        allMC = hist_ttbar.Clone('allMC')
        allMC += hist_wjets + hist_zjets + hist_singleTop# + hist_diboson
        if 'MuPlusJets' in histname or 'Muon' in histname:
            allMC += hist_muQCD
        else:
            allMC += hist_qcd
            
#        ttbarErr = allMC.Clone('ttbar_err')
#        for bin_i in range(1, ttbarErr.GetNbinsX()):
#            value = hist_ttbar.GetBinContent(bin_i)
#            error = value * ttbarUncertainty
#            ttbarErr.SetBinError(bin_i, error)
#        ttbarErr.SetFillColor(kGray +2)
#        ttbarErr.SetMarkerStyle(0)
#        ttbarErr.SetFillStyle(3001);

        leg = TLegend(0.696, 0.95, 0.94, 0.55)
        leg.SetBorderSize(0)
        leg.SetLineStyle(0)
        leg.SetTextFont(42)
        leg.SetFillStyle(0)

        leg.AddEntry(hist_data, "data", "P")
        #        leg.AddEntry(hist_data2, "data(no HLT)", "P");
        leg.AddEntry(hist_ttbar, "t#bar{t}", "f")
        leg.AddEntry(hist_singleTop, "Single-Top", "f")
        leg.AddEntry(hist_wjets, "W#rightarrowl#nu", "f")
        leg.AddEntry(hist_zjets, "Z/#gamma*#rightarrowl^{+}l^{-}", "f")
        if 'MuPlusJets' in histname or 'Muon' in histname:
            leg.AddEntry(hist_muQCD, "QCD #mu Enriched", "f")
        else:
            leg.AddEntry(hist_qcd, "QCD/#gamma + jets", "f")
#        leg.AddEntry(hist_diboson, "VV + X", "f")
#        leg.AddEntry(hist_ttbarW, "t#bar{t} + W x 100", "f")
#        leg.AddEntry(hist_ttbarZ, "t#bar{t} + Z x 100", "f")
        #leg.AddEntry(ttbarErr, "t#bar{t} uncertainty", 'F')
        
        if normalise:
            if 'EPlusJets' in histname or 'Electron' in histname:
                normalisePlotsToUnitArea(hist_data, hist_ttbar, hist_wjets, hist_zjets, hist_singleTop, hist_qcd)#, hist_diboson)
            else:
                normalisePlotsToUnitArea(hist_data, hist_ttbar, hist_wjets, hist_zjets, hist_singleTop, hist_muQCD)#, hist_diboson)
            

        
        canvases.append(TCanvas("cname" + histname, histname, 1600, 1200))
        canvases[-1].cd().SetRightMargin(0.04);
        if 'TTbarPlusMetAnalysis' in histname and not 'QCD' in histname and 'EPlusJets' in histname:
#            relativeQCDEstimationError = 0
            errorHist = QCDEstimation.createErrorHistogram([hist_ttbar, hist_wjets, hist_zjets, hist_singleTop, hist_qcd],
                                                       hist_qcd, relativeQCDEstimationError, shapeErrorHist)
        
        hs = THStack("MC", "MC");
        if reverseMCOrder:
            hs.Add(hist_ttbar);
            hs.Add(hist_wjets);
            hs.Add(hist_zjets);
            hs.Add(hist_singleTop);
            if 'MuPlusJets' in histname or 'Muon' in histname:
                hs.Add(hist_muQCD);
            else:
                hs.Add(hist_qcd);
#            hs.Add(hist_diboson);
        
        else:
 #           hs.Add(hist_diboson);
            if 'MuPlusJets' in histname or 'Muon' in histname:
                hs.Add(hist_muQCD);
            else:
                hs.Add(hist_qcd);
            hs.Add(hist_zjets);
            hs.Add(hist_wjets);
            hs.Add(hist_singleTop);
            hs.Add(hist_ttbar);
        max = 0
        if hs.GetMaximum() > hist_data.GetMaximum():
            max = hs.GetMaximum() * 1.4
        else:
            max = hist_data.GetMaximum() * 1.4
        hist_data.GetYaxis().SetRangeUser(0, max);
        if setLogY:
            hist_data.GetYaxis().SetRangeUser(0.1, max);
        hist_data.Draw('error');
        hs.Draw("hist same");
#        hist_ttbarW.Draw("same")
#        hist_ttbarZ.Draw("same")
        setErrorX = TExec('ex1', 'gStyle->SetErrorX(0.5);')
        unsetErrorX = TExec('ex2', 'gStyle->SetErrorX(0.);')
#        gStyle.SetErrorX(0.5);
        setErrorX.Draw()
#        ttbarErr.Draw('e2 same')
        unsetErrorX.Draw()
#        gStyle.SetErrorX(0);
        if errorHist and drawQCDError:
            gStyle.SetErrorX(0.5);
            errorHist.SetFillColor(kGray + 3)
            errorHist.SetMarkerStyle(0)
            errorHist.SetFillStyle(3001);
            leg.AddEntry(errorHist, "QCD uncertainty")
            errorHist.Draw('e2 same')
        else:
            gStyle.SetErrorX(0);
            
        hist_data.Draw("error same");
        leg.Draw();
        text1, text2 = HistPlotter.get_cms_label(lumiInInvPb=lumi, njet=HistPlotter.getJetBin(histname),
                                          nbjet=HistPlotter.getBjetBin(histname), channel=HistPlotter.getChannel(histname))
        text1.Draw();
        text2.Draw();
#
        postfix = ''
        if setLogY:
            canvases[-1].SetLogy(1)
            postfix = '_log'
        if normalise:
            postfix = postfix + '_norm'
        if custom_suffix:
            postfix += '_' + custom_suffix
            
        prefix = 'EPlusJets_'
        if 'MuPlusJets' in histname or 'Muon' in histname:
            prefix = 'MuPlusJets_'
        selectionLabel = ''
        if 'Ref' in histname:
            selectionLabel = 'Ref_'
        if 'QCDConversions' in histname:
            selectionLabel = 'QCDConversions_'
        if 'QCD non iso e+jets' in histname:
            selectionLabel = 'AntiIsolated_'
            
        name = ''.join(histname[:histname.rfind('/') + 1]) + prefix + selectionLabel + ''.join(histname[histname.rfind('/') + 1:]) + postfix
        #specific selections
        
        
#        fullName = name.replace('EPlusJets', 'EPlusJets' + selectionLabel) + postfix
        saveAs(canvas=canvases[-1], name=name, outputFormats=outputFormats, outputFolder=savePath)
        del canvases[-1]

#        cu_hist_data = getCumulativePlot(hist_data, "data_" + histname);
#        cu_hist_ttbar = getCumulativePlot(hist_ttbar, "ttbar_" + histname);
#        cu_hist_wjets = getCumulativePlot(hist_wjets, "wjets_" + histname);
#        cu_hist_zjets = getCumulativePlot(hist_zjets, "zjets_" + histname);
#        cu_hist_qcd = getCumulativePlot(hist_qcd, "qcd_" + histname);
#        cu_hist_muQCD = getCumulativePlot(hist_qcd, "MUqcd_" + histname);
#        cu_hist_singleTop = getCumulativePlot(hist_singleTop, "singleTop_" + histname);
#        cu_hist_diboson = getCumulativePlot(hist_diboson, "di-boson_" + histname);
##        cu_hist_ttbarW = getCumulativePlot(hist_ttbarW, "ttbarW_" + histname);
##        cu_hist_ttbarZ = getCumulativePlot(hist_ttbarZ, "ttbarZ_" + histname);
###        cu_hist_Zprime500 = getCumulativePlot(hist_Zprime500, "Zprime500");
###        cu_hist_Zprime750 = getCumulativePlot(hist_Zprime750, "Zprime750");
###        cu_hist_Zprime1000 = getCumulativePlot(hist_Zprime1000, "Zprime1000");
###        cu_hist_Zprime1250 = getCumulativePlot(hist_Zprime1250, "Zprime1250");
##        cu_hist_Zprime4000 = getCumulativePlot(hist_Zprime4000, "Zprime4000");
#        cu_hist_data.SetYTitle("Integrated" + cu_hist_data.GetYaxis().GetTitle())
###        
##
#        cu_hist_data.SetAxisRange(Urange[0], Urange[1]);
#        cu_hist_ttbar.SetAxisRange(Urange[0], Urange[1]);
#        cu_hist_wjets.SetAxisRange(Urange[0], Urange[1]);
#        cu_hist_zjets.SetAxisRange(Urange[0], Urange[1]);
#        cu_hist_qcd.SetAxisRange(Urange[0], Urange[1]);
#        cu_hist_muQCD.SetAxisRange(Urange[0], Urange[1]);
#        cu_hist_singleTop.SetAxisRange(Urange[0], Urange[1]);
#        cu_hist_diboson.SetAxisRange(Urange[0], Urange[1]);
##        cu_hist_ttbarW.SetAxisRange(Urange[0], Urange[1]);
##        cu_hist_ttbarZ.SetAxisRange(Urange[0], Urange[1]);
#        
#        cu_hs = THStack("cu_MC", "cu_MC");
#        cu_hs.Add(cu_hist_diboson);
#        cu_hs.Add(cu_hist_ttbar);
#        cu_hs.Add(cu_hist_wjets);
#        cu_hs.Add(cu_hist_zjets);
#        cu_hs.Add(cu_hist_singleTop);
#        if 'Muon' in histname:
#                hs.Add(cu_hist_muQCD);
#        else:
#                cu_hs.Add(cu_hist_qcd);
#        
#        scanvases.append(TCanvas("cu_cname" + histname, histname + "(cu)", 1600, 1200))
#        scanvases[-1].cd().SetRightMargin(0.04);
#        
#        cu_hist_data.Draw("error");
#        cu_hs.Draw("hist same");
##        cu_hist_ttbarW.Draw("same");
##        cu_hist_ttbarZ.Draw("same");
####        cu_hist_Zprime500.Draw("same");
####        cu_hist_Zprime750.Draw("same");
####        cu_hist_Zprime1000.Draw("same");
####        cu_hist_Zprime1250.Draw("same");
##        cu_hist_Zprime4000.Draw("same");
###        #        cu_hist_data2.Draw("error same");
#        cu_hist_data.Draw("error same");
#        leg.Draw();
###
#        text1.Draw()
#        postfix = ''
#        if setLogY:
#            scanvases[-1].SetLogy(1)
#            postfix = '_log'
##        scanvases[-1].SetGridy(1)       
#        name = ''.join(histname[:histname.rfind('/') + 1]) + prefix + ''.join(histname[histname.rfind('/') + 1:])
#        saveAs(canvas=scanvases[-1], name=name + '_integrated' + postfix, outputFormats=outputFormats, outputFolder=savePath)
#        del scanvases[-1]
#        del cu_hs
#        del cu_hist_data
#        del cu_hist_ttbar
#        del cu_hist_wjets
#        del cu_hist_zjets
#        del cu_hist_qcd
#        del cu_hist_singleTop
#        del cu_hist_diboson


# fixOverlay: Redraws the axis

def fixOverlay():
    gPad.RedrawAxis();


def getCumulativePlot(initial, type):
    name = initial.GetName()
    name = "cu_" + name + "_" + type;
    title = initial.GetTitle()
    title = "cu_" + title + "_" + type;
    xaxis = initial.GetXaxis().GetTitle();
    yaxis = initial.GetYaxis().GetTitle();
    nBins = initial.GetNbinsX();
    cu = TH1F(name, title, nBins, initial.GetXaxis().GetXmin(), initial.GetXaxis().GetXmax());
#    cu.Sumw2()
    for bin in range(1, nBins + 1):
        cu.SetBinContent(bin, initial.Integral(bin, nBins));
    
    cu.SetFillStyle(initial.GetFillStyle());
    cu.SetFillColor(initial.GetFillColor());
    cu.SetLineColor(initial.GetLineColor());
    cu.SetMarkerSize(initial.GetMarkerSize());
    cu.SetMarkerStyle(initial.GetMarkerStyle());
    cu.SetMarkerColor(initial.GetMarkerColor());
    cu.SetLineWidth(initial.GetLineWidth());
    cu.GetXaxis().SetTitle(xaxis);
    cu.GetYaxis().SetTitle(yaxis);
    return cu;


def normalisePlotsToUnitArea(data, hist_ttbar, hist_wjets, hist_zjets, hist_singleTop, hist_qcd):#, hist_diboson):
    nData = data.Integral()
    nTop = hist_ttbar.Integral()
    nWJ = hist_wjets.Integral()
    nZJ = hist_zjets.Integral()
    nST = hist_singleTop.Integral()
    nQCD = hist_qcd.Integral()
#    nDB = hist_diboson.Integral()
    data.Sumw2()   
    nMC = sum([nTop, nWJ, nZJ, nST, nQCD])#, nDB])
    print 'nMC', nMC
    if not nData == 0:
        data.Scale(1 / nData)
    
    
    if not nMC == 0:
        hist_ttbar.Scale(1 / nMC)
        hist_wjets.Scale(1 / nMC)
        hist_zjets.Scale(1 / nMC)
        hist_singleTop.Scale(1 / nMC)
        hist_qcd.Scale(1 / nMC)
#        hist_diboson.Scale(1 / nMC)
    
    chi2 = 0
    for bin in range(1, data.GetNbinsX() + 1):
        nData = data.GetBinContent(bin)
        nTop = hist_ttbar.GetBinContent(bin)
        nWJ = hist_wjets.GetBinContent(bin)
        nZJ = hist_zjets.GetBinContent(bin)
        nST = hist_singleTop.GetBinContent(bin)
        nQCD = hist_qcd.GetBinContent(bin)
#        nDB = hist_diboson.GetBinContent(bin)
        nMC = sum([nTop, nWJ, nZJ, nST, nQCD])#, nDB])
        chi2 += (nData - nMC) ** 2
    print 'Chi2:', chi2
        
    
def rescaleMC(data, ttbar, wjets, qcd):
    #rescaling
    
    
    chi2 = {}
    
    eventsData = []
    appendData = eventsData.append
    eventsTTbar = []
    appendTTbar = eventsTTbar.append
    eventsWJets = []
    appendWJets = eventsWJets.append
    eventsQCD = []
    appendQCD = eventsQCD.append
    nBins = data.GetNbinsX()
    
    getData = data.GetBinContent
    getttbar = ttbar.GetBinContent
    getwjets = wjets.GetBinContent
    getqcd = qcd.GetBinContent
    for bin in range(nBins):        
        appendData(getData(bin))
        appendTTbar(getttbar(bin))
        appendWJets(getwjets(bin))
        appendQCD(getqcd(bin))
    
    events = {}
    events['data'] = eventsData
    events['ttbar'] = eventsTTbar
    events['wjets'] = eventsWJets
    events['qcd'] = eventsQCD
    
    for tscale in arange(1, 2, 0.2):
        for wscale in arange(1, 4, 0.4):
            for qscale in arange(1, 4, 0.4):
                res = getChi2(events, {'ttbar': tscale, 'wjets':wscale, 'qcd':qscale})
                chi2[res] = {'ttbar': tscale, 'wjets':wscale, 'qcd':qscale}
    keys = chi2.keys()
    result = {'ttbar': 1, 'wjets':1, 'qcd':1}
    if len(keys) > 0:
        result = sorted(keys)[0]
    return result, chi2[result]
        
            
def getChi2(events={}, scales={}):
    diff = 0
    for eventsData, eventsTTbar, eventsWJets, eventsQCD  in zip(events['data'], events['ttbar'], events['wjets'], events['qcd']):        
        eventsMC = eventsTTbar * scales['ttbar'] + eventsWJets * scales['wjets'] + eventsQCD * scales['qcd']
        diff += (eventsData - eventsMC) ** 2
    return diff / len(events['data'])

if __name__ == "__main__":
    gROOT.SetBatch(True)
    gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    parser = OptionParser()
    parser.add_option("-l", "--logY",
                  action="store_true", dest="logY", default=False,
                  help="enable logarithmic y-axis")
    parser.add_option("-n", "--normalise",
                  action="store_true", dest="norm", default=False,
                  help="normalise to unit area")

    (options, args) = parser.parse_args()
    setLogY = options.logY
    normalise = options.norm
    plotMttbar()
