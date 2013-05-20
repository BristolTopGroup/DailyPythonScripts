'''
Created on 4 May 2013

@author: kreczko
'''
b_tag_bins_latex = {'0btag':'0 b-tags', '0orMoreBtag':'$\geq$ 0 b-tags', '1btag':'1 b-tags',
                    '1orMoreBtag':'$\geq$ 1 b-tags',
                    '2btags':'2 b-tags', '2orMoreBtags':'$\geq$ 2 b-tags',
                    '3btags':'3 b-tags', '3orMoreBtags':'$\geq$ 3 b-tags',
                    '4orMoreBtags':'$\geq$ 4 b-tags'}
    
variables_latex = {
                       'MET': 'E_{\mathrm{T}}^{\mathrm{miss}}',
                       'HT': 'H_{\mathrm{T}}',
                       'ST': 'S_{\mathrm{T}}',
                       'MT': 'M_{\mathrm{T}}',
                       'WPT': 'W p_{\mathrm{T}}'}

measurements_latex = {'unfolded': 'unfolded',
                        'measured': 'measured',
                        'MADGRAPH': '$t\\bar{t}$ (MADGRAPH)',
                        'MCATNLO': '$t\\bar{t}$ (MC@NLO)',
                        'POWHEG': '$t\\bar{t}$ (POWHEG)',
                        'matchingdown': '$t\\bar{t}$ (matching down)',
                        'matchingup': '$t\\bar{t}$ (matching up)',
                        'scaledown': '$t\\bar{t}$ ($Q^{2}$ down)',
                        'scaleup': '$t\\bar{t}$ ($Q^{2}$ up)',
                        'TTJets_matchingdown': '$t\\bar{t}$ (matching down)',
                        'TTJets_matchingup': '$t\\bar{t}$ (matching up)',
                        'TTJets_scaledown': '$t\\bar{t}$ ($Q^{2}$ down)',
                        'TTJets_scaleup': '$t\\bar{t}$ ($Q^{2}$ up)',
                        'VJets_matchingdown': 'V+jets (matching down)',
                        'VJets_matchingup': 'V+jets (matching up)',
                        'VJets_scaledown': 'V+jets ($Q^{2}$ down)',
                        'VJets_scaleup': 'V+jets ($Q^{2}$ up)'
                          }

samples_latex = {
                 'data':'data',
                 'QCD':'QCD',
                 'WJets':'W $\\rightarrow \ell\\nu$',
                 'ZJets':'Z/$\gamma^*$ + jets',
                 'TTJet':'$\mathrm{t}\\bar{\mathrm{t}}$',
                 'SingleTop':'Single-Top'                 
                 }
