'''
Created on 4 Apr 2013

@author: kreczko
'''

met_systematics_suffixes = [
        "ElectronEnUp",
        "ElectronEnDown",
        "MuonEnUp",
        "MuonEnDown",
        "TauEnUp",
        "TauEnDown",
        "JetResUp",
        "JetResDown",
        "JetEnUp",
        "JetEnDown",
        "UnclusteredEnUp",
        "UnclusteredEnDown"
        ]

analysis_types = {
                'electron':'EPlusJets',
                'muon':'MuPlusJets'
                }

#measurement script options
translate_options = {
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
                        'pf':'PFMET',
                        'type1':'patType1CorrectedPFMet',
                        }

ttbar_theory_systematic_prefix = 'TTJets_'
vjets_theory_systematic_prefix = 'VJets_'
