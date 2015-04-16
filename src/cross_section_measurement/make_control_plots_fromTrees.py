from optparse import OptionParser
from config.latex_labels import b_tag_bins_latex, samples_latex, fit_variables_latex, fit_variables_units_latex, variables_latex, control_plots_latex
from config.variable_binning import fit_variable_bin_edges, bin_edges, control_plots_bins
from config import XSectionConfig
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from tools.plotting import make_data_mc_comparison_plot, Histogram_properties, \
make_control_region_comparison
from tools.hist_utilities import prepare_histograms, get_fitted_normalisation, get_normalisation_error, get_data_derived_qcd
from tools.ROOT_utils import get_histograms_from_files, set_root_defaults, get_histograms_from_trees

channels = [
'EPlusJets',
'MuPlusJets'
]
if __name__ == '__main__':

    set_root_defaults()
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data/M3_angle_bl/',
                  help = "set path to JSON files" )
    parser.add_option( "-o", "--output_folder", dest = "output_folder", default = 'plots/control_plots/',
                  help = "set path to save plots" )
    parser.add_option( "-c", "--centre-of-mass-energy", dest = "CoM", default = 13, type = int,
                      help = "set the centre of mass energy for analysis. Default = 13 [TeV]" )
    parser.add_option( "--category", dest = "category", default = 'central',
                      help = "set the category to take the fit results from (default: central)" )
    parser.add_option( "-n", "--normalise_to_fit", dest = "normalise_to_fit", action = "store_true",
                  help = "normalise the MC to fit results" )

    ( options, args ) = parser.parse_args()
    measurement_config = XSectionConfig( options.CoM )
    # caching of variables for shorter access
    translate_options = measurement_config.translate_options

    normalise_to_fit = options.normalise_to_fit

    # Input and output
    path_to_JSON = '%s/%dTeV/' % ( options.path, measurement_config.centre_of_mass_energy )

    if normalise_to_fit:
        output_folder = '%s/after_fit/%dTeV/' % ( options.output_folder, measurement_config.centre_of_mass_energy )
    else:
        output_folder = '%s/before_fit/%dTeV/' % ( options.output_folder, measurement_config.centre_of_mass_energy )
    make_folder_if_not_exists(output_folder)

    outputDirForVariables = output_folder + '/Variables/'
    make_folder_if_not_exists(outputDirForVariables)
    if not normalise_to_fit:
        outputDirForFitVariables = output_folder + '/FitVariables/'
        make_folder_if_not_exists(outputDirForFitVariables)
        outputDirForOtherControl = output_folder + '/Control/'
        make_folder_if_not_exists(outputDirForOtherControl)

    # Central or whatever
    category = options.category
    
    # Input files for each group of samples
    histogram_files = {
        'data' : measurement_config.data_file_electron_trees,
        'TTJet': measurement_config.ttbar_category_templates_trees[category],
        'V+Jets': measurement_config.VJets_category_templates_trees[category],
        'QCD': 'Nothing',
        'SingleTop': measurement_config.SingleTop_category_templates_trees[category],
    }

    # Fitted normalisation
    normalisations_electron = {}
    normalisations_muon = {}
    if normalise_to_fit:
        normalisations_electron = {
                'MET':get_fitted_normalisation( 'MET', 'electron', path_to_JSON, category, 'patType1CorrectedPFMet' ),
                'HT':get_fitted_normalisation( 'HT', 'electron', path_to_JSON, category, 'patType1CorrectedPFMet'  ),
                'ST':get_fitted_normalisation( 'ST', 'electron', path_to_JSON, category, 'patType1CorrectedPFMet'  ),
                'MT':get_fitted_normalisation( 'MT', 'electron', path_to_JSON, category, 'patType1CorrectedPFMet'  ),
                'WPT':get_fitted_normalisation( 'WPT', 'electron', path_to_JSON, category, 'patType1CorrectedPFMet'  )
        }

        normalisations_muon = {
                'MET':get_fitted_normalisation( 'MET', 'muon', path_to_JSON, category, 'patType1CorrectedPFMet' ),
                'HT':get_fitted_normalisation( 'HT', 'muon', path_to_JSON, category, 'patType1CorrectedPFMet'  ),
                'ST':get_fitted_normalisation( 'ST', 'muon', path_to_JSON, category, 'patType1CorrectedPFMet'  ),
                'MT':get_fitted_normalisation( 'MT', 'muon', path_to_JSON, category, 'patType1CorrectedPFMet'  ),
                'WPT':get_fitted_normalisation( 'WPT', 'muon', path_to_JSON, category, 'patType1CorrectedPFMet'  )
        }

    # Templates of titles for all plots
    title_template = 'CMS Preliminary, $\mathcal{L} = %.1f$ fb$^{-1}$  at $\sqrt{s}$ = %d TeV \n %s'
    # Title in electron channel
    e_title = title_template % ( measurement_config.new_luminosity / 1000., measurement_config.centre_of_mass_energy, 'e+jets, $\geq$ 4 jets' )
    # Title in muon channel
    mu_title = title_template % ( measurement_config.new_luminosity / 1000., measurement_config.centre_of_mass_energy, '#mu+jets, $\geq$ 4 jets' )

    for channel in channels:
        print channel
        control_region = ''
        fitted_normalisation = {}
        if channel == 'EPlusJets':
            control_region = 'QCD non iso e+jets'
            histogram_files['QCD'] = measurement_config.electron_QCD_MC_category_templates_trees[category]
            fitted_normalisation = normalisations_electron
        elif channel == 'MuPlusJets':
            control_region = 'QCD non iso mu+jets'
            histogram_files['QCD'] = measurement_config.muon_QCD_MC_category_templates_trees[category]
            fitted_normalisation = normalisations_muon

        # Variables for diff xsec
        for var in [ 'MET', 'HT', 'ST', 'WPT', 'MT' ]:
            print '--->',var
            signal_region = 'Ref selection'

            signalTree = 'TTbar_plus_X_analysis/%s/%s/FitVariables' % ( channel, signal_region )
            controlTree = 'TTbar_plus_X_analysis/%s/%s/FitVariables' % ( channel, control_region )

            bins = bin_edges[var]
            xMin = bins[0]
            xMax = bins[-1]
            nBins = 40

            histograms = get_histograms_from_trees( trees = [signalTree, controlTree], branch = var, weightBranch = 'EventWeight', files = histogram_files, nBins = nBins, xMin = xMin, xMax = xMax )

            histogram_dataDerivedQCD = get_data_derived_qcd( { h : histograms[h][controlTree] for h in ['data','TTJet','SingleTop','V+Jets','QCD']}, histograms['QCD'][signalTree])

            for sample in histograms:
                signalNorm = histograms[sample][signalTree].integral( overflow = True )
                controlNorm = histograms[sample][controlTree].integral( overflow = True )
                if signalNorm < 1. : signalNorm = 1.
                if controlNorm < 0.1 : controlNorm = 1.
                histograms[sample][controlTree].Scale( signalNorm / controlNorm )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )

            if normalise_to_fit:
                prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale, normalisation = fitted_normalisation[var] )
            else:
                prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )

            histograms_to_draw = [histograms['data'][signalTree],
                                  histogram_dataDerivedQCD,
                                  # histograms['QCD'][signalTree],
                                  histograms['V+Jets'][signalTree],
                                  histograms['SingleTop'][signalTree], histograms['TTJet'][signalTree]]
            histogram_lables = ['data', 'QCD', 
                                'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow', 
                                'green', 'magenta', 'red']

            histogram_properties = Histogram_properties()
            histogram_properties.name = '%s_%s' % (channel, var)
            if category != 'central':
                histogram_properties.name += '_' + category
            if channel == 'EPlusJets':
                histogram_properties.title = e_title
            elif channel == 'MuPlusJets':
                histogram_properties.title = mu_title

            eventsPerBin = (xMax - xMin) / nBins
            histogram_properties.x_axis_title = '%s [GeV]' % ( variables_latex[var] )
            histogram_properties.y_axis_title = 'Events/(%.2g GeV)' % (eventsPerBin)
            histogram_properties.y_limits = [0, histograms['data'][signalTree].GetMaximum() * 1.3 ]
            # histogram_properties.set_log_y = True

          
            histogram_properties.name += '_with_ratio'
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = outputDirForVariables, show_ratio = True )

        if normalise_to_fit : continue
        # Fit variables (inclusive)
        for var in ['M3', 'angle_bl', 'M_bl', 'absolute_eta']:
            print '--->',var
            signal_region = 'Ref selection'
            signalTree = 'TTbar_plus_X_analysis/%s/%s/FitVariables' % ( channel, signal_region )
            controlTree = 'TTbar_plus_X_analysis/%s/%s/FitVariables' % ( channel, control_region )

            bins = fit_variable_bin_edges[var]
            xMin = bins[0]
            xMax = bins[-1]
            nBins = len(bins) -1
            
            histograms = get_histograms_from_trees( trees = [signalTree, controlTree], branch = var, weightBranch = 'EventWeight', files = histogram_files, nBins = nBins, xMin = xMin, xMax = xMax )
            histogram_dataDerivedQCD = get_data_derived_qcd( { h : histograms[h][controlTree] for h in ['data','TTJet','SingleTop','V+Jets','QCD']}, histograms['QCD'][signalTree])

            for sample in histograms:
                signalNorm = histograms[sample][signalTree].integral( overflow = True )
                controlNorm = histograms[sample][controlTree].integral( overflow = True )
                if signalNorm < 1. : signalNorm = 1.
                if controlNorm < 0.1 : controlNorm = 1.
                histograms[sample][controlTree].Scale( signalNorm / controlNorm )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
            
            histograms_to_draw = [histograms['data'][signalTree], 
                                  # histograms['QCD'][signalTree],
                                  histogram_dataDerivedQCD,
                                  histograms['V+Jets'][signalTree],
                                  histograms['SingleTop'][signalTree], histograms['TTJet'][signalTree]]
            histogram_lables = ['data', 'QCD', 
                                'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow',
                                 'green', 'magenta', 'red']
            
            histogram_properties = Histogram_properties()
            histogram_properties.name = '%s_%s' % (channel, var)
            if category != 'central':
                histogram_properties.name += '_' + category
            if channel == 'EPlusJets':
                histogram_properties.title = e_title
            elif channel == 'MuPlusJets':
                histogram_properties.title = mu_title

            eventsPerBin = (xMax - xMin) / nBins
            if fit_variables_units_latex[var] != '':
                histogram_properties.x_axis_title = '%s [%s]' % ( fit_variables_latex[var], fit_variables_units_latex[var] )
                histogram_properties.y_axis_title = 'Events/(%.2g %s)' % (eventsPerBin, fit_variables_units_latex[var])
            else :
                histogram_properties.x_axis_title = '%s' % ( fit_variables_latex[var] )
                histogram_properties.y_axis_title = 'Events/(%.2g)' % eventsPerBin             
            histogram_properties.name += '_with_ratio'
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = outputDirForFitVariables, show_ratio = True )


        # Jet control plots
        for var in [ 'NJets', 'NBJets', 'pt' ]:
            print '--->',var
            signal_region = 'Ref selection'
            signalTree = 'TTbar_plus_X_analysis/%s/%s/Jets/Jets' % ( channel, signal_region )

            bins = control_plots_bins[var]
            xMin = bins[0]
            xMax = bins[-1]
            nBins = len(bins)-1
            histograms = get_histograms_from_trees( trees = [signalTree], branch = var, weightBranch = 'EventWeight', files = histogram_files, nBins = nBins, xMin = xMin, xMax = xMax )
            prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
            
            histograms_to_draw = [histograms['data'][signalTree],
                                  histograms['QCD'][signalTree],
                                  histograms['V+Jets'][signalTree],
                                  histograms['SingleTop'][signalTree], histograms['TTJet'][signalTree]]
            histogram_lables = ['data', 'QCD',
                                'V+Jets', 'Single-Top', samples_latex['TTJet']]
            histogram_colors = ['black', 'yellow',
                                'green', 'magenta', 'red']
            
            histogram_properties = Histogram_properties()
            histogram_properties.name = '%s_%s' % (channel, var)
            if category != 'central':
                histogram_properties.name += '_' + category
            if channel == 'EPlusJets':
                histogram_properties.title = e_title
            elif channel == 'MuPlusJets':
                histogram_properties.title = mu_title

            eventsPerBin = (xMax - xMin) / nBins
            histogram_properties.x_axis_title = '%s [GeV]' % ( control_plots_latex[var] )
            histogram_properties.y_axis_title = 'Events/(%.2g GeV)' % (eventsPerBin)
            histogram_properties.x_limits = [xMin, xMax]
            histogram_properties.set_log_y = True

            histogram_properties.name += '_with_ratio'
            make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                         histogram_properties, save_folder = outputDirForOtherControl, show_ratio = True )
