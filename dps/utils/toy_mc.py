'''
Created on 11 Dec 2012

@author: kreczko
'''
from __future__ import division
from numpy.random import poisson
from math import sqrt
from .hist_utilities import value_error_tuplelist_to_hist
from numpy.ma.extras import average

def generate_toy_MC_from_distribution( distribution ):
    initial_values = list( distribution.y() )
    new_values, new_errors = generate_toy_MC_from_values( initial_values )
    toy_MC = value_error_tuplelist_to_hist( zip( new_values, new_errors ), list( distribution.xedges() ) )
    return toy_MC

def generate_toy_MC_from_values( values ):
    values = [ 0 if i < 0 else i for i in values ]

    new_values = [poisson( value ) for value in values]
    # statistical errors
    new_errors = [sqrt( value ) for value in new_values]
    return new_values, new_errors

def generate_toy_MC_from_2Ddistribution( distribution ):
    n_bins_x = distribution.nbins(axis = 0)
    n_bins_y = distribution.nbins(axis = 1)
    
    new_distribution = distribution.Clone()
    get_bin_content = distribution.GetBinContent
    set_bin_content = new_distribution.SetBinContent
    set_bin_error = new_distribution.SetBinError
    
    for bin_x in range(1, n_bins_x + 1):
        for bin_y in range(1, n_bins_y + 1):
            value = get_bin_content(bin_x, bin_y)
            if value < 0 : value = 0
            new_value = poisson(value)
            error = sqrt(new_value)
            set_bin_content(bin_x, bin_y, new_value)
            set_bin_error(bin_x, bin_y, error)
    return new_distribution

def generate_n_poisson_weights(n, b = 1000):
    '''
        Creates N weights from a Poisson distribution peak at 1.
        @param n: sample size
        @param b: base (base = 1000 creates weights with precirion of 3 decimals

        For large b this corresponds to a gaussian centred at 1
    '''
    return poisson(b, n)/b

def generate_n_poisson_weights_for_average(n, n_events_in_bins = [100, 120]):
    mean = average(n_events_in_bins)
    return generate_n_poisson_weights(n, mean)

if __name__ == '__main__':
    from array import array
    from rootpy.plotting import Hist
    import rootpy.plotting.root2matplotlib as rplt
    import matplotlib.pyplot as plt
    from matplotlib.ticker import AutoMinorLocator
    
    bins = array('d', [0, 25, 45, 70, 100, 1000])
    h_data = Hist(bins.tolist())
    h_data.SetBinContent(1, 2146)
    h_data.SetBinError(1, 145)
    h_data.SetBinContent(2, 3399)
    h_data.SetBinError(2, 254)
    h_data.SetBinContent(3, 3723)
    h_data.SetBinError(3, 69)
    h_data.SetBinContent(4, 2256)
    h_data.SetBinError(4, 53)
    h_data.SetBinContent(5, 1722)
    h_data.SetBinError(5, 91)
    h_data.SetTitle('input distribution')
    h_new = generate_toy_MC_from_distribution(h_data)
    h_new.SetTitle('toy MC')
    fig = plt.figure(figsize=(16, 10), dpi=100, facecolor='white')
    axes = plt.axes([0.15, 0.15, 0.8, 0.8])
    axes.xaxis.set_minor_locator(AutoMinorLocator())
    axes.yaxis.set_minor_locator(AutoMinorLocator())
    axes.tick_params(which='major', labelsize=15, length=8)
    axes.tick_params(which='minor', length=4)
    rplt.hist(h_new, axes=axes)
    rplt.errorbar(h_data, emptybins=False, axes=axes)
    plt.xlabel('Mass', position=(1., 0.), ha='right')
    plt.ylabel('Events', position=(0., 1.), va='top')
    plt.legend(numpoints=1)
    plt.savefig('toy_MC_test.png')
    print  list( h_data.y() )
    print list( h_new.y() )
