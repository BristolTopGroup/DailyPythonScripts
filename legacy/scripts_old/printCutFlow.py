from __future__ import division
from numpy import arange
from tdrStyle import *
from ROOT import *
#from QCDEstimation import getQCDEstimate#, estimateQCDFor
import QCDEstimation

import HistPlotter
import HistGetter
import inputFiles


cuts = None
cuts_electrons = [
        "All events after skim",
        "Event cleaning and High Level Trigger", 
                "exactly one isolated electron", 
                "loose muon veto", 
                "di-lepton veto", 
                "Conversion veto", 
                ">= 3 jets", 
                ">= 4 jets", 
                ">=1 CSV b-tag", 
                ">=2 CSV b-tag" 
        ]

cuts_muons = [
        "All events after skim",
        "Event cleaning and High Level Trigger", 
                "exactly one isolated muon", 
                "loose lepton veto", 
                "di-lepton veto", 
                ">= 3 jets", 
                ">= 4 jets", 
                ">=1 CSV b-tag", 
                ">=2 CSV b-tag"  
        ]

samples = [
           'ttbar', 'W1Jet', 'W2Jets', 'W3Jets', 'W4Jets', 'zjets',
           'data', 'qcd', 'singleTop']

def printCutFlow(hist, analysis):
    files = inputFiles.files
    hist_1mBtag =  'TTbarPlusMetAnalysis/' + analysis + '/Ref selection/MET/patMETsPFlow/MET_1orMoreBtag'
    hist_2mBtag = 'TTbarPlusMetAnalysis/' + analysis + '/Ref selection/MET/patMETsPFlow/MET_2orMoreBtags'
    hists = [hist, #due to b-tag scale factors these are not as simple any more
             hist_1mBtag,
             hist_2mBtag
             ]
    hists = HistGetter.getHistsFromFiles(hists, files, bJetBins=[])
    hists = HistGetter.addSampleSum(hists)
#    histname3 = 'EventCount/TTbarEplusJetsSelection_2orMoreBtags'
    
    header = "| Step | TTJet | W+jets | DY + Jets | single top | QCD | Sum MC | Data |"
    row = " | %s  |  %d |  %d |  %d |  %d |  %d|  %d |  %d | "
    print header
    
    numbers = getEventNumbers(hists, hist, hist_1mBtag, hist_2mBtag)# + '_0orMoreBtag')
    for step in range(len(cuts)):
        nums = numbers[step]
        sumMC = nums['ttbar'] + nums['wjets'] + nums['zjets'] + nums['singleTop'] + nums['qcd']
        print row % (cuts[step], nums['ttbar'], nums['wjets'], nums['zjets'], nums['singleTop'], nums['qcd'], sumMC, nums['data'])

def getEventNumbers(hists, histname, hist_1mBtag, hist_2mBtag):        
    eventNumbers = []
    for step in range(len(cuts)):
        events = {}
        events['wjets'] = hists['wjets'][histname].GetBinContent(step + 1)
        for sample in samples:
            events[sample] = hists[sample][histname].GetBinContent(step + 1)
            if step == len(cuts) - 2:
                events[sample] = hists[sample][hist_1mBtag].Integral()
            if step == len(cuts) - 1:
                events[sample] = hists[sample][hist_2mBtag].Integral()
        eventNumbers.append(events)
    return eventNumbers
    

if __name__ == "__main__":
    gROOT.SetBatch(True)
    gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    cuts = cuts_electrons
    print '='*120
    print 'TTbarEplusJetsRefSelection'
    printCutFlow('EventCount/TTbarEplusJetsRefSelection', 'EPlusJets')
    print '='*120
    cuts = cuts_muons
    print '='*120
    print 'TTbarMuPlusJetsRefSelection'
    printCutFlow('EventCount/TTbarMuPlusJetsRefSelection', 'MuPlusJets')
    print '='*120
