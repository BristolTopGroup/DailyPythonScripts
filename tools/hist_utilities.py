'''
Created on 20 Nov 2012

@author: kreczko
'''

from rootpy.plotting import Hist

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

def value_error_tuplelist_to_hist(value_error_tuplelist, bin_edges):
    assert(len(bin_edges) == len(value_error_tuplelist) + 1)
    rootpy_hist = Hist(bin_edges)
    set_bin_value = rootpy_hist.SetBinContent
    set_bin_error = rootpy_hist.SetBinError
    for bin_i, (value, error) in enumerate(value_error_tuplelist):
        set_bin_value(bin_i + 1, value)
        set_bin_error(bin_i + 1, error)
    return rootpy_hist

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