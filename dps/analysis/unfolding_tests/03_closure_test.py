'''
    This module creates the closure tests for each variable & 
    channel (electron, muon, combined). 
'''
from rootpy.io import File

from dps.config.variable_binning import bin_edges_vis, bin_widths_visiblePS
from dps.utils.Unfolding import Unfolding, get_unfold_histogram_tuple
from dps.utils.hist_utilities import hist_to_value_error_tuplelist, value_error_tuplelist_to_hist, values_and_errors_to_hist
from dps.utils.Calculation import calculate_normalised_xsection
from dps.config.xsection import XSectionConfig
from dps.utils.plotting import compare_measurements, Histogram_properties
from dps.config import latex_labels
from rootpy import asrootpy
from collections import OrderedDict
from dps.utils.latex import setup_matplotlib
from dps.utils.pandas_utilities import file_to_df

# latex, font, etc
setup_matplotlib()
def main():
    config = XSectionConfig(13)
    method = 'TUnfold'

    file_for_response = File(config.unfolding_central_secondHalf, 'read')
    file_for_powhegPythia  = File(config.unfolding_central_firstHalf, 'read')
    file_for_ptReweight_up  = File(config.unfolding_ptreweight_up_firstHalf, 'read')
    file_for_ptReweight_down  = File(config.unfolding_ptreweight_down_firstHalf, 'read')
    file_for_amcatnlo           = File(config.unfolding_amcatnlo, 'read')
    file_for_powhegHerwig       = File(config.unfolding_powheg_herwig, 'read')
    file_for_etaReweight_up = File(config.unfolding_etareweight_up, 'read')
    file_for_etaReweight_down = File(config.unfolding_etareweight_down, 'read')

    samples_and_files_to_compare = {
    'Central' : file_for_powhegPythia,
    'Nominal' : file_for_response,
    'PtReweighted Up' : file_for_ptReweight_up,
    'PtReweighted Down' : file_for_ptReweight_down,
    # 'amcatnlo' : file_for_amcatnlo,
    # 'powhegHerwig' : file_for_powhegHerwig,
    # 'EtaReweighted Up' : file_for_etaReweight_up,
    # 'EtaReweighted Down' : file_for_etaReweight_down,
    }

    for channel in config.analysis_types.keys():
        if channel is 'combined':continue
        print 'Channel :',channel
        for variable in config.variables:
        # for variable in ['ST']:


            print 'Variable :',variable

            # Always unfold with the same response matrix and tau value
            tau_value = get_tau_value(config, channel, variable) 
            # tau_value = 0.00000001

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
            unfolded_and_truth_xsection_for_sample = {}

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
                    method=method, tau=tau_value)
                
                unfolded_data = unfolding.unfold()



                # unfolded_and_truth_for_sample[sample] = {
                #                                             'truth' : truth_xsection,
                #                                             'unfolded' : unfolded_xsection,
                #                                             'bias' : bias
                # }

                bias = calculate_bias( truth, unfolded_data )

                unfolded_and_truth_for_sample[sample] = {
                                                            'truth' : truth,
                                                            'unfolded' : unfolded_data,
                                                            'bias' : bias
                }

                unfolded_xsection = calculate_xsection( unfolded_data, variable )
                truth_xsection = calculate_xsection( truth, variable )
                bias_xsection = calculate_bias( truth_xsection, unfolded_xsection )
                unfolded_and_truth_xsection_for_sample[sample] = {
                                                            'truth' : truth_xsection,
                                                            'unfolded' : unfolded_xsection,
                                                            'bias' : bias_xsection
                }

            plot_closure(unfolded_and_truth_for_sample, variable, channel,
                         config.centre_of_mass_energy, method, 'number_of_unfolded_events')

            plot_closure(unfolded_and_truth_xsection_for_sample, variable, channel,
                         config.centre_of_mass_energy, method, 'normalised_xsection')

            plot_bias(unfolded_and_truth_for_sample, variable, channel,
                         config.centre_of_mass_energy, method, 'number_of_unfolded_events')

            plot_bias(unfolded_and_truth_xsection_for_sample, variable, channel,
                         config.centre_of_mass_energy, method, 'normalised_xsection', plot_systematics=True)

def get_tau_value(config, channel, variable):
    if channel == 'electron':
        return config.tau_values_electron[variable]
    if channel == 'muon':
        return config.tau_values_muon[variable]
    if channel == 'combined':
        return config.tau_values_combined[variable]


def plot_closure(unfolded_and_truths, variable, channel, come, method, quantity):
    hp = Histogram_properties()
    hp.name = '{quantity}_{channel}_closure_test_for_{variable}_at_{come}TeV'.format(
        quantity=quantity,
        channel=channel,
        variable=variable,
        come=come,
    )
    v_latex = latex_labels.variables_latex[variable]
    unit = ''
    if variable in ['HT', 'ST', 'MET', 'WPT', 'lepton_pt']:
        unit = ' [GeV]'
    hp.x_axis_title = v_latex + unit
    if quantity == 'number_of_unfolded_events':
        hp.y_axis_title = 'Number of unfolded events'
    elif quantity == 'normalised_xsection':
        hp.y_axis_title = 'Normalised Cross Section'        
    hp.title = 'Closure tests for {variable}'.format(variable=v_latex)

    output_folder = 'plots/unfolding/closure_test/'

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
        match_models_to_measurements = True
    )

def plot_bias(unfolded_and_truths, variable, channel, come, method, prefix, plot_systematics=False):
    hp = Histogram_properties()
    hp.name = 'Bias_{prefix}_{channel}_{variable}_at_{come}TeV'.format(
        prefix=prefix,
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
    hp.y_axis_title = 'Unfolded / Truth'
    hp.y_limits = [0.7, 1.5]
    hp.title = 'Bias for {variable}'.format(variable=v_latex)
    hp.legend_location = (0.98, 0.95)
    output_folder = 'plots/unfolding/bias_test/'

    measurements = {}
    # measurements = { 'Central' : unfolded_and_truths['Central']['bias'] }
    # for bin in range(0, unfolded_and_truths['Central']['bias'].GetNbinsX() + 1 ):
    #     unfolded_and_truths['Central']['bias'].SetBinError(bin,0)

    models = OrderedDict()
    lineStyles = []
    for sample in unfolded_and_truths:
        if sample == 'Central' or sample == 'Nominal': 
            lineStyles.append('dashed')
        else:
            lineStyles.append('dotted')
        models[sample] = unfolded_and_truths[sample]['bias']

    if plot_systematics:
        models['systematicsup'], models['systematicsdown'] = get_systematics(variable,channel,come,method)
        lineStyles.append('solid')
        lineStyles.append('solid')

    compare_measurements(
        models = models,
        measurements = measurements,
        show_measurement_errors=True,
        histogram_properties=hp,
        save_folder=output_folder,
        save_as=['pdf'],
        line_styles_for_models = lineStyles,
        match_models_to_measurements = True
    )

def calculate_xsection( nEventsHistogram, variable ):
    resultsAsTuple = hist_to_value_error_tuplelist( nEventsHistogram )
    normalised_xsection, _, _ = calculate_normalised_xsection( resultsAsTuple, bin_widths_visiblePS[variable], False )

    return value_error_tuplelist_to_hist(normalised_xsection, bin_edges_vis[variable])

def calculate_bias( true_histogram, unfolded_histogram ):
    bias_histogram = ( unfolded_histogram ) / true_histogram
    return bias_histogram

def get_systematics(variable,channel,com,method):
    input_file = 'data/normalisation/background_subtraction/13TeV/{var}/VisiblePS/central/xsection_normalised_{channel}_{method}_summary_relative.txt'.format(
    var = variable,
    channel = channel,
    method = method,
    )
    systematic_uncertainties = file_to_df(input_file)['systematic']
    sys_up = []
    sys_down = []
    for i in range(0, len(systematic_uncertainties) ):
        sys_up.append( 1 + systematic_uncertainties[i] )
        sys_down.append( 1 - systematic_uncertainties[i] )
    return values_and_errors_to_hist( sys_up, [], bin_edges_vis[variable] ), values_and_errors_to_hist( sys_down, [], bin_edges_vis[variable] )


if __name__ == '__main__':
    main()
