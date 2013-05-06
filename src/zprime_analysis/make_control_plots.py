'''
Created on 4 May 2013

@author: kreczko
'''


from config import CMS
from tools.ROOT_utililities import get_histograms_from_files
from tools.plotting import make_data_mc_comparison_plot
from tools.hist_utilities import prepare_histograms
                
if __name__ == '__main__':
    CMS.title['fontsize'] = 40
    CMS.x_axis_title['fontsize'] = 50
    CMS.y_axis_title['fontsize'] = 50
    CMS.axis_label_major['labelsize'] = 40
    CMS.axis_label_minor['labelsize'] = 40
    CMS.legend_properties['size'] = 40
    
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
    control_region = 'topReconstruction/backgroundShape/mttbar_3jets_conversions_withMETAndAsymJets_0btag'
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=50)
    
    histograms_to_draw = [histograms['data'][control_region], histograms['QCD'][control_region], 
                          histograms['ZJets'][control_region], histograms['WJets'][control_region], 
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'Z/$\gamma^*$ + jets', 'W $\\rightarrow \ell\\nu$', 'Single-Top', '$\mathrm{t}\\bar{\mathrm{t}}$']
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    histogram_name = 'Mttbar'
    histogram_title = 'CMS Preliminary, $\mathcal{L}$ = 5.0 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV \n e+jets, $\geq$4 jets, 0 b-tag'
    x_axis_title = '$m_{\mathrm{t}\\bar{\mathrm{t}}}$ [GeV]'
    y_axis_title = 'Events/(50 GeV)'
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors, histogram_name, histogram_title, x_axis_title, y_axis_title, x_limits=[300,1800])
