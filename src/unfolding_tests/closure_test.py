'''
    This module creates the closure tests for each variable & 
    channel (electron, muon, combined). 
'''
from rootpy.io import File

from config.variable_binning import bin_edges_vis
from tools.Unfolding import Unfolding, get_unfold_histogram_tuple
from tools.hist_utilities import hist_to_value_error_tuplelist
from config.cross_section_config import XSectionConfig
from tools.plotting import compare_measurements, Histogram_properties
from config import latex_labels
from rootpy import asrootpy
from collections import OrderedDict

def main():
    config = XSectionConfig(13)
    method = 'TUnfold'

    file_for_response = File(config.unfolding_central, 'read')

    file_for_powhegPythia  = File(config.unfolding_central, 'read')
    file_for_madgraph = File(config.unfolding_madgraphMLM, 'read')
    file_for_amcatnlo = File(config.unfolding_amcatnlo, 'read')

    samples_and_files_to_compare = {
    'powhegPythia' : file_for_powhegPythia,
    'madgraph' : file_for_madgraph,
    'amcatnlo' : file_for_amcatnlo
    }

    for channel in ['combined']:
        # for variable in config.variables:
        for variable in ['WPT']:


            print ('Variable :',variable)

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

                # Unfold, and set 'data' to 'measured' 
                unfolding = Unfolding( measured,
                    truth, measured, h_response, None,
                    method=method, k_value=-1, tau=tau_value)
                
                unfolded_data = unfolding.unfold()

                unfolded_and_truth_for_sample[sample] = {
                                                            'truth' : truth.Clone(),
                                                            'unfolded' : unfolded_data.Clone()
                }

                # print ('Measured :', list ( measured.y() ) )
                # print ('Unfolded :', list ( unfolded_data.y() ) )
                # print ('Truth :', list ( truth.y() ) )

                # relDiff = ( unfolded_data - truth ) / truth * 100

                # truth_tuple = hist_to_value_error_tuplelist(truth)
                # unfolded_data_tuple = hist_to_value_error_tuplelist(unfolded_data)
                # relDiff_tuple = hist_to_value_error_tuplelist(relDiff)

                # for r in relDiff_tuple:
                #     print (r[0],r[1])
                # for u,t in zip( unfolded_data_tuple, truth_tuple ) :
                #     print ( 'Unfolded :',u[0], u[1],'Truth :',t[0],t[1] )
                #     # print ( ( u[0]/t[0] - 1) * 100, u[1], t[1])

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
    if variable in ['HT', 'ST', 'MET', 'WPT']:
        unit = ' [GeV]'
    hp.x_axis_title = v_latex + unit
    hp.y_axis_title = 'Events'
    hp.title = 'Closure tests for {variable}'.format(variable=v_latex)

    output_folder = 'plots/unfolding/closure_test/{0}/'.format(method)

    models = OrderedDict()
    measurements = OrderedDict()
    for sample in unfolded_and_truths:
        models[sample + ' truth'] = unfolded_and_truths[sample]['truth']
        measurements[sample + ' unfolded'] = unfolded_and_truths[sample]['unfolded']

    # models['powhegPythia'] = unfolded_and_truths['powhegPythia']['truth']
    # models['madgraph'] = unfolded_and_truths['madgraph']['truth']

    # measurements['powhegPythia'] = unfolded_and_truths['powhegPythia']['unfolded']
    # measurements['madgraph'] = unfolded_and_truths['madgraph']['unfolded']

    print (models)
    print (measurements)

    compare_measurements(
                         models = models,
                         measurements = measurements,
                         # models={'MC truth': h_truth},
                         # measurements={'unfolded reco': unfolded_data},
                         show_measurement_errors=True,
                         histogram_properties=hp,
                         save_folder=output_folder,
                         save_as=['pdf'],
                         match_models_to_measurements = True)

if __name__ == '__main__':
    main()
