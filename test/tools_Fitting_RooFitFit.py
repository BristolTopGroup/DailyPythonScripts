'''
Created on 31 Oct 2012

@author: kreczko
'''
import unittest
from tools.Fitting import RooFitFit, FitData, FitDataCollection
from rootpy.plotting import Hist
from math import sqrt

import numpy as np
N_bkg1 = 9000
N_signal = 1000
N_bkg1_obs = 10000
N_signal_obs = 2000
N_data = N_bkg1_obs + N_signal_obs
mu1, mu2, sigma1, sigma2 = 100, 140, 15, 5
x1 = mu1 + sigma1 * np.random.randn(N_bkg1)
x2 = mu2 + sigma2 * np.random.randn(N_signal)
x1_obs = mu1 + sigma1 * np.random.randn(N_bkg1_obs)
x2_obs = mu2 + sigma2 * np.random.randn(N_signal_obs)

class Test(unittest.TestCase):

    def setUp(self):
        # create histograms
        h_bkg1_1 = Hist(100, 40, 200, title='Background')
        h_signal_1 = h_bkg1_1.Clone(title='Signal')
        h_data_1 = h_bkg1_1.Clone(title='Data')
    
        # fill the histograms with our distributions
        map(h_bkg1_1.Fill, x1)
        map(h_signal_1.Fill, x2)
        map(h_data_1.Fill, x1_obs)
        map(h_data_1.Fill, x2_obs)
        
        histograms_1 = {'signal': h_signal_1,
                      'bkg1': h_bkg1_1,
#                       'data': h_data_1
                      }
        fit_data_1 = FitData(h_data_1, histograms_1, fit_boundaries=(40, 200))
        self.single_fit_collection = FitDataCollection()
        self.single_fit_collection.add( fit_data_1 )
        
#         self.roofitFitter = RooFitFit(histograms_1, dataLabel='data', fit_boundries=(40, 200))
        self.roofitFitter = RooFitFit(self.single_fit_collection)

    def tearDown(self):
        pass

    def test_normalisation(self):
        normalisation = self.roofitFitter.normalisation
        self.assertAlmostEqual(normalisation["data"], N_data, delta=sqrt(N_data))
        self.assertAlmostEqual(normalisation["bkg1"], N_bkg1, delta=sqrt(N_bkg1))
        self.assertAlmostEqual(normalisation["signal"], N_signal, delta=sqrt(N_signal))
        
    def test_signal_result(self):
        self.roofitFitter.fit()
        results = self.roofitFitter.readResults()
        self.assertAlmostEqual(N_signal_obs, results['signal'][0], delta=2 * results['signal'][1])
        self.assertAlmostEqual(N_bkg1_obs, results['bkg1'][0], delta=2 * results['bkg1'][1])
        
    def test_constraints(self):
        self.single_fit_collection.set_normalisation_constraints({'signal': 0.8, 'bkg1': 0.5})
        self.roofitFitter = RooFitFit(self.single_fit_collection)
#         self.roofitFitter.set_fit_constraints({'signal': 0.8, 'bkg1': 0.5})
        self.roofitFitter.fit()
        results = self.roofitFitter.readResults()
        self.assertAlmostEqual(N_signal_obs, results['signal'][0], delta=2 * results['signal'][1])
        self.assertAlmostEqual(N_bkg1_obs, results['bkg1'][0], delta=2 * results['bkg1'][1])
        
#     def test_relative_error(self):
#         results = self.roofitFitter.readResults()
#         self.roofitFitter.saved_result.Print("v");
#         self.assertLess(results['signal'][1]/results['signal'][0], 0.1)
#         self.assertLess(results['bkg1'][1]/results['bkg1'][0], 0.1)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testTemplates']
    unittest.main()
