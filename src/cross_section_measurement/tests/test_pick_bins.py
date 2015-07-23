'''
Created on 31 Oct 2012

@author: kreczko
'''
from __future__ import division
import unittest
from rootpy.plotting import Hist2D
from tools.Calculation import calculate_purities, calculate_stabilities
import importlib
from tools.hist_utilities import rebin_2d

pick_bins = importlib.import_module( "src.cross_section_measurement.00_pick_bins" )


import numpy as np

class Test( unittest.TestCase ):


    def setUp( self ):
        

        # create histograms
        self.h1 = Hist2D( 60, 40, 100, 60, 40, 100 )
        self.h2 = Hist2D( 60, 40, 100, 60, 40, 100 )
        self.h3 = Hist2D( 60, 40, 100, 60, 40, 100 )
    
        n_1 = 10000
        n_2 = int( n_1 / 5 )
        x_1 = 60 + 10 * np.random.randn( n_1 )
        x_2 = 60 + 10 * np.random.randn( n_2 )
        x_3 = 60 + 5 * np.random.randn( n_1 )
        y_1 = x_1 + np.random.randn( n_1 )
        y_2 = x_2 + np.random.randn( n_2 )
        y_3 = x_3 + np.random.randn( n_1 )
        
        z_1 = np.vstack( ( x_1, y_1 ) ).T
        z_2 = np.vstack( ( x_2, y_2 ) ).T
        z_3 = np.vstack( ( x_3, y_3 ) ).T
        # fill the histograms with our distributions
        self.h1.fill_array( z_1 )
        # reduced number of events
        self.h2.fill_array( z_2 )
        # reduced spread
        self.h3.fill_array( z_3 )
        
        self.histogram_information_1 = [
                {'hist': self.h1,
                 'CoM': 7,
                 'channel':'test_1'},
                   ]
        self.histogram_information_2 = [
                {'hist': self.h2,
                 'CoM': 7,
                 'channel':'test_2'},
                   ]
        self.histogram_information_3 = [
                {'hist': self.h3,
                 'CoM': 7,
                 'channel':'test_3'},
                   ]
        self.histogram_information_1_2 = [
                {'hist': self.h1,
                 'CoM': 7,
                 'channel':'test_1'},
                {'hist': self.h2,
                 'CoM': 7,
                 'channel':'test_2'},
                   ]
        self.histogram_information_1_3 = [
                {'hist': self.h1,
                 'CoM': 7,
                 'channel':'test_1'},
                {'hist': self.h3,
                 'CoM': 7,
                 'channel':'test_3'},
                   ]
        # requirements for new binning
        self.p_min, self.s_min, self.n_min = 0.5, 0.5, 100
        self.bin_edges_1, _ = pick_bins.get_best_binning( 
                                        self.histogram_information_1, 
                                        self.p_min, 
                                        self.s_min, 
                                        self.n_min 
                                        )
        self.bin_edges_2, _ = pick_bins.get_best_binning( 
                                        self.histogram_information_2, 
                                        self.p_min, 
                                        self.s_min, 
                                        self.n_min 
                                        )
        self.bin_edges_3, _ = pick_bins.get_best_binning( 
                                        self.histogram_information_3, 
                                        self.p_min, 
                                        self.s_min, 
                                        self.n_min 
                                        )
        self.bin_edges_1_2, _ = pick_bins.get_best_binning( 
                                        self.histogram_information_1_2, 
                                        self.p_min, 
                                        self.s_min, 
                                        self.n_min 
                                        )
        self.bin_edges_1_3, _ = pick_bins.get_best_binning( 
                                        self.histogram_information_1_3, 
                                        self.p_min, 
                                        self.s_min, 
                                        self.n_min 
                                        )
        
        self.h1_rebinned = rebin_2d(self.h1, self.bin_edges_1, self.bin_edges_1)
        self.h2_rebinned = rebin_2d(self.h2, self.bin_edges_2, self.bin_edges_2)
        self.h3_rebinned = rebin_2d(self.h3, self.bin_edges_3, self.bin_edges_3)
        self.h1_2_rebinned = rebin_2d(self.h1, self.bin_edges_1_2, self.bin_edges_1_2)
        self.h1_3_rebinned = rebin_2d(self.h1, self.bin_edges_1_3, self.bin_edges_1_3)
        

    def tearDown( self ):
        pass
            
    def test_purities( self ):
        purities_1 = calculate_purities( self.h1_rebinned )
        for purity in purities_1:
            self.assertGreaterEqual( purity, self.p_min )
            
    def test_purities_reduced_N(self):
        purities = calculate_purities( self.h2_rebinned )
        for purity in purities:
            self.assertGreaterEqual( purity, self.p_min )
             
    def test_purities_reduced_spread(self):
        purities = calculate_purities( self.h3_rebinned )
        for purity in purities:
            self.assertGreaterEqual( purity, self.p_min )
            
    def test_purities_combined_1_2(self):
        purities = calculate_purities( self.h1_2_rebinned )
        for purity in purities:
            self.assertGreaterEqual( purity, self.p_min )
    
    def test_purities_combined_1_3(self):
        purities = calculate_purities( self.h1_3_rebinned )
        for purity in purities:
            self.assertGreaterEqual( purity, self.p_min )
             
    def test_stabilities( self ):
        stabilities_1 = calculate_stabilities( self.h1_rebinned )
        for stability in stabilities_1:
            self.assertGreaterEqual( stability, self.s_min )
            
    def test_stabilities_reduced_N(self):
        stabilities = calculate_stabilities( self.h2_rebinned )
        for stability in stabilities:
            self.assertGreaterEqual( stability, self.s_min )
             
    def test_stabilities_reduced_spread(self):
        stabilities = calculate_stabilities( self.h3_rebinned )
        for stability in stabilities:
            self.assertGreaterEqual( stability, self.s_min )
            
    def test_stabilities_combined_1_2(self):
        stabilities = calculate_stabilities( self.h1_2_rebinned )
        for stability in stabilities:
            self.assertGreaterEqual( stability, self.s_min )
    
    def test_stabilities_combined_1_3(self):
        stabilities = calculate_stabilities( self.h1_3_rebinned )
        for stability in stabilities:
            self.assertGreaterEqual( stability, self.s_min )
             
    def test_n_events( self ):
        n_events = [self.h1_rebinned.GetBinContent( i, i ) for i in range( 1, len( self.bin_edges_1 ) )]
        for N in n_events:
            self.assertGreaterEqual( N, self.n_min )
            
    def test_n_events_reduced_N(self):
        n_events = [self.h2_rebinned.GetBinContent( i, i ) for i in range( 1, len( self.bin_edges_2 ) )]
        for N in n_events:
            self.assertGreaterEqual( N, self.n_min )
             
    def test_n_events_reduced_spread(self):
        n_events = [self.h3_rebinned.GetBinContent( i, i ) for i in range( 1, len( self.bin_edges_3 ) )]
        for N in n_events:
            self.assertGreaterEqual( N, self.n_min )
            
    def test_n_events_combined_1_2(self):
        n_events = [self.h1_2_rebinned.GetBinContent( i, i ) for i in range( 1, len( self.bin_edges_1_2 ) )]
        for N in n_events:
            self.assertGreaterEqual( N, self.n_min )
    
    def test_n_events_combined_1_3(self):
        n_events = [self.h1_3_rebinned.GetBinContent( i, i ) for i in range( 1, len( self.bin_edges_1_3 ))]
        for N in n_events:
            self.assertGreaterEqual( N, self.n_min )
        
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testTemplates']
    unittest.main()
