'''
Created on Aug 3, 2012

@author: Lukasz Kreczko

Email: Lukasz.Kreczko@cern.ch
'''
from __future__ import division
from data.results import *
from scipy.misc.common import comb
from math import sqrt

error_correlations = {
                      'stat error': 0,
                      'lumi_down': 0,
                      'lumi_up': 0,
                      }


def combine(result1, result2, errors1, errors2):#errors have to be relative!!
    #absolute errors
    totalErrors1 = getTotalError(errors1)
    totalErrors2 = getTotalError(errors2)
    
    numerator = result1 / pow(totalErrors1['total'], 2) + result2 / pow(totalErrors2['total'], 2)
    denominator = 1. / pow(totalErrors1['total'], 2) + 1 / pow(totalErrors2['total'], 2)
    combinedResult = numerator / denominator
    
    inverseSumUpErrors = 1. / pow(totalErrors1['up'], 2) + 1 / pow(totalErrors2['up'], 2)
    inverseSumDownErrors = 1. / pow(totalErrors1['down'], 2) + 1 / pow(totalErrors2['down'], 2)
    combinedUpError = sqrt(1. / inverseSumUpErrors)
    combinedDownError = sqrt(1. / inverseSumDownErrors)
    
    errorNames = list(set(errors1.keys() + errors2.keys())) 
    sumOfInverseErrors = 0
    for errorName in errorNames:
        correlation = 0
        if error_correlations.has_key(errorName):
            correlation = error_correlations[errorName]
        error = 0
        if errorName in errors1.keys() and errorName in errors2.keys() and not correlation == 0:
            error = 1. / pow(errors1[errorName], 2) + 1 / pow(errors2[errorName], 2) + 1 / (2*pow(errors1[errorName] * errors2[errorName] * correlation, 2))
        elif errorName in errors1.keys() and errorName in errors2.keys() and correlation == 0:
            error = 1. / pow(errors1[errorName], 2) + 1 / pow(errors2[errorName], 2)
        elif errorName in errors1.keys() and not errorName in errors2.keys():
            error = 1. / pow(errors1[errorName], 2)
        elif not errorName in errors1.keys() and errorName in errors2.keys():
            error = 1. / pow(errors2[errorName], 2)
        sumOfInverseErrors += error
        
    return combinedResult, combinedUpError, combinedDownError, sqrt(1 / sumOfInverseErrors)
    

def getTotalError(errors):
    totalUp = 0
    totalDown = 0
    for name, error in errors.iteritems():
        if error > 0:
            totalUp += error ** 2
        else:
            totalDown += error ** 2
    total = totalUp + totalDown
    total = sqrt(total)
    totalUp = sqrt(totalUp)
    totalDown = sqrt(totalDown)
    return {'up':totalUp, 'down':totalDown, 'total':total}

def combineErrors(errors1, errors2):
    pass

if __name__ == "__main__":
    #testing
    result1 = 2
    result2 = 5
    errors1 = {'stat error': 0.5, 'lumi_down':-0.5, 'lumi_up': 0.5}
    errors2 = {'stat error': 0.5, 'lumi_down':-0.5, 'lumi_up': 0.5}
    combination = combine(result1, result2, errors1, errors2)
    print combination
    
