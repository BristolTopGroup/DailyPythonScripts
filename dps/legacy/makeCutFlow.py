from multiprocessing import Process

from ROOT import *

def getHLTCut():
    hltTriggers = [
               #2010 data RunA + RunB
    'HLT_Ele10_LW_L1R', #0
    'HLT_Ele15_SW_L1R', #1
    'HLT_Ele15_SW_CaloEleId_L1R', #2
    'HLT_Ele17_SW_CaloEleId_L1R', #3
    'HLT_Ele17_SW_EleId_L1R', #4
    'HLT_Ele17_SW_LooseEleId_L1R', #5
    'HLT_Ele17_SW_TightEleIdIsol_L1R_v1', #6
    'HLT_Ele17_SW_TightEleId_L1R', #7
    'HLT_Ele17_SW_TighterEleIdIsol_L1R_v1', #8
    'HLT_Ele17_SW_TighterEleId_L1R_v1', #9
    'HLT_Ele22_SW_TighterEleId_L1R', #10
    'HLT_Ele27_SW_TightCaloEleIdTrack_L1R_v1', #11
    #========== 2011 data ==============
    #ElectronHad PD
    'HLT_Ele25_CaloIdVT_TrkIdT_CentralJet40_BTagIP', #12
    'HLT_Ele25_CaloIdVT_TrkIdT_CentralJet30', #13
    'HLT_Ele25_CaloIdVT_TrkIdT_CentralDiJet30', #14
    'HLT_Ele25_CaloIdVT_TrkIdT_CentralTriJet30', #15
    #renaming for 1E33
    'HLT_Ele25_CaloIdVT_TrkIdT_CentralJet30_BTagIP', #16
    'HLT_Ele25_CaloIdVT_TrkIdT_DiCentralJet30', #17
    'HLT_Ele25_CaloIdVT_TrkIdT_TriCentralJet30', #18
    'HLT_Ele25_CaloIdVT_TrkIdT_QuadCentralJet30', #19
    #new iso triggers:
    'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_CentralJet30_BTagIP',#20
    'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_CentralJet30', #21
    'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_DiCentralJet30', #22
    'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralJet30', #23
    'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_QuadCentralJet30', #24
    #Higgs trigger
    'HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_CentralJet30_CentralJet25_PFMHT20', #25
    #EWK triggers
    'HLT_Ele25_WP80_PFMT40', #26
    'HLT_Ele27_WP70_PFMT40_PFMHT20', #27


    #SingleElectron PD
    'HLT_Ele27_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT', #28
    'HLT_Ele25_CaloIdL_CaloIsoVL_TrkIdVL_TrkIsoVL', #29
    'HLT_Ele32_CaloIdVL_CaloIsoVL_TrkIdVL_TrkIsoVL', #30
    'HLT_Ele32_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT', #31
    ]

    result = "Trigger.HLTResults[%d] > 0" % hltTriggers.index('HLT_Ele25_CaloIdVT_TrkIdT_CentralTriJet30')
    HLT_Ele25_CaloIdVT_TrkIdT_CentralTriJet30 = "((Event.Run >= 160404 && Event.Run <= 163869) && " + result + ')'

    result = "Trigger.HLTResults[%d] > 0" % hltTriggers.index('HLT_Ele25_CaloIdVT_TrkIdT_TriCentralJet30')
    HLT_Ele25_CaloIdVT_TrkIdT_TriCentralJet30 = "((Event.Run > 163869 && Event.Run <= 165633) && " + result + ')'

    result = "Trigger.HLTResults[%d] > 0" % hltTriggers.index('HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralJet30')
    HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralJet30 = "((Event.Run > 165633) && " + result + ')'
    hltCut = TCut(HLT_Ele25_CaloIdVT_TrkIdT_CentralTriJet30 + '||' + HLT_Ele25_CaloIdVT_TrkIdT_TriCentralJet30 + '||' + HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralJet30)
    return hltCut

def getElectronCut():
    electronPt = TCut("selectedPatElectronsLoosePFlow.Pt > 30")
    electronIsoCut = TCut("((selectedPatElectronsLoosePFlow.PFGammaIso + selectedPatElectronsLoosePFlow.PfChargedHadronIso + selectedPatElectronsLoosePFlow.PfNeutralHadronIso)/selectedPatElectronsLoosePFlow.Pt) > 0.1")
    electronID = TCut("selectedPatElectronsLoosePFlow.PassID >= 32")
    electronD0 = TCut("fabs(selectedPatElectronsLoosePFlow.dB) < 0.02")
    electronZDistance = TCut("fabs(selectedPatElectronsLoosePFlow.VtxDistZ) < 1")
    electronEta = TCut("fabs(selectedPatElectronsLoosePFlow.Eta) < 2.5")
    electronNotInCrack = TCut("(( fabs(selectedPatElectronsLoosePFlow.SCEta) < 1.4442) || ( fabs(selectedPatElectronsLoosePFlow.SCEta) > 1.5660)")
    goodPFIsoElectronCut = TCut(electronPt)
    goodPFIsoElectronCut += electronIsoCut
    goodPFIsoElectronCut += electronID
    goodPFIsoElectronCut += electronD0
    goodPFIsoElectronCut += electronZDistance
    goodPFIsoElectronCut += electronEta
    
    
    onlyOnegoodPFIsoElectronCut = TCut("Sum$(%s) == 1" % goodPFIsoElectronCut.GetTitle())
    return onlyOnegoodPFIsoElectronCut


def getLooseMuonVeto():
    muonPt = TCut("selectedPatMuonsLoosePFlow.Pt > 10")
    muonPt = TCut("selectedPatMuonsLoosePFlow.Pt > 10")
    muonPt = TCut("selectedPatMuonsLoosePFlow.Pt > 10")
def enableVariables(chain):
    setStatus = chain.SetBranchStatus
    setStatus("*", 0);
    setStatus("Event.Run", 1);
    setStatus("Event.Number", 1);
    setStatus("Event.LumiSection", 1)
    setStatus("Trigger.HLTResults", 1)
    setStatus("selectedPatElectronsLoosePFlow.Pt", 1)
    setStatus("selectedPatElectronsLoosePFlow.PFGammaIso", 1)
    setStatus("selectedPatElectronsLoosePFlow.PfChargedHadronIso", 1)
    setStatus("selectedPatElectronsLoosePFlow.PfNeutralHadronIso", 1)
    setStatus("selectedPatElectronsLoosePFlow.PassID", 1)
    setStatus("selectedPatElectronsLoosePFlow.dB", 1)
    setStatus("selectedPatElectronsLoosePFlow.VtxDistZ", 1)
    setStatus("selectedPatElectronsLoosePFlow.Eta", 1)
    setStatus("selectedPatElectronsLoosePFlow.SCEta", 1)
    
    

def getCutResult(chain, cut):
    nEvents = chain.Draw("Event.Run", cut)
    return nEvents

def getCutFlow(chain):
    cutflow = []
    hltCut = getHLTCut()
    electronCut = getElectronCut()
    upToElectronCut = TCut(hltCut)
    upToElectronCut+= electronCut
    hltResult = getCutResult(chain, hltCut)
    onlyOneGoodElectron = getCutResult(chain, hltCut + electronCut)
    cutflow.append( ('HLT',hltResult))
    cutflow.append( ('== 1 isolated good electron',onlyOneGoodElectron))
    return cutflow

def getCutFlowMulti(listOfChains):
    jobs = []
    for chain in listOfChains:
        p = Process(target = getCutFlow, args = (chain,))
        jobs.append(p)
        p.start()
        
    result = 0
    for job in jobs:
        job.join()
#    pool = Pool(processes=2)              # start n worker processes
#    results = [pool.apply_async(getCutFlow, [chain]) for chain in lis]
#    result = sum(pool.map(getCutFlow, listOfChains))
    return result 
    
if __name__ == '__main__':
    chain = TChain("rootTupleTree/tree")
#    chain1 = TChain("rootTupleTree/tree")
#    chain2 = TChain("rootTupleTree/tree")
#    chain3 = TChain("rootTupleTree/tree")
#    chain4  = TChain("rootTupleTree/tree")
#    chain5 = TChain("rootTupleTree/tree")
#    chain6 = TChain("rootTupleTree/tree")

#    chain1.Add("/storage/TopQuarkGroup/data/ElectronHad/nTuple_v2b_Run2011-May10ReReco_GoldenJSON/db3f92ba514324d173b9a1664acdc31b/*.root");#203.815529928 pb-1
#    chain1.Add("/storage/TopQuarkGroup/data/ElectronHad/nTuple_v2b_Run2011-PromptReco_GoldenJSON_exclRereco/db3f92ba514324d173b9a1664acdc31b/*.root");#294.450534905 pb-1
#    
#    chain2.Add("/storage/TopQuarkGroup/data/ElectronHad/nTuple_v2b_Run2011-PromptReco_GoldenJSON_24.06.11-01.07.11/4ee1203e97f9a00957561f563636708a/*.root");#94 pb-1
#    chain2.Add("/storage/TopQuarkGroup/data/ElectronHad/nTuple_v2b_Run2011-PromptReco_GoldenJSON_10.06.11-17.06.11/c43a0fd1e74060a8f9608df5f5bafba0/*.root");#216.429549292 pb-1
#    chain2.Add("/storage/TopQuarkGroup/data/ElectronHad/nTuple_v2b_Run2011-PromptReco_GoldenJSON_01.07.11-06.07.11/4ee1203e97f9a00957561f563636708a/*.root");#115 pb-1
#    chain4.Add("/storage/TopQuarkGroup/data/ElectronHad/nTuple_v2b_Run2011-PromptReco_GoldenJSON_17.06.11-24.06.11/4ee1203e97f9a00957561f563636708a/*.root");#166 pb-1
    
    
#    chain.Add("/storage/TopQuarkGroup/data/ElectronHad/nTuple_v2b_Run2011-May10ReReco_GoldenJSON/db3f92ba514324d173b9a1664acdc31b/*.root");#203.815529928 pb-1
#    chain.Add("/storage/TopQuarkGroup/data/ElectronHad/nTuple_v2b_Run2011-PromptReco_GoldenJSON_exclRereco/db3f92ba514324d173b9a1664acdc31b/*.root");#294.450534905 pb-1
#    chain.Add("/storage/TopQuarkGroup/data/ElectronHad/nTuple_v2b_Run2011-PromptReco_GoldenJSON_10.06.11-17.06.11/c43a0fd1e74060a8f9608df5f5bafba0/*.root");#216.429549292 pb-1
#    chain.Add("/storage/TopQuarkGroup/data/ElectronHad/nTuple_v2b_Run2011-PromptReco_GoldenJSON_17.06.11-24.06.11/4ee1203e97f9a00957561f563636708a/*.root");#166 pb-1
#    chain.Add("/storage/TopQuarkGroup/data/ElectronHad/nTuple_v2b_Run2011-PromptReco_GoldenJSON_24.06.11-01.07.11/4ee1203e97f9a00957561f563636708a/*.root");#94 pb-1
#    chain.Add("/storage/TopQuarkGroup/data/ElectronHad/nTuple_v2b_Run2011-PromptReco_GoldenJSON_01.07.11-06.07.11/4ee1203e97f9a00957561f563636708a/*.root");#115 pb-1
    
    #test file
    chain.Add("/storage/TopQuarkGroup/data/ElectronHad/nTuple_v2b_Run2011-PromptReco_GoldenJSON_01.07.11-06.07.11/4ee1203e97f9a00957561f563636708a/ElectronHad_nTuple_42x_data_1_1_lNO.root");#115 pb-1
                        
    gROOT.ProcessLine("gErrorIgnoreLevel = 3001;"); 
    gROOT.SetBatch(True)    
                   


    
    
    watch = TStopwatch()
    watch.Start()
    cutflow =  getCutFlow(chain)
    watch.Stop()
    watch.Print()
    
    for name, value in cutflow:
        print name, '  ', value
    
#    watch.Reset()
#    watch.Start()
#    print getCutFlowMulti([chain1, chain2])
#    watch.Stop()
#    watch.Print()
    
#print HLT_Ele25_CaloIdVT_TrkIdT_CentralTriJet30
#print HLT_Ele25_CaloIdVT_TrkIdT_TriCentralJet30
#print HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralJet30
#print
#print hltCut.GetTitle()
        

                        