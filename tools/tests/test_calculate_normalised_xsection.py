'''
Created on 12 Nov 2014

@author: kreczko
'''
from __future__ import division
import unittest
from tools.Calculation import calculate_normalised_xsection
from uncertainties import ufloat

class Test( unittest.TestCase ):


    def setUp( self ):
        self.n_events = [1, 2, 3]
        self.n_events_errors = [1, 1, 1]
        self.u_n_events = [ufloat( 1, 1 ), ufloat( 2, 1 ), ufloat( 3, 1 )]
        self.n_total = sum( self.n_events )
        self.inputs = zip( self.n_events, self.n_events_errors ) 
        self.bin_widths = [2, 5, 7]
        self.results = calculate_normalised_xsection( self.inputs,
                                               self.bin_widths )


    def tearDown( self ):
        pass

    def testLength( self ):
        self.assertEqual( len( self.results ), len( self.n_events ) )

    def testValues( self ):
        for i in range( len( self.n_events ) ):
            n_i = self.n_events[i]
            N = self.n_total
            w_i = self.bin_widths[i]
            value = self.results[i][0]
            xsection_i = float( n_i ) / w_i / N
            self.assertEqual( value, xsection_i )
            
    def testErrorWithCorrelation( self ):
        '''
        This test makes sure that the correlation between N_i and N_total is
        considered for the error of the x-section calculation
        '''
        N = sum( self.u_n_events )
        
        for i in range ( len ( self.n_events_errors ) ):
            n_i = self.u_n_events[i]
            w_i = self.bin_widths[i]
            xsection_i = 1 / w_i * n_i / N
            error = self.results[i][1]
            self.assertAlmostEqual( error, xsection_i.std_dev, 10 )

if __name__ == "__main__":
    unittest.main()
