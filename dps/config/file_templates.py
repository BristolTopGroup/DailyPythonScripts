'''
Created on 13 Dec 2012

@author: kreczko
'''

suffix_default = 'PFElectron_PFMuon_PF2PATJets_PFMET.root'
suffixes = {
            'central': suffix_default,
            'JES_down': suffix_default.replace('.root', '_minusJES.root'),
            'JES_up': suffix_default.replace('.root', '_plusJES.root'),
            'PU_down': suffix_default.replace('.root', '_PU_64600mb.root'),
            'PU_up': suffix_default.replace('.root', '_PU_71400mb.root'),
            'BJet_down': suffix_default.replace('.root', '_minusBJet.root'),
            'BJet_up': suffix_default.replace('.root', '_plusBjet.root'),
            'LightJet_down': suffix_default.replace('.root', '_minusLightJet.root'),
            'LightJet_up': suffix_default.replace('.root', '_plusLightJet.root'),
            }

samples = [
         'ElectronHad', 'SingleMu', 'TTJet', 'DYJetsToLL', 'QCD_Pt-20_MuEnrichedPt-15',
         'QCD_Pt-20to30_BCtoE', 'QCD_Pt-30to80_BCtoE', 'QCD_Pt-80to170_BCtoE',
         'QCD_Pt-20to30_EMEnriched', 'QCD_Pt-30to80_EMEnriched', 'QCD_Pt-80to170_EMEnriched',
         'GJets_HT-40To100', 'GJets_HT-100To200', 'GJets_HT-200',
         'WWtoAnything', 'WZtoAnything', 'ZZtoAnything',
         'T_tW-channel', 'T_t-channel', 'T_s-channel', 'Tbar_tW-channel', 'Tbar_t-channel', 'Tbar_s-channel',
         'W1Jet', 'W2Jets', 'W3Jets', 'W4Jets',
         'TTJets-matchingdown', 'TTJets-matchingup', 'TTJets-scaledown', 'TTJets-scaleup',
         'WJets-matchingdown', 'WJets-matchingup', 'WJets-scaledown', 'WJets-scaleup',
         'ZJets-matchingdown', 'ZJets-matchingup', 'ZJets-scaledown', 'ZJets-scaleup'                 
                 ]

file_templates = {}

for name, suffix in suffixes.iteritems():
    file_templates[name] = {}
    for sample in samples:
        file_templates[name][sample] = name + '/' + sample + '%(luminosity_in_pbinv)dpb' + suffix
