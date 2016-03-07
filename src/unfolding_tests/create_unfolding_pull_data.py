'''
Created on 9 Dec 2012

@author: kreczko
'''
from __future__ import print_function
from optparse import OptionParser
from rootpy.io import File
from rootpy import asrootpy
from tools.Unfolding import Unfolding
from tools.hist_utilities import hist_to_value_error_tuplelist
from tools.file_utilities import write_data_to_JSON, make_folder_if_not_exists
from tools.Timer import Timer
from math import sqrt, log10
from time import time
from tools.ROOT_utils import set_root_defaults

from config import XSectionConfig


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
    parser.add_option("--tau", type='float',
                      dest="tau_value", default=-1.,
                      help="tau-value for SVD unfolding")
    parser.add_option("-m", "--method", type='string',
                      dest="method", default='TUnfold',
                      help="unfolding method")
    parser.add_option("-f", "--file", type='string',
                      dest="file", default='data/toy_mc/unfolding_toy_mc.root',
                      help="file with toy MC")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                      help="set the variable to analyse (defined in config/variable_binning.py)")
    parser.add_option("--com", "--centre-of-mass-energy", dest="CoM", default=13,
                      help='''set the centre of mass energy for analysis.
                      Default = 8 [TeV]''', type=int)
    parser.add_option("-c", "--channel", type='string',
                      dest="channel", default='combined',
                      help="channel to be analysed: electron|muon|combined")
    parser.add_option("-s", type='string',
                      dest="sample", default='madgraph',
                      help="channel to be analysed: electron|muon|combined")

    (options, _) = parser.parse_args()

    centre_of_mass = options.CoM
    measurement_config = XSectionConfig(centre_of_mass)
    make_folder_if_not_exists(options.output_folder)

    use_n_toy = options.n_input_mc
    method = options.method
    variable = options.variable
    sample = options.sample
    tau_value = options.tau_value

    create_unfolding_pull_data(options.file, method, options.channel,
                               centre_of_mass, variable,
                               sample,
                               measurement_config.unfolding_central,
                               use_n_toy,
                               options.output_folder,
                               tau_value)


def create_unfolding_pull_data(input_file_name, method, channel,
                               centre_of_mass, variable,
                               sample, 
                               responseFile,
                               n_toy_data,
                               output_folder, 
                               tau_value,
                                run_matrix=None):
    '''
        Sets up all variables for check_multiple_data_multiple_unfolding
    '''
    set_root_defaults(msg_ignore_level=3001)
    timer = Timer()
    input_file = File(input_file_name, 'read')
    folder_template = '{path}/{centre_of_mass}TeV/{variable}/{sample}/'

    msg_template = 'Producing unfolding pull data for {variable},'
    msg_template += ' tau-value {value}'
    inputs = {
        'path': output_folder,
        'centre_of_mass': centre_of_mass,
        'variable': variable,
        'sample': sample,
        'value': round(tau_value,4),
    }

    h_response = get_response_histogram(responseFile, variable, channel)
    output_folder = folder_template.format(**inputs)
    make_folder_if_not_exists(output_folder)
    print(msg_template.format(**inputs))
    print('Output folder: {0}'.format(output_folder))
    print ('Response here :',h_response)
    check_multiple_data_multiple_unfolding(
        input_file, method, channel, variable, 
        h_response,
        n_toy_data,
        output_folder, 
        tau_value,
    )
    print('Runtime', timer.elapsed_time())


def create_run_matrix(n_toy_mc, n_toy_data
    ):
    mc_range = range(0, n_toy_mc + 1)
    data_range = range(0, n_toy_data + 1)
    for mc in mc_range:
        for data in data_range:
            yield (mc, data)


def check_multiple_data_multiple_unfolding(
        input_file, method, channel, variable,
        responseMatrix,
        n_toy_data, output_folder,
        tau_value=-1
        ):
    '''
        Loops through a n_toy_data of pseudo data, 
        unfolds the pseudo data and compares it to the MC truth
    '''
    # same unfolding input, different data
    get_folder = input_file.Get
    pulls = []
    add_pull = pulls.append
    histograms = []
    add_histograms = histograms.append

    print('Reading toy MC')
    start1 = time()
    data_range = range(0, n_toy_data)
    for nth_toy_data in range(0, n_toy_data + 1):  # read all of them (easier)
        if nth_toy_data in data_range:
            tpl = '{channel}/{variable}/toy_{nth}'
            folder_mc = tpl.format(channel=channel, variable=variable,
                                   nth=nth_toy_data+1)
            folder_mc = get_folder(folder_mc)
            add_histograms(get_measured_histogram(folder_mc))
        else:
            add_histograms(0)
    print('Done reading toy MC in', time() - start1, 's')


    h_truth = get_truth_histogram( get_folder('{channel}/{variable}/Original'.format(channel=channel, variable=variable) ) )
    h_response = responseMatrix
    for nth_toy_data in data_range:
        if nth_toy_data % 100 == 0 :
            print(
                'Doing data no', nth_toy_data)
        h_data = histograms[nth_toy_data]

        unfolding_obj = Unfolding(
            h_data,
            h_truth, h_data, h_response, method=method, k_value=-1,
            tau=tau_value)
        unfold, get_pull = unfolding_obj.unfold, unfolding_obj.pull
        reset = unfolding_obj.Reset


        unfold()
        pull = get_pull()
        diff = unfolding_obj.unfolded_data - unfolding_obj.truth
        diff_tuple = hist_to_value_error_tuplelist(diff)

        truth_tuple = hist_to_value_error_tuplelist(unfolding_obj.truth)

        bias = []
        sumBias2 = 0
        for d, t in zip(diff_tuple, truth_tuple):
            b = d[0] / t[0]
            bias.append(b)

        unfolded = unfolding_obj.unfolded_data
        unfolded_tuple = hist_to_value_error_tuplelist(unfolded)
        all_data = {'unfolded': unfolded_tuple,
                    'difference': diff_tuple,
                    'truth': truth_tuple,
                    'bias':bias,
                    'pull': pull,
                    'nth_toy_data': nth_toy_data
                    }

        add_pull(all_data)
        reset()

    save_pulls(pulls, method,
               channel, tau_value, output_folder)


def save_pulls(pulls, method, channel, tau_value, output_folder):
    '''
        Saves pull distributions in JSON format
    '''
    file_template = 'Pull_data_%s_%s_%.4g.txt'
    output_file = output_folder + \
        file_template % (method, channel, tau_value)
    write_data_to_JSON(pulls, output_file)
    print('Pulls saved in file: ', output_file)

def get_response_histogram(responseFileName, variable, channel):
    '''
        clones the response matrix from file
    '''
    responseFile = File(responseFileName, 'read')
    folder = '{variable}_{channel}'.format( variable = variable, channel = channel )
    h_response = responseFile.Get(folder).responseVis_without_fakes.Clone()
    return asrootpy( h_response )


def get_truth_histogram(folder):
    '''
        clones the pseudo data histogram given a TDirectory
        @folder: A directory containting the histograms 'truth'
    '''
    h_response = folder.response.Clone()
    h_truth = asrootpy( h_response.ProjectionY() )
    return h_truth

def get_measured_histogram(folder):
    '''
        clones the pseudo data histogram given a TDirectory
        @folder: A directory containting the histograms 'measured'
    '''
    h_measured = asrootpy( folder.measured.Clone() )

    return h_measured

if __name__ == "__main__":
    main()
