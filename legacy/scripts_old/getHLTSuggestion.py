'''
Created on Mar 5, 2011

@author: lkreczko
'''
from __future__ import division
from ROOT import *


triggers = [
    #========== 2011 data ==============  
    #ElectronHad PD
    'HLT_Ele25_CaloIdVT_TrkIdT_CentralJet40_BTagIP_v', #12
    'HLT_Ele25_CaloIdVT_TrkIdT_CentralJet30_v', #13
    'HLT_Ele25_CaloIdVT_TrkIdT_CentralDiJet30_v', #14
    'HLT_Ele25_CaloIdVT_TrkIdT_CentralTriJet30_v', #15
    #renaming for 1E33
    'HLT_Ele25_CaloIdVT_TrkIdT_CentralJet30_BTagIP_v', #16
    'HLT_Ele25_CaloIdVT_TrkIdT_DiCentralJet30_v',#17
    'HLT_Ele25_CaloIdVT_TrkIdT_TriCentralJet30_v', #18
    'HLT_Ele25_CaloIdVT_TrkIdT_QuadCentralJet30_v', #19
    #new iso triggers:
    'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_CentralJet30_BTagIP_v',#20
    'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_CentralJet30_v',#21
    'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_DiCentralJet30_v',#22
    'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralJet30_v',#23
    'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_QuadCentralJet30_v',#24
    #Higgs trigger
    'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_CentralJet30_CentralJet25_PFMHT20_v',#25
    #EWK triggers
    'HLT_Ele25_WP80_PFMT40_v',#26
    'HLT_Ele27_WP70_PFMT40_PFMHT20_v',#27
    #SingleElectron PD
    'HLT_Ele27_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_v', #28
    'HLT_Ele25_CaloIdL_CaloIsoVL_TrkIdVL_TrkIsoVL_v',#29
    'HLT_Ele32_CaloIdVL_CaloIsoVL_TrkIdVL_TrkIsoVL_v',#30
    'HLT_Ele32_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_v',#31
    #5E33 change to PF jets @ HLT
    'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_CentralPFJet30_v',
    'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_DiCentralPFJet30_v',
    'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralPFJet30_v',
    'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_QuadCentralPFJet30_v',
    #control triggers
    'HLT_Ele25_CaloIdVT_TrkIdT_CentralPFJet30_v',
    'HLT_Ele25_CaloIdVT_TrkIdT_DiCentralPFJet30_v',
    'HLT_Ele25_CaloIdVT_TrkIdT_TriCentralPFJet30_v',
    'HLT_Ele25_CaloIdVT_TrkIdT_QuadCentralPFJet30_v',
    #Muon Triggers
    #SingleMuon - last unprescaled in 1E33 menu
    'HLT_Mu15_v', 
    'HLT_Mu20_v',
    'HLT_IsoMu17_v', 
    'HLT_IsoMu15_v', 
    'HLT_IsoMu24_v',
    'HLT_IsoMu24_eta2p1_v',
    'HLT_IsoMu30_eta2p1_v',
    #MuHad
    'HLT_IsoMu17_CentralJet40_BTagIP_v', #32
    'HLT_Mu17_CentralJet30_v', #33
    'HLT_Mu17_CentralJet40_BTagIP_v', #34
    'HLT_Mu17_DiCentralJet30_v', #35
    'HLT_Mu17_TriCentralJet30_v', #36
    #2E33
    'HLT_IsoMu17_CentralJet30_BTagIP_v',
    'HLT_IsoMu17_CentralJet30_v',
    'HLT_IsoMu17_DiCentralJet30_v',
    'HLT_IsoMu17_QuadCentralJet30_v',
    'HLT_IsoMu17_TriCentralJet30_v',
    #3E33 - added eta requirement @ L1
    'HLT_IsoMu17_eta2p1_CentralJet30_BTagIP_v',
    'HLT_IsoMu17_eta2p1_CentralJet30_v',
    'HLT_IsoMu17_eta2p1_DiCentralJet30_v',
    'HLT_IsoMu17_eta2p1_QuadCentralJet30_v',
    'HLT_IsoMu17_eta2p1_TriCentralJet30_v',
    #5E33 change to PF jets @ HLT
    'HLT_IsoMu17_eta2p1_CentralPFJet30_v',
    'HLT_IsoMu17_eta2p1_DiCentralPFJet30_v',
    'HLT_IsoMu17_eta2p1_TriCentralPFJet30_v',
    'HLT_IsoMu17_eta2p1_QuadCentralPFJet30_v',
    #control triggers
    'HLT_Mu17_eta2p1_CentralPFJet30_v',
    'HLT_Mu17_eta2p1_DiCentralPFJet30_v',
    'HLT_Mu17_eta2p1_TriCentralPFJet30_v',
    'HLT_Mu17_eta2p1_QuadCentralPFJet30_v',
    ]

if __name__ == '__main__':
    gROOT.SetBatch(1);
    chain = TChain("rootTupleTree/tree");

    chain.Add("/storage/TopQuarkGroup/data/MuHad/nTuple_v4c_Run2011A-05Aug2011-v1_GoldenJSON_muonSkim/*.root");
    chain.Add("/storage/TopQuarkGroup/data/MuHad/nTuple_v4c_Run2011A-May10ReReco-v1_GoldenJSON_muonSkim/*.root");
    chain.Add("/storage/TopQuarkGroup/data/MuHad/nTuple_v4d_Run2011A-PromptReco-v4_GoldenJSON_muonSkim/*.root");
    chain.Add("/storage/TopQuarkGroup/data/MuHad/nTuple_v4d_Run2011A-PromptReco-v6_GoldenJSON_muonSkim/*.root");
    chain.Add("/storage/TopQuarkGroup/data/MuHad/nTuple_v4d_Run2011B-PromptReco-v1_GoldenJSON_muonSkim/*.root");
    chain.SetBranchStatus("*", 0);
    chain.SetBranchStatus("Event.Run", 1);
    chain.SetBranchStatus("Trigger.HLTPrescales", 1);
    muPlus3Jets = triggers.index('HLT_Mu17_TriCentralJet30_v')
    muPlus3JetsUnprescaledRuns = []
    
    mu3JetsAdd = muPlus3JetsUnprescaledRuns.append
    
    print 'Starting analysis'
    for event in chain:
        getVar = event.__getattr__
        prescales = getVar("Trigger.HLTPrescales")
        run = getVar("Event.Run")
        if not prescales[muPlus3Jets] == 1:
            mu3JetsAdd(run)
    print 'Finished analysis'
    muPlus3JetsUnprescaledRuns.sort()
    print muPlus3JetsUnprescaledRuns[0]
             
        