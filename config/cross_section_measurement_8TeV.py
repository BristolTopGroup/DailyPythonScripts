'''
Created on 4 Apr 2013

@author: kreczko
'''
centre_of_mass = 8  # TeV

'''
The path is expected to contain a folder for each systematic (there are some exceptions)
'''
path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-13-015_V6/'
luminosity = 19584  # pb-1
ttbar_xsection = 245.8  # pb

middle = '_' + str(luminosity) + 'pb_PFElectron_PFMuon_PF2PATJets_PFMET'

data_file_electron = path_to_files + 'central/SingleElectron' + middle + '.root'
data_file_muon = path_to_files + 'central/SingleMu' + middle + '.root'
muon_QCD_file = path_to_files + 'QCD_data_mu.root'
SingleTop_file = path_to_files + 'central/SingleTop' + middle + '.root'
muon_QCD_MC_file = path_to_files + 'central/QCD_Muon' + middle + '.root'

generator_systematics = [ 'matchingup', 'matchingdown', 'scaleup', 'scaledown' ]
generator_systematic_ttbar_templates = { systematic: path_to_files + 'central/TTJets-%s_%dpb_PFElectron_PFMuon_PF2PATJets_PFMET.root' % (systematic, luminosity) for systematic in generator_systematics}
generator_systematic_vjets_templates = { systematic:path_to_files + 'central/VJets_%s_%dpb_PFElectron_PFMuon_PF2PATJets_PFMET.root' % (systematic, luminosity) for systematic in generator_systematics}

pdf_uncertainty_template = path_to_files + 'PDFWeights/TTJet' + middle + '_PDFWeights_%d.root'

categories_and_prefixes = {
                 'central':'',
                 'BJet_down':'_minusBJet',
                 'BJet_up':'_plusBjet',
                 'JES_down':'_minusJES',
                 'JES_up':'_plusJES',
                 'LightJet_down':'_minusLightJet',
                 'LightJet_up':'_plusLightJet',
                 'PU_down':'_PU_65835mb',
                 'PU_up':'_PU_72765mb'
                 }

ttbar_category_templates = {category: path_to_files + category + '/TTJet' + middle + prefix + '.root' for category, prefix in categories_and_prefixes.iteritems()}
SingleTop_category_templates = {category: path_to_files + category + '/SingleTop' + middle + prefix + '.root' for (category, prefix) in categories_and_prefixes.iteritems()}
VJets_category_templates = {category: path_to_files + category + '/VJets' + middle + prefix + '.root' for (category, prefix) in categories_and_prefixes.iteritems()}
muon_QCD_MC_category_templates = {category: path_to_files + category + '/QCD_Muon' + middle + prefix + '.root' for (category, prefix) in categories_and_prefixes.iteritems()}

data_electron_category_templates = {'central': data_file_electron,
                                    'JES_up': path_to_files + 'JES_up/SingleElectron' + middle + categories_and_prefixes['JES_up'] + '.root',
                                    'JES_down': path_to_files + 'JES_down/SingleElectron' + middle + categories_and_prefixes['JES_down'] + '.root'
                                    }
data_muon_category_templates = {'central': data_file_muon,
                                    'JES_up': path_to_files + 'JES_up/SingleMu' + middle + categories_and_prefixes['JES_up'] + '.root',
                                    'JES_down': path_to_files + 'JES_down/SingleMu' + middle + categories_and_prefixes['JES_down'] + '.root'
                                    }

unfolding_madgraph_file = path_to_files + 'unfolding_merged.root'
unfolding_powheg = path_to_files + 'unfolding_TTJets_8TeV_powheg.root'
unfolding_mcatnlo = path_to_files + 'unfolding_TTJets_8TeV_mcatnlo.root'

unfolding_scale_down = path_to_files + 'unfolding_TTJets_8TeV_scaledown.root'
unfolding_scale_up = path_to_files + 'unfolding_TTJets_8TeV_scaleup.root'
unfolding_matching_down = path_to_files + 'unfolding_TTJets_8TeV_matchingdown.root'
unfolding_matching_up = path_to_files + 'unfolding_TTJets_8TeV_matchingup.root'

histogram_path_templates = {
                   'MET' : 'TTbar_plus_X_analysis/%s/Ref selection/Binned_MET_Analysis/%s_bin_%s/%s_absolute_eta',
                   'HT' : 'TTbar_plus_X_analysis/%s/Ref selection/Binned_HT_Analysis/HT_bin_%s/%s_absolute_eta',
                   'ST': 'TTbar_plus_X_analysis/%s/Ref selection/Binned_ST_Analysis/ST_with_%s_bin_%s/%s_absolute_eta',
                   'MT': 'TTbar_plus_X_analysis/%s/Ref selection/Binned_MT_Analysis/MT_with_%s_bin_%s/%s_absolute_eta',
                   'WPT': 'TTbar_plus_X_analysis/%s/Ref selection/Binned_WPT_Analysis/WPT_with_%s_bin_%s/%s_absolute_eta'
                   }

special_muon_histogram = 'muon_AbsEta_0btag'
rebin = 2
