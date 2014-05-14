from copy import deepcopy

qcd_samples = [ 'QCD_Pt_20_30_BCtoE',
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
                'GJets_HT-400ToInf'
                ]

muon_qcd_samples = [ 'QCD_Pt-15to20_MuEnrichedPt5',
                     'QCD_Pt-20to30_MuEnrichedPt5',
                     'QCD_Pt-30to50_MuEnrichedPt5',
                     'QCD_Pt-50to80_MuEnrichedPt5',
                     'QCD_Pt-80to120_MuEnrichedPt5',
                     'QCD_Pt-120to170_MuEnrichedPt5',
                     'QCD_Pt-170to300_MuEnrichedPt5',
                     'QCD_Pt-300to470_MuEnrichedPt5',
                     'QCD_Pt-470to600_MuEnrichedPt5',
#                     'QCD_Pt-600to800_MuEnrichedPt5',
                     'QCD_Pt-800to1000_MuEnrichedPt5',
                     'QCD_Pt-1000_MuEnrichedPt5'
                    ]

singleTop_samples = [ 'T_tW-channel',
                 'T_t-channel',
                 'T_s-channel',
                 'Tbar_tW-channel',
                 'Tbar_t-channel',
                 'Tbar_s-channel']

wplusjets_samples = [ 'W1Jet', 'W2Jets', 'W3Jets', 'W4Jets']
zplusjets_samples = [ 'DY1JetsToLL', 'DY2JetsToLL', 'DY3JetsToLL', 'DY4JetsToLL' ]
vplusjets_samples = deepcopy(wplusjets_samples)
vplusjets_samples.append('DY1JetsToLL')
vplusjets_samples.append('DY2JetsToLL')
vplusjets_samples.append('DY3JetsToLL')
vplusjets_samples.append('DY4JetsToLL')
#diboson_samples = [ 'WWtoAnything', 'WZtoAnything', 'ZZtoAnything']
signal_samples = [ 'TTJet', 'SingleTop']
allMC_samples = [ 'TTJet', 'DYJetsToLL', 'QCD', 'W+Jets', 'SingleTop']

btag_bins_inclusive = ['0orMoreBtag', '1orMoreBtag', '2orMoreBtags', '3orMoreBtags']
btag_sums = {
             '0orMoreBtag':['0btag', '1btag', '2btags', '3btags', '4orMoreBtags'],
             '1orMoreBtag':['1btag', '2btags', '3btags', '4orMoreBtags'],
             '2orMoreBtags':['2btags', '3btags', '4orMoreBtags'],
             '3orMoreBtags':['3btags', '4orMoreBtags']
             }
