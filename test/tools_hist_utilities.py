'''
Created on 31 Oct 2012

@author: kreczko
'''
from __future__ import division
import unittest
from rootpy.plotting import Hist, Hist2D
from tools.hist_utilities import rebin_2d, adjust_overflow_to_limit, hist_to_value_error_tuplelist

import numpy as np
N_bkg1 = 9000
mu1, sigma1 = 50, 20
x1 = mu1 + sigma1 * np.random.randn( N_bkg1 )

class Test( unittest.TestCase ):

    def setUp( self ):
        # create histograms
        self.h1 = Hist( 100, 0, 100, title = '1D' )
        self.h2 = Hist2D( 60, 40, 100, 60, 40, 100 )
        self.simple = Hist( 100, 0, 100, title = '1D' )
    
        # fill the histograms with our distributions
        map( self.h1.Fill, x1 )
        self.h2.fill_array( np.random.multivariate_normal( 
                                    mean = ( 50, 50 ),
                                    cov = np.arange( 4 ).reshape( 2, 2 ),
                                    size = ( int( 1E6 ), ) ) 
                        )
        self.bins = [40, 45, 50, 60, 65, 70, 75, 80, 100]
        # rebin them
        self.h2_rebinned = self.h2.rebinned( self.bins, axis = 0 )
        self.h2_rebinned = self.h2_rebinned.rebinned( self.bins, axis = 1 )
        self.h2_rebinned_2 = rebin_2d( self.h2, self.bins, self.bins )
        
        # we only test symmetric bins for now
        self.n_bins_x = 5
        self.n_bins_y = 5
        # only entries in diagonals, p = 1, s = 1 for all bins
        self.diagonals = Hist2D( self.n_bins_x, 0, 10, self.n_bins_y, 0, 10 )
        # this creates
        # [0, 0, 0, 0, 1],
        # [0, 0, 0, 1, 0],
        # [0, 0, 1, 0, 0],
        # [0, 1, 0, 0, 0],
        # [1, 0, 0, 0, 0]
        for i in range( 1, self.n_bins_x + 1 ):
            self.diagonals.SetBinContent( i, i, 1 )
        
        # the following should result in
        # [0, 0, 2],
        # [0, 2, 0],
        # [1, 0, 0]    
        self.bin_edges_nice = [0, 2, 6, 10]
        self.result_nice = [1, 2, 2]
        
        # the following should result in
        # [0, 0, 0, 2],
        # [0, 0, 2, 0]
        # [0, 1, 0, 0]
        # [0, 0, 0, 0]  
        self.bin_edges_out_of_bound = [-2, 0, 2, 6, 20]
        self.result_out_of_bound = [0, 1, 2, 2]
        # the following should result in
        # [0, 0, 2],
        # [0, 1, 0],
        # [2, 0, 0] 
        self.bin_edges_not_on_boundaries = [0, 3.5, 6, 20]
        self.result_not_on_boundaries = [2, 1, 2]
        
        for i in range(100):
            self.simple.Fill(i, 1)

    def tearDown( self ):
        pass

    def test_rebin_2d_vs_rootpy_rebin( self ):
        for i, _ in enumerate( self.bins[1:] ):
            bin_content = self.h2_rebinned.GetBinContent( i + 1, i + 1 )
            bin_content_2 = self.h2_rebinned_2.GetBinContent( i + 1, i + 1 )
            self.assertEqual( bin_content, bin_content_2 )
            
    def test_2D_integral( self ):
        for i, bin_i in enumerate( self.bins[:-1] ):
            current_bin_start = self.h2.FindBin( bin_i )
            current_bin_end = self.h2.FindBin( self.bins[i + 1] )
            integral = self.h2.Integral( current_bin_start, current_bin_end - 1, current_bin_start, current_bin_end - 1 )
            bin_content = self.h2_rebinned.GetBinContent( i + 1 , i + 1 )
            self.assertEqual( bin_content, integral )
            
    def test_rebin_2d_nice( self ):
        new_hist = rebin_2d( self.diagonals, self.bin_edges_nice, self.bin_edges_nice )
        for i in range( 1, new_hist.nbins() + 1 ):
            
            self.assertEqual( 
                new_hist.GetBinContent( i, i ),
                self.result_nice[i - 1],
                'histogram contents do not match' )
            
    def test_rebin_2d_out_of_bound( self ):
        new_hist = rebin_2d( self.diagonals, self.bin_edges_out_of_bound, self.bin_edges_out_of_bound )
        for i in range( 1, new_hist.nbins() + 1 ):
            self.assertEqual( 
                new_hist.GetBinContent( i, i ),
                self.result_out_of_bound[i - 1],
                'histogram contents do not match' )
             
    def test_rebin_2d_not_on_boundaries( self ):
        new_hist = rebin_2d( self.diagonals, self.bin_edges_not_on_boundaries, self.bin_edges_not_on_boundaries )
        for i in range( 1, new_hist.nbins() + 1 ):
            self.assertEqual( 
                new_hist.GetBinContent( i, i ),
                self.result_not_on_boundaries[i - 1],
                'histogram contents do not match' )
            
            
    def test_adjust_overflow_to_limit_simple( self ):
        x_min = 0
        x_max = 95
        adjusted = adjust_overflow_to_limit(self.simple, x_min, x_max)
#         for entry_1, entry_2 in zip(hist_to_value_error_tuplelist(self.simple), hist_to_value_error_tuplelist(adjusted)):
#             print entry_1, entry_2
#         print self.simple.integral( overflow = True ), adjusted.integral()
#         print self.simple.GetBinContent(1), self.simple.GetBinContent(self.simple.nbins())
        # number of events should be unchanged
        # the adjusted histogram should have no overflow for this example
        self.assertEqual( self.simple.integral( overflow = True ), adjusted.integral() )
        # first bin (x_min) should contain all events
        # with x <= x_min
        x_min_bin = self.simple.FindBin(x_min)
        x_max_bin = self.simple.FindBin(x_max)
        self.assertEqual(self.simple.integral(0, x_min_bin), 
                         adjusted.GetBinContent(x_min_bin))
        # last bin (x_max) should contain all events
        # with x >= x_max
        self.assertEqual( self.simple.integral( x_max_bin, self.simple.nbins() + 1),
                         adjusted.GetBinContent( x_max_bin ) )
        
        
    def test_adjust_overflow_to_limit( self ):
        x_min = 40
        x_max = 80
        adjusted = adjust_overflow_to_limit(self.h1, x_min, x_max)
        # number of events should be unchanged
        # the adjusted histogram should have no overflow for this example
        self.assertEqual(self.h1.integral( overflow = True ), adjusted.Integral())
        # first bin (x_min) should contain all events
        # with x <= x_min
        x_min_bin = self.h1.FindBin(x_min)
        x_max_bin = self.h1.FindBin(x_max)
        self.assertEqual(self.h1.integral(0, x_min_bin), 
                         adjusted.GetBinContent(x_min_bin))
        # last bin (x_max) should contain all events
        # with x >= x_max
        self.assertEqual( self.h1.integral( x_max_bin, self.h1.nbins() + 1 ),
                         adjusted.GetBinContent( x_max_bin ) )
        
            
if __name__ == "__main__":
    unittest.main()
