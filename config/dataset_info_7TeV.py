####################################################################################################
#MCInfo V6
####################################################################################################
#cross-section: the cross-section of the MC process in pb-1, 
#twiki: https://twiki.cern.ch/twiki/bin/viewauth/CMS/StandardModelCrossSections
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
#dataset_info['TTJet'] = {"cross-section": 157.5, "NumberOfProcessedEvents":29475803}
#if using the designated subset:
dataset_info['TTJet'] = {"cross-section": 164.5, "NumberOfProcessedEvents":7483496}
dataset_info['WJetsToLNu'] = {"cross-section": 31314., "NumberOfProcessedEvents":0 }
#from https://twiki.cern.ch/twiki/bin/view/CMS/SingleTopMoscowTuples
#more: http://prl.aps.org/abstract/PRL/v106/i9/e092001
dataset_info['W1Jet'] = {"cross-section": 4480., "NumberOfProcessedEvents":12594068 }
dataset_info['W2Jets'] = {"cross-section": 1674., "NumberOfProcessedEvents":25232812}
dataset_info['W3Jets'] = {"cross-section": 484.7, "NumberOfProcessedEvents":7685939}
dataset_info['W4Jets'] = {"cross-section": 211.7, "NumberOfProcessedEvents":13071340}

dataset_info['DYJetsToLL'] = {"cross-section": 3048., "NumberOfProcessedEvents":36222153}

dataset_info['GJets_HT-40To100'] = {"cross-section": 23620., "NumberOfProcessedEvents":12730863}
dataset_info['GJets_HT-100To200'] = {"cross-section": 3476., "NumberOfProcessedEvents":1536287}
dataset_info['GJets_HT-200'] = {"cross-section": 485., "NumberOfProcessedEvents":9377168}

dataset_info['QCD_Pt-20to30_BCtoE'] = {"cross-section": 0.2355e9 * 0.00046, "NumberOfProcessedEvents":2002588}
dataset_info['QCD_Pt-30to80_BCtoE'] = {"cross-section": 0.0593e9 * 0.00234, "NumberOfProcessedEvents":2030030}
dataset_info['QCD_Pt-80to170_BCtoE'] = {"cross-section": 0.906e6 * 0.0104, "NumberOfProcessedEvents":1082690}

dataset_info['QCD_Pt-20to30_EMEnriched'] = {"cross-section": 0.2355e9 * 0.0073, "NumberOfProcessedEvents":34720808}
dataset_info['QCD_Pt-30to80_EMEnriched'] = {"cross-section": 0.0593e9 * 0.059, "NumberOfProcessedEvents":70375915}
dataset_info['QCD_Pt-80to170_EMEnriched'] = {"cross-section": 0.906e6 * 0.148, "NumberOfProcessedEvents":8150669}

dataset_info['QCD_Pt-20_MuEnrichedPt-15'] = {"cross-section": 84679.3, "NumberOfProcessedEvents":25080199}

dataset_info['T_s-channel'] = {"cross-section": 2.72, "NumberOfProcessedEvents":259971}
dataset_info['T_t-channel'] = {"cross-section": 42.6, "NumberOfProcessedEvents":3814228}
dataset_info['T_tW-channel'] = {"cross-section": 5.3, "NumberOfProcessedEvents":814390}

dataset_info['Tbar_s-channel'] = {"cross-section": 1.49, "NumberOfProcessedEvents":137980}
dataset_info['Tbar_t-channel'] = {"cross-section": 22.0, "NumberOfProcessedEvents":1944822}
dataset_info['Tbar_tW-channel'] = {"cross-section": 5.3, "NumberOfProcessedEvents":809984}

dataset_info['WWtoAnything'] = {"cross-section": 43., "NumberOfProcessedEvents":4225857}
dataset_info['WZtoAnything'] = {"cross-section": 18.2, "NumberOfProcessedEvents":4265171}
dataset_info['ZZtoAnything'] = {"cross-section": 5.9, "NumberOfProcessedEvents":4190973}
#leaving non-used samples in comments for future use
#Ttbar + Z/W from http://cms.cern.ch/iCMS/jsp/openfile.jsp?tp=draft&files=AN2011_288_v14.pdf
#dataset_info['TTbarZIncl'] = {"cross-section": 0.14, "NumberOfProcessedEvents":196277}
#dataset_info['TTbarInclWIncl'] = {"cross-section": 0.16, "NumberOfProcessedEvents":349038}

#systematic samples
dataset_info['TTJets-matchingdown'] = {"cross-section": 764., "NumberOfProcessedEvents":1607808}
dataset_info['TTJets-matchingup'] = {"cross-section": 172., "NumberOfProcessedEvents":4029823}
dataset_info['TTJets-scaledown'] = {"cross-section": 552., "NumberOfProcessedEvents":3990597}
dataset_info['TTJets-scaleup'] = {"cross-section": 200., "NumberOfProcessedEvents":3603380}

dataset_info['WJets-matchingdown'] = {"cross-section": 42352, "NumberOfProcessedEvents":9954652}
dataset_info['WJets-matchingup'] = {"cross-section": 11439, "NumberOfProcessedEvents":10459163}
dataset_info['WJets-scaledown'] = {"cross-section": 20137, "NumberOfProcessedEvents":6958027}
dataset_info['WJets-scaleup'] = {"cross-section": 17859, "NumberOfProcessedEvents":9724308}

dataset_info['ZJets-matchingdown'] = {"cross-section": 3048., "NumberOfProcessedEvents":1614808}
dataset_info['ZJets-matchingup'] = {"cross-section": 3048., "NumberOfProcessedEvents":1641121}
dataset_info['ZJets-scaledown'] = {"cross-section": 3048., "NumberOfProcessedEvents":1619875}
dataset_info['ZJets-scaleup'] = {"cross-section": 3048., "NumberOfProcessedEvents":1592742}
