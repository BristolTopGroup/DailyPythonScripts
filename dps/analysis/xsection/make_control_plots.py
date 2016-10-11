from optparse import OptionParser
from dps.config.latex_labels import b_tag_bins_latex, samples_latex, channel_latex, \
    variables_latex, fit_variables_latex
from dps.config.variable_binning import variable_bins_ROOT
from dps.config.xsection import XSectionConfig
from dps.utils.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from dps.utils.plotting import make_data_mc_comparison_plot, Histogram_properties, \
make_control_region_comparison
from dps.utils.hist_utilities import prepare_histograms, clean_control_region
from dps.utils.ROOT_utils import get_histograms_from_files, set_root_defaults
from dps.utils.latex import setup_matplotlib
# latex, font, etc
setup_matplotlib()

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
        fitted_normalisation[sample] = ( total_value, total_error )
    return fitted_normalisation
    
def get_normalisation_error( normalisation ):
    total_normalisation = 0.
    total_error = 0.
    for _, number in normalisation.iteritems():
        total_normalisation += number[0]
        total_error += number[1]
    return total_error / total_normalisation

def compare_shapes( channel, x_axis_title, y_axis_title,
              control_region_1, control_region_2,
              name_region_1, name_region_2,
              name_prefix, x_limits,
              y_limits = [],
              y_max_scale = 1.2,
              rebin = 1,
              legend_location = ( 0.98, 0.78 ), cms_logo_location = 'right',
              legend_color = False,
              ratio_y_limits = None,
              ):
    global output_folder, measurement_config, category, normalise_to_fit
    global preliminary, norm_variable, sum_bins, b_tag_bin, histogram_files

    title = title_template % ( measurement_config.new_luminosity / 1000., measurement_config.centre_of_mass_energy )
    if channel == 'electron':
        histogram_files['data'] = measurement_config.data_file_electron
        histogram_files['QCD'] = measurement_config.electron_QCD_MC_category_templates[category]
    if channel == 'muon':
        histogram_files['data'] = measurement_config.data_file_muon
        histogram_files['QCD'] = measurement_config.muon_QCD_MC_category_templates[category]

    histograms = get_histograms_from_files( [control_region_1, control_region_2], histogram_files )
    prepare_histograms( histograms, rebin = rebin, scale_factor = measurement_config.luminosity_scale )
    
    region_1 = histograms['data'][control_region_1].Clone()
    region_2 = histograms['data'][control_region_2].Clone()

    histogram_properties = Histogram_properties()
    histogram_properties.name = name_prefix + b_tag_bin
    histogram_properties.title = title
    histogram_properties.x_axis_title = y_axis_title
    histogram_properties.y_axis_title = x_axis_title
    histogram_properties.x_limits = x_limits
    histogram_properties.y_limits = y_limits
    histogram_properties.legend_location = legend_location
    histogram_properties.cms_logo_location = cms_logo_location
    histogram_properties.preliminary = preliminary
    histogram_properties.legend_color = legend_color
    if b_tag_bin and b_tag_bin in b_tag_bins_latex.keys():
        histogram_properties.additional_text = channel_latex[channel] + ', ' + b_tag_bins_latex[b_tag_bin]
    else:
        histogram_properties.additional_text = channel_latex[channel]
    if ratio_y_limits:
        histogram_properties.ratio_y_limits = ratio_y_limits

    make_control_region_comparison( region_1, region_2,
                                   name_region_1 = name_region_1,
                                   name_region_2 = name_region_2,
                                   histogram_properties = histogram_properties,
                                   save_folder = output_folder )

def make_plot( channel, x_axis_title, y_axis_title,
              signal_region,
              name_prefix, x_limits,
              qcd_data_region_btag = '',
              use_qcd_data_region = True,
              y_limits = [],
              y_max_scale = 1.2,
              rebin = 1,
              legend_location = ( 0.98, 0.78 ), cms_logo_location = 'right',
              log_y = False,
              legend_color = False,
              ratio_y_limits = [0.3, 1.7],
              normalise = False,
              ):
    global output_folder, measurement_config, category, normalise_to_fit
    global preliminary, norm_variable, sum_bins, b_tag_bin, histogram_files

    qcd_data_region = ''
    title = title_template % ( measurement_config.new_luminosity / 1000., measurement_config.centre_of_mass_energy )
    normalisation = None
    if channel == 'electron':
        histogram_files['data'] = measurement_config.data_file_electron
        histogram_files['QCD'] = measurement_config.electron_QCD_MC_category_templates[category]
        normalisation = normalisations_electron[norm_variable]
        if use_qcd_data_region:
            qcd_data_region = 'QCDConversions'
    if channel == 'muon':
        histogram_files['data'] = measurement_config.data_file_muon
        histogram_files['QCD'] = measurement_config.muon_QCD_MC_category_templates[category]
        normalisation = normalisations_muon[norm_variable]
        if use_qcd_data_region:
            qcd_data_region = 'QCD non iso mu+jets ge3j'

    multi = isinstance( signal_region, list )
    histograms = {}
    qcd_control_region = ''
    if multi:
        signal_region_sum = signal_region[0].replace( '_bin_' + sum_bins[0], '' )
        qcd_control_region_sum = signal_region_sum.replace( 'Ref selection', qcd_data_region )
        qcd_control_region_sum = qcd_control_region_sum.replace( b_tag_bin, qcd_data_region_btag )
        for region in signal_region:
            qcd_control_region = region.replace( 'Ref selection', qcd_data_region )
            qcd_control_region = qcd_control_region.replace( b_tag_bin, qcd_data_region_btag )
            tmp_hists = get_histograms_from_files( [region, qcd_control_region], histogram_files )
            for name in tmp_hists.keys():
                if not histograms.has_key( name ):
                    histograms[name] = {}
                    histograms[name][signal_region_sum] = tmp_hists[name][region]
                    histograms[name][qcd_control_region_sum] = tmp_hists[name][qcd_control_region]
                else:
                    histograms[name][signal_region_sum] += tmp_hists[name][region]
                    histograms[name][qcd_control_region_sum] += tmp_hists[name][qcd_control_region]
        signal_region = signal_region_sum
        qcd_control_region = qcd_control_region_sum
    else:
        qcd_control_region = signal_region.replace( 'Ref selection', qcd_data_region )
        qcd_control_region = qcd_control_region.replace( b_tag_bin, qcd_data_region_btag )
        if qcd_data_region:
            histograms = get_histograms_from_files( [signal_region, qcd_control_region], histogram_files )
        else:
            histograms = get_histograms_from_files( [signal_region], histogram_files )

    signal_region_hists = {}
    inclusive_control_region_hists = {}
    for sample in histograms.keys():
        signal_region_hists[sample] = histograms[sample][signal_region]
        if use_qcd_data_region:
            inclusive_control_region_hists[sample] = histograms[sample][qcd_control_region]

    if normalise_to_fit:
        # only scale signal region to fit (results are invalid for control region)
        prepare_histograms( signal_region_hists, rebin = rebin,
                            scale_factor = measurement_config.luminosity_scale,
                            normalisation = normalisation )
    else:
        prepare_histograms( signal_region_hists, rebin = rebin,
                            scale_factor = measurement_config.luminosity_scale )
    prepare_histograms( inclusive_control_region_hists, rebin = rebin,
                            scale_factor = measurement_config.luminosity_scale )
    qcd_from_data = None
    if use_qcd_data_region:
        qcd_from_data = clean_control_region( inclusive_control_region_hists,
                          subtract = ['TTJet', 'V+Jets', 'SingleTop'] )
    else:
        qcd_from_data = signal_region_hists['QCD']

    n_qcd_predicted_mc = histograms['QCD'][signal_region].Integral()
    n_qcd_control_region = qcd_from_data.Integral()
    if not n_qcd_control_region == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )

    histograms_to_draw = [signal_region_hists['data'], qcd_from_data,
                          signal_region_hists['V+Jets'],
                          signal_region_hists['SingleTop'],
                          signal_region_hists['TTJet']]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']

    histogram_properties = Histogram_properties()
    histogram_properties.name = name_prefix + b_tag_bin
    if category != 'central':
        histogram_properties.name += '_' + category
    histogram_properties.title = title
    histogram_properties.x_axis_title = x_axis_title
    histogram_properties.y_axis_title = y_axis_title
    histogram_properties.x_limits = x_limits
    histogram_properties.y_limits = y_limits
    histogram_properties.y_max_scale = y_max_scale
    histogram_properties.xerr = None
    # workaround for rootpy issue #638
    histogram_properties.emptybins = True
    if b_tag_bin:
        histogram_properties.additional_text = channel_latex[channel] + ', ' + b_tag_bins_latex[b_tag_bin]
    else:
        histogram_properties.additional_text = channel_latex[channel]
    histogram_properties.legend_location = legend_location
    histogram_properties.cms_logo_location = cms_logo_location
    histogram_properties.preliminary = preliminary
    histogram_properties.set_log_y = log_y
    histogram_properties.legend_color = legend_color
    if ratio_y_limits:
        histogram_properties.ratio_y_limits = ratio_y_limits

    if normalise_to_fit:
        histogram_properties.mc_error = get_normalisation_error( normalisation )
        histogram_properties.mc_errors_label = 'fit uncertainty'
    else:
        histogram_properties.mc_error = mc_uncertainty
        histogram_properties.mc_errors_label = 'MC unc.'

    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder,
                                 show_ratio = False, normalise = normalise,
                                 )
    histogram_properties.name += '_with_ratio'
    loc = histogram_properties.legend_location
    # adjust legend location as it is relative to canvas!
    histogram_properties.legend_location = ( loc[0], loc[1] + 0.05 )
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder,
                                 show_ratio = True, normalise = normalise,
                                 )

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
    make_folder_if_not_exists( output_folder )
    category = options.category
    met_type = translate_options[options.metType]
    make_additional_QCD_plots = options.additional_QCD_plots

    # this is shown as \ttbar (or MC) uncertainty on the plots
    # in fact, it takes the uncertainty on the whole MC stack
    # although unimportant, this needs revision
    mc_uncertainty = 0.10
    
    histogram_files = {
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
    title_template = '$%.1f$ fb$^{-1}$ (%d TeV)'
    e_title = title_template % ( measurement_config.new_luminosity / 1000., measurement_config.centre_of_mass_energy )
    preliminary = True
    
    b_tag_bin = '2orMoreBtags'
    norm_variable = 'MET'
    # comment out plots you don't want
    include_plots = [
                        'eta',
                        'pT',
                        'MET',
                        'MET log',
                        'MET phi',
                        'HT',
                        'ST',
                        'WPT',
                        'MT',
                        'M3',
                        'angle_bl',
                        'bjet invariant mass',
                        'b-tag multiplicity',
                        'b-tag multiplicity reweighted',
                        'jet multiplicity',
                        'n vertex',
                        'n vertex reweighted',
                        ]
    additional_qcd_plots = [
                            'eta in MET bins',
                            'eta in HT bins',
                            'eta in ST bins',
                            'eta in MT bins',
                            'eta in WPT bins',
                            'QCD PFReliso non-iso',
                            'QCD PFReliso',
                            'QCD eta',
                            'QCD eta shapes',
                            ]
    if make_additional_QCD_plots:
        include_plots.extend( additional_qcd_plots )
    ###################################################
    # lepton |eta|
    ###################################################
    if 'eta' in include_plots:
        make_plot( 'electron',
                  x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Electron/electron_AbsEta_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'electron_AbsEta_',
                  x_limits = [0, 2.6],
                  rebin = 10,
                  legend_location = ( 0.98, 0.78 ),
                  cms_logo_location = 'right',
                  )
        make_plot( 'muon',
                  x_axis_title = '$\left|\eta(\mu)\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Muon/muon_AbsEta_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'muon_AbsEta_',
                  x_limits = [0, 2.6],
                  rebin = 10,
                  legend_location = ( 0.98, 0.78 ),
                  cms_logo_location = 'right',
                  )
    ###################################################
    # lepton p_T
    ###################################################
    if 'pT' in include_plots:
        make_plot( 'electron',
                  x_axis_title = '$p_\mathrm{T}(\mathrm{e})$ [GeV]',
                  y_axis_title = 'Events/(10 GeV)',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Electron/electron_pT_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'electron_pT_',
                  x_limits = [0, 250],
                  rebin = 10,
                  legend_location = ( 0.98, 0.78 ),
                  cms_logo_location = 'right',
                  )
        make_plot( 'muon',
                  x_axis_title = '$p_\mathrm{T}(\mu)$ [GeV]',
                  y_axis_title = 'Events/(10 GeV)',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Muon/muon_pT_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'muon_pT_',
                  x_limits = [0, 250],
                  rebin = 10,
                  legend_location = ( 0.98, 0.78 ),
                  cms_logo_location = 'right',
                  )
    ###################################################
    # MET
    ###################################################
    if 'MET' in include_plots:
        make_plot( 'electron',
                  x_axis_title = '$%s$ [GeV]' % variables_latex['MET'],
                  y_axis_title = 'Events/(5 GeV)',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'EPlusJets_patType1CorrectedPFMet_',
                  x_limits = [0, 200],
                  rebin = 1,
                  legend_location = ( 0.98, 0.78 ),
                  cms_logo_location = 'right',
                  )
        make_plot( 'muon',
                  x_axis_title = '$%s$ [GeV]' % variables_latex['MET'],
                  y_axis_title = 'Events/(5 GeV)',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'MuPlusJets_patType1CorrectedPFMet_',
                  x_limits = [0, 200],
                  rebin = 1,
                  legend_location = ( 0.98, 0.78 ),
                  cms_logo_location = 'right',
                  )
    ###################################################
    # MET log
    ###################################################
    if 'MET log' in include_plots:
        make_plot( 'electron',
                  x_axis_title = '$%s$ [GeV]' % variables_latex['MET'],
                  y_axis_title = 'Events/(20 GeV)',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'EPlusJets_patType1CorrectedPFMet_log_',
                  x_limits = [200, 700],
                  rebin = 4,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'left',
                  log_y = True,
                  )
        make_plot( 'muon',
                  x_axis_title = '$%s$ [GeV]' % variables_latex['MET'],
                  y_axis_title = 'Events/(20 GeV)',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'MuPlusJets_patType1CorrectedPFMet_log_',
                  x_limits = [200, 700],
                  rebin = 4,
                  legend_location = ( 0.98, 0.78 ),
                  cms_logo_location = 'right',
                  log_y = True,
                  )
    ###################################################
    # MET phi
    ###################################################
    if 'MET phi' in include_plots:
        make_plot( 'electron',
                  x_axis_title = '$\phi\left(%s\\right)$' % variables_latex['MET'],
                  y_axis_title = 'Events/(0.2)',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_phi_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'EPlusJets_patType1CorrectedPFMet_phi_',
                  x_limits = [-3.3, 3.3],
                  rebin = 2,
                  legend_location = ( 0.7, 0.62 ),
                  cms_logo_location = 'left',
                  legend_color = True,
                  )
        make_plot( 'muon',
                  x_axis_title = '$\phi\left(%s\\right)$' % variables_latex['MET'],
                  y_axis_title = 'Events/(0.2)',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/MET_phi_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'MuPlusJets_patType1CorrectedPFMet_phi_',
                  x_limits = [-3.3, 3.3],
                  rebin = 2,
                  legend_location = ( 0.7, 0.62 ),
                  cms_logo_location = 'left',
                  legend_color = True,
                  )
    ###################################################
    # HT
    ###################################################
    norm_variable = 'HT'
    if 'HT' in include_plots:
        make_plot( 'electron',
                  x_axis_title = '$%s$ [GeV]' % variables_latex['HT'],
                  y_axis_title = 'Events/(20 GeV)',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/HT_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'EPlusJets_HT_',
                  x_limits = [100, 1000],
                  rebin = 4,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
        make_plot( 'muon',
                  x_axis_title = '$%s$ [GeV]' % variables_latex['HT'],
                  y_axis_title = 'Events/(20 GeV)',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/HT_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'MuPlusJets_HT_',
                  x_limits = [100, 1000],
                  rebin = 4,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
    ###################################################
    # ST
    ###################################################
    norm_variable = 'ST'
    if 'ST' in include_plots:
        make_plot( 'electron',
                  x_axis_title = '$%s$ [GeV]' % variables_latex['ST'],
                  y_axis_title = 'Events/(20 GeV)',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/ST_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'EPlusJets_patType1CorrectedPFMet_ST_',
                  x_limits = [150, 1200],
                  rebin = 4,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
        make_plot( 'muon',
                  x_axis_title = '$%s$ [GeV]' % variables_latex['ST'],
                  y_axis_title = 'Events/(20 GeV)',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/ST_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'MuPlusJets_patType1CorrectedPFMet_ST_',
                  x_limits = [150, 1200],
                  rebin = 4,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
    ###################################################
    # WPT
    ###################################################
    norm_variable = 'WPT'
    if 'WPT' in include_plots:
        make_plot( 'electron',
                  x_axis_title = '$%s$ [GeV]' % variables_latex['WPT'],
                  y_axis_title = 'Events/(10 GeV)',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/WPT_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'EPlusJets_patType1CorrectedPFMet_WPT_',
                  x_limits = [0, 500],
                  rebin = 10,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
        make_plot( 'muon',
                  x_axis_title = '$%s$ [GeV]' % variables_latex['WPT'],
                  y_axis_title = 'Events/(10 GeV)',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/WPT_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'MuPlusJets_patType1CorrectedPFMet_WPT_',
                  x_limits = [0, 500],
                  rebin = 10,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
    ###################################################
    # MT
    ###################################################
    norm_variable = 'MT'
    if 'MT' in include_plots:
        make_plot( 'electron',
                  x_axis_title = '$%s$ [GeV]' % variables_latex['MT'],
                  y_axis_title = 'Events/(5 GeV)',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/MET/patType1CorrectedPFMet/Transverse_Mass_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'EPlusJets_patType1CorrectedPFMet_MT_',
                  x_limits = [0, 200],
                  rebin = 5,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
        make_plot( 'muon',
                  x_axis_title = '$%s$ [GeV]' % variables_latex['MT'],
                  y_axis_title = 'Events/(5 GeV)',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/MET/patType1CorrectedPFMet/Transverse_Mass_' + b_tag_bin,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'MuPlusJets_patType1CorrectedPFMet_MT_',
                  x_limits = [0, 200],
                  rebin = 5,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
        
    ###################################################
    # M3 
    ###################################################  
    norm_variable = 'MT'
    if 'M3' in include_plots:
        # M3 histograms are not plotted in the histogram output files from analysis software
        # so sum the M3 histograms from the BAT output histogram file and sum over all bins
        sum_bins = variable_bins_ROOT['MT']
        tmp = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_MT_Analysis/MT_with_patType1CorrectedPFMet_bin_%s/M3_' + b_tag_bin
        regions = [tmp % bin_i for bin_i in variable_bins_ROOT['MT']]
        make_plot( 'electron',
                  x_axis_title = '$M3$ [GeV]',
                  y_axis_title = 'Events/(20 GeV)',
                  signal_region = regions,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'EPlusJets_M3_',
                  x_limits = [0, 1000],
                  rebin = 4,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
        tmp = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Binned_MT_Analysis/MT_with_patType1CorrectedPFMet_bin_%s/M3_' + b_tag_bin
        regions = [tmp % bin_i for bin_i in variable_bins_ROOT['MT']]
        make_plot( 'muon',
                  x_axis_title = '$M3$ [GeV]',
                  y_axis_title = 'Events/(20 GeV)',
                  signal_region = regions,
                  qcd_data_region_btag = '0btag',
                  name_prefix = 'MuPlusJets_M3_',
                  x_limits = [0, 1000],
                  rebin = 4,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
    ###################################################
    # angle_bl
    ###################################################
    if 'angle_bl' in include_plots:
        # angle_bl histograms are not plotted in the histogram output files from analysis software
        # so sum the angle_bl histograms from the BAT output histogram file and sum over all bins
        sum_bins = variable_bins_ROOT['MT']
        tmp = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_MT_Analysis/MT_with_patType1CorrectedPFMet_bin_%s/angle_bl_' + b_tag_bin
        regions = [tmp % bin_i for bin_i in variable_bins_ROOT['MT']]
        make_plot( 'electron',
                  x_axis_title = fit_variables_latex['angle_bl'],
                  y_axis_title = 'Events/(0.2)',
                  signal_region = regions,
                  qcd_data_region_btag = '1btag',
                  name_prefix = 'EPlusJets_angle_bl_',
                  x_limits = [0, 4],
                  rebin = 2,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
        tmp = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Binned_MT_Analysis/MT_with_patType1CorrectedPFMet_bin_%s/angle_bl_' + b_tag_bin
        regions = [tmp % bin_i for bin_i in variable_bins_ROOT['MT']]
        make_plot( 'muon',
                  x_axis_title = fit_variables_latex['angle_bl'],
                  y_axis_title = 'Events/(0.2)',
                  signal_region = regions,
                  qcd_data_region_btag = '1btag',
                  name_prefix = 'MuPlusJets_angle_bl_',
                  x_limits = [0, 4],
                  rebin = 2,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
    ###################################################
    # bjet invariant mass
    ###################################################
    norm_variable = 'MET'
    if 'bjet invariant mass' in include_plots:
        b_tag_bin = '4orMoreBtags'
        make_plot( 'electron',
                  x_axis_title = '$M_{\mathrm{b}\\bar{\mathrm{b}}}$',
                  y_axis_title = 'Normalised events/(10 GeV)',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/bjet_invariant_mass_' + b_tag_bin,
                  qcd_data_region_btag = '',
                  use_qcd_data_region = False,
                  name_prefix = 'EPlusJets_BJets_invmass_',
                  x_limits = [0, 800],
                  rebin = 10,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
        make_plot( 'muon',
                  x_axis_title = '$M_{\mathrm{b}\\bar{\mathrm{b}}}$',
                  y_axis_title = 'Normalised events/(10 GeV)',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/bjet_invariant_mass_' + b_tag_bin,
                  qcd_data_region_btag = '',
                  use_qcd_data_region = False,
                  name_prefix = 'MuPlusJets_BJets_invmass_',
                  x_limits = [0, 800],
                  rebin = 10,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
    ###################################################
    # b-tag multiplicity
    ###################################################
    if 'b-tag multiplicity' in include_plots:
        b_tag_bin = ''
        make_plot( 'electron',
                  x_axis_title = 'B-tag multiplicity',
                  y_axis_title = 'Events',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/N_BJets',
                  qcd_data_region_btag = '',
                  use_qcd_data_region = False,
                  name_prefix = 'EPlusJets_N_BJets',
                  x_limits = [1.5, 7.5],
                  rebin = 1,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
        make_plot( 'muon',
                  x_axis_title = 'B-tag multiplicity',
                  y_axis_title = 'Events',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/N_BJets',
                  qcd_data_region_btag = '',
                  use_qcd_data_region = False,
                  name_prefix = 'MuPlusJets_N_BJets',
                  x_limits = [1.5, 7.5],
                  rebin = 1,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
    if 'b-tag multiplicity reweighted' in include_plots:
        b_tag_bin = ''
        make_plot( 'electron',
                  x_axis_title = 'B-tag multiplicity',
                  y_axis_title = 'Events',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/N_BJets_reweighted',
                  qcd_data_region_btag = '',
                  use_qcd_data_region = False,
                  name_prefix = 'EPlusJets_N_BJets_reweighted',
                  x_limits = [1.5, 7.5],
                  rebin = 1,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
        make_plot( 'muon',
                  x_axis_title = 'B-tag multiplicity',
                  y_axis_title = 'Events',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/N_BJets',
                  qcd_data_region_btag = '',
                  use_qcd_data_region = False,
                  name_prefix = 'MuPlusJets_N_BJets',
                  x_limits = [1.5, 7.5],
                  rebin = 1,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
    ###################################################
    # jet multiplicity
    ###################################################
    b_tag_bin = '2orMoreBtags'
    if 'jet multiplicity' in include_plots:
        make_plot( 'electron',
                  x_axis_title = 'Jet multiplicity',
                  y_axis_title = 'Events',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Jets/N_Jets_' + b_tag_bin,
                  qcd_data_region_btag = '',
                  use_qcd_data_region = False,
                  name_prefix = 'EPlusJets_N_Jets_',
                  x_limits = [3.5, 9.5],
                  rebin = 1,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
        make_plot( 'muon',
                  x_axis_title = 'Jet multiplicity',
                  y_axis_title = 'Events',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Jets/N_Jets_' + b_tag_bin,
                  qcd_data_region_btag = '',
                  use_qcd_data_region = False,
                  name_prefix = 'MuPlusJets_N_Jets_',
                  x_limits = [3.5, 9.5],
                  rebin = 1,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  )
    ###################################################
    # vertex multiplicity
    ###################################################
    b_tag_bin = ''
    if 'n vertex' in include_plots:
        make_plot( 'electron',
                  x_axis_title = 'N(PV)',
                  y_axis_title = 'arbitrary units',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Vertices/nVertex',
                  qcd_data_region_btag = '',
                  use_qcd_data_region = False,
                  name_prefix = 'EPlusJets_nVertex_',
                  x_limits = [0, 50],
                  rebin = 1,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  normalise = True,
                  )
        make_plot( 'muon',
                  x_axis_title = 'N(PV)',
                  y_axis_title = 'arbitrary units',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Vertices/nVertex',
                  qcd_data_region_btag = '',
                  use_qcd_data_region = False,
                  name_prefix = 'MuPlusJets_nVertex_',
                  x_limits = [0, 50],
                  rebin = 1,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  normalise = True,
                  )
    if 'n vertex reweighted' in include_plots:
        make_plot( 'electron',
                  x_axis_title = 'N(PV)',
                  y_axis_title = 'arbitrary units',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Vertices/nVertex_reweighted',
                  qcd_data_region_btag = '',
                  use_qcd_data_region = False,
                  name_prefix = 'EPlusJets_nVertex_reweighted_',
                  x_limits = [0, 50],
                  rebin = 1,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  normalise = True,
                  )
        make_plot( 'muon',
                  x_axis_title = 'N(PV)',
                  y_axis_title = 'arbitrary units',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/Vertices/nVertex_reweighted',
                  qcd_data_region_btag = '',
                  use_qcd_data_region = False,
                  name_prefix = 'MuPlusJets_nVertex_reweighted_',
                  x_limits = [0, 50],
                  rebin = 1,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  normalise = True,
                  )
    tmp_out = output_folder
    output_folder += '/qcd_plots/'
    ###################################################
    # eta in measurement variable bins
    ###################################################
    if 'eta in MET bins' in include_plots:
        # QCD control regions (electron |eta|), MET bins
        b_tag_bin = '0btag'
        for variable_bin in variable_bins_ROOT['MET']:
            signal_region_e = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Binned_MET_Analysis/patType1CorrectedPFMet_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            signal_region_mu = 'TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Binned_MET_Analysis/patType1CorrectedPFMet_bin_' + variable_bin + '/muon_absolute_eta_' + b_tag_bin
            name_e = 'QCD_conversion_control_region_electron_AbsEta_MET_bin_' + variable_bin + '_'
            name_mu = 'QCD_non_iso_control_region_muon_AbsEta_MET_bin_' + variable_bin + '_'
            make_plot( 'electron',
                  x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = signal_region_e,
                  qcd_data_region_btag = b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = name_e,
                  x_limits = [0, 2.6],
                  rebin = 1,
                  legend_location = ( 0.95, 0.88 ),
                  cms_logo_location = 'left',
                  y_max_scale = 1.5,
                  ratio_y_limits = [0.1, 3.0],
                  )
            signal_region_e = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Binned_MET_Analysis/patType1CorrectedPFMet_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            name_e = 'QCD_non_iso_control_region_electron_AbsEta_MET_bin_' + variable_bin + '_'
            make_plot( 'electron',
                  x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = signal_region_e,
                  qcd_data_region_btag = b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = name_e,
                  x_limits = [0, 2.6],
                  rebin = 1,
                  legend_location = ( 0.95, 0.88 ),
                  cms_logo_location = 'left',
                  y_max_scale = 1.5,
                  ratio_y_limits = [0.1, 3.0],
                  )
            make_plot( 'muon',
                  x_axis_title = '$\left|\eta(\mu)\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = signal_region_mu,
                  qcd_data_region_btag = b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = name_mu,
                  x_limits = [0, 2.6],
                  rebin = 1,
                  legend_location = ( 0.95, 0.88 ),
                  cms_logo_location = 'left',
                  y_max_scale = 1.5,
                  ratio_y_limits = [0.1, 3.0],
                  )
    if 'eta in ST bins' in include_plots:
        b_tag_bin = '0btag'
        for variable_bin in variable_bins_ROOT['ST']:
            signal_region_e = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Binned_ST_Analysis/ST_with_patType1CorrectedPFMet_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            signal_region_mu = 'TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Binned_ST_Analysis/ST_with_patType1CorrectedPFMet_bin_' + variable_bin + '/muon_absolute_eta_' + b_tag_bin
            name_e = 'QCD_conversion_control_region_electron_AbsEta_ST_bin_' + variable_bin + '_'
            name_mu = 'QCD_non_iso_control_region_muon_AbsEta_ST_bin_' + variable_bin + '_'
            make_plot( 'electron',
                  x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = signal_region_e,
                  qcd_data_region_btag = b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = name_e,
                  x_limits = [0, 2.6],
                  rebin = 1,
                  legend_location = ( 0.95, 0.88 ),
                  cms_logo_location = 'left',
                  y_max_scale = 1.5,
                  ratio_y_limits = [0.1, 3.0],
                  )
            signal_region_e = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Binned_ST_Analysis/ST_with_patType1CorrectedPFMet_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            name_e = 'QCD_non_iso_control_region_electron_AbsEta_ST_bin_' + variable_bin + '_'
            make_plot( 'electron',
                  x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = signal_region_e,
                  qcd_data_region_btag = b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = name_e,
                  x_limits = [0, 2.6],
                  rebin = 1,
                  legend_location = ( 0.95, 0.88 ),
                  cms_logo_location = 'left',
                  y_max_scale = 1.5,
                  ratio_y_limits = [0.1, 3.0],
                  )
            make_plot( 'muon',
                  x_axis_title = '$\left|\eta(\mu)\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = signal_region_mu,
                  qcd_data_region_btag = b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = name_mu,
                  x_limits = [0, 2.6],
                  rebin = 1,
                  legend_location = ( 0.95, 0.88 ),
                  cms_logo_location = 'left',
                  y_max_scale = 1.5,
                  ratio_y_limits = [0.1, 3.0],
                  )
    if 'eta in HT bins' in include_plots:
        b_tag_bin = '0btag'
        for variable_bin in variable_bins_ROOT['HT']:
            signal_region_e = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Binned_HT_Analysis/HT_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            signal_region_mu = 'TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Binned_HT_Analysis/HT_bin_' + variable_bin + '/muon_absolute_eta_' + b_tag_bin
            name_e = 'QCD_conversion_control_region_electron_AbsEta_HT_bin_' + variable_bin + '_'
            name_mu = 'QCD_non_iso_control_region_muon_AbsEta_HT_bin_' + variable_bin + '_'
            make_plot( 'electron',
                  x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = signal_region_e,
                  qcd_data_region_btag = b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = name_e,
                  x_limits = [0, 2.6],
                  rebin = 1,
                  legend_location = ( 0.95, 0.88 ),
                  cms_logo_location = 'left',
                  y_max_scale = 1.5,
                  ratio_y_limits = [0.1, 3.0],
                  )
            signal_region_e = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Binned_HT_Analysis/HT_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            name_e = 'QCD_non_iso_control_region_electron_AbsEta_HT_bin_' + variable_bin + '_'
            make_plot( 'electron',
                  x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = signal_region_e,
                  qcd_data_region_btag = b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = name_e,
                  x_limits = [0, 2.6],
                  rebin = 1,
                  legend_location = ( 0.95, 0.88 ),
                  cms_logo_location = 'left',
                  y_max_scale = 1.5,
                  ratio_y_limits = [0.1, 3.0],
                  )
            make_plot( 'muon',
                  x_axis_title = '$\left|\eta(\mu)\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = signal_region_mu,
                  qcd_data_region_btag = b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = name_mu,
                  x_limits = [0, 2.6],
                  rebin = 1,
                  legend_location = ( 0.95, 0.88 ),
                  cms_logo_location = 'left',
                  y_max_scale = 1.5,
                  ratio_y_limits = [0.1, 3.0],
                  )
    if 'eta in MT bins' in include_plots:
        b_tag_bin = '0btag'
        for variable_bin in variable_bins_ROOT['MT']:
            signal_region_e = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Binned_MT_Analysis/MT_with_patType1CorrectedPFMet_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            signal_region_mu = 'TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Binned_MT_Analysis/MT_with_patType1CorrectedPFMet_bin_' + variable_bin + '/muon_absolute_eta_' + b_tag_bin
            name_e = 'QCD_conversion_control_region_electron_AbsEta_MT_bin_' + variable_bin + '_'
            name_mu = 'QCD_non_iso_control_region_muon_AbsEta_MT_bin_' + variable_bin + '_'
            make_plot( 'electron',
                  x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = signal_region_e,
                  qcd_data_region_btag = b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = name_e,
                  x_limits = [0, 2.6],
                  rebin = 1,
                  legend_location = ( 0.95, 0.88 ),
                  cms_logo_location = 'left',
                  y_max_scale = 1.5,
                  ratio_y_limits = [0.1, 3.0],
                  )
            signal_region_e = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Binned_MT_Analysis/MT_with_patType1CorrectedPFMet_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            name_e = 'QCD_non_iso_control_region_electron_AbsEta_MT_bin_' + variable_bin + '_'
            make_plot( 'electron',
                  x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = signal_region_e,
                  qcd_data_region_btag = b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = name_e,
                  x_limits = [0, 2.6],
                  rebin = 1,
                  legend_location = ( 0.95, 0.88 ),
                  cms_logo_location = 'left',
                  y_max_scale = 1.5,
                  ratio_y_limits = [0.1, 3.0],
                  )
            make_plot( 'muon',
                  x_axis_title = '$\left|\eta(\mu)\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = signal_region_mu,
                  qcd_data_region_btag = b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = name_mu,
                  x_limits = [0, 2.6],
                  rebin = 1,
                  legend_location = ( 0.95, 0.88 ),
                  cms_logo_location = 'left',
                  y_max_scale = 1.5,
                  ratio_y_limits = [0.1, 3.0],
                  )
    if 'eta in WPT bins' in include_plots:
        b_tag_bin = '0btag'
        for variable_bin in variable_bins_ROOT['WPT']:
            signal_region_e = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Binned_WPT_Analysis/WPT_with_patType1CorrectedPFMet_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            signal_region_mu = 'TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Binned_WPT_Analysis/WPT_with_patType1CorrectedPFMet_bin_' + variable_bin + '/muon_absolute_eta_' + b_tag_bin
            name_e = 'QCD_conversion_control_region_electron_AbsEta_WPT_bin_' + variable_bin + '_'
            name_mu = 'QCD_non_iso_control_region_muon_AbsEta_WPT_bin_' + variable_bin + '_'
            make_plot( 'electron',
                  x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = signal_region_e,
                  qcd_data_region_btag = b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = name_e,
                  x_limits = [0, 2.6],
                  rebin = 1,
                  legend_location = ( 0.95, 0.88 ),
                  cms_logo_location = 'left',
                  y_max_scale = 1.5,
                  ratio_y_limits = [0.1, 3.0],
                  )
            signal_region_e = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Binned_WPT_Analysis/WPT_with_patType1CorrectedPFMet_bin_' + variable_bin + '/electron_absolute_eta_' + b_tag_bin
            name_e = 'QCD_non_iso_control_region_electron_AbsEta_WPT_bin_' + variable_bin + '_'
            make_plot( 'electron',
                  x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = signal_region_e,
                  qcd_data_region_btag = b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = name_e,
                  x_limits = [0, 2.6],
                  rebin = 1,
                  legend_location = ( 0.95, 0.88 ),
                  cms_logo_location = 'left',
                  y_max_scale = 1.5,
                  ratio_y_limits = [0.1, 3.0],
                  )
            make_plot( 'muon',
                  x_axis_title = '$\left|\eta(\mu)\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = signal_region_mu,
                  qcd_data_region_btag = b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = name_mu,
                  x_limits = [0, 2.6],
                  rebin = 1,
                  legend_location = ( 0.95, 0.88 ),
                  cms_logo_location = 'left',
                  y_max_scale = 1.5,
                  ratio_y_limits = [0.1, 3.0],
                  )
    ###################################################
    # QCD PFReliso (rho-corrected) for non-isolated region
    ###################################################
    if 'QCD PFReliso non-iso' in include_plots:
        norm_variable = 'MET'
        b_tag_bin = '0btag'
        make_plot( 'electron',
                  x_axis_title = 'PF reliso(e)',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Electron/electron_rhoCorrectedIso_03_' + b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = 'QCD_electron_rhoCorrectedIso_non_iso_control_region_',
                  x_limits = [0, 3],
                  rebin = 10,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  log_y = True,
                  )
        make_plot( 'muon',
                  x_axis_title = 'PF reliso($\mu$)',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Muon/muon_pfIsolation_04_' + b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = 'QCD_muon_pfIsolation_non_iso_control_region_',
                  x_limits = [0, 3],
                  rebin = 10,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  log_y = True,
                  )
    ###################################################
    # QCD PFReliso (rho-corrected)  without iso cut
    ###################################################
    if 'QCD PFReliso' in include_plots:
        norm_variable = 'MET'
        b_tag_bin = '0btag'
        make_plot( 'electron',
                  x_axis_title = 'PF reliso(e)',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/QCD e+jets PFRelIso/Electron/electron_rhoCorrectedIso_03_' + b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = 'QCD_electron_rhoCorrectedIso_',
                  x_limits = [0, 3],
                  rebin = 10,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  log_y = True,
                  )
        make_plot( 'muon',
                  x_axis_title = 'PF reliso($\mu$)',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/QCD mu+jets PFRelIso ge3j/Muon/muon_pfIsolation_04_' + b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = 'QCD_muon_pfIsolation_',
                  x_limits = [0, 3],
                  rebin = 10,
                  legend_location = ( 0.95, 0.78 ),
                  cms_logo_location = 'right',
                  log_y = True,
                  )
    ###################################################
    # QCD lepton |eta|
    ###################################################
    if 'QCD eta' in include_plots:
        b_tag_bin = '0btag'
        make_plot( 'electron',
                  x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Electron/electron_AbsEta_' + b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = 'QCD_electron_AbsEta_conversion_control_region_',
                  x_limits = [0, 2.6],
                  rebin = 10,
                  legend_location = ( 0.98, 0.78 ),
                  cms_logo_location = 'right',
                  )
        make_plot( 'electron',
                  x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Electron/electron_AbsEta_' + b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = 'QCD_electron_AbsEta_non_iso_control_region_',
                  x_limits = [0, 2.6],
                  rebin = 10,
                  legend_location = ( 0.98, 0.78 ),
                  cms_logo_location = 'right',
                  )
        make_plot( 'muon',
                  x_axis_title = '$\left|\eta(\mu)\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = 'TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Muon/muon_AbsEta_' + b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = 'QCD_muon_AbsEta_non_iso_control_region_',
                  x_limits = [0, 2.6],
                  rebin = 10,
                  legend_location = ( 0.98, 0.78 ),
                  cms_logo_location = 'right',
                  )
        b_tag_bin = '1orMoreBtag'
        make_plot( 'electron',
                  x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Electron/electron_AbsEta_' + b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = 'QCD_electron_AbsEta_conversion_control_region_',
                  x_limits = [0, 2.6],
                  rebin = 10,
                  legend_location = ( 0.98, 0.78 ),
                  cms_logo_location = 'right',
                  )
        make_plot( 'electron',
                  x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                  y_axis_title = 'Events/(0.1)',
                  signal_region = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Electron/electron_AbsEta_' + b_tag_bin,
                  use_qcd_data_region = False,
                  name_prefix = 'QCD_electron_AbsEta_non_iso_control_region_',
                  x_limits = [0, 2.6],
                  rebin = 10,
                  legend_location = ( 0.98, 0.78 ),
                  cms_logo_location = 'right',
                  )
    output_folder = tmp_out
    ###################################################
    # QCD shape comparison electron
    ###################################################
    b_tag_bin = '0btag'
    output_folder += '/qcd_plots/shape_comparisons/'
    if 'QCD eta shapes' in include_plots:
        compare_shapes( 'electron',
                       x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                       y_axis_title = 'arbitrary units/(0.1)',
                       control_region_1 = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Electron/electron_AbsEta_' + b_tag_bin,
                       control_region_2 = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Electron/electron_AbsEta_' + b_tag_bin,
                       name_region_1 = 'conversions',
                       name_region_2 = 'non-isolated e',
                       name_prefix = 'QCD_electron_AbsEta_control_region_comparison_',
                       x_limits = [0, 2.6],
                       y_limits = [0, 0.14],
                       ratio_y_limits = [0, 4],
                       rebin = 10,
                       legend_location = ( 0.98, 0.88 ),
                       cms_logo_location = 'left',
                       )
        # QCD conversions btag bin shape comparison
        b_tag_bin = '0btag_1orMoreBtag'
        b_tag_bin_1 = '0btag'
        b_tag_bin_2 = '1orMoreBtag'
        compare_shapes( 'electron',
                       x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                       y_axis_title = 'arbitrary units/(0.1)',
                       control_region_1 = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Electron/electron_AbsEta_' + b_tag_bin_1,
                       control_region_2 = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/Electron/electron_AbsEta_' + b_tag_bin_2,
                       name_region_1 = b_tag_bins_latex[b_tag_bin_1],
                       name_region_2 = b_tag_bins_latex[b_tag_bin_2],
                       name_prefix = 'QCD_electron_AbsEta_conversions_btag_bin_comparison_',
                       x_limits = [0, 2.6],
                       y_limits = [0, 0.14],
                       rebin = 10,
                       legend_location = ( 0.98, 0.78 ),
                       cms_logo_location = 'left',
                       )
        # QCD non-iso btag bin shape comparison
        compare_shapes( 'electron',
                       x_axis_title = '$\left|\eta(\mathrm{e})\\right|$',
                       y_axis_title = 'arbitrary units/(0.1)',
                       control_region_1 = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Electron/electron_AbsEta_' + b_tag_bin_1,
                       control_region_2 = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/Electron/electron_AbsEta_' + b_tag_bin_2,
                       name_region_1 = b_tag_bins_latex[b_tag_bin_1],
                       name_region_2 = b_tag_bins_latex[b_tag_bin_2],
                       name_prefix = 'QCD_electron_AbsEta_noniso_btag_bin_comparison_',
                       x_limits = [0, 2.6],
                       y_limits = [0, 0.14],
                       rebin = 10,
                       legend_location = ( 0.98, 0.78 ),
                       cms_logo_location = 'left',
                       )
        compare_shapes( 'muon',
                       x_axis_title = '$\left|\eta(\mu)\\right|$',
                       y_axis_title = 'arbitrary units/(0.1)',
                       control_region_1 = 'TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Muon/muon_AbsEta_' + b_tag_bin_1,
                       control_region_2 = 'TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets ge3j/Muon/muon_AbsEta_' + b_tag_bin_2,
                       name_region_1 = b_tag_bins_latex[b_tag_bin_1],
                       name_region_2 = b_tag_bins_latex[b_tag_bin_2],
                       name_prefix = 'QCD_muon_AbsEta_noniso_btag_bin_comparison_',
                       x_limits = [0, 2.6],
                       y_limits = [0, 0.14],
                       rebin = 10,
                       legend_location = ( 0.98, 0.78 ),
                       cms_logo_location = 'left',
                       )
        
    output_folder = tmp_out
