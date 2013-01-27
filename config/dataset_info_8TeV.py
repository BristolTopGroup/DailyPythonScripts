####################################################################################################
#MCInfo V6
####################################################################################################
#cross-section: the cross-section of the MC process in pb-1, 
#twiki: https://twiki.cern.ch/twiki/bin/viewauth/CMS/StandardModelCrossSectionsat8TeV
####################################################################################################
#Number of processed events: Number of events processed by CRAB. Not identical to number of produced events if not all grid jobs succeed!
####################################################################################################
#Number of produced events: Number of total events in the parent sample, i.e. 
#https://cmsweb.cern.ch/das/request?view=list&limit=10&instance=cms_dbs_prod_global&input=dataset%3D%2FElectronHad%2FRun2011A-08Nov2011-v1%2FAOD
####################################################################################################
#Number of selected events: Number of events passing the pre-selection at the nTuple process
####################################################################################################
#Naming of the samples:
#Please use the same naming as in (names array)
#https://svnweb.cern.ch/trac/bat/browser/trunk/AnalysisTools/interface/DataTypes.h
####################################################################################################

dataset_info = {}
#dataset_info['TTJet'] = {"cross-section": 225.197, "NumberOfProcessedEvents":59414270}
#if using the designated subset:
dataset_info['TTJet'] = {"cross-section": 225.197, "NumberOfProcessedEvents":6920475}
dataset_info['WJetsToLNu'] = {"cross-section": 36257.2, "NumberOfProcessedEvents":57708550}
dataset_info['W1Jet'] = {"cross-section": 5400.0, "NumberOfProcessedEvents":23140779 }
dataset_info['W2Jets'] = {"cross-section": 1750.0, "NumberOfProcessedEvents":34041404}
dataset_info['W3Jets'] = {"cross-section": 519.0, "NumberOfProcessedEvents":15536443}
dataset_info['W4Jets'] = {"cross-section": 214.0, "NumberOfProcessedEvents":13370904}

dataset_info['DYJetsToLL'] = {"cross-section": 3503.71, "NumberOfProcessedEvents":30457954}
dataset_info['DY1JetsToLL'] = {"cross-section": 561.0, "NumberOfProcessedEvents":24042904}
dataset_info['DY2JetsToLL'] = {"cross-section": 181.0, "NumberOfProcessedEvents":21835749}
dataset_info['DY3JetsToLL'] = {"cross-section": 51.1, "NumberOfProcessedEvents":11010628}
dataset_info['DY4JetsToLL'] = {"cross-section": 23.04, "NumberOfProcessedEvents":6391785}

dataset_info['GJets_HT-40To100'] = {"cross-section": 23620., "NumberOfProcessedEvents":12659371}
dataset_info['GJets_HT-100To200'] = {"cross-section": 3476., "NumberOfProcessedEvents":1536287}
dataset_info['GJets_HT-200ToInf'] = {"cross-section": 485., "NumberOfProcessedEvents":9377170}

dataset_info['GJets_HT-200To400'] = {"cross-section": 960.5, "NumberOfProcessedEvents":10484464}
dataset_info['GJets_HT-400ToInf'] = {"cross-section": 107.5, "NumberOfProcessedEvents":1606586}

dataset_info['QCD_Pt_20_30_BCtoE'] = {"cross-section": 2.886e8 * 5.8e-4, "NumberOfProcessedEvents":1740223}
dataset_info['QCD_Pt_30_80_BCtoE'] = {"cross-section": 7.424e7 * 0.00225, "NumberOfProcessedEvents":2048147}
dataset_info['QCD_Pt_80_170_BCtoE'] = {"cross-section": 1191000.0 * 0.0109, "NumberOfProcessedEvents":1937602}
dataset_info['QCD_Pt_170_250_BCtoE'] = {"cross-section": 30980.0 * 0.0204, "NumberOfProcessedEvents":1945895}
dataset_info['QCD_Pt_250_350_BCtoE'] = {"cross-section": 4250.0 * 0.0243, "NumberOfProcessedEvents":2019922}
dataset_info['QCD_Pt_350_BCtoE'] = {"cross-section": 811.0 * 0.0295, "NumberOfProcessedEvents":1934813}

dataset_info['QCD_Pt_20_30_EMEnriched'] = {"cross-section": 2.886e8 * 0.0101, "NumberOfProcessedEvents":35005597}
dataset_info['QCD_Pt_30_80_EMEnriched'] = {"cross-section": 7.433e7 * 0.0621, "NumberOfProcessedEvents":28753832}
dataset_info['QCD_Pt_80_170_EMEnriched'] = {"cross-section": 1191000.0 * 0.1539, "NumberOfProcessedEvents":19295479}
dataset_info['QCD_Pt_170_250_EMEnriched'] = {"cross-section": 30990.0 * 0.148, "NumberOfProcessedEvents":31581299}
dataset_info['QCD_Pt_250_350_EMEnriched'] = {"cross-section": 4250.0 * 0.131, "NumberOfProcessedEvents":31034946}
dataset_info['QCD_Pt_350_EMEnriched'] = {"cross-section": 810.0 * 0.11, "NumberOfProcessedEvents":33478691}

dataset_info['QCD_Pt-20_MuEnrichedPt-15'] = {"cross-section": 3.64e8 * 3.7e-4, "NumberOfProcessedEvents":21484326}

dataset_info['QCD_Pt-15to20_MuEnrichedPt5'] = {"cross-section": 7.022e8 * 0.0039, "NumberOfProcessedEvents":1722678}
dataset_info['QCD_Pt-20to30_MuEnrichedPt5'] = {"cross-section": 2.87e8 * 0.0065, "NumberOfProcessedEvents":8486893}
dataset_info['QCD_Pt-30to50_MuEnrichedPt5'] = {"cross-section": 6.609e7 * 0.0122, "NumberOfProcessedEvents":8928999}
dataset_info['QCD_Pt-50to80_MuEnrichedPt5'] = {"cross-section": 8082000.0 * 0.0218, "NumberOfProcessedEvents":7256011}
dataset_info['QCD_Pt-80to120_MuEnrichedPt5'] = {"cross-section": 1024000.0 * 0.0395, "NumberOfProcessedEvents":9030624}
dataset_info['QCD_Pt-120to170_MuEnrichedPt5'] = {"cross-section": 157800.0 * 0.0473, "NumberOfProcessedEvents":8500505}
dataset_info['QCD_Pt-170to300_MuEnrichedPt5'] = {"cross-section": 34020.0 * 0.0676, "NumberOfProcessedEvents":7662483}
dataset_info['QCD_Pt-300to470_MuEnrichedPt5'] = {"cross-section": 1757.0 * 0.0864, "NumberOfProcessedEvents":7797481}
dataset_info['QCD_Pt-470to600_MuEnrichedPt5'] = {"cross-section": 115.2 * 0.1024, "NumberOfProcessedEvents":2995767}
dataset_info['QCD_Pt-600to800_MuEnrichedPt5'] = {"cross-section": 27.01 * 0.0996, "NumberOfProcessedEvents":0}
dataset_info['QCD_Pt-800to1000_MuEnrichedPt5'] = {"cross-section": 3.57 * 0.1033, "NumberOfProcessedEvents":4047142}
dataset_info['QCD_Pt-1000_MuEnrichedPt5'] = {"cross-section": 0.774 * 0.1097, "NumberOfProcessedEvents":3807263}

dataset_info['T_s-channel'] = {"cross-section": 3.89394, "NumberOfProcessedEvents":249516}
dataset_info['T_t-channel'] = {"cross-section": 55.531, "NumberOfProcessedEvents":3757707}
dataset_info['T_tW-channel'] = {"cross-section": 11.1773, "NumberOfProcessedEvents":497395}

dataset_info['Tbar_s-channel'] = {"cross-section": 1.75776, "NumberOfProcessedEvents":139948}
dataset_info['Tbar_t-channel'] = {"cross-section": 30.0042, "NumberOfProcessedEvents":1934817}
dataset_info['Tbar_tW-channel'] = {"cross-section": 11.1773, "NumberOfProcessedEvents":493239}

dataset_info['WWtoAnything'] = {"cross-section": 57.1097, "NumberOfProcessedEvents":4191740}
dataset_info['WZtoAnything'] = {"cross-section": 32.3161, "NumberOfProcessedEvents":4136765}
dataset_info['ZZtoAnything'] = {"cross-section": 8.25561, "NumberOfProcessedEvents":2408805}
#Ttbar + Z/W from http://cms.cern.ch/iCMS/jsp/openfile.jsp?tp=draft&files=AN2011_288_v14.pdf
dataset_info['TTbarZIncl'] = {"cross-section": 0.14, "NumberOfProcessedEvents":196277}
dataset_info['TTbarInclWIncl'] = {"cross-section": 0.16, "NumberOfProcessedEvents":349038}
#heavy flavour sample
dataset_info['VqqJets'] = {"cross-section": 35.3, "NumberOfProcessedEvents":720613}

#Z' samples
dataset_info['Zprime_M500GeV_W5GeV'] = {"cross-section": 50, "NumberOfProcessedEvents":0}
dataset_info['Zprime_M500GeV_W50GeV'] = {"cross-section": 50, "NumberOfProcessedEvents":0}
dataset_info['Zprime_M750GeV_W7500MeV'] = {"cross-section": 50, "NumberOfProcessedEvents":0}
dataset_info['Zprime_M1000GeV_W10GeV'] = {"cross-section": 50, "NumberOfProcessedEvents":0}
dataset_info['Zprime_M1000GeV_W100GeV'] = {"cross-section": 50, "NumberOfProcessedEvents":0}
dataset_info['Zprime_M1250GeV_W12500MeV'] = {"cross-section": 50, "NumberOfProcessedEvents":0}
dataset_info['Zprime_M1500GeV_W15GeV'] = {"cross-section": 50, "NumberOfProcessedEvents":0}
dataset_info['Zprime_M1500GeV_W150GeV'] = {"cross-section": 50, "NumberOfProcessedEvents":0}
dataset_info['Zprime_M2000GeV_W20GeV'] = {"cross-section": 50, "NumberOfProcessedEvents":0}
dataset_info['Zprime_M2000GeV_W200GeV'] = {"cross-section": 50, "NumberOfProcessedEvents":0}
dataset_info['Zprime_M3000GeV_W30GeV'] = {"cross-section": 50, "NumberOfProcessedEvents":0}
dataset_info['Zprime_M3000GeV_W300GeV'] = {"cross-section": 50, "NumberOfProcessedEvents":0}
dataset_info['Zprime_M4000GeV_W40GeV'] = {"cross-section": 50, "NumberOfProcessedEvents":0}
dataset_info['Zprime_M4000GeV_W400GeV'] = {"cross-section": 50, "NumberOfProcessedEvents":0}

#top samples with different top mass
dataset_info['TTJets161'] = {"cross-section": 157.5, "NumberOfProcessedEvents":1620072}
dataset_info['TTJets163'] = {"cross-section": 157.5, "NumberOfProcessedEvents":1633197}
dataset_info['TTJets166'] = {"cross-section": 157.5, "NumberOfProcessedEvents":1669034}
dataset_info['TTJets169'] = {"cross-section": 157.5, "NumberOfProcessedEvents":1606570}
dataset_info['TTJets175'] = {"cross-section": 157.5, "NumberOfProcessedEvents":1538301}
dataset_info['TTJets178'] = {"cross-section": 157.5, "NumberOfProcessedEvents":1648519}
dataset_info['TTJets181'] = {"cross-section": 157.5, "NumberOfProcessedEvents":1665350}
dataset_info['TTJets184'] = {"cross-section": 157.5, "NumberOfProcessedEvents":1671859}

#systematic samples
dataset_info['TTJets-matchingdown'] = {"cross-section": 130., "NumberOfProcessedEvents":5458456}
dataset_info['TTJets-matchingup'] = {"cross-section": 138., "NumberOfProcessedEvents":5412642}
dataset_info['TTJets-scaledown'] = {"cross-section": 228.0, "NumberOfProcessedEvents":5384596}
dataset_info['TTJets-scaleup'] = {"cross-section": 97.7, "NumberOfProcessedEvents":5007277}

dataset_info['WJets-matchingdown'] = {"cross-section": 29690.0, "NumberOfProcessedEvents":21364189}
dataset_info['WJets-matchingup'] = {"cross-section": 30290.0, "NumberOfProcessedEvents":20126095}
dataset_info['WJets-scaledown'] = {"cross-section": 33300.0, "NumberOfProcessedEvents":20760315}
dataset_info['WJets-scaleup'] = {"cross-section": 32000.0, "NumberOfProcessedEvents":19402929}

dataset_info['ZJets-matchingdown'] = {"cross-section": 2888.0, "NumberOfProcessedEvents":2091131}
dataset_info['ZJets-matchingup'] = {"cross-section": 2915.0, "NumberOfProcessedEvents":1985440}
dataset_info['ZJets-scaledown'] = {"cross-section": 3312.0, "NumberOfProcessedEvents":1934768}
dataset_info['ZJets-scaleup'] = {"cross-section": 2954.0, "NumberOfProcessedEvents":2126758}

#Data and not used samples
dataset_info['ElectronHad'] = {"cross-section": 0, "NumberOfProcessedEvents":0}
dataset_info['MuHad'] = {"cross-section": 0, "NumberOfProcessedEvents":0}
dataset_info['SingleElectron'] = {"cross-section": 0, "NumberOfProcessedEvents":0}
dataset_info['SingleMu'] = {"cross-section": 0, "NumberOfProcessedEvents":0}

#Old QCD samples (kept to avoid dictionary errors)
dataset_info['QCD_Pt-20to30_BCtoE'] = {"cross-section": 0.2355e9 * 0.00046, "NumberOfProcessedEvents":2081560}
dataset_info['QCD_Pt-30to80_BCtoE'] = {"cross-section": 0.0593e9 * 0.00234, "NumberOfProcessedEvents":2013126}
dataset_info['QCD_Pt-80to170_BCtoE'] = {"cross-section": 0.906e6 * 0.0104, "NumberOfProcessedEvents":1044013}

dataset_info['QCD_Pt-20to30_EMEnriched'] = {"cross-section": 0.2355e9 * 0.0073, "NumberOfProcessedEvents":34607077}
dataset_info['QCD_Pt-30to80_EMEnriched'] = {"cross-section": 0.0593e9 * 0.059, "NumberOfProcessedEvents":70376046}
dataset_info['QCD_Pt-80to170_EMEnriched'] = {"cross-section": 0.906e6 * 0.148, "NumberOfProcessedEvents":8150672}
