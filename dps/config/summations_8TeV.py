
# 8 TeV
electron_qcd_samples = [ 'QCD_Pt_20_30_BCtoE',
                         'QCD_Pt_30_80_BCtoE',
                         'QCD_Pt_80_170_BCtoE',
                         'QCD_Pt_170_250_BCtoE',
                         'QCD_Pt_250_350_BCtoE',
                         'QCD_Pt_350_BCtoE',
                         'QCD_Pt_20_30_EMEnriched',
                         'QCD_Pt_30_80_EMEnriched',
                         'QCD_Pt_80_170_EMEnriched',
                         'QCD_Pt_170_250_EMEnriched',
                         'QCD_Pt_250_350_EMEnriched',
                         'QCD_Pt_350_EMEnriched',
                         'GJets_HT-200To400',
                         'GJets_HT-400ToInf']
muon_qcd_samples = [ 'QCD_Pt-15to20_MuEnrichedPt5',
		     'QCD_Pt-20to30_MuEnrichedPt5',
		     'QCD_Pt-30to50_MuEnrichedPt5',
		     'QCD_Pt-50to80_MuEnrichedPt5',
		     'QCD_Pt-80to120_MuEnrichedPt5',
		     'QCD_Pt-120to170_MuEnrichedPt5',
		     'QCD_Pt-170to300_MuEnrichedPt5',
		     'QCD_Pt-300to470_MuEnrichedPt5',
		     'QCD_Pt-470to600_MuEnrichedPt5',
		     'QCD_Pt-600to800_MuEnrichedPt5',
		     'QCD_Pt-800to1000_MuEnrichedPt5',
		     'QCD_Pt-1000_MuEnrichedPt5']
singleTop_samples = [ 'T_tW-channel',
             'T_t-channel',
             'T_s-channel',
             'Tbar_tW-channel',
             'Tbar_t-channel',
             'Tbar_s-channel' ]
wplusjets_samples = [ 'W1Jet', 'W2Jets', 'W3Jets', 'W4Jets' ]
dyplusjets_samples = [ 'DY1JetsToLL', 'DY2JetsToLL', 'DY3JetsToLL', 'DY4JetsToLL' ]
vplusjets_samples = wplusjets_samples + dyplusjets_samples
diboson_samples = [ 'WWtoAnything', 'WZtoAnything', 'ZZtoAnything' ]
signal_samples = [ 'TTJet', 'SingleTop']

wplusjets_matchingup_samples = [ 'WJets-matchingup' ]
dyplusjets_matchingup_samples = [ 'ZJets-matchingup' ]
vplusjets_matchingup_samples = wplusjets_matchingup_samples + dyplusjets_matchingup_samples

wplusjets_matchingdown_samples = [ 'WJets-matchingdown' ]
dyplusjets_matchingdown_samples = [ 'ZJets-matchingdown' ]
vplusjets_matchingdown_samples = wplusjets_matchingdown_samples + dyplusjets_matchingdown_samples

wplusjets_scaledown_samples = [ 'WJets-scaledown' ]
dyplusjets_scaledown_samples = [ 'ZJets-scaledown' ]
vplusjets_scaledown_samples = wplusjets_scaledown_samples + dyplusjets_scaledown_samples

wplusjets_scaleup_samples = [ 'WJets-scaleup' ]
dyplusjets_scaleup_samples = [ 'ZJets-scaleup' ]
vplusjets_scaleup_samples = wplusjets_scaleup_samples + dyplusjets_scaleup_samples

ttjets_unfolding_samples = ['TTJets']
ttjets_mcatnlo_unfolding_samples = ['TTJets']
ttjets_powheg_unfolding_samples = ['TTJets']
ttjets_matchingup_unfolding_samples = ['TTJets-matchingup']
ttjets_matchingdown_unfolding_samples = ['TTJets-matchingdown']
ttjets_scaleup_unfolding_samples = ['TTJets-scaleup']
ttjets_scaledown_unfolding_samples = ['TTJets-scaledown']

sample_summations = {
                  'QCD_Electron':electron_qcd_samples,
                  'QCD_Muon':muon_qcd_samples,
                  'SingleTop' : singleTop_samples,
                  'WJets' : wplusjets_samples,
                  'DYJets' : dyplusjets_samples,
                  'VJets' : vplusjets_samples,
                  'DiBoson': diboson_samples,
                  'Signal': signal_samples,
                  'VJets-matchingup' : vplusjets_matchingup_samples,
                  'VJets-matchingdown' : vplusjets_matchingdown_samples,
                  'VJets-scaledown' : vplusjets_scaledown_samples,
                  'VJets-scaleup' : vplusjets_scaleup_samples,
                  'unfolding_merged' : ttjets_unfolding_samples,
                  'unfolding_TTJets_8TeV_mcatnlo' : ttjets_mcatnlo_unfolding_samples,
                  'unfolding_TTJets_8TeV_powheg' : ttjets_powheg_unfolding_samples,
                  'unfolding_TTJets_8TeV_matchingup' : ttjets_matchingup_unfolding_samples,
                  'unfolding_TTJets_8TeV_matchingdown' : ttjets_matchingdown_unfolding_samples,
                  'unfolding_TTJets_8TeV_scaleup' : ttjets_scaleup_unfolding_samples,
                  'unfolding_TTJets_8TeV_scaledown' : ttjets_scaledown_unfolding_samples
                  }

