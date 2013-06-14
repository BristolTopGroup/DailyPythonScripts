'''
Created on 19 Jan 2013

@author: kreczko
'''

# 7 TeV
electron_qcd_samples = [ 'QCD_Pt-20to30_BCtoE',
                 'QCD_Pt-30to80_BCtoE',
                 'QCD_Pt-80to170_BCtoE',
                 'QCD_Pt-20to30_EMEnriched',
                 'QCD_Pt-30to80_EMEnriched',
                 'QCD_Pt-80to170_EMEnriched',
                 'GJets_HT-40To100',
                 'GJets_HT-100To200',
                 'GJets_HT-200']
singleTop_samples = [ 'T_tW-channel',
             'T_t-channel',
             'T_s-channel',
             'Tbar_tW-channel',
             'Tbar_t-channel',
             'Tbar_s-channel']
wplusjets_samples = [ 'W1Jet', 'W2Jets', 'W3Jets', 'W4Jets']
vplusjets_samples = wplusjets_samples
vplusjets_samples.append('DYJetsToLL')
diboson_samples = [ 'WWtoAnything', 'WZtoAnything', 'ZZtoAnything']
signal_samples = [ 'TTJet', 'SingleTop']

sample_summations = {
                  'QCD_Electron':electron_qcd_samples,
                  'SingleTop' : singleTop_samples,
                  'WJets' : wplusjets_samples,
                  'VJets' : vplusjets_samples,
                  'DiBoson': diboson_samples,
                  'Signal': signal_samples
                  }
