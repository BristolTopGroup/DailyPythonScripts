'''
Created on 9 Dec 2012

@author: kreczko

Episode 0 - Histogram preparation:
- get all interesting histograms from the analysis output files
- normalise them to the correct luminosity
- make sure the bins are correct (rebin etc)
- write output to a single file! Folder:
    - electron, muon
        - TTJet, QCD (from data), V+Jets, single top
            - met types
            - HT
            - other differential variables
            - lepton eta
                - met bins
                - HT bins
                - etc
- do the same for unfolding files:
    - electron, muon
    - MADGRAPH, POWHEG, PYTHIA, MC@NLO
    
result output files have the format
TTbar_plus_MET_analysis_<lumi>pbinv_<nbtag>.root
'''
from rootpy.io import File
from rootpy.utils import asrootpy
from array import array

def get_unfold_histogram_tuple(inputfile, channel):
    global bin_edges
    folder = None
    if channel == 'electron':
        folder = inputfile.unfoldingAnalyserElectronChannel
    else:  # channel == 'muon'
        folder = inputfile.unfoldingAnalyserMuonChannel
        
    n_bins = len(bin_edges) - 1
    bin_edge_array = array('d', bin_edges)
    
    h_truth = asrootpy(folder.truth.Rebin(n_bins, 'truth', bin_edge_array))
    h_measured = asrootpy(folder.measured.Rebin(n_bins, 'measured', bin_edge_array))
    h_response = folder.response_withoutFakes_AsymBins  # response_AsymBins
    
    nEvents = inputfile.EventFilter.EventCounter.GetBinContent(1)#number of processed events 
    lumiweight = 164.5 * 5050 / nEvents #ttbar x-section = 164.5pb, lumi = 5050pb-1
    h_truth.Scale(lumiweight)
    h_measured.Scale(lumiweight)
    h_response.Scale(lumiweight)
    return h_truth, h_measured, h_response


def get_result_histograms():
    pass
if __name__ == '__main__':
    import ROOT
    #prevent directory ownership of ROOT histograms (python does the garbage collection)
    ROOT.TH1F.AddDirectory(False)
    # setup
    bin_edges = [0, 25, 45, 70, 100, 1000]
    bin_widths = [25, 20, 25, 30, 150]
    met_bins_ROOT = ['0-25', '25-45', '45-70', '70-100', '100-inf']
    btag_labels = []
    
    path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-12-241_V4/'
    file_for_unfolding = File(path_to_files + 'unfolding_merged.root', 'read')
    file_for_powheg = File(path_to_files + 'unfolding_TTJets_7TeV_powheg.root', 'read')
    file_for_pythia = File(path_to_files + 'unfolding_TTJets_7TeV_pythia.root', 'read')
    file_for_mcatnlo = File(path_to_files + 'unfolding_merged.root', 'read')
    
    file_for_scaledown = File(path_to_files + 'unfolding_TTJets_7TeV_scaledown.root', 'read')
    file_for_scaleup = File(path_to_files + 'unfolding_TTJets_7TeV_scaleup.root', 'read')
    file_for_matchingdown = File(path_to_files + 'unfolding_TTJets_7TeV_matchingdown.root', 'read')
    file_for_matchingup = File(path_to_files + 'unfolding_TTJets_7TeV_matchingup.root', 'read')

    #different inputs
    input_folders = ['central', 'BJet_down', 'BJet_up', 'JES_down', 'JES_up', 
                     'LightJet_down', 'LightJet_up', 'PU_down', 'PU_up']
    #'PDFWeights' x 44
    #read all data but TTJet from central    
    
    # get data from histograms or JSON files
    TTJet_file = File(path_to_files + 'central/TTJet_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    SingleTop_file = File(path_to_files + 'central/SingleTop_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    W1Jet_file = File(path_to_files + 'central/W1Jet_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    W2Jets_file = File(path_to_files + 'central/W2Jets_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    W3Jets_file = File(path_to_files + 'central/W3Jets_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    W4Jets_file = File(path_to_files + 'central/W4Jets_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    ZJets_file = File(path_to_files + 'central/DYJetsToLL_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    data_file_electron = File(path_to_files + 'central/ElectronHad_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    data_file_muon = File(path_to_files + 'central/SingleMu_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root')
    muon_QCD_file = File(path_to_files + 'QCD_data_mu.root')
    
    #get histograms
    
    #store normalisation of all samples
    
    
    

