from optparse import OptionParser
from config.latex_labels import b_tag_bins_latex, samples_latex, channel_latex, \
    variables_latex, fit_variables_latex, control_plots_latex
from config.variable_binning import variable_bins_ROOT, bin_edges, fit_variable_bin_edges, control_plots_bins
from config import XSectionConfig
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from tools.plotting import make_data_mc_comparison_plot, Histogram_properties, \
make_control_region_comparison
from rootpy.plotting import Hist
from tools.hist_utilities import prepare_histograms, clean_control_region, get_normalisation_error, get_fitted_normalisation
from tools.ROOT_utils import get_histograms_from_trees, set_root_defaults
from tools.latex import setup_matplotlib
# latex, font, etc
setup_matplotlib()

title_template = '$%.1f$ pb$^{-1}$ (%d TeV)'

def compare_shapes( channel, x_axis_title, y_axis_title,
              control_region_1, name_region_1, samples_region_1,
              control_region_2, name_region_2, samples_region_2,
              name_prefix, x_limits, nBins,
              y_limits = [],
              y_max_scale = 1.2,
              rebin = 1,
              legend_location = ( 0.98, 0.78 ), cms_logo_location = 'right',
              legend_color = False,
              ratio_y_limits = None,
              ):
    global output_folder, measurement_config, category, normalise_to_fit, normalise_to_data
    global preliminary, norm_variable, sum_bins, b_tag_bin, histogram_files

    title = title_template % ( measurement_config.new_luminosity, measurement_config.centre_of_mass_energy )
    if 'electron' in channel:
        histogram_files['data'] = measurement_config.data_file_electron_trees
        histogram_files['QCD'] = measurement_config.electron_QCD_MC_category_templates_trees[category]
    if 'muon' in channel:
        histogram_files['data'] = measurement_config.data_file_muon_trees
        histogram_files['QCD'] = measurement_config.muon_QCD_MC_category_templates_trees[category]

    histograms_region1 = get_histograms_from_trees( trees = [control_region_1], branch = name_region_1, weightBranch = 'EventWeight', files = histogram_files, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1] )
    histograms_region2 = get_histograms_from_trees( trees = [control_region_2], branch = name_region_2, weightBranch = 'EventWeight', files = histogram_files, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1] )

    for samples, region, histograms in zip( [ samples_region_1, samples_region_2], [control_region_1, control_region_2], [histograms_region1, histograms_region2]):
        if samples == 'data':
            del histograms['TTJet']
            del histograms['V+Jets']
            del histograms['QCD']
            del histograms['SingleTop']
        elif samples == 'MC':
            del histograms['data']
            histograms['MC'] = { region : Hist() }
            for h in histograms:
                print h, histograms[h]
                histograms['MC'][''] += histograms[h][region]

    prepare_histograms( histograms_region1, rebin = rebin, scale_factor = measurement_config.luminosity_scale )
    prepare_histograms( histograms_region2, rebin = rebin, scale_factor = measurement_config.luminosity_scale )

    print histograms_region1
    print histograms_region2
    
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
              signal_region_tree,
              control_region_tree,
              branchName,
              name_prefix, x_limits, nBins,
              use_qcd_data_region = False,
              compare_qcd_signal_with_data_control = False,
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

    # Input files, normalisations, tree/region names
    qcd_data_region = ''
    title = title_template % ( measurement_config.new_luminosity, measurement_config.centre_of_mass_energy )
    normalisation = None
    if 'electron' in channel:
        histogram_files['data'] = measurement_config.data_file_electron_trees
        histogram_files['QCD'] = measurement_config.electron_QCD_MC_category_templates_trees[category]
        if normalise_to_fit:
            normalisation = normalisations_electron[norm_variable]
        if use_qcd_data_region:
            qcd_data_region = 'QCDConversions'
    if 'muon' in channel:
        histogram_files['data'] = measurement_config.data_file_muon_trees
        histogram_files['QCD'] = measurement_config.muon_QCD_MC_category_templates_trees[category]
        if normalise_to_fit:
            normalisation = normalisations_muon[norm_variable]
        if use_qcd_data_region:
            qcd_data_region = 'QCD non iso mu+jets ge3j'

    # Get all histograms
    # multi = isinstance( signal_region, list )
    # histograms = {}
    # qcd_control_region = ''
    # if multi:
    #     signal_region_sum = signal_region[0].replace( '_bin_' + sum_bins[0], '' )
    #     qcd_control_region_sum = signal_region_sum.replace( 'Ref selection', qcd_data_region )
    #     qcd_control_region_sum = qcd_control_region_sum.replace( b_tag_bin, qcd_data_region_btag )
    #     for region in signal_region:
    #         qcd_control_region = region.replace( 'Ref selection', qcd_data_region )
    #         qcd_control_region = qcd_control_region.replace( b_tag_bin, qcd_data_region_btag )
    #         tmp_hists = get_histograms_from_files( [region, qcd_control_region], histogram_files )
    #         for name in tmp_hists.keys():
    #             if not histograms.has_key( name ):
    #                 histograms[name] = {}
    #                 histograms[name][signal_region_sum] = tmp_hists[name][region]
    #                 histograms[name][qcd_control_region_sum] = tmp_hists[name][qcd_control_region]
    #             else:
    #                 histograms[name][signal_region_sum] += tmp_hists[name][region]
    #                 histograms[name][qcd_control_region_sum] += tmp_hists[name][qcd_control_region]
    #     signal_region = signal_region_sum
    #     qcd_control_region = qcd_control_region_sum
    # else:
    #     qcd_control_region = signal_region.replace( 'Ref selection', qcd_data_region )
    #     qcd_control_region = qcd_control_region.replace( b_tag_bin, qcd_data_region_btag )
    #     if qcd_data_region:
    #         histograms = get_histograms_from_files( [signal_region, qcd_control_region], histogram_files )
    #     else:
    #         histograms = get_histograms_from_files( [signal_region], histogram_files )
    histograms = get_histograms_from_trees( trees = [signal_region_tree, control_region_tree], branch = branchName, weightBranch = 'EventWeight', files = histogram_files, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1] )

    # Split histograms up into signal/control (?)
    signal_region_hists = {}
    inclusive_control_region_hists = {}
    for sample in histograms.keys():
        signal_region_hists[sample] = histograms[sample][signal_region_tree]

        if compare_qcd_signal_with_data_control:
            if sample is 'data':
                signal_region_hists[sample] = histograms[sample][control_region_tree]
            elif sample is 'QCD' :
                signal_region_hists[sample] = histograms[sample][signal_region_tree]
            else:
                del signal_region_hists[sample]

        if use_qcd_data_region:
            inclusive_control_region_hists[sample] = histograms[sample][control_region_tree]

    # Prepare histograms
    if normalise_to_fit:
        # only scale signal region to fit (results are invalid for control region)
        prepare_histograms( signal_region_hists, rebin = rebin,
                            scale_factor = measurement_config.luminosity_scale,
                            normalisation = normalisation )
    elif normalise_to_data:
        totalMC = 0
        for sample in signal_region_hists:
            totalMC += signal_region_hists[sample].Integral()
        newScale = signal_region_hists['data'].Integral() / totalMC
        prepare_histograms( signal_region_hists, rebin = rebin,
                            scale_factor = newScale,
                            )        
    else:
        prepare_histograms( signal_region_hists, rebin = rebin,
                            scale_factor = measurement_config.luminosity_scale )
    prepare_histograms( inclusive_control_region_hists, rebin = rebin,
                            scale_factor = measurement_config.luminosity_scale )

    # Use qcd from data control region or not
    qcd_from_data = None
    if use_qcd_data_region:
        qcd_from_data = clean_control_region( inclusive_control_region_hists,
                          subtract = ['TTJet', 'V+Jets', 'SingleTop'] )
        # Normalise contorl region correctly
        n_qcd_predicted_mc = histograms['QCD'][signal_region_tree].Integral()
        n_qcd_control_region = qcd_from_data.Integral()
        if not n_qcd_control_region == 0:
            qcd_from_data.Scale( 1.0 / n_qcd_control_region * n_qcd_predicted_mc )
    else:
        qcd_from_data = signal_region_hists['QCD']

    # Which histograms to draw, and properties
    histograms_to_draw = []
    histogram_lables = []
    histogram_colors = []

    if compare_qcd_signal_with_data_control :
        histograms_to_draw = [signal_region_hists['data'], qcd_from_data ]
        histogram_lables = ['data', 'QCD']
        histogram_colors = ['black', 'yellow']
    else :
        histograms_to_draw = [signal_region_hists['data'], qcd_from_data,
                              signal_region_hists['V+Jets'],
                              signal_region_hists['SingleTop'],
                              signal_region_hists['TTJet']]
        histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
        histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']

    # # # if channel == 'electron':
    # if compare_qcd_signal_with_data_control:
    #     histograms_to_draw.remove(signal_region_hists['V+Jets'])
    #     histograms_to_draw.remove(signal_region_hists['SingleTop'])
    #     histograms_to_draw.remove(signal_region_hists['TTJet'])

    #     histogram_lables.remove('V+Jets')
    #     histogram_lables.remove('Single-Top')
    #     histogram_lables.remove(samples_latex['TTJet'])

    #     histogram_colors.remove('green')
    #     histogram_colors.remove('magenta')
    #     histogram_colors.remove('red')

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

    # if normalise_to_fit:
    #     histogram_properties.mc_error = get_normalisation_error( normalisation )
    #     histogram_properties.mc_errors_label = 'fit uncertainty'
    # else:
    #     histogram_properties.mc_error = mc_uncertainty
    #     histogram_properties.mc_errors_label = 'MC unc.'


    if normalise_to_data:
            histogram_properties.name += '_normToData'

    # Actually draw histograms
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
    parser.add_option( "-p", "--path", dest = "path", default = 'data/M3_angle_bl/',
                  help = "set path to JSON files" )
    parser.add_option( "-o", "--output_folder", dest = "output_folder", default = 'plots/control_plots/',
                  help = "set path to save plots" )
    parser.add_option( "-m", "--metType", dest = "metType", default = 'type1',
                      help = "set MET type used in the analysis of MET-dependent variables" )
    parser.add_option( "-c", "--centre-of-mass-energy", dest = "CoM", default = 13, type = int,
                      help = "set the centre of mass energy for analysis. Default = 13 [TeV]" )
    parser.add_option( "--category", dest = "category", default = 'central',
                      help = "set the category to take the fit results from (default: central)" )
    parser.add_option( "-n", "--normalise_to_fit", dest = "normalise_to_fit", action = "store_true",
                  help = "normalise the MC to fit results" )
    parser.add_option( "-d", "--normalise_to_data", dest = "normalise_to_data", action = "store_true",
                  help = "normalise the MC to data" )
    parser.add_option( "-a", "--additional-plots", action = "store_true", dest = "additional_QCD_plots",
                      help = "creates a set of QCD plots for exclusive bins for all variables" )

    ( options, args ) = parser.parse_args()
    measurement_config = XSectionConfig( options.CoM )
    # caching of variables for shorter access
    translate_options = measurement_config.translate_options
    
    path_to_JSON = '%s/%dTeV/' % ( options.path, measurement_config.centre_of_mass_energy )
    normalise_to_fit = options.normalise_to_fit
    normalise_to_data = options.normalise_to_data
    if normalise_to_fit:
        output_folder = '%s/after_fit/%dTeV/' % ( options.output_folder, measurement_config.centre_of_mass_energy )
    else:
        output_folder = '%s/before_fit/%dTeV/' % ( options.output_folder, measurement_config.centre_of_mass_energy )
    make_folder_if_not_exists( output_folder )
    output_folder_base = output_folder
    category = options.category
    met_type = translate_options[options.metType]
    make_additional_QCD_plots = options.additional_QCD_plots

    # this is shown as \ttbar (or MC) uncertainty on the plots
    # in fact, it takes the uncertainty on the whole MC stack
    # although unimportant, this needs revision
    mc_uncertainty = 0.10
    
    histogram_files = {
            'TTJet': measurement_config.ttbar_category_templates_trees[category],
            'V+Jets': measurement_config.VJets_category_templates_trees[category],
            'QCD': measurement_config.electron_QCD_MC_category_templates_trees[category],
            'SingleTop': measurement_config.SingleTop_category_templates_trees[category],
    }

    # getting normalisations
    normalisations_electron = {
            # 'MET':get_fitted_normalisation( 'MET', 'electron', path_to_JSON, category, met_type ),
            # 'HT':get_fitted_normalisation( 'HT', 'electron', path_to_JSON, category, met_type ),
            # 'ST':get_fitted_normalisation( 'ST', 'electron', path_to_JSON, category, met_type ),
            # 'MT':get_fitted_normalisation( 'MT', 'electron', path_to_JSON, category, met_type ),
            # 'WPT':get_fitted_normalisation( 'WPT', 'electron', path_to_JSON, category, met_type )
            }
    normalisations_muon = {
            # 'MET':get_fitted_normalisation( 'MET', 'muon', path_to_JSON, category, met_type ),
            # 'HT':get_fitted_normalisation( 'HT', 'muon', path_to_JSON, category, met_type ),
            # 'ST':get_fitted_normalisation( 'ST', 'muon', path_to_JSON, category, met_type ),
            # 'MT':get_fitted_normalisation( 'MT', 'muon', path_to_JSON, category, met_type ),
            # 'WPT':get_fitted_normalisation( 'WPT', 'muon', path_to_JSON, category, met_type )
            }
    preliminary = True
    
    b_tag_bin = '2orMoreBtags'
    norm_variable = 'MET'
    # comment out plots you don't want
    include_plots = [
                        # 'HT',
                        # 'MET',
                        # 'ST',
                        # 'WPT',
                        # 'Mjj',
                        # 'M3',
                        # 'angle_bl',
                        # 'NJets',
                        # 'NBJets',
                        # 'JetPt',
                        # 'NVertex',
                        # 'LeptonPt',
                        # 'LeptonEta',
                        # 'QCDHT',
                        # 'QCDMET',
                        # 'QCDST',
                        # 'QCDWPT',
                        'QCDLeptonEta',
                        # 'QCDRelIso',
                        # 'QCDHT_dataControl_mcSignal',
                        ]
    print include_plots
    additional_qcd_plots = [
                            ]
    if make_additional_QCD_plots:
        include_plots.extend( additional_qcd_plots )


    for channel, label in {
                            'electron' : 'EPlusJets', 
                            'muon' : 'MuPlusJets'
                            }.iteritems() :
        # Set folder for this batch of plots
        output_folder = output_folder_base + "/Variables/"
        make_folder_if_not_exists(output_folder)

        ###################################################
        # HT
        ###################################################
        norm_variable = 'HT'
        if 'HT' in include_plots:
            print '---> HT'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['HT'],
                      y_axis_title = 'Events/(20 GeV)',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'HT',
                      name_prefix = '%s_HT_' % label,
                      x_limits = bin_edges['HT'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        ###################################################
        # MET
        ###################################################
        norm_variable = 'MET'
        if 'MET' in include_plots:
            print '---> MET'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['MET'],
                      y_axis_title = 'Events/(20 GeV)',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'MET',
                      name_prefix = '%s_MET_' % label,
                      x_limits = bin_edges['MET'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        ###################################################
        # ST
        ###################################################
        norm_variable = 'ST'
        if 'ST' in include_plots:
            print '---> ST'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['ST'],
                      y_axis_title = 'Events/(20 GeV)',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'ST',
                      name_prefix = '%s_ST_' % label,
                      x_limits = bin_edges['ST'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        ###################################################
        # WPT
        ###################################################
        norm_variable = 'WPT'
        if 'WPT' in include_plots:
            print '---> WPT'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['WPT'],
                      y_axis_title = 'Events/(20 GeV)',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'WPT',
                      name_prefix = '%s_WPT_' % label,
                      x_limits = bin_edges['WPT'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        # Set folder for this batch of plots
        output_folder =  output_folder_base + "/FitVariables/"
        make_folder_if_not_exists(output_folder)

        ###################################################
        # Mjj
        ###################################################
        if 'Mjj' in include_plots:
            print '---> Mjj'
            make_plot( channel,
                      x_axis_title = 'M(jj) [GeV]',
                      y_axis_title = 'Events/(X GeV)',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/W Bosons/W Bosons' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/W Bosons/W Bosons' % label,
                      branchName = 'mjj',
                      name_prefix = '%s_mjj_' % label,
                      x_limits = fit_variable_bin_edges['Mjj'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        ###################################################
        # M3
        ###################################################
        if 'M3' in include_plots:
            print '---> M3'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % fit_variables_latex['M3'],
                      y_axis_title = 'Events/(X GeV)',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'M3',
                      name_prefix = '%s_M3_' % label,
                      x_limits = fit_variable_bin_edges['M3'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        ###################################################
        # angle_bl
        ###################################################
        if 'angle_bl' in include_plots:
            print '---> angle_bl'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % fit_variables_latex['angle_bl'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'angle_bl',
                      name_prefix = '%s_angle_bl_' % label,
                      x_limits = fit_variable_bin_edges['angle_bl'],
                      nBins = 10,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        # Set folder for this batch of plots
        output_folder =  output_folder_base + "/Control/"
        make_folder_if_not_exists(output_folder)

        ###################################################
        # NJets
        ###################################################
        if 'NJets' in include_plots:
            print '---> NJets'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NJets'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/Jets/Jets' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/Jets/Jets' % label,
                      branchName = 'NJets',
                      name_prefix = '%s_NJets_' % label,
                      x_limits = control_plots_bins['NJets'],
                      nBins = len(control_plots_bins['NJets'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NJets'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/Jets/Jets' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/Jets/Jets' % label,
                      branchName = 'NJets',
                      name_prefix = '%s_NJets_logY_' % label,
                      x_limits = control_plots_bins['NJets'],
                      nBins = len(control_plots_bins['NJets'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      log_y = True,
                      )
        ###################################################
        # NBJets
        ###################################################
        if 'NBJets' in include_plots:
            print '---> NBJets'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NBJets'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/Jets/Jets' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/Jets/Jets' % label,
                      branchName = 'NBJets',
                      name_prefix = '%s_NBJets_' % label,
                      x_limits = control_plots_bins['NBJets'],
                      nBins = len(control_plots_bins['NBJets'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NBJets'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/Jets/Jets' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/Jets/Jets' % label,
                      branchName = 'NBJets',
                      name_prefix = '%s_NBJets_logY_' % label,
                      x_limits = control_plots_bins['NBJets'],
                      nBins = len(control_plots_bins['NBJets'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      log_y = True,
                      )
        ###################################################
        # Jet Pt
        ###################################################
        if 'JetPt' in include_plots:
            print '---> Jet Pt'
            treeName = 'Electron/Electrons'
            if channel == 'muon':
                treeName = 'Muon/Muons'

            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['pt'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/Jets/Jets' % ( label ),
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/Jets/Jets' % (label ),
                      branchName = 'pt',
                      name_prefix = '%s_JetPt_' % label,
                      x_limits = control_plots_bins['JetPt'],
                      nBins = len(control_plots_bins['JetPt'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )
        ###################################################
        # NVertex
        ###################################################
        if 'NVertex' in include_plots:
            print '---> NVertex'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NVertex'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/W Bosons/W Bosons' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/W Bosons/W Bosons' % label,
                      branchName = 'NPU',
                      name_prefix = '%s_NPU_' % label,
                      x_limits = control_plots_bins['NVertex'],
                      nBins = len(control_plots_bins['NVertex'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )
        ###################################################
        # Lepton Pt
        ###################################################
        if 'LeptonPt' in include_plots:
            print '---> Lepton Pt'
            treeName = 'Electron/Electrons'
            if channel == 'muon':
                treeName = 'Muon/Muons'

            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['pt'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/%s' % ( label, treeName),
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/%s' % (label, treeName),
                      branchName = 'pt',
                      name_prefix = '%s_LeptonPt_' % label,
                      x_limits = control_plots_bins['LeptonPt'],
                      nBins = len(control_plots_bins['LeptonPt'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )
        ###################################################
        # Lepton Eta
        ###################################################
        if 'LeptonEta' in include_plots:
            print '---> Lepton Eta'
            treeName = 'Electron/Electrons'
            if channel == 'muon':
                treeName = 'Muon/Muons'

            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['eta'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/%s' % ( label, treeName),
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/%s' % (label, treeName),
                      branchName = 'eta',
                      name_prefix = '%s_LeptonEta_' % label,
                      x_limits = control_plots_bins['LeptonEta'],
                      nBins = len(control_plots_bins['LeptonEta'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

    ###################################################
    # QCD Control Region
    ###################################################
    for channel, label in {
                            'electronQCDNonIso' : 'EPlusJets/QCD non iso e+jets',
                            'electronQCDConversions' : 'EPlusJets/QCDConversions', 
                            'muonQCDNonIso' : 'MuPlusJets/QCD non iso mu+jets'
                            }.iteritems() :
        # Set folder for this batch of plots
        output_folder = output_folder_base + "QCDControl/Variables/%s/" % channel
        make_folder_if_not_exists(output_folder)

        print 'Control region :',label

        treeName = 'EPlusJets/QCD non iso e+jets'
        signalTreeName = 'EPlusJets/Ref selection'
        if channel == 'electronQCDConversions':
            treeName = 'EPlusJets/QCDConversions'
        elif channel == 'muonQCDNonIso':
            treeName = 'MuPlusJets/QCD non iso mu+jets'
            signalTreeName = 'MuPlusJets/Ref selection'

        ###################################################
        # HT
        ###################################################
        norm_variable = 'HT'
        if 'QCDHT' in include_plots:
            print '---> QCD HT'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['HT'],
                      y_axis_title = 'Events/(20 GeV)',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      branchName = 'HT',
                      name_prefix = '%s_HT_' % channel,
                      x_limits = bin_edges['HT'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        if 'QCDHT_dataControl_mcSignal' in include_plots:
            print '---> QCD HT data to signal QCD'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['HT'],
                      y_axis_title = 'Events/(20 GeV)',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % signalTreeName,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      compare_qcd_signal_with_data_control = True,
                      branchName = 'HT',
                      name_prefix = '%s_HT_' % channel,
                      x_limits = bin_edges['HT'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        ###################################################
        # MET
        ###################################################
        norm_variable = 'MET'
        if 'QCDMET' in include_plots:
            print '---> QCD MET'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['MET'],
                      y_axis_title = 'Events/(20 GeV)',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      branchName = 'MET',
                      name_prefix = '%s_MET_' % channel,
                      x_limits = bin_edges['MET'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        ###################################################
        # ST
        ###################################################
        norm_variable = 'ST'
        if 'QCDST' in include_plots:
            print '---> QCD ST'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['ST'],
                      y_axis_title = 'Events/(20 GeV)',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      branchName = 'ST',
                      name_prefix = '%s_ST_' % channel,
                      x_limits = bin_edges['ST'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        ###################################################
        # WPT
        ###################################################
        norm_variable = 'WPT'
        if 'QCDWPT' in include_plots:
            print '---> QCD WPT'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['WPT'],
                      y_axis_title = 'Events/(20 GeV)',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      branchName = 'WPT',
                      name_prefix = '%s_WPT_' % channel,
                      x_limits = bin_edges['WPT'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        # Set folder for this batch of plots
        output_folder =  output_folder_base + "QCDControl/Control/%s" % channel
        make_folder_if_not_exists(output_folder)
        ###################################################
        # Lepton Pt
        ###################################################
        if 'QCDLeptonEta' in include_plots:
            print '---> QCD Lepton Eta'
            channelTreeName = 'Electron/Electrons'
            if channel == 'muonQCDNonIso':
                channelTreeName = 'Muon/Muons'

            make_plot( channel,
                      x_axis_title = '$%s$' % fit_variables_latex['absolute_eta'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/%s' % ( treeName, channelTreeName),
                      control_region_tree = 'TTbar_plus_X_analysis/%s/%s' % ( treeName, channelTreeName),
                      branchName = 'fabs(eta)',
                      name_prefix = '%s_LeptonEta_' % channel,
                      x_limits = control_plots_bins['AbsLeptonEta'],
                      nBins = len(control_plots_bins['AbsLeptonEta'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )


        ###################################################
        # Rel iso
        ###################################################
        if 'QCDRelIso' in include_plots:
            if channel != 'muonQCDNonIso': 
                print '---> QCD Rel iso'
                channelTreeName = 'Electron/Electrons'
                if channel == 'muonQCDNonIso':
                    channelTreeName = 'Muon/Muons'

                make_plot( channel,
                          x_axis_title = '$%s$' % control_plots_latex['relIso'],
                          y_axis_title = 'Events',
                          signal_region_tree = 'TTbar_plus_X_analysis/%s/%s' % ( treeName, channelTreeName),
                          control_region_tree = 'TTbar_plus_X_analysis/%s/%s' % ( treeName, channelTreeName),
                          branchName = 'relIso_03_deltaBeta',
                          name_prefix = '%s_relIso_' % channel,
                          x_limits = control_plots_bins['relIso'],
                          nBins = len(control_plots_bins['relIso'])-1,
                          rebin = 1,
                          legend_location = ( 0.95, 0.78 ),
                          cms_logo_location = 'right',
                          )            