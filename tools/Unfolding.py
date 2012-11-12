'''
Created on 31 Oct 2012

@author: kreczko
'''

from ROOT import gSystem, cout
import config.RooUnfold as unfoldCfg
gSystem.Load(unfoldCfg.library)
from ROOT import RooUnfoldResponse, RooUnfold, RooUnfoldBayes, RooUnfoldSvd
from ROOT import RooUnfoldBinByBin, RooUnfoldInvert, RooUnfoldTUnfold
from rootpy.utils import asrootpy
from math import sqrt

class Unfolding:

    def __init__(self, truth, measured, response, fakes=None, method='RooUnfoldSvd'):
        if not method in unfoldCfg.availablemethods:
            raise ValueError('Unknown unfolding method "%s". Available methods: %s' % (method, str(self.availablemethods)))
        self.method = method        
        self.truth = truth
        self.measured = measured
        self.fakes = fakes
        self.response = response
        self.data = None
        self.unfolded_closure = None
        self.unfolded_data = None
        self.unfoldObject = None
        self.unfoldResponse = None
        self.closure_test = None
    
    def unfold(self, data):
        self.data = data
        if not self.unfoldObject:
            if not self.unfoldResponse:
                self.unfoldResponse = self._makeUnfoldResponse()
            if self.method == 'RooUnfoldBayes':
                self.unfoldObject = RooUnfoldBayes     (self.unfoldResponse, data, unfoldCfg.Bayes_n_repeat)
            elif self.method == 'RooUnfoldBinByBin':
                self.unfoldObject = RooUnfoldBinByBin     (self.unfoldResponse, data)
            elif self.method == 'RooUnfoldInvert':
                self.unfoldObject = RooUnfoldInvert     (self.unfoldResponse, data)
            elif self.method == 'RooUnfoldTUnfold':
                self.unfoldObject = RooUnfoldTUnfold     (self.unfoldResponse, data)
            elif self.method == 'RooUnfoldSvd':
                self.unfoldObject = RooUnfoldSvd(self.unfoldResponse, data, unfoldCfg.SVD_k_value, unfoldCfg.SVD_n_toy)
        self.unfolded_data = asrootpy(self.unfoldObject.Hreco())
        return self.unfolded_data
    
    def closureTest(self):
        if not self.closure_test:
            if not self.unfoldResponse:
                self.unfoldResponse = self._makeUnfoldResponse()
            if self.method == 'RooUnfoldBayes':
                self.closure_test = RooUnfoldBayes     (self.unfoldResponse, self.measured, unfoldCfg.Bayes_n_repeat)
            elif self.method == 'RooUnfoldBinByBin':
                self.closure_test = RooUnfoldBinByBin     (self.unfoldResponse, self.measured)
            elif self.method == 'RooUnfoldInvert':
                self.closure_test = RooUnfoldInvert     (self.unfoldResponse, self.measured)
            elif self.method == 'RooUnfoldTUnfold':
                self.closure_test = RooUnfoldTUnfold     (self.unfoldResponse, self.measured)
            elif self.method == 'RooUnfoldSvd':
                self.closure_test = RooUnfoldSvd(self.unfoldResponse, self.measured, unfoldCfg.SVD_k_value, unfoldCfg.SVD_n_toy)
        self.unfolded_closure = asrootpy(self.closure_test.Hreco())
        return self.unfolded_closure
    
    def _makeUnfoldResponse(self):
        if self.fakes:
            return RooUnfoldResponse (self.measured, self.truth, self.fakes, self.response)
        else:
            return RooUnfoldResponse (self.measured, self.truth, self.response)

    def printTable(self):
        self.unfoldObject.PrintTable(cout, self.truth)
    
    def Reset(self):
        if self.unfoldObject:
            self.unfoldObject = None
        if self.closure_test:
            self.closure_test = None
            
    def chi2(self):
        chi2 = 99999999, 0
        if self.unfolded_data and self.truth:
            diff = self.truth - self.unfolded_data
            values = list(diff)
            errors = []
            for bin_i in range(len(values)):
                errors.append(diff.GetBinError(bin_i + 1))
            values = [abs(value) for value in values]
            errorsSquared = [error* error for error in errors]
            value = sum(values)
            error = sqrt(sum(errorsSquared))
            chi2 = value, error
        return chi2
    
    def pull(self):
        result = [9999999]
        if self.unfolded_data and self.truth:
            diff = self.unfolded_data - self.truth 
            errors = []
            values = list(diff)
            for bin_i in range(len(values)):
                errors.append(self.unfolded_data.GetBinError(bin_i + 1))
            result = [value/error for value, error in zip(values, errors)]
        return result
            
