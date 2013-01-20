'''
Created on 9 Dec 2012

@author: kreczko

Episode 0 - Histogram preparation:
- get all interesting histograms from the analysis output files
- make sure the bins are correct (rebin etc)
- write output to a single file! Folder:
    - electron, muon
        - TTJet, QCD (from data), V+Jets, single top
            - met 
                - types
            - HT
            - ST
                -types
            - other differential variables
            - lepton eta
                - met bins
                - HT bins
                - etc
result output files have the format
TTbar_plus_X_analysis_<lumi>pbinv_<nbtag>.root
'''
from rootpy.io import File
from rootpy import asrootpy
from array import array
from config import cross_section_measurement as csm, summations
from tools.ROOT_utililities import get_histograms_from_files, get_histogram_info_tuple, root_file_mkdir

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
    #set to batch mode
    ROOT.gROOT.SetBatch(True)
    #ignore warnings
#    ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 3001;");
    # setup
    bin_edges = [0, 25, 45, 70, 100, 1000]
    bin_widths = [25, 20, 25, 30, 150]
    met_bins_ROOT = ['0-25', '25-45', '45-70', '70-100', '100-inf']
    btag_labels = []
    
    path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-12-241_V4/'

    #different inputs
    input_folders = ['central', 'BJet_down', 'BJet_up', 'JES_down', 'JES_up', 
                     'LightJet_down', 'LightJet_up', 'PU_down', 'PU_up']
    #'PDFWeights' x 44
    #read all data but TTJet from central    
    
    # get data from histograms or JSON files
    TTJet_file = path_to_files + 'central/TTJet_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'
    #this should consist of 6 different files
    SingleTop_file = path_to_files + 'central/SingleTop_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'
    W1Jet_file = path_to_files + 'central/W1Jet_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'
    W2Jets_file = path_to_files + 'central/W2Jets_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'
    W3Jets_file = path_to_files + 'central/W3Jets_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'
    W4Jets_file = path_to_files + 'central/W4Jets_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'
    ZJets_file = path_to_files + 'central/DYJetsToLL_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'
    
    data_file_electron = path_to_files + 'central/ElectronHad_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'
    data_file_muon = path_to_files + 'central/SingleMu_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'

#    electron_QCD_file = File(path_to_files + 'QCD_data_electron.root')
#    muon_QCD_file = File(path_to_files + 'QCD_data_muon.root')
    
    histograms_of_interest = csm.get_histograms_of_interest_7TeV()
    #get histograms
    histograms = get_histograms_from_files(histograms_of_interest, {'data':data_file_electron})
    #store normalisation of all samples
    #for now OK.
    
    output_files = {}
    luminosity = 5050
    for b_tag_bin in summations.all_b_tag_bins:
        file_name = "TTbar_plus_X_analysis_%dpbinv_%s.root" %(luminosity, b_tag_bin)
        output_files[b_tag_bin] = File(file_name, "recreate")
        
    #sum samples up    
        
    #write them all up
    for sample, histogram_list  in histograms.iteritems():
        for histogram_path, histogram in histogram_list.iteritems():
            directory, histogram_name, b_tag_bin = get_histogram_info_tuple(histogram_path)
            analysis_folder = ""
            variable_folder = ""
            variable_bin = ""
            distribution= ""
            if 'EPlusJets' in histogram_path:#electron channel
                analysis_folder = 'electron'
            elif 'MuPlusJets' in histogram_path:#muon channel
                analysis_folder = 'muon'

            for variable, identifier in csm.variable_identifiers.iteritems():
                if identifier in histogram_path:
                    variable_folder = variable
                
            if analysis_folder + '_AbsEta' in histogram_name:
                distribution = 'lepton_absolute_eta'
                histogram.SetName('absolute_eta_' + variable_folder + 'bin_')
            
            # electron/data/lepton_absolute_eta/absolute_eta_VAR_bin_X_Y
            new_path = analysis_folder + '/' + sample + '/' + distribution + '/' + variable_folder
            current_file = output_files[b_tag_bin]
            current_directory = root_file_mkdir(current_file, new_path)
    
    for output_file in output_files.items():
        output_file.Close()
    
    
    

