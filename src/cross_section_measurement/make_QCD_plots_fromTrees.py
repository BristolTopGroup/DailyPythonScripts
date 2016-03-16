from optparse import OptionParser
from config.latex_labels import b_tag_bins_latex, samples_latex, fit_variables_latex, fit_variables_units_latex, variables_latex, control_plots_latex
from config.variable_binning import fit_variable_bin_edges, bin_edges_vis, control_plots_bins
from config import XSectionConfig
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from tools.plotting import make_data_mc_comparison_plot, Histogram_properties, \
make_control_region_comparison
from tools.hist_utilities import prepare_histograms
from tools.ROOT_utils import get_histograms_from_files, set_root_defaults, get_histograms_from_trees

channels = [
'EPlusJets',
'MuPlusJets'
]
if __name__ == '__main__':

    set_root_defaults()
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data/absolute_eta_M3_angle_bl/',
                  help = "set path to JSON files" )
    parser.add_option( "-o", "--output_folder", dest = "output_folder", default = 'plots/control_plots/',
                  help = "set path to save plots" )
    parser.add_option( "-c", "--centre-of-mass-energy", dest = "CoM", default = 13, type = int,
                      help = "set the centre of mass energy for analysis. Default = 13 [TeV]" )
    parser.add_option( "--category", dest = "category", default = 'central',
                      help = "set the category to take the fit results from (default: central)" )

    ( options, args ) = parser.parse_args()
    measurement_config = XSectionConfig( options.CoM )
    # caching of variables for shorter access
    translate_options = measurement_config.translate_options

    # Input and output
    path_to_JSON = '%s/%dTeV/' % ( options.path, measurement_config.centre_of_mass_energy )
    output_folder = '%s/before_fit/%dTeV/' % ( options.output_folder, measurement_config.centre_of_mass_energy )
    make_folder_if_not_exists(output_folder)

    # Central or whatever
    category = options.category
    
    # Input files for each group of samples
    histogram_files = {
        'data' : measurement_config.data_file_electron_trees,
        'TTJet': measurement_config.ttbar_category_templates_trees[category],
        'V+Jets': measurement_config.VJets_category_templates_trees[category],
        'QCD': measurement_config.electron_QCD_MC_category_templates_trees[category],
        'SingleTop': measurement_config.SingleTop_category_templates_trees[category],
    }

    # Templates of titles for all plots
    title_template = 'CMS Preliminary, $\mathcal{L} = %.1f$ fb$^{-1}$  at $\sqrt{s}$ = %d TeV \n %s'
    # Title in electron channel
    e_title = title_template % ( measurement_config.new_luminosity / 1000., measurement_config.centre_of_mass_energy, 'e+jets, $\geq$ 4 jets' )
    # Title in muon channel
    mu_title = title_template % ( measurement_config.new_luminosity / 1000., measurement_config.centre_of_mass_energy, '#mu+jets, $\geq$ 4 jets' )


    for channel in channels:

        regions = []
        if channel == 'MuPlusJets':
            regions = ['QCD non iso mu+jets']
        elif channel == 'EPlusJets':
            regions = ['QCD non iso e+jets', 'QCDConversions']

        for control_region in regions :
            # Fit variables (inclusive)
            for var in ['M3', 'angle_bl', 'M_bl', 'absolute_eta']:
                print channel,var
                controlTree = 'TTbar_plus_X_analysis/%s/%s/FitVariables' % ( channel, control_region )

                bins = fit_variable_bin_edges[var]
                xMin = bins[0]
                xMax = bins[-1]
                nBins = len(bins) -1
                
                histograms = get_histograms_from_trees( trees = [controlTree], branch = var, weightBranch = 'EventWeight', files = histogram_files, nBins = nBins, xMin = xMin, xMax = xMax )

                prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
                
                histograms_to_draw = [histograms['data'][controlTree], histograms['QCD'][controlTree],
                                      histograms['V+Jets'][controlTree],
                                      histograms['SingleTop'][controlTree], histograms['TTJet'][controlTree]]
                histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
                histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
                
                histogram_properties = Histogram_properties()
                histogram_properties.name = 'QCD_nonIso_%s_%s' % (channel, var)
                if control_region == 'QCDConversions' :
                    histogram_properties.name = 'QCD_Conversions_%s_%s' % (channel, var)
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
                                             histogram_properties, save_folder = output_folder, show_ratio = False )

            # Variables for diff xsec
            for var in [ 'MET', 'HT', 'ST', 'WPT', 'MT' ]:
                print var  
                controlTree = 'TTbar_plus_X_analysis/%s/%s/FitVariables' % ( channel, control_region )

                bins = bin_edges_vis[var]
                xMin = bins[0]
                xMax = bins[-1]
                nBins = 40

                histograms = get_histograms_from_trees( trees = [controlTree], branch = var, weightBranch = 'EventWeight', files = histogram_files, nBins = nBins, xMin = xMin, xMax = xMax )
                prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
                
                histograms_to_draw = [histograms['data'][controlTree], histograms['QCD'][controlTree],
                                      histograms['V+Jets'][controlTree],
                                      histograms['SingleTop'][controlTree], histograms['TTJet'][controlTree]]
                histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
                histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
                
                histogram_properties = Histogram_properties()
                histogram_properties.name = 'QCD_nonIso_%s_%s' % (channel, var)
                if control_region == 'QCDConversions' :
                    histogram_properties.name = 'QCD_Conversions_%s_%s' % (channel, var)
                if category != 'central':
                    histogram_properties.name += '_' + category
                if channel == 'EPlusJets':
                    histogram_properties.title = e_title
                elif channel == 'MuPlusJets':
                    histogram_properties.title = mu_title

                eventsPerBin = (xMax - xMin) / nBins
                histogram_properties.x_axis_title = '%s [GeV]' % ( variables_latex[var] )
                histogram_properties.y_axis_title = 'Events/(%.2g GeV)' % (eventsPerBin)
              
                histogram_properties.name += '_with_ratio'
                make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                             histogram_properties, save_folder = output_folder, show_ratio = False )

# Variables for diff xsec
            for var in [ 'relIso_03_deltaBeta', 'relIso_04_deltaBeta' ]:

                if channel is 'EPlusJets' and var is 'relIso_04_deltaBeta' : continue
                elif channel is 'MuPlusJets' and var is 'relIso_03_deltaBeta' : continue

                tree = ''
                if channel is 'EPlusJets' : tree = 'Electron/Electrons'
                elif channel is 'MuPlusJets' : tree = 'Muon/Muons'
                print var
                controlTree = 'TTbar_plus_X_analysis/%s/%s/%s' % ( channel, control_region, tree )

                bins = control_plots_bins[var]
                xMin = bins[0]
                xMax = bins[-1]
                nBins = 40
                print bins,
                print xMin, xMax, nBins
                histograms = get_histograms_from_trees( trees = [controlTree], branch = var, weightBranch = 'EventWeight', files = histogram_files, nBins = nBins, xMin = xMin, xMax = xMax )
                prepare_histograms( histograms, rebin = 1, scale_factor = measurement_config.luminosity_scale )
                
                histograms_to_draw = [histograms['data'][controlTree], histograms['QCD'][controlTree],
                                      histograms['V+Jets'][controlTree],
                                      histograms['SingleTop'][controlTree], histograms['TTJet'][controlTree]]
                histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
                histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
                
                histogram_properties = Histogram_properties()
                histogram_properties.name = 'QCD_nonIso_%s_%s' % (channel, var)
                if control_region == 'QCDConversions' :
                    histogram_properties.name = 'QCD_Conversions_%s_%s' % (channel, var)
                if category != 'central':
                    histogram_properties.name += '_' + category
                if channel == 'EPlusJets':
                    histogram_properties.title = e_title
                elif channel == 'MuPlusJets':
                    histogram_properties.title = mu_title

                eventsPerBin = (xMax - xMin) / nBins
                histogram_properties.x_axis_title = '%s [GeV]' % ( control_plots_latex[var] )
                histogram_properties.y_axis_title = 'Events/(%.2g GeV)' % (eventsPerBin)
              
                histogram_properties.set_log_y = True
                histogram_properties.name += '_with_ratio'
                make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                             histogram_properties, save_folder = output_folder, show_ratio = False )
                