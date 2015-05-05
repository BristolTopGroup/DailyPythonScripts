'''
Created on 4 May 2013

@author: kreczko
'''
b_tag_bins_latex = {'0btag':'0 b-tags', '0orMoreBtag':'$\geq$ 0 b-tags', '1btag':'1 b-tag',
                    '1orMoreBtag':'$\geq$ 1 b-tags',
                    '2btags':'2 b-tags', '2orMoreBtags':'$\geq$ 2 b-tags',
                    '3btags':'3 b-tags', '3orMoreBtags':'$\geq$ 3 b-tags',
                    '4orMoreBtags':'$\geq$ 4 b-tags'}
    
variables_latex = {
                       'MET': 'E_{\mathrm{T}}^{\mathrm{miss}}',
                       'HT': 'H_{\mathrm{T}}',
                       'ST': 'S_{\mathrm{T}}',
                       'MT': 'M^{\mathrm{W}}_{\mathrm{T}}',
                       'WPT': 'p^\mathrm{W}_{\mathrm{T}}'}

measurements_latex = {'unfolded': 'unfolded',
                        'measured': 'measured',
                        'MADGRAPH': '$t\\bar{t}$ (MADGRAPH+Pythia)',
                        'MADGRAPH_ptreweight': '$t\\bar{t}$ (MADGRAPH+$p_\mathrm{T}$^\mathrm{reweight})',
                        'MCATNLO': '$t\\bar{t}$ (MC@NLO+Herwig)',
                        'POWHEG_PYTHIA': '$t\\bar{t}$ (POWHEG+Pythia)',
                        'POWHEG_HERWIG': '$t\\bar{t}$ (POWHEG+Herwig)',
                        'matchingdown': '$t\\bar{t}$ (matching down)',
                        'matchingup': '$t\\bar{t}$ (matching up)',
                        'scaledown': '$t\\bar{t}$ ($Q^{2}$ down)',
                        'scaleup': '$t\\bar{t}$ ($Q^{2}$ up)',
                        'TTJets_matchingdown': '$t\\bar{t}$ (matching down)',
                        'TTJets_matchingup': '$t\\bar{t}$ (matching up)',
                        'TTJets_scaledown': '$t\\bar{t}$ ($Q^{2}$ down)',
                        'TTJets_scaleup': '$t\\bar{t}$ ($Q^{2}$ up)',
                        'TTJets_massdown': '$t\\bar{t}$ (top mass down)',
                        'TTJets_massup': '$t\\bar{t}$ (top mass up)',
                        'VJets_matchingdown': 'V+jets (matching down)',
                        'VJets_matchingup': 'V+jets (matching up)',
                        'VJets_scaledown': 'V+jets ($Q^{2}$ down)',
                        'VJets_scaleup': 'V+jets ($Q^{2}$ up)',
                        'BJet_down':'b-tagging efficiency $-1\sigma$',
                        'BJet_up':'b-tagging efficiency $+1\sigma$',
                        'JES_down':'Jet energy scale $-1\sigma$',
                        'JES_up':'Jet energy scale $+1\sigma$',
                        'JER_down':'Jet energy resolution $-1\sigma$',
                        'JER_up':'Jet energy resolution $+1\sigma$',
                        'LightJet_down':'b-tagging mis-tag rate $-1\sigma$',
                        'LightJet_up':'b-tagging mis-tag rate $+1\sigma$',
                        'PU_down':'Pile-up $-1\sigma$',
                        'PU_up':'Pile-up $+1\sigma$',
                        'central':'central',
                        'ptreweight_max': '$p_\mathrm{T}(t,\\bar{t})$ reweighting',
                        'hadronisation': 'Hadronisation uncertainty',
                        'PDF_total_lower': 'PDF uncertainty $-1\sigma$',
                        'PDF_total_upper': 'PDF uncertainty $+1\sigma$',
                        'QCD_shape' : 'QCD shape uncertainty',
                        'luminosity+' : 'Luminosity $+1\sigma$',
                        'luminosity-' : 'Luminosity $-1\sigma$',
                        'TTJet_cross_section+' : '$t\\bar{t}$ cross section $+1\sigma$',
                        'TTJet_cross_section-' : '$t\\bar{t}$ cross section $-1\sigma$',
                        'SingleTop_cross_section+' : 'Single top cross section $+1\sigma$',
                        'SingleTop_cross_section-' : 'Single top cross section $-1\sigma$',
                        'Electron_down' : 'Electron efficiency $-1\sigma$',
                        'Electron_up' : 'Electron efficiency $+1\sigma$',
                        'Muon_down' : 'Muon efficiency $-1\sigma$',
                        'Muon_up' : 'Muon efficiency $+1\sigma$',
                        'kValue_up' : 'k Value $+1$',
                        'kValue_down' : 'k Value $-1$',
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
                 'SingleTop':'Single-Top'  ,
                 'V+Jets' : 'W/Z + jets'               
                 }

fit_variables_latex = {
                       'absolute_eta' : r'lepton $|\eta|$',
                       'M3' : r'$M3$',
                       'M_bl' : r'$M(b,l)$',
                       'angle_bl' : r'angle$(b,l)$',
                       }

typical_systematics_latex = {"typical_systematics_electron": "Electron trigger efficiency \& selection",
                      "typical_systematics_muon": "Muon trigger efficiency \& selection",
                      "typical_systematics_btagging": "btagging",
                      "typical_systematics_JES": "Jet Energy Scale",
                      "typical_systematics_JER": "Jet Energy Resolution",
                      "typical_systematics_PU": "pileup",
                      "typical_systematics_hadronisation": "hadronisation",
                      "typical_systematics_QCD_shape": "QCD shape",
                      "typical_systematics_PDF": "PDF uncertainties",
                      "typical_systematics_top_mass": "top mass",
                      "typical_systematics_theoretical": "Theoretical systematics",
                      'typical_systematics_background_other': 'Background (other)',
                      'typical_systematics_MET': '$E_{T}^{miss}$ uncertainties',
                      'typical_systematics_pt_reweight': '$p_\mathrm{T}$ reweighting'
                      }

channel_latex = {
                 'electron' : r"e + jets",
                 'muon' : r"$\mu$ + jets",
                 'combined' : r"e, $\mu$ + jets combined",
                 }