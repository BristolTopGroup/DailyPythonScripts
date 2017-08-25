'''
Created on 4 May 2013

@author: kreczko
'''
b_tag_bins_latex = {'0btag': '0 b-tags',
                    '0orMoreBtag': ' $\geq$ 0 b-tags',
                    '1btag': '1 b-tag',
                    '1orMoreBtag': ' $\geq$ 1 b-tags',
                    '2btags': '2 b-tags',
                    '2orMoreBtags': ' $\geq$ 2 b-tags',
                    '3btags': '3 b-tags',
                    '3orMoreBtags': ' $\geq$ 3 b-tags',
                    '4orMoreBtags': ' $\geq$ 4 b-tags'
                    }

variables_latex = {
    'MET': '\ensuremath{p_{\mathrm{T}}^{\mathrm{miss}}}',
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
    'abs_lepton_eta_coarse': '\ensuremath{ |\eta^\mathrm{l}| }',
    'bjets_pt': '\ensuremath{ \mathrm{b-jet} p_{\mathrm{T}} }',
    'bjets_eta': '\ensuremath{ \mathrm{b-jet} \eta }',
    'sigmaietaieta' : '\ensuremath{\sigma_{i\eta i \eta}}',
}

variables_NonLatex = {
    'MET': 'Missing Pt',
    'HT': 'HT',
    'ST': 'ST',
    'WPT': 'WPT',
    'NJets': 'N Jets',
    'lepton_pt': 'lepton pt',
    'abs_lepton_eta': 'lepton eta',
    'abs_lepton_eta_coarse': 'lepton eta',
}

control_plots_latex = {
    'NJets': '\ensuremath{N_{\mathrm{Jets}}}',
    'NBJets': '\ensuremath{N_{\mathrm{B Jets}}}',
    'pt': '\ensuremath{p_{\mathrm{T}}^{l}}',
    'jpt': '\ensuremath{p_{\mathrm{T}}^{\\text{jet}}}',
    'eta': '\ensuremath{\eta^{l}}',
    'relIso_03_deltaBeta': "RelIso",
    'relIso_04_deltaBeta': "RelIso",
    'relIso': "RelIso",
    'NVertex' : '\# Vertex',
}

measurements_latex = {
    'data'                      : 'Unfolded data',
    'unfolded'                  : 'unfolded',
    'measured'                  : 'measured',
    'central'                   : 'central',

    'TTJets_madgraphMLM'        : r'\textsc{MG5}\_a\textsc{MC@NLO (LO) \raisebox{.2ex}{+} Pythia8}',
    'TTJets_powhegPythia8'      : r'\textsc{Powheg \raisebox{.2ex}{+} Pythia8}',
    'TTJets_powhegHerwig'       : r'\textsc{Powheg \raisebox{.2ex}{+} Herwig\raisebox{.2ex}{++}}',
    'TTJets_amcatnloPythia8'    : r'\textsc{MG5}\_a\textsc{MC@NLO (NLO) \raisebox{.2ex}{+} Pythia8}',

    'TTJets_powhegPythia8_withMCTheoryUnc': r'with MC theory uncertainties',

    'TTJets_massdown'           : '$\mathrm{m}_{\mathrm{t}}$=169.5 GeV',
    'TTJets_massup'             : '$\mathrm{m}_{\mathrm{t}}$=175.5 GeV',
    'TTJets_uedown'             : 'UE down',
    'TTJets_ueup'               : 'UE up',
    'TTJets_fsrdown'            : 'FSR down',
    'TTJets_fsrup'              : 'FSR up',
    'TTJets_hdampdown'          : '$h_{damp}$ down',
    'TTJets_hdampup'            : '$h_{damp}$ up',

    'TTJets_scale'              : 'Renormalization and factorization scales',
    'TTJets_matching'           : 'ME/PS matching',
    'TTJets_fragup'             : 'Fragmentation Up',
    'TTJets_fragdown'           : 'Fragmentation Down',
    'TTJets_petersonFrag'       : 'Alternative fragmentation model',

    'TTJets_semiLepBrup'        : 'Decay Tables Up',
    'TTJets_semiLepBrdown'      : 'Decay Tables Down',
    'TTJets_erdOn'              : 'CR (erdOn)',
    'TTJets_QCDbased_erdOn'     : 'CR (QCD based)',
    'TTJets_GluonMove'          : 'CR (Gluon Move)',

    'TTJets_isrdown'            : 'ISR Down',
    'TTJets_isrup'              : 'ISR Up',
    'TTJets_scaledown'          : 'Shower Scales Up',
    'TTJets_scaleup'            : 'Shower Scales Down',
    'TTJets_alphaSup'           : 'alphaS Up',
    'TTJets_alphaSdown'         : 'alphaS Down',
    'TTJets_topPt'              : 'Reweighted top pt',
    'TTJets_factorisationup'    : 'Factorisation Scale Up',
    'TTJets_factorisationdown'  : 'Factorisation Scale Down',
    'TTJets_renormalisationup'  : 'Renormalisation Scale Up',
    'TTJets_renormalisationdown': 'Renormalisation Scale Down',
    'TTJets_combinedup'         : 'Combined Scale Up',
    'TTJets_combineddown'       : 'Combined Scale Down',

    'BJet_down'                 : 'b-tagging efficiency $-1\sigma$',
    'BJet_up'                   : 'b-tagging efficiency $+1\sigma$',
    'JES_down'                  : 'Jet energy scale $-1\sigma$',
    'JES_up'                    : 'Jet energy scale $+1\sigma$',
    'JER_down'                  : 'Jet energy resolution $-1\sigma$',
    'JER_up'                    : 'Jet energy resolution $+1\sigma$',
    'LightJet_down'             : 'b-tagging mis-tag rate $-1\sigma$',
    'LightJet_up'               : 'b-tagging mis-tag rate $+1\sigma$',
    'PU_down'                   : 'Pile-up $-1\sigma$',
    'PU_up'                     : 'Pile-up $+1\sigma$',
    'PileUpSystematic'          : 'Pile-up',

    #'ptreweight_max': '$p_\mathrm{T}(t,\\bar{t})$ reweighting',
    'PDF_total_lower'           : 'PDF uncertainty $-1\sigma$',
    'PDF_total_upper'           : 'PDF uncertainty $+1\sigma$',
    'QCD_shape'                 : 'QCD shape uncertainty',
    'luminosity_up'             : 'Luminosity $+1\sigma$',
    'luminosity_down'           : 'Luminosity $-1\sigma$',
    'TTJet_cross_section_up'    : '$t\\bar{t}$ cross section $+1\sigma$',
    'TTJet_cross_section_down'  : '$t\\bar{t}$ cross section $-1\sigma$',
    'SingleTop_cross_section_up'    : 'Single top cross section $+1\sigma$',
    'SingleTop_cross_section_down'  : 'Single top cross section $-1\sigma$',
    'Electron_down'             : 'Electron efficiency $-1\sigma$',
    'Electron_up'               : 'Electron efficiency $+1\sigma$',
    'Muon_down'                 : 'Muon efficiency $-1\sigma$',
    'Muon_up'                   : 'Muon efficiency $+1\sigma$',
    'V+Jets_cross_section-'     : 'V+jets cross section \ensuremath{-1\sigma}',
    'V+Jets_cross_section+'     : 'V+jets cross section \ensuremath{+1\sigma}',
    'TTJet_cross_section-'      : '\ensuremath{t\\bar{t}} cross section \ensuremath{-1\sigma}',
    'TTJet_cross_section+'      : '\ensuremath{t\\bar{t}} cross section \ensuremath{+1\sigma}',
    'QCD_cross_section-'        : 'QCD cross section \ensuremath{-1\sigma}',
    'QCD_cross_section+'        : 'QCD cross section \ensuremath{+1\sigma}',
    'SingleTop_cross_section-'  : 'Single top cross section \ensuremath{-1\sigma}',
    'SingleTop_cross_section+'  : 'Single top cross section \ensuremath{+1\sigma}',
    'luminosity-'               : 'Luminosity \ensuremath{-1\sigma}',
    'luminosity+'               : 'Luminosity \ensuremath{+1\sigma}',

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
    'data': 'Unfolded data',
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

systematics_latex = {
    'Electron'                : 'Electron efficiency',
    'Muon'                    : 'Muon efficiency',
    'ElectronEn'                : 'Electron energy in \ensuremath{p_{\mathrm{T}}^{\mathrm{miss}}}',
    'MuonEn'                    : 'Muon energy in \ensuremath{p_{\mathrm{T}}^{\mathrm{miss}}}',
    'TauEn'                     : 'Tau energy in \ensuremath{p_{\mathrm{T}}^{\mathrm{miss}}}',
    'UnclusteredEn'             : 'Unclustered energy in \ensuremath{p_{\mathrm{T}}^{\mathrm{miss}}}',
    'PileUp'                    : 'Pile-up',
    'BJet'                      : 'b-tagging efficiency',
    'JES'                       : 'JES',
    'JER'                       : 'JER',
    'luminosity'                : 'Luminosity',
    'V+Jets_cross_section'      : 'V+jets cross section',
    'SingleTop_cross_section'   : 'Single top cross section',
    'QCD_cross_section'         : 'QCD cross section',
    'QCD_shape'                 : 'QCD shape ',
    'PDF'                       : 'PDF ',
    'TTJets_topPt'              : 'Top \ensuremath{\pt}',
    'TTJets_mass'               : 'Top mass',
    'TTJets_scale'              : 'Renormalization and factorization scales',
    'TTJets_matching'           : 'ME/PS matching',
    'TTJets_ue'                 : 'Underlying event tune',
    'TTJets_frag'               : 'Fragmentation',
    'TTJets_petersonFrag'       : 'Alternative fragmentation model',
    'TTJets_hdamp'              : '\hdamp',
    'TTJets_semiLepBr'          : 'B hadron decay semileptonic branching fraction',
    'TTJets_CR_erdOn'              : 'Colour reconnection (erdOn)',
    'TTJets_CR_QCDbased_erdOn'              : 'Colour reconnection (QCD based)',
    'TTJets_CR_GluonMove'              : 'Colour reconnection (Gluon move)',
    'inputMC'              : 'MC statistics',
    'central'                   : '',
    'systematic'                : '',
    'statistical'               : '',
}


