'''
Created on 15 Jan 2013

@author: kreczko
Set of functions for the estimation of the number of QCD multijet events after the event selection.

Format of the final result:
result = {'value': value,
          'error':error,
          'fit':fit}
'''

from __future__ import division
from math import sqrt

DEBUG = False
relative_isolation_bias = 0.0
rebin = 10 
bin_width = 0.01


def estimate_with_fit_to_relative_isolation(input_histogram, function='expo',
                   fit_range=(0.3, 1.6), fit_ranges_for_systematics=[(0.2, 1.6), (0.4, 1.6)]):
    global rebin
    if DEBUG:
        print '*' * 120
        print "Estimating QCD using a fit to relative isolation"
        print 'Histogram = ', input_histogram
        print 'Fit function = ', function
        print 'Fit range = ', fit_range
        print 'Fit ranges for systematics = ', fit_ranges_for_systematics
        print '*' * 120
    input_histogram.Rebin(rebin)
    result = fit_to_relative_isolation_with_systematics(input_histogram, function, fit_range=fit_range, fit_ranges_for_systematics=fit_ranges_for_systematics)
    return result
     

def fit_to_relative_isolation_with_systematics(input_histogram, function, fit_range=(0.3, 1.6), fit_ranges_for_systematics=[(0.2, 1.6), (0.4, 1.6)],
                                         apply_bias_correction=True):
    central_result = fit_to_relative_isolation(input_histogram, function, fit_range=fit_range)
    central_value, central_error = central_result['value'], central_result['error']
    
    # systematic errors
    systematic_relative_error_squared = 0
    for current_range in fit_ranges_for_systematics:
        result = fit_to_relative_isolation(input_histogram, function, fit_range=current_range)
        value = result['value']
        deviation = value - central_value
        if not central_value == 0:
            systematic_relative_error_squared += (deviation / central_value) ** 2
            
    relative_error_from_bias_correction = 0
    if apply_bias_correction:
        reduction_from_bias = 1 - relative_isolation_bias
        central_value = central_value * reduction_from_bias
        relative_error_from_bias_correction = relative_isolation_bias

    error_squared = central_error ** 2 + (systematic_relative_error_squared + relative_error_from_bias_correction) * (central_value ** 2)
    central_error = sqrt(error_squared)
    
    result = {
              'value':central_value,
              'error': central_error,
              'fit':central_result['fit']
              }
    return result

def fit_to_relative_isolation(input_histogram, function, fit_range, signal_region=(0., 0.1)):
    global rebin, bin_width
    value, error = 0,0
    relative_error_squared = 0
    
    histogram = input_histogram.Clone('tmp')
    fit = perform_fit(histogram, function, fit_range)
    if fit:
        value = fit.Integral(signal_region[0], signal_region[1])/(bin_width * rebin)
        for n in range(0, fit.GetNumberFreeParameters()):
            parameter = fit.GetParameter(n)
            error = fit.GetParError(n)
            if not parameter == 0:
                relative_error_squared += (error / parameter) ** 2
    
    error = sqrt(relative_error_squared)*value
    result = {'value': value,
              'error':error,
              'fit':fit}
    return result

def perform_fit(histogram, function, fit_range):
    histogram.Fit(function, "Q0", "ah", fit_range[0], fit_range[1])
    fit = histogram.GetFunction(function)
    if fit:
        return fit.Clone()
    else:
        return None