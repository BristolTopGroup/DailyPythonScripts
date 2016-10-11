'''
Created on 31 Oct 2012

@author: kreczko
'''
from __future__ import division
import unittest
from random import random
import numpy as np
from rootpy.plotting import Hist2D

# under test
from dps.utils.Calculation import calculate_purities
from dps.utils.Calculation import calculate_stabilities
from dps.utils.Calculation import decombine_result

class Test( unittest.TestCase ):

    def setUp( self ):
        # we only test symmetric bins for now
        self.n_bins_x = 6
        self.n_bins_y = 6
        # only entries in diagonals, p = 1, s = 1 for all bins
        self.best_case = Hist2D( self.n_bins_x, -3, 3, self.n_bins_y, 0, 6 )
        for i in range( 1, self.n_bins_x + 1 ):
            self.best_case.SetBinContent( i, i, random() * 1000 )
            
        # random eclipse
        self.random_elipse = Hist2D( self.n_bins_x, -3, 3, self.n_bins_y, 0, 6 )
        self.random_elipse.fill_array( 
                np.random.multivariate_normal( 
                        mean = ( 0, 3 ),
                        cov = [[1., 1.12], [1.12, 2.25]],
                        size = ( 1000 ) 
                        ) 
                )
        
        # this creates
        # [4, 0, 0, 0, 0, 1],
        # [0, 0, 0, 0, 1, 0],
        # [0, 0, 0, 1, 0, 0],
        # [0, 0, 1, 0, 0, 0],
        # [0, 1, 0, 0, 0, 0],
        # [1, 0, 0, 0, 0, 3],
        # this should result in a purity and stability value of 1 for all bins
        # except the first and last. The first bin should have p = 1/5 and 
        # s = 1/4 and the last bin should have p = 1/4 and s = 1/5
        
        self.pre_calculated = Hist2D( self.n_bins_x, -3, 3, self.n_bins_y, 0, 6 )
        for i in range( 1, self.n_bins_x + 1 ):
            self.pre_calculated.SetBinContent( i, i, 1 )
        self.pre_calculated.SetBinContent( 1, self.n_bins_y, 4 )
        self.pre_calculated.SetBinContent( self.n_bins_x, 1, 3 )
        


    def tearDown( self ):
        pass
    
    def test_best_case_purity( self ):
        purities = calculate_purities( self.best_case )
        self.assertEqual( len( purities ), self.n_bins_x, 'Invalid number of purity terms' )
        for p in purities:
            self.assertEqual( p, 1 )
            
    def test_best_case_stability( self ):
        stabilities = calculate_stabilities( self.best_case )
        self.assertEqual( len( stabilities ), self.n_bins_x, 'Invalid number of stability terms' )
        for s in stabilities:
            self.assertEqual( s, 1 )
            
    def test_random_elipse_purity( self ):
        purities = calculate_purities( self.random_elipse )
        self.assertEqual( len( purities ), self.n_bins_x, 'Invalid number of purity terms' )

        # purities should always be above 0 and below ~0.5
        for p in purities:
            self.assertGreater( p, 0 )
            # allow for 10% error due to randomness
            self.assertLess( p, 0.5 + 0.1)
            
    def test_random_elipse_stability( self ):
        stabilities = calculate_stabilities( self.random_elipse )
        self.assertEqual( len( stabilities ), self.n_bins_x, 'Invalid number of stability terms' )

        # stabilities should always be above 0 and below ~0.6
        for s in stabilities:
            self.assertGreater( s, 0 )
            # allow for 10% error due to randomness
            self.assertLess( s, 0.6 + 0.06)
            
    def test_pre_calculated_purity( self ):
        purities = calculate_purities( self.pre_calculated )
        self.assertEqual( len( purities ), self.n_bins_x, 'Invalid number of purity terms' )
        for p in purities[1:-1]:
            self.assertEqual( p, 1 )
        self.assertEqual( purities[0], 0.2 )
        self.assertEqual( purities[-1], 0.25 )
            
    def test_pre_calculated_stability( self ):
        stabilities = calculate_stabilities( self.pre_calculated )
        self.assertEqual( len( stabilities ), self.n_bins_x, 'Invalid number of stability terms' )
        for s in stabilities[1:-1]:
            self.assertEqual( s, 1 )
        self.assertEqual( stabilities[0], 0.25 )
        self.assertEqual( stabilities[-1], 0.2 )
        
    def test_decombine_result_default(self):
        N_signal = 100
        N_background = 20
        N_total = N_signal + N_background
        ratio_signal_bkg = N_signal/N_background
        
        N_total_prime = N_total * 2
        N_signal_prime, N_background_prime = decombine_result((N_total_prime, 0), ratio_signal_bkg)
        
        self.assertEqual(N_signal_prime[0], N_signal * 2)
        self.assertEqual(N_background_prime[0], N_background * 2)

    def test_decombine_result_background_free(self):
        N_signal = 100
        N_background = 0
        N_total = N_signal
        ratio_signal_bkg = 0
        
        N_total_prime = N_total * 2
        N_signal_prime, N_background_prime = decombine_result((N_total_prime, 0), ratio_signal_bkg)
        
        self.assertEqual(N_signal_prime[0], N_signal * 2)
        self.assertEqual(N_background_prime[0], N_background * 2)
        
    def test_decombine_result_multiple_backgrounds(self):
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
        N_signal_prime, N_background_2_prime = decombine_result(N_signal_plus_bkg_2_prime, ratio_signal_bkg_2)
        
        self.assertEqual(N_signal_prime[0], N_signal * 2)
        self.assertEqual(N_background_1_prime[0], N_background_1 * 2)
        self.assertEqual(N_background_2_prime[0], N_background_2 * 2)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testTemplates']
    unittest.main()
