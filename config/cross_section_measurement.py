'''
Created on 9 Dec 2012

@author: kreczko
'''
from copy import copy

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

# systematics in other files
ttjet_systematics = ['TTJets-matchingdown', 'TTJets-matchingup', 'TTJets-scaledown', 'TTJets-scaleup', ]
wjets_systematics = ['WJets-matchingdown', 'WJets-matchingup', 'WJets-scaledown', 'WJets-scaleup']
zjets_systematics = ['ZJets-matchingdown', 'ZJets-matchingup', 'ZJets-scaledown', 'ZJets-scaleup' ]

# MET systematics




met_bins = [
           '0-25',
               '25-45',
               '45-70',
               '70-100',
               '100-inf'
               ]
met_bin_widths = {
           '0-25':25,
               '25-45':20,
               '45-70':25,
               '70-100':30,
               '100-inf':50
               }  

MET_LATEX = "E_{T}^{miss}"
met_bin_latex = {
           '0-25':'0 #leq %s < 25 GeV' % MET_LATEX,
               '25-45':'25 #leq %s < 45 GeV' % MET_LATEX,
               '45-70':'45 #leq %s < 70 GeV' % MET_LATEX,
               '70-100':'70 #leq %s < 100 GeV' % MET_LATEX,
               '100-inf':'%s $\geq$ 100 GeV' % MET_LATEX,
               }  

met_bin_latex_tables = {
           '0-25':'0--25~\GeV',
               '25-45':'25--45~\GeV',
               '45-70':'45--70~\GeV',
               '70-100':'70--100~\GeV',
               '100-inf':'$\\geq 100$~\GeV'
               }  
met_types = [
#             'patMETs',
             'patType1CorrectedPFMet',
             'patType1p2CorrectedPFMet'
             ]

met_systematics_sources = [
 "ElectronEnUp",
        "ElectronEnDown",
        "MuonEnUp",
        "MuonEnDown",
        "TauEnUp",
        "TauEnDown",
        "JetResUp",
        "JetResDown",
        "JetEnUp",
        "JetEnDown",
        "UnclusteredEnUp",
        "UnclusteredEnDown"
                      ]
all_met_types = [met_type + met_systematic for met_type in met_types for met_systematic in met_systematics_sources]
all_met_types.extend(met_types)


met_systematics_sources_latex = {
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

b_tag_bins_latex = {'0btag':'0 b-tags', '0orMoreBtag':'$\geq$ 0 b-tags', '1btag':'1 b-tags',
                    '1orMoreBtag':'$\geq$ 1 b-tags',
                    '2btags':'2 b-tags', '2orMoreBtags':'$\geq$ 2 b-tags',
                    '3btags':'3 b-tags', '3orMoreBtags':'$\geq$ 3 b-tags',
                    '4orMoreBtags':'$\geq$ 4 b-tags'}

def get_histograms_of_interest_7TeV():
    histograms_of_interest = []

    histograms_of_interest_electron = []
    histograms_of_interest_electron_QCD = []

    add_electron_histogram = histograms_of_interest_electron.append
    add_electron_QCD_histogram = histograms_of_interest_electron_QCD.append
    base = 'TTbarPlusMetAnalysis/EPlusJets/'
    
    from summations import all_b_tag_bins
    for met_bin in met_bins:
        for met_type in all_met_types:
            for b_tag_bin in all_b_tag_bins:
                distribution = base + 'Ref selection/BinnedMETAnalysis/Electron_%s_bin_%s/electron_AbsEta_%s' % (met_type, met_bin, b_tag_bin)
                qcdDistribution = base + 'QCDConversions/BinnedMETAnalysis/Electron_%s_bin_%s/electron_AbsEta_0btag' % (met_type, met_bin)
                qcdDistribution2 = base + 'QCD non iso e+jets/BinnedMETAnalysis/Electron_%s_bin_%s/electron_AbsEta_0btag' % (met_type, met_bin)
                add_electron_histogram(distribution)
                add_electron_QCD_histogram(qcdDistribution)
                add_electron_QCD_histogram(qcdDistribution2)
    
    histograms_of_interest_muon = []
    histograms_of_interest_muon_QCD = []
    
    add_muon_histogram = histograms_of_interest_muon.append
    add_muon_QCD_histogram = histograms_of_interest_muon_QCD.append
    base = 'TTbarPlusMetAnalysis/MuPlusJets/'
    
    for met_bin in met_bins:
        for met_type in all_met_types:
            for b_tag_bin in all_b_tag_bins:
                distribution = base + 'Ref selection/BinnedMETAnalysis/Muon_%s_bin_%s/muon_AbsEta_%s' % (met_type, met_bin, b_tag_bin)
                qcdDistribution = base + 'QCD non iso mu+jets/BinnedMETAnalysis/Muon_%s_bin_%s/muon_AbsEta_0btag' % (met_type, met_bin)
                add_muon_histogram(distribution)
                add_muon_QCD_histogram(qcdDistribution)
    histograms_of_interest.extend(histograms_of_interest_electron)
    histograms_of_interest.extend(histograms_of_interest_electron_QCD)
    histograms_of_interest.extend(histograms_of_interest_muon)
    histograms_of_interest.extend(histograms_of_interest_muon_QCD)
    return histograms_of_interest
    

variable_identifiers = {
                        'MET': 'BinnedMETAnalysis',
                        'ST': 'Binned_ST_Analysis',
                        'HT': 'Binned_HT_Analysis'
                        }    
