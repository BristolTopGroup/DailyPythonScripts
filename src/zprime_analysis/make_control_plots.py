'''
Created on 4 May 2013

@author: kreczko
'''


from config import CMS
from tools.ROOT_utils import get_histograms_from_files
from tools.plotting import make_data_mc_comparison_plot, Histogram_properties
from tools.hist_utilities import prepare_histograms
                
if __name__ == '__main__':
    CMS.title['fontsize'] = 40
    CMS.x_axis_title['fontsize'] = 50
    CMS.y_axis_title['fontsize'] = 50
    CMS.axis_label_major['labelsize'] = 40
    CMS.axis_label_minor['labelsize'] = 40
    CMS.legend_properties['size'] = 40
    
    from config.latex_labels import b_tag_bins_latex, samples_latex
    
    path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-11-265_V2/'
    lumi = 5028
    data = 'ElectronHad'
    pfmuon = 'PFMuon_'
    histogram_files = {
            'TTJet': path_to_files + 'TTJet_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'data' : path_to_files + '%s_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (data, str(lumi), pfmuon),
            'WJets': path_to_files + 'WJetsToLNu_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'ZJets': path_to_files + 'DYJetsToLL_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'QCD': path_to_files + 'QCD_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'SingleTop': path_to_files + 'SingleTop_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
                       }
    
    b_tag_bin = '0btag'
    control_region = 'topReconstruction/backgroundShape/mttbar_3jets_conversions_withMETAndAsymJets_' + b_tag_bin
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=50)
    
    histograms_to_draw = [histograms['data'][control_region], histograms['QCD'][control_region], 
                          histograms['ZJets'][control_region], histograms['WJets'][control_region], 
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'Mttbar'
    histogram_properties.title = 'CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV \n e+jets, $\geq$4 jets, ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$m_{\mathrm{t}\\bar{\mathrm{t}}}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(50 GeV)'
    histogram_properties.x_limits=[300,1800]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors, 
                                 histogram_properties)
