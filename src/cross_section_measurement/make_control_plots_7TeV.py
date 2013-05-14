'''
Created on 4 May 2013

@author: kreczko
'''


from config import CMS
from tools.ROOT_utililities import get_histograms_from_files
from tools.plotting import make_data_mc_comparison_plot, Histogram_properties, make_control_region_comparison
from tools.plotting import make_plot
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
    
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale(1.0 / n_qcd_control_region * n_qcd_predicted_mc)
    
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'electron_AbsEta_' + b_tag_bin
    histogram_properties.title = 'CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV \n e+jets, $\geq$4 jets, ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
    histogram_properties.y_axis_title = 'Events/(0.2 GeV)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbarPlusMetAnalysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_' + b_tag_bin
    qcd_control_region = control_region.replace('Ref selection', 'QCDConversions')
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region, qcd_control_region], histogram_files)
    prepare_histograms(histograms, rebin=5)
    
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale(1.0 / n_qcd_control_region * n_qcd_predicted_mc)
    
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_patType1CorrectedPFMet_' + b_tag_bin
    histogram_properties.title = 'CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV \n e+jets, $\geq$4 jets, ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$E_{\mathrm{T}}^{\mathrm{miss}}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(5 GeV)'
    histogram_properties.x_limits = [0, 200]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    MET log
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbarPlusMetAnalysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_' + b_tag_bin
    qcd_control_region = control_region.replace('Ref selection', 'QCDConversions')
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region, qcd_control_region], histogram_files)
    prepare_histograms(histograms, rebin=10)
    
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale(1.0 / n_qcd_control_region * n_qcd_predicted_mc)
    
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_patType1CorrectedPFMet_log_' + b_tag_bin
    histogram_properties.title = 'CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV \n e+jets, $\geq$4 jets, ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$E_{\mathrm{T}}^{\mathrm{miss}}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(10 GeV)'
    histogram_properties.x_limits = [200, 600]
    histogram_properties.y_limits = [0.1, 50]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    histogram_properties.set_log_y = True
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #MET phi
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbarPlusMetAnalysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_phi_' + b_tag_bin
    qcd_control_region = control_region.replace('Ref selection', 'QCDConversions')
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region, qcd_control_region], histogram_files)
    prepare_histograms(histograms, rebin=2)
    
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale(1.0 / n_qcd_control_region * n_qcd_predicted_mc)
    
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_patType1CorrectedPFMet_phi_' + b_tag_bin
    histogram_properties.title = 'CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV \n e+jets, $\geq$4 jets, ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\phi\left(E_{\mathrm{T}}^{\mathrm{miss}}\\right)$'
    histogram_properties.y_axis_title = 'Events/(0.2)'
    histogram_properties.x_limits = [-3.3, 3.3]
    histogram_properties.y_limits = [0, 850]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    histogram_properties.legend_columns = 2
    histogram_properties.legend_location = 'upper center'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #MT
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbarPlusMetAnalysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/Transverse_Mass_' + b_tag_bin
    qcd_control_region = control_region.replace('Ref selection', 'QCDConversions')
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region, qcd_control_region], histogram_files)
    prepare_histograms(histograms, rebin=5)
    
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale(1.0 / n_qcd_control_region * n_qcd_predicted_mc)
    
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_patType1CorrectedPFMet_MT_' + b_tag_bin
    histogram_properties.title = 'CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV \n e+jets, $\geq$4 jets, ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = 'transverse W boson mass [GeV]'
    histogram_properties.y_axis_title = 'Events/(5 GeV)'
    histogram_properties.x_limits = [0, 200]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #M3
    b_tag_bin = '2orMoreBtags'
    control_region = 'MttbarAnalysis/ElectronPlusJets/Ref selection/FourJetChi2/m3_' + b_tag_bin
    qcd_control_region = control_region.replace('Ref selection', 'QCDConversions')
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region, qcd_control_region], histogram_files)
    prepare_histograms(histograms, rebin=10)
    
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale(1.0 / n_qcd_control_region * n_qcd_predicted_mc)
    
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_M3_' + b_tag_bin
    histogram_properties.title = 'CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV \n e+jets, $\geq$4 jets, ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$M3$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(10 GeV)'
    histogram_properties.x_limits = [0, 500]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    b_tag_bin = '0orMoreBtag'
#    control_region = 'TTbarPlusMetAnalysis/EPlusJets/Ref selection/Jets/all_jet_eta_' + b_tag_bin
    control_region = 'JetAnalysis/all_jet_eta_' + b_tag_bin
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=10)
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'jet_eta_' + b_tag_bin
    histogram_properties.title = 'CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV \n e+jets, $\geq$4 jets, ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(\mathrm{jet})\\right|$'
    histogram_properties.y_axis_title = 'arbitrary units/(0.2 GeV)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.y_limits = [0, 0.06]
    
    make_plot(histograms['data'][control_region], 'data', histogram_properties, normalise=True)
    
    b_tag_bin = '0btag'
    control_region = 'TTbarPlusMetAnalysis/EPlusJets/QCDConversions/Electron/electron_AbsEta_' + b_tag_bin
    qcd_control_region = control_region.replace('Ref selection', 'QCDConversions')
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region, qcd_control_region], histogram_files)
    prepare_histograms(histograms, rebin=10)
    
    qcd_from_data = histograms['QCD'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale(1.0 / n_qcd_control_region * n_qcd_predicted_mc)
    
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'conversion_control_region_electron_AbsEta_' + b_tag_bin
    histogram_properties.title = 'CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV \n e+jets, $\geq$4 jets, ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
    histogram_properties.y_axis_title = 'Events/(0.1 GeV)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.mc_error = 0.0
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    histogram_properties.legend_location = 'upper left'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    b_tag_bin = '0btag'
    control_region = 'TTbarPlusMetAnalysis/EPlusJets/QCD non iso e+jets/Electron/electron_AbsEta_' + b_tag_bin
    qcd_control_region = control_region.replace('Ref selection', 'QCDConversions')
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region, qcd_control_region], histogram_files)
    prepare_histograms(histograms, rebin=10)
    
    qcd_from_data = histograms['QCD'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale(1.0 / n_qcd_control_region * n_qcd_predicted_mc)
    
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'non_iso_control_region_electron_AbsEta_' + b_tag_bin
    histogram_properties.title = 'CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV \n e+jets, $\geq$4 jets, ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
    histogram_properties.y_axis_title = 'Events/(0.1 GeV)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.mc_error = 0.0
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    histogram_properties.legend_location = 'upper right'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #shape comparison
    b_tag_bin = '0btag'
    control_region_1 = 'TTbarPlusMetAnalysis/EPlusJets/QCDConversions/Electron/electron_AbsEta_' + b_tag_bin
    control_region_2 = 'TTbarPlusMetAnalysis/EPlusJets/QCD non iso e+jets/Electron/electron_AbsEta_' + b_tag_bin
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region_1, control_region_2], histogram_files)
    prepare_histograms(histograms, rebin=10)
    
    region_1 = histograms['data'][control_region_1].Clone()
    region_2 = histograms['data'][control_region_2].Clone()
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'control_region_comparison_electron_AbsEta_' + b_tag_bin
    histogram_properties.title = 'CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV \n e+jets, $\geq$4 jets, ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
    histogram_properties.y_axis_title = 'arbitrary units/(0.1 GeV)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.y_limits = [0, 0.14]
    histogram_properties.mc_error = 0.0
    histogram_properties.legend_location = 'upper right'
    make_control_region_comparison(region_1, region_2, 
                                   name_region_1 = 'conversions', name_region_2='non-isolated electrons',
                                   histogram_properties=histogram_properties)

#muons
    data = 'SingleMu'
    histogram_files['data'] = path_to_files + '%s_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (data, str(lumi), pfmuon)
    histogram_files['QCD'] = path_to_files + 'QCD_Pt-20_MuEnrichedPt-15_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon)
    mu_title = 'CMS Preliminary, $\mathcal{L}$ = 5.1 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV \n $\mu$+jets, $\geq$4 jets, '
    
    #Muon |eta|
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbarPlusMetAnalysis/MuPlusJets/Ref selection/Muon/muon_AbsEta_' + b_tag_bin
    qcd_control_region = control_region.replace('Ref selection', 'QCD non iso mu+jets')
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region, qcd_control_region], histogram_files)
    prepare_histograms(histograms, rebin=10)
    
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()*1.2
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale(1.0 / n_qcd_control_region * n_qcd_predicted_mc)
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'muon_AbsEta_' + b_tag_bin
    histogram_properties.title = mu_title + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(\mu)\\right|$'
    histogram_properties.y_axis_title = 'Events/(0.2 GeV)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    control_region = 'TTbarPlusMetAnalysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_' + b_tag_bin
    qcd_control_region = control_region.replace('Ref selection', 'QCD non iso mu+jets')
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region, qcd_control_region], histogram_files)
    prepare_histograms(histograms, rebin=5)
    
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()*1.2
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale(1.0 / n_qcd_control_region * n_qcd_predicted_mc)
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_patType1CorrectedPFMet_' + b_tag_bin
    histogram_properties.title = mu_title + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$E_{\mathrm{T}}^{\mathrm{miss}}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(5 GeV)'
    histogram_properties.x_limits = [0, 200]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)

    #MET log
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbarPlusMetAnalysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_' + b_tag_bin
    qcd_control_region = control_region.replace('Ref selection', 'QCD non iso mu+jets')
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region, qcd_control_region], histogram_files)
    prepare_histograms(histograms, rebin=10)
    
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale(1.0 / n_qcd_control_region * n_qcd_predicted_mc)
    
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_patType1CorrectedPFMet_log_' + b_tag_bin
    histogram_properties.title = mu_title + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$E_{\mathrm{T}}^{\mathrm{miss}}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(10 GeV)'
    histogram_properties.x_limits = [200, 600]
    histogram_properties.y_limits = [0.1, 50]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    histogram_properties.set_log_y = True
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #MET phi
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbarPlusMetAnalysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_phi_' + b_tag_bin
    qcd_control_region = control_region.replace('Ref selection', 'QCD non iso mu+jets')
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region, qcd_control_region], histogram_files)
    prepare_histograms(histograms, rebin=2)
    
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale(1.0 / n_qcd_control_region * n_qcd_predicted_mc)
    
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_patType1CorrectedPFMet_phi_' + b_tag_bin
    histogram_properties.title = mu_title + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\phi\left(E_{\mathrm{T}}^{\mathrm{miss}}\\right)$'
    histogram_properties.y_axis_title = 'Events/(0.2)'
    histogram_properties.x_limits = [-3.3, 3.3]
    histogram_properties.y_limits = [0, 850]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    histogram_properties.legend_columns = 2
    histogram_properties.legend_location = 'upper center'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #MT
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbarPlusMetAnalysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/Transverse_Mass_' + b_tag_bin
    qcd_control_region = control_region.replace('Ref selection', 'QCD non iso mu+jets')
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region, qcd_control_region], histogram_files)
    prepare_histograms(histograms, rebin=5)
    
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale(1.0 / n_qcd_control_region * n_qcd_predicted_mc)
    
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_patType1CorrectedPFMet_MT_' + b_tag_bin
    histogram_properties.title = mu_title + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = 'transverse W boson mass [GeV]'
    histogram_properties.y_axis_title = 'Events/(5 GeV)'
    histogram_properties.x_limits = [0, 200]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #M3
    b_tag_bin = '2orMoreBtags'
    control_region = 'MttbarAnalysis/MuonPlusJets/Ref selection/FourJetChi2/m3_' + b_tag_bin
    qcd_control_region = control_region.replace('Ref selection', 'QCD non iso mu+jets')
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region, qcd_control_region], histogram_files)
    prepare_histograms(histograms, rebin=10)
    
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale(1.0 / n_qcd_control_region * n_qcd_predicted_mc)
    
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_M3_' + b_tag_bin
    histogram_properties.title = mu_title + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$M3$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(10 GeV)'
    histogram_properties.x_limits = [0, 500]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #b-tag multiplicity
    b_tag_bin = ''
    control_region = 'TTbarPlusMetAnalysis/MuPlusJets/Ref selection/N_BJets'
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=1)
    
    n_qcd_predicted_mc = histograms['QCD'][control_region]
    
    histograms_to_draw = [histograms['data'][control_region], n_qcd_predicted_mc,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_N_BJets' + b_tag_bin
    histogram_properties.title = mu_title + b_tag_bins_latex['0orMoreBtag']
    histogram_properties.x_axis_title = 'B-tag multiplicity'
    histogram_properties.y_axis_title = 'Events'
    histogram_properties.x_limits = [-0.5, 5.5]
    histogram_properties.mc_error = 0.0
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    b_tag_bin = ''
    control_region = 'TTbarPlusMetAnalysis/MuPlusJets/Ref selection/N_BJets_reweighted'
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=1)
    
    n_qcd_predicted_mc = histograms['QCD'][control_region]
    
    histograms_to_draw = [histograms['data'][control_region], n_qcd_predicted_mc,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_N_BJets_reweighted' + b_tag_bin
    histogram_properties.title = mu_title + b_tag_bins_latex['0orMoreBtag']
    histogram_properties.x_axis_title = 'B-tag multiplicity'
    histogram_properties.y_axis_title = 'Events'
    histogram_properties.x_limits = [-0.5, 5.5]
    histogram_properties.mc_error = 0.0
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    #vertex
    b_tag_bin = ''
    control_region = 'TTbarPlusMetAnalysis/MuPlusJets/Ref selection/Vertices/nVertex'
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=1)
    
    n_qcd_predicted_mc = histograms['QCD'][control_region]
    
    histograms_to_draw = [histograms['data'][control_region], n_qcd_predicted_mc,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_nVertex' + b_tag_bin
    histogram_properties.title = mu_title + b_tag_bins_latex['0orMoreBtag']
    histogram_properties.x_axis_title = 'N(PV)'
    histogram_properties.y_axis_title = 'arbitrary units'
    histogram_properties.x_limits = [0, 22]
    histogram_properties.mc_error = 0.0
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, normalise=True)
    
    b_tag_bin = ''
    control_region = 'TTbarPlusMetAnalysis/MuPlusJets/Ref selection/Vertices/nVertex_reweighted'
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=1)
    
    n_qcd_predicted_mc = histograms['QCD'][control_region]
    
    histograms_to_draw = [histograms['data'][control_region], n_qcd_predicted_mc,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_nVertex_reweighted' + b_tag_bin
    histogram_properties.title = mu_title + b_tag_bins_latex['0orMoreBtag']
    histogram_properties.x_axis_title = 'N(PV)'
    histogram_properties.y_axis_title = 'arbitrary units'
    histogram_properties.x_limits = [0, 22]
    histogram_properties.mc_error = 0.0
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, normalise=True)