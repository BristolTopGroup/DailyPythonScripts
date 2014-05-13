'''
Created on 4 Apr 2013

@author: kreczko
'''
centre_of_mass = 7  # TeV

'''
The path is expected to contain a folder for each systematic (there are some exceptions)
'''
path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-14-071_2nd_draft/7TeV/'
path_to_unfolding_histograms = path_to_files + '/unfolding/'
luminosity = 5050  # pb-1 (if you add 1 pb-1 the rounding works as it should....)
new_luminosity = 5050  # pb-1
luminosity_scale = float( new_luminosity ) / float( luminosity )
ttbar_xsection = 164  # pb

middle = '_' + str( luminosity ) + 'pb_PFElectron_PFMuon_PF2PATJets_PFMET'

data_file_electron = path_to_files + 'central/ElectronHad' + middle + '.root'
data_file_muon = path_to_files + 'central/SingleMu' + middle + '.root'
muon_QCD_file = path_to_files + 'QCD_data_mu.root'
SingleTop_file = path_to_files + 'central/SingleTop' + middle + '.root'
muon_QCD_MC_file = path_to_files + 'central/QCD_Pt-20_MuEnrichedPt-15' + middle + '.root'
electron_QCD_MC_file = path_to_files + 'central/QCD_Electron' + middle + '.root'

rate_changing_systematics = {'luminosity': 0.022,  # https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupSystematicErrors
                             'SingleTop_cross_section': 0.3,
                             'TTJet_cross_section': 0.15
                             }

generator_systematics = [ 'matchingup', 'matchingdown', 'scaleup', 'scaledown' ]
ttbar_generator_systematics = [ 'matchingup', 'matchingdown', 'scaleup', 'scaledown', 'mcatnlo', 'ptreweight']
central_general_template = path_to_files + 'central/%s' + middle + '.root'
generator_systematic_ttbar_templates = { systematic: path_to_files + 'central/TTJets-%s_%dpb_PFElectron_PFMuon_PF2PATJets_PFMET.root' % ( systematic, luminosity ) for systematic in ttbar_generator_systematics}
generator_systematic_vjets_templates = { systematic:path_to_files + 'central/VJets-%s_%dpb_PFElectron_PFMuon_PF2PATJets_PFMET.root' % ( systematic, luminosity ) for systematic in generator_systematics}

pdf_uncertainty_template = path_to_files + 'PDFWeights/TTJet' + middle + '_PDFWeights_%d.root'

categories_and_prefixes = {
                 'central':'',
                 'Electron_down':'_minusElectron',
                 'Electron_up':'_plusElectron',
                 'Muon_down':'_minusMuon',
                 'Muon_up':'_plusMuon',
                 'BJet_down':'_minusBJet',
                 'BJet_up':'_plusBjet',
                 'JES_down':'_minusJES',
                 'JES_up':'_plusJES',
                 'JER_down':'_minusJER',
                 'JER_up':'_plusJER',
                 'LightJet_down':'_minusLightJet',
                 'LightJet_up':'_plusLightJet',
                 'PU_down':'_PU_64600mb',
                 'PU_up':'_PU_71400mb'
                 }

general_category_templates = {category: path_to_files + category + '/%s' + middle + prefix + '.root' for category, prefix in categories_and_prefixes.iteritems()}
ttbar_category_templates = {category: path_to_files + category + '/TTJet' + middle + prefix + '.root' for category, prefix in categories_and_prefixes.iteritems()}
SingleTop_category_templates = {category: path_to_files + category + '/SingleTop' + middle + prefix + '.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}
VJets_category_templates = {category: path_to_files + category + '/VJets' + middle + prefix + '.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}
muon_QCD_MC_category_templates = {category: path_to_files + category + '/QCD_Pt-20_MuEnrichedPt-15' + middle + prefix + '.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}
higgs_category_templates = {category: path_to_files + category + '/TTH_Inclusive_M-125' + middle + prefix + '.root' for ( category, prefix ) in categories_and_prefixes.iteritems()}

data_electron_category_templates = {'central': data_file_electron,
                                    'JES_up': path_to_files + 'JES_up/ElectronHad' + middle + categories_and_prefixes['JES_up'] + '.root',
                                    'JES_down': path_to_files + 'JES_down/ElectronHad' + middle + categories_and_prefixes['JES_down'] + '.root'
                                    }
data_muon_category_templates = {'central': data_file_muon,
                                    'JES_up': path_to_files + 'JES_up/SingleMu' + middle + categories_and_prefixes['JES_up'] + '.root',
                                    'JES_down': path_to_files + 'JES_down/SingleMu' + middle + categories_and_prefixes['JES_down'] + '.root'
                                    }

unfolding_output_general_template = path_to_unfolding_histograms + '%s.root'
unfolding_madgraph_raw = path_to_unfolding_histograms + 'unfolding_merged.root'
unfolding_powheg_raw = path_to_unfolding_histograms + 'unfolding_TTJets_7TeV_powheg.root'
unfolding_mcatnlo_raw = path_to_unfolding_histograms + 'unfolding_TTJets_7TeV_mcatnlo.root'

unfolding_scale_down_raw = path_to_unfolding_histograms + 'unfolding_TTJets_7TeV_scaledown.root'
unfolding_scale_up_raw = path_to_unfolding_histograms + 'unfolding_TTJets_7TeV_scaleup.root'
unfolding_matching_down_raw = path_to_unfolding_histograms + 'unfolding_TTJets_7TeV_matchingdown.root'
unfolding_matching_up_raw = path_to_unfolding_histograms + 'unfolding_TTJets_7TeV_matchingup.root'

unfolding_madgraph = unfolding_madgraph_raw.replace( '.root', '_asymmetric.root' )
unfolding_powheg = unfolding_powheg_raw.replace( '.root', '_asymmetric.root' )
unfolding_mcatnlo = unfolding_mcatnlo_raw.replace( '.root', '_asymmetric.root' )

unfolding_scale_down = unfolding_scale_down_raw.replace( '.root', '_asymmetric.root' )
unfolding_scale_up = unfolding_scale_up_raw.replace( '.root', '_asymmetric.root' )
unfolding_matching_down = unfolding_matching_down_raw.replace( '.root', '_asymmetric.root' )
unfolding_matching_up = unfolding_matching_up_raw.replace( '.root', '_asymmetric.root' )

histogram_path_templates = {
                   'MET' : 'TTbar_plus_X_analysis/%s/Ref selection/Binned_MET_Analysis/%s_bin_%s/%s_absolute_eta',
                   'HT' : 'TTbar_plus_X_analysis/%s/Ref selection/Binned_HT_Analysis/HT_bin_%s/%s_absolute_eta',
                   'ST': 'TTbar_plus_X_analysis/%s/Ref selection/Binned_ST_Analysis/ST_with_%s_bin_%s/%s_absolute_eta',
                   'MT': 'TTbar_plus_X_analysis/%s/Ref selection/Binned_MT_Analysis/MT_with_%s_bin_%s/%s_absolute_eta',
                   'WPT': 'TTbar_plus_X_analysis/%s/Ref selection/Binned_WPT_Analysis/WPT_with_%s_bin_%s/%s_absolute_eta'
                   }

# optimal regularisation parameters (needs study!)
k_values_electron = {
                   'MET' : 3,
                   'HT' : 7,
                   'ST' : 6,
                   'MT' : 2,
                   'WPT' : 3
}

k_values_muon = {
                   'MET' : 3,
                   'HT' : 6,
                   'ST' : 6,
                   'MT' : 2,
                   'WPT' : 6
}

k_values_combined = {
                   'MET' : 3,
                   'HT' : 3,
                   'ST' : 3,
                   'MT' : 2,
                   'WPT' : 4
}

electron_control_region = 'QCDConversions'
electron_control_region_systematic = 'QCD non iso e+jets'

muon_control_region = 'QCD non iso mu+jets ge3j'
muon_control_region_systematic = 'QCD non iso mu+jets ge3j'  # no systematic yet
special_muon_histogram = 'etaAbs_ge2j_data'

rebin = 2

include_higgs = False
