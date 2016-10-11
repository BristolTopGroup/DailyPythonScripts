'''
Approval conditions for TOP-15-013
'''
from __future__ import division
from dps.utils.plotting import Histogram_properties, compare_histograms, Plot, \
    ErrorBand, compare_measurements
from dps.utils.file_utilities import read_data_from_JSON
from dps.utils.hist_utilities import value_error_tuplelist_to_hist,\
    clean_control_region, absolute, value_tuplelist_to_hist, spread_x,\
    value_errors_tuplelist_to_graph
from dps.config.variable_binning import bin_edges_vis
from dps.config.latex_labels import variables_latex
from dps.utils.ROOT_utils import get_histogram_from_tree
from dps.config.xsection import XSectionConfig
from collections import namedtuple


def compare_unfolding_methods(measurement='normalised_xsection',
                              add_before_unfolding=False, channel='combined'):
    file_template = '/hdfs/TopQuarkGroup/run2/dpsData/'
    file_template += 'data/normalisation/background_subtraction/13TeV/'
    file_template += '{variable}/VisiblePS/central/'
    file_template += '{measurement}_{channel}_RooUnfold{method}.txt'

    variables = ['MET', 'HT', 'ST', 'NJets',
                 'lepton_pt', 'abs_lepton_eta', 'WPT']
    for variable in variables:
        svd = file_template.format(
            variable=variable,
            method='Svd',
            channel=channel,
            measurement=measurement)
        bayes = file_template.format(
            variable=variable,
            method='Bayes', channel=channel,
            measurement=measurement)
        data = read_data_from_JSON(svd)
        before_unfolding = data['TTJet_measured_withoutFakes']
        svd_data = data['TTJet_unfolded']
        bayes_data = read_data_from_JSON(bayes)['TTJet_unfolded']
        h_svd = value_error_tuplelist_to_hist(
            svd_data, bin_edges_vis[variable])
        h_bayes = value_error_tuplelist_to_hist(
            bayes_data, bin_edges_vis[variable])
        h_before_unfolding = value_error_tuplelist_to_hist(
            before_unfolding, bin_edges_vis[variable])

        properties = Histogram_properties()
        properties.name = '{0}_compare_unfolding_methods_{1}_{2}'.format(
            measurement, variable, channel)
        properties.title = 'Comparison of unfolding methods'
        properties.path = 'plots'
        properties.has_ratio = True
        properties.xerr = True
        properties.x_limits = (
            bin_edges_vis[variable][0], bin_edges_vis[variable][-1])
        properties.x_axis_title = variables_latex[variable]
        if 'xsection' in measurement:
            properties.y_axis_title = r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + \
                variables_latex[variable] + '}$'
        else:
            properties.y_axis_title = r'$t\bar{t}$ normalisation'

        histograms = {'SVD': h_svd, 'Bayes': h_bayes}
        if add_before_unfolding:
            histograms['before unfolding'] = h_before_unfolding
            properties.name += '_ext'
            properties.has_ratio = False
        plot = Plot(histograms, properties)
        plot.draw_method = 'errorbar'
        compare_histograms(plot)

def compare_combine_before_after_unfolding(measurement='normalised_xsection',
                              add_before_unfolding=False):
    file_template = 'data/normalisation/background_subtraction/13TeV/'
    file_template += '{variable}/VisiblePS/central/'
    file_template += '{measurement}_{channel}_RooUnfold{method}.txt'

    variables = ['MET', 'HT', 'ST', 'NJets',
                 'lepton_pt', 'abs_lepton_eta', 'WPT']
    for variable in variables:
        combineBefore = file_template.format(
            variable=variable,
            method='Svd',
            channel='combinedBeforeUnfolding',
            measurement=measurement)
        combineAfter = file_template.format(
            variable=variable,
            method='Svd',
            channel='combined',
            measurement=measurement)
        data = read_data_from_JSON(combineBefore)
        before_unfolding = data['TTJet_measured']
        combineBefore_data = data['TTJet_unfolded']
        combineAfter_data = read_data_from_JSON(combineAfter)['TTJet_unfolded']
        h_combineBefore = value_error_tuplelist_to_hist(
            combineBefore_data, bin_edges_vis[variable])
        h_combineAfter = value_error_tuplelist_to_hist(
            combineAfter_data, bin_edges_vis[variable])
        h_before_unfolding = value_error_tuplelist_to_hist(
            before_unfolding, bin_edges_vis[variable])

        properties = Histogram_properties()
        properties.name = '{0}_compare_combine_before_after_unfolding_{1}'.format(
            measurement, variable)
        properties.title = 'Comparison of combining before/after unfolding'
        properties.path = 'plots'
        properties.has_ratio = True
        properties.xerr = True
        properties.x_limits = (
            bin_edges_vis[variable][0], bin_edges_vis[variable][-1])
        properties.x_axis_title = variables_latex[variable]
        if 'xsection' in measurement:
            properties.y_axis_title = r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + \
                variables_latex[variable] + '}$'
        else:
            properties.y_axis_title = r'$t\bar{t}$ normalisation'

        histograms = {'Combine before unfolding': h_combineBefore, 'Combine after unfolding': h_combineAfter}
        if add_before_unfolding:
            histograms['before unfolding'] = h_before_unfolding
            properties.name += '_ext'
            properties.has_ratio = False
        plot = Plot(histograms, properties)
        plot.draw_method = 'errorbar'
        compare_histograms(plot)

def compare_QCD_control_regions_to_MC():
    config = XSectionConfig(13)
    ctrl_e1 = 'TTbar_plus_X_analysis/EPlusJets/QCDConversions/FitVariables'
    ctrl_e2 = 'TTbar_plus_X_analysis/EPlusJets/QCD non iso e+jets/FitVariables'
    mc_e = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/FitVariables'
    data_file_e = config.data_file_electron_trees
    ttbar_file = config.ttbar_category_templates_trees['central']
    vjets_file = config.VJets_category_templates_trees['central']
    singleTop_file = config.SingleTop_category_templates_trees['central']
    qcd_file_e = config.electron_QCD_MC_tree_file

    ctrl_mu1 = 'TTbar_plus_X_analysis/MuPlusJets/QCD iso > 0.3/FitVariables'
    ctrl_mu2 = 'TTbar_plus_X_analysis/MuPlusJets/QCD 0.12 < iso <= 0.3/FitVariables'
    mc_mu = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/FitVariables'
    data_file_mu = config.data_file_muon_trees
    qcd_file_mu = config.muon_QCD_MC_tree_file
    weight_branches_electron = [
        "EventWeight",
        "PUWeight",
        "BJetWeight",
        "ElectronEfficiencyCorrection"
    ]
    weight_branches_mu = [
        "EventWeight",
        "PUWeight",
        "BJetWeight",
        "MuonEfficiencyCorrection"
    ]
    variables = ['MET', 'HT', 'ST', 'NJets',
                 'lepton_pt', 'abs_lepton_eta', 'WPT']
#     variables = ['abs_lepton_eta']
    for variable in variables:
        branch = variable
        selection = '{0} >= 0'.format(branch)
        if variable == 'abs_lepton_eta':
            branch = 'abs(lepton_eta)'
            selection = 'lepton_eta >= -3'
        for channel in ['electron', 'muon']:
            data_file = data_file_e
            qcd_file = qcd_file_e
            ctrl1 = ctrl_e1
            ctrl2 = ctrl_e2
            mc = mc_e
            weight_branches = weight_branches_electron
            if channel == 'muon':
                data_file = data_file_mu
                qcd_file = qcd_file_mu
                ctrl1 = ctrl_mu1
                ctrl2 = ctrl_mu2
                mc = mc_mu
                weight_branches = weight_branches_mu
            inputs = {
                'branch': branch,
                'weight_branches': weight_branches,
                'tree': ctrl1,
                'bin_edges': bin_edges_vis[variable],
                'selection': selection,
            }
            hs_ctrl1 = {
                'data': get_histogram_from_tree(input_file=data_file, **inputs),
                'TTJet': get_histogram_from_tree(input_file=ttbar_file, **inputs),
                'VJets': get_histogram_from_tree(input_file=vjets_file, **inputs),
                'SingleTop': get_histogram_from_tree(input_file=singleTop_file, **inputs),
                'QCD': get_histogram_from_tree(input_file=qcd_file, **inputs),
            }
            inputs['tree'] = ctrl2
            hs_ctrl2 = {
                'data': get_histogram_from_tree(input_file=data_file, **inputs),
                'TTJet': get_histogram_from_tree(input_file=ttbar_file, **inputs),
                'VJets': get_histogram_from_tree(input_file=vjets_file, **inputs),
                'SingleTop': get_histogram_from_tree(input_file=singleTop_file, **inputs),
                'QCD': get_histogram_from_tree(input_file=qcd_file, **inputs),
            }
            inputs['tree'] = mc
            h_qcd = get_histogram_from_tree(input_file=qcd_file, **inputs)

            h_ctrl1 = clean_control_region(
                hs_ctrl1,
                data_label='data',
                subtract=['TTJet', 'VJets', 'SingleTop'],
                fix_to_zero=True)
            h_ctrl2 = clean_control_region(
                hs_ctrl2,
                data_label='data',
                subtract=['TTJet', 'VJets', 'SingleTop'],
                fix_to_zero=True)
            n_qcd_ctrl1 = hs_ctrl1['QCD'].integral()
            n_qcd_ctrl2 = hs_ctrl2['QCD'].integral()
            n_data1 = h_ctrl1.integral()
            n_data2 = h_ctrl2.integral()
            n_qcd_sg = h_qcd.integral()

            ratio_ctrl1 = n_data1 / n_qcd_ctrl1
            ratio_ctrl2 = n_data2 / n_qcd_ctrl2
            qcd_estimate_ctrl1 = n_qcd_sg * ratio_ctrl1
            qcd_estimate_ctrl2 = n_qcd_sg * ratio_ctrl2
            h_ctrl1.Scale(qcd_estimate_ctrl1 / n_data1)
            h_ctrl2.Scale(qcd_estimate_ctrl2 / n_data2)

            properties = Histogram_properties()
            properties.name = 'compare_qcd_control_regions_to_mc_{0}_{1}_channel'.format(
                variable, channel)
            properties.title = 'Comparison of QCD control regions ({0} channel)'.format(
                channel)
            properties.path = 'plots'
            properties.has_ratio = False
            properties.xerr = True
            properties.x_limits = (
                bin_edges_vis[variable][0], bin_edges_vis[variable][-1])
            properties.x_axis_title = variables_latex[variable]
            properties.y_axis_title = 'number of QCD events'

            histograms = {'control region 1': h_ctrl1,
                          'control region 2': h_ctrl2,
                          'MC prediction': h_qcd}
            diff = absolute(h_ctrl1 - h_ctrl2)
            lower = h_ctrl1 - diff
            upper = h_ctrl1 + diff
            err_e = ErrorBand('uncertainty', lower, upper)
            plot_e = Plot(histograms, properties)
            plot_e.draw_method = 'errorbar'
            plot_e.add_error_band(err_e)
            compare_histograms(plot_e)


def compare_unfolding_uncertainties():
    file_template = '/hdfs/TopQuarkGroup/run2/dpsData/'
    file_template += 'data/normalisation/background_subtraction/13TeV/'
    file_template += '{variable}/VisiblePS/central/'
    file_template += 'unfolded_normalisation_combined_RooUnfold{method}.txt'

    variables = ['MET', 'HT', 'ST', 'NJets',
                 'lepton_pt', 'abs_lepton_eta', 'WPT']
#     variables = ['ST']
    for variable in variables:
        svd = file_template.format(
            variable=variable, method='Svd')
        bayes = file_template.format(
            variable=variable, method='Bayes')
        data = read_data_from_JSON(svd)
        before_unfolding = data['TTJet_measured_withoutFakes']
        svd_data = data['TTJet_unfolded']
        bayes_data = read_data_from_JSON(bayes)['TTJet_unfolded']

        before_unfolding = [e / v * 100 for v, e in before_unfolding]
        svd_data = [e / v * 100 for v, e in svd_data]
        bayes_data = [e / v * 100 for v, e in bayes_data]

        h_svd = value_tuplelist_to_hist(
            svd_data, bin_edges_vis[variable])
        h_bayes = value_tuplelist_to_hist(
            bayes_data, bin_edges_vis[variable])
        h_before_unfolding = value_tuplelist_to_hist(
            before_unfolding, bin_edges_vis[variable])

        properties = Histogram_properties()
        properties.name = 'compare_unfolding_uncertainties_{0}'.format(
            variable)
        properties.title = 'Comparison of unfolding uncertainties'
        properties.path = 'plots'
        properties.has_ratio = False
        properties.xerr = True
        properties.x_limits = (
            bin_edges_vis[variable][0], bin_edges_vis[variable][-1])
        properties.x_axis_title = variables_latex[variable]
        properties.y_axis_title = 'relative uncertainty (\\%)'
        properties.legend_location = (0.98, 0.95)

        histograms = {'SVD': h_svd, 'Bayes': h_bayes,
                      'before unfolding': h_before_unfolding}
        plot = Plot(histograms, properties)
        plot.draw_method = 'errorbar'
        compare_histograms(plot)

def compare_combine_before_after_unfolding_uncertainties():
    file_template = 'data/normalisation/background_subtraction/13TeV/'
    file_template += '{variable}/VisiblePS/central/'
    file_template += 'unfolded_normalisation_{channel}_RooUnfoldSvd.txt'

    variables = ['MET', 'HT', 'ST', 'NJets',
                 'lepton_pt', 'abs_lepton_eta', 'WPT']
#     variables = ['ST']
    for variable in variables:
        beforeUnfolding = file_template.format(
            variable=variable, channel='combinedBeforeUnfolding')
        afterUnfolding = file_template.format(
            variable=variable, channel='combined')
        data = read_data_from_JSON(beforeUnfolding)
        before_unfolding = data['TTJet_measured']
        beforeUnfolding_data = data['TTJet_unfolded']
        afterUnfolding_data = read_data_from_JSON(afterUnfolding)['TTJet_unfolded']

        before_unfolding = [e / v * 100 for v, e in before_unfolding]
        beforeUnfolding_data = [e / v * 100 for v, e in beforeUnfolding_data]
        afterUnfolding_data = [e / v * 100 for v, e in afterUnfolding_data]

        h_beforeUnfolding = value_tuplelist_to_hist(
            beforeUnfolding_data, bin_edges_vis[variable])
        h_afterUnfolding = value_tuplelist_to_hist(
            afterUnfolding_data, bin_edges_vis[variable])
        h_before_unfolding = value_tuplelist_to_hist(
            before_unfolding, bin_edges_vis[variable])

        properties = Histogram_properties()
        properties.name = 'compare_combine_before_after_unfolding_uncertainties_{0}'.format(
            variable)
        properties.title = 'Comparison of unfolding uncertainties'
        properties.path = 'plots'
        properties.has_ratio = False
        properties.xerr = True
        properties.x_limits = (
            bin_edges_vis[variable][0], bin_edges_vis[variable][-1])
        properties.x_axis_title = variables_latex[variable]
        properties.y_axis_title = 'relative uncertainty (\\%)'
        properties.legend_location = (0.98, 0.95)

        histograms = {'Combine before unfolding': h_beforeUnfolding, 'Combine after unfolding': h_afterUnfolding,
                      # 'before unfolding': h_before_unfolding
                      }
        plot = Plot(histograms, properties)
        plot.draw_method = 'errorbar'
        compare_histograms(plot)

def debug_last_bin():
    '''
        For debugging why the last bin in the problematic variables deviates a
        lot in _one_ of the channels only.
    '''
    file_template = '/hdfs/TopQuarkGroup/run2/dpsData/'
    file_template += 'data/normalisation/background_subtraction/13TeV/'
    file_template += '{variable}/VisiblePS/central/'
    file_template += 'normalised_xsection_{channel}_RooUnfoldSvd{suffix}.txt'
    problematic_variables = ['HT', 'MET', 'NJets', 'lepton_pt']

    for variable in problematic_variables:
        results = {}
        Result = namedtuple(
            'Result', ['before_unfolding', 'after_unfolding', 'model'])
        for channel in ['electron', 'muon', 'combined']:
            input_file_data = file_template.format(
                variable=variable,
                channel=channel,
                suffix='_with_errors',
            )
            input_file_model = file_template.format(
                variable=variable,
                channel=channel,
                suffix='',
            )
            data = read_data_from_JSON(input_file_data)
            data_model = read_data_from_JSON(input_file_model)
            before_unfolding = data['TTJet_measured_withoutFakes']
            after_unfolding = data['TTJet_unfolded']

            model = data_model['powhegPythia8']

            # only use the last bin
            h_before_unfolding = value_errors_tuplelist_to_graph(
                [before_unfolding[-1]], bin_edges_vis[variable][-2:])
            h_after_unfolding = value_errors_tuplelist_to_graph(
                [after_unfolding[-1]], bin_edges_vis[variable][-2:])
            h_model = value_error_tuplelist_to_hist(
                [model[-1]], bin_edges_vis[variable][-2:])

            r = Result(before_unfolding, after_unfolding, model)
            h = Result(h_before_unfolding, h_after_unfolding, h_model)
            results[channel] = (r, h)

        models = {'POWHEG+PYTHIA': results['combined'][1].model}
        h_unfolded = [results[channel][1].after_unfolding for channel in [
            'electron', 'muon', 'combined']]
        tmp_hists = spread_x(h_unfolded, bin_edges_vis[variable][-2:])
        measurements = {}
        for channel, hist in zip(['electron', 'muon', 'combined'], tmp_hists):
            value = results[channel][0].after_unfolding[-1][0]
            error = results[channel][0].after_unfolding[-1][1]
            label = '{c_label} ({value:1.2g} $\pm$ {error:1.2g})'.format(
                    c_label=channel,
                    value=value,
                    error=error,
            )
            measurements[label] = hist

        properties = Histogram_properties()
        properties.name = 'normalised_xsection_compare_channels_{0}_{1}_last_bin'.format(
            variable, channel)
        properties.title = 'Comparison of channels'
        properties.path = 'plots'
        properties.has_ratio = True
        properties.xerr = False
        properties.x_limits = (
            bin_edges_vis[variable][-2], bin_edges_vis[variable][-1])
        properties.x_axis_title = variables_latex[variable]
        properties.y_axis_title = r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + \
            variables_latex[variable] + '}$'
        properties.legend_location = (0.95, 0.40)
        if variable == 'NJets':
            properties.legend_location = (0.97, 0.80)
        properties.formats = ['png']

        compare_measurements(models=models, measurements=measurements, show_measurement_errors=True,
                             histogram_properties=properties, save_folder='plots/', save_as=properties.formats)


if __name__ == '__main__':
    import sys
    if '-d' in sys.argv:
        from dps.utils.logger import log
        log.setLevel(log.DEBUG)

    compare_combine_before_after_unfolding(measurement='unfolded_normalisation')
    compare_combine_before_after_unfolding(measurement='normalised_xsection')
    compare_combine_before_after_unfolding_uncertainties()
    compare_unfolding_methods('normalised_xsection')
    compare_unfolding_methods('normalised_xsection', add_before_unfolding=True)
    compare_unfolding_methods(
        'normalised_xsection', add_before_unfolding=True, channel='electron')
    compare_unfolding_methods(
        'normalised_xsection', add_before_unfolding=True, channel='muon')
    compare_unfolding_methods('unfolded_normalisation')
    compare_unfolding_methods(
        'unfolded_normalisation', add_before_unfolding=True)
    compare_unfolding_methods(
        'unfolded_normalisation', add_before_unfolding=True, channel='electron')
    compare_unfolding_methods(
        'unfolded_normalisation', add_before_unfolding=True, channel='muon')
    compare_QCD_control_regions_to_MC()
    compare_unfolding_uncertainties()
    debug_last_bin()
