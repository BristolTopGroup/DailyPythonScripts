'''
Created on 15 Jan 2013

@author: kreczko

- sum up the b-tag multiplicity bins
- sum up the different samples
'''

#rootpy very slow
#from rootpy.io import File
from rootpy.logger import logging
from ROOT import TFile, gROOT
from argparse import ArgumentParser
from dps.utils.file_utilities import make_folder_if_not_exists, get_files_in_path, merge_ROOT_files, get_process_from_file

File = TFile.Open
gcd = gROOT.cd


def sum_b_tag_bins_in_file(file_in_path):
    global existing_bins, to_be_created, existing_histogram_file, input_folder, output_folder
    logging.debug('Processing file %s' % file_in_path)
    
    output_file_name = file_in_path.replace('.root', '_summed.root')
    output_file_name = output_file_name.replace(input_folder, output_folder)
    #run rootinfo on file
    #or read the output (histogram list)
    input_file = open(existing_histogram_file) 
    seen_summed_hists = False
    histogram_set = get_set_of_histogram_paths(input_file, seen_summed_hists)
    logging.debug('Found %d unique b-tag binned histograms' %len(histogram_set)) 
    if seen_summed_hists:
        logging.warn('Summed histograms have been detected. Will skip this part')
        return
    input_file.close()
    
    directories = []
    for path in histogram_set:
        histogram_path, histogram_name, b_tag_bin = get_histogram_info_tuple(path)
        directories.append(histogram_path)
    
    logging.debug('opening file %s ' % output_file_name) 
    output_file = File(output_file_name, 'recreate')
    cd = output_file.cd
        
    logging.debug( 'creating folder structure') 
    create_folder_structure(output_file, directories)
    logging.debug( 'created folder structure')
    
    logging.debug('opening file %s ' % file_in_path) 
    input_file = File(file_in_path, 'read')
    get_histogram = input_file.Get
    logging.debug('opened file')
     
    new_histograms = {}
    for histogram in histogram_set:
        cd()
        logging.debug('Processing histogram: %s' % histogram)
        histogram_path, histogram_name, b_tag_bin = get_histogram_info_tuple(histogram)
        logging.debug('Found histogram_path %s' % histogram_path)
        logging.debug('Found histogram_name %s' % histogram_name)
        cd(histogram_path)
        existing_histograms = [get_histogram(histogram + '_' + existing_bin).Clone() for existing_bin in existing_bins]
        for bin_i, b_tag_bin in enumerate(existing_bins):#write existing b-tag bins
            current_histogram_name = histogram_name + '_' + b_tag_bin
            existing_histograms[bin_i].Write(current_histogram_name)
            
        for bin_i, b_tag_bin in enumerate(to_be_created):#write new b-tag bins
            current_histogram_name = histogram_name + '_' + b_tag_bin
            new_histogram = existing_histograms[bin_i].Clone(current_histogram_name)
            for existing_histogram in existing_histograms[bin_i + 1:]:
                new_histogram.Add(existing_histogram)
                
            new_histogram.Write(current_histogram_name)

    input_file.Close()

    output_file.Close()
    logging.debug( 'Finished %s' % file_in_path)
    logging.debug( 'Output: %s' % output_file_name)  
    
    del new_histograms, histogram_set, input_file, output_file
    return
    
    
def get_set_of_histogram_paths(input_file, seen_summed_hists = False):
    global existing_bins, to_be_created, filter_on_folders, filter_on_histograms
    histogram_list = []
    add_histogram = histogram_list.append       
    
    checked_n_entries = 0
    for histogram_path in input_file.readlines():
        checked_n_entries += 1
        if checked_n_entries % 10000 == 0:
            logging.debug( 'Checked %d' %checked_n_entries)
            
        if not filter_string(histogram_path, filter_on_folders):
            continue
        if not filter_string(histogram_path, filter_on_histograms):
            continue
        
        histogram_path = histogram_path.rstrip(' \n')
        directory, histogram_name, b_tag_bin = get_histogram_info_tuple(histogram_path)
        logging.debug('Searching %s' % histogram_path)
        logging.debug('Found directory %s' % directory)
        logging.debug('Found histogram_name %s' % histogram_name)
        logging.debug('Found b_tag_bin %s' % b_tag_bin)

        if b_tag_bin in existing_bins:
            histogram_name = '_'.join(histogram_name.split('_')[:-1])
            logging.debug('Adding histogram %s' % (directory + histogram_name))
            add_histogram(directory + histogram_name)
        if b_tag_bin in to_be_created:
            seen_summed_hists = True
                
    return set(histogram_list)#only unique ones

def filter_string(input_string, filter_list):
    accept = False
    if not filter_list: #empty list
        accept = True
    else:
        for filter_item in filter_list:
            if filter_item in input_string:
                accept = True #found a matching entry
                break
    return accept
    
def create_folder_structure(root_file, path_list):
    get_directory = root_file.Get

    for path in path_list:
        directories = path.split('/')
        current_path = ''
        root_file.cd()
        for directory in directories:
            if current_path == '':
                if not get_directory(directory):
                    root_file.mkdir(directory)
                current_path = directory
            else:
                current_dir = get_directory(current_path)
                if not current_dir.Get(directory):
                    current_dir.mkdir(directory)
                current_path += "/" + directory
 
 
def get_histogram_info_tuple(histogram_in_path):
     histogram_name = histogram_in_path.split('/')[-1]
     directory = ''.join(histogram_in_path.rsplit(histogram_name, 1)[:-1])
     b_tag_bin = histogram_name.split('_')[-1]
     return directory, histogram_name, b_tag_bin
     
def merge_files_by_process(root_files):
    global input_folder, output_folder
    electron_qcd_samples = [ 'QCD_Pt-20to30_BCtoE',
                 'QCD_Pt-30to80_BCtoE',
                 'QCD_Pt-80to170_BCtoE',
                 'QCD_Pt-20to30_EMEnriched',
                 'QCD_Pt-30to80_EMEnriched',
                 'QCD_Pt-80to170_EMEnriched',
                 'GJets_HT-40To100',
                 'GJets_HT-100To200',
                 'GJets_HT-200']
    singleTop_samples = [ 'T_tW-channel',
                 'T_t-channel',
                 'T_s-channel',
                 'Tbar_tW-channel',
                 'Tbar_t-channel',
                 'Tbar_s-channel']
    wplusjets_samples = [ 'W1Jet', 'W2Jets', 'W3Jets', 'W4Jets']
    vplusjets_samples = wplusjets_samples
    vplusjets_samples.append('DYJetsToLL')
    diboson_samples = [ 'WWtoAnything', 'WZtoAnything', 'ZZtoAnything']
    signal_samples = [ 'TTJet', 'SingleTop']
    
    summations = {
                  'QCD_Electron':electron_qcd_samples,
                  'SingleTop' : singleTop_samples,
                  'WPlusJets' : wplusjets_samples,
                  'VPlusJets' : vplusjets_samples,
                  'DiBoson': diboson_samples,
                  'Signal': signal_samples
                  }
    
    summation_files = {}
    file_template = ''
    template_token = '<temp>'
    for summation, samples in summations.iteritems():
        summation_files[summation] = []
        for file_in_path in root_files:
            process_name = get_process_from_file(file_in_path)
            if not file_template:
                file_template = file_in_path.replace(process_name, template_token)
                file_template = file_template.replace(input_folder, output_folder)
            if process_name in samples:
                summation_files[summation].append(file_in_path)
    
    for summation, files in summation_files.iteritems():
        output_file = file_template.replace(template_token, summation)
        merge_ROOT_files(files, output_file)        
    
                
if __name__ == "__main__":
    parser = ArgumentParser(description='Sum b-tag binned histograms and merge files into main processes (e.g. 6 single top samples into one).')
    parser.add_argument('input_folder', metavar='input_folder', 
                        help="input folder for histogram files to be summed")
    parser.add_argument('output_folder', metavar='output_folder', 
                        help="output folder for the summed histogram files to be written to.",
                        default = '', nargs='?')
    parser.add_argument('--debug', 
                        help="Turn on debug output",
                        action='store_true')
    args = parser.parse_args()
    
    if args.debug:
        logging.basicConfig()#fancy logger for better error messages
    else:
        logging.basicConfig(level=logging.WARNING)#turn debug off
        
    existing_histogram_file = 'data/list_of_7TeV_histograms.txt'
    existing_bins = ['0btag', '1btag', '2btags','3btags','4orMoreBtags']
    to_be_created = ['0orMoreBtag','1orMoreBtag','2orMoreBtags','3orMoreBtags']
    filter_on_folders = ['TTbarPlusMetAnalysis']    
    filter_on_histograms = []
    #first sum up the histograms
    input_folder = args.input_folder 
    output_folder = args.output_folder
    if not output_folder:
        output_folder = input_folder
    make_folder_if_not_exists(output_folder)
    root_files = get_files_in_path(input_folder, file_ending='.root')
#    from multiprocessing import Pool
#    pool = Pool(processes=4)
#    pool.map_async(sum_b_tag_bins_in_file, root_files)
#    pool.close()
#    pool.join()
#    sum_b_tag_bins_in_file(input_folder + '/' + 'TTJet_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET_MCatNLO.root')
    map(sum_b_tag_bins_in_file, root_files)
