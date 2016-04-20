'''
Created on 4 May 2013

@author: kreczko
'''
b_tag_bins_latex = {'0btag': '0 b-tags',
                    '0orMoreBtag': '$\geq$ 0 b-tags',
                    '1btag': '1 b-tag',
                    '1orMoreBtag': '$\geq$ 1 b-tags',
                    '2btags': '2 b-tags',
                    '2orMoreBtags': '$\geq$ 2 b-tags',
                    '3btags': '3 b-tags',
                    '3orMoreBtags': '$\geq$ 3 b-tags',
                    '4orMoreBtags': '$\geq$ 4 b-tags'
                    }

variables_latex = {
    'MET': '\ensuremath{E_{\mathrm{T}}^{\mathrm{miss}}}',
    'HT': '\ensuremath{H_{\mathrm{T}}}',
    'ST': '\ensuremath{S_{\mathrm{T}}}',
    'MT': '\ensuremath{M^{\mathrm{W}}_{\mathrm{T}}}',
    'WPT': '\ensuremath{p^\mathrm{W}_{\mathrm{T}}}',
    'lepTopPt': '\ensuremath{p^\mathrm{lep}_{\mathrm{T}}}',
    'hadTopPt': '\ensuremath{p^\mathrm{had}_{\mathrm{T}}}',
    'lepTopRap': '\ensuremath{y^\mathrm{lep}}',
    'hadTopRap': '\ensuremath{y^\mathrm{had}}',
    'ttbarPt': '\ensuremath{p^\mathrm{t\\bar{t}}_{\mathrm{T}}}',
    'ttbarM': '\ensuremath{M_\mathrm{t\\bar{t}}}',
    'ttbarRap': '\ensuremath{y_{\mathrm{t\\bar{t}}}}',
    'NJets': '\ensuremath{N_{\mathrm{Jets}}}',
    'lepton_pt': '\ensuremath{ p_{\mathrm{T}}^\mathrm{l} }',
    'lepton_pt_+': '\ensuremath{ p_{\mathrm{T}+}^\mathrm{l} }',
    'lepton_pt_-': '\ensuremath{ p_{\mathrm{T}-}^\mathrm{l} }',
    'lepton_eta': '\ensuremath{ \eta^\mathrm{l} }',
    'abs_lepton_eta': '\ensuremath{ |\eta^\mathrm{l}| }',
    'bjets_pt': '\ensuremath{ \mathrm{b-jet} p_{\mathrm{T}} }',
    'bjets_eta': '\ensuremath{ \mathrm{b-jet} \eta }',
    'sigmaietaieta' : '\ensuremath{\sigma_{i\eta i \eta}}',
}

variables_NonLatex = {
    'MET': 'MET',
    'HT': 'HT',
    'ST': 'ST',
    'WPT': 'WPT',
    'NJets': 'N Jets',
    'lepton_pt': 'lepton pt',
    'abs_lepton_eta': 'lepton eta',
}

control_plots_latex = {
    'NJets': '\ensuremath{N_{\mathrm{Jets}}}',
    'NBJets': '\ensuremath{N_{\mathrm{B Jets}}}',
    'pt': '\ensuremath{p_{\mathrm{T}}}',
    'eta': '\ensuremath{\eta}',
    'relIso_03_deltaBeta': "RelIso",
    'relIso_04_deltaBeta': "RelIso",
    'relIso': "RelIso",
    'NVertex' : '\# Vertex',
}

measurements_latex = {
    'unfolded': 'unfolded',
    'measured': 'measured',
    'MADGRAPH': '$t\\bar{t}$ (MADGRAPH+Pythia)',
    'MADGRAPH_ptreweight': '$t\\bar{t}$ (MADGRAPH+$p_\mathrm{T}^\mathrm{reweight}$)',
    'amcatnlo': 'aMC@NLO Pythia8',
    'amcatnlo_HERWIG': 'aMC@NLO Herwig++',
    'madgraphMLM': 'Madgraph Pythia8',
    'POWHEG_PYTHIA': '$t\\bar{t}$ (POWHEG+Pythia)',
    'powhegHERWIG': 'Powheg Herwig++',
    'powhegPythia8': 'Powheg Pythia8',
    'pythia8': '$t\\bar{t}$ (Pythia8)',
    'matchingdown': '$t\\bar{t}$ (matching down)',
    'matchingup': '$t\\bar{t}$ (matching up)',
    # 'scaledown': '$t\\bar{t}$ ($Q^{2}$ down)',
    # 'scaleup': '$t\\bar{t}$ ($Q^{2}$ up)',
    'scaledown': '$Q^{2}$ down',
    'scaleup': '$Q^{2}$ up',
    'TTJets_matchingdown': '$t\\bar{t}$ (matching down)',
    'TTJets_matchingup': '$t\\bar{t}$ (matching up)',
    # 'TTJets_scaledown': '$t\\bar{t}$ ($Q^{2}$ down)',
    # 'TTJets_scaleup': '$t\\bar{t}$ ($Q^{2}$ up)',
    'TTJets_scaledown': '$Q^{2}$ down',
    'TTJets_scaleup': '$Q^{2}$ up',
    'TTJets_massdown': '$t\\bar{t}$ (top mass down)',
    'TTJets_massup': '$t\\bar{t}$ (top mass up)',
    'VJets_matchingdown': 'V+jets (matching down)',
    'VJets_matchingup': 'V+jets (matching up)',
    'VJets_scaledown': 'V+jets ($Q^{2}$ down)',
    'VJets_scaleup': 'V+jets ($Q^{2}$ up)',
    'BJet_down': 'b-tagging efficiency $-1\sigma$',
    'BJet_up': 'b-tagging efficiency $+1\sigma$',
    'JES_down': 'Jet energy scale $-1\sigma$',
    'JES_up': 'Jet energy scale $+1\sigma$',
    'JES_down_alphaCorr': 'Jet energy scale $-1\sigma$ alphaCorr',
    'JES_up_alphaCorr': 'Jet energy scale $+1\sigma$ alphaCorr',
    'JER_down': 'Jet energy resolution $-1\sigma$',
    'JER_up': 'Jet energy resolution $+1\sigma$',
    'LightJet_down': 'b-tagging mis-tag rate $-1\sigma$',
    'LightJet_up': 'b-tagging mis-tag rate $+1\sigma$',
    'PU_down': 'Pile-up $-1\sigma$',
    'PU_up': 'Pile-up $+1\sigma$',
    'PileUpSystematic' : 'Pile-up',
    'central': 'central',
    #'ptreweight_max': '$p_\mathrm{T}(t,\\bar{t})$ reweighting',
    'TTJets_hadronisation': 'Hadronisation uncertainty',
    'TTJets_NLOgenerator': 'NLO generator',
    'PDF_total_lower': 'PDF uncertainty $-1\sigma$',
    'PDF_total_upper': 'PDF uncertainty $+1\sigma$',
    'QCD_shape': 'QCD shape uncertainty',
    'luminosity_up': 'Luminosity $+1\sigma$',
    'luminosity_down': 'Luminosity $-1\sigma$',
    'TTJet_cross_section_up': '$t\\bar{t}$ cross section $+1\sigma$',
    'TTJet_cross_section_down': '$t\\bar{t}$ cross section $-1\sigma$',
    'SingleTop_cross_section_up': 'Single top cross section $+1\sigma$',
    'SingleTop_cross_section_down': 'Single top cross section $-1\sigma$',
    'Electron_down': 'Electron efficiency $-1\sigma$',
    'Electron_up': 'Electron efficiency $+1\sigma$',
    'Muon_down': 'Muon efficiency $-1\sigma$',
    'Muon_up': 'Muon efficiency $+1\sigma$',
    'kValue_up': 'k Value $+1$',
    'kValue_down': 'k Value $-1$',
    'V+Jets_cross_section-': 'V+jets cross section \ensuremath{-1\sigma}',
    'V+Jets_cross_section+': 'V+jets cross section \ensuremath{+1\sigma}',
    'TTJet_cross_section-': '\ensuremath{t\\bar{t}} cross section \ensuremath{-1\sigma}',
    'TTJet_cross_section+': '\ensuremath{t\\bar{t}} cross section \ensuremath{+1\sigma}',
    'QCD_cross_section-': 'QCD cross section \ensuremath{-1\sigma}',
    'QCD_cross_section+': 'QCD cross section \ensuremath{+1\sigma}',
    'SingleTop_cross_section-': 'Single top cross section \ensuremath{-1\sigma}',
    'SingleTop_cross_section+': 'Single top cross section \ensuremath{+1\sigma}',
    'luminosity-': 'Luminosity \ensuremath{-1\sigma}',
    'luminosity+': 'Luminosity \ensuremath{+1\sigma}',
    'massdown': '$\mathrm{m}_{\mathrm{t}}$=169.5 GeV',
    'massup': '$\mathrm{m}_{\mathrm{t}}$=175.5 GeV',

}

met_systematics_latex = {
    "ElectronEnUp": 'Electron energy $+1\sigma$',
    "ElectronEnDown": 'Electron energy $-1\sigma$',
    "MuonEnUp": 'Muon energy $+1\sigma$',
    "MuonEnDown": 'Muon energy $-1\sigma$',
    "TauEnUp": 'Tau energy $+1\sigma$',
    "TauEnDown": 'Tau energy $-1\sigma$',
    "JetResUp": 'Jet resolution $+1\sigma$',
    "JetResDown": 'Jet resolution $-1\sigma$',
    "JetEnUp": 'Jet energy $+1\sigma$',
    "JetEnDown": 'Jet energy $-1\sigma$',
    "UnclusteredEnUp": 'Unclustered energy $+1\sigma$',
    "UnclusteredEnDown": 'Unclustered energy $-1\sigma$'
}

samples_latex = {
    'data': 'data',
    'QCD': 'QCD',
    'WJets': 'W $\\rightarrow \ell\\nu$',
    'ZJets': 'Z/$\gamma^*$ + jets',
    'TTJet': '$\mathrm{t}\\bar{\mathrm{t}}$',
    'SingleTop': 'Single-Top',
                 'V+Jets': 'W/Z + jets'
}

fit_variables_latex = {
    'absolute_eta': '\ensuremath{ \mathrm{lepton} |\eta| }',
    'M3': '\ensuremath{ M3 }',
    'M_bl': '\ensuremath{ M(b,l) }',
    'angle_bl': '\ensuremath{ \alpha }',
}

typical_systematics_latex = {
    "typical_systematics_electron": "Electron trigger efficiency \& electron selection",
    "typical_systematics_muon": "Muon trigger efficiency \& muon selection",
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

                 'electronQCDNonIso' : r"Non-iso e + jets",
                 'electronQCDConversions' : r"Conversion e + jets",
                 'muonQCDNonIso' : r"Non-iso $\mu$ + jets (iso $>$ 0.3)",
                 'muonQCDNonIso2' : r"Non-iso $\mu$ + jets (0.15 $<$ iso $<$ 0.3)",
                 }

fit_variables_units_latex = {
    'absolute_eta': '',
    'M3': 'GeV',
    'M_bl': 'GeV',
    'angle_bl': '',
}
