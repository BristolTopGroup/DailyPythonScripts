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
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt


class Unfolding:

    def __init__(self, truth, measured, response, method='RooUnfoldSvd'):
        if not method in unfoldCfg.availablemethods:
            raise ValueError('Unknown unfolding method "%s". Available methods: %s' % (method, str(self.availablemethods)))
        self.method = method        
        self.truth = truth
        self.measured = measured
        self.response = response
        self.data = None
        self.unfolded_closure = None
        self.unfolded_data = None
        self.unfoldObject = None
        self.unfoldResponse = None
    
    def unfold(self, data):
        self.data = data
        if not self.unfoldResponse:
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
        if not self.unfoldingObject:
            if not self.unfoldResponse:
                self.unfoldResponse = self._makeUnfoldResponse()
            if self.method == 'RooUnfoldBayes':
                self.closure_test = RooUnfoldBayes     (self.response, self.measured, unfoldCfg.Bayes_n_repeat)
            elif self.method == 'RooUnfoldBinByBin':
                self.closure_test = RooUnfoldBinByBin     (self.response, self.measured)
            elif self.method == 'RooUnfoldInvert':
                self.closure_test = RooUnfoldInvert     (self.response, self.measured)
            elif self.method == 'RooUnfoldTUnfold':
                self.closure_test = RooUnfoldInvert     (self.response, self.measured)
            elif self.method == 'RooUnfoldSvd':
                self.closure_test = RooUnfoldSvd(self.response, self.measured, unfoldCfg.SVD_k_value, unfoldCfg.SVD_n_toy)
        self.unfolded_closure = asrootpy(self.unfoldObject.Hreco())
        return self.unfolded_closure
    
    def _makeUnfoldResponse(self):
        return RooUnfoldResponse (self.measured, self.truth, self.response)

    def saveClosureTest(self, outputfile, **kwargs):
        if not self.unfolded_closure:
            print 'Run closureTest function first'
            return
        self.setDrawStyles()
        # TODO: change this to be more generic
        plt.figure(figsize=(16, 10), dpi=100)
        rplt.hist(self.truth, label=r'truth', stacked=False)
        rplt.hist(self.measured, label=r'measured', stacked=False)
        rplt.errorbar(self.unfolded_closure, label='unfolded')
        plt.xlabel('$E_{\mathrm{T}}^{miss}$')
        plt.axis([0, 1000, 0, 60000])
        plt.ylabel('Events')
        plt.title('Unfolding')
        plt.legend()
        plt.savefig('Unfolding_' + self.method + '_closureTest.png')
    
    def saveUnfolding(self, outputfile, **kwargs):
        if not self.unfolded_data:
            print 'Run unfold function first'
            return
        self.setDrawStyles()
        # TODO: change this to be more generic
        plt.figure(figsize=(16, 10), dpi=100)
        rplt.hist(self.truth, label=r'SM $\mathrm{t}\bar{\mathrm{t}}$ truth', stacked=False)
        rplt.hist(self.data, label=r'$\mathrm{t}\bar{\mathrm{t}}$ from fit', stacked=False)
        rplt.errorbar(self.unfolded_data, label='unfolded')
        plt.xlabel('$E_{\mathrm{T}}^{miss}$')
        plt.axis([0, 1000, 0, 60000])
        plt.ylabel('Events')
        plt.title('Unfolding')
        plt.legend()
        plt.savefig(outputfile)
    
    def setDrawStyles(self):
        if self.unfolded_data:
            self.unfolded_data.SetFillStyle(unfoldCfg.unfolded_fillStyle)
            self.unfolded_data.SetColor(unfoldCfg.unfolded_color)
            self.unfolded_data.SetMarkerStyle(unfoldCfg.unfolded_markerStyle)
        
        if self.unfolded_closure:
            self.unfolded_closure.SetFillStyle(unfoldCfg.unfolded_fillStyle)
            self.unfolded_closure.SetColor(unfoldCfg.unfolded_color)
            self.unfolded_closure.SetMarkerStyle(unfoldCfg.unfolded_markerStyle)
        
        self.truth.SetFillStyle(unfoldCfg.truth_fillStyle)
        self.truth.SetColor(unfoldCfg.truth_color)
        
        self.measured.SetFillStyle(unfoldCfg.measured_fillStyle)
        self.measured.SetColor(unfoldCfg.measured_color)
        
        self.data.SetFillStyle(unfoldCfg.measured_fillStyle)
        self.data.SetColor(unfoldCfg.measured_color)
        
    def printTable(self):
        self.unfoldObject.PrintTable(cout, self.truth)
