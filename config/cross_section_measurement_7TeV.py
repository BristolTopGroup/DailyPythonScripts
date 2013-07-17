'''
Created on 4 Apr 2013

@author: kreczko
'''

centre_of_mass = 7  # TeV

'''
The path is expected to contain a folder for each systematic (there are some exceptions)
'''
path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-12-241_V4/'
luminosity = 5051  # pb-1 (if you add 1 pb-1 the rounding works as it should....)
ttbar_xsection = 164  # pb
middle = '_' + str(luminosity) + 'pb_PFElectron_PFMuon_PF2PATJets_PFMET'

data_file_electron = path_to_files + 'central/ElectronHad' + middle + '.root'
data_file_muon = path_to_files + 'central/SingleMu' + middle + '.root'
muon_QCD_file = path_to_files + 'QCD_data_mu.root'
SingleTop_file = path_to_files + 'central/SingleTop' + middle + '.root'
muon_QCD_MC_file = path_to_files + 'central/QCD_Pt-20_MuEnrichedPt-15' + middle + '.root'

generator_systematics = [ 'matchingup', 'matchingdown', 'scaleup', 'scaledown' ]
generator_systematic_ttbar_templates = { systematic: path_to_files + 'central/TTJets-%s_%dpb_PFElectron_PFMuon_PF2PATJets_PFMET.root' % (systematic, luminosity) for systematic in generator_systematics}
generator_systematic_vjets_templates = { systematic:path_to_files + 'central/VJets-%s_%dpb_PFElectron_PFMuon_PF2PATJets_PFMET.root' % (systematic, luminosity) for systematic in generator_systematics}

pdf_uncertainty_template = path_to_files + 'PDFWeights/TTJet' + middle + '_PDFWeights_%d.root'

categories_and_prefixes = {
                 'central':'',
                 'BJet_down':'_minusBJet',
                 'BJet_up':'_plusBjet',
                 'JES_down':'_minusJES',
                 'JES_up':'_plusJES',
                 #placeholders
#                 'JER_down':'_minusJER',
#                 'JER_up':'_plusJER',
                 'LightJet_down':'_minusLightJet',
                 'LightJet_up':'_plusLightJet',
                 'PU_down':'_PU_64600mb',
                 'PU_up':'_PU_71400mb'
                 }


general_category_templates = {category: path_to_files + category + '/%s' + middle + prefix + '.root' for category, prefix in categories_and_prefixes.iteritems()}
ttbar_category_templates = {category: path_to_files + category + '/TTJet' + middle + prefix + '.root' for category, prefix in categories_and_prefixes.iteritems()}
SingleTop_category_templates = {category: path_to_files + category + '/SingleTop' + middle + prefix + '.root' for (category, prefix) in categories_and_prefixes.iteritems()}
VJets_category_templates = {category: path_to_files + category + '/VJets' + middle + prefix + '.root' for (category, prefix) in categories_and_prefixes.iteritems()}
muon_QCD_MC_category_templates = {category: path_to_files + category + '/QCD_Pt-20_MuEnrichedPt-15' + middle + prefix + '.root' for (category, prefix) in categories_and_prefixes.iteritems()}

data_electron_category_templates = {'central': data_file_electron,
                                    'JES_up': path_to_files + 'JES_up/ElectronHad' + middle + categories_and_prefixes['JES_up'] + '.root',
                                    'JES_down': path_to_files + 'JES_down/ElectronHad' + middle + categories_and_prefixes['JES_down'] + '.root'
                                    }
data_muon_category_templates = {'central': data_file_muon,
                                    'JES_up': path_to_files + 'JES_up/SingleMu' + middle + categories_and_prefixes['JES_up'] + '.root',
                                    'JES_down': path_to_files + 'JES_down/SingleMu' + middle + categories_and_prefixes['JES_down'] + '.root'
                                    }

unfolding_madgraph_file = path_to_files + 'unfolding_TTJets_7TeV_madgraph.root'
unfolding_powheg = path_to_files + 'unfolding_TTJets_7TeV_powheg.root'
unfolding_mcatnlo = path_to_files + 'unfolding_TTJets_7TeV_pythia.root'

unfolding_scale_down = path_to_files + 'unfolding_TTJets_7TeV_scaledown.root'
unfolding_scale_up = path_to_files + 'unfolding_TTJets_7TeV_scaleup.root'
unfolding_matching_down = path_to_files + 'unfolding_TTJets_7TeV_matchingdown.root'
unfolding_matching_up = path_to_files + 'unfolding_TTJets_7TeV_matchingup.root'

histogram_path_templates = {
                   'MET' : 'TTbarPlusMetAnalysis/%s/Ref selection/BinnedMETAnalysis/%s_%s_bin_%s/%s_AbsEta',
#                   'HT' : 'TTbarPlusMetAnalysis/%s/Ref selection/Binned_HT_Analysis/HT_bin_%s/%s_absolute_eta',
#                   'ST': 'TTbarPlusMetAnalysis/%s/Ref selection/Binned_ST_Analysis/ST_with_%s_bin_%s/%s_absolute_eta',
#                   'MT': 'TTbarPlusMetAnalysis/%s/Ref selection/Binned_MT_Analysis/MT_with_%s_bin_%s/%s_absolute_eta'
                   }

electron_control_region = 'QCDConversions'
electron_control_region_systematic = 'QCD non iso e+jets'

special_muon_histogram = 'etaAbs_ge2j_data'

rebin = 20
