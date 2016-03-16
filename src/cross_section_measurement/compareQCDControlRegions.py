from optparse import OptionParser
from config.latex_labels import b_tag_bins_latex, samples_latex, channel_latex, \
    variables_latex, fit_variables_latex, control_plots_latex
from config.variable_binning import control_plots_bins
from config.histogram_colours import histogram_colours as colours
from config import XSectionConfig
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from tools.plotting import make_data_mc_comparison_plot, Histogram_properties, \
make_control_region_comparison
from rootpy.plotting import Hist
from tools.hist_utilities import prepare_histograms, clean_control_region, get_normalisation_error, get_fitted_normalisation
from tools.ROOT_utils import get_histograms_from_trees, set_root_defaults
from tools.latex import setup_matplotlib
from uncertainties import ufloat

# latex, font, etc
setup_matplotlib()

title_template = '$%.0f$ pb$^{-1}$ (%d TeV)'

def binWidth(binning):
    return  ( binning[-1] - binning[0] ) / ( len(binning)-1 )


def getPUWeights(histograms_to_draw, histogram_lables) :
    # hists = dict(zip(histogram_lables, histograms_to_draw))
    hists = {}
    dataHist = None
    mcHist = None
    for label, histogram in zip(histogram_lables, histograms_to_draw):
        if label == 'data':
            dataHist = histogram.Clone()
        else :
            if mcHist == None:
                mcHist = histogram.Clone()
            else:
                mcHist += histogram
    dataValues = list(dataHist.y())
    mcValues = list(mcHist.y())

    weights = [ data / mc for data, mc in zip(dataValues, mcValues)]
    print 'PU weights'
    print 'Bin edges :',list(dataHist.xedges())
    print 'Weights : ',weights

def make_plot( channel, x_axis_title, y_axis_title,
              signal_region_tree,
              control_region_tree,
              branchName,
              name_prefix, x_limits, nBins,
              use_qcd_data_region = False,
              compare_qcd_signal_with_data_control = False,
              y_limits = [],
              y_max_scale = 1.3,
              rebin = 1,
              legend_location = ( 0.98, 0.78 ), cms_logo_location = 'right',
              log_y = False,
              legend_color = False,
              ratio_y_limits = [0.3, 2.5],
              normalise = False,
              ):
    global output_folder, measurement_config, category, normalise_to_fit
    global preliminary, norm_variable, sum_bins, b_tag_bin, histogram_files

    controlToCompare = []
    if 'electron' in channel :
        controlToCompare =  ['QCDConversions', 'QCD non iso e+jets']
    elif 'muon' in channel :
        controlToCompare =  ['QCD iso > 0.3', 'QCD 0.12 < iso <= 0.3']

    histogramsToCompare = {}
    for qcd_data_region in controlToCompare:
        print 'Doing ',qcd_data_region
        # Input files, normalisations, tree/region names
        title = title_template % ( measurement_config.new_luminosity, measurement_config.centre_of_mass_energy )
        normalisation = None
        weightBranchSignalRegion = 'EventWeight'
        if 'electron' in channel:
            histogram_files['data'] = measurement_config.data_file_electron_trees
            histogram_files['QCD'] = measurement_config.electron_QCD_MC_category_templates_trees[category]
            if normalise_to_fit:
                normalisation = normalisations_electron[norm_variable]
            # if use_qcd_data_region:
            #     qcd_data_region = 'QCDConversions'
            #     # qcd_data_region = 'QCD non iso e+jets'
            if not 'QCD' in channel and not 'NPU' in branchName:
                weightBranchSignalRegion += ' * ElectronEfficiencyCorrection'
        if 'muon' in channel:
            histogram_files['data'] = measurement_config.data_file_muon_trees
            histogram_files['QCD'] = measurement_config.muon_QCD_MC_category_templates_trees[category]
            if normalise_to_fit:
                normalisation = normalisations_muon[norm_variable]
            # if use_qcd_data_region:
            #     qcd_data_region = 'QCD iso > 0.3'
            if not 'QCD' in channel and not 'NPU' in branchName:
                weightBranchSignalRegion += ' * MuonEfficiencyCorrection'

        if not "_NPUNoWeight" in name_prefix:
            weightBranchSignalRegion += ' * PUWeight'

        if not "_NBJetsNoWeight" in name_prefix:
            weightBranchSignalRegion += ' * BJetWeight'

        selection = '1'
        if branchName == 'abs(lepton_eta)' :
            selection = 'lepton_eta > -10'
        else:
            selection = '%s >= 0' % branchName
        # if 'QCDConversions' in signal_region_tree:
        #     selection += '&& isTightElectron'
        # print selection
        histograms = get_histograms_from_trees( trees = [signal_region_tree, control_region_tree], branch = branchName, weightBranch = weightBranchSignalRegion, files = histogram_files, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1], selection = selection )
        histograms_QCDControlRegion = None
        if use_qcd_data_region:
            qcd_control_region = signal_region_tree.replace( 'Ref selection', qcd_data_region )
            histograms_QCDControlRegion = get_histograms_from_trees( trees = [qcd_control_region], branch = branchName, weightBranch = 'EventWeight', files = histogram_files, nBins = nBins, xMin = x_limits[0], xMax = x_limits[-1], selection = selection )

        # Split histograms up into signal/control (?)
        signal_region_hists = {}
        control_region_hists = {}
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
            print measurement_config.luminosity_scale
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
                print 'Overall scale : ',dataDrivenQCDScale
                qcd_from_data.Scale( dataDrivenQCDScale.nominal_value )
                signalToControlScale = n_qcd_predicted_mc_signal / n_qcd_control_region
                dataToMCscale = n_qcd_control_region / n_qcd_predicted_mc_control
                print "Signal to control :",signalToControlScale
                print "QCD scale : ",dataToMCscale
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
            histogram_colors = [colours['data'], colours['QCD'], colours['V+Jets'], colours['Single-Top'], colours['TTJet'] ]

        
        print list(qcd_from_data.y())
        histogramsToCompare[qcd_data_region] = qcd_from_data

    print histogramsToCompare
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'QCD_control_region_comparison_' + channel + '_' + branchName
    histogram_properties.title = title
    histogram_properties.x_axis_title = x_axis_title
    histogram_properties.y_axis_title = y_axis_title
    histogram_properties.x_limits = x_limits
    histogram_properties.y_limits = y_limits
    histogram_properties.mc_error = 0.0
    histogram_properties.legend_location = ( 0.98, 0.78 )
    histogram_properties.ratio_y_limits = ratio_y_limits
    if 'electron' in channel:
        make_control_region_comparison(histogramsToCompare['QCDConversions'], histogramsToCompare['QCD non iso e+jets'],
                                       name_region_1='Conversions', name_region_2='Non Iso',
                                       histogram_properties=histogram_properties, save_folder=output_folder)
    elif 'muon' in channel:
        make_control_region_comparison(histogramsToCompare['QCD iso > 0.3'], histogramsToCompare['QCD 0.12 < iso <= 0.3'],
                                       name_region_1='QCD iso > 0.3', name_region_2='QCD 0.12 < iso <= 0.3',
                                       histogram_properties=histogram_properties, save_folder=output_folder)

        # histogram_properties = Histogram_properties()
        # histogram_properties.name = name_prefix + b_tag_bin
        # if category != 'central':
        #     histogram_properties.name += '_' + category
        # histogram_properties.title = title
        # histogram_properties.x_axis_title = x_axis_title
        # histogram_properties.y_axis_title = y_axis_title
        # histogram_properties.x_limits = x_limits
        # histogram_properties.y_limits = y_limits
        # histogram_properties.y_max_scale = y_max_scale
        # histogram_properties.xerr = None
        # # workaround for rootpy issue #638
        # histogram_properties.emptybins = True
        # if b_tag_bin:
        #     histogram_properties.additional_text = channel_latex[channel] + ', ' + b_tag_bins_latex[b_tag_bin]
        # else:
        #     histogram_properties.additional_text = channel_latex[channel]
        # histogram_properties.legend_location = legend_location
        # histogram_properties.cms_logo_location = cms_logo_location
        # histogram_properties.preliminary = preliminary
        # histogram_properties.set_log_y = log_y
        # histogram_properties.legend_color = legend_color
        # if ratio_y_limits:
        #     histogram_properties.ratio_y_limits = ratio_y_limits

        # # if normalise_to_fit:
        # #     histogram_properties.mc_error = get_normalisation_error( normalisation )
        # #     histogram_properties.mc_errors_label = 'fit uncertainty'
        # # else:
        # #     histogram_properties.mc_error = mc_uncertainty
        # #     histogram_properties.mc_errors_label = 'MC unc.'

        # if normalise_to_data:
        #         histogram_properties.name += '_normToData'
        # output_folder_to_use = output_folder
        # if use_qcd_data_region:
        #     output_folder_to_use += 'WithQCDFromControl/'
        #     make_folder_if_not_exists(output_folder_to_use)

        # if branchName == 'NPU':
        #     getPUWeights(histograms_to_draw, histogram_lables)

        # print output_folder_to_use
        # # Actually draw histograms
        # make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
        #                              histogram_properties, save_folder = output_folder_to_use,
        #                              show_ratio = False, normalise = normalise,
        #                              )
        # histogram_properties.name += '_with_ratio'
        # loc = histogram_properties.legend_location
        # # adjust legend location as it is relative to canvas!
        # histogram_properties.legend_location = ( loc[0], loc[1] + 0.05 )
        # make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
        #                              histogram_properties, save_folder = output_folder_to_use,
        #                              show_ratio = True, normalise = normalise,
        #                              )


if __name__ == '__main__':
    set_root_defaults()
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data/M3_angle_bl/',
                  help = "set path to JSON files" )
    parser.add_option( "-o", "--output_folder", dest = "output_folder", default = 'plots/qcdComparison/',
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
    useQCDControl = True
    b_tag_bin = '2orMoreBtags'
    norm_variable = 'MET'
    # comment out plots you don't want
    include_plots = [
                        'HT',
                        # 'MET',
                        'METNoHF',
                        'ST',
                        'WPT',
                        # 'NVertex',
                        # 'NVertexNoWeight',
                        'LeptonPt',
                        'AbsLeptonEta',
                        # # # 'Mjj',
                        # # # 'M3',
                        # # # 'angle_bl',
                        'NJets',
                        # 'NBJets',
                        # 'NBJetsNoWeight',
                        # 'JetPt',
                        # 'AbsLeptonEta',
                        # 'RelIso',
                        # 'sigmaietaieta'
                        ]

    additional_qcd_plots = [
                        # 'QCDHT',
                        # 'QCDMET',
                        # 'QCDST',
                        # 'QCDWPT',
                        # 'QCDAbsLeptonEta',
                        # 'QCDLeptonPt',
                        # 'QCDNJets',
                        # 'QCDsigmaietaieta',
                        # 'QCDRelIso',
                        # 'QCDHT_dataControl_mcSignal',
                        ]

    if make_additional_QCD_plots:
        include_plots.extend( additional_qcd_plots )


    for channel, label in {
                            'electron' : 'EPlusJets', 
                            'muon' : 'MuPlusJets'
                            }.iteritems() :
        b_tag_bin = '2orMoreBtags'

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
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins['HT']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'HT',
                      name_prefix = '%s_HT_' % label,
                      x_limits = control_plots_bins['HT'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.9, 0.83 ),
                      cms_logo_location = 'left',
                      use_qcd_data_region = useQCDControl,
                      )

###################################################
        # MET
        ###################################################
        norm_variable = 'MET'
        if 'METNoHF' in include_plots:
            print '---> METNoHF'
            make_plot( channel,
                      x_axis_title = '$%s$ [GeV]' % variables_latex['MET'],
                      y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins['MET']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % label,
                      branchName = 'METNoHF',
                      name_prefix = '%s_METNoHF_' % label,
                      x_limits = control_plots_bins['MET'],
                      nBins = len(control_plots_bins['MET'])-1,
                      rebin = 1,
                      legend_location = ( 0.9, 0.83 ),
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
                      branchName = 'STNoHF',
                      name_prefix = '%s_STNoHF_' % label,
                      x_limits = control_plots_bins['ST'],
                      nBins = 20,
                      rebin = 1,
                      legend_location = ( 0.9, 0.83 ),
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
                      branchName = 'WPTNoHF',
                      name_prefix = '%s_WPTNoHF_' % label,
                      x_limits = control_plots_bins['WPT'],
                      nBins = 16,
                      rebin = 1,
                      legend_location = ( 0.9, 0.83 ),
                      cms_logo_location = 'left',
                      use_qcd_data_region = useQCDControl,
                      )

        # Set folder for this batch of plots
        output_folder =  output_folder_base + "/FitVariables/"
        make_folder_if_not_exists(output_folder)

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
                      nBins = len(control_plots_bins['NJets'])-1,
                      rebin = 1,
                      legend_location = ( 0.9, 0.83 ),
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
                      legend_location = ( 0.9, 0.83 ),
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
                      legend_location = ( 0.95, 0.78 ),
                      cms_logo_location = 'right',
                      use_qcd_data_region = False,
                      )

        ###################################################
        # AbsLepton Eta
        ###################################################
        if 'AbsLeptonEta' in include_plots:
            print '---> Abs Lepton Eta'

            make_plot( channel,
                      x_axis_title = '$%s$' % control_plots_latex['eta'],
                      y_axis_title = 'Events/(%.1f)' % binWidth(control_plots_bins['AbsLeptonEta']),
                      signal_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % ( label ),
                      control_region_tree = 'TTbar_plus_X_analysis/%s/Ref selection/FitVariables' % (label ),
                      branchName = 'abs(lepton_eta)',
                      name_prefix = '%s_AbsLeptonEta_' % label,
                      x_limits = control_plots_bins['AbsLeptonEta'],
                      nBins = len(control_plots_bins['AbsLeptonEta'])-1,
                      rebin = 1,
                      legend_location = ( 0.9, 0.88 ),
                      cms_logo_location = 'left',
                      use_qcd_data_region = True,
                      )