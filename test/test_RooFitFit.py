'''
Created on 31 Oct 2012

@author: kreczko
'''
import unittest
from tools.Fitting import RooFitFit
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
        h1 = Hist(100, 40, 200, title='Background')
        h2 = h1.Clone(title='Signal')
        h3 = h1.Clone(title='Data')
        h3.markersize=1.2
    
        # fill the histograms with our distributions
        map(h1.Fill, x1)
        map(h2.Fill, x2)
        map(h3.Fill, x1_obs)
        map(h3.Fill, x2_obs)
        
        histograms = {'signal': h2,
                      'bkg1': h1,
                      'data': h3}
        self.roofitFitter = RooFitFit(histograms, dataLabel='data', fit_boundries = (40, 200))
        self.roofitFitter.fit()


    def tearDown(self):
        pass

    def testTemplateKeys(self):
        templateKeys = sorted(self.roofitFitter.templates.keys())
        self.assertEqual(templateKeys, sorted(['signal', 'bkg1', 'data']))

    def testNormalisation(self):
        normalisation = self.roofitFitter.normalisation
        self.assertAlmostEqual(normalisation["data"], N_data, delta = sqrt(N_data))
        self.assertAlmostEqual(normalisation["bkg1"], N_bkg1, delta = sqrt(N_bkg1))
        self.assertAlmostEqual(normalisation["signal"], N_signal, delta = sqrt(N_signal))
        
    def testSignalResult(self):
        results = self.roofitFitter.readResults()
        self.assertAlmostEqual(N_signal_obs, results['signal'][0], delta=2 * results['signal'][1])
        self.assertAlmostEqual(N_bkg1_obs, results['bkg1'][0], delta=2 * results['bkg1'][1])
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testTemplates']
    unittest.main()
