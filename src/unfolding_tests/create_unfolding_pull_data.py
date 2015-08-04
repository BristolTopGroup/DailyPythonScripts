'''
Created on 9 Dec 2012

@author: kreczko
'''
from __future__ import print_function
from optparse import OptionParser
from rootpy.io import File
from tools.Unfolding import Unfolding
from tools.hist_utilities import hist_to_value_error_tuplelist
from tools.file_utilities import write_data_to_JSON, make_folder_if_not_exists
from tools.Timer import Timer

from time import time
from tools.ROOT_utils import set_root_defaults


def main():
    '''
        Main function for this script
    '''
    set_root_defaults(msg_ignore_level=3001)

    parser = OptionParser()
    parser.add_option("-o", "--output",
                      dest="output_folder", default='data/pull_data/',
                      help="output folder for pull data files")
    parser.add_option("-n", "--n_input_mc", type=int,
                      dest="n_input_mc", default=100,
                      help="number of toy MC used for the tests")
    parser.add_option("-k", "--k_value", type=int,
                      dest="k_value", default=3,
                      help="k-value for SVD unfolding")
    parser.add_option("--tau", type='float',
                      dest="tau_value", default=-1.,
                      help="tau-value for SVD unfolding")
    parser.add_option("-m", "--method", type='string',
                      dest="method", default='RooUnfoldSvd',
                      help="unfolding method")
    parser.add_option("-f", "--file", type='string',
                      dest="file", default='data/toy_mc/unfolding_toy_mc.root',
                      help="file with toy MC")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                      help="set the variable to analyse (MET, HT, ST, MT, WPT)")
    parser.add_option("-s", "--centre-of-mass-energy", dest="CoM", default=8,
                      help='''set the centre of mass energy for analysis.
                      Default = 8 [TeV]''', type=int)
    parser.add_option("-c", "--channel", type='string',
                      dest="channel", default='combined',
                      help="channel to be analysed: electron|muon|combined")

    parser.add_option("--offset_toy_mc", type=int,
                      dest="offset_toy_mc", default=0,
                      help="offset of the toy MC used to response matrix")
    parser.add_option("--offset_toy_data", type=int,
                      dest="offset_toy_data", default=0,
                      help="offset of the toy MC used as data for unfolding")
    (options, _) = parser.parse_args()

    centre_of_mass = options.CoM
    make_folder_if_not_exists(options.output_folder)

    # set the number of toy MC for error calculation
    k_value = options.k_value
    tau_value = options.tau_value
    use_n_toy = options.n_input_mc
    offset_toy_mc = options.offset_toy_mc
    offset_toy_data = options.offset_toy_data
    method = options.method
    variable = options.variable

    create_unfolding_pull_data(options.file, method, options.channel,
                               centre_of_mass, variable, use_n_toy, use_n_toy,
                               options.output_folder, offset_toy_mc,
                               offset_toy_data, k_value, tau_value)


def create_unfolding_pull_data(input_file_name, method, channel,
                               centre_of_mass, variable, n_toy_mc, n_toy_data,
                               output_folder, offset_toy_mc, offset_toy_data,
                               k_value, tau_value=-1, run_matrix=None):
    '''
        Sets up all variables for check_multiple_data_multiple_unfolding
    '''
    timer = Timer()
    input_file = File(input_file_name, 'read')
    folder_template = '{path}/{centre_of_mass}TeV/{variable}/'
    folder_template += '{n_toy_mc}_input_toy_mc/{n_toy_data}_input_toy_data/'
    folder_template += '{vtype}_value_{value}/'

    msg_template = 'Producing unfolding pull data for {variable},'
    msg_template += ' {vtype}-value {value}'
    inputs = {
        'path': output_folder,
        'centre_of_mass': centre_of_mass,
        'variable': variable,
        'n_toy_mc': n_toy_mc,
        'n_toy_data': n_toy_data,
        'vtype': 'k',
        'value': k_value,
    }
    if tau_value >= 0:
        inputs['vtype'] = 'tau'
        inputs['value'] = round(tau_value, 1)

    output_folder = folder_template.format(**inputs)
    make_folder_if_not_exists(output_folder)
    print(msg_template.format(**inputs))
    print('Output folder: {0}'.format(output_folder))

    check_multiple_data_multiple_unfolding(
        input_file, method, channel, variable, n_toy_mc, n_toy_data,
        output_folder, offset_toy_mc, offset_toy_data, k_value, tau_value,
        run_matrix,
    )
    print('Runtime', timer.elapsed_time())


def create_run_matrix(n_toy_mc, n_toy_data, offset_toy_mc, offset_toy_data):
    mc_range = range(offset_toy_mc + 1, offset_toy_mc + n_toy_mc + 1)
    data_range = range(offset_toy_data + 1, offset_toy_data + n_toy_data + 1)
    for mc in mc_range:
        for data in data_range:
            yield (mc, data)


def check_multiple_data_multiple_unfolding(
        input_file, method, channel, variable,
        n_toy_mc, n_toy_data, output_folder,
        offset_toy_mc, offset_toy_data,
        k_value, tau_value=-1,
        run_matrix=None):
    '''
        Loops through a n_toy_mc x n_toy_data matrix of pseudo data versus
        simulation, unfolds the pseudo data and compares it to the MC truth
    '''
    # same unfolding input, different data
    get_folder = input_file.Get
    pulls = []
    add_pull = pulls.append
    histograms = []
    add_histograms = histograms.append

    print('Reading toy MC')
    start1 = time()
    mc_range = range(offset_toy_mc + 1, offset_toy_mc + n_toy_mc + 1)
    data_range = range(offset_toy_data + 1, offset_toy_data + n_toy_data + 1)
    for nth_toy_mc in range(1, 10000 + 1):  # read all of them (easier)
        if nth_toy_mc in mc_range or nth_toy_mc in data_range:
            tpl = '{channel}/{variable}/toy_{nth}'
            folder_mc = tpl.format(channel=channel, variable=variable,
                                   nth=nth_toy_mc)
            folder_mc = get_folder(folder_mc)
            add_histograms(get_histograms(folder_mc))
        else:
            add_histograms((0, 0, 0))
    print('Done reading toy MC in', time() - start1, 's')

    if not run_matrix:
        run_matrix = create_run_matrix(n_toy_mc, n_toy_data, offset_toy_mc,
                                       offset_toy_data)

    for nth_toy_mc, nth_toy_data in run_matrix:
        h_truth, h_measured, h_response = histograms[nth_toy_mc - 1]
        if tau_value >= 0:
            unfolding_obj = Unfolding(
                h_truth, h_measured, h_response, method=method, k_value=-1,
                tau=tau_value)
        else:
            unfolding_obj = Unfolding(
                h_truth, h_measured, h_response, method=method, k_value=k_value)
        unfold, get_pull = unfolding_obj.unfold, unfolding_obj.pull
        reset = unfolding_obj.Reset

        if nth_toy_data == nth_toy_mc:
            continue
        print(
            'Doing MC no, ' + str(nth_toy_mc) + ', data no', nth_toy_data)
        h_data = histograms[nth_toy_data - 1][1]
        unfold(h_data)
        pull = get_pull()
        diff = unfolding_obj.unfolded_data - unfolding_obj.truth
        diff_tuple = hist_to_value_error_tuplelist(diff)
        unfolded = unfolding_obj.unfolded_data
        unfolded_tuple = hist_to_value_error_tuplelist(unfolded)
        all_data = {'unfolded': unfolded_tuple,
                    'difference': diff_tuple,
                    'pull': pull,
                    'nth_toy_mc': nth_toy_mc,
                    'nth_toy_data': nth_toy_data
                    }

        add_pull(all_data)
        reset()

    save_pulls(pulls, 'multiple_data_multiple_unfolding', method,
               channel, output_folder, n_toy_mc, n_toy_data, offset_toy_mc,
               offset_toy_data)


def save_pulls(pulls, test, method, channel, output_folder, n_toy_mc,
               n_toy_data, offset_toy_mc, offset_toy_data):
    '''
        Saves pull distributions in JSON format
    '''
    file_template = 'Pulls_%s_%s_%s_toy_MC_%d_to_%d_MC_%d_to_%d_data.txt'
    output_file = output_folder + \
        file_template % (test, method, channel, offset_toy_mc + 1, n_toy_mc +
                         offset_toy_mc, offset_toy_data + 1,
                         n_toy_data + offset_toy_data)
    write_data_to_JSON(pulls, output_file)
    print('Pulls saved in file: ', output_file)


def get_histograms(folder):
    '''
        clones the triplet of unfolding histograms given a TDirectory
        @folder: A directory containting the histograms 'truth', 
        'measured' and 'response'
    '''
    h_truth = folder.truth.Clone()
    h_measured = folder.measured.Clone()
    h_response = folder.response.Clone()

    return h_truth, h_measured, h_response

if __name__ == "__main__":
    main()
