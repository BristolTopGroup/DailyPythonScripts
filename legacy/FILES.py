placeholder = 'SAMPLE'
pathToFiles = '/storage/TopQuarkGroup/results/histogramfiles/AN-13-015_V2'
luminosity = 5814#pb-1
suffix = 'PFElectron_PFMuon_PF2PATJets_PFMET.root'
JES_down_suffix = 'PFElectron_PFMuon_PF2PATJets_PFMET_minusJES.root'
JES_up_suffix = 'PFElectron_PFMuon_PF2PATJets_PFMET_plusJES.root'
PU_down_suffix = 'PFElectron_PFMuon_PF2PATJets_PFMET_PU_65835mb.root'
PU_up_suffix = 'PFElectron_PFMuon_PF2PATJets_PFMET_PU_72765mb.root'
PDFWeights_suffix = 'PFElectron_PFMuon_PF2PATJets_PFMET_PDFWeights_%d.root'
BJet_down_suffix = 'PFElectron_PFMuon_PF2PATJets_PFMET_minusBJet.root'
BJet_up_suffix = 'PFElectron_PFMuon_PF2PATJets_PFMET_plusBjet.root'
LightJet_down_suffix = 'PFElectron_PFMuon_PF2PATJets_PFMET_minusLightJet.root'
LightJet_up_suffix = 'PFElectron_PFMuon_PF2PATJets_PFMET_plusLightJet.root'

template = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % {'path':pathToFiles + '/central', 'lumi':luminosity, 'suffix':suffix, 'placeholder':placeholder}
template_JES_down = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % {'path':pathToFiles + '/JES_down', 'lumi':luminosity, 'suffix':JES_down_suffix, 'placeholder':placeholder}
template_JES_up = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % {'path':pathToFiles + '/JES_up', 'lumi':luminosity, 'suffix':JES_up_suffix, 'placeholder':placeholder}
template_PU_down = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % {'path':pathToFiles + '/PU_down', 'lumi':luminosity, 'suffix':PU_down_suffix, 'placeholder':placeholder}
template_PU_up = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % {'path':pathToFiles+ '/PU_up', 'lumi':luminosity, 'suffix':PU_up_suffix, 'placeholder':placeholder}
template_PDFWeights = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % {'path':pathToFiles+ '/PDFWeights', 'lumi':luminosity, 'suffix':PDFWeights_suffix, 'placeholder':'TTJet'}
template_BJet_down = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % {'path':pathToFiles + '/BJet_down', 'lumi':luminosity, 'suffix':BJet_down_suffix, 'placeholder':placeholder}
template_BJet_up = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % {'path':pathToFiles+ '/BJet_up', 'lumi':luminosity, 'suffix':BJet_up_suffix, 'placeholder':placeholder}
template_LightJet_down = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % {'path':pathToFiles + '/LightJet_down', 'lumi':luminosity, 'suffix':LightJet_down_suffix, 'placeholder':placeholder}
template_LightJet_up = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % {'path':pathToFiles+ '/LightJet_up', 'lumi':luminosity, 'suffix':LightJet_up_suffix, 'placeholder':placeholder}

samplesToLoad = ['SingleElectron',
                 'SingleMu',
                 'TTJet', 
                 'DY1JetsToLL',
                 'DY2JetsToLL',
                 'DY3JetsToLL',
                 'DY4JetsToLL',
                 'QCD_Pt-15to20_MuEnrichedPt5',
                 'QCD_Pt-20to30_MuEnrichedPt5',
                 'QCD_Pt-30to50_MuEnrichedPt5',
                 'QCD_Pt-50to80_MuEnrichedPt5',
                 'QCD_Pt-80to120_MuEnrichedPt5',
                 'QCD_Pt-120to170_MuEnrichedPt5',
                 'QCD_Pt-170to300_MuEnrichedPt5',
                 'QCD_Pt-300to470_MuEnrichedPt5',
                 'QCD_Pt-470to600_MuEnrichedPt5',
#                 'QCD_Pt-600to800_MuEnrichedPt5',
                 'QCD_Pt-800to1000_MuEnrichedPt5',
                 'QCD_Pt-1000_MuEnrichedPt5',
                 'QCD_Pt_20_30_BCtoE',
                 'QCD_Pt_30_80_BCtoE',
                 'QCD_Pt_80_170_BCtoE',
                 'QCD_Pt_170_250_BCtoE',
                 'QCD_Pt_250_350_BCtoE',
                 'QCD_Pt_350_BCtoE',
                 'QCD_Pt_20_30_EMEnriched',
                 'QCD_Pt_30_80_EMEnriched',
                 'QCD_Pt_80_170_EMEnriched',
                 'QCD_Pt_170_250_EMEnriched',
                 'QCD_Pt_250_350_EMEnriched',
                 'QCD_Pt_350_EMEnriched',
                 'GJets_HT-200To400',
                 'GJets_HT-400ToInf',
#                 'WWtoAnything',
#                 'WZtoAnything',
#                 'ZZtoAnything',
                 'T_tW-channel',
                 'T_t-channel',
                 'T_s-channel',
                 'Tbar_tW-channel',
                 'Tbar_t-channel',
                 'Tbar_s-channel',
#                 'TTbarZIncl',
#                 'TTbarInclWIncl',
                 'W1Jet',
                 'W2Jets',
                 'W3Jets',
                 'W4Jets'                 
                 ]
additionalSamples = [
                 'TTJets-matchingdown',
                 'TTJets-matchingup',
                 'TTJets-scaledown',
                 'TTJets-scaleup',
                 'WJets-matchingdown',
                 'WJets-matchingup',
                 'WJets-scaledown',
                 'WJets-scaleup',
                 'ZJets-matchingdown',
                 'ZJets-matchingup',
                 'ZJets-scaledown',
                 'ZJets-scaleup'
                     ]

files = {}
files_JES_down = {}
files_JES_up = {}
files_PU_down = {}
files_PU_up = {}
files_PDF_weights = {}
files_BJet_down = {}
files_BJet_up = {}
files_LightJet_down = {}
files_LightJet_up = {}

rpl = template.replace
rpl_JES_down = template_JES_down.replace
rpl_JES_up = template_JES_up.replace
rpl_PU_down = template_PU_down.replace
rpl_PU_up = template_PU_up.replace
rpl_BJet_down = template_BJet_down.replace
rpl_BJet_up = template_BJet_up.replace
rpl_LightJet_down = template_LightJet_down.replace
rpl_LightJet_up = template_LightJet_up.replace

for sample in samplesToLoad:
    files[sample] = rpl(placeholder, sample)
    files_JES_down[sample] = rpl_JES_down(placeholder, sample)
    files_JES_up[sample] = rpl_JES_up(placeholder, sample)
    files_PU_down[sample] = rpl_PU_down(placeholder, sample)
    files_PU_up[sample] = rpl_PU_up(placeholder, sample)
    files_BJet_down[sample] = rpl_BJet_down(placeholder, sample)
    files_BJet_up[sample] = rpl_BJet_up(placeholder, sample)
    files_LightJet_down[sample] = rpl_LightJet_down(placeholder, sample)
    files_LightJet_up[sample] = rpl_LightJet_up(placeholder, sample)
    
for sample in additionalSamples:
    files[sample] = rpl(placeholder, sample)
    
for sample in ['POWHEG', 'MCatNLO']:
    formatting = {'path':pathToFiles + '/central', 'lumi':luminosity, 'suffix':'PFElectron_PFMuon_PF2PATJets_PFMET_%s.root'%sample, 'placeholder':'TTJet'}
    files[sample] = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % formatting
    files_JES_down[sample] = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % formatting
    files_JES_up[sample] = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % formatting
    files_PU_down[sample] = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % formatting
    files_PU_up[sample] = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % formatting
    files_BJet_down[sample] = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % formatting
    files_BJet_up[sample] = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % formatting
    files_LightJet_down[sample] = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % formatting
    files_LightJet_up[sample] = '%(path)s/%(placeholder)s_%(lumi)dpb_%(suffix)s' % formatting
    
for index in range(1,45):
    files_PDF_weights['TTJet_%d' % index] = template_PDFWeights % index
    
#data is the same for:
files_PU_down['SingleElectron'] = files['SingleElectron']
files_PU_up['SingleElectron'] = files['SingleElectron']
files_BJet_down['SingleElectron'] = files['SingleElectron']
files_BJet_up['SingleElectron'] = files['SingleElectron']
files_LightJet_down['SingleElectron'] = files['SingleElectron']
files_LightJet_up['SingleElectron'] = files['SingleElectron']
#muon channel
files_PU_down['SingleMu'] = files['SingleMu']
files_PU_up['SingleMu'] = files['SingleMu']
files_BJet_down['SingleMu'] = files['SingleMu']
files_BJet_up['SingleMu'] = files['SingleMu']
files_LightJet_down['SingleMu'] = files['SingleMu']
files_LightJet_up['SingleMu'] = files['SingleMu']
