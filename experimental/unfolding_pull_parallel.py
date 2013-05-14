'''
Created on 9 Dec 2012

@author: kreczko
'''
from optparse import OptionParser
import os
from rootpy.io import File
from array import array
from tools.Unfolding import Unfolding
from config import RooUnfold
from tools.file_utilities import write_data_to_JSON
import multiprocessing

def check_multiple_data_multiple_unfolding(input_file, method, channel):
    global nbins, use_N_toy, skip_N_toy, output_folder
    # same unfolding input, different data
    get_folder = input_file.Get
    pulls = []
    add_pull = pulls.append
    histograms = []
    add_histograms = histograms.append
    
    for nth_toy_mc in range(skip_N_toy + 1, skip_N_toy + use_N_toy + 1):
        folder_mc = get_folder(channel + '/toy_%d' % nth_toy_mc)
        add_histograms(get_histograms(folder_mc))
           
    for nth_toy_mc in range(skip_N_toy + 1, skip_N_toy + use_N_toy + 1):
        print 'Doing MC no', nth_toy_mc
        h_truth, h_measured, h_response = histograms[nth_toy_mc - 1 - skip_N_toy]
        unfolding_obj = Unfolding(h_truth, h_measured, h_response, method=method)
        pool = multiprocessing.Pool(4)
        pull = pool.map(get_pull, range(skip_N_toy + 1, skip_N_toy + use_N_toy + 1))
#        for nth_toy_data in range(skip_N_toy + 1, skip_N_toy + use_N_toy + 1):
#            pull = get_pull(unfolding_obj, histograms, nth_toy_mc, nth_toy_data)
#            add_pull(pull)
    save_pulls(pulls, test='multiple_data_multiple_unfolding', method=method, channel=channel)

def get_pull(unfolding_obj, histograms, nth_toy_mc, nth_toy_data):
    if nth_toy_data == nth_toy_mc:
        continue
    h_data = histograms[nth_toy_data - 1 - skip_N_toy][1]
    unfolding_obj.unfold(h_data)
    pull = unfolding_obj.pull()
    unfolding_obj.Reset()
    return pull

def save_pulls(pulls, test, method, channel):    
    global use_N_toy, skip_N_toy
    file_template = 'Pulls_%s_%s_%s_toy_MC_%d_to_%d.txt'
    output_file = output_folder + file_template % (test, method, channel, skip_N_toy + 1, use_N_toy + skip_N_toy)
    write_data_to_JSON(pulls, output_file)
    
def get_histograms(folder):
    h_truth = folder.truth.Clone()
    h_measured = folder.measured.Clone()
    h_response = folder.response_withoutFakes_AsymBins.Clone()
    
    return h_truth, h_measured, h_response

if __name__ == "__main__":
    from ROOT import gROOT
    gROOT.SetBatch(True)
    gROOT.ProcessLine("gErrorIgnoreLevel = 3001;");
    bins = array('d', [0, 25, 45, 70, 100, 1000])
    nbins = len(bins) - 1
    
    
    parser = OptionParser()
    parser.add_option("-n", "--n_input_mc", type='int',
                      dest="n_input_mc", default=100,
                      help="number of toy MC used for the tests")
    parser.add_option("-s", "--skip_mc", type='int',
                      dest="skip_mc", default=0,
                      help="skip first n toy MC used for the tests")
    parser.add_option("-e", "--error_toy_MC", type='int',
                      dest="error_toy_MC", default=1000,
                      help="number of toy MC used for the error calculation in SVD unfolding")
    parser.add_option("-k", "--k_value", type='int',
                      dest="k_value", default=6,
                      help="k-value for SVD unfolding")
    parser.add_option("-m", "--method", type='string',
                      dest="method", default='RooUnfoldSvd',
                      help="unfolding method")
    parser.add_option("-f", "--file", type='string',
                      dest="file", default='../data/unfolding_toy_mc.root',
                      help="file with toy MC")
    parser.add_option("-c", "--channel", type='string',
                      dest="channel", default='both',
                      help="channel to be analysed: electron|muon|both")
    (options, args) = parser.parse_args()
    
    # set the number of toy MC for error calculation
    RooUnfold.SVD_n_toy = options.error_toy_MC
    RooUnfold.SVD_k_value = options.k_value
    use_N_toy = options.n_input_mc
    skip_N_toy = options.skip_mc
    method = options.method
    
    output_folder = 'plots/%d_input_toy_mc/k_value_%d/%d_error_toy_MC/' % (use_N_toy, RooUnfold.SVD_k_value, RooUnfold.SVD_n_toy)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    input_file = input_file = File(options.file, 'read')
    
#    check_one_data_multiple_unfolding(input_file, method, 'electron')
#    check_multiple_data_one_unfolding(input_file, method, 'electron')
#    check_one_data_multiple_unfolding(input_file, method, 'muon')
#    check_multiple_data_one_unfolding(input_file, method, 'muon')
    
    from time import clock, time
    start1, start2 = clock(), time()
    if options.channel == 'electron':
        check_multiple_data_multiple_unfolding(input_file, method, 'electron')
    elif options.channel == 'muon':
        check_multiple_data_multiple_unfolding(input_file, method, 'muon')
    else:
        check_multiple_data_multiple_unfolding(input_file, method, 'electron')
        check_multiple_data_multiple_unfolding(input_file, method, 'muon')
    end1, end2 = clock(), time()
    
    print 'Runtime', end1 - start1
    print 'Runtime', end2 - start2
    
