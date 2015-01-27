'''
Created on 15 Jan 2013

@author: kreczko

Generate a QCD template from a data distribution and normalise it to the correct cross section.
The normalisation is done either from data (fit to relative isolation for electron channel) or
a scale to MC (scale to match control regions in both data and MC for muon channel).

In the end this script will create a single ROOT file 
QCD_from_data_<channel>_<lumi>.root
with the content
- qcd_template_absolute_eta_<variable bin>
...

'''
from __future__ import division
from rootpy.io import File
from tools.QCD_rate_estimation import estimate_with_fit_to_relative_isolation
from tools.ROOT_utils import set_root_defaults
# one template function per variable
def get_electron_absolute_eta_templates(b_tag):
    global electron_data_file, met_bins
    data = File(electron_data_file)
    hist_template = 'TTbarPlusMetAnalysis/EPlusJets/QCDConversions/BinnedMETAnalysis/Electron_patType1CorrectedPFMet_bin_%s/electron_AbsEta_0btag'
    
    histograms = []
    for met_bin in met_bins:
        histogram = data.Get(hist_template % met_bin).Clone('qcd_template_absolute_eta_MET_bin_%s_%s' % (met_bin, b_tag))
        histogram.Sumw2()
        #rebin to 0.2 bin width
        current_bin_width = histogram.xwidth(1)# assume all bins have the same size
        rebin = int(0.2/current_bin_width)
        if rebin > 1:
            histogram.Rebin(rebin)
        n_events = histogram.Integral()
        if not n_events == 0:
            histogram.Scale(1 / n_events)
        histograms.append(histogram)
    return histograms

def get_muon_absolute_eta_templates(b_tag):
    global muon_data_file
    data = File(muon_data_file)
    
    histograms = []
    for met_bin in met_bins:  # same tempalte for all bins
        histogram = data.etaAbs_ge2j_data.Clone('qcd_template_absolute_eta_MET_bin_%s_%s' % (met_bin, b_tag))  # already normalised to 1
        histogram.Sumw2()
        histograms.append(histogram)
    return histograms

# one normalisation function per channel
def get_electron_normalisation(met_bin, b_tag):
    global electron_data_file
    input_file = File(electron_data_file)
    histogram_for_estimation = 'TTbarPlusMetAnalysis/EPlusJets/QCD e+jets PFRelIso/BinnedMETAnalysis/Electron_patType1CorrectedPFMet_bin_%s/electron_pfIsolation_03_%s' % (met_bin, b_tag)
    input_histogram = input_file.Get(histogram_for_estimation)
    result = estimate_with_fit_to_relative_isolation(input_histogram)
    value, error = result['value'], result['error']
    return value, error
    
def get_muon_normalisation(met_bin, b_tag):
    global path_to_files
    muon_qcd_file = path_to_files + 'central/QCD_Pt-20_MuEnrichedPt-15_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'
    input_file = File(muon_qcd_file)
    histogram_for_estimation = 'TTbarPlusMetAnalysis/MuPlusJets/Ref selection/BinnedMETAnalysis/Muon_patType1CorrectedPFMet_bin_%s/muon_AbsEta_%s' % (met_bin, b_tag)
    #if not correctly scaled, rescale here
    #    
    input_histogram = input_file.Get(histogram_for_estimation)
    scale_factor = 1.21
    value = input_histogram.Integral()*scale_factor
    error = sum([input_histogram.GetBinError(bin_i)*scale_factor for bin_i in range(1, input_histogram.nbins())])
    return value, error
    

def scale_histogram(histogram, value, error):
    n_events = histogram.Integral()
    if not n_events == 0:
        histogram.Scale(value / n_events)
    # now get the error right
    if value == 0:
        return histogram
    
    for bin_i in range(1, histogram.nbins()):
        n_events_bin_i = histogram.GetBinContent(bin_i)
        fraction_of_total = n_events_bin_i / value
        histogram.SetBinError(bin_i, fraction_of_total * error)
    return histogram

def save_to_root_file(histograms, file_name):
    output = File(file_name, 'recreate')
    output.cd()
    for histogram in histograms:
        histogram.Write()
    output.close()
            

if __name__ == "__main__":
    set_root_defaults()
    met_bins = ['0-25', '25-45', '45-70', '70-100', '100-inf']
    b_tag = '0btag'  # for normalisation
    path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-12-241_V4/'
    electron_data_file = path_to_files + 'central/ElectronHad_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'
    muon_data_file = path_to_files + 'QCD_data_mu.root'
    
    electron_templates = get_electron_absolute_eta_templates(b_tag)
    muon_templates = get_muon_absolute_eta_templates(b_tag)
    
    for met_bin, template in zip(met_bins, electron_templates):
        value, error = get_electron_normalisation(met_bin, b_tag)
        template = scale_histogram(template, value, error)
    
    for met_bin, template in zip(met_bins, muon_templates):
        value, error = get_muon_normalisation(met_bin, b_tag)
        template = scale_histogram(template, value, error)  
        
    save_to_root_file(electron_templates, 'QCD_from_data_electron_5050pb-1.root')
    save_to_root_file(muon_templates, 'QCD_from_data_muon_5050pb-1.root')
        
    
        
    
    
