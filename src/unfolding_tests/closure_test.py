'''
    This module creates the closure tests for each variable & 
    channel (electron, muon, combined). 
'''
from rootpy.io import File

from config.variable_binning import bin_edges_vis, bin_widths_visiblePS
from tools.Unfolding import Unfolding, get_unfold_histogram_tuple
from tools.hist_utilities import hist_to_value_error_tuplelist, value_error_tuplelist_to_hist
from tools.Calculation import calculate_normalised_xsection
from config.cross_section_config import XSectionConfig
from tools.plotting import compare_measurements, Histogram_properties
from config import latex_labels
from rootpy import asrootpy
from collections import OrderedDict
from tools.latex import setup_matplotlib
# latex, font, etc
setup_matplotlib()
def main():
    config = XSectionConfig(13)
    method = 'TUnfold'

    file_for_response = File(config.unfolding_central, 'read')
    file_for_powhegPythia  = File(config.unfolding_central, 'read')
    file_for_madgraph  = File(config.unfolding_madgraphMLM, 'read')

    samples_and_files_to_compare = {
    'Central' : file_for_powhegPythia,
    'Reweighted' : File('unfolding/13TeV/unfolding_TTJets_13TeV_asymmetric_withTopPtReweighting.root','read'),
    'Madgraph' : file_for_madgraph,

    }

    for channel in ['combined']:
        for variable in config.variables:
        # for variable in ['ST']:


            print 'Variable :',variable

            # Always unfold with the same response matrix and tau value
            tau_value = get_tau_value(config, channel, variable) 
            _, _, h_response, _ = get_unfold_histogram_tuple(
                inputfile=file_for_response,
                variable=variable,
                channel=channel,
                met_type=config.met_type,
                centre_of_mass=config.centre_of_mass_energy,
                ttbar_xsection=config.ttbar_xsection,
                luminosity=config.luminosity,
                load_fakes=False,
                visiblePS=True,
            )

            integralOfResponse = asrootpy(h_response.ProjectionY()).integral(0,-1)

            # Dictionary to hold results
            unfolded_and_truth_for_sample = {}

            for sample, input_file_for_unfolding in samples_and_files_to_compare.iteritems():

                _, _, h_response_to_unfold, _ = get_unfold_histogram_tuple(
                    inputfile=input_file_for_unfolding,
                    variable=variable,
                    channel=channel,
                    met_type=config.met_type,
                    centre_of_mass=config.centre_of_mass_energy,
                    ttbar_xsection=config.ttbar_xsection,
                    luminosity=config.luminosity,
                    load_fakes=False,
                    visiblePS=True,
                )

                measured = asrootpy(h_response_to_unfold.ProjectionX('px',1))
                truth = asrootpy(h_response_to_unfold.ProjectionY())

                scale = integralOfResponse / truth.integral(0,-1)
                measured.Scale( scale )
                truth.Scale( scale )
                # Unfold, and set 'data' to 'measured' 
                unfolding = Unfolding( measured,
                    truth, measured, h_response, None,
                    method=method, k_value=-1, tau=tau_value)
                
                unfolded_data = unfolding.unfold()

                unfolded_xsection = calculate_xsection( unfolded_data, variable )
                truth_xsection = calculate_xsection( truth, variable )

                unfolded_and_truth_for_sample[sample] = {
                                                            'truth' : truth_xsection,
                                                            'unfolded' : unfolded_xsection
                }

            plot_closure(unfolded_and_truth_for_sample, variable, channel,
                         config.centre_of_mass_energy, method)


def get_tau_value(config, channel, variable):
    if channel == 'electron':
        return config.tau_values_electron[variable]
    if channel == 'muon':
        return config.tau_values_muon[variable]
    if channel == 'combined':
        return config.tau_values_combined[variable]


def plot_closure(unfolded_and_truths, variable, channel, come, method):
    hp = Histogram_properties()
    hp.name = '{channel}_closure_test_for_{variable}_at_{come}TeV'.format(
        channel=channel,
        variable=variable,
        come=come,
    )
    v_latex = latex_labels.variables_latex[variable]
    unit = ''
    if variable in ['HT', 'ST', 'MET', 'WPT', 'lepton_pt']:
        unit = ' [GeV]'
    hp.x_axis_title = v_latex + unit
    # plt.ylabel( r, CMS.y_axis_title )
    hp.y_axis_title = r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + v_latex + '}$' + unit
    hp.title = 'Closure tests for {variable}'.format(variable=v_latex)

    output_folder = 'plots/unfolding/closure_test/{0}/'.format(method)

    models = OrderedDict()
    measurements = OrderedDict()
    for sample in unfolded_and_truths:
        models[sample + ' truth'] = unfolded_and_truths[sample]['truth']
        measurements[sample + ' unfolded'] = unfolded_and_truths[sample]['unfolded']


    compare_measurements(
                         models = models,
                         measurements = measurements,
                         show_measurement_errors=True,
                         histogram_properties=hp,
                         save_folder=output_folder,
                         save_as=['pdf'],
                         match_models_to_measurements = True)

def calculate_xsection( nEventsHistogram, variable ):
    resultsAsTuple = hist_to_value_error_tuplelist( nEventsHistogram )
    normalised_xsection = calculate_normalised_xsection( resultsAsTuple, bin_widths_visiblePS[variable], False )
    return value_error_tuplelist_to_hist(normalised_xsection, bin_edges_vis[variable])

if __name__ == '__main__':
    main()
