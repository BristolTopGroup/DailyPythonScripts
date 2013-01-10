'''
Created on 9 Dec 2012

@author: kreczko
'''

folder_for_results = 'data'
fit_results_electron_file = folder_for_results + '/fit_results_electron.txt'
fit_results_muon_file = folder_for_results + '/fit_results_muon.txt'

normalisation_electron_unfolded_file = folder_for_results + '/normalisation_electron_unfolded.txt'
normalisation_muon_unfolded_file = folder_for_results + '/normalisation_muon_unfolded.txt'
normalisation_combined_unfolded_file = folder_for_results + '/normalisation_combined_unfolded.txt'

xsection_electron_unfolded_file = folder_for_results + '/xsection_electron_unfolded.txt'
xsection_muon_unfolded_file = folder_for_results + '/xsection_muon_unfolded.txt'
xsection_combined_unfolded_file = folder_for_results + '/xsection_combined_unfolded.txt'

normalised_to_one_xsection_electron_unfolded_file = folder_for_results + '/normalised_to_one_xsection_electron_unfolded.txt'
normalised_to_one_xsection_muon_unfolded_file = folder_for_results + '/normalised_to_one_xsection_muon_unfolded.txt'
normalised_to_one_xsection_combined_unfolded_file = folder_for_results + '/normalised_to_one_xsection_combined_unfolded.txt'

normalised_xsection_electron_unfolded_file = folder_for_results + '/normalised_xsection_electron_unfolded.txt'
normalised_xsection_muon_unfolded_file = folder_for_results + '/normalised_xsection_muon_unfolded.txt'
normalised_xsection_combined_unfolded_file = folder_for_results + '/normalised_xsection_combined_unfolded.txt'

bin_edges = [0, 25, 45, 70, 100, 1000]
bin_widths = [25, 20, 25, 30, 150]
met_bins_ROOT = ['0-25', '25-45', '45-70', '70-100', '100-inf']
btag_labels = []
luminosity_in_pbinv = 5050

path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-12-241_V4/'
input_folders = ['central', 'BJet_down', 'BJet_up', 'JES_down', 'JES_up',
                     'LightJet_down', 'LightJet_up', 'PU_down', 'PU_up']

histogram_template_path_electron = 'TTbarPlusMetAnalysis/EPlusJets/Ref selection/BinnedMETAnalysis/Electron_%{met_type}s_bin_%{met_bin}s/electron_AbsEta_%{b_tag_bin}s'
histogram_template_path_muon = 'TTbarPlusMetAnalysis/MuPlusJets/Ref selection/BinnedMETAnalysis/Electron_%{met_type}s_bin_%{met_bin}s/electron_AbsEta_%{b_tag_bin}s'

file_for_unfolding = path_to_files + 'unfolding_TTJets_7TeV_madgraph.root'
file_for_powheg = path_to_files + 'unfolding_TTJets_7TeV_powheg.root'
file_for_pythia = path_to_files + 'unfolding_TTJets_7TeV_pythia.root'
file_for_mcatnlo = path_to_files + 'unfolding_merged.root'

file_for_scaledown = path_to_files + 'unfolding_TTJets_7TeV_scaledown.root'
file_for_scaleup = path_to_files + 'unfolding_TTJets_7TeV_scaleup.root'
file_for_matchingdown = path_to_files + 'unfolding_TTJets_7TeV_matchingdown.root'
file_for_matchingup = path_to_files + 'unfolding_TTJets_7TeV_matchingup.root'

from config.file_templates import file_templates, suffix
file_TTJet = file_templates['central']['TTJet'] % {'luminosity_in_pbinv' : luminosity_in_pbinv, 'suffix':suffix}
file_template_pdf_weights = file_TTJet.replace('.root', '_PDFWeights_%(n_pdf)d.root')

single_top_samples = ['T_tW-channel', 'T_t-channel', 'T_s-channel', 'Tbar_tW-channel', 'Tbar_t-channel', 'Tbar_s-channel']
v_plus_jets_samples = ['W1Jet', 'W2Jets', 'W3Jets', 'W4Jets', 'DYJetsToLL']
diboson_samples = ['WWtoAnything', 'WZtoAnything', 'ZZtoAnything']

#systematics in other files
ttjet_systematics = ['TTJets-matchingdown', 'TTJets-matchingup', 'TTJets-scaledown', 'TTJets-scaleup', ]
wjets_systematics = ['WJets-matchingdown', 'WJets-matchingup', 'WJets-scaledown', 'WJets-scaleup']
zjets_systematics = ['ZJets-matchingdown', 'ZJets-matchingup', 'ZJets-scaledown', 'ZJets-scaleup' ]

#MET systematics