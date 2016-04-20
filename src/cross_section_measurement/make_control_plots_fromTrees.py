from optparse import OptionParser
from config.latex_labels import b_tag_bins_latex, samples_latex, channel_latex, \
    variables_latex, fit_variables_latex, control_plots_latex
from config.variable_binning import fit_variable_bin_edges, control_plots_bins
from config.histogram_colours import histogram_colours as colours
from config import XSectionConfig
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from tools.plotting import make_data_mc_comparison_plot, Histogram_properties, \
    make_control_region_comparison
from tools.plotting  import make_plot as make_plot_tmp
from rootpy.plotting import Hist
from tools.hist_utilities import prepare_histograms, clean_control_region, get_normalisation_error, get_fitted_normalisation
from tools.ROOT_utils import get_histograms_from_trees, set_root_defaults
from tools.latex import setup_matplotlib
from uncertainties import ufloat
from math import sqrt
from copy import deepcopy

# latex, font, etc
setup_matplotlib()

title_template = '$%.1f$ fb$^{-1}$ (%d TeV)'

def binWidth(binning):
    return  ( binning[-1] - binning[0] ) / ( len(binning)-1 )


def getHistograms( histogram_files,
                   signal_region_tree,
                   use_qcd_data_region,
                   channel,
                   branchName,
                   weightBranchSignalRegion,
                   nBins,
                   rebin,
                   x_limits ):
    global measurement_config

    # Names of QCD regions to use
    qcd_data_region = ''
    qcd_data_region_electron = 'QCDConversions'
    qcd_data_region_muon = 'QCD non iso mu+jets 3toInf'
    
    # Channel specific files and weights
    if 'electron' in channel:
        histogram_files['data'] = measurement_config.data_file_electron_trees
        histogram_files['QCD'] = measurement_config.electron_QCD_MC_category_templates_trees[category]
        if normalise_to_fit:
            normalisation = normalisations_electron[norm_variable]
        if use_qcd_data_region:
            qcd_data_region = qcd_data_region_electron
        if not 'QCD' in channel and not 'NPU' in branchName:
            weightBranchSignalRegion += ' * ElectronEfficiencyCorrection'
    if 'muon' in channel:
        histogram_files['data'] = measurement_config.data_file_muon_trees
        histogram_files['QCD'] = measurement_config.muon_QCD_MC_category_templates_trees[category]
        if normalise_to_fit:
            normalisation = normalisations_muon[norm_variable]
        if use_qcd_data_region:
            qcd_data_region = qcd_data_region_muon
        if not 'QCD' in channel:
            weightBranchSignalRegion += ' * MuonEfficiencyCorrection'
    print weightBranchSignalRegion

    # Apply selection to avoid non-physical values
    if branchName == 'abs(lepton_eta)' :
        selection = 'lepton_eta > -10'
    else:
        selection = '%s >= 0' % branchName

    histograms = {}
    histograms_QCDControlRegion = {}
    # Get histograms for combined channel
    if channel == 'combined':
        histogram_files_electron = dict(histogram_files)
        histogram_files_electron['data'] = measurement_config.data_file_electron_trees
        histogram_files_electron['QCD'] = measurement_config.electron_QCD_MC_category_templates_trees[category]

        histogram_files_muon = dict(histogram_files)
        histogram_files_muon['data'] = measurement_config.data_file_muon_trees
        histogram_files_muon['QCD'] = measurement_config.muon_QCD_MC_category_templates_trees[category]

        histograms_electron = get_histograms_from_trees( trees = [signal_region_tree.replace('COMBINED','EPlusJets')], branch = branchName, weightBranch = weightBranchSignalRegion + ' * ElectronEfficiencyCorrection', files = histogram_files_electron, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1], selection = selection )
        histograms_muon = get_histograms_from_trees( trees = [signal_region_tree.replace('COMBINED','MuPlusJets')], branch = branchName, weightBranch = weightBranchSignalRegion + ' * MuonEfficiencyCorrection', files = histogram_files_muon, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1], selection = selection )
        # histograms_muon = get_histograms_from_trees( trees = [signal_region_tree.replace('COMBINED','MuPlusJets')], branch = branchName, weightBranch = weightBranchSignalRegion, files = histogram_files_muon, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1], selection = selection )
        # histograms_electron = get_histograms_from_trees( trees = [signal_region_tree.replace('COMBINED','EPlusJets')], branch = branchName, weightBranch = weightBranchSignalRegion, files = histogram_files_electron, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1], selection = selection )

        if use_qcd_data_region:
            qcd_control_region = signal_region_tree.replace('Ref selection','QCD_Control')
            qcd_control_region_electron = signal_region_tree.replace( 'Ref selection', qcd_data_region_electron ).replace('COMBINED','EPlusJets')
            histograms_electron_QCDControlRegion = get_histograms_from_trees( trees = [qcd_control_region_electron], branch = branchName, weightBranch = 'EventWeight', files = histogram_files_electron, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1], selection = selection )
            qcd_control_region_muon = signal_region_tree.replace( 'Ref selection', qcd_data_region_muon ).replace('COMBINED','MuPlusJets')
            histograms_muon_QCDControlRegion = get_histograms_from_trees( trees = [qcd_control_region_muon], branch = branchName, weightBranch = 'EventWeight', files = histogram_files_muon, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1], selection = selection )

        for sample in histograms_electron:
            h_electron = histograms_electron[sample][signal_region_tree.replace('COMBINED','EPlusJets')]
            h_muon = histograms_muon[sample][signal_region_tree.replace('COMBINED','MuPlusJets')]
            h_combined = h_electron + h_muon
            histograms[sample] = { signal_region_tree : h_combined}

            if use_qcd_data_region:
                h_qcd_electron = histograms_electron_QCDControlRegion[sample][qcd_control_region_electron]
                h_qcd_muon = histograms_muon_QCDControlRegion[sample][qcd_control_region_muon]
                h_qcd_combined = h_qcd_electron + h_qcd_muon
                histograms_QCDControlRegion[sample] = { qcd_control_region : h_qcd_combined }
    # Get hsitgorams for specific channel
    else :
        histograms = get_histograms_from_trees( trees = [signal_region_tree], branch = branchName, weightBranch = weightBranchSignalRegion, files = histogram_files, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1], selection = selection )
        if use_qcd_data_region:
            qcd_control_region = signal_region_tree.replace( 'Ref selection', qcd_data_region )
            histograms_QCDControlRegion = get_histograms_from_trees( trees = [qcd_control_region], branch = branchName, weightBranch = 'EventWeight', files = histogram_files, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1], selection = selection )

    # Technical step, don't need key for tree
    signal_region_hists = {}
    control_region_hists = {}
    for sample in histograms.keys():
        signal_region_hists[sample] = histograms[sample][signal_region_tree]

        if use_qcd_data_region:
            control_region_hists[sample] = histograms_QCDControlRegion[sample][qcd_control_region]

    # Prepare histograms
    if normalise_to_fit:
        # only scale signal region to fit (results are invalid for control region)
        prepare_histograms( signal_region_hists, rebin = rebin,
                            scale_factor = measurement_config.luminosity_scale,
                            normalisation = normalisation )
    elif normalise_to_data:
        totalMC = 0
        for sample in signal_region_hists:
            if sample is 'data' : continue
            totalMC += signal_region_hists[sample].Integral()
        newScale = signal_region_hists['data'].Integral() / totalMC

        prepare_histograms( signal_region_hists, rebin = rebin,
                            scale_factor = newScale,
                           )
    else:
        prepare_histograms( signal_region_hists, rebin = rebin,
                            scale_factor = measurement_config.luminosity_scale )
        prepare_histograms( control_region_hists, rebin = rebin,
                            scale_factor = measurement_config.luminosity_scale )

    # Use qcd from data control region or not
    qcd_from_data = None
    if use_qcd_data_region:
        qcd_from_data = clean_control_region( control_region_hists,

                          subtract = ['TTJet', 'V+Jets', 'SingleTop'] )
        # Normalise control region correctly
        nBins = signal_region_hists['QCD'].GetNbinsX()
        n, error = signal_region_hists['QCD'].integral(0,nBins+1,error=True)
        n_qcd_predicted_mc_signal = ufloat( n, error)

        n, error = control_region_hists['QCD'].integral(0,nBins+1,error=True)
        n_qcd_predicted_mc_control = ufloat( n, error)

        n, error = qcd_from_data.integral(0,nBins+1,error=True)
        n_qcd_control_region = ufloat( n, error)

        if not n_qcd_control_region == 0:
            dataDrivenQCDScale = n_qcd_predicted_mc_signal / n_qcd_predicted_mc_control
            qcd_from_data.Scale( dataDrivenQCDScale.nominal_value )
            # signalToControlScale = n_qcd_predicted_mc_signal / n_qcd_control_region
            # dataToMCscale = n_qcd_control_region / n_qcd_predicted_mc_control
    else:
        qcd_from_data = signal_region_hists['QCD']
        
    return signal_region_hists, control_region_hists, qcd_from_data

def make_plot( channel, x_axis_title, y_axis_title,
              signal_region_tree,
              control_region_tree,
              branchName,
              name_prefix, x_limits, nBins,
              use_qcd_data_region = False,
              y_limits = [],
              y_max_scale = 1.3,
              rebin = 1,
              legend_location = ( 0.98, 0.78 ), cms_logo_location = 'right',
              log_y = False,
              legend_color = False,
              ratio_y_limits = [0.5, 1.5],
              normalise = False,
              ):
    global output_folder, measurement_config, category, normalise_to_fit, showErrorBandOnRatio
    global preliminary, norm_variable, sum_bins, b_tag_bin, histogram_files

    # Lumi title of plots
    title = title_template % ( measurement_config.new_luminosity/1000, measurement_config.centre_of_mass_energy )
    normalisation = None

    # Define weights
    weightBranchSignalRegion = 'EventWeight'
    if not "_NPUNoWeight" in name_prefix:
        if '_NPUUp' in name_prefix: weightBranchSignalRegion += ' * PUWeight_up'
        elif '_NPUDown' in name_prefix: weightBranchSignalRegion += ' * PUWeight_down'
        else: weightBranchSignalRegion += ' * PUWeight'

    if not "_NBJetsNoWeight" in name_prefix:
        if '_NBJetsUp' in name_prefix: weightBranchSignalRegion += ' * BJetUpWeight'
        elif '_NBJetsDown' in name_prefix: weightBranchSignalRegion += ' * BJetDownWeight'
        elif '_NBJets_LightUp' in name_prefix: weightBranchSignalRegion += ' * LightJetUpWeight'
        elif '_NBJets_LightDown' in name_prefix: weightBranchSignalRegion += ' * LightJetDownWeight'
        else: weightBranchSignalRegion += ' * BJetWeight'
    # Get all histograms
    signal_region_hists, control_region_hists, qcd_from_data = getHistograms( histogram_files, signal_region_tree, use_qcd_data_region, channel, branchName, weightBranchSignalRegion, nBins, rebin, x_limits )


    # Which histograms to draw, and properties
    histograms_to_draw = []
    histogram_lables = []
    histogram_colors = []

    histograms_to_draw = [signal_region_hists['data'], 
                          qcd_from_data,
                          signal_region_hists['V+Jets'],
                          signal_region_hists['SingleTop'],
                          signal_region_hists['TTJet']]
    histogram_lables = ['data',
                        'QCD', 
                        'V+Jets', 
                        'Single-Top', 
                        samples_latex['TTJet']]
    histogram_colors = [colours['data'], 
                        colours['QCD'], 
                        colours['V+Jets'], 
                        colours['Single-Top'], 
                        colours['TTJet'] ]


    # Printout on normalisation of different samples
    print 'Normalisation after selection'
    print 'Data :',signal_region_hists['data'].integral(overflow=True)
    print 'TTJet :',signal_region_hists['TTJet'].integral(overflow=True)
    print 'Single Top :',signal_region_hists['SingleTop'].integral(overflow=True)
    print 'V+Jets :',signal_region_hists['V+Jets'].integral(overflow=True)
    print 'QCD :',qcd_from_data.integral(overflow=True)

    mcSum = signal_region_hists['TTJet'].integral(overflow=True) + signal_region_hists['SingleTop'].integral(overflow=True) + signal_region_hists['V+Jets'].integral(overflow=True) + qcd_from_data.integral(overflow=True)
    print 'Total MC :',mcSum

    # More histogram settings
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


    if branchName in ['NJets', 'NBJets', 'NBJetsNoWeight']:
        histogram_properties.integerXVariable = True

    # if normalise_to_fit:
    #     histogram_properties.mc_error = get_normalisation_error( normalisation )
    #     histogram_properties.mc_errors_label = 'fit uncertainty'

    if normalise_to_data:
            histogram_properties.name += '_normToData'
    output_folder_to_use = output_folder
    if use_qcd_data_region:
        output_folder_to_use += 'WithQCDFromControl/'
        make_folder_if_not_exists(output_folder_to_use)

    if branchName == 'NPU':
        getPUWeights(histograms_to_draw, histogram_lables)

    # Actually draw histograms
    # make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
    #                              histogram_properties, save_folder = output_folder_to_use,
    #                              show_ratio = False, normalise = normalise,
    #                              )
    # Draw same histogram, but with ratio plot
    histogram_properties.name += '_with_ratio'
    loc = histogram_properties.legend_location
    # adjust legend location as it is relative to canvas!
    histogram_properties.legend_location = ( loc[0], loc[1] + 0.05 )

    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder_to_use,
                                 show_ratio = True, normalise = normalise
                                  )
    print ("Plot written to : ", output_folder_to_use)
    # make_plot_tmp( qcd_from_data, histogram_properties, save_folder = output_folder_to_use+'test' )


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
    
    histogram_files = {
            'TTJet': measurement_config.ttbar_category_templates_trees[category],
            'V+Jets': measurement_config.VJets_category_templates_trees[category],
            'QCD': measurement_config.electron_QCD_MC_category_templates_trees[category],
            'SingleTop': measurement_config.SingleTop_category_templates_trees[category],
    }

    # Leftover from run1, when fit method was used
    # Leave implementation for now
    normalisations_electron = {
            }
    normalisations_muon = {
            }

    preliminary = True
    useQCDControl = True
    showErrorBandOnRatio = False
    b_tag_bin = '2orMoreBtags'
    norm_variable = 'MET'
    # comment out plots you don't want
    include_plots = [
                        'HT',
                        'MET',
                        'ST',
                        'WPT',
                        'NVertex',
                        'NVertexNoWeight',
                        'NVertexUp',
                        'NVertexDown',
                        'LeptonPt',
                        'AbsLeptonEta',
                        'NJets',
                        'NBJets',
                        'NBJetsNoWeight',
                        'NBJetsUp',
                        'NBJetsDown',
                        'NBJets_LightUp',
                        'NBJets_LightDown',
                        'JetPt',

                        # # # # # # # # 'Mjj',
                        # # # # # # # # 'M3',
                        # # # # # # # # 'angle_bl',
                        'RelIso',
                        # 'sigmaietaieta'
                        ]

    additional_qcd_plots = [
                        'QCDHT',
                        'QCDMET',
                        'QCDST',
                        'QCDWPT',
                        'QCDAbsLeptonEta',
                        'QCDLeptonPt',
                        'QCDNJets',

                        # 'QCDsigmaietaieta',
                        'QCDRelIso',
                        # 'QCDHT_dataControl_mcSignal',
                        ]

    if make_additional_QCD_plots:
        include_plots.extend( additional_qcd_plots )


    for channel, label in {
                            'electron' : 'EPlusJets', 
                            'muon' : 'MuPlusJets',
                            # 'combined' : 'COMBINED'
                            }.iteritems() :
        b_tag_bin = '2orMoreBtags'

        # Set folder for this batch of plots
        output_folder = output_folder_base + "/Variables/"
        make_folder_if_not_exists(output_folder)
        print '--->', channel
        ###################################################
        # HT
        ###################################################
        norm_variable = 'HT'
        if 'HT' in include_plots:
            print '---> HT'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['HT'],
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins['HT']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'HT',
                      name_prefix = '%s_HT_' % label,
                      x_limits = control_plots_bins['HT'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.9, 0.73 ),
                      cms_logo_location = 'left',
                      use_qcd_data_region = useQCDControl,
                      )

        ###################################################
        # MET
        ###################################################
        norm_variable = 'MET'
        if 'MET' in include_plots:
            print '---> MET'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['MET'],
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins['MET']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'MET',
                      name_prefix = '%s_MET_' % label,
                      x_limits = control_plots_bins['MET'],
                      nBins = len(control_plots_bins['MET'])-1,
                      rebin = 1,
                      legend_location = ( 0.9, 0.73 ),
                      cms_logo_location = 'left',
                      use_qcd_data_region = useQCDControl,
                      )

        ###################################################
        # ST
        ###################################################
        norm_variable = 'ST'
        if 'ST' in include_plots:
            print '---> ST'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['ST'],
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins['ST']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'ST',
                      name_prefix = '%s_ST_' % label,
                      x_limits = control_plots_bins['ST'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.9, 0.73 ),
                      cms_logo_location = 'left',
                      use_qcd_data_region = useQCDControl,
                      )

        ###################################################
        # WPT
        ###################################################
        norm_variable = 'WPT'
        if 'WPT' in include_plots:
            print '---> WPT'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['WPT'],
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins['WPT']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'WPT',
                      name_prefix = '%s_WPT_' % label,
                      x_limits = control_plots_bins['WPT'],
                      y_max_scale = 1.4,
                      nBins = 16,
                      rebin = 1,
                      legend_location = ( 0.9, 0.73 ),
                      cms_logo_location = 'left',
                      use_qcd_data_region = useQCDControl,
                      )

        ###################################################
        # Lepton Pt
        ###################################################
        if 'LeptonPt' in include_plots:
            print '---> Lepton Pt'
            binsLabel = 'ElectronPt'
            if channel == 'muon':
                binsLabel = 'MuonPt'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['pt'],
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins[binsLabel]),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % ( label ),
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % (label ),
                      branchName = 'lepton_pt',
                      name_prefix = '%s_LeptonPt_' % label,
                      x_limits = control_plots_bins[binsLabel],
                      nBins = len(control_plots_bins[binsLabel])-1,
                      rebin = 1,
                      legend_location = ( 0.9, 0.73 ),
                      cms_logo_location = 'left',
                      use_qcd_data_region = useQCDControl,
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
                      y_axis_title = 'Events/(%.1f)' % binWidth(control_plots_bins['LeptonEta']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/%s' % ( label, treeName),
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/%s' % (label, treeName),
                      branchName = 'lepton_eta',
                      name_prefix = '%s_LeptonEta_' % label,
                      x_limits = control_plots_bins['LeptonEta'],
                      nBins = len(control_plots_bins['LeptonEta'])-1,
                      rebin = 1,
                      legend_location = ( 0.9, 0.73 ),
                      cms_logo_location = 'right',
                      use_qcd_data_region = False,
                      )

        ###################################################
        # AbsLepton Eta
        ###################################################
        if 'AbsLeptonEta' in include_plots:
            print '---> Abs Lepton Eta'
            print output_folder
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['eta'],
                      y_axis_title = 'Events/(%.1f)' % binWidth(control_plots_bins['AbsLeptonEta']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % ( label ),
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % (label ),
                      branchName = 'abs(lepton_eta)',
                      name_prefix = '%s_AbsLeptonEta_' % label,
                      x_limits = control_plots_bins['AbsLeptonEta'],
                      y_max_scale = 1.4,
                      nBins = len(control_plots_bins['AbsLeptonEta'])-1,
                      rebin = 1,
                      legend_location = ( 0.99, 0.79 ),
                      cms_logo_location = 'left',
                      use_qcd_data_region = useQCDControl,
                      )

        ###################################################
        # NJets
        ###################################################
        if 'NJets' in include_plots:
            print '---> NJets'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NJets'],
                      y_axis_title = 'Events / 1',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'NJets',
                      name_prefix = '%s_NJets_' % label,
                      x_limits = control_plots_bins['NJets'],
                      y_max_scale = 1.4,
                      nBins = len(control_plots_bins['NJets'])-1,
                      rebin = 1,
                      legend_location = ( 0.9, 0.73 ),
                      cms_logo_location = 'left',
                      use_qcd_data_region = useQCDControl,
                      )

            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NJets'],
                      y_axis_title = 'Events / 1',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'NJets',
                      name_prefix = '%s_NJets_logY_' % label,
                      x_limits = control_plots_bins['NJets'],
                      nBins = len(control_plots_bins['NJets'])-1,
                      rebin = 1,
                      legend_location = ( 0.9, 0.83 ),
                      cms_logo_location = 'left',
                      use_qcd_data_region = useQCDControl,
                      log_y = True,
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
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins['MET']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/W Bosons/W Bosons' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/W Bosons/W Bosons' % label,
                      branchName = 'mjj',
                      name_prefix = '%s_mjj_' % label,
                      x_limits = fit_variable_bin_edges['Mjj'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.9, 0.78 ),
                      cms_logo_location = 'right',
                      )

        ###################################################
        # M3
        ###################################################
        if 'M3' in include_plots:
            print '---> M3'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % fit_variables_latex['M3'],
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins['M3']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'M3',
                      name_prefix = '%s_M3_' % label,
                      x_limits = fit_variable_bin_edges['M3'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.9, 0.78 ),
                      cms_logo_location = 'right',
                      use_qcd_data_region = useQCDControl,
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
                      use_qcd_data_region = useQCDControl,
                      )

        # Set folder for this batch of plots
        output_folder =  output_folder_base + "/Control/"
        make_folder_if_not_exists(output_folder)


        ###################################################
        # NBJets
        ###################################################
        if 'NBJets' in include_plots:
            print '---> NBJets'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NBJets'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection NoBSelection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection NoBSelection/FitVariables' % label,
                      branchName = 'NBJets',
                      name_prefix = '%s_NBJets_' % label,
                      x_limits = control_plots_bins['NBJets'],
                      nBins = len(control_plots_bins['NBJets'])-1,
                      rebin = 1,
                      legend_location = ( 0.9, 0.73 ),
                      cms_logo_location = 'right',
                      use_qcd_data_region = False,
                      )

            # make_plot( channel,
            #           x_axis_title = '$%s$' % control_plots_latex['NBJets'],
            #           y_axis_title = 'Events',
            #           signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
            #           control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
            #           branchName = 'NBJets',
            #           name_prefix = '%s_NBJets_logY_' % label,
            #           x_limits = control_plots_bins['NBJets'],
            #           nBins = len(control_plots_bins['NBJets'])-1,
            #           rebin = 1,
            #           legend_location = ( 0.95, 0.83 ),
            #           cms_logo_location = 'right',
            #           log_y = True,
            #           use_qcd_data_region = False,
            #           )
        ###################################################
        # NBJets NoWeight
        ###################################################
        if 'NBJetsNoWeight' in include_plots:
            print '---> NBJetsNoWeight'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NBJets'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection NoBSelection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection NoBSelection/FitVariables' % label,
                      branchName = 'NBJets',
                      name_prefix = '%s_NBJetsNoWeight_' % label,
                      x_limits = control_plots_bins['NBJets'],
                      nBins = len(control_plots_bins['NBJets'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      use_qcd_data_region = False,
                      )
        ###################################################
        # NBJetsUp
        ###################################################
        if 'NBJetsUp' in include_plots:
            print '---> NBJetsUp'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NBJets'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection NoBSelection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection NoBSelection/FitVariables' % label,
                      branchName = 'NBJets',
                      name_prefix = '%s_NBJetsUp_' % label,
                      x_limits = control_plots_bins['NBJets'],
                      nBins = len(control_plots_bins['NBJets'])-1,
                      rebin = 1,
                      legend_location = ( 0.9, 0.73 ),
                      cms_logo_location = 'right',
                      use_qcd_data_region = False,
                      )
        ###################################################
        # NBJetsDown
        ###################################################
        if 'NBJetsDown' in include_plots:
            print '---> NBJetsDown'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NBJets'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection NoBSelection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection NoBSelection/FitVariables' % label,
                      branchName = 'NBJets',
                      name_prefix = '%s_NBJetsDown_' % label,
                      x_limits = control_plots_bins['NBJets'],
                      nBins = len(control_plots_bins['NBJets'])-1,
                      rebin = 1,
                      legend_location = ( 0.9, 0.73 ),
                      cms_logo_location = 'right',
                      use_qcd_data_region = False,
                      )

        ###################################################
        # NLightJetsUp
        ###################################################
        if 'NBJets_LightUp' in include_plots:
            print '---> NBJets_LightUp'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NBJets'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection NoBSelection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection NoBSelection/FitVariables' % label,
                      branchName = 'NBJets',
                      name_prefix = '%s_NBJets_LightUp_' % label,
                      x_limits = control_plots_bins['NBJets'],
                      nBins = len(control_plots_bins['NBJets'])-1,
                      rebin = 1,
                      legend_location = ( 0.9, 0.73 ),
                      cms_logo_location = 'right',
                      use_qcd_data_region = False,
                      )
        ###################################################
        # NLightJetsDown
        ###################################################
        if 'NBJets_LightDown' in include_plots:
            print '---> NBJets_LightDown'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NBJets'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection NoBSelection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection NoBSelection/FitVariables' % label,
                      branchName = 'NBJets',
                      name_prefix = '%s_NBJets_LightDown_' % label,
                      x_limits = control_plots_bins['NBJets'],
                      nBins = len(control_plots_bins['NBJets'])-1,
                      rebin = 1,
                      legend_location = ( 0.9, 0.73 ),
                      cms_logo_location = 'right',
                      use_qcd_data_region = False,
                      )

        ###################################################
        # Jet Pt
        ###################################################
        if 'JetPt' in include_plots:
            print '---> Jet Pt'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['pt'],
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins['JetPt']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % ( label ),
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % (label ),
                      branchName = 'jet_pt',
                      name_prefix = '%s_JetPt_' % label,
                      x_limits = control_plots_bins['JetPt'],
                      nBins = len(control_plots_bins['JetPt'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      use_qcd_data_region = useQCDControl,
                      )
        ###################################################
        # NVertex
        ###################################################
        if 'NVertex' in include_plots:
            print '---> NVertex'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NVertex'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'NVertices',
                      name_prefix = '%s_NPU_' % label,
                      x_limits = control_plots_bins['NVertex'],
                      nBins = len(control_plots_bins['NVertex'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      use_qcd_data_region = False,
                      )

        if 'NVertexNoWeight' in include_plots:
            print '---> NVertexNoWeight'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NVertex'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'NVertices',
                      name_prefix = '%s_NPUNoWeight_' % label,
                      x_limits = control_plots_bins['NVertex'],
                      nBins = len(control_plots_bins['NVertex'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      use_qcd_data_region = False,
                      )
        
        if 'NVertexUp' in include_plots:
            print '---> NVertexUp'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NVertex'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'NVertices',
                      name_prefix = '%s_NPUUp_' % label,
                      x_limits = control_plots_bins['NVertex'],
                      nBins = len(control_plots_bins['NVertex'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      use_qcd_data_region = False,
                      )

        if 'NVertexDown' in include_plots:
            print '---> NVertexDown'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NVertex'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'NVertices',
                      name_prefix = '%s_NPUDown_' % label,
                      x_limits = control_plots_bins['NVertex'],
                      nBins = len(control_plots_bins['NVertex'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      use_qcd_data_region = False,
                      )
        ###################################################
        # Rel iso
        ###################################################
        if 'RelIso' in include_plots:
            print '---> Rel iso'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['relIso'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = '%s' % 'lepton_isolation',
                      name_prefix = '%s_relIso_' % channel,
                      x_limits = control_plots_bins['relIso'],
                      nBins = len(control_plots_bins['relIso'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      use_qcd_data_region = useQCDControl,
                      )

        ###################################################
        # Sigma ieta ieta
        ###################################################

        norm_variable = 'sigmaietaieta'
        if 'sigmaietaieta' in include_plots and channel == 'electron':
            print '---> sigmaietaieta'
            make_plot( channel,
                      x_axis_title = '$%s$' % variables_latex['sigmaietaieta'],
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins['sigmaietaieta']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'sigmaIetaIeta',
                      name_prefix = '%s_sigmaIetaIeta_' % label,
                      x_limits = control_plots_bins['sigmaietaieta'],
                      nBins = len(control_plots_bins['sigmaietaieta'])-1,
                      rebin = 1,
                      legend_location = ( 0.9, 0.83 ),
                      cms_logo_location = 'left',
                      use_qcd_data_region = useQCDControl,
                      )

    ###################################################
    # QCD Control Region
    ###################################################
    for channel, label in {
                            'electronQCDNonIso' : 'EPlusJets/QCD non iso e+jets',
                            'electronQCDConversions' : 'EPlusJets/QCDConversions', 
                            'muonQCDNonIso' : 'MuPlusJets/QCD non iso mu+jets 3toInf',
                            'muonQCDNonIso2' : 'MuPlusJets/QCD non iso mu+jets 1p5to3',
                            }.iteritems() :
        b_tag_bin = '0btag'

        # Set folder for this batch of plots
        output_folder = output_folder_base + "QCDControl/Variables/%s/" % channel
        # output_folder = output_folder_base + "QCDControl/Variables/%s/TightElectron/" % channel
        make_folder_if_not_exists(output_folder)

        print 'Control region :',label

        treeName = 'EPlusJets/QCD non iso e+jets'
        signalTreeName = 'EPlusJets/Ref selection'
        if channel == 'electronQCDConversions':
            treeName = 'EPlusJets/QCDConversions'
        elif channel == 'muonQCDNonIso':
            treeName = 'MuPlusJets/QCD non iso mu+jets 3toInf'
            signalTreeName = 'MuPlusJets/Ref selection'
        elif channel == 'muonQCDNonIso2':
            treeName = 'MuPlusJets/QCD non iso mu+jets 1p5to3'
            signalTreeName = 'MuPlusJets/Ref selection'

        ###################################################
        # HT
        ###################################################
        norm_variable = 'HT'
        if 'QCDHT' in include_plots:
            print '---> QCD HT'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['HT'],
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins['HT']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      branchName = 'HT',
                      name_prefix = '%s_HT_' % channel,
                      x_limits = control_plots_bins['HT'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        if 'QCDHT_dataControl_mcSignal' in include_plots:
            print '---> QCD HT data to signal QCD'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['HT'],
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins['HT']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % signalTreeName,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      branchName = 'HT',
                      name_prefix = '%s_HT_' % channel,
                      x_limits = control_plots_bins['HT'],
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
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins['MET']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      branchName = 'MET',
                      name_prefix = '%s_MET_' % channel,
                      x_limits = control_plots_bins['MET'],
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
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins['ST']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      branchName = 'ST',
                      name_prefix = '%s_ST_' % channel,
                      x_limits = control_plots_bins['ST'],
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
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins['WPT']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % treeName,
                      branchName = 'WPT',
                      name_prefix = '%s_WPT_' % channel,
                      x_limits = control_plots_bins['WPT'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        ###################################################
        # Abs Lepton Eta
        ###################################################
        if 'QCDAbsLeptonEta' in include_plots:
            print '---> QCD Abs Lepton Eta'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['eta'],
                      y_axis_title = 'Events/(%.1f)' % binWidth(control_plots_bins['AbsLeptonEtaQCD']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % ( treeName ),
                      control_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % ( treeName ),
                      branchName = 'abs(lepton_eta)',
                      name_prefix = '%s_AbsLeptonEta_' % channel,
                      x_limits = control_plots_bins['AbsLeptonEtaQCD'],
                      nBins = len(control_plots_bins['AbsLeptonEtaQCD'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        ###################################################
        # Lepton Pt
        ###################################################
        if 'QCDLeptonPt' in include_plots:
            print '---> QCD Lepton Pt'
            binsLabel = 'ElectronPt'
            if channel == 'muon':
                binsLabel = 'MuonPt'

            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['pt'],
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins[binsLabel]),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % ( treeName ),
                      control_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % ( treeName ),
                      branchName = 'lepton_pt',
                      name_prefix = '%s_LeptonPt_' % channel,
                      x_limits = control_plots_bins[binsLabel],
                      nBins = len(control_plots_bins[binsLabel])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        ###################################################
        # NJets
        ###################################################
        if 'QCDNJets' in include_plots:
            print '---> QCD NJets'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['NJets'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % ( treeName ),
                      control_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % ( treeName ),
                      branchName = 'NJets',
                      name_prefix = '%s_NJets_' % channel,
                      x_limits = control_plots_bins['NJets'],
                      nBins = len(control_plots_bins['NJets'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )

        # # Set folder for this batch of plots
        # output_folder =  output_folder_base + "QCDControl/Control/%s/" % channel
        # # output_folder =  output_folder_base + "QCDControl/Control/%s/TightElectron/" % channel
        # make_folder_if_not_exists(output_folder)
        # ###################################################
        # # Rel iso
        # ###################################################
        if 'QCDRelIso' in include_plots:
            print '---> QCD Rel iso'
            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['relIso'],
                      y_axis_title = 'Events',
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % label,
                      branchName = '%s' % 'lepton_isolation',
                      name_prefix = '%s_relIso_' % channel,
                      x_limits = control_plots_bins['relIsoQCD'],
                      nBins = len(control_plots_bins['relIsoQCD'])-1,
                      rebin = 1,
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      )
        # ###################################################
        # # Sigma ieta ieta
        # ###################################################

        # norm_variable = 'sigmaietaieta'
        # if 'QCDsigmaietaieta' in include_plots and not 'MuPlusJets' in treeName:
        #     print '---> sigmaietaieta'
        #     make_plot( channel,
        #               x_axis_title = '$%s$' % variables_latex['sigmaietaieta'],
        #               y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins['sigmaietaieta']),
        #               signal_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % ( treeName ),
        #               control_region_tree = 'TTbar_plus_X_analysis/%s/FitVariables' % ( treeName ),
        #               branchName = 'sigmaIetaIeta',
        #               name_prefix = '%s_sigmaIetaIeta_' % channel,
        #               x_limits = control_plots_bins['sigmaietaieta'],
        #               y_max_scale = 1.5,
        #               nBins = len(control_plots_bins['sigmaietaieta'])-1,
        #               rebin = 1,
        #               legend_location = ( 0.95, 0.85 ),
        #               cms_logo_location = 'left',
        #               )