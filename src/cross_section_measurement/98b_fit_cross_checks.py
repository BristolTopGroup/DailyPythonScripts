from optparse import OptionParser
from config import XSectionConfig, fit_var_inputs
from config.variable_binning import bin_edges_vis
from lib import read_normalisation, closure_tests
# from tools.file_utilities import read_data_from_JSON
# from tools.plotting import Histogram_properties

# from matplotlib import pyplot as plt
# import rootpy.plotting.root2matplotlib as rplt
from tools.hist_utilities import value_error_tuplelist_to_hist, spread_x, \
    limit_range_y
from tools.plotting import compare_measurements, Histogram_properties
from config.latex_labels import fit_variables_latex, samples_latex
from src.cross_section_measurement.lib import read_initial_normalisation
# import linecache
# 
# from config.variable_binning import variable_bins_ROOT
def plot_fit_results( fit_results, initial_values, channel ):
    global variable, output_folder
    
    title = electron_histogram_title if channel == 'electron' else muon_histogram_title
    
    
    histogram_properties = Histogram_properties()
    histogram_properties.title = title
    
    histogram_properties.x_axis_title = variable + ' [GeV]'
    histogram_properties.mc_error = 0.0
    histogram_properties.legend_location = 'upper right'
    # we will need 4 histograms: TTJet, SingleTop, QCD, V+Jets
    for sample in ['TTJet', 'SingleTop', 'QCD', 'V+Jets']:
        histograms = {}
        # absolute eta measurement as baseline
        h_absolute_eta = None
        h_before = None
        histogram_properties.y_axis_title = 'Fitted number of events for ' + samples_latex[sample]
        
        for fit_var_input in fit_results.keys():
            latex_string = create_latex_string( fit_var_input )
            fit_data = fit_results[fit_var_input][sample]
            h = value_error_tuplelist_to_hist( fit_data,
                                              bin_edges_vis[variable] )
            if fit_var_input == 'absolute_eta':
                h_absolute_eta = h
            elif fit_var_input == 'before':
                h_before = h
            else:
                histograms[latex_string] = h
        graphs = spread_x( histograms.values(), bin_edges_vis[variable] )
        for key, graph in zip( histograms.keys(), graphs ):
            histograms[key] = graph
        filename = sample.replace( '+', '_' ) + '_fit_var_comparison_' + channel
        histogram_properties.name = filename
        histogram_properties.y_limits = 0, limit_range_y( h_absolute_eta )[1] * 1.3
        histogram_properties.x_limits = bin_edges_vis[variable][0], bin_edges_vis[variable][-1]
        
        h_initial_values = value_error_tuplelist_to_hist( initial_values[sample],
                                                         bin_edges_vis[variable] )
        h_initial_values.Scale(closure_tests['simple'][sample])
        
        compare_measurements( models = {fit_variables_latex['absolute_eta']:h_absolute_eta,
                                        'initial values' : h_initial_values,
                                        'before': h_before},
                             measurements = histograms,
                             show_measurement_errors = True,
                             histogram_properties = histogram_properties,
                             save_folder = output_folder,
                             save_as = ['png', 'pdf'] )
        
def create_latex_string( fit_var_input ):
    known_fit_vars = fit_variables_latex.keys()
    if fit_var_input in known_fit_vars:
        return fit_variables_latex[fit_var_input]
    
    if fit_var_input == 'before':
        return 'before'
    # now we are left with multi-var
    latex_string = fit_var_input
    # replace all known variables with their latex equivalent
    for known_var in known_fit_vars:
        latex_string = latex_string.replace( known_var,
                                            fit_variables_latex[known_var] )
    # lastly replace the remaining '_' with commas
    latex_string = latex_string.replace( '_', ',' )
    
    return latex_string
    
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data/',
                  help = "set path to JSON files" )
    parser.add_option( "-v", "--variable", dest = "variable", default = 'MET',
                  help = "set the variable to analyse (MET, HT, ST, MT)" )
    parser.add_option( "-o", "--output_folder", dest = "output_folder", default = 'plots/fitchecks/',
                  help = "set path to save plots" )
    parser.add_option( "-m", "--metType", dest = "metType", default = 'type1',
                      help = "set MET type used in the analysis of MET-dependent variables" )
    parser.add_option( "-c", "--category", dest = "category", default = 'central',
                      help = "set the category to take the fit results from (default: central)" )
    parser.add_option( "-e", "--centre-of-mass-energy", dest = "CoM", default = 8, type = int,
                  help = "set the centre of mass energy for analysis. Default = 8 [TeV]" )
    
    ( options, args ) = parser.parse_args()
    measurement_config = XSectionConfig( options.CoM )
    # caching of variables for shorter access
    translate_options = measurement_config.translate_options
    lumi = measurement_config.luminosity
    come = measurement_config.centre_of_mass_energy
    
    path_to_JSON = options.path
    output_folder = options.output_folder
    if not output_folder.endswith( '/' ):
        output_folder += '/'
    category = options.category
    met_type = translate_options[options.metType]
    variable = options.variable
    
    electron_histogram_title = 'CMS Preliminary, $\mathcal{L}$ = %.1f fb$^{-1}$ at $\sqrt{s}$ = %d TeV \n e+jets, $\geq$4 jets' % ( lumi/1000, come )
    muon_histogram_title = 'CMS Preliminary, $\mathcal{L}$ = %.1f fb$^{-1}$ at $\sqrt{s}$ = %d TeV \n $\mu$+jets, $\geq$4 jets' % ( lumi/1000, come )
    
    fit_variables = fit_var_inputs

    fit_results_electron = {}
    fit_results_muon = {}
    initial_values_electron = {}
    initial_values_muon = {}
    for fit_variable in fit_variables:
        path = path_to_JSON + fit_variable + '/' + str( come ) + 'TeV/'
        fit_results_electron[fit_variable] = read_normalisation( path,
                                                variable,
                                                category,
                                                'electron',
                                                 met_type )
        fit_results_muon[fit_variable] = read_normalisation( path,
                                                variable,
                                                category,
                                                'muon',
                                                 met_type )
    # it doesn't matter which one to use, all of them are identical
    # so lets use the 2011 and 2012 default, |eta|
    initial_values_electron = read_initial_normalisation( path_to_JSON + 'absolute_eta' + '/' + str( come ) + 'TeV/',
                                             variable,
                                             category,
                                             'electron',
                                             met_type )
    initial_values_muon = read_initial_normalisation( path_to_JSON + 'absolute_eta' + '/' + str( come ) + 'TeV/',
                                             variable,
                                             category,
                                             'muon',
                                             met_type )
    
    if not 'closure' in path_to_JSON:
        fit_results_electron['before'] =  read_normalisation( 'data_single_var_fit/8TeV/',
                                                variable,
                                                category,
                                                'electron',
                                                 met_type )
        fit_results_muon['before'] = read_normalisation( 'data_single_var_fit/8TeV/',
                                                variable,
                                                category,
                                                'muon',
                                                 met_type )
    plot_fit_results( fit_results_electron, initial_values_electron, 'electron' )
    plot_fit_results( fit_results_muon, initial_values_muon, 'muon' )
