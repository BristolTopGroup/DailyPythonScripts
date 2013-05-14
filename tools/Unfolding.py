'''
Created on 31 Oct 2012

@author: kreczko
'''

from ROOT import gSystem, cout, TDecompSVD
import config.RooUnfold as unfoldCfg
gSystem.Load(unfoldCfg.library)
from ROOT import RooUnfoldResponse, RooUnfold, RooUnfoldBayes, RooUnfoldSvd
from ROOT import RooUnfoldBinByBin, RooUnfoldInvert, RooUnfoldTUnfold
from ROOT import TSVDUnfold
from rootpy import asrootpy
from rootpy.plotting import Hist, Hist2D
from math import sqrt
class Unfolding:

    def __init__(self, truth, measured, response, fakes=None, method='RooUnfoldSvd'):
        if not method in unfoldCfg.availablemethods:
            raise ValueError('Unknown unfolding method "%s". Available methods: %s' % (method, str(unfoldCfg.availablemethods)))
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
        self.verbose = 0
    
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
            elif self.method == 'TSVDUnfold':
                new_data = Hist(list(data.xedges()), type = 'D')
                new_data.Add(data)
                new_measured = Hist(list(self.measured.xedges()), type = 'D')
                new_measured.Add(self.measured)
                new_truth = Hist(list(self.truth.xedges()), type = 'D')
                new_truth.Add(self.truth)
                new_response = Hist2D(list(self.response.xedges()),list(self.response.yedges()), type = 'D')
                new_response.Add(self.response)
                self.unfoldObject = TSVDUnfold(new_data, new_measured, new_truth, new_response)
        if self.method == 'TSVDUnfold':
            self.unfolded_data = asrootpy(self.unfoldObject.Unfold(unfoldCfg.SVD_k_value))
        else:
            self.unfoldObject.SetVerbose(self.verbose)
            self.unfolded_data = asrootpy(self.unfoldObject.Hreco(unfoldCfg.Hreco))
        #remove unfold reports (faster)
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
            elif self.method == 'TSVDUnfold':
                new_measured = Hist(list(self.measured.xedges()), type = 'D')
                new_measured.Add(self.measured)
                new_truth = Hist(list(self.truth.xedges()), type = 'D')
                new_truth.Add(self.truth)
                new_response = Hist2D(list(self.response.xedges()),list(self.response.yedges()), type = 'D')
                new_response.Add(self.response)
                self.closure_test = TSVDUnfold(new_measured, new_measured, new_truth, new_response)
        if self.method == 'TSVDUnfold':
            self.unfolded_closure = asrootpy(self.closure_test.Unfold(unfoldCfg.SVD_k_value))
        else:
            self.unfolded_closure = asrootpy(self.closure_test.Hreco(unfoldCfg.Hreco))
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
                errors.append(diff.GetBinError(bin_i + 1))
            result = [value/error for value, error in zip(values, errors)]
        return result
    
    def pull_inputErrorOnly(self):
        result = [9999999]
        if self.unfolded_data and self.truth:
            # set unfolded_data errors to stat errors from data
            temp = self.unfolded_data.Clone()
            temp_list = list(temp)
#            data_list = list(self.data)
            unfolded_errors = self.get_unfolded_data_errors()
            for bin_i in range(len(temp_list)):
                temp.SetBinError(bin_i+1, unfolded_errors[bin_i])
            #set truth errors to 0
            temp_truth = self.truth.Clone()
            for bin_i in range(len(temp_truth)):
                temp_truth.SetBinError(bin_i +1, 0)
                
            diff = temp - temp_truth
            errors = []
            values = list(diff)
            for bin_i in range(len(values)):
                errors.append(diff.GetBinError(bin_i + 1))
            result = [value/error for value, error in zip(values, errors)]
        return result
    
    def get_unfolded_data_errors(self):
        #get the data errors
        input_errors = self.unfoldObject.Emeasured()
#        input_errors.Print()
        unfolded_errors = input_errors.Clone()
        #get the response matrix
        decomposition = TDecompSVD(self.unfoldResponse.Mresponse());
        #apply R-1 to data errors
        decomposition.Solve(unfolded_errors);
        
        return unfolded_errors
            
