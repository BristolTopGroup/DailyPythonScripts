'''
Created on 31 Oct 2012

@author: kreczko
'''
from __future__ import division
import unittest
from rootpy.plotting import Hist2D
from tools.hist_utilities import rebin_2d

import numpy as np

class Test( unittest.TestCase ):

    def setUp( self ):
        # create histograms
        self.h2 = Hist2D( 60, 40, 100, 60, 40, 100 )
    
        # fill the histograms with our distributions
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
            
if __name__ == "__main__":
    unittest.main()
