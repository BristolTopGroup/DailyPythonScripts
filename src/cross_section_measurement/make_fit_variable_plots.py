'''
Created on 1 May 2014

@author: kreczko
'''
import config.cross_section_measurement_8TeV as measurement_config
from tools.ROOT_utililities import get_histograms_from_files
from copy import copy
from tools.hist_utilities import prepare_histograms
from tools.plotting import make_data_mc_comparison_plot, Histogram_properties, make_shape_comparison_plot
from config.cross_section_measurement import b_tag_bins_latex
from config.latex_labels import samples_latex
common_fit_variables = ['M3', 'M_bl', 'angle_bl']
electron_fit_variables = copy( common_fit_variables )
electron_fit_variables.append( 'electron_absolute_eta' )
muon_fit_variables = copy( common_fit_variables )
muon_fit_variables.append( 'muon_absolute_eta' )

fit_variable_properties = {
                       'M3': {'min':0, 'max':600, 'rebin':4, 'x-title': 'M3 [GeV]', 'y-title': 'Events/20 GeV'},
                       'M_bl': {'min':0, 'max':400, 'rebin':4, 'x-title': 'M(b,l) [GeV]', 'y-title': 'Events/20 GeV'},
                       'angle_bl': {'min':0, 'max':4, 'rebin':1, 'x-title': 'angle(b,l)', 'y-title': 'Events/(0.1)'},
                       'electron_absolute_eta': {'min':0, 'max':2.6, 'rebin':1, 'x-title': '$\left|\eta(e)\\right|$', 'y-title': 'Events/(0.1)'},
                       'muon_absolute_eta': {'min':0, 'max':2.6, 'rebin':1, 'x-title': '$\left|\eta(\mu)\\right|$', 'y-title': 'Events/(0.1)'},
                       }

b_tag_bin = '2orMoreBtags'
category = 'central'
histogram_files = {
        'data' : measurement_config.data_file_electron,
        'TTJet': measurement_config.ttbar_category_templates[category],
        'V+Jets': measurement_config.VJets_category_templates[category],
        'QCD': measurement_config.electron_QCD_MC_file,  # this should also be category-dependent, but unimportant and not available atm
        'SingleTop': measurement_config.SingleTop_category_templates[category]
}

# the following will move into variable_binning etc.
variables = ['MET']
variable_bins_ROOT = {
                  'MET': ['0-31', '31-58', '58-96', '96-142', '142-191', '191-inf'],
                  }
    
def main():
    global electron_fit_variables, muon_fit_variables, fit_variable_properties, b_tag_bin, category, histogram_files, variables, variable_bins_ROOT
    
    title_template = 'CMS Preliminary, $\mathcal{L} = %.1f$ fb$^{-1}$  at $\sqrt{s}$ = %d TeV \n %s'
    e_title = title_template % ( measurement_config.new_luminosity / 1000., measurement_config.centre_of_mass, 'e+jets, $\geq$ 4 jets' )
    met_type = 'patType1CorrectedPFMet'
    for variable in variables:
        variable_bins = variable_bins_ROOT[variable]
        histogram_template = ''
        if variable == 'HT':
            histogram_template = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_HT_Analysis/HT_bin_%(bin_range)s/%(fit_variable)s_%(b_tag_bin)s'
        elif variable == 'MET':
            histogram_template = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_MET_Analysis/%(met_type)s_bin_%(bin_range)s/%(fit_variable)s_%(b_tag_bin)s'
        else:
            histogram_template = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/Binned_%s_Analysis/%(variable)s_with_%(met_type)s_bin_%(bin_range)s/%(fit_variable)s_%(b_tag_bin)s'
        
        for bin_range in variable_bins:
            for fit_variable in electron_fit_variables:
                params = {'met_type': met_type, 'bin_range':bin_range, 'fit_variable':fit_variable, 'b_tag_bin':b_tag_bin, 'variable':variable}
                fit_variable_distribution = histogram_template % params
                qcd_fit_variable_distribution = fit_variable_distribution.replace( 'Ref selection', 'QCDConversions' )
                histograms = get_histograms_from_files( [fit_variable_distribution, qcd_fit_variable_distribution], histogram_files )
                plot_fit_variable( histograms, fit_variable, variable, bin_range, fit_variable_distribution, qcd_fit_variable_distribution, e_title )
                
def plot_fit_variable( histograms, fit_variable, variable, bin_range,
                      fit_variable_distribution, qcd_fit_variable_distribution,
                      title ):
    global fit_variable_properties, b_tag_bin
    mc_uncertainty = 0.10
    prepare_histograms( histograms, rebin = fit_variable_properties[fit_variable]['rebin'], scale_factor = measurement_config.luminosity_scale )
    
    qcd_from_data = histograms['data'][qcd_fit_variable_distribution].Clone()
    n_qcd_predicted_mc = histograms['QCD'][fit_variable_distribution].Integral()
    n_qcd_fit_variable_distribution = qcd_from_data.Integral()
    if not n_qcd_fit_variable_distribution == 0:
        qcd_from_data.Scale( 1.0 / n_qcd_fit_variable_distribution * n_qcd_predicted_mc )
    
    histograms_to_draw = [histograms['data'][fit_variable_distribution], qcd_from_data,
                          histograms['V+Jets'][fit_variable_distribution],
                          histograms['SingleTop'][fit_variable_distribution], histograms['TTJet'][fit_variable_distribution]]
    histogram_lables = ['data', 'QCD', 'V+Jets', 'Single-Top', samples_latex['TTJet']]
    histogram_colors = ['black', 'yellow', 'green', 'magenta', 'red']
    
    histogram_properties = Histogram_properties()
    histogram_properties.name = variable + '_' + bin_range + '_' + fit_variable + '_' + b_tag_bin
    histogram_properties.title = title + ', ' + b_tag_bins_latex[b_tag_bin]
    histogram_properties.x_axis_title = fit_variable_properties[fit_variable]['x-title']
    histogram_properties.y_axis_title = fit_variable_properties[fit_variable]['y-title']
    histogram_properties.x_limits = [fit_variable_properties[fit_variable]['min'], fit_variable_properties[fit_variable]['max']]
    histogram_properties.mc_error = mc_uncertainty
    histogram_properties.mc_errors_label = '$\mathrm{t}\\bar{\mathrm{t}}$ uncertainty'
    
    make_data_mc_comparison_plot( histograms_to_draw, histogram_lables, histogram_colors,
                                 histogram_properties, save_folder = 'plots/fit_variables/', show_ratio = False )
    histogram_properties.name += '_templates'
    # change QCD color to orange for better visibility
    histogram_colors = ['black', 'orange', 'green', 'magenta', 'red']
    make_shape_comparison_plot( shapes = histograms_to_draw[1:], 
                                  names = histogram_lables[1:], 
                                  colours = histogram_colors[1:],
                                 histogram_properties = histogram_properties,
                                 fill_area = False, 
                                 alpha = 1,
                                 save_folder = 'plots/fit_variables/')
    
if __name__ == '__main__':
    main()
