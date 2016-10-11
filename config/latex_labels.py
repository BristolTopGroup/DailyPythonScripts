'''
Created on 4 May 2013

@author: kreczko
'''
b_tag_bins_latex = {'0btag':'0 b tags', '0orMoreBtag':'$\geq$ 0 b tags', '1btag':'1 b tag',
                    '1orMoreBtag':'$\geq$ 1 b tags',
                    '2btags':'2 b tags', '2orMoreBtags':'$\geq$ 2 b tags',
                    '3btags':'3 b tags', '3orMoreBtags':'$\geq$ 3 b tags',
                    '4orMoreBtags':'$\geq$ 4 b tags'}
    
variables_latex = {
    'MET': '\ensuremath{E_{\mathrm{T}}^{\mathrm{miss}}}',
    'HT': '\ensuremath{H_{\mathrm{T}}}',
    'ST': '\ensuremath{S_{\mathrm{T}}}',
    'WPT': '\ensuremath{p^{\mathrm{W}}_{\mathrm{T}}}',
    'MT': '\ensuremath{M^{\mathrm{W}}_{\mathrm{T}}}'
    }

ttBarLatex = '$\mathrm{t}\\bar{\mathrm{t}}$'

measurements_latex = {'unfolded': 'unfolded',
                        'measured': 'measured',
                        'MADGRAPH':  'Madgraph Pythia6',
                        'MADGRAPH_ptreweight': 'Madgraph+$p_\mathrm{T}$ reweighting',
                        'MCATNLO': 'MC@NLO Herwig6',
                        'powheg_v1_pythia': 'Powheg (v1) Pythia6',
                        'powheg_v2_pythia': 'Powheg (v2) Pythia6',
                        'powheg_v1_herwig': 'Powheg (v1) Herwig6',
                        'powheg_v2_herwig': 'Powheg (v2) Herwig6',
                        'matchingdown':  'Matching down',
                        'matchingup':  'Matching up',
                        'scaledown':  '$Q^{2}$ down',
                        'scaleup':  '$Q^{2}$ up',
                        'TTJets_matchingdown':  'Matching down',
                        'TTJets_matchingup':  'Matching up',
                        'TTJets_scaledown':  '$Q^{2}$ down',
                        'TTJets_scaleup':  '$Q^{2}$ up',
                        'TTJets_massdown':  'Top mass down',
                        'TTJets_massup':  'Top mass up',
                        'VJets_matchingdown': 'V+jets (matching down)',
                        'VJets_matchingup': 'V+jets (matching up)',
                        'VJets_scaledown': 'V+jets ($Q^{2}$ down)',
                        'VJets_scaleup': 'V+jets ($Q^{2}$ up)',
                        'BJet_down':'b tagging efficiency $-1\sigma$',
                        'BJet_up':'b tagging efficiency $+1\sigma$',
                        'JES_down':'Jet energy scale $-1\sigma$',
                        'JES_up':'Jet energy scale $+1\sigma$',
                        'JER_down':'Jet energy resolution $-1\sigma$',
                        'JER_up':'Jet energy resolution $+1\sigma$',
                        'LightJet_down':'b tagging mis-tag rate $-1\sigma$',
                        'LightJet_up':'b tagging mis-tag rate $+1\sigma$',
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
                        'TTJet_cross_section+' : ttBarLatex + ' cross section $+1\sigma$',
                        'TTJet_cross_section-' : ttBarLatex + ' cross section $-1\sigma$',
                        'SingleTop_cross_section+' : 'Single top cross section $+1\sigma$',
                        'SingleTop_cross_section-' : 'Single top cross section $-1\sigma$',
                        'V+Jets_cross_section+': 'V+jets cross section \ensuremath{+1\sigma}',
                        'V+Jets_cross_section-': 'V+jets cross section \ensuremath{-1\sigma}',
                        'QCD_cross_section+': 'QCD cross section \ensuremath{+1\sigma}',
                        'QCD_cross_section-': 'QCD cross section \ensuremath{-1\sigma}',
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
                 'data':'Data',
                 'QCD':'QCD',
                 'WJets':'W $\\rightarrow \ell\\nu$',
                 'ZJets':'Z/$\gamma^*$ + jets',
                 'TTJet':ttBarLatex,
                 'SingleTop':'Single Top'  ,
                 'V+Jets' : 'W/Z + jets'               
                 }

fit_variables_latex = {
                       'absolute_eta' : r'lepton $|\eta|$',
                       'M3' : r'$M_3$',
                       'M_bl' : r'$M(b,l)$',
                       'angle_bl' : r'$\alpha$',
                       }

typical_systematics_latex = {"typical_systematics_electron": "Electron trigger efficiency \& electron selection",
                      "typical_systematics_muon": "Muon trigger efficiency \& muon selection",
                      "typical_systematics_btagging": "b-tagging",
                      "typical_systematics_JES": "Jet Energy Scale",
                      "typical_systematics_JER": "Jet Energy Resolution",
                      "typical_systematics_PU": "Pileup",
                      "typical_systematics_hadronisation": "Hadronisation",
                      "typical_systematics_QCD_shape": "QCD shape",
                      "typical_systematics_PDF": "PDF uncertainties",
                      "typical_systematics_top_mass": "Top mass",
                      "typical_systematics_theoretical": "Theoretical systematics",
                      'typical_systematics_background_other': 'Background (other)',
                      'typical_systematics_MET': '$E_{\mathrm{T}}^{\mathrm{miss}}$ uncertainties',
                      'typical_systematics_pt_reweight': '$p_\mathrm{T}$ reweighting'
                      }

channel_latex = {
                 'electron' : r"e + jets",
                 'muon' : r"$\mu$ + jets",
                 'combined' : r"e, $\mu$ + jets combined",
                 }