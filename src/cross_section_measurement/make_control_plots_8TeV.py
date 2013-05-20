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
    
    path_to_data = '/storage/TopQuarkGroup/results/histogramfiles/AN-13-015_V6/central/'
    path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-13-015_V6/central/'
    suffix = ''
    lumi = 19584
    data = 'SingleElectron'
    pfmuon = 'PFMuon_'
    histogram_files = {
            'data' : path_to_data + '%s_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (data, str(lumi), pfmuon),
            'TTJet': path_to_files + 'TTJet_%spb_PFElectron_%sPF2PATJets_PFMET%s.root' % (str(lumi), pfmuon, suffix),
            'WJets': path_to_files + 'WJets_%spb_PFElectron_%sPF2PATJets_PFMET%s.root' % (str(lumi), pfmuon, suffix),
            'ZJets': path_to_files + 'DYJetsToLL_%spb_PFElectron_%sPF2PATJets_PFMET%s.root' % (str(lumi), pfmuon, suffix),
            'QCD': path_to_files + 'QCD_%spb_PFElectron_%sPF2PATJets_PFMET%s.root' % (str(lumi), pfmuon, suffix),
            'SingleTop': path_to_files + 'SingleTop_%spb_PFElectron_%sPF2PATJets_PFMET%s.root' % (str(lumi), pfmuon, suffix)
    }
    
    e_title = 'CMS Preliminary, $\mathcal{L}$ = 19.6 fb$^{-1}$ at $\sqrt{s}$ = 8 TeV \n e+jets, $\geq$4 jets'

    #electron |eta|
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Electron/electron_AbsEta_' + b_tag_bin
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
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
    histogram_properties.y_axis_title = 'Events/(0.1)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #MET
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_' + b_tag_bin
    qcd_control_region = control_region.replace('Ref selection', 'QCDConversions')
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region, qcd_control_region], histogram_files)
    prepare_histograms(histograms, rebin=1)
    
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
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$E_{\mathrm{T}}^{\mathrm{miss}}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(5 GeV)'
    histogram_properties.x_limits = [0, 200]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    #MET log
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_' + b_tag_bin
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
    histogram_properties.name = 'EPlusJets_patType1CorrectedPFMet_log_' + b_tag_bin
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$E_{\mathrm{T}}^{\mathrm{miss}}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(10 GeV)'
    histogram_properties.x_limits = [200, 700]
    #histogram_properties.y_limits = [0.1, 50]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    histogram_properties.set_log_y = True
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #MET phi
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_phi_' + b_tag_bin
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
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\phi\left(E_{\mathrm{T}}^{\mathrm{miss}}\\right)$'
    histogram_properties.y_axis_title = 'Events/(0.2)'
    histogram_properties.x_limits = [-3.3, 3.3]
    #histogram_properties.y_limits = [0, 850]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    histogram_properties.legend_columns = 2
    #histogram_properties.legend_location = 'upper center'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)

    #HT
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/HT_' + b_tag_bin
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
    histogram_properties.name = 'EPlusJets_HT_' + b_tag_bin
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = 'HT [GeV]'
    histogram_properties.y_axis_title = 'Events/(10 GeV)'
    histogram_properties.x_limits = [100, 1000]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'

    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)

    #ST
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/ST_' + b_tag_bin
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
    histogram_properties.name = 'EPlusJets_patType1CorrectedPFMet_ST_' + b_tag_bin
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = 'ST [GeV]'
    histogram_properties.y_axis_title = 'Events/(10 GeV)'
    histogram_properties.x_limits = [150, 1200]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'

    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)


    #WPT
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/WPT_' + b_tag_bin
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
    histogram_properties.name = 'EPlusJets_patType1CorrectedPFMet_WPT_' + b_tag_bin
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = 'W $p_T$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(10 GeV)'
    histogram_properties.x_limits = [0, 500]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'

    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #MT
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/Transverse_Mass_' + b_tag_bin
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
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = 'transverse W boson mass [GeV]'
    histogram_properties.y_axis_title = 'Events/(5 GeV)'
    histogram_properties.x_limits = [0, 200]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #M3
    b_tag_bin = ''
    control_region = 'DiffVariablesAnalyser/EPlusJets/M3'
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=1)
    
    histograms_to_draw = [histograms['data'][control_region], histograms['QCD'][control_region],
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_M3'
    histogram_properties.title = e_title
    histogram_properties.x_axis_title = '$M3$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(9 GeV)'
    histogram_properties.x_limits = [100, 600]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)

    #bjet invariant mass
    b_tag_bin = '4orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/bjet_invariant_mass_' + b_tag_bin
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=10)
    
    qcd_predicted_mc = histograms['QCD'][control_region]
    
    histograms_to_draw = [histograms['data'][control_region], qcd_predicted_mc,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_BJets_invmass_' + b_tag_bin
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$M_{\mathrm{b}\\bar{\mathrm{b}}}$'
    histogram_properties.y_axis_title = 'Normalised events/(10 GeV)'
    histogram_properties.x_limits = [0, 800]
    histogram_properties.mc_error = 0.15
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)

    #b-tag multiplicity
    b_tag_bin = ''
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/N_BJets'
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=1)
    
    n_qcd_predicted_mc = histograms['QCD'][control_region]
    
    histograms_to_draw = [histograms['data'][control_region], n_qcd_predicted_mc,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_N_BJets' + b_tag_bin
    histogram_properties.title = e_title
    histogram_properties.x_axis_title = 'B-tag multiplicity'
    histogram_properties.y_axis_title = 'Events'
    histogram_properties.x_limits = [-0.5, 5.5]
    histogram_properties.mc_error = 0.15
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    b_tag_bin = ''
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/N_BJets_reweighted'
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=1)
    
    n_qcd_predicted_mc = histograms['QCD'][control_region]
    
    histograms_to_draw = [histograms['data'][control_region], n_qcd_predicted_mc,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_N_BJets_reweighted' + b_tag_bin
    histogram_properties.title = e_title
    histogram_properties.x_axis_title = 'B-tag multiplicity'
    histogram_properties.y_axis_title = 'Events'
    histogram_properties.x_limits = [-0.5, 5.5]
    histogram_properties.mc_error = 0.15
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)

    #Jet multiplicity
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Jets/N_Jets_' + b_tag_bin
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=1)
    
    qcd_predicted_mc = histograms['QCD'][control_region]
    
    histograms_to_draw = [histograms['data'][control_region], qcd_predicted_mc,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_N_Jets_' + b_tag_bin
    histogram_properties.title = e_title + b_tag_bins_latex['0orMoreBtag']
    histogram_properties.x_axis_title = 'Jet multiplicity'
    histogram_properties.y_axis_title = 'Events'
    histogram_properties.x_limits = [3.5, 9.5]
    histogram_properties.mc_error = 0.15
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)

    #QCD control regions (electron |eta|)
    b_tag_bin = '0btag'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Electron/electron_AbsEta_' + b_tag_bin
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
    histogram_properties.name = 'QCD_conversion_control_region_electron_AbsEta_' + b_tag_bin
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
    histogram_properties.y_axis_title = 'Events/(0.1)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.mc_error = 0.0
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    histogram_properties.legend_location = 'upper left'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    b_tag_bin = '0btag'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Electron/electron_AbsEta_' + b_tag_bin
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
    histogram_properties.name = 'QCD_non_iso_control_region_electron_AbsEta_' + b_tag_bin
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
    histogram_properties.y_axis_title = 'Events/(0.1)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.mc_error = 0.0
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    histogram_properties.legend_location = 'upper right'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #QCD shape comparison
    b_tag_bin = '0btag'
    control_region_1 = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Electron/electron_AbsEta_' + b_tag_bin
    control_region_2 = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Electron/electron_AbsEta_' + b_tag_bin
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region_1, control_region_2], histogram_files)
    prepare_histograms(histograms, rebin=10)
    
    region_1 = histograms['data'][control_region_1].Clone()
    region_2 = histograms['data'][control_region_2].Clone()
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'QCD_control_region_comparison_electron_AbsEta_' + b_tag_bin
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
    histogram_properties.y_axis_title = 'arbitrary units/(0.1)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.y_limits = [0, 0.14]
    histogram_properties.mc_error = 0.0
    histogram_properties.legend_location = 'upper right'
    make_control_region_comparison(region_1, region_2, 
                                   name_region_1 = 'conversions', name_region_2='non-isolated electrons',
                                   histogram_properties=histogram_properties)

    # Number of vertices
    b_tag_bin = ''
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Vertices/nVertex'
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=1)
    
    n_qcd_predicted_mc = histograms['QCD'][control_region]
    
    histograms_to_draw = [histograms['data'][control_region], n_qcd_predicted_mc,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_nVertex' + b_tag_bin
    histogram_properties.title = e_title + b_tag_bins_latex['0orMoreBtag']
    histogram_properties.x_axis_title = 'N(PV)'
    histogram_properties.y_axis_title = 'arbitrary units'
    histogram_properties.x_limits = [0, 50]
    histogram_properties.mc_error = 0.0
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, normalise=True)
    
    b_tag_bin = ''
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Vertices/nVertex_reweighted'
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=1)
    
    n_qcd_predicted_mc = histograms['QCD'][control_region]
    
    histograms_to_draw = [histograms['data'][control_region], n_qcd_predicted_mc,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_nVertex_reweighted' + b_tag_bin
    histogram_properties.title = e_title + b_tag_bins_latex['0orMoreBtag']
    histogram_properties.x_axis_title = 'N(PV)'
    histogram_properties.y_axis_title = 'arbitrary units'
    histogram_properties.x_limits = [0, 50]
    histogram_properties.mc_error = 0.0
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, normalise=True)

    #muons
    data = 'SingleMu'
    histogram_files['data'] = path_to_data + '%s_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (data, str(lumi), pfmuon)
    histogram_files['QCD'] = path_to_files + 'QCD_Muon_%spb_PFElectron_%sPF2PATJets_PFMET%s.root' % (str(lumi), pfmuon, suffix)
    mu_title = 'CMS Preliminary, $\mathcal{L}$ = 19.6 fb$^{-1}$ at $\sqrt{s}$ = 8 TeV \n $\mu$+jets, $\geq$4 jets'
    
    #Muon |eta|
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Muon/muon_AbsEta_' + b_tag_bin
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
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(\mu)\\right|$'
    histogram_properties.y_axis_title = 'Events/(0.1)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_' + b_tag_bin
    qcd_control_region = control_region.replace('Ref selection', 'QCD non iso mu+jets')
    qcd_control_region = control_region.replace(b_tag_bin, '0btag')
    
    histograms = get_histograms_from_files([control_region, qcd_control_region], histogram_files)
    prepare_histograms(histograms, rebin=1)
    
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
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$E_{\mathrm{T}}^{\mathrm{miss}}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(5 GeV)'
    histogram_properties.x_limits = [0, 200]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)

    #MET log
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_' + b_tag_bin
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
    histogram_properties.name = 'MuPlusJets_patType1CorrectedPFMet_log_' + b_tag_bin
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$E_{\mathrm{T}}^{\mathrm{miss}}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(10 GeV)'
    histogram_properties.x_limits = [200, 700]
    #histogram_properties.y_limits = [0.1, 50]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    histogram_properties.set_log_y = True
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #MET phi
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_phi_' + b_tag_bin
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
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\phi\left(E_{\mathrm{T}}^{\mathrm{miss}}\\right)$'
    histogram_properties.y_axis_title = 'Events/(0.2)'
    histogram_properties.x_limits = [-3.3, 3.3]
    #histogram_properties.y_limits = [0, 850]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    histogram_properties.legend_columns = 2
    #histogram_properties.legend_location = 'upper center'
    
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)

    #HT
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/HT_' + b_tag_bin
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
    histogram_properties.name = 'MuPlusJets_HT_' + b_tag_bin
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = 'HT [GeV]'
    histogram_properties.y_axis_title = 'Events/(10 GeV)'
    histogram_properties.x_limits = [100, 1000]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'

    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)

    #ST
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/ST_' + b_tag_bin
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
    histogram_properties.name = 'MuPlusJets_patType1CorrectedPFMet_ST_' + b_tag_bin
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = 'ST [GeV]'
    histogram_properties.y_axis_title = 'Events/(10 GeV)'
    histogram_properties.x_limits = [150, 1200]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'

    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)


    #WPT
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/WPT_' + b_tag_bin
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
    histogram_properties.name = 'MuPlusJets_patType1CorrectedPFMet_WPT_' + b_tag_bin
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = 'W $p_T$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(10 GeV)'
    histogram_properties.x_limits = [0, 500]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'

    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #MT
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/Transverse_Mass_' + b_tag_bin
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
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = 'transverse W boson mass [GeV]'
    histogram_properties.y_axis_title = 'Events/(5 GeV)'
    histogram_properties.x_limits = [0, 200]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #M3
    b_tag_bin = ''
    control_region = 'DiffVariablesAnalyser/MuPlusJets/M3'
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=1)
    
    histograms_to_draw = [histograms['data'][control_region], histograms['QCD'][control_region],
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_M3'
    histogram_properties.title = mu_title
    histogram_properties.x_axis_title = '$M3$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(9 GeV)'
    histogram_properties.x_limits = [100, 600]
    histogram_properties.mc_error = 0.15
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    #Jet multiplicity
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Jets/N_Jets_' + b_tag_bin
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=1)
    
    qcd_predicted_mc = histograms['QCD'][control_region]
    
    histograms_to_draw = [histograms['data'][control_region], qcd_predicted_mc,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_N_Jets_' + b_tag_bin
    histogram_properties.title = mu_title + b_tag_bins_latex['0orMoreBtag']
    histogram_properties.x_axis_title = 'Jet multiplicity'
    histogram_properties.y_axis_title = 'Events'
    histogram_properties.x_limits = [3.5, 9.5]
    histogram_properties.mc_error = 0.15
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)

    #bjet invariant mass
    b_tag_bin = '4orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/bjet_invariant_mass_' + b_tag_bin
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=10)
    
    qcd_predicted_mc = histograms['QCD'][control_region]
    
    histograms_to_draw = [histograms['data'][control_region], qcd_predicted_mc,
                          histograms['ZJets'][control_region], histograms['WJets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', samples_latex['ZJets'], samples_latex['WJets'], 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'blue', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_BJets_invmass_' + b_tag_bin
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$M_{\mathrm{b}\\bar{\mathrm{b}}}$'
    histogram_properties.y_axis_title = 'Normalised events/(10 GeV)'
    histogram_properties.x_limits = [0, 800]
    histogram_properties.mc_error = 0.15
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)

    #b-tag multiplicity
    b_tag_bin = ''
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/N_BJets'
    
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
    histogram_properties.title = mu_title
    histogram_properties.x_axis_title = 'B-tag multiplicity'
    histogram_properties.y_axis_title = 'Events'
    histogram_properties.x_limits = [-0.5, 5.5]
    histogram_properties.mc_error = 0.15
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    b_tag_bin = ''
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/N_BJets_reweighted'
    
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
    histogram_properties.title = mu_title
    histogram_properties.x_axis_title = 'B-tag multiplicity'
    histogram_properties.y_axis_title = 'Events'
    histogram_properties.x_limits = [-0.5, 5.5]
    histogram_properties.mc_error = 0.15
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties)
    
    # Number of vertices
    b_tag_bin = ''
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Vertices/nVertex'
    
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
    histogram_properties.x_limits = [0, 50]
    histogram_properties.mc_error = 0.0
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, normalise=True)
    
    b_tag_bin = ''
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Vertices/nVertex_reweighted'
    
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
    histogram_properties.x_limits = [0, 50]
    histogram_properties.mc_error = 0.0
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, normalise=True)
