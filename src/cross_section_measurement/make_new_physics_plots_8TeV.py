from config import CMS, XSectionConfig
from optparse import OptionParser
from tools.ROOT_utils import get_histograms_from_files
from tools.file_utilities import read_data_from_JSON
from tools.plotting import make_data_mc_comparison_plot, Histogram_properties
from tools.hist_utilities import prepare_histograms
from config.variable_binning import variable_bins_ROOT

def get_fitted_normalisation(variable, channel):
    global path_to_JSON, category, met_type
    fit_results = read_data_from_JSON(path_to_JSON + variable + '/fit_results/' + category + '/fit_results_' + channel + '_' + met_type + '.txt')

    N_fit_ttjet = [0, 0]
    N_fit_singletop = [0, 0]
    N_fit_vjets = [0, 0]
    N_fit_qcd = [0, 0]

    bins = variable_bins_ROOT[variable]
    for bin_i, _ in enumerate(bins):
        #central values
        N_fit_ttjet[0] += fit_results['TTJet'][bin_i][0]
        N_fit_singletop[0] += fit_results['SingleTop'][bin_i][0]
        N_fit_vjets[0] += fit_results['V+Jets'][bin_i][0]
        N_fit_qcd[0] += fit_results['QCD'][bin_i][0]

        #errors
        N_fit_ttjet[1] += fit_results['TTJet'][bin_i][1]
        N_fit_singletop[1] += fit_results['SingleTop'][bin_i][1]
        N_fit_vjets[1] += fit_results['V+Jets'][bin_i][1]
        N_fit_qcd[1] += fit_results['QCD'][bin_i][1]

    fitted_normalisation = {
                'TTJet': N_fit_ttjet,
                'SingleTop': N_fit_singletop,
                'V+Jets': N_fit_vjets,
                'QCD': N_fit_qcd
                }
    return fitted_normalisation

def get_normalisation_error(normalisation):
    total_normalisation = 0.
    total_error = 0.
    for _, number in normalisation.iteritems():
        total_normalisation += number[0]
        total_error += number[1]
    return total_error/total_normalisation

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data/',
                  help="set path to JSON files")
    parser.add_option("-o", "--output_folder", dest="output_folder", default='plots/',
                  help="set path to save plots")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type used in the analysis of MET-dependent variables")
    parser.add_option("-c", "--category", dest="category", default='central',
                      help="set the category to take the fit results from (default: central)")
    parser.add_option("-n", "--normalise_to_fit", dest="normalise_to_fit", action="store_true",
                  help="normalise the MC to fit results")
    parser.add_option("-a", "--additional-plots", action="store_true", dest="additional_QCD_plots",
                      help="creates a set of QCD plots for exclusive bins for all variables")

    (options, args) = parser.parse_args()
    measurement_config = XSectionConfig(8)
    path_to_JSON = options.path + '/' + '8TeV/'
    output_folder = options.output_folder
    normalise_to_fit = options.normalise_to_fit
    category = options.category
    met_type = measurement_config.translate_options[options.metType]
    make_additional_QCD_plots = options.additional_QCD_plots

    CMS.title['fontsize'] = 40
    CMS.x_axis_title['fontsize'] = 50
    CMS.y_axis_title['fontsize'] = 50
    CMS.axis_label_major['labelsize'] = 40
    CMS.axis_label_minor['labelsize'] = 40
    CMS.legend_properties['size'] = 40
    
    from config.latex_labels import b_tag_bins_latex, samples_latex
    
    histogram_files = {
            'data' : measurement_config.data_file_electron,
            'TTJet': measurement_config.ttbar_category_templates[category],
            'V+Jets': measurement_config.VJets_category_templates[category],
            'QCD': measurement_config.electron_QCD_MC_file, #this should also be category-dependent, but unimportant and not available atm
            'SingleTop': measurement_config.SingleTop_category_templates[category]
    }

#     #getting normalisations
#     normalisations_electron = {
#             'MET':get_fitted_normalisation('MET', 'electron'),
#             'HT':get_fitted_normalisation('HT', 'electron'),
#             'ST':get_fitted_normalisation('ST', 'electron'),
#             'MT':get_fitted_normalisation('MT', 'electron'),
#             'WPT':get_fitted_normalisation('WPT', 'electron')
#             }
#     normalisations_muon = {
#             'MET':get_fitted_normalisation('MET', 'muon'),
#             'HT':get_fitted_normalisation('HT', 'muon'),
#             'ST':get_fitted_normalisation('ST', 'muon'),
#             'MT':get_fitted_normalisation('MT', 'muon'),
#             'WPT':get_fitted_normalisation('WPT', 'muon')
#             }
    title_template = 'CMS Preliminary, $\mathcal{L} = %.1f$ fb$^{-1}$  at $\sqrt{s}$ = %d TeV \n %s'
    e_title = title_template % (measurement_config.new_luminosity/ 1000., 
                                measurement_config.centre_of_mass_energy, 
                                'e+jets, $\geq$4 jets')
    #bjet_invariant_mass
    #bjet invariant mass
    b_tag_bin = '4orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/bjet_invariant_mass_' + b_tag_bin
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=20, scale_factor = measurement_config.luminosity_scale)
    
    qcd_predicted_mc = histograms['QCD'][control_region]
    
    histograms_to_draw = [histograms['data'][control_region], qcd_predicted_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_BJets_invmass_' + b_tag_bin
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$M_{\mathrm{b}\\bar{\mathrm{b}}}$'
    histogram_properties.y_axis_title = 'Normalised events/(20 GeV)'
    histogram_properties.x_limits = [0, 800]
    histogram_properties.mc_error = 0.15
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False)
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True)
    
    #bjet invariant mass
    b_tag_bin = '3btags'
    control_region = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/bjet_invariant_mass_' + b_tag_bin
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=10, scale_factor = measurement_config.luminosity_scale)
    
    qcd_predicted_mc = histograms['QCD'][control_region]
    
    histograms_to_draw = [histograms['data'][control_region], qcd_predicted_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'EPlusJets_BJets_invmass_' + b_tag_bin
    histogram_properties.title = e_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$M_{\mathrm{b}\\bar{\mathrm{b}}}$'
    histogram_properties.y_axis_title = 'Normalised events/(10 GeV)'
    histogram_properties.x_limits = [0, 800]
    histogram_properties.mc_error = 0.15
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False)
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True)

    #muons
    data = 'SingleMu'
    histogram_files['data'] = measurement_config.data_file_muon
    histogram_files['QCD'] = measurement_config.muon_QCD_MC_category_templates[category]

    mu_title = title_template % (measurement_config.new_luminosity/ 1000., measurement_config.centre_of_mass_energy, '$\mu$+jets, $\geq$4 jets')
    
    #Muon |eta|
    b_tag_bin = '4orMoreBtags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/bjet_invariant_mass_' + b_tag_bin
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=20, scale_factor = measurement_config.luminosity_scale)
    
    qcd_predicted_mc = histograms['QCD'][control_region]
    
    histograms_to_draw = [histograms['data'][control_region], qcd_predicted_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_BJets_invmass_' + b_tag_bin
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$M_{\mathrm{b}\\bar{\mathrm{b}}}$'
    histogram_properties.y_axis_title = 'Normalised events/(20 GeV)'
    histogram_properties.x_limits = [0, 800]
    histogram_properties.mc_error = 0.15
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False)
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True)
    
    b_tag_bin = '3btags'
    control_region = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/bjet_invariant_mass_' + b_tag_bin
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=10, scale_factor = measurement_config.luminosity_scale)
    
    qcd_predicted_mc = histograms['QCD'][control_region]
    
    histograms_to_draw = [histograms['data'][control_region], qcd_predicted_mc,
                          histograms['V+Jets'][control_region],
                          histograms['SingleTop'][control_region], histograms['TTJet'][control_region]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'MuPlusJets_BJets_invmass_' + b_tag_bin
    histogram_properties.title = mu_title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = '$M_{\mathrm{b}\\bar{\mathrm{b}}}$'
    histogram_properties.y_axis_title = 'Normalised events/(10 GeV)'
    histogram_properties.x_limits = [0, 800]
    histogram_properties.mc_error = 0.15
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = False)
    histogram_properties.name += '_with_ratio'
    make_data_mc_comparison_plot(histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = output_folder, show_ratio = True)

