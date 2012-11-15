'''
Created on 31 Oct 2012

@author: kreczko
'''
import unittest
from tools.Fitter import TMinuitFit
from rootpy.plotting import Hist

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
        self.minuitFitter = TMinuitFit(histograms, dataLabel='data')
        self.minuitFitter.fit()


    def tearDown(self):
        pass

    def testTemplateKeys(self):
        templateKeys = sorted(self.minuitFitter.templates.keys())
        self.assertEqual(templateKeys, sorted(['signal', 'bkg1', 'data']))

    def testNormalisation(self):
        normalisation = self.minuitFitter.normalisation
        self.assertAlmostEqual(normalisation["data"], N_data, delta = 1)
        self.assertAlmostEqual(normalisation["bkg1"], N_bkg1, delta = 1)
        self.assertAlmostEqual(normalisation["signal"], N_signal, delta = 1)
        
    def testSignalResult(self):
        results = self.minuitFitter.readResults()
        self.assertAlmostEqual(N_signal_obs, results['signal']['value'], delta = results['signal']['error'])
        self.assertAlmostEqual(N_bkg1_obs, results['bkg1']['value'], delta = results['bkg1']['error'])
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testTemplates']
    unittest.main()