'''
	Mapping of variable names to branch names in AnalysisTools output files
	under
	TTbar_plus_X_analysis/Unfolding.
'''
branchNames = {
    'MT': 'MT',
    'WPT': 'WPT',
    'HT': 'HT',
    'ST': 'ST',
    'MET': 'MET',

    'lepTopPt': 'lepTopPt',
    'hadTopPt': 'hadTopPt',
    'lepTopRap': 'lepTopRap',
    'hadTopRap': 'hadTopRap',
    'ttbarPt': 'ttbarPt',
    'ttbarM': 'ttbarM',
    'ttbarRap': 'ttbarRap',

    'abs_lepTopRap': 'abs(lepTopRap)',
    'abs_hadTopRap': 'abs(hadTopRap)',
    'abs_ttbarRap': 'abs(ttbarRap)',

    'NJets': 'NJets',

    'bjets_pt': 'bPt',
    'bjets_eta': 'bEta',
    'abs_bjets_eta': 'abs(bEta)',

    'lepton_pt': 'leptonPt',
    'lepton_pt_+': 'leptonPt',
    'lepton_pt_-': 'leptonPt',
    'lepton_eta': 'leptonEta',
    'abs_lepton_eta': 'leptonEta',
    'abs_lepton_eta_muonBins': 'leptonEta',
    'abs_lepton_eta_electronBins': 'leptonEta',
    'abs_lepton_eta_coarse': 'leptonEta',

}

genBranchNames_particle = {
    'MT': 'pseudoMT',
    'WPT': 'pseudoWPT',
    'HT': 'pseudoHT',
    'ST': 'pseudoST',
    'MET': 'pseudoMET',

    'lepTopPt': 'pseudoTop_pT',
    'hadTopPt': 'pseudoTop_pT',
    'lepTopRap': 'pseudoTop_y',
    'hadTopRap': 'pseudoTop_y',
    'ttbarPt': 'pseudoTTbar_pT',
    'ttbarM': 'pseudoTTbar_m',
    'ttbarRap': 'pseudoTTbar_y',

    'abs_lepTopRap': 'abs(pseudoTop_y)',
    'abs_hadTopRap': 'abs(pseudoTop_y)',
    'abs_ttbarRap': 'abs(pseudoTTbar_y)',

    'NJets': 'NPseudoJets',

    'bjets_pt': 'pseudoB_pT',
    'bjets_eta': 'pseudoB_eta',
    'abs_bjets_eta': 'abs(pseudoB_eta)',

    'lepton_pt': 'pseudoLepton_pT',
    'lepton_pt_+': 'pseudoLepton_pT',
    'lepton_pt_-': 'pseudoLepton_pT',
    'lepton_eta': 'pseudoLepton_eta',
    'abs_lepton_eta': 'pseudoLepton_eta',
    'abs_lepton_eta_muonBins': 'pseudoLepton_eta',
    'abs_lepton_eta_electronBins': 'pseudoLepton_eta',
    'abs_lepton_eta_coarse': 'pseudoLepton_eta',
}

genBranchNames_parton = {
    'MET': 'neutrinoPt_parton',

    'lepTopPt': 'lepTopPt_parton',
    'hadTopPt': 'hadTopPt_parton',
    'lepTopRap': 'lepTopRap_parton',
    'hadTopRap': 'hadTopRap_parton',
    'ttbarPt': 'ttbarPt',
    'ttbarM': 'ttbarM',
    'ttbarRap': 'ttbarRap',

    'abs_lepTopRap': 'abs(lepTopRap_parton)',
    'abs_hadTopRap': 'abs(hadTopRap_parton)',
    'abs_ttbarRap': 'abs(ttbarRap)',

    'NJets': 'NPseudoJets',

    'bjets_pt': 'pseudoB_pT',
    'bjets_eta': 'pseudoB_eta',
    'abs_bjets_eta': 'abs(pseudoB_eta)',

    'lepton_pt': 'leptonPt_parton',
    'lepton_eta': 'leptonEta_parton',
    'abs_lepton_eta': 'abs(leptonEta_parton)',
}
