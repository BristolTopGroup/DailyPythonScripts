'''
Created on Dec 1, 2011

@author: Lukasz Kreczko

Email: Lukasz.Kreczko@cern.ch

The AnalysisTools produce a 2D histogram with the cut flow for each sample which is saved in the histogram file
First dimension is the cut-stage, second dimension the jet-bin (== 1, ==2, ==3, >=4)

printCutFlow reads 2D histogram
outputFormat = CSV|plain|twiki|latex
'''

from __future__ import division
from ROOT import *
import tools.ROOTFileReader as FileReader
import tools.PlottingUtilities as plotting
import FILES
from math import sqrt
import QCDRateEstimation

cuts = None
cuts_electrons = [
        "Skim", #
        "Event cleaning and HLT", #
                "Electron", #
                "Muon Veto", #
                "Electron veto", #
                "Conversion veto", #
                "$\geq 3$ jets", #
                "$\geq 4$ jets", #
                "$\geq 1$ CSV b-tag", #
                "$\geq 2$ CSV b-tag" #
        ]

cuts_muons = [
        "Skim", #
        "Event cleaning and HLT", #
                "Muon", #
                "Electron veto", #
                "Muon Veto", #
                "$\geq 3$ jets", #
                "$\geq 4$ jets", #
                "$\geq 1$ CSV b-tag", #
                "$\geq 2$ CSV b-tag" #
        ]

def printCutFlow(hist, analysis, outputFormat='Latex'):
    scale_ttbar = 164.4 / 157.5
    used_data = 'ElectronHad'
    lepton = 'Electron/electron'
    if 'Mu' in analysis:
        used_data = 'SingleMu'
        lepton = 'Muon/muon'
    hist_1mBtag = 'TTbarPlusMetAnalysis/' + analysis + '/Ref selection/' + lepton + '_AbsEta_1orMoreBtag'
    hist_2mBtag = 'TTbarPlusMetAnalysis/' + analysis + '/Ref selection/' + lepton + '_AbsEta_2orMoreBtags'
    hist_names = [hist, #due to b-tag scale factors these are not as simple any more
             hist_1mBtag,
             hist_2mBtag
             ]
    inputfiles = {}
    for sample in FILES.samplesToLoad:
        inputfiles[sample] = FILES.files[sample]
    hists = FileReader.getHistogramsFromFiles(hist_names, inputfiles)
    for sample in hists.keys():
        for histname in hists[sample].keys():
            hists[sample][histname].Sumw2()
    if analysis == 'EPlusJets':
        hists['QCD'] = plotting.sumSamples(hists, plotting.qcd_samples)
    else:
        hists['QCD'] = hists['QCD_Pt-20_MuEnrichedPt-15']
    
    hists['SingleTop'] = plotting.sumSamples(hists, plotting.singleTop_samples)
    hists['Di-Boson'] = plotting.sumSamples(hists, plotting.diboson_samples)
    hists['W+Jets'] = plotting.sumSamples(hists, plotting.wplusjets_samples)
#    hists['SumMC'] = plotting.sumSamples(hists, plotting.allMC_samples)
    
    header = "| Step | TTJet | W+jets | DY + Jets | single top | Di-boson | QCD | Sum MC | Data |"
    row = " | %s  |  %d +- %d |  %d +- %d |  %d +- %d |  %d +- %d |  %d +- %d |  %d +- %d |  %d +- %d |  %d | "
    if outputFormat == 'Latex':
        header = "Selection step & \\ttbar & W + Jets & Z + Jets & Single-top & Di-boson & QCD~  & Sum MC & Data\\\\"
        row = " %s  &  $%d \pm %d$ &  $%d \pm %d$ &  $%d \pm %d$ &  $%d \pm %d$ &  $%d \pm %d$ &  $%d \pm %d$ &  $%d \pm %d$ &  %d \\\\ "
    print header
    
    numbers, errors = getEventNumbers(hists, hist, hist_1mBtag, hist_2mBtag)# + '_0orMoreBtag')
    

    for step in range(len(cuts)):
        nums = numbers[step]
        errs = errors[step]
        nums['TTJet'] = nums['TTJet'] * scale_ttbar
        errs['TTJet'] = errs['TTJet'] * scale_ttbar
        if analysis == 'EPlusJets' and step >= len(cuts) - 3:#have only estimates for >= 4 jet and beyond
            histForEstimation = 'TTbarPlusMetAnalysis/EPlusJets/QCD e+jets PFRelIso/Electron/electron_pfIsolation_03_0orMoreBtag'
            if step == len(cuts) - 2:
                histForEstimation = 'TTbarPlusMetAnalysis/EPlusJets/QCD e+jets PFRelIso/Electron/electron_pfIsolation_03_1orMoreBtag'
            if step == len(cuts) - 1:
                histForEstimation = 'TTbarPlusMetAnalysis/EPlusJets/QCD e+jets PFRelIso/Electron/electron_pfIsolation_03_2orMoreBtags'
            estimate = QCDRateEstimation.estimateQCDWithRelIso(FILES.files, histForEstimation)
            nums['QCD'], errs['QCD'] = estimate['estimate'], estimate['absoluteError'] 
        if analysis == 'MuPlusJets' and step >= len(cuts) - 3:#have only estimates for >= 4 jet and beyond
            scale = 1.21
            nums['QCD'], errs['QCD'] = nums['QCD'] * scale, errs['QCD'] * scale
            
        sumMC = nums['TTJet'] + nums['W+Jets'] + nums['DYJetsToLL'] + nums['SingleTop'] + nums['QCD'] + nums['Di-Boson']
        sumMC_err = sqrt(errs['TTJet'] ** 2 + errs['W+Jets'] ** 2 + errs['DYJetsToLL'] ** 2 + errs['SingleTop'] ** 2 + errs['QCD'] ** 2 + errs['Di-Boson'] ** 2)
        print row % (cuts[step], nums['TTJet'], errs['TTJet'], nums['W+Jets'], errs['W+Jets'], nums['DYJetsToLL'], errs['DYJetsToLL'],
                     nums['SingleTop'], errs['SingleTop'], nums['Di-Boson'], errs['Di-Boson'], nums['QCD'], errs['QCD'], sumMC, sumMC_err, nums[used_data])

def getEventNumbers(hists, histname, hist_1mBtag, hist_2mBtag):        
    eventNumbers = []
    errorValues = []
    for step in range(len(cuts)):
        events = {}
        errors = {}
        for sample in hists.keys():
            events[sample] = hists[sample][histname].GetBinContent(step + 1)
            errors[sample] = hists[sample][histname].GetBinError(step + 1)
            if step == len(cuts) - 2:
                events[sample] = hists[sample][hist_1mBtag].Integral()
                entries = hists[sample][hist_1mBtag].GetEntries()
                if not entries == 0:
                    errors[sample] = sqrt(entries) / entries * events[sample]
                else:
                    errors[sample] = 0
            if step == len(cuts) - 1:
                events[sample] = hists[sample][hist_2mBtag].Integral()
                entries = hists[sample][hist_2mBtag].GetEntries()
                if not entries == 0:
                    errors[sample] = sqrt(entries) / entries * events[sample]
                else:
                    errors[sample] = 0
        eventNumbers.append(events)
        errorValues.append(errors)
    return eventNumbers, errorValues
    

if __name__ == "__main__":
    gROOT.SetBatch(True)
    gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    cuts = cuts_electrons
    print '=' * 120
    print 'TTbarEplusJetsRefSelection'
    printCutFlow('EventCount/TTbarEplusJetsRefSelection', 'EPlusJets')
    print '=' * 120
    cuts = cuts_muons
    print '=' * 120
    print 'TTbarMuPlusJetsRefSelection'
    printCutFlow('EventCount/TTbarMuPlusJetsRefSelection', 'MuPlusJets')
    print '=' * 120
