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
    
    from config.latex_labels import b_tag_bins_latex, samples_latex
    
    path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-12-241_V4/central/'
    lumi = 5050
    data = 'ElectronHad'
    pfmuon = 'PFMuon_'
    histogram_files = {
            'TTJet': path_to_files + 'TTJet_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'data' : path_to_files + '%s_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (data, str(lumi), pfmuon),
            'WJets': path_to_files + 'WJets_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'ZJets': path_to_files + 'DYJetsToLL_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'QCD': path_to_files + 'QCD_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'SingleTop': path_to_files + 'SingleTop_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
                       }
    
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbarPlusMetAnalysis/EPlusJets/Ref selection/Electron/electron_AbsEta_' + b_tag_bin
    qcd_control_region = control_region.replace('Ref selection', 'QCDConversions')
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region, qcd_control_region], histogram_files)
    prepare_histograms(histograms, rebin=10)
    
    qcd_from_data = histograms['data'][qcd_control_region]
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale(1.0/n_qcd_control_region*n_qcd_predicted_mc)
    
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data, 
                          histograms['ZJets'][control_region], histograms['WJets'][control_region], 
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    histogram_name = 'electron_AbsEta_2orMoreBtags'
    histogram_title = 'CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV \n e+jets, $\geq$4 jets, ' + b_tag_bins_latex[b_tag_bin]
    x_axis_title = '$\left|\eta(e)\\right|$'
    y_axis_title = 'Events/(0.2 GeV)'
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors, 
                                 histogram_name, histogram_title, x_axis_title, 
                                 y_axis_title, x_limits=[0,2.6],
                                 mc_error=0.15, mc_errors_label='$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty')
