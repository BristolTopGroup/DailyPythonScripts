'''
    This module creates the closure tests for each variable & 
    channel (electron, muon, combined). 
'''
from rootpy.io import File

from config.variable_binning import bin_edges
from tools.Unfolding import Unfolding, get_unfold_histogram_tuple
from config.cross_section_config import XSectionConfig
from tools.plotting import compare_measurements, Histogram_properties
from config import latex_labels


def main():
    config = XSectionConfig(13)
#     method = 'RooUnfoldSvd'
    method = 'RooUnfoldBayes'
    file_for_unfolding = File(config.unfolding_central, 'read')
    for channel in ['electron', 'muon', 'combined']:
        for variable in bin_edges.keys():
            tau_value = get_tau_value(config, channel, variable)
            h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple(
                inputfile=file_for_unfolding,
                variable=variable,
                channel=channel,
                met_type=config.met_type,
                centre_of_mass=config.centre_of_mass_energy,
                ttbar_xsection=config.ttbar_xsection,
                luminosity=config.luminosity,
                load_fakes=False,
                visiblePS=False,
            )
            unfolding = Unfolding(
                h_truth, h_measured, h_response, h_fakes,
                method=method, k_value=-1, tau=tau_value)

            unfolded_data = unfolding.closureTest()
            plot_closure(h_truth, unfolded_data, variable, channel,
                         config.centre_of_mass_energy, method)


def get_tau_value(config, channel, variable):
    if channel == 'electron':
        return config.tau_values_electron[variable]
    if channel == 'muon':
        return config.tau_values_muon[variable]
    if channel == 'combined':
        return config.tau_values_combined[variable]


def plot_closure(h_truth, unfolded_data, variable, channel, come, method):
    hp = Histogram_properties()
    hp.name = '{channel}_closure_test_for_{variable}_at_{come}TeV'.format(
        channel=channel,
        variable=variable,
        come=come,
    )
    v_latex = latex_labels.variables_latex[variable]
    unit = ''
    if variable in ['HT', 'ST', 'MET', 'WPT']:
        unit = ' [GeV]'
    hp.x_axis_title = v_latex + unit
    hp.y_axis_title = 'Events'
    hp.title = 'Closure tests for {variable}'.format(variable=v_latex)

    output_folder = 'plots/unfolding/closure_test/{0}/'.format(method)

    compare_measurements(models={'MC truth': h_truth},
                         measurements={'unfolded reco': unfolded_data},
                         show_measurement_errors=True,
                         histogram_properties=hp,
                         save_folder=output_folder,
                         save_as=['png', 'pdf'])

if __name__ == '__main__':
    main()
