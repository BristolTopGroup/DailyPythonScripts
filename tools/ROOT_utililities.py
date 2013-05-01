'''
Created on 19 Jan 2013

@author: kreczko
'''
from rootpy.logger import logging
from ROOT import TFile, gROOT
File = TFile.Open
gcd = gROOT.cd
from config.summations import b_tag_bins_inclusive, b_tag_summations

def get_histogram_from_file(histogram_path, input_file):
    current_btag = b_tag_bins_inclusive[0]
    found_btag = False
    
    for b_tag in b_tag_bins_inclusive:
        if b_tag in histogram_path:
            current_btag = b_tag
            found_btag = True
            break
    
    root_file = File(input_file)
    get_histogram = root_file.Get
    
    
    if not found_btag:
        root_histogram = get_histogram(histogram_path)
        if not is_valid_histogram(root_histogram, histogram_path, input_file):
            return
    else:
        listOfExclusiveBins = b_tag_summations[current_btag]
        exclhists = []
        
        for excbin in listOfExclusiveBins:
            hist = get_histogram(histogram_path.replace(current_btag, excbin))
            if not is_valid_histogram(hist, histogram_path.replace(current_btag, excbin), input_file):
                return
            exclhists.append(hist)
        root_histogram = exclhists[0].Clone()
        
        for hist in exclhists[1:]:
            root_histogram.Add(hist)
    
    gcd()
    histogram = root_histogram.Clone()
    root_file.Close()
    return histogram 
    
def is_valid_histogram(histogram, histogram_name, file_name):
    if not histogram:
        logging.error('Histogram \n"%s" \ncould not be found in root_file:\n%s' % (histogram_name, file_name))
        return False
    return True


#Reads a single histogram from each given rootFile
#and returns a dictionary with the same naming as 'files'
def get_histogram_dictionary(histogram_path, files={}):
    hists = {}
    for sample, file_name in files.iteritems():
        hists[sample] = get_histogram_from_file(histogram_path, file_name)
    return hists

#Reads a list of histograms from each given file
def get_histograms_from_files(histogram_paths=[], files={}, verbose = False):
    histograms = {}
    nHistograms = 0
    for sample, input_file in files.iteritems():
        root_file = File(input_file)
        get_histogram = root_file.Get
        histograms[sample] = {}
        
        for histogram_path in histogram_paths:
            current_btag = b_tag_bins_inclusive[0]
            found_btag = False
            
            for b_tag in b_tag_bins_inclusive:
                if b_tag in histogram_path:
                    current_btag = b_tag
                    found_btag = True
                    break
            
            root_histogram = None
            if not found_btag:
                root_histogram = get_histogram(histogram_path)
                if not is_valid_histogram(root_histogram, histogram_path, input_file):
                    return
            else:
                listOfExclusiveBins = b_tag_summations[current_btag]
                exclhists = []
                
                for excbin in listOfExclusiveBins:
                    hist = get_histogram(histogram_path.replace(current_btag, excbin))
                    if not is_valid_histogram(hist, histogram_path.replace(current_btag, excbin), input_file):
                        return
                    exclhists.append(hist)
                root_histogram = exclhists[0].Clone()
                
                for hist in exclhists[1:]:
                    root_histogram.Add(hist)
            
            gcd()
            nHistograms += 1
            histograms[sample][histogram_path] = root_histogram.Clone()
            if verbose and nHistograms % 5000 == 0:
                print 'Read', nHistograms, 'histograms'
        root_file.Close()
    return histograms

def root_file_mkdir(root_file, directory):
    pointer_to_directory = root_file.Get(directory)
    if not pointer_to_directory:
        root_file.mkdir(directory)#if directory = a/b/c this will only return a, but make complete path
        pointer_to_directory = root_file.Get(directory)
    return pointer_to_directory
    
def get_histogram_info_tuple(histogram_in_path):
    histogram_name = histogram_in_path.split('/')[-1]
    directory = ''.join(histogram_in_path.rsplit(histogram_name, 1)[:-1])
    b_tag_bin = histogram_name.split('_')[-1]
    
    return directory, histogram_name, b_tag_bin    
        