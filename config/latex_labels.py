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
                       'MT': 'M_{\mathrm{T}} (\ell, E_{\mathrm{T}}^{\mathrm{miss}})',
                       'WPT': '\mathrm{W} p_{\mathrm{T}}'}

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
                        'VJets_scaleup': 'V+jets ($Q^{2}$ up)',
                        'BJet_down':'b-jets -',
                        'BJet_up':'b-jets +',
                        'JES_down':'JES -',
                        'JES_up':'JES +',
                        'JER_down':'JER -',
                        'JER_up':'JER +',
                        'LightJet_down':'Light jet -',
                        'LightJet_up':'Light jet +',
                        'PU_down':'Pile-up -',
                        'PU_up':'Pile-up +',
                        'central':'central'
                          }

met_systematics_latex = {
                "ElectronEnUp":'Electron energy $+1\sigma$',
                "ElectronEnDown":'Electron energy $-1\sigma$',
                "MuonEnUp":'Muon energy $+1\sigma$',
                "MuonEnDown":'Muon energy $-1\sigma$',
                "TauEnUp":'Tau energy $+1\sigma$',
                "TauEnDown":'Tau energy $-1\sigma$',
                "JetResUp":'Jet resolution $+1\sigma$',
                "JetResDown":'Jet resolution $-1\sigma$',
                "JetEnUp":'Jet energy $+1\sigma$',
                "JetEnDown":'Jet energy $-1\sigma$',
                "UnclusteredEnUp":'Unclustered energy $+1\sigma$',
                "UnclusteredEnDown":'Unclustered energy $-1\sigma$'
}

samples_latex = {
                 'data':'data',
                 'QCD':'QCD',
                 'WJets':'W $\\rightarrow \ell\\nu$',
                 'ZJets':'Z/$\gamma^*$ + jets',
                 'TTJet':'$\mathrm{t}\\bar{\mathrm{t}}$',
                 'SingleTop':'Single-Top'                 
                 }
