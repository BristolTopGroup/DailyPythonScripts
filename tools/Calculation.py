'''
Created on 20 Nov 2012

@author: kreczko
'''
from uncertainties import ufloat
import numpy

def calculate_xsection(inputs, luminosity, efficiency=1.):
    '''
    BUG: this doesn't work unless the inputs are unfolded!
    inputs = list of value-error pairs
    luminosity = integrated luminosity of the measurement
    '''
    result = []
    add_result = result.append
    for value, error in inputs:
        xsection = value / luminosity / efficiency
        xsection_error = error / luminosity / efficiency
        add_result((xsection, xsection_error))        
    return result

def calculate_normalised_xsection(inputs, bin_widths, normalise_to_one=False):
    '''
    Calculates normalised average x-section for each bin: 1/N *1/bin_width sigma_i
    There are two ways to calculate this
    1) N = sum(sigma_i)
    2) N = sum(sigma_i/bin_width)
    The latter one will normalise the total distribution to 1
    inputs = list of value-error pairs
    bin_widths = bin widths of the inputs
    '''
    result = []
    add_result = result.append
    
    normalisation = 0
    for measurement, bin_width in zip(inputs, bin_widths):
        value = ufloat(measurement)
        
        if normalise_to_one:
            normalisation += value / bin_width
        else:
            normalisation += value
    for measurement, bin_width in zip(inputs, bin_widths):
        value = ufloat(measurement)
        xsection = value / normalisation / bin_width
        add_result((xsection.nominal_value, xsection.std_dev()))   
    return result

def decombine_result(combined_result, original_ratio):
    '''
    Use to extract the individual results from a combined result
    i.e. 
    combined_result = (sample_1_value + sample_2_value, combined_error)
    original_ratio = sample_1_value/sample_2_value
    This method will return the decombined values for the two samples:
    return (sample_1_value, sample_1_error), (sample_2_value, sample_2_error)
    with the proper errors
    '''
    combined_result = ufloat(combined_result)
    sample_1 = combined_result * original_ratio / (1 + original_ratio)
    sample_2 = combined_result - sample_1
    return (sample_1.nominal_value, sample_1.std_dev()), (sample_2.nominal_value, sample_2.std_dev())

def combine_results(result1, result2):
    '''
    Combines results of the form {measurement: (value, error)
    '''
    samples = result1.keys()
    if not samples == result2.keys():
        print 'Error - combine_results: results have a different set of keys!'
        return None
    combined_result = {}
    for sample in result1.keys():
        value1, error1 = result1[sample]
        value2, error2 = result2[sample]
        combined_result[sample] = (value1 + value2, error1 + error2)
    return combined_result

def combine_complex_results(result1, result2):
    '''
    Combines results of the form {measurement: [(value, error), ....]
    '''
    
    samples = result1.keys()
    if not samples == result2.keys():
        print 'Error - combine_results: results have a different set of keys!'
        return None
    
    combined_result = {}
    
    for sample in samples:
        results = []
        for entry1, entry2 in zip(result1[sample], result2[sample]):
            value1, error1 = entry1
            value2, error2 = entry2
            results.append((value1 + value2, error1 + error2))
        combined_result[sample] = results
    return combined_result

def calculate_lower_and_upper_PDFuncertainty(central_measurement, pdf_uncertainty_values={}):
    '''
    Calculates the appropriate lower and upper PDF uncertainty
    @param central_measurement: measurement from central PDF weight
    @param pdf_uncertainty_values: dictionary of measurements with different PDF weights; 
                                    format {PDFWeights_%d: measurement}
    '''
    negative = []
    positive = []
    
    # split PDF uncertainties into downwards (negative) and upwards (positive) components
    for index in range(1, 45):
        pdf_weight = 'PDFWeights_%d' % index
        pdf_uncertainty = pdf_uncertainty_values[pdf_weight]
        if index % 2 == 0:  # even == negative
            negative.append(pdf_uncertainty)
        else:
            positive.append(pdf_uncertainty)
            
    pdf_max = numpy.sqrt(sum(max(x - central_measurement, y - central_measurement, 0) ** 2 for x, y in zip(negative, positive)))
    pdf_min = numpy.sqrt(sum(max(central_measurement - x, central_measurement - y, 0) ** 2 for x, y in zip(negative, positive)))
    
    return pdf_min, pdf_max   

def calculate_lower_and_upper_systematics(central_measurement, lower_systematics, upper_systematics, 
                                          group = {}):
    pass
    