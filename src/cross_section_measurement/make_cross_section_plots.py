'''
Created on 28 Nov 2012

@author: kreczko
'''
from tools.file_utilities import read_data_from_JSON
from tools.hist_utilities import values_and_errors_to_hist

def plot_initial_values():
    initial_values_electron = read_data_from_JSON(initial_values_electron_file)
    
def plot_normalisation():
    fit_results_electron = read_data_from_JSON(fit_results_electron_file)
    h_signal = values_and_errors_to_hist(fit_results_electron['signal'])
    h_VJets = values_and_errors_to_hist(fit_results_electron['V+Jets'])
    h_QCD = values_and_errors_to_hist(fit_results_electron['QCD'])
    h_background = h_VJets + h_QCD
    make_normalisation_plot(h_signal, h_background, 'electron')
    
    fit_results_muon = read_data_from_JSON(fit_results_muon_file)
    #TODO: V+Jets + QCD (background)
    

def make_normalisation_plot(h_signal, h_background, channel):
    pass    

def plot_unfolding():
    fit_results_electron = read_data_from_JSON(fit_results_electron_file)
    TTJet_fit_results_electron = fit_results_electron['TTJet']
    TTJet_fit_results_electron_unfolded = read_data_from_JSON('data/TTJet_fit_results_electron_unfolded.txt')
    MADGRAPH_results_electron = read_data_from_JSON('data/MADGRAPH_results_electron.txt')
    
def plot_cross_section():
    pass

def plot_normalised_cross_section():
    pass

def plot_normalised_to_one_cross_section():
    pass    
    
if __name__ == '__main__':
    b_tag_multiplicity = '>=2'
    #has to include data, signal, V+Jets, QCD, TTJet, SingleTop
    initial_values_electron_file = 'data/initial_values_electron.txt'
    initial_values_electron_file = 'data/initial_values_muon.txt'
    #has to include data, signal, V+Jets, QCD, TTJet, SingleTop
    fit_results_electron_file = 'data/fit_results_electron.txt'
    fit_results_muon_file = 'data/fit_results_muon.txt'
    
    #has to include TTJet, MADGRAPH, POWHEG, PYTHIA, MCATNLO, 
    #TTJet_scaledown, TTJet_scaleup, TTJet_matchingdown, TTJet_matchingup
    normalisation_electron_unfolded_file = 'data/normalisation_electron_unfolded.txt'
    normalisation_muon_unfolded_file = 'data/normalisation_muon_unfolded.txt'  
#    TTJet_fit_results_electron_unfolded_file = 'data/TTJet_fit_results_electron_unfolded.txt'
#    TTJet_fit_results_muon_unfolded_file = 'data/TTJet_fit_results_muon_unfolded.txt'
#    MADGRAPH_results_electron_file = 'data/MADGRAPH_results_electron.txt'
    #POWHEG_results_electron_file
    plot_initial_values()
    plot_normalisation()
    plot_unfolding()
    plot_cross_section()
    plot_normalised_cross_section()
    plot_normalised_to_one_cross_section()
    