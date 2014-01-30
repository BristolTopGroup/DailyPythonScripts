'''
Created on 31 Oct 2012

@author: kreczko
'''
from __future__ import division
import unittest
from tools.Calculation import decombine_result

class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_default(self):
        N_signal = 100
        N_background = 20
        N_total = N_signal + N_background
        ratio_signal_bkg = N_signal/N_background
        
        N_total_prime = N_total * 2
        N_signal_prime, N_background_prime = decombine_result((N_total_prime, 0), ratio_signal_bkg)
        
        self.assertEqual(N_signal_prime[0], N_signal * 2)
        self.assertEqual(N_background_prime[0], N_background * 2)

    def test_background_free(self):
        N_signal = 100
        N_background = 0
        N_total = N_signal
        ratio_signal_bkg = 0
        
        N_total_prime = N_total * 2
        N_signal_prime, N_background_prime = decombine_result((N_total_prime, 0), ratio_signal_bkg)
        
        self.assertEqual(N_signal_prime[0], N_signal * 2)
        self.assertEqual(N_background_prime[0], N_background * 2)
        
    def test_multiple_backgrounds(self):
        N_signal = 100
        N_background_1 = 20
        N_background_2 = 40
        N_total = N_signal + N_background_1 + N_background_2
        # ratio of bkg_1 to other samples
        ratio_signal_bkg_1 = (N_signal + N_background_2)/N_background_1
        # ratio of bkg_2 to signal
        ratio_signal_bkg_2 = N_signal/N_background_2
        
        N_total_prime = N_total * 2
        N_signal_plus_bkg_2_prime, N_background_1_prime = decombine_result((N_total_prime, 0), ratio_signal_bkg_1)
        N_signal_prime, N_background_2_prime = decombine_result((N_signal_plus_bkg_2_prime, 0), ratio_signal_bkg_2)
        
        self.assertEqual(N_signal_prime[0], N_signal * 2)
        self.assertEqual(N_background_1_prime[0], N_background_1 * 2)
        self.assertEqual(N_background_2_prime[0], N_background_2 * 2)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testTemplates']
    unittest.main()
