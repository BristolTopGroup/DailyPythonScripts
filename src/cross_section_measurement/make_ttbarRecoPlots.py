from optparse import OptionParser
from config.latex_labels import b_tag_bins_latex, samples_latex, channel_latex, \
    variables_latex, fit_variables_latex, control_plots_latex
from config.variable_binning import variable_bins_ROOT, bin_edges_vis, control_plots_bins
from config import XSectionConfig
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from tools.plotting import make_data_mc_comparison_plot, Histogram_properties, \
make_control_region_comparison
from tools.hist_utilities import prepare_histograms, clean_control_region, get_normalisation_error, get_fitted_normalisation
from tools.ROOT_utils import get_histograms_from_trees, set_root_defaults
from tools.latex import setup_matplotlib
# latex, font, etc
setup_matplotlib()

def make_ttbarReco_plot( channel, x_axis_title, y_axis_title,
              signal_region_tree,
              control_region_tree,
              branchName,
              name_prefix, x_limits, nBins,
              use_qcd_data_region = False,
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
    title = title_template % ( measurement_config.new_luminosity / 1000., measurement_config.centre_of_mass_energy )
    normalisation = None
    if channel == 'electron':
        histogram_files['data'] = measurement_config.data_file_electron_trees
        histogram_files['QCD'] = measurement_config.electron_QCD_MC_category_templates_trees[category]
        if normalise_to_fit:
            normalisation = normalisations_electron[norm_variable]
        if use_qcd_data_region:
            qcd_data_region = 'QCDConversions'
    if channel == 'muon':
        histogram_files['data'] = measurement_config.data_file_muon_trees
        histogram_files['QCD'] = measurement_config.muon_QCD_MC_category_templates_trees[category]
        if normalise_to_fit:
            normalisation = normalisations_muon[norm_variable]
        if use_qcd_data_region:
            qcd_data_region = 'QCD non iso mu+jets ge3j'

    histograms = get_histograms_from_trees( trees = [signal_region_tree, control_region_tree], branch = branchName, weightBranch = '1', files = histogram_files, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1] )

    selection = 'SolutionCategory == 0'
    histogramsNoSolution = get_histograms_from_trees( trees = [signal_region_tree], branch = branchName, weightBranch = '1', selection = selection, files = histogram_files, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1] )

    selection = 'SolutionCategory == 1'
    histogramsCorrect = get_histograms_from_trees( trees = [signal_region_tree], branch = branchName, weightBranch = '1', selection = selection, files = histogram_files, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1] )

    selection = 'SolutionCategory == 2'
    histogramsNotSL = get_histograms_from_trees( trees = [signal_region_tree], branch = branchName, weightBranch = '1', selection = selection, files = histogram_files, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1] )

    selection = 'SolutionCategory == 3'
    histogramsNotReco = get_histograms_from_trees( trees = [signal_region_tree], branch = branchName, weightBranch = '1', selection = selection, files = histogram_files, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1] )

    selection = 'SolutionCategory > 3'
    histogramsWrong = get_histograms_from_trees( trees = [signal_region_tree], branch = branchName, weightBranch = '1', selection = selection, files = histogram_files, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1] )

    # Split histograms up into signal/control (?)
    signal_region_hists = {}
    inclusive_control_region_hists = {}
    for sample in histograms.keys():
        signal_region_hists[sample] = histograms[sample][signal_region_tree]
        if use_qcd_data_region:
            inclusive_control_region_hists[sample] = histograms[sample][control_region_tree]

    prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
    prepare_histograms( histogramsNoSolution, rebin = 1, scale_factor = measurement_config.luminosity_scale )
    prepare_histograms( histogramsCorrect, rebin = 1, scale_factor = measurement_config.luminosity_scale )
    prepare_histograms( histogramsNotSL, rebin = 1, scale_factor = measurement_config.luminosity_scale )
    prepare_histograms( histogramsNotReco, rebin = 1, scale_factor = measurement_config.luminosity_scale )
    prepare_histograms( histogramsWrong, rebin = 1, scale_factor = measurement_config.luminosity_scale )

    qcd_from_data = signal_region_hists['QCD']

    # Which histograms to draw, and properties
    histograms_to_draw = [signal_region_hists['data'], qcd_from_data,
                          signal_region_hists['V+Jets'],
                          signal_region_hists['SingleTop'],
                          histogramsNoSolution['TTJet'][signal_region_tree],
                          histogramsNotSL['TTJet'][signal_region_tree],
                          histogramsNotReco['TTJet'][signal_region_tree],
                          histogramsWrong['TTJet'][signal_region_tree],
                          histogramsCorrect['TTJet'][signal_region_tree]
                          ]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', 
                        samples_latex['TTJet'] + ' - no solution',
                        samples_latex['TTJet'] + ' - not SL',
                        samples_latex['TTJet'] + ' - not reconstructible',
                        samples_latex['TTJet'] + ' - wrong reco',
                        samples_latex['TTJet'] + ' - correct',
                        ]
    histogram_colors = ['black', 'yellow', 'green', 'magenta',
                        'black',
                        'burlywood',
                        'chartreuse',
                        'blue',
                        'red'
                        ]

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
    if normalise_to_fit:
        normalisations_electron = {
                'lepTopPt':get_fitted_normalisation( 'lepTopPt', 'electron', path_to_JSON, category, 'patType1CorrectedPFMet' ),
        }

        normalisations_muon = {
                'lepTopPt':get_fitted_normalisation( 'lepTopPt', 'muon', path_to_JSON, category, 'patType1CorrectedPFMet' ),
        }

    title_template = '$%.1f$ fb$^{-1}$ (%d TeV)'
    e_title = title_template % ( measurement_config.new_luminosity / 1000., measurement_config.centre_of_mass_energy )
    preliminary = True
    
    b_tag_bin = '2orMoreBtags'
    norm_variable = 'lepTopPt'
    # comment out plots you don't want
    include_plots = [
                        'chi2p',
                        'solutionCategory',
                        'lepTopPt',
                        'ttbarRap',
                        ]
    additional_qcd_plots = [
                            ]
    if make_additional_QCD_plots:
        include_plots.extend( additional_qcd_plots )


    for channel, label in {'electron' : 'EPlusJets', 
                            'muon' : 'MuPlusJets'
                            }.iteritems() :
        # Set folder for this batch of plots
        output_folder = output_folder_base + "/HitFit/"
        make_folder_if_not_exists(output_folder)

        ###################################################
        # Chi2 probability of second fit
        ###################################################
        norm_variable = 'chi2p'
        if 'chi2p' in include_plots:
            make_ttbarReco_plot( channel,
                      x_axis_title = '#Chi^{2}-probability',
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/HitFit/HitFit' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/HitFit/HitFit' % label,
                      branchName = 'FitChiSquaredProbabilityBestSolutions_second',
                      name_prefix = '%s_chi2p_' % label,
                      x_limits = [0,1],
                      nBins = 30,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

            make_ttbarReco_plot( channel,
                      x_axis_title = '#Chi^{2}-probability',
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/HitFit/HitFit' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/HitFit/HitFit' % label,
                      branchName = 'FitChiSquaredProbabilityBestSolutions_second',
                      name_prefix = '%s_chi2p_logy_' % label,
                      x_limits = [0,1],
                      nBins = 30,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      log_y = True,
                      )

        ###################################################
        # Chi2 probability of second fit
        ###################################################
        norm_variable = 'solutionCategory'
        if 'solutionCategory' in include_plots:
            make_ttbarReco_plot( channel,
                      x_axis_title = 'Solution Category',
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/HitFit/HitFit' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/HitFit/HitFit' % label,
                      branchName = 'SolutionCategory_second',
                      name_prefix = '%s_solutionCategory_' % label,
                      x_limits = [-0.5,9.5],
                      nBins = 10,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        ###################################################
        # lepTopPt
        ###################################################
        norm_variable = 'lepTopPt'
        if 'lepTopPt' in include_plots:
            make_ttbarReco_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['lepTopPt'],
                      y_axis_title = 'Events/(20 GeV)',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'lepTopPt',
                      name_prefix = '%s_lepTopPt_' % label,
                      x_limits = bin_edges_vis['lepTopPt'],
                      nBins = 30,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        ###################################################
        # ttbarRap
        ###################################################
        norm_variable = 'ttbarRap'
        if 'ttbarRap' in include_plots:
            make_ttbarReco_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['ttbarRap'],
                      y_axis_title = 'Events/(20 GeV)',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'ttbarRap',
                      name_prefix = '%s_ttbarRap_' % label,
                      x_limits = bin_edges_vis['ttbarRap'],
                      nBins = 30,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )