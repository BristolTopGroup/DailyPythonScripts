'''
    Script to make plots from unfolding pull JSON files. Will output
     - difference_errors_stats_#.pdf
     - difference_stats_#.pdf
     - pull_distributino_mean_and_sigma_<variable>_<channel>_<centre of mass energy>TeV
     - pull_from_files_all_bins_stats_#.pdf
     - pull_from_files_bin_X_stats_#.pdf
     into output_folder/<centre of mass energy>TeV/<variable>/<channel>/
    
    Usage:
        python src/unfolding_tests/make_unfolding_pull_plots.py <input files>\
        -s <centre of mass energy> -c <channel> -o <output folder> \
        -v <variable>
    
    Example:
        python src/unfolding_tests/make_unfolding_pull_plots.py data/pull_data/13TeV/HT/electron/*.txt -s 13 -c electron -o plots/pull_plots/ -v HT
'''
from __future__ import division, print_function
from tools.ROOT_utils import set_root_defaults
from optparse import OptionParser
from glob import glob
import sys

import matplotlib as mpl
from tools.plotting import Histogram_properties, compare_measurements
mpl.use('agg')

import numpy
from numpy import frompyfunc
from pylab import plot
from array import array

from rootpy.plotting import Hist
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt


from config.variable_binning import bin_edges
from config import CMS, latex_labels, XSectionConfig
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from tools.hist_utilities import value_error_tuplelist_to_hist, make_line_hist
from tools.latex import setup_matplotlib

setup_matplotlib()


class fitResults:

    def __init__(self, fit_pull):
        self.A = fit_pull.GetParameter(0)
        self.Aerror = fit_pull.GetParError(0)
        self.mean = fit_pull.GetParameter(1)
        self.meanError = fit_pull.GetParError(1)
        self.sigma = fit_pull.GetParameter(2)
        self.sigmaError = fit_pull.GetParError(2)

    def __str__(self):
        text = 'A:     {0} +- {1}\n'.format(self.A, self.Aerror)
        text += 'mean: {0} +- {1}\n'.format(self.mean, self.meanError)
        text += 'sigma: {0} +- {1}\n'.format(self.sigma, self.sigmaError)
        return text

    def toDict(self):
        d = {
            'A': (self.A, self.Aerror),
            'mean': (self.mean, self.meanError),
            'sigma': (self.sigma, self.sigmaError)
        }
        return d


def main():
    parser = OptionParser(__doc__)
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                      help="set the variable to analyse (MET, HT, ST, MT, WPT)")
    parser.add_option("-s", "--centre-of-mass-energy", dest="CoM", default=8,
                      help="set the centre of mass energy for analysis. Default = 8 [TeV]", type=int)
    parser.add_option("-o", "--output",
                      dest="output_folder", default='plots/unfolding_pulls',
                      help="output folder for unfolding pull plots")
    parser.add_option("-c", "--channel", type='string',
                      dest="channel", default='combined',
                      help="channel to be analysed: electron|muon|combined")
    parser.add_option("-k", "--k_value", type='int',
                      dest="k_value", default=-1,
                      help="k-value used in SVD unfolding, only for categorisation purpose at this stage")
    parser.add_option("--tau", type='float',
                      dest="tau_value", default=-1.,
                      help="tau-value for SVD unfolding")

    (options, args) = parser.parse_args()
#     measurement_config = XSectionConfig(options.CoM)

    if len(args) == 0:
        print('No input files specified.')
        print('Run script with "-h" for usage')
        sys.exit(-1)
    files = args
    centre_of_mass = options.CoM
    variable = options.variable
    channel = options.channel
    config = XSectionConfig(centre_of_mass)
    k_value = get_k_value(options.k_value, config, channel, variable)
    tau_value = get_tau_value(options.tau_value, config, channel, variable)

    output_folder = '{option_output}/{centre_of_mass}TeV/{variable}/{channel}/'
    output_folder = output_folder.format(option_output=options.output_folder,
                                         centre_of_mass=centre_of_mass,
                                         variable=variable,
                                         channel=channel)
    make_folder_if_not_exists(output_folder)
    output_formats = ['pdf']

    bins = array('d', bin_edges[variable])
    nbins = len(bins) - 1

    msg = 'Producing unfolding pull plots for {0} variable, channel: {1}'
    print(msg.format(variable, channel))
    value = get_value_title(k_value, tau_value)
    print('Using {0}'.format(value))
    print ('Output folder: {0}'.format(output_folder))

    pulls = get_data(files, subset='pull')

    fit_results = []
    for bin_i in range(0, nbins):
        fr = plot_pull(pulls, centre_of_mass, channel, variable, k_value,
                       tau_value, output_folder, output_formats,
                       bin_index=bin_i, n_bins=nbins)
        fit_results.append(fr)

    plot_fit_results(fit_results, centre_of_mass, channel, variable, k_value, tau_value,
                     output_folder, output_formats, bins)
    # plot all bins
    plot_pull(pulls, centre_of_mass, channel, variable, k_value, tau_value,
              output_folder, output_formats)
    del pulls  # deleting to make space in memory

    difference = get_data(files, subset='difference')
    plot_difference(difference, centre_of_mass, channel, variable, k_value,
                    tau_value, output_folder, output_formats)


def get_k_value(k_value, config, channel, variable):
    if k_value > 0:
        return k_value
    if channel == 'electron':
        k_values = config.k_values_electron
    else:
        k_values = config.k_values_muon
    if k_values.has_key(variable):
        k_value = k_values[variable]


def get_tau_value(tau_value, config, channel, variable):
    if tau_value >= 0:
        return tau_value
    if channel == 'electron':
        tau_values = config.tau_values_electron
    else:
        tau_values = config.tau_values_muon
    if tau_values.has_key(variable):
        tau_value = tau_values[variable]
    return tau_value


def get_value_title(k_value, tau_value):
    if tau_value >= 0:  # prefer tau
        value = 'tau-value = {0}'.format(round(tau_value, 1))
    else:
        value = 'k-value = {0}'.format(k_value)
    return value


def get_data(files, subset=''):
    # this takes a LOT of memory, please use subset!!
    all_data = []
    extend = all_data.extend
    for f in files:
        data = read_data_from_JSON(f)

        if subset:
            for entry in data:  # loop over all data entries
                extend(entry[subset])
        else:
            extend(data)

    return all_data


def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step


def plot_fit_results(fit_results, centre_of_mass, channel, variable, k_value,
                     tau_value, output_folder, output_formats, bin_edges):
    h_mean = Hist(bin_edges, type='D')
    h_sigma = Hist(bin_edges, type='D')
    n_bins = h_mean.nbins()
    assert len(fit_results) == n_bins
    for i, fr in enumerate(fit_results):
        h_mean.SetBinContent(i + 1, fr.mean)
        h_mean.SetBinError(i + 1, fr.meanError)
        h_sigma.SetBinContent(i + 1, fr.sigma)
        h_sigma.SetBinError(i + 1, fr.sigmaError)
    histogram_properties = Histogram_properties()
    name_mpt = 'pull_distribution_mean_and_sigma_{0}_{1}_{2}TeV'
    histogram_properties.name = name_mpt.format(
        variable,
        channel,
        centre_of_mass
    )
    histogram_properties.y_axis_title = r'$\mu_{\text{pull}}$ ($\sigma_{\text{pull}}$)'
    histogram_properties.x_axis_title = latex_labels.variables_latex[variable]
    value = get_value_title(k_value, tau_value)
    title = 'pull distribution mean \& sigma for {0}'.format(value)
    histogram_properties.title = title
    histogram_properties.y_limits = [-0.5, 2]
    histogram_properties.xerr = True

    compare_measurements(
        models={
            'ideal $\mu$': make_line_hist(bin_edges, 0),
            'ideal $\sigma$': make_line_hist(bin_edges, 1)
        },
        measurements={
            r'$\mu_{\text{pull}}$': h_mean,
            r'$\sigma_{\text{pull}}$': h_sigma
        },
        show_measurement_errors=True,
        histogram_properties=histogram_properties,
        save_folder=output_folder,
        save_as=output_formats)


def plot_pull(pulls, centre_of_mass, channel, variable, k_value, tau_value,
              output_folder, output_formats,
              bin_index=None, n_bins=1):
    min_x, max_x = min(pulls), max(pulls)
    abs_max = int(max(abs(min_x), max_x))
    if abs_max < 1:
        abs_max = 1
    n_x_bins = 2 * abs_max * 10  # bin width = 0.1
#     print(n_x_bins, -abs_max, abs_max)
    h_pull = Hist(n_x_bins, -abs_max, abs_max)
    filling = h_pull.Fill
    stats = 0

    for pull_index, pull in enumerate(pulls):
        if not bin_index is None:
            matches_bin = (pull_index - bin_index) % (n_bins) == 0
            if pull_index < n_bins:  # first set correction
                matches_bin = pull_index == bin_index
            if not matches_bin:
                continue
        filling(pull)
        stats += 1

#    printstats
#    h_list = hist_to_value_error_tuplelist(h_pull)
#    printh_list
#    printlen(hist_data), min(hist_data), max(hist_data)
    fr = None
    if bin_index is None:
        fr = plot_h_pull(h_pull, centre_of_mass, channel, variable, k_value,
                         tau_value, output_folder,
                         output_formats, stats=stats,
                         name='pull_from_files_all_bins_stats_%d' % stats)
    else:
        fr = plot_h_pull(h_pull, centre_of_mass, channel, variable, k_value,
                         tau_value, output_folder,
                         output_formats, stats=stats,
                         name='pull_from_files_bin_%d_stats_%d' % (bin_index, stats))

    return fr


def plot_pull_from_list(hist_data, hist_min_x, hist_max_x, hist_n_bins):
    stats = 19596500
    bin_width = (2.0 * hist_max_x) / hist_n_bins
    print(hist_n_bins, bin_width)
    bin_edges = list(drange(hist_min_x, hist_max_x, bin_width))
    print(bin_edges)
    print(len(bin_edges))
    h_pull = value_error_tuplelist_to_hist(hist_data, bin_edges)
    plot_h_pull(h_pull, stats=stats, name='pull_from_list')


def plot_h_pull(h_pull, centre_of_mass, channel, variable, k_value, tau_value,
                output_folder, output_formats, stats=19596500, name='pull_test'):
    h_pull.Fit('gaus', 'WWSQ')
    fit_pull = h_pull.GetFunction('gaus')
    fr = fitResults(fit_pull)
    mean = (fr.mean, fr.meanError)
    sigma = (fr.sigma, fr.sigmaError)
    print('Fit data for "' + name + '"')
    print(str(fr))

    plt.figure(figsize=(16, 16), dpi=200, facecolor='white')
    axes = plt.axes()
    h_pull.SetMarkerSize(CMS.data_marker_size)
    rplt.errorbar(h_pull, xerr=True, emptybins=True, axes=axes)

    # *4 for a very smooth curve
    x = numpy.linspace(
        fit_pull.GetXmin(), fit_pull.GetXmax(), fit_pull.GetNpx() * 4)
    function_data = frompyfunc(fit_pull.Eval, 1, 1)
    plot(x, function_data(x), axes=axes, color='red', linewidth=2)

    plt.xlabel(
        '$\\frac{N^{\mathrm{unfolded}} - N^{\mathrm{true}}}{\sigma}$',
        CMS.x_axis_title)
    plt.ylabel('number of toy experiments', CMS.y_axis_title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)

    channel_label = latex_labels.channel_latex[channel]
    var_label = latex_labels.variables_latex[variable]
    title_template = 'Pull distribution for unfolding of {variable}\n'
    title_template += '$\sqrt{{s}}$ = {com} TeV, {channel}, {value}'
    title = title_template.format(
        variable=var_label,
        com=centre_of_mass,
        channel=channel_label,
        value=get_value_title(k_value, tau_value)
    )
    plt.title(title, CMS.title)

    text_template = 'entries = {stats}\n'
    text_template += 'mean = ${mean} \pm  {mean_error}$\n'
    text_template += '$\sigma = {sigma} \pm  {sigma_error}$'
    text = text_template.format(
        stats=stats,
        mean=round(mean[0], 2),
        mean_error=round(mean[1], 2),
        sigma=round(sigma[0], 2),
        sigma_error=round(sigma[1], 2),
    )
    axes.text(0.6, 0.8, text,
              verticalalignment='bottom', horizontalalignment='left',
              transform=axes.transAxes,
              color='black', fontsize=40, bbox=dict(facecolor='white', edgecolor='none', alpha=0.5))
    plt.tight_layout()

    for save in output_formats:
        plt.savefig(output_folder + name + '.' + save)

    return fr


def plot_difference(difference, centre_of_mass, channel, variable, k_value, tau_value,
                    output_folder, output_formats):
    stats = len(difference)
    values, errors = [], []
    add_value = values.append
    add_error = errors.append
    for value, error in difference:
        add_value(value)
        add_error(error)
    min_x, max_x = min(values), max(values)
    abs_max = int(max(abs(min_x), max_x))
#    n_x_bins = 2 * abs_max * 10
    h_values = Hist(100, -abs_max, abs_max)
    fill_value = h_values.Fill
    for value in values:
        fill_value(value)

    plt.figure(figsize=(16, 16), dpi=200, facecolor='white')
    axes = plt.axes()
    h_values.SetMarkerSize(CMS.data_marker_size)
    rplt.errorbar(h_values, xerr=True, emptybins=True, axes=axes)

    channel_label = latex_labels.channel_latex[channel]
    var_label = latex_labels.variables_latex[variable]
    title_template = 'SVD unfolding performance for unfolding of {variable}\n'
    title_template += '$\sqrt{{s}}$ = {com} TeV, {channel}, {value}'
    title = title_template.format(
        variable=var_label,
        com=centre_of_mass,
        channel=channel_label,
        value=get_value_title(k_value, tau_value)
    )

    plt.xlabel('$\mathrm{unfolded} - \mathrm{true}$', CMS.x_axis_title)
    plt.ylabel('number of toy experiments', CMS.y_axis_title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    plt.title(title, CMS.title)
    plt.tight_layout()

    for save in output_formats:
        plt.savefig(
            output_folder + 'difference_stats_' + str(stats) + '.' + save)

    min_x, max_x = min(errors), max(errors)
    h_errors = Hist(1000, min_x, max_x)
    fill_value = h_errors.Fill
    for error in errors:
        fill_value(error)

    plt.figure(figsize=(16, 16), dpi=200, facecolor='white')
    axes = plt.axes()
    h_errors.SetMarkerSize(CMS.data_marker_size)
    rplt.errorbar(h_errors, xerr=True, emptybins=True, axes=axes)

    plt.xlabel('$\sigma(\mathrm{unfolded} - \mathrm{true})$', CMS.x_axis_title)
    plt.ylabel('number of toy experiments', CMS.y_axis_title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    plt.title(title_template, CMS.title)

    plt.tight_layout()

    for save in output_formats:
        plt.savefig(
            output_folder + 'difference_errors_stats_' + str(stats) + '.' + save)


if __name__ == "__main__":
    set_root_defaults()
    main()
