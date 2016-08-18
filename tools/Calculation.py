'''
Created on 20 Nov 2012

@author: kreczko
'''
from __future__ import division
import uncertainties as u
import numpy
from math import sqrt
from config.met_systematics import metsystematics_sources
from rootpy import asrootpy
from rootpy.plotting import Hist2D
from config.variable_binning import bin_edges
from decimal import *

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

def get_correlation_matrix(uncertainties,covariance):
    nBins = len(uncertainties)
    correlation = numpy.array( numpy.zeros( (nBins, nBins) ) )
    for i in range(0,nBins):
        for j in range(0,nBins):
            cov = covariance[i,j]
            unc_i = uncertainties[i]
            unc_j = uncertainties[j]
            correlation[i,j] = cov / ( unc_i * unc_j)
    return correlation

def calculate_covariance_for_normalised_xsection(covariance, inputs, bin_widths,):
    new_covariance = covariance.copy()

    values = [u.ufloat( i[0], i[1] ) for i in inputs]
    normalisation = sum( values )

    nominal_values = [v.nominal_value for v in values]

    values_correlated = u.correlated_values( nominal_values, covariance.tolist() )
    print 'Original values :',values_correlated
    print 'Original correlation :',u.correlation_matrix(values_correlated)
    norm = sum(values_correlated)

    norm_values_correlated = []

    for v,width in zip( values_correlated, bin_widths ):
        norm_values_correlated.append( v / width / norm )

    print 'New values :',norm_values_correlated
    print 'New correlation :',u.correlation_matrix(norm_values_correlated)
    new_covariance = numpy.array( u.covariance_matrix(norm_values_correlated) )
    print 'New covariance :',u.covariance_matrix(norm_values_correlated)

    # n_rows = covariance.shape[0]
    # n_cols = covariance.shape[1]

    # uncertainties = [numpy.sqrt(covariance[i,i]) for i in range(0,n_rows)]


    # # for i in range(0,n_rows):
    # #     print numpy.sqrt(covariance[i,i]),values[i].std_dev
    # correlation = get_correlation_matrix( uncertainties, covariance )
    # print 'Original correlation'
    # print correlation

    # # print correlation
    # for i_row in range(0,n_rows):
    #     for i_col in range(0,n_cols):

    #         cor_ij = correlation[i_row,i_col]

    #         xsec_i = ( values[i_row] / bin_widths[i_row] / normalisation )
    #         xsec_j = ( values[i_col] / bin_widths[i_col] / normalisation )

    #         new_element = xsec_i.std_dev * xsec_j.std_dev * cor_ij
    #         # value_row = u.ufloat( values[i_row].nominal_value, numpy.sqrt( abs(covariance[i_row,i_col]) ) )
    #         # value_column = u.ufloat( values[i_col].nominal_value, numpy.sqrt( abs(covariance[i_row,i_col]) ) )

    #         # xsec_i_xsec_j = u.ufloat( (values[i_row] * values[i_col]).nominal_value, abs( covariance[i_row,i_col] ) )
    #         # value_i_value_j = value_row * value_column



    #         # normalisation = u.ufloat(0,0)
    #         # for i in range(0,n_rows):
    #         #     if i == n_rows:
    #         #         # normalisation += value_row
    #         #     elif i == n_cols: 
    #         #         # normalisation += value_column 
    #         #     else:
    #         #         # normalisation += values[i]

    #         # if i_row == i_col:
    #         #     print i_row, i_col, new_element, numpy.sqrt(new_element)
    #         #     print value_row,value_column,value_i_value_j
    #         #     print normalisation
    #         # new_element = value_i_value_j / bin_widths[i_row] / bin_widths[i_col] / normalisation / normalisation
    #         # new_element = new_element.std_dev * numpy.sign( covariance[i_row,i_col] )

    #         # simple = covariance[i_row,i_col] / bin_widths[i_row] / bin_widths[i_col] / normalisation ** 2
    #         # new_element = covariance[i_row, i_col] / values[i_row].nominal_value ** 2 + norm2Error / normalisation.nominal_value ** 2
    #         # print covariance[i_row, i_col] / values[i_row].nominal_value ** 2
    #         # print norm2Error
    #         # print normalisation.nominal_value
    #         # print normalisation.nominal_value ** 2
    #         # print norm2Error / normalisation.nominal_value ** 2
    #         # print 'Sqrt this :',new_element
    #         # new_element = numpy.sqrt( new_element )
    #         # new_element *= values[i_row].nominal_value * values[i_col].nominal_value
    #         # new_element /= ( bin_widths[i_col] * bin_widths[i_row] )
    #         # new_element = covariance[i_row,i_col] / bin_widths[i_row] / bin_widths[i_col] / normalisation.nominal_value ** 2
    #         # / ( bin_widths[i_col] * bin_widths[i_row] * normalisation * normalisation )
    #         # if i_row == i_col:
    #         # # # print values[i_row]
    #         # # # # print numpy.sqrt( values[i_row].nominal_value / values[i_row].std_dev ) ** 2 + (norm2Error / normalisation ** 2) * values[i_row].nominal_value / bin_widths[i_row] / normalisation

    #         # # # print 'Original : ',covariance[i_row, i_col]
    #         # # # print bin_widths[i_col],bin_widths[i_row],normalisation
    #         #     # print xsec_i_xsec_j
    #         #     print values[i_row].nominal_value,values[i_row].std_dev
    #         #     print (values[i_row] * values[i_col]).std_dev, covariance[i_row,i_col]
    #         #     print values[i_row] * values[i_col], covariance[i_row,i_col]

    #         #     print 'New :',new_element, numpy.sqrt(new_element)
    #         #     print 'Simple : ',simple, numpy.sqrt(simple.nominal_value)
    #         new_covariance[i_row, i_col] = new_element

    # new_uncertainties = [numpy.sqrt(new_covariance[i,i]) for i in range(0,n_rows)]
    # print 'New uncertainties :',new_uncertainties

    # new_correlation = get_correlation_matrix( new_uncertainties, new_covariance )
    # print 'New correlation'
    # print new_correlation

    return new_covariance

def calculate_normalised_xsection(inputs, bin_widths, normalise_to_one=False, debug=False):
    """
        Calculates normalised average x-section for each bin: 1/N *1/bin_width sigma_i
        There are two ways to calculate this
            1) N = sum(sigma_i)
            2) N = sum(sigma_i/bin_width)
        The latter one will normalise the total distribution to 1
        @param inputs: list of value-error pairs
        @param bin_widths: bin widths of the inputs
    """
    values = [u.ufloat( i[0], i[1] ) for i in inputs]
    normalisation = 0
    if normalise_to_one:
        normalisation = sum( [value / bin_width for value, bin_width in zip( values, bin_widths )] )
    else:
        normalisation = sum( values )

    xsections = [( 1 / bin_width ) * value / normalisation for value, bin_width in zip( values, bin_widths )]
    result = [(xsection.nominal_value, xsection.std_dev) for xsection in xsections]

    # if debug:

    #     # for value, bin_width in zip( values, bin_widths ):
    #     #     print value.nominal_value,value.std_dev

    #     for xsec in xsections:
    #         print xsec.nominal_value, xsec.std_dev
    #         # print 'Here'
    #         # xsec = ( 1 / bin_width ) * value / normalisation.nominal_value
    #         # print value.nominal_value, bin_width, normalisation.nominal_value, xsec.nominal_value
    #         # print value.std_dev, bin_width, normalisation.std_dev, xsec.std_dev

    #         # print ( 1 / bin_width ) * value / normalisation
    #         # print ( 1 / bin_width ) * value / normalisation.nominal_value
    #         # print value, bin_width, normalisation, xsec
    #         # print xsec.nominal_value,xsec.std_dev, numpy.sqrt( (value.std_dev / value.nominal_value) ** 2 + ( normalisation.std_dev / normalisation.nominal_value ) ** 2 ) * ( 1 / bin_width ) * value.nominal_value / normalisation.nominal_value

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
    if original_ratio == 0:
        return combined_result, (0,0)
    else:
        combined_result = u.ufloat(combined_result[0], combined_result[1])
        sample_1 = combined_result * original_ratio / (1 + original_ratio)
        sample_2 = combined_result - sample_1
        
        return (sample_1.nominal_value, sample_1.std_dev), (sample_2.nominal_value, sample_2.std_dev)

def combine_results(result1, result2):
    '''
    Combines results of the form {measurement: (value, error)
    The errors are added in quadrature
    '''
    samples = result1.keys()
    if not samples == result2.keys():
        print 'Error - combine_results: results have a different set of keys!'
        return None
    combined_result = {}
    for sample in result1.keys():
        value1, error1 = result1[sample]
        value2, error2 = result2[sample]
        combined_result[sample] = ( value1 + value2, sqrt( error1**2 + error2**2 ) )
    return combined_result

def combine_complex_results(result1, result2):
    '''
    Combines results of the form {measurement: [(value, error), ....]
    The errors are added in quadrature
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
            results.append( ( value1 + value2, sqrt( error1**2 + error2**2 ) ) )
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
    # print 'Negative :',negative
    # print 'Positive :',positive
    # print 'Max sign :',numpy.sign( sum(max(x - central_measurement, y - central_measurement, 0) for x, y in zip(negative, positive)) )
    # print 'Min sign :',numpy.sign( sum(max(central_measurement - x, central_measurement - y, 0) for x, y in zip(negative, positive)) )
    dict_of_unc = {}
    # for i in range(1,45):
    #     list_of_unc.append([])

    pdf_max = numpy.sqrt(sum(max(x - central_measurement, y - central_measurement, 0) ** 2 for x, y in zip(negative, positive)))
    pdf_min = numpy.sqrt(sum(max(central_measurement - x, central_measurement - y, 0) ** 2 for x, y in zip(negative, positive)))


    for x,y,i in zip(negative, positive, range(0,44)):
        maxUnc = 0.
        if pdf_max > pdf_min:
            maxUnc = max( x - central_measurement, y - central_measurement, 0 )
        else:
            maxUnc = max( central_measurement - x, central_measurement - y, 0 )

        # maxUnc = max( abs(pMax), abs(pMin) )

        sign = 0.
        if maxUnc == abs( x - central_measurement ):
            sign = -1.0
        elif maxUnc == abs( y - central_measurement ):
            sign = 1.0
        elif maxUnc == abs( central_measurement - x ):
            sign = 1.0
        elif maxUnc == abs( central_measurement - y ):
            sign = -1.0

        maxUnc = maxUnc * sign
        # print x, y, pMax, pMin, maxUnc
        dict_of_unc[str(i)] = maxUnc

    # print dict_of_unc
    # raw_input('...')
    
    return pdf_min, pdf_max, dict_of_unc

def calculate_lower_and_upper_systematics(central_measurement, list_of_systematics, symmetrise_errors = False, debug=False, mass = False):
    '''
    More generic replacement for calculateTotalUncertainty. Calculates the total negative and positve systematics.
    @param central_measurement: measurement from the central sample
    @param list_of_systematics: list of systematic measurements 
    @param symmetrise_errors: make the errors symmetric. Picks the largest of the two and returns it as both upper and lower error. Default is false.
    '''
    negative_error = 0
    positive_error = 0

    positive_error_dictionary = {}
    negative_error_dictionary = {}

    for name,systematic in list_of_systematics.iteritems():
        deviation = abs(systematic) - abs(central_measurement)
        if debug:
            print name, systematic, central_measurement, deviation, (systematic/central_measurement - 1)*100

        if deviation > 0:
            positive_error += deviation**2
            positive_error_dictionary[name] = deviation
            negative_error_dictionary[name] = 0
        else:
            negative_error += deviation**2
            positive_error_dictionary[name] = 0
            negative_error_dictionary[name] = deviation

    negative_error = sqrt(negative_error)
    positive_error = sqrt(positive_error)

    # print negative_error_dictionary
    # print positive_error_dictionary
    dictionary_of_errors_to_use = {}

    if debug:
        print 'In calculate'
        print symmetrise_errors
        print negative_error, positive_error

    if symmetrise_errors:
        if negative_error > positive_error:
            dictionary_of_errors_to_use = negative_error_dictionary
        else:
            dictionary_of_errors_to_use = positive_error_dictionary
        if debug:
            print dictionary_of_errors_to_use

        negative_error = max(negative_error, positive_error)
        positive_error = max(negative_error, positive_error)
    else :
        for source,value in negative_error_dictionary.iteritems():
            if value == 0:
                dictionary_of_errors_to_use[source] = positive_error_dictionary[source]
            else:
                dictionary_of_errors_to_use[source] = negative_error_dictionary[source]
    if debug :
        print 'Debug :',negative_error,positive_error,dictionary_of_errors_to_use
    #     print negative_error_dictionary
    #     print positive_error_dictionary    
    return negative_error, positive_error, dictionary_of_errors_to_use

def calculate_covariance_of_systematics_03(errors, central, mass_systematic=False, hadronisation=False, pdf=False, oneway=False, debug = False):

    all_systematic_labels = errors[0].keys()
    # print all_systematic_labels
    systematic_labels = []
    # print all_systematic_labels
    for systematic in all_systematic_labels:
        if 'patType1CorrectedPFMet' in systematic:
            systematic = systematic.split('patType1CorrectedPFMet')[-1]

        if 'down' in systematic or '-' in systematic or ( 'min' in systematic and systematic != 'luminosity+') or 'Down' in systematic : 
            systematic_labels.append( systematic )
        elif not ( 'up' in systematic or '+' in systematic or 'max' in systematic or 'Up' in systematic ):
            systematic_labels.append( systematic )

    # Now have list of down systematics (or the only systematic e.g. QCD_shape)
    if debug :
        print 'In calculate covariance'
        print systematic_labels

    # For each systematic, need a list of errors in each bin
    errors_for_each_syst = {}
    for syst in systematic_labels:
        errors_for_each_syst[syst] = []


    nBins = len(errors)
    for bin, c in zip(errors,central):
        # for e in bin.values():
        #     totalE2 += e*e
        nSystematics = 0
        for systName, error in bin.iteritems():
            if systName in systematic_labels:
                nSystematics += 1
                down_error = error
                sign = numpy.sign( down_error )

                # Get up variation
                upSource = None
                if 'down' in systName:
                    upSource = systName.replace('down', 'up')
                elif '-' in systName:
                    upSource = systName.replace('-', '+')
                elif 'min' in systName and systName != 'luminosity+':
                    upSource = systName.replace('min', 'max')
                elif 'Down' in systName:
                    upSource = systName.replace('Down', 'Up')

                up_error = 0
                if upSource in bin.keys():
                    nSystematics += 1
                    up_error = bin[upSource]
                    if sign == 0:
                        sign = numpy.sign( up_error )

                # if debug:
                #     print systName, upSource, down_error, up_error

                sign = 0
                if hadronisation or oneway:
                    sign = numpy.sign(down_error)
                else:
                    if down_error == 0:
                        if up_error > 0:
                            sign = 1
                        elif up_error < 0:
                            sign = -1
                    elif up_error == 0:
                        if down_error > 0:
                            sign = -1
                        elif down_error < 0:
                            sign = 1
                    else:
                        sign = numpy.sign( up_error - down_error )
                        # if debug:
                        #     print 'Up down have same sign :',upSource,up_error,systName,down_error
                        #     print up_error / c[0] * 100, down_error / c[0] * 100
                        #     print sign
                        #     t = numpy.sqrt(up_error**2 + down_error**2)
                        #     print t/c[0] * 100

                if mass_systematic:

                    sign = numpy.sign( up_error - down_error )
                    # total_error = numpy.sqrt(up_error**2 + down_error**2) * sign
                    total_error = 0

                    if numpy.sign( up_error ) == numpy.sign( down_error ):
                        total_error = numpy.sqrt(up_error**2 + down_error**2) * sign
                    elif abs(up_error) > abs(down_error):
                        total_error = abs( up_error ) * sign
                    else:
                        total_error = abs( down_error ) * sign

                    if debug:
                        print 'Mass',up_error,down_error,sign,total_error

                else:
                    total_error = numpy.sqrt(up_error**2 + down_error**2) * sign

                errors_for_each_syst[systName].append(total_error)

    if debug:
        print errors_for_each_syst

    # Have 1D hist of errors for each systematic source
    # Construct covariance matrix for each source
    total_covariance_matrix = numpy.array( numpy.zeros((nBins,nBins )) )
    for source,e in errors_for_each_syst.iteritems():
        covariance_matrix = numpy.array( numpy.zeros((nBins,nBins )) )
        correlation_matrix = numpy.array( numpy.zeros((nBins,nBins )) )

        maxError = max( [abs(error/c[0]) for error,c in zip( e, central ) ] )
        # print e
        # print central
        # for error, c in zip( e,central ):
        #     print error/c[0]


        for i_row in range(0,nBins):
            for i_col in range(0,nBins):
                cor = 1.0
                # if pdf:
                #     cor = 0.0

                # if 'JES' in source or 'JER' in source or 'BJet' in source:
                #     cor = 0.9

                # if 'hadronisation' in source:
                #     cor = 1

                # if 'TTJets_scaledown' in source:
                #     cor = 0.9

                # if 'hadronisation' in source or 'VJets' in source or 'TTJets_scale' in source or 'TTJets_matching' in source or mass_systematic:
                #     if abs(e[i_row]) < central[i_row][1] or abs(e[i_col]) < central[i_col][1] :
                #         if debug:
                #             print central[i_row],central[i_col],e[i_row],e[i_col]
                #         cor = 0.
                # else:
                # if abs(e[i_row]) < central[i_row][1] * 0.2 or abs(e[i_col]) < central[i_col][1] * 0.2 :
                #     if debug:
                #         print central[i_row],central[i_col],e[i_row],e[i_col]
                #     cor = 0.

                # if 'TTJets_ptreweight' in source:
                #     cor = 0
                # if 'JES' in source or 'BJet' in source or 'PU' in source or 'SingleTop' in source or 'PDF' in source:
                #     cor = 0

                # if maxError < 0.01: cor = 0.


                if i_row == i_col: cor = 1.



                # if debug:
                    # print e[i_row],e[i_col]



                cov = e[i_row] * e[i_col] * cor
                covariance_matrix[i_row, i_col] = cov
                if cov != 0:
                    correlation_matrix[i_row, i_col] = cov / abs( e[i_row] * e[i_col] )
                else:
                    correlation_matrix[i_row, i_col] = 0

        if debug :
            print 'Correlation for',source
            print correlation_matrix
            raw_input('...')
        total_covariance_matrix += covariance_matrix

    # for i_row in range(0,nBins):
    #         print i_row, total_covariance_matrix[i_row,i_row],sqrt(total_covariance_matrix[i_row,i_row])


    return total_covariance_matrix

def calculate_covariance_of_systematics(all_categories, all_variations):
    nBins = len(all_variations['central'])
    total_covariance_matrix = numpy.array( numpy.zeros((nBins,nBins )) )

    all_categories_errors = {}
    for systematic in all_categories:
        if 'patType1CorrectedPFMet' in systematic:
            systematic = systematic.split('patType1CorrectedPFMet')[-1]
        
        if 'down' in systematic or '-' in systematic or ( 'min' in systematic and systematic != 'luminosity+') or 'Down' in systematic : 
            all_categories_errors[systematic] = []
        elif not ( 'up' in systematic or '+' in systematic or 'max' in systematic or 'Up' in systematic ):
            all_categories_errors[systematic] = []

    errors = []
    for bin in range(0,nBins):

        # print all_categories
        # print all_variations.keys()
        error_for_bin = 0
        negative_error = 0
        positive_error = 0

        sources_for_this_bin = []
        negative_sources = []
        positive_sources = []

        for systematic in all_categories:
            if 'patType1CorrectedPFMet' in systematic:
                systematic = systematic.split('patType1CorrectedPFMet')[-1]

            deviation = all_variations[systematic][bin]
            if deviation > 0:
                positive_error += deviation**2
                positive_sources.append( systematic )
            else:
                negative_error += deviation**2
                negative_sources.append( systematic )

        negative_error = sqrt(negative_error)
        positive_error = sqrt(positive_error)


        if negative_error > positive_error:
            sources_for_this_bin = negative_sources
            error_for_bin = negative_error
        else :
            sources_for_this_bin = positive_sources
            error_for_bin = positive_error

        print sources_for_this_bin
        for source in sources_for_this_bin:
            if 'down' in systematic or '-' in systematic or ( 'min' in systematic and systematic != 'luminosity+') or 'Down' in systematic : 
                # Check to see if 'up' version is also present
                upSource = None
                if 'down' in systematic:
                    upSource = source.replace('down', 'up')
                elif '-' in systematic:
                    upSource = source.replace('-', '+')
                elif 'min' in systematic and systematic != 'luminosity+':
                    upSource = source.replace('min', 'max')
                elif 'Down' in systematic:
                    upSource = source.replace('Down', 'Up')

                if upSource in sources_for_this_bin:
                    print 'Up and down in here!',source,upSource

            print source
            # all_categories_errors[source].append(all_variations[source][bin])

        print sources_for_this_bin
        errors.append(error_for_bin)

    for i in range(0,nBins):
        total_covariance_matrix[i,i] = errors[i] * errors[i]

    return total_covariance_matrix

def calculate_covariance_of_systematics_properly(dictionary_of_systematics, central_measurement, debug=False):
    # print all_categories
    # print all_variations.keys()
    if debug:
        print central_measurement
        print dictionary_of_systematics
    all_categories = dictionary_of_systematics.keys()

    all_categories_errors = {}
    for systematic in all_categories:
        if 'patType1CorrectedPFMet' in systematic:
            systematic = systematic.split('patType1CorrectedPFMet')[-1]
        
        if 'down' in systematic or '-' in systematic or ( 'min' in systematic and systematic != 'luminosity+') or 'Down' in systematic : 
            all_categories_errors[systematic] = []
        elif not ( 'up' in systematic or '+' in systematic or 'max' in systematic or 'Up' in systematic ):
            all_categories_errors[systematic] = []

    nBins = len(dictionary_of_systematics[all_categories[0]])

    total_covariance_matrix = numpy.array( numpy.zeros((nBins,nBins )) )

    for down_source in all_categories_errors:
        max_variation = []

        down_variation = dictionary_of_systematics[down_source]

        up_variation = down_variation
        if 'down' in down_source:
            up_variation = dictionary_of_systematics[down_source.replace('down','up')]
        elif '-' in down_source:
            up_variation = dictionary_of_systematics[down_source.replace('-','+')]
        elif 'min' in systematic and systematic != 'luminosity+':
            up_variation = dictionary_of_systematics[down_source.replace('min','max')]
        elif 'Down' in down_source:
            up_variation = dictionary_of_systematics[down_source.replace('Down','Up')]

        # print down_source

        for u,d,c in zip( up_variation, down_variation, central_measurement):
            up_deviation = abs(u[0]) - abs(c[0])
            down_deviation = abs(d[0]) - abs(c[0])
            if debug:
                print 'Differences'
                print c[0],u[0],d[0]
                print up_deviation,down_deviation
            m = max( abs(up_deviation), abs(down_deviation) )
            sign = 0
            # if m == abs(up_deviation):
            #     sign = numpy.sign(up_deviation)
            # elif m == abs(down_deviation):
            #     sign = numpy.sign(down_deviation)
            # if debug:
            #     print 'Signs :',sign,numpy.sign( up_deviation - down_deviation )
            sign = numpy.sign( up_deviation - down_deviation )
            max_variation.append( m * sign )

        covariance_matrix = numpy.array( numpy.zeros((nBins,nBins )) )

        for i_row in range(0,nBins):
            for i_col in range(0,nBins):
                covariance = max_variation[i_row] * max_variation[i_col]
                covariance_matrix[i_row,i_col] = covariance

        if debug:
            print down_source
            print max_variation
            uncertainties = [numpy.sqrt(covariance_matrix[i,i]) for i in range(0,nBins)]
            cor = get_correlation_matrix( uncertainties, covariance_matrix)
            print cor
            raw_input('...')
        total_covariance_matrix += covariance_matrix

    if debug:
        uncertainties = [numpy.sqrt(total_covariance_matrix[i,i]) for i in range(0,nBins)]
        cor = get_correlation_matrix( uncertainties, total_covariance_matrix)
        print 'Total correlation matrix'
        print cor
        raw_input('...')
    # for category in all_categories:
    #     if 'down' in category or '-' in category or 'min' in category:
    return total_covariance_matrix


def calculate_lower_and_upper_systematics_properly(central_measurement, dictionary_of_systematics):

    all_systematics = dictionary_of_systematics.keys()
    systematic_categories = []
    print all_systematics
    for systematic in all_systematics:
        if 'down' in systematic or '-' in systematic : 
            systematic_categories.append( systematic )
        elif not ( 'up' in systematic or '+' in systematic ):
            systematic_categories.append( systematic )
    print systematic_categories
    negative_error = 0
    positive_error = 0

    for category in systematic_categories:
        down_variation = dictionary_of_systematics[category] - central_measurement

        up_variation = down_variation
        if 'down' in category:
            up_variation = dictionary_of_systematics[category.replace('down','up')] - central_measurement
        elif '-' in category:
            up_variation = dictionary_of_systematics[category.replace('-','+')] - central_measurement

        max_variation = max( abs(up_variation), abs(down_variation) )
        sign = 0
        if max_variation == abs(up_variation):
            sign = numpy.sign(up_variation)
        elif max_variation == abs(down_variation):
            sign = numpy.sign(down_variation)

        print category,down_variation,up_variation, max_variation, sign

    # for systematic in list_of_systematics:
    #     deviation = abs(systematic) - abs(central_measurement)
        
    #     if deviation > 0:
    #         positive_error += deviation**2
    #     else:
    #         negative_error += deviation**2
            
    # negative_error = sqrt(negative_error)
    # positive_error = sqrt(positive_error)
    
    # if symmetrise_errors:
    #     negative_error = max(negative_error, positive_error)
    #     positive_error = max(negative_error, positive_error)
    
    return negative_error, positive_error

def combine_errors_in_quadrature(list_of_errors):
    list_of_errors_squared = [error**2 for error in list_of_errors]
    sum_of_errors_squared = sum(list_of_errors_squared)
    combined_error = sqrt(sum_of_errors_squared)
    
    return combined_error

def getRelativeError(value, error):
    relativeError = 0
    if not value == 0:
        relativeError = error / value
    return relativeError

def symmetriseErrors(error1, error2):
    error1, error2 = abs(error1), abs(error2)
    if error1 > error2:
        return error1, error1
    return error2, error2

def calculateTotalUncertainty(results, bin_i, omitTTJetsSystematics=False):
    #pdf_min, pdf_max = calculate_lower_and_upper_PDFuncertainty(results['central'][bin_i])
    pdf_min, pdf_max = 0, 0
    centralResult = results['central'][bin_i]
    centralvalue, centralerror = centralResult[0], centralResult[1]
    totalMinus, totalPlus = pdf_min ** 2 , pdf_max ** 2
    totalMinus_err, totalPlus_err = 0, 0
    totalMETMinus, totalMETPlus = 0, 0
    totalMETMinus_err, totalMETPlus_err = 0, 0
    uncertainty = {}
    for source in results.keys():
        if source == 'central' or 'PDFWeights_' in source:
            continue
        if omitTTJetsSystematics and source in ['TTJet scale-', 'TTJet scale+', 'TTJet matching-', 'TTJet matching+']:
            continue
        result = results[source][bin_i]
        value, error = result[0], result[1]
        diff = abs(value) - abs(centralvalue)
        diff_error = sqrt((centralerror / centralvalue) ** 2 + (error / value) ** 2) * abs(diff)
        uncertainty[source] = [diff, diff_error]
        if diff > 0:
            totalPlus += diff ** 2
            totalPlus_err += diff_error ** 2
        else:
            totalMinus += diff ** 2
            totalMinus_err += diff_error ** 2
            
        if source in metsystematics_sources:
            if diff > 0:
                totalMETPlus += diff ** 2
                totalMETPlus_err += diff_error ** 2
            else:
                totalMETMinus += diff ** 2
                totalMETMinus_err += diff_error ** 2
        
    total = sqrt(totalPlus + totalMinus)
    total_error = sqrt(totalPlus_err + totalMinus_err)
    totalPlus, totalMinus, totalPlus_err, totalMinus_err = (sqrt(totalPlus), sqrt(totalMinus),
                                                             sqrt(totalPlus_err), sqrt(totalMinus_err))
    
    totalMETPlus, totalMETMinus, totalMETPlus_err, totalMETMinus_err = (sqrt(totalMETPlus), sqrt(totalMETMinus),
                                                             sqrt(totalMETPlus_err), sqrt(totalMETMinus_err))
    uncertainty['Total+'] = [totalPlus, totalPlus_err]
    uncertainty['Total-'] = [totalMinus, totalMinus_err]
    uncertainty['Total'] = [total, total_error]
    uncertainty['TotalMETUnc+'] = [totalMETPlus, totalMETPlus_err]
    uncertainty['TotalMETUnc-'] = [totalMETMinus, totalMETMinus_err]
    uncertainty['PDFWeights+'] = [pdf_max, 0]
    uncertainty['PDFWeights-'] = [pdf_min, 0]
    
    return uncertainty

def calculate_purities( gen_vs_reco_histogram ):
    '''
    Takes a 2D histogram of generated versus reconstructed events and returns
    a list of *purity* values  for each bin.
    
    *purity* is defined as the number reconstructed & generated events in one 
    bin divided by the number of reconstructed events:
    p_i = \frac{N^{\text{rec\&gen}}}{N^{\text{rec}}}
    '''
    # assume reco = x axis and gen = y axis
    reco = asrootpy( gen_vs_reco_histogram.ProjectionX() )
    reco_i = list( reco.y() )
    n_bins = len( reco_i )
    
    purities = []
    add_purity = purities.append
    
    for i in range( 1, n_bins + 1 ):
        n_gen_and_reco = gen_vs_reco_histogram.GetBinContent( i, i )
        n_reco = reco_i[i - 1]
        p = 0
        if n_reco > 0:
            p = round( n_gen_and_reco / n_reco, 3 )
        add_purity( p )
        
    return purities

def calculate_stabilities( gen_vs_reco_histogram ):
    '''
    Takes a 2D histogram of generated versus reconstructed events and returns
    a list of *stability* values  for each bin.
    
    *stability* is defined as the number reconstructed & generated events in
    one bin divided by the number of generated events: 
    s_i = \frac{N^{\text{rec\&gen}}}{N^{\text{rec}}}
    '''
    # assume reco = x axis and gen = y axis
    gen = asrootpy( gen_vs_reco_histogram.ProjectionY() )
    gen_i = list( gen.y() )
    n_bins = len( gen_i )
    
    stabilities = []
    add_stability = stabilities.append
    
    for i in range( 1, n_bins + 1 ):
        n_gen_and_reco = gen_vs_reco_histogram.GetBinContent( i, i )
        n_gen = gen_i[i - 1]
        s = 0
        if n_gen > 0:
            s = round( n_gen_and_reco / n_gen, 3 )
        add_stability( s )
        
    return stabilities
    
def which_variable_bin(variable, value):
    variable_bin = 0
    # last bin is to INF
    for i,edge in enumerate(bin_edges[variable][:-1]):
        if value > edge:
            variable_bin = i
        else:
            break
    return variable_bin

