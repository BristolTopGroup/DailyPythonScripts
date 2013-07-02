'''
Created on 4 Apr 2013

@author: kreczko
'''
centre_of_mass = 8  # TeV

'''
The path is expected to contain a folder for each systematic (there are some exceptions)
'''
path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-13-015_V6_22JanRereco/'
path_to_unfolding_histograms = '/storage/TopQuarkGroup/results/histogramfiles/AN-13-015_V6_fixed_unfolding_new_variables_ARC_review/'

path_to_unfolding_ntuples = '/storage/TopQuarkGroup/mc/8TeV/NoSkimUnfolding/v10/' #for merging
luminosity = 19584  # pb-1
ttbar_xsection = 245.8  # pb

middle = '_' + str(luminosity) + 'pb_PFElectron_PFMuon_PF2PATJets_PFMET'

data_file_electron = path_to_files + 'central/SingleElectron' + middle + '.root'
data_file_muon = path_to_files + 'central/SingleMu' + middle + '.root'
muon_QCD_file = path_to_files + 'QCD_data_mu.root'
SingleTop_file = path_to_files + 'central/SingleTop' + middle + '.root'
muon_QCD_MC_file = path_to_files + 'central/QCD_Muon' + middle + '.root'
electron_QCD_MC_file =  path_to_files + 'central/QCD' + middle + '.root'

generator_systematics = [ 'matchingup', 'matchingdown', 'scaleup', 'scaledown' ]
central_general_template = path_to_files + 'central/%s' + middle + '.root'
generator_systematic_ttbar_templates = { systematic: path_to_files + 'central/TTJets-%s_%dpb_PFElectron_PFMuon_PF2PATJets_PFMET.root' % (systematic, luminosity) for systematic in generator_systematics}
generator_systematic_vjets_templates = { systematic:path_to_files + 'central/VJets_%s_%dpb_PFElectron_PFMuon_PF2PATJets_PFMET.root' % (systematic, luminosity) for systematic in generator_systematics}

pdf_uncertainty_template = path_to_files + 'PDFWeights/TTJet' + middle + '_PDFWeights_%d.root'

categories_and_prefixes = {
                 'central':'',
                 'BJet_down':'_minusBJet',
                 'BJet_up':'_plusBjet',
                 'JES_down':'_minusJES',
                 'JES_up':'_plusJES',
                 'JER_down':'_minusJER',
                 'JER_up':'_plusJER',
                 'LightJet_down':'_minusLightJet',
                 'LightJet_up':'_plusLightJet',
                 'PU_down':'_PU_65835mb',
                 'PU_up':'_PU_72765mb'
                 }

general_category_templates = {category: path_to_files + category + '/%s' + middle + prefix + '.root' for category, prefix in categories_and_prefixes.iteritems()}
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

unfolding_input_templates = {'unfolding_merged': path_to_unfolding_ntuples + 'TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/unfolding_v10_Summer12_DR53X-PU_S10_START53_V7C-v1_NoSkim/%s*.root',
                            'unfolding_TTJets_8TeV_mcatnlo': path_to_unfolding_ntuples + 'TT_8TeV-mcatnlo/unfolding_v10_Summer12_DR53X-PU_S10_START53_V7A-v1_NoSkim/%s*.root',
                            'unfolding_TTJets_8TeV_powheg': path_to_unfolding_ntuples + 'TT_CT10_TuneZ2star_8TeV-powheg-tauola/unfolding_v10_Summer12_DR53X-PU_S10_START53_V7A-v1_NoSkim/%s*.root',
                            'unfolding_TTJets_8TeV_matchingup': path_to_unfolding_ntuples + 'TTJets_matchingup_TuneZ2star_8TeV-madgraph-tauola/unfolding_v10_Summer12_DR53X-PU_S10_START53_V7A-v1_NoSkim/%s*.root',
                            'unfolding_TTJets_8TeV_matchingdown': path_to_unfolding_ntuples + 'TTJets_matchingdown_TuneZ2star_8TeV-madgraph-tauola/unfolding_v10_Summer12_DR53X-PU_S10_START53_V7A-v1_NoSkim/%s*.root',
                            'unfolding_TTJets_8TeV_scaleup': path_to_unfolding_ntuples + 'TTJets_scaleup_TuneZ2star_8TeV-madgraph-tauola/unfolding_v10_Summer12_DR53X-PU_S10_START53_V7A-v1_NoSkim/%s*.root',
                            'unfolding_TTJets_8TeV_scaledown': path_to_unfolding_ntuples + 'TTJets_scaledown_TuneZ2star_8TeV-madgraph-tauola/unfolding_v10_Summer12_DR53X-PU_S10_START53_V7A-v1_NoSkim/%s*.root'
			    }

unfolding_output_general_template = path_to_unfolding_histograms + '%s.root'
unfolding_madgraph_file = path_to_unfolding_histograms + 'unfolding_merged.root'
unfolding_powheg = path_to_unfolding_histograms + 'unfolding_TTJets_8TeV_powheg.root'
unfolding_mcatnlo = path_to_unfolding_histograms + 'unfolding_TTJets_8TeV_mcatnlo.root'

unfolding_scale_down = path_to_unfolding_histograms + 'unfolding_TTJets_8TeV_scaledown.root'
unfolding_scale_up = path_to_unfolding_histograms + 'unfolding_TTJets_8TeV_scaleup.root'
unfolding_matching_down = path_to_unfolding_histograms + 'unfolding_TTJets_8TeV_matchingdown.root'
unfolding_matching_up = path_to_unfolding_histograms + 'unfolding_TTJets_8TeV_matchingup.root'

histogram_path_templates = {
                   'MET' : 'TTbar_plus_X_analysis/%s/Ref selection/Binned_MET_Analysis/%s_bin_%s/%s_absolute_eta',
                   'HT' : 'TTbar_plus_X_analysis/%s/Ref selection/Binned_HT_Analysis/HT_bin_%s/%s_absolute_eta',
                   'ST': 'TTbar_plus_X_analysis/%s/Ref selection/Binned_ST_Analysis/ST_with_%s_bin_%s/%s_absolute_eta',
                   'MT': 'TTbar_plus_X_analysis/%s/Ref selection/Binned_MT_Analysis/MT_with_%s_bin_%s/%s_absolute_eta',
                   'WPT': 'TTbar_plus_X_analysis/%s/Ref selection/Binned_WPT_Analysis/WPT_with_%s_bin_%s/%s_absolute_eta'
                   }

special_muon_histogram = 'muon_AbsEta_0btag'
rebin = 2
