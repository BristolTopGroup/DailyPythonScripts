'''
Created on 20 Nov 2012

@author: kreczko
'''

from rootpy.plotting import Hist, Graph
from rootpy import asrootpy
from ROOT import TGraphAsymmErrors

def hist_to_value_error_tuplelist(hist):
    values = list(hist)
    errors = []
    add_error = errors.append
    get_bin_error = hist.GetBinError
    for bin_i in range(len(values)):
        add_error(get_bin_error(bin_i + 1))
    return zip(values, errors)

def values_and_errors_to_hist(values, errors, bins):
    assert(len(values) == len(bins))
    if len(errors) == 0:
        errors = [0.]*len(values)
    value_error_tuplelist = zip(values, errors)
    return value_error_tuplelist_to_hist(value_error_tuplelist, bins)

def value_errors_tuplelist_to_graph(value_errors_tuplelist, bin_edges):
    value_error_tuplelist = [(value, 0) for value, lower_error, upper_error in value_errors_tuplelist]
    hist = value_error_tuplelist_to_hist(value_error_tuplelist, bin_edges)
    rootpy_graph = asrootpy(TGraphAsymmErrors(hist)) 
#    rootpy_graph = Graph(hist = hist)
    set_lower_error = rootpy_graph.SetPointEYlow
    set_upper_error = rootpy_graph.SetPointEYhigh
    
    for point_i, (value, lower_error, upper_error) in enumerate(value_errors_tuplelist):
        set_lower_error(point_i, lower_error)
        set_upper_error(point_i, upper_error)
        
    return rootpy_graph

def value_error_tuplelist_to_hist(value_error_tuplelist, bin_edges):
    assert(len(bin_edges) == len(value_error_tuplelist) + 1)
    rootpy_hist = Hist(bin_edges)
    set_bin_value = rootpy_hist.SetBinContent
    set_bin_error = rootpy_hist.SetBinError
    for bin_i, (value, error) in enumerate(value_error_tuplelist):
        set_bin_value(bin_i + 1, value)
        set_bin_error(bin_i + 1, error)
    return rootpy_hist

def value_tuplelist_to_hist(value_tuplelist, bin_edges):
    assert(len(bin_edges) == len(value_tuplelist) + 1)
    rootpy_hist = Hist(bin_edges)
    set_bin_value = rootpy_hist.SetBinContent
    for bin_i, value in enumerate(value_tuplelist):
        set_bin_value(bin_i + 1, value)
    return rootpy_hist

def sum_histograms(histogram_dict, sample_list):
    #histogram_dict = {sample:{histogram_name:histogram}
    summary = {}
    preparation = {}
    for sample in sample_list:
        sample_hists = histogram_dict[sample]
        for histogram_name, histogram in sample_hists.iteritems():
            if not preparation.has_key(histogram_name):
                preparation[histogram_name] = []
            preparation[histogram_name].append(histogram)
    for histogram_name, histogram_list in preparation.iteritems():
        summary[histogram_name] = sum(histogram_list)
    return summary

def scale_histogram_errors(histogram, total_error):
    bins_number = histogram.GetNbinsX()
    current_total_error = 0
    for bin_i in range(bins_number):
        current_total_error += histogram.GetBinError(bin_i+1)

    scale_factor = total_error/current_total_error

    for bin_i in range(bins_number):
        histogram.SetBinError(bin_i+1, scale_factor*histogram.GetBinError(bin_i+1))

def prepare_histograms(histograms, rebin=1, scale_factor=1., normalisation={}):
    for sample, histogram_dict in histograms.iteritems():
        for _, histogram in histogram_dict.iteritems():
            histogram.Rebin(rebin)
            histogram.Scale(scale_factor)
            if normalisation != {} and histogram.Integral() != 0:
                if sample == 'TTJet':
                    histogram.Scale(normalisation['TTJet'][0]/histogram.Integral())
                    scale_histogram_errors(histogram, normalisation['TTJet'][1])
                if sample == 'SingleTop':
                    histogram.Scale(normalisation['SingleTop'][0]/histogram.Integral())
                    scale_histogram_errors(histogram, normalisation['SingleTop'][1])
                if sample == 'V+Jets':
                    histogram.Scale(normalisation['V+Jets'][0]/histogram.Integral())
                    scale_histogram_errors(histogram, normalisation['V+Jets'][1])
                if sample == 'QCD':
                    histogram.Scale(normalisation['QCD'][0]/histogram.Integral())
                    scale_histogram_errors(histogram, normalisation['QCD'][1])

            
if __name__ == '__main__':
    value_error_tuplelist = [(0.006480446927374301, 0.0004647547547401945), 
                             (0.012830288388947605, 0.0010071677178938234), 
                             (0.011242639287332025, 0.000341258792551077), 
                             (0.005677185565453722, 0.00019082371879446718), 
                             (0.0008666767325985203, 5.0315979327182054e-05)]
    hist = value_error_tuplelist_to_hist(value_error_tuplelist, bin_edges = [0, 25, 45, 70, 100, 300])
    import rootpy.plotting.root2matplotlib as rplt
    import matplotlib.pyplot as plt
    plt.figure(figsize=(16, 10), dpi=100)
    plt.figure(1)
    rplt.errorbar(hist, label='test')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Testing')
    plt.legend(numpoints=1)
    plt.savefig('Array2Hist.png')
    plt.close()
    
    value_errors_tuplelist = [(0.006480446927374301, 0.0004647547547401945, 0.0004647547547401945*2), 
                             (0.012830288388947605, 0.0010071677178938234, 0.0010071677178938234*2), 
                             (0.011242639287332025, 0.000341258792551077*2, 0.000341258792551077), 
                             (0.005677185565453722, 0.00019082371879446718*2, 0.00019082371879446718), 
                             (0.0008666767325985203, 5.0315979327182054e-05, 5.0315979327182054e-05)]
    hist = value_errors_tuplelist_to_graph(value_errors_tuplelist, bin_edges = [0, 25, 45, 70, 100, 300])

    plt.figure(figsize=(16, 10), dpi=100)
    plt.figure(1)
    rplt.errorbar(hist, label='test2')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Testing')
    plt.legend(numpoints=1)
    plt.savefig('Array2Graph.png')