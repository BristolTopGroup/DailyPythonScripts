from optparse import OptionParser
from config.latex_labels import b_tag_bins_latex, samples_latex
from config.variable_binning import variable_bins_ROOT
from config import XSectionConfig
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from tools.plotting import make_data_mc_comparison_plot, Histogram_properties, \
make_control_region_comparison
from tools.hist_utilities import prepare_histograms
from tools.ROOT_utils import get_histograms_from_files, set_root_defaults

def get_fitted_normalisation( variable, channel ):
    '''
    This function now gets the error on the fit correctly, so that it can be applied if the --normalise_to_fit option is used 
    '''
    global path_to_JSON, category, met_type
    fit_results = read_data_from_JSON( path_to_JSON + variable + '/fit_results/' + category + '/fit_results_' + channel + '_' + met_type + '.txt' )
    
    fitted_normalisation = {}
    
    for sample, fit_result in fit_results.iteritems():
        total_value = 0
        total_error = 0
        for result in fit_result:
            value = result[0]
            error = result[1]
            total_value += value
            total_error += error
        if total_error > total_value:
            total_error = total_value
        fitted_normalisation[sample] = (total_value, total_error)
    return fitted_normalisation
    
def get_normalisation_error( normalisation ):
    total_normalisation = 0.
    total_error = 0.
    for _, number in normalisation.iteritems():
        total_normalisation += number[0]
        total_error += number[1]
    return total_error / total_normalisation

if __name__ == '__main__':
    set_root_defaults()
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data/absolute_eta_M3_angle_bl/',
                  help = "set path to JSON files" )
    parser.add_option( "-o", "--output_folder", dest = "output_folder", default = 'plots/control_plots/',
                  help = "set path to save plots" )
    parser.add_option( "-m", "--metType", dest = "metType", default = 'type1',
                      help = "set MET type used in the analysis of MET-dependent variables" )
    parser.add_option( "-c", "--centre-of-mass-energy", dest = "CoM", default = 8, type = int,
                      help = "set the centre of mass energy for analysis. Default = 8 [TeV]" )
    parser.add_option( "--category", dest = "category", default = 'central',
                      help = "set the category to take the fit results from (default: central)" )
    parser.add_option( "-n", "--normalise_to_fit", dest = "normalise_to_fit", action = "store_true",
                  help = "normalise the MC to fit results" )
    parser.add_option( "-a", "--additional-plots", action = "store_true", dest = "additional_QCD_plots",
                      help = "creates a set of QCD plots for exclusive bins for all variables" )

    ( options, args ) = parser.parse_args()
    measurement_config = XSectionConfig( options.CoM )
    # caching of variables for shorter access
    translate_options = measurement_config.translate_options
    
    path_to_JSON = '%s/%dTeV/' % ( options.path, measurement_config.centre_of_mass_energy )
    normalise_to_fit = options.normalise_to_fit
    if normalise_to_fit:
        output_folder = '%s/after_fit/%dTeV/' % ( options.output_folder, measurement_config.centre_of_mass_energy )
    else:
        output_folder = '%s/before_fit/%dTeV/' % ( options.output_folder, measurement_config.centre_of_mass_energy )
    make_folder_if_not_exists(output_folder)
    category = options.category
    met_type = translate_options[options.metType]
    make_additional_QCD_plots = options.additional_QCD_plots

    # this is shown as \ttbar (or MC) uncertainty on the plots
    # in fact, it takes the uncertainty on the whole MC stack
    # although unimportant, this needs revision
    mc_uncertainty = 0.10
    
    histogram_files = {
            'data' : measurement_config.data_file_electron,
            'TTJet': measurement_config.ttbar_category_templates[category],
            'V+Jets': measurement_config.VJets_category_templates[category],
            'QCD': measurement_config.electron_QCD_MC_category_templates[category],
            'SingleTop': measurement_config.SingleTop_category_templates[category],
    }

    # getting normalisations
    normalisations_electron = {
            'MET':get_fitted_normalisation( 'MET', 'electron' ),
            'HT':get_fitted_normalisation( 'HT', 'electron' ),
            'ST':get_fitted_normalisation( 'ST', 'electron' ),
            'MT':get_fitted_normalisation( 'MT', 'electron' ),
            'WPT':get_fitted_normalisation( 'WPT', 'electron' )
            }
    normalisations_muon = {
            'MET':get_fitted_normalisation( 'MET', 'muon' ),
            'HT':get_fitted_normalisation( 'HT', 'muon' ),
            'ST':get_fitted_normalisation( 'ST', 'muon' ),
            'MT':get_fitted_normalisation( 'MT', 'muon' ),
            'WPT':get_fitted_normalisation( 'WPT', 'muon' )
            }
    title_template = 'CMS Preliminary, $\mathcal{L} = %.1f$ fb$^{-1}$  at $\sqrt{s}$ = %d TeV \n %s'
    e_title = title_template % ( measurement_config.new_luminosity / 1000., measurement_config.centre_of_mass_energy, 'e+jets, $\geq$ 4 jets' )

    # electron |eta|
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Electron/electron_AbsEta_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCDConversions' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
      
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'electron_AbsEta_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
    histogram_properties.y_axis_title = 'Events/(0.1)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.mc_error = mc_uncertainty
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
      
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
  
    # electron pt
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Electron/electron_pT_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCDConversions' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
      
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'electron_pT_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$p_\mathrm{T}(e)$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(10 GeV)'
    histogram_properties.x_limits = [0, 250]
    histogram_properties.mc_error = mc_uncertainty
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
      
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
 
    # MET
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCDConversions' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
     
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    if normalise_to_fit:
        prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale, normalisation = normalisations_electron['MET'] )
    else:
        prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
     
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
     
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
     
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_patType1CorrectedPFMet_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$E_{\mathrm{T}}^{\mathrm{miss}}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(5 GeV)'
    histogram_properties.x_limits = [0, 200]
    histogram_properties.ratio_y_limits = [0.5, 1.5]
    if normalise_to_fit:
        histogram_properties.mc_error = get_normalisation_error( normalisations_electron['MET'] )
        histogram_properties.mc_errors_label = 'fit uncertainty'
    else:
        histogram_properties.mc_error = mc_uncertainty
        histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
     
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
    # MET log
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCDConversions' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
      
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    if normalise_to_fit:
        prepare_histograms( histograms, rebin = 4, scale_factor = measurement_config.luminosity_scale, normalisation = normalisations_electron['MET'] )
    else:
        prepare_histograms( histograms, rebin = 4, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_patType1CorrectedPFMet_log_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$E_{\mathrm{T}}^{\mathrm{miss}}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(20 GeV)'
    histogram_properties.x_limits = [200, 700]
    # histogram_properties.y_limits = [0.1, 50]
    if normalise_to_fit:
        histogram_properties.mc_error = get_normalisation_error( normalisations_electron['MET'] )
        histogram_properties.mc_errors_label = 'fit uncertainty'
    else:
        histogram_properties.mc_error = mc_uncertainty
        histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    histogram_properties.set_log_y = True
      
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
      
    # MET phi
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_phi_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCDConversions' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
      
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    if normalise_to_fit:
        prepare_histograms( histograms, rebin = 2, scale_factor = measurement_config.luminosity_scale, normalisation = normalisations_electron['MET'] )
    else:
        prepare_histograms( histograms, rebin = 2, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_patType1CorrectedPFMet_phi_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\phi\left(E_{\mathrm{T}}^{\mathrm{miss}}\\right)$'
    histogram_properties.y_axis_title = 'Events/(0.2)'
    histogram_properties.x_limits = [-3.3, 3.3]
    # histogram_properties.y_limits = [0, 850]
    if normalise_to_fit:
        histogram_properties.mc_error = get_normalisation_error( normalisations_electron['MET'] )
        histogram_properties.mc_errors_label = 'fit uncertainty'
    else:
        histogram_properties.mc_error = mc_uncertainty
        histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    histogram_properties.legend_columns = 2
    # histogram_properties.legend_location = 'upper center'
      
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
  
    # HT
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/HT_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCDConversions' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
      
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    if normalise_to_fit:
        prepare_histograms( histograms, rebin = 4, scale_factor = measurement_config.luminosity_scale, normalisation = normalisations_electron['HT'] )
    else:
        prepare_histograms( histograms, rebin = 4, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_HT_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$H_\mathrm{T}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(20 GeV)'
    histogram_properties.x_limits = [100, 1000]
    histogram_properties.ratio_y_limits = [0.5, 1.5]
    if normalise_to_fit:
        histogram_properties.mc_error = get_normalisation_error( normalisations_electron['HT'] )
        histogram_properties.mc_errors_label = 'fit uncertainty'
    else:
        histogram_properties.mc_error = mc_uncertainty
        histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
  
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
  
    # ST
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/ST_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCDConversions' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
      
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    if normalise_to_fit:
        prepare_histograms( histograms, rebin = 4, scale_factor = measurement_config.luminosity_scale, normalisation = normalisations_electron['ST'] )
    else:
        prepare_histograms( histograms, rebin = 4, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_patType1CorrectedPFMet_ST_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$S_\mathrm{T}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(20 GeV)'
    histogram_properties.x_limits = [150, 1200]
    histogram_properties.ratio_y_limits = [0.5, 1.5]
    if normalise_to_fit:
        histogram_properties.mc_error = get_normalisation_error( normalisations_electron['ST'] )
        histogram_properties.mc_errors_label = 'fit uncertainty'
    else:
        histogram_properties.mc_error = mc_uncertainty
        histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
  
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
  
  
    # WPT
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/WPT_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCDConversions' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
      
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    if normalise_to_fit:
        prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale, normalisation = normalisations_electron['WPT'] )
    else:
        prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_patType1CorrectedPFMet_WPT_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$p^\mathrm{W}_\mathrm{T}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(10 GeV)'
    histogram_properties.x_limits = [0, 500]
    histogram_properties.ratio_y_limits = [0.5, 1.5]
    if normalise_to_fit:
        histogram_properties.mc_error = get_normalisation_error( normalisations_electron['WPT'] )
        histogram_properties.mc_errors_label = 'fit uncertainty'
    else:
        histogram_properties.mc_error = mc_uncertainty
        histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
  
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
      
      
    # MT
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/Transverse_Mass_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCDConversions' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
      
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    if normalise_to_fit:
        prepare_histograms( histograms, rebin = 5, scale_factor = measurement_config.luminosity_scale, normalisation = normalisations_electron['MT'] )
    else:
        prepare_histograms( histograms, rebin = 5, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_patType1CorrectedPFMet_MT_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$M^\mathrm{W}_\mathrm{T}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(5 GeV)'
    histogram_properties.x_limits = [0, 200]
    histogram_properties.ratio_y_limits = [0.5, 1.5]
    if normalise_to_fit:
        histogram_properties.mc_error = get_normalisation_error( normalisations_electron['MT'] )
        histogram_properties.mc_errors_label = 'fit uncertainty'
    else:
        histogram_properties.mc_error = mc_uncertainty
        histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
      
    # M3
    b_tag_bin = ''
    control_region = 'DiffVariablesAnalyser/EPlusJets/M3'
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
      
    histograms_to_draw = [histograms['data'][control_region], histograms['QCD'][control_region],
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_M3' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = e_title
    histogram_properties.x_axis_title = '$M3$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(9 GeV)'
    histogram_properties.x_limits = [100, 600]
    histogram_properties.mc_error = mc_uncertainty
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
  
    # bjet invariant mass
    b_tag_bin = '4orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/bjet_invariant_mass_' + b_tag_bin
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    qcd_predicted_mc = histograms['QCD'][control_region]
      
    histograms_to_draw = [histograms['data'][control_region], qcd_predicted_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_BJets_invmass_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$M_{\mathrm{b}\\bar{\mathrm{b}}}$'
    histogram_properties.y_axis_title = 'Normalised events/(10 GeV)'
    histogram_properties.x_limits = [0, 800]
    histogram_properties.mc_error = mc_uncertainty
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
  
    # b-tag multiplicity
    b_tag_bin = ''
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/N_BJets'
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
      
    n_qcd_predicted_mc = histograms['QCD'][control_region]
      
    histograms_to_draw = [histograms['data'][control_region], n_qcd_predicted_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_N_BJets' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = e_title
    histogram_properties.x_axis_title = 'B-tag multiplicity'
    histogram_properties.y_axis_title = 'Events'
    histogram_properties.x_limits = [-0.5, 5.5]
    histogram_properties.mc_error = mc_uncertainty
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder )
      
    b_tag_bin = ''
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/N_BJets_reweighted'
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
      
    n_qcd_predicted_mc = histograms['QCD'][control_region]
      
    histograms_to_draw = [histograms['data'][control_region], n_qcd_predicted_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_N_BJets_reweighted' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = e_title
    histogram_properties.x_axis_title = 'B-tag multiplicity'
    histogram_properties.y_axis_title = 'Events'
    histogram_properties.x_limits = [-0.5, 5.5]
    histogram_properties.mc_error = mc_uncertainty
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder )
  
    # Jet multiplicity
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Jets/N_Jets_' + b_tag_bin
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
      
    qcd_predicted_mc = histograms['QCD'][control_region]
      
    histograms_to_draw = [histograms['data'][control_region], qcd_predicted_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_N_Jets_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex['0orMoreBtag']
    histogram_properties.x_axis_title = 'Jet multiplicity'
    histogram_properties.y_axis_title = 'Events'
    histogram_properties.x_limits = [3.5, 9.5]
    histogram_properties.mc_error = mc_uncertainty
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder )
  
    if make_additional_QCD_plots:
        # QCD control regions (electron |eta|), MET bins
        for variable_bin in variable_bins_ROOT['MET']:
            b_tag_bin = '0btag'
            control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_MET_Analysis/patType1CorrectedPFMet_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            control_region = control_region.replace( 'Ref selection', 'QCDConversions' )
            qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
              
            histograms = get_histograms_from_files( [control_region], histogram_files )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
              
            qcd_from_mc = histograms['QCD'][control_region].Clone()
              
            histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                                  histograms['V+Jets'][control_region],
                                  histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
            histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
              
            histogram_properties = Histogram_properties()
            histogram_properties.name = 'QCD_conversion_control_region_electron_AbsEta_MET_bin_' + variable_bin + '_' + b_tag_bin
            histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
            histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
            histogram_properties.y_axis_title = 'Events/(0.1)'
            histogram_properties.x_limits = [0, 2.6]
            histogram_properties.mc_error = 0.0
            histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
            histogram_properties.legend_location = 'upper right'
              
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = output_folder )
  
        # QCD control regions (electron |eta|), ST bins
        for variable_bin in variable_bins_ROOT['ST']:
            b_tag_bin = '0btag'
            control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_ST_Analysis/ST_with_patType1CorrectedPFMet_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            control_region = control_region.replace( 'Ref selection', 'QCDConversions' )
            qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
              
            histograms = get_histograms_from_files( [control_region], histogram_files )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
              
            qcd_from_mc = histograms['QCD'][control_region].Clone()
              
            histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                                  histograms['V+Jets'][control_region],
                                  histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
            histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
              
            histogram_properties = Histogram_properties()
            histogram_properties.name = 'QCD_conversion_control_region_electron_AbsEta_ST_bin_' + variable_bin + '_' + b_tag_bin
            histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
            histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
            histogram_properties.y_axis_title = 'Events/(0.1)'
            histogram_properties.x_limits = [0, 2.6]
            histogram_properties.mc_error = 0.0
            histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
            histogram_properties.legend_location = 'upper right'
              
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = output_folder )
  
        # QCD control regions (electron |eta|), HT bins
        for variable_bin in variable_bins_ROOT['HT']:
            b_tag_bin = '0btag'
            control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_HT_Analysis/HT_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            control_region = control_region.replace( 'Ref selection', 'QCDConversions' )
            qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
              
            histograms = get_histograms_from_files( [control_region], histogram_files )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
              
            qcd_from_mc = histograms['QCD'][control_region].Clone()
              
            histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                                  histograms['V+Jets'][control_region],
                                  histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
            histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
              
            histogram_properties = Histogram_properties()
            histogram_properties.name = 'QCD_conversion_control_region_electron_AbsEta_HT_bin_' + variable_bin + '_' + b_tag_bin
            histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
            histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
            histogram_properties.y_axis_title = 'Events/(0.1)'
            histogram_properties.x_limits = [0, 2.6]
            histogram_properties.mc_error = 0.0
            histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
            histogram_properties.legend_location = 'upper right'
              
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = output_folder )
  
        # QCD control regions (electron |eta|), MT bins
        for variable_bin in variable_bins_ROOT['MT']:
            b_tag_bin = '0btag'
            control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_MT_Analysis/MT_with_patType1CorrectedPFMet_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            control_region = control_region.replace( 'Ref selection', 'QCDConversions' )
            qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
              
            histograms = get_histograms_from_files( [control_region], histogram_files )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
              
            qcd_from_mc = histograms['QCD'][control_region].Clone()
              
            histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                                  histograms['V+Jets'][control_region],
                                  histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
            histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
              
            histogram_properties = Histogram_properties()
            histogram_properties.name = 'QCD_conversion_control_region_electron_AbsEta_MT_bin_' + variable_bin + '_' + b_tag_bin
            histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
            histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
            histogram_properties.y_axis_title = 'Events/(0.1)'
            histogram_properties.x_limits = [0, 2.6]
            histogram_properties.mc_error = 0.0
            histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
            histogram_properties.legend_location = 'upper right'
              
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = output_folder )
  
        # QCD control regions (electron |eta|), WPT bins
        for variable_bin in variable_bins_ROOT['WPT']:
            b_tag_bin = '0btag'
            control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_WPT_Analysis/WPT_with_patType1CorrectedPFMet_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            control_region = control_region.replace( 'Ref selection', 'QCDConversions' )
            qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
              
            histograms = get_histograms_from_files( [control_region], histogram_files )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
              
            qcd_from_mc = histograms['QCD'][control_region].Clone()
              
            histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                                  histograms['V+Jets'][control_region],
                                  histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
            histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
              
            histogram_properties = Histogram_properties()
            histogram_properties.name = 'QCD_conversion_control_region_electron_AbsEta_WPT_bin_' + variable_bin + '_' + b_tag_bin
            histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
            histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
            histogram_properties.y_axis_title = 'Events/(0.1)'
            histogram_properties.x_limits = [0, 2.6]
            histogram_properties.mc_error = 0.0
            histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
            histogram_properties.legend_location = 'upper right'
              
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = output_folder )
  
        # QCD non-iso control regions (electron |eta|), MET bins
        for variable_bin in variable_bins_ROOT['MET']:
            b_tag_bin = '0btag'
            control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_MET_Analysis/patType1CorrectedPFMet_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            control_region = control_region.replace( 'Ref selection', 'QCD non iso e+jets' )
            qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
              
            histograms = get_histograms_from_files( [control_region], histogram_files )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
              
            qcd_from_mc = histograms['QCD'][control_region].Clone()
              
            histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                                  histograms['V+Jets'][control_region],
                                  histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
            histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
              
            histogram_properties = Histogram_properties()
            histogram_properties.name = 'QCD_non_iso_control_region_electron_AbsEta_MET_bin_' + variable_bin + '_' + b_tag_bin
            histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
            histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
            histogram_properties.y_axis_title = 'Events/(0.1)'
            histogram_properties.x_limits = [0, 2.6]
            histogram_properties.mc_error = 0.0
            histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
            histogram_properties.legend_location = 'upper right'
              
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = output_folder )
  
        # QCD control regions (electron |eta|), ST bins
        for variable_bin in variable_bins_ROOT['ST']:
            b_tag_bin = '0btag'
            control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_ST_Analysis/ST_with_patType1CorrectedPFMet_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            control_region = control_region.replace( 'Ref selection', 'QCD non iso e+jets' )
            qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
              
            histograms = get_histograms_from_files( [control_region], histogram_files )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
              
            qcd_from_mc = histograms['QCD'][control_region].Clone()
              
            histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                                  histograms['V+Jets'][control_region],
                                  histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
            histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
              
            histogram_properties = Histogram_properties()
            histogram_properties.name = 'QCD_non_iso_control_region_electron_AbsEta_ST_bin_' + variable_bin + '_' + b_tag_bin
            histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
            histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
            histogram_properties.y_axis_title = 'Events/(0.1)'
            histogram_properties.x_limits = [0, 2.6]
            histogram_properties.mc_error = 0.0
            histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
            histogram_properties.legend_location = 'upper right'
              
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = output_folder )
  
        # QCD control regions (electron |eta|), HT bins
        for variable_bin in variable_bins_ROOT['HT']:
            b_tag_bin = '0btag'
            control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_HT_Analysis/HT_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            control_region = control_region.replace( 'Ref selection', 'QCD non iso e+jets' )
            qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
              
            histograms = get_histograms_from_files( [control_region], histogram_files )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
              
            qcd_from_mc = histograms['QCD'][control_region].Clone()
              
            histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                                  histograms['V+Jets'][control_region],
                                  histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
            histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
              
            histogram_properties = Histogram_properties()
            histogram_properties.name = 'QCD_non_iso_control_region_electron_AbsEta_HT_bin_' + variable_bin + '_' + b_tag_bin
            histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
            histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
            histogram_properties.y_axis_title = 'Events/(0.1)'
            histogram_properties.x_limits = [0, 2.6]
            histogram_properties.mc_error = 0.0
            histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
            histogram_properties.legend_location = 'upper right'
              
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = output_folder )
  
        # QCD control regions (electron |eta|), MT bins
        for variable_bin in variable_bins_ROOT['MT']:
            b_tag_bin = '0btag'
            control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_MT_Analysis/MT_with_patType1CorrectedPFMet_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            control_region = control_region.replace( 'Ref selection', 'QCD non iso e+jets' )
            qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
              
            histograms = get_histograms_from_files( [control_region], histogram_files )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
              
            qcd_from_mc = histograms['QCD'][control_region].Clone()
              
            histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                                  histograms['V+Jets'][control_region],
                                  histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
            histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
              
            histogram_properties = Histogram_properties()
            histogram_properties.name = 'QCD_non_iso_control_region_electron_AbsEta_MT_bin_' + variable_bin + '_' + b_tag_bin
            histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
            histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
            histogram_properties.y_axis_title = 'Events/(0.1)'
            histogram_properties.x_limits = [0, 2.6]
            histogram_properties.mc_error = 0.0
            histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
            histogram_properties.legend_location = 'upper right'
              
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = output_folder )
  
        # QCD control regions (electron |eta|), WPT bins
        for variable_bin in variable_bins_ROOT['WPT']:
            b_tag_bin = '0btag'
            control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_WPT_Analysis/WPT_with_patType1CorrectedPFMet_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            control_region = control_region.replace( 'Ref selection', 'QCD non iso e+jets' )
            qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
              
            histograms = get_histograms_from_files( [control_region], histogram_files )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
              
            qcd_from_mc = histograms['QCD'][control_region].Clone()
              
            histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                                  histograms['V+Jets'][control_region],
                                  histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
            histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
              
            histogram_properties = Histogram_properties()
            histogram_properties.name = 'QCD_non_iso_control_region_electron_AbsEta_WPT_bin_' + variable_bin + '_' + b_tag_bin
            histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
            histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
            histogram_properties.y_axis_title = 'Events/(0.1)'
            histogram_properties.x_limits = [0, 2.6]
            histogram_properties.mc_error = 0.0
            histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
            histogram_properties.legend_location = 'upper right'
              
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = output_folder )
  
    # QCD PFReliso (rho-corrected) for non-isolated region
    b_tag_bin = '0btag'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Electron/electron_rhoCorrectedIso_03_' + b_tag_bin
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['QCD'][control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'QCD_electron_rhoCorrectedIso_non_iso_control_region_' + b_tag_bin
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = 'PF reliso($e$)'
    histogram_properties.y_axis_title = 'Events/(0.1)'
    histogram_properties.x_limits = [0, 3]
    histogram_properties.y_limits = [1, 10000000]
    histogram_properties.mc_error = 0.0
    histogram_properties.mc_errors_label = 'MC unc.'
    histogram_properties.legend_location = 'upper right'
    histogram_properties.set_log_y = True
      
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_stat_errors_on_mc = True )
  
    # QCD PFReliso (rho-corrected) without iso cut
    b_tag_bin = '0btag'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/QCD e+jets PFRelIso/Electron/electron_rhoCorrectedIso_03_' + b_tag_bin
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['QCD'][control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'QCD_electron_rhoCorrectedIso_' + b_tag_bin
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = 'PF reliso($e$)'
    histogram_properties.y_axis_title = 'Events/(0.1)'
    histogram_properties.x_limits = [0, 3]
    histogram_properties.y_limits = [1, 10000000]
    histogram_properties.mc_error = 0.0
    histogram_properties.mc_errors_label = 'MC unc.'
    histogram_properties.legend_location = 'upper right'
    histogram_properties.set_log_y = True
      
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_stat_errors_on_mc = True, draw_vertical_line = 0.2 )
  
    # QCD control regions (electron |eta|)
    # conversion control region
    b_tag_bin = '0btag'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Electron/electron_AbsEta_' + b_tag_bin
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['QCD'][control_region].Clone()
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'QCD_conversion_control_region_electron_AbsEta_' + b_tag_bin
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
    histogram_properties.y_axis_title = 'Events/(0.1)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.y_limits = [0, 7000]
    histogram_properties.mc_error = 0.0
    histogram_properties.mc_errors_label = 'MC unc.'
    histogram_properties.legend_location = 'upper left'
      
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_stat_errors_on_mc = True )
      
    # non-iso control region
    b_tag_bin = '0btag'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Electron/electron_AbsEta_' + b_tag_bin
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['QCD'][control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'QCD_non_iso_control_region_electron_AbsEta_' + b_tag_bin
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
    histogram_properties.y_axis_title = 'Events/(0.1)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.mc_error = 0.0
    histogram_properties.mc_errors_label = 'MC unc.'
    histogram_properties.legend_location = 'upper right'
      
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_stat_errors_on_mc = True )
      
    # QCD shape comparison
    b_tag_bin = '0btag'
    control_region_1 = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Electron/electron_AbsEta_' + b_tag_bin
    control_region_2 = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Electron/electron_AbsEta_' + b_tag_bin
      
    histograms = get_histograms_from_files( [control_region_1, control_region_2], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
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
    make_control_region_comparison( region_1, region_2,
                                   name_region_1 = 'conversions', name_region_2 = 'non-isolated electrons',
                                   histogram_properties = histogram_properties, save_folder = output_folder )
  
    # QCD control regions (electron |eta|), 1 or more btags
    b_tag_bin = '1orMoreBtag'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Electron/electron_AbsEta_' + b_tag_bin
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['QCD'][control_region].Clone()
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'QCD_conversion_control_region_electron_AbsEta_' + b_tag_bin
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
    histogram_properties.y_axis_title = 'Events/(0.1)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.y_limits = [0, 1000]
    histogram_properties.mc_error = 0.0
    histogram_properties.mc_errors_label = 'MC unc.'
    histogram_properties.legend_location = 'upper left'
      
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_stat_errors_on_mc = True )
      
    b_tag_bin = '1orMoreBtag'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Electron/electron_AbsEta_' + b_tag_bin
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['QCD'][control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'QCD_non_iso_control_region_electron_AbsEta_' + b_tag_bin
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
    histogram_properties.y_axis_title = 'Events/(0.1)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.mc_error = 0.0
    histogram_properties.mc_errors_label = 'MC unc.'
    histogram_properties.legend_location = 'upper right'
      
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_stat_errors_on_mc = True )
  
    # QCD conversions btag bin shape comparison
    b_tag_bin_1 = '0btag'
    b_tag_bin_2 = '1orMoreBtag'
    control_region_1 = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Electron/electron_AbsEta_' + b_tag_bin_1
    control_region_2 = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Electron/electron_AbsEta_' + b_tag_bin_2
      
    histograms = get_histograms_from_files( [control_region_1, control_region_2], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    region_1 = histograms['data'][control_region_1].Clone() - histograms['TTJet'][control_region_1].Clone() - histograms['V+Jets'][control_region_1].Clone()
    region_2 = histograms['data'][control_region_2].Clone() - histograms['TTJet'][control_region_2].Clone() - histograms['V+Jets'][control_region_2].Clone()
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'QCD_Conversions_btag_bin_comparison_electron_AbsEta_' + b_tag_bin_1 + '_' + b_tag_bin_2
    histogram_properties.title = e_title + ', conversions, ' + b_tag_bins_latex[b_tag_bin_1] + '/' + b_tag_bins_latex[b_tag_bin_2]
    histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
    histogram_properties.y_axis_title = 'arbitrary units/(0.1)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.y_limits = [0, 0.14]
    histogram_properties.mc_error = 0.0
    histogram_properties.legend_location = 'upper right'
    make_control_region_comparison( region_1, region_2,
                                   name_region_1 = b_tag_bins_latex[b_tag_bin_1], name_region_2 = b_tag_bins_latex[b_tag_bin_2],
                                   histogram_properties = histogram_properties, save_folder = output_folder )
  
    # QCD non-iso btag bin shape comparison
    b_tag_bin_1 = '0btag'
    b_tag_bin_2 = '1orMoreBtag'
    control_region_1 = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Electron/electron_AbsEta_' + b_tag_bin_1
    control_region_2 = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Electron/electron_AbsEta_' + b_tag_bin_2
      
    histograms = get_histograms_from_files( [control_region_1, control_region_2], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    region_1 = histograms['data'][control_region_1].Clone() - histograms['TTJet'][control_region_1].Clone() - histograms['V+Jets'][control_region_1].Clone()
    region_2 = histograms['data'][control_region_2].Clone() - histograms['TTJet'][control_region_2].Clone() - histograms['V+Jets'][control_region_2].Clone()
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'QCD_non_iso_btag_bin_comparison_electron_AbsEta_' + b_tag_bin_1 + '_' + b_tag_bin_2
    histogram_properties.title = e_title + ', non-iso, ' + b_tag_bins_latex[b_tag_bin_1] + '/' + b_tag_bins_latex[b_tag_bin_2]
    histogram_properties.x_axis_title = '$\left|\eta(e)\\right|$'
    histogram_properties.y_axis_title = 'arbitrary units/(0.1)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.y_limits = [0, 0.14]
    histogram_properties.mc_error = 0.0
    histogram_properties.legend_location = 'upper right'
    make_control_region_comparison( region_1, region_2,
                                   name_region_1 = b_tag_bins_latex[b_tag_bin_1], name_region_2 = b_tag_bins_latex[b_tag_bin_2],
                                   histogram_properties = histogram_properties, save_folder = output_folder )
  
    # Number of vertices
    b_tag_bin = ''
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Vertices/nVertex'
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
      
    n_qcd_predicted_mc = histograms['QCD'][control_region]
      
    histograms_to_draw = [histograms['data'][control_region], n_qcd_predicted_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_nVertex' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex['0orMoreBtag']
    histogram_properties.x_axis_title = 'N(PV)'
    histogram_properties.y_axis_title = 'arbitrary units'
    histogram_properties.x_limits = [0, 50]
    histogram_properties.mc_error = 0.0
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, normalise = True )
      
    b_tag_bin = ''
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Vertices/nVertex_reweighted'
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
      
    n_qcd_predicted_mc = histograms['QCD'][control_region]
      
    histograms_to_draw = [histograms['data'][control_region], n_qcd_predicted_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_nVertex_reweighted' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex['0orMoreBtag']
    histogram_properties.x_axis_title = 'N(PV)'
    histogram_properties.y_axis_title = 'arbitrary units'
    histogram_properties.x_limits = [0, 50]
    histogram_properties.mc_error = 0.0
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, normalise = True )
  
    # muons
    data = 'SingleMu'
    histogram_files['data'] = measurement_config.data_file_muon
    histogram_files['QCD'] = measurement_config.muon_QCD_MC_category_templates[category]
  
    mu_title = title_template % ( measurement_config.new_luminosity / 1000., measurement_config.centre_of_mass_energy, '$\mu$+jets, $\geq$ 4 jets' )
      
    # Muon |eta|
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Muon/muon_AbsEta_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCD non iso mu+jets' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
      
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral() * 1.2
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'muon_AbsEta_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(\mu)\\right|$'
    histogram_properties.y_axis_title = 'Events/(0.1)'
    histogram_properties.x_limits = [0, 2.6]
    histogram_properties.mc_error = mc_uncertainty
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
      
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
  
    # Muon pt
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Muon/muon_pT_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCD non iso mu+jets' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
      
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral() * 1.2
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'muon_pT_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$p_\mathrm{T}(\mu)$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(10 GeV)'
    histogram_properties.x_limits = [0, 250]
    histogram_properties.mc_error = mc_uncertainty
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
      
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
  
    # MET
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCD non iso mu+jets' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
      
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    if normalise_to_fit:
        prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale, normalisation = normalisations_muon['MET'] )
    else:
        prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral() * 1.2
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_patType1CorrectedPFMet_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$E_{\mathrm{T}}^{\mathrm{miss}}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(5 GeV)'
    histogram_properties.x_limits = [0, 200]
    histogram_properties.ratio_y_limits = [0.5, 1.5]
    if normalise_to_fit:
        histogram_properties.mc_error = get_normalisation_error( normalisations_muon['MET'] )
        histogram_properties.mc_errors_label = 'fit uncertainty'
    else:
        histogram_properties.mc_error = mc_uncertainty
        histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
      
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
  
    # MET log
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCD non iso mu+jets' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
      
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    if normalise_to_fit:
        prepare_histograms( histograms, rebin = 4, scale_factor = measurement_config.luminosity_scale, normalisation = normalisations_muon['MET'] )
    else:
        prepare_histograms( histograms, rebin = 4, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_patType1CorrectedPFMet_log_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$E_{\mathrm{T}}^{\mathrm{miss}}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(20 GeV)'
    histogram_properties.x_limits = [200, 700]
    # histogram_properties.y_limits = [0.1, 50]
    if normalise_to_fit:
        histogram_properties.mc_error = get_normalisation_error( normalisations_muon['MET'] )
        histogram_properties.mc_errors_label = 'fit uncertainty'
    else:
        histogram_properties.mc_error = mc_uncertainty
        histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    histogram_properties.set_log_y = True
      
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
      
    # MET phi
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_phi_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCD non iso mu+jets' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
      
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    if normalise_to_fit:
        prepare_histograms( histograms, rebin = 2, scale_factor = measurement_config.luminosity_scale, normalisation = normalisations_muon['MET'] )
    else:
        prepare_histograms( histograms, rebin = 2, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_patType1CorrectedPFMet_phi_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\phi\left(E_{\mathrm{T}}^{\mathrm{miss}}\\right)$'
    histogram_properties.y_axis_title = 'Events/(0.2)'
    histogram_properties.x_limits = [-3.3, 3.3]
    # histogram_properties.y_limits = [0, 850]
    if normalise_to_fit:
        histogram_properties.mc_error = get_normalisation_error( normalisations_muon['MET'] )
        histogram_properties.mc_errors_label = 'fit uncertainty'
    else:
        histogram_properties.mc_error = mc_uncertainty
        histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    histogram_properties.legend_columns = 2
    # histogram_properties.legend_location = 'upper center'
      
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
  
    # HT
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/HT_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCD non iso mu+jets' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
      
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    if normalise_to_fit:
        prepare_histograms( histograms, rebin = 4, scale_factor = measurement_config.luminosity_scale, normalisation = normalisations_muon['HT'] )
    else:
        prepare_histograms( histograms, rebin = 4, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_HT_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$H_\mathrm{T}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(20 GeV)'
    histogram_properties.x_limits = [100, 1000]
    histogram_properties.ratio_y_limits = [0.5, 1.5]
    if normalise_to_fit:
        histogram_properties.mc_error = get_normalisation_error( normalisations_muon['HT'] )
        histogram_properties.mc_errors_label = 'fit uncertainty'
    else:
        histogram_properties.mc_error = mc_uncertainty
        histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
  
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
  
    # ST
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/ST_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCD non iso mu+jets' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
      
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    if normalise_to_fit:
        prepare_histograms( histograms, rebin = 4, scale_factor = measurement_config.luminosity_scale, normalisation = normalisations_muon['ST'] )
    else:
        prepare_histograms( histograms, rebin = 4, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_patType1CorrectedPFMet_ST_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$S_\mathrm{T}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(20 GeV)'
    histogram_properties.x_limits = [150, 1200]
    histogram_properties.ratio_y_limits = [0.5, 1.5]
    if normalise_to_fit:
        histogram_properties.mc_error = get_normalisation_error( normalisations_muon['ST'] )
        histogram_properties.mc_errors_label = 'fit uncertainty'
    else:
        histogram_properties.mc_error = mc_uncertainty
        histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
  
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
  
  
    # WPT
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/WPT_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCD non iso mu+jets' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
      
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    if normalise_to_fit:
        prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale, normalisation = normalisations_muon['WPT'] )
    else:
        prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
      
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_patType1CorrectedPFMet_WPT_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$p^\mathrm{W}_\mathrm{T}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(10 GeV)'
    histogram_properties.x_limits = [0, 500]
    histogram_properties.ratio_y_limits = [0.5, 1.5]
    if normalise_to_fit:
        histogram_properties.mc_error = get_normalisation_error( normalisations_muon['WPT'] )
        histogram_properties.mc_errors_label = 'fit uncertainty'
    else:
        histogram_properties.mc_error = mc_uncertainty
        histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
   
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
     
    # MT
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/Transverse_Mass_' + b_tag_bin
    qcd_control_region = control_region.replace( 'Ref selection', 'QCD non iso mu+jets' )
    qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
     
    histograms = get_histograms_from_files( [control_region, qcd_control_region], histogram_files )
    if normalise_to_fit:
        prepare_histograms( histograms, rebin = 5, scale_factor = measurement_config.luminosity_scale, normalisation = normalisations_muon['MT'] )
    else:
        prepare_histograms( histograms, rebin = 5, scale_factor = measurement_config.luminosity_scale )
     
    qcd_from_data = histograms['data'][qcd_control_region].Clone()
    n_qcd_predicted_mc = histograms['QCD'][control_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
     
    histograms_to_draw = [histograms['data'][control_region], qcd_from_data,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
     
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_patType1CorrectedPFMet_MT_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$M^\mathrm{W}_\mathrm{T}$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(5 GeV)'
    histogram_properties.x_limits = [0, 200]
    histogram_properties.ratio_y_limits = [0.5, 1.5]
    if normalise_to_fit:
        histogram_properties.mc_error = get_normalisation_error( normalisations_muon['MT'] )
        histogram_properties.mc_errors_label = 'fit uncertainty'
    else:
        histogram_properties.mc_error = mc_uncertainty
        histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
     
    # M3
    b_tag_bin = ''
    control_region = 'DiffVariablesAnalyser/MuPlusJets/M3'
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
      
    histograms_to_draw = [histograms['data'][control_region], histograms['QCD'][control_region],
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_M3'
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title
    histogram_properties.x_axis_title = '$M3$ [GeV]'
    histogram_properties.y_axis_title = 'Events/(9 GeV)'
    histogram_properties.x_limits = [100, 600]
    histogram_properties.mc_error = mc_uncertainty
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
      
    # Jet multiplicity
    b_tag_bin = '2orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Jets/N_Jets_' + b_tag_bin
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
      
    qcd_predicted_mc = histograms['QCD'][control_region]
      
    histograms_to_draw = [histograms['data'][control_region], qcd_predicted_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_N_Jets_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex['0orMoreBtag']
    histogram_properties.x_axis_title = 'Jet multiplicity'
    histogram_properties.y_axis_title = 'Events'
    histogram_properties.x_limits = [3.5, 9.5]
    histogram_properties.mc_error = mc_uncertainty
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder )
  
    # bjet invariant mass
    b_tag_bin = '4orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/bjet_invariant_mass_' + b_tag_bin
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    qcd_predicted_mc = histograms['QCD'][control_region]
      
    histograms_to_draw = [histograms['data'][control_region], qcd_predicted_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_BJets_invmass_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$M_{\mathrm{b}\\bar{\mathrm{b}}}$'
    histogram_properties.y_axis_title = 'Normalised events/(10 GeV)'
    histogram_properties.x_limits = [0, 800]
    histogram_properties.mc_error = mc_uncertainty
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False )
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True )
  
    # b-tag multiplicity
    b_tag_bin = ''
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/N_BJets'
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
      
    n_qcd_predicted_mc = histograms['QCD'][control_region]
      
    histograms_to_draw = [histograms['data'][control_region], n_qcd_predicted_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_N_BJets' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title
    histogram_properties.x_axis_title = 'B-tag multiplicity'
    histogram_properties.y_axis_title = 'Events'
    histogram_properties.x_limits = [-0.5, 5.5]
    histogram_properties.mc_error = mc_uncertainty
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder )
      
    b_tag_bin = ''
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/N_BJets_reweighted'
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
      
    n_qcd_predicted_mc = histograms['QCD'][control_region]
      
    histograms_to_draw = [histograms['data'][control_region], n_qcd_predicted_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_N_BJets_reweighted' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title
    histogram_properties.x_axis_title = 'B-tag multiplicity'
    histogram_properties.y_axis_title = 'Events'
    histogram_properties.x_limits = [-0.5, 5.5]
    histogram_properties.mc_error = mc_uncertainty
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder )
      
    # Number of vertices
    b_tag_bin = ''
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Vertices/nVertex'
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
      
    n_qcd_predicted_mc = histograms['QCD'][control_region]
      
    histograms_to_draw = [histograms['data'][control_region], n_qcd_predicted_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_nVertex' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex['0orMoreBtag']
    histogram_properties.x_axis_title = 'N(PV)'
    histogram_properties.y_axis_title = 'arbitrary units'
    histogram_properties.x_limits = [0, 50]
    histogram_properties.mc_error = 0.0
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, normalise = True )
      
    b_tag_bin = ''
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Vertices/nVertex_reweighted'
      
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
      
    n_qcd_predicted_mc = histograms['QCD'][control_region]
      
    histograms_to_draw = [histograms['data'][control_region], n_qcd_predicted_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_nVertex_reweighted' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex['0orMoreBtag']
    histogram_properties.x_axis_title = 'N(PV)'
    histogram_properties.y_axis_title = 'arbitrary units'
    histogram_properties.x_limits = [0, 50]
    histogram_properties.mc_error = 0.0
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, normalise = True )
  
    if make_additional_QCD_plots:
        # QCD non-iso control regions (muon |eta|), MET bins
        for variable_bin in variable_bins_ROOT['MET']:
            b_tag_bin = '0btag'
            control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Binned_MET_Analysis/patType1CorrectedPFMet_bin_' + variable_bin + '/muon_absolute_eta_' + b_tag_bin
            control_region = control_region.replace( 'Ref selection', 'QCD non iso mu+jets ge3j' )
            qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
              
            histograms = get_histograms_from_files( [control_region], histogram_files )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
              
            qcd_from_mc = histograms['QCD'][control_region].Clone()
              
            histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                                  histograms['V+Jets'][control_region],
                                  histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
            histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
              
            histogram_properties = Histogram_properties()
            histogram_properties.name = 'QCD_non_iso_control_region_muon_AbsEta_MET_bin_' + variable_bin + '_' + b_tag_bin
            histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
            histogram_properties.x_axis_title = '$\left|\eta(\mu)\\right|$'
            histogram_properties.y_axis_title = 'Events/(0.1)'
            histogram_properties.x_limits = [0, 2.6]
            histogram_properties.mc_error = 0.0
            histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
            histogram_properties.legend_location = 'upper right'
              
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = output_folder, show_ratio = False )
            histogram_properties.name += '_with_ratio'
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = output_folder, show_ratio = True )
  
        # QCD control regions (muon |eta|), ST bins
        for variable_bin in variable_bins_ROOT['ST']:
            b_tag_bin = '0btag'
            control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Binned_ST_Analysis/ST_with_patType1CorrectedPFMet_bin_' + variable_bin + '/muon_absolute_eta_' + b_tag_bin
            control_region = control_region.replace( 'Ref selection', 'QCD non iso mu+jets ge3j' )
            qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
              
            histograms = get_histograms_from_files( [control_region], histogram_files )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
              
            qcd_from_mc = histograms['QCD'][control_region].Clone()
              
            histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                                  histograms['V+Jets'][control_region],
                                  histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
            histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
              
            histogram_properties = Histogram_properties()
            histogram_properties.name = 'QCD_non_iso_control_region_muon_AbsEta_ST_bin_' + variable_bin + '_' + b_tag_bin
            histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
            histogram_properties.x_axis_title = '$\left|\eta(\mu)\\right|$'
            histogram_properties.y_axis_title = 'Events/(0.1)'
            histogram_properties.x_limits = [0, 2.6]
            histogram_properties.mc_error = 0.0
            histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
            histogram_properties.legend_location = 'upper right'
              
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = output_folder )
  
        # QCD control regions (muon |eta|), HT bins
        for variable_bin in variable_bins_ROOT['HT']:
            b_tag_bin = '0btag'
            control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Binned_HT_Analysis/HT_bin_' + variable_bin + '/muon_absolute_eta_' + b_tag_bin
            control_region = control_region.replace( 'Ref selection', 'QCD non iso mu+jets ge3j' )
            qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
              
            histograms = get_histograms_from_files( [control_region], histogram_files )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
              
            qcd_from_mc = histograms['QCD'][control_region].Clone()
              
            histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                                  histograms['V+Jets'][control_region],
                                  histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
            histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
              
            histogram_properties = Histogram_properties()
            histogram_properties.name = 'QCD_non_iso_control_region_muon_AbsEta_HT_bin_' + variable_bin + '_' + b_tag_bin
            histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
            histogram_properties.x_axis_title = '$\left|\eta(\mu)\\right|$'
            histogram_properties.y_axis_title = 'Events/(0.1)'
            histogram_properties.x_limits = [0, 2.6]
            histogram_properties.mc_error = 0.0
            histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
            histogram_properties.legend_location = 'upper right'
              
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = output_folder )
  
        # QCD control regions (muon |eta|), MT bins
        for variable_bin in variable_bins_ROOT['MT']:
            b_tag_bin = '0btag'
            control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Binned_MT_Analysis/MT_with_patType1CorrectedPFMet_bin_' + variable_bin + '/muon_absolute_eta_' + b_tag_bin
            control_region = control_region.replace( 'Ref selection', 'QCD non iso mu+jets ge3j' )
            qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
              
            histograms = get_histograms_from_files( [control_region], histogram_files )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
              
            qcd_from_mc = histograms['QCD'][control_region].Clone()
              
            histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                                  histograms['V+Jets'][control_region],
                                  histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
            histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
              
            histogram_properties = Histogram_properties()
            histogram_properties.name = 'QCD_non_iso_control_region_muon_AbsEta_MT_bin_' + variable_bin + '_' + b_tag_bin
            histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
            histogram_properties.x_axis_title = '$\left|\eta(\mu)\\right|$'
            histogram_properties.y_axis_title = 'Events/(0.1)'
            histogram_properties.x_limits = [0, 2.6]
            histogram_properties.mc_error = 0.0
            histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
            histogram_properties.legend_location = 'upper right'
              
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = output_folder )
  
        # QCD control regions (muon |eta|), WPT bins
        for variable_bin in variable_bins_ROOT['WPT']:
            b_tag_bin = '0btag'
            control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Binned_WPT_Analysis/WPT_with_patType1CorrectedPFMet_bin_' + variable_bin + '/muon_absolute_eta_' + b_tag_bin
            control_region = control_region.replace( 'Ref selection', 'QCD non iso mu+jets ge3j' )
            qcd_control_region = control_region.replace( b_tag_bin, '0btag' )
              
            histograms = get_histograms_from_files( [control_region], histogram_files )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
              
            qcd_from_mc = histograms['QCD'][control_region].Clone()
              
            histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                                  histograms['V+Jets'][control_region],
                                  histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
            histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
              
            histogram_properties = Histogram_properties()
            histogram_properties.name = 'QCD_non_iso_control_region_muon_AbsEta_WPT_bin_' + variable_bin + '_' + b_tag_bin
            histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
            histogram_properties.x_axis_title = '$\left|\eta(\mu)\\right|$'
            histogram_properties.y_axis_title = 'Events/(0.1)'
            histogram_properties.x_limits = [0, 2.6]
            histogram_properties.mc_error = 0.0
            histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
            histogram_properties.legend_location = 'upper right'
              
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = output_folder )
  
      
    # QCD muon |eta| in ge3jet, 0btag bin
    b_tag_bin = '0btag'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Muon/muon_AbsEta_' + b_tag_bin
  
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
  
    qcd_from_mc = histograms['QCD'][control_region].Clone()
  
    histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
  
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'QCD_non_iso_control_region_muon_AbsEta_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title.replace( '4 jets', '3 jets' ) + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$\left|\eta(\mu)\\right|$'
    histogram_properties.y_axis_title = 'Events/(0.1)'
    histogram_properties.x_limits = [0, 2.5]
    histogram_properties.mc_error = 0.0
    histogram_properties.mc_errors_label = 'MC unc.'
    histogram_properties.legend_location = 'upper right'
  
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_stat_errors_on_mc = True )
  
    # QCD muon pfReliso for non-iso region in ge3jet, 0btag bin
    b_tag_bin = '0btag'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Muon/muon_pfIsolation_04_' + b_tag_bin
  
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
  
    qcd_from_mc = histograms['QCD'][control_region].Clone()
  
    histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
  
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'QCD_muon_pfIsolation_non_iso_control_region_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title.replace( '4 jets', '3 jets' ) + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = 'PF reliso($\mu$)'
    histogram_properties.y_axis_title = 'Events/(0.1)'
    histogram_properties.x_limits = [0, 3.5]
    histogram_properties.y_limits = [1, 10000000]
    histogram_properties.mc_error = 0.0
    histogram_properties.mc_errors_label = 'MC unc.'
    histogram_properties.legend_location = 'upper right'
    histogram_properties.set_log_y = True
  
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_stat_errors_on_mc = True )
  
    # QCD muon pfReliso without iso cut in ge3jet, 0btag bin
    b_tag_bin = '0btag'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/QCD mu+jets PFRelIso ge3j/Muon/muon_pfIsolation_04_' + b_tag_bin
  
    histograms = get_histograms_from_files( [control_region], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
  
    qcd_from_mc = histograms['QCD'][control_region].Clone()
  
    histograms_to_draw = [histograms['data'][control_region], qcd_from_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
  
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'QCD_muon_pfIsolation_' + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title.replace( '4 jets', '3 jets' ) + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = 'PF reliso($\mu$)'
    histogram_properties.y_axis_title = 'Events/(0.1)'
    histogram_properties.x_limits = [0, 3.5]
    histogram_properties.y_limits = [1, 10000000]
    histogram_properties.mc_error = 0.0
    histogram_properties.mc_errors_label = 'MC unc.'
    histogram_properties.legend_location = 'upper right'
    histogram_properties.set_log_y = True
  
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_stat_errors_on_mc = True, draw_vertical_line = 0.3 )
      
    # QCD non-iso btag bin shape comparison
    b_tag_bin_1 = '0btag'
    b_tag_bin_2 = '1orMoreBtag'
    control_region_1 = 'TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Muon/muon_AbsEta_' + b_tag_bin_1
    control_region_2 = 'TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Muon/muon_AbsEta_' + b_tag_bin_2
      
    histograms = get_histograms_from_files( [control_region_1, control_region_2], histogram_files )
    prepare_histograms( histograms, rebin = 10, scale_factor = measurement_config.luminosity_scale )
      
    region_1 = histograms['data'][control_region_1].Clone() - histograms['TTJet'][control_region_1].Clone() - histograms['V+Jets'][control_region_1].Clone()
    region_2 = histograms['data'][control_region_2].Clone() - histograms['TTJet'][control_region_2].Clone() - histograms['V+Jets'][control_region_2].Clone()
      
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'QCD_non_iso_btag_bin_comparison_muon_AbsEta_' + b_tag_bin_1 + '_' + b_tag_bin_2
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = mu_title + ', non-iso, ' + b_tag_bins_latex[b_tag_bin_1] + '/' + b_tag_bins_latex[b_tag_bin_2]
    histogram_properties.x_axis_title = '$\left|\eta(\mu)\\right|$'
    histogram_properties.y_axis_title = 'arbitrary units/(0.1)'
    histogram_properties.x_limits = [0, 2.5]
    histogram_properties.y_limits = [0, 0.14]
    histogram_properties.mc_error = 0.0
    histogram_properties.legend_location = 'upper right'
    make_control_region_comparison( region_1, region_2,
                                   name_region_1 = b_tag_bins_latex[b_tag_bin_1], name_region_2 = b_tag_bins_latex[b_tag_bin_2],
                                   histogram_properties = histogram_properties, save_folder = output_folder )
