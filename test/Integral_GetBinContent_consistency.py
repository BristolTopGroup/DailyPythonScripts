from __future__ import division
import unittest
from rootpy.plotting import Hist2D
from tools.Calculation import calculate_purities, calculate_stabilities
import importlib
from tools.hist_utilities import rebin_2d, fix_overflow

pick_bins = importlib.import_module( "src.cross_section_measurement.00_pick_bins" )

import numpy as np

class Test( unittest.TestCase ):


    def setUp( self ):
    	# create histograms
        # self.h1 = Hist2D( 15, 0, 15, 15, 0, 15 )
        # x_1 = [1, 3, 7, 7, 8, 1, 12, 7, 8, 6]
        # y_1 = [1, 7, 3, 7, 8, 12, 7, 12, 13, 11]
        self.h1 = Hist2D( 60, 40, 100, 60, 40, 100 )
        n_1 = 100000
        x_1 = 60 + 10 * np.random.randn( n_1 )
        y_1 = x_1 + np.random.randn( n_1 )
        z_1 = np.vstack( ( x_1, y_1 ) ).T
        self.h1.fill_array( z_1 )

        self.h1 = fix_overflow( self.h1 )

        self.histogram_information = [
                {'hist': self.h1,
                 'CoM': 7,
                 'channel':'test_1'},
                ]

        self.histograms = [info['hist'] for info in self.histogram_information]
        
        # requirements for new binning
        self.p_min, self.s_min, self.n_min = 0.5, 0.5, 1000

        self.bin_edges = []
        self.purities_GetBinContent = []
        self.stabilities_GetBinContent = []
        self.n_events_GetBinContent = []

        self.purities_Integral = []
        self.stabilities_Integral = []
        self.n_events_Integral = []

        first_hist = self.histograms[0]
        n_bins = first_hist.GetNbinsX()

        current_bin_start = 0
        current_bin_end = 0

        while current_bin_end < n_bins:
            current_bin_end, p, s, n_gen_and_reco = pick_bins.get_next_end( self.histograms, current_bin_start, current_bin_end, self.p_min, self.s_min, self.n_min )
            if not self.bin_edges:
                # if empty
                self.bin_edges.append( first_hist.GetXaxis().GetBinLowEdge( current_bin_start + 1 ) )
            self.bin_edges.append( first_hist.GetXaxis().GetBinLowEdge( current_bin_end ) + first_hist.GetXaxis().GetBinWidth( current_bin_end ) )
            self.purities_Integral.append(p)
            self.stabilities_Integral.append(s)
            self.n_events_Integral.append(n_gen_and_reco)
            current_bin_start = current_bin_end

        self.h1_rebinned = rebin_2d(self.h1, self.bin_edges, self.bin_edges)

        self.purities_GetBinContent = calculate_purities( self.h1_rebinned )
        self.stabilities_GetBinContent = calculate_stabilities( self.h1_rebinned )
        self.n_events_GetBinContent = [int( self.h1_rebinned.GetBinContent( i, i ) ) for i in range( 1, len( self.bin_edges ) )]

    def tearDown( self ):
        pass

    def test_number_of_bins_equivalence( self ):
    	self.assertEqual( len(self.n_events_GetBinContent), len(self.n_events_Integral) )
    	self.assertEqual( len(self.purities_GetBinContent), len(self.purities_Integral) )
    	self.assertEqual( len(self.stabilities_GetBinContent), len(self.stabilities_Integral) )
        pass

    def test_number_of_events( self ):
    	for i, n in enumerate(self.n_events_GetBinContent):
    		self.assertEqual( n, self.n_events_Integral[i] )
    	pass
    
    def test_purities_equivalence( self ):
        for i, p in enumerate(self.purities_GetBinContent):
            self.assertEqual( p, self.purities_Integral[i], msg = 'Calculated with Integral method purity ' + str(self.purities_Integral[i]) + ' is not equal to GetBinContent one ' + str(p) + ' in bin ' + str(i+1) )
        pass

    def test_stabilities_equivalence( self ):
        for i, s in enumerate(self.stabilities_GetBinContent):
            self.assertEqual( s, self.stabilities_Integral[i], msg = 'Calculated with Integral method stability ' + str(self.stabilities_Integral[i]) + ' is not equal to GetBinContent one ' + str(s) + ' in bin ' + str(i+1) )
        pass

if __name__ == "__main__":
    unittest.main()
