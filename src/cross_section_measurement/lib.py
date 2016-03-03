# Library for all cross section measurement specific functions
# that need to be shared between scripts
from rootpy.io import File
from config.variable_binning import bin_edges_vis

from tools.hist_utilities import value_error_tuplelist_to_hist, value_errors_tuplelist_to_graph
from tools.file_utilities import read_data_from_JSON
from tools.Timer import Timer

from tools.logger import log
mylog = log["src.cross_section_measurement.lib"]

closure_tests = {
    'simple': {'V+Jets': 1.1, 'SingleTop': 1.2, 'TTJet': 1.3, 'QCD': 1.5},
    'ttbar_only': {'V+Jets': 0, 'SingleTop': 0, 'TTJet': 1, 'QCD': 0},
    'singletop_only': {'V+Jets': 0, 'SingleTop': 1, 'TTJet': 0, 'QCD': 0},
    'vjets_only': {'V+Jets': 1, 'SingleTop': 0, 'TTJet': 0, 'QCD': 0},
    'qcd_only': {'V+Jets': 0, 'SingleTop': 0, 'TTJet': 0, 'QCD': 1},
}


@mylog.trace()
def read_normalisation(path_to_JSON='data',
                       variable='MET',
                       category='central',
                       channel='combined',
                       met_type='patType1CorrectedPFMet'):
    return read_from_fit_results_folder(path_to_JSON, variable, category, channel, met_type, 'normalisation')


@mylog.trace()
def read_initial_normalisation(path_to_JSON='data',
                               variable='MET',
                               category='central',
                               channel='combined',
                               met_type='patType1CorrectedPFMet',
                               phase_space='FullPS'):
    return read_from_fit_results_folder(path_to_JSON, variable, category, channel, met_type, 'initial_normalisation')


@mylog.trace()
def read_unfolded_normalisation(
        path_to_JSON='data',
        variable='MET',
        category='central',
        channel='combined',
        met_type='patType1CorrectedPFMet'):
    new_path = '{path}/xsection_measurement_results/{channel}/{category}/{file}'
    result_file = 'normalisation_{0}.txt'.format(met_type)
    new_path = new_path.format(
        path=path_to_JSON,
        channel=channel,
        category=category,
        file=result_file,
    )
    return read_data_from_JSON(new_path)


@mylog.trace()
def read_fit_templates(path_to_JSON='data',
                       variable='MET',
                       category='central',
                       channel='combined',
                       met_type='patType1CorrectedPFMet'):
    return read_from_fit_results_folder(path_to_JSON, variable, category, channel, met_type, 'templates')


@mylog.trace()
def read_from_fit_results_folder(path_to_JSON='data',
                                 variable='MET',
                                 category='central',
                                 channel='combined',
                                 met_type='patType1CorrectedPFMet',
                                 data_type='fit_results'):
    filename = path_to_JSON + '/' + category + '/'
    filename += data_type + '_' + channel + '_' + met_type + '.txt'
    results = read_data_from_JSON(filename)

    return results


@mylog.trace()
def read_xsection_measurement_results(path_to_JSON, variable, bin_edges,
                                      category,
                                      channel,
                                      k_values,
                                      met_type='patType1CorrectedPFMet',
                                      met_uncertainties=[]):

    filename = ''
    if category in met_uncertainties and variable == 'HT' and not 'JES' in category and not 'JER' in category:
        filename = path_to_JSON + '/xsection_measurement_results/' + \
            channel + '/central/normalised_xsection_' + met_type + '.txt'
    else:
        filename = path_to_JSON + '/xsection_measurement_results/' + channel + \
            '/' + category + '/normalised_xsection_' + met_type + '.txt'

    if channel == 'combined':
        filename = filename.replace('kv' + str(k_values[channel]), '')

    normalised_xsection_unfolded = read_data_from_JSON(filename)

    h_normalised_xsection = value_error_tuplelist_to_hist(
        normalised_xsection_unfolded['TTJet_measured'], bin_edges[variable])
    h_normalised_xsection_unfolded = value_error_tuplelist_to_hist(
        normalised_xsection_unfolded['TTJet_unfolded'], bin_edges[variable])

    histograms_normalised_xsection_different_generators = {'measured': h_normalised_xsection,
                                                           'unfolded': h_normalised_xsection_unfolded}

    histograms_normalised_xsection_systematics_shifts = {'measured': h_normalised_xsection,
                                                         'unfolded': h_normalised_xsection_unfolded}

    if category == 'central':
        # true distributions
        h_normalised_xsection_MADGRAPH = value_error_tuplelist_to_hist(
            normalised_xsection_unfolded['MADGRAPH'], bin_edges[variable])
        h_normalised_xsection_POWHEG_PYTHIA = value_error_tuplelist_to_hist(
            normalised_xsection_unfolded['POWHEG_PYTHIA'], bin_edges[variable])
        h_normalised_xsection_POWHEG_HERWIG = value_error_tuplelist_to_hist(
            normalised_xsection_unfolded['POWHEG_HERWIG'], bin_edges[variable])
        h_normalised_xsection_MCATNLO = value_error_tuplelist_to_hist(
            normalised_xsection_unfolded['MCATNLO'], bin_edges[variable])
        h_normalised_xsection_mathchingup = value_error_tuplelist_to_hist(
            normalised_xsection_unfolded['matchingup'], bin_edges[variable])
        h_normalised_xsection_mathchingdown = value_error_tuplelist_to_hist(
            normalised_xsection_unfolded['matchingdown'], bin_edges[variable])
        h_normalised_xsection_scaleup = value_error_tuplelist_to_hist(
            normalised_xsection_unfolded['scaleup'], bin_edges[variable])
        h_normalised_xsection_scaledown = value_error_tuplelist_to_hist(
            normalised_xsection_unfolded['scaledown'], bin_edges[variable])

        histograms_normalised_xsection_different_generators.update({'MADGRAPH': h_normalised_xsection_MADGRAPH,
                                                                    'POWHEG_PYTHIA': h_normalised_xsection_POWHEG_PYTHIA,
                                                                    'POWHEG_HERWIG': h_normalised_xsection_POWHEG_HERWIG,
                                                                    'MCATNLO': h_normalised_xsection_MCATNLO})

        histograms_normalised_xsection_systematics_shifts.update({'MADGRAPH': h_normalised_xsection_MADGRAPH,
                                                                  'matchingdown': h_normalised_xsection_mathchingdown,
                                                                  'matchingup': h_normalised_xsection_mathchingup,
                                                                  'scaledown': h_normalised_xsection_scaledown,
                                                                  'scaleup': h_normalised_xsection_scaleup})

        file_template = path_to_JSON + '/xsection_measurement_results/' + channel + \
            '/kv' + str(k_values[channel]) + '/' + \
            category + '/normalised_xsection_' + met_type
        if channel == 'combined':
            file_template = file_template.replace(
                'kv' + str(k_values[channel]), '')
#         normalised_xsection_unfolded_with_errors = read_data_from_JSON( file_template + '_with_errors.txt' )
        normalised_xsection_unfolded_with_errors_with_systematics_but_without_ttbar_theory = read_data_from_JSON(
            file_template + '_with_systematics_but_without_ttbar_theory_errors.txt')
        normalised_xsection_unfolded_with_errors_with_systematics_but_without_generator = read_data_from_JSON(
            file_template + '_with_systematics_but_without_generator_errors.txt')

        # a rootpy.Graph with asymmetric errors!
        h_normalised_xsection_with_systematics_but_without_ttbar_theory = value_errors_tuplelist_to_graph(
            normalised_xsection_unfolded_with_errors_with_systematics_but_without_ttbar_theory[
                'TTJet_measured'],
            bin_edges[variable])
        h_normalised_xsection_with_systematics_but_without_ttbar_theory_unfolded = value_errors_tuplelist_to_graph(
            normalised_xsection_unfolded_with_errors_with_systematics_but_without_ttbar_theory[
                'TTJet_unfolded'],
            bin_edges[variable])

        h_normalised_xsection_with_systematics_but_without_generator = value_errors_tuplelist_to_graph(
            normalised_xsection_unfolded_with_errors_with_systematics_but_without_generator[
                'TTJet_measured'],
            bin_edges[variable])
        h_normalised_xsection_with_systematics_but_without_generator_unfolded = value_errors_tuplelist_to_graph(
            normalised_xsection_unfolded_with_errors_with_systematics_but_without_generator[
                'TTJet_unfolded'],
            bin_edges[variable])

        histograms_normalised_xsection_different_generators[
            'measured_with_systematics'] = h_normalised_xsection_with_systematics_but_without_generator
        histograms_normalised_xsection_different_generators[
            'unfolded_with_systematics'] = h_normalised_xsection_with_systematics_but_without_generator_unfolded

        histograms_normalised_xsection_systematics_shifts[
            'measured_with_systematics'] = h_normalised_xsection_with_systematics_but_without_ttbar_theory
        histograms_normalised_xsection_systematics_shifts[
            'unfolded_with_systematics'] = h_normalised_xsection_with_systematics_but_without_ttbar_theory_unfolded

    return histograms_normalised_xsection_different_generators, histograms_normalised_xsection_systematics_shifts


@mylog.trace()
def convert_unfolding_histograms(file_name,
                                 histograms_to_load=['truth',
                                                     'fake', 'measured', 'response',
                                                     'response_withoutFakes', 'response_without_fakes',
                                                     'EventCounter',
                                                     ]):

    file_start = Timer()
    print 'Converting', file_name
    histograms = {}
    with File(file_name) as f:
        for path, _, objects in f.walk():
            # keep only unfolding and EventFilter
            if path.startswith('unfolding_') or path == 'EventFilter':
                histograms[path] = {}
                for hist_name in objects:
                    if hist_name in histograms_to_load:
                        hist = f.Get(path + '/' + hist_name).Clone()
                        hist.SetDirectory(0)
                        histograms[path][hist_name] = hist
    new_histograms = {}
    # rebin
    for path, hists in histograms.iteritems():
        new_histograms[path] = {}
        variable = ''
        if not path == 'EventFilter':
            variable = path.split('_')[1]
        for name, hist in hists.iteritems():
            if name == 'EventCounter':
                new_histograms[path][name] = hist.Clone()
            else:
                new_hist = hist.rebinned(bin_edges_vis[variable])
                if 'TH2' in new_hist.class_name():
                    new_hist = new_hist.rebinned(bin_edges_vis[variable], axis=1)
                new_histograms[path][name] = new_hist

    # save_to_file
    output = File(file_name.replace('.root', '_asymmetric.root'), 'recreate')
    for path, hists in new_histograms.iteritems():
        directory = output.mkdir(path)
        directory.cd()
        for name, hist in hists.iteritems():
            if name == 'response_withoutFakes':  # fix this name
                hist.Write('response_without_fakes')
            else:
                hist.Write(name)
    output.close()
    secs = file_start.elapsed_time()
    print 'File %s converted in %d seconds' % (file_name, secs)
