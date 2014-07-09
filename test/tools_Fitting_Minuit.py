'''
Created on 31 Oct 2012

@author: kreczko
'''
import unittest
from tools.Fitting import Minuit, FitData, FitDataCollection
from rootpy.plotting import Hist
from math import sqrt

import numpy as np
N_bkg1 = 9000
N_signal = 1000
N_bkg1_obs = 10000
N_signal_obs = 2000
N_data = N_bkg1_obs + N_signal_obs
mu1, mu2, sigma1, sigma2 = 100, 140, 15, 5
x1 = mu1 + sigma1 * np.random.randn( N_bkg1 )
x2 = mu2 + sigma2 * np.random.randn( N_signal )
x1_obs = mu1 + sigma1 * np.random.randn( N_bkg1_obs )
x2_obs = mu2 + sigma2 * np.random.randn( N_signal_obs )

x3 = mu2 + sigma1 * np.random.randn( N_bkg1 )
x4 = mu1 + sigma2 * np.random.randn( N_signal )
x3_obs = mu2 + sigma1 * np.random.randn( N_bkg1_obs )
x4_obs = mu1 + sigma2 * np.random.randn( N_signal_obs )

data_scale = 1.2
N_data = N_data * data_scale

class Test( unittest.TestCase ):


    def setUp( self ):
        

        # create histograms
        h_bkg1_1 = Hist( 100, 40, 200, title = 'Background' )
        h_signal_1 = h_bkg1_1.Clone( title = 'Signal' )
        h_data_1 = h_bkg1_1.Clone( title = 'Data' )
        h_bkg1_2 = h_bkg1_1.Clone( title = 'Background' )
        h_signal_2 = h_bkg1_1.Clone( title = 'Signal' )
        h_data_2 = h_bkg1_1.Clone( title = 'Data' )
    
        # fill the histograms with our distributions
        map( h_bkg1_1.Fill, x1 )
        map( h_signal_1.Fill, x2 )
        map( h_data_1.Fill, x1_obs )
        map( h_data_1.Fill, x2_obs )
        
        map( h_bkg1_2.Fill, x3 )
        map( h_signal_2.Fill, x4 )
        map( h_data_2.Fill, x3_obs )
        map( h_data_2.Fill, x4_obs )
        
        h_data_1.Scale( data_scale )
        h_data_2.Scale( data_scale )
        
        histograms_1 = {'signal': h_signal_1,
                        'bkg1': h_bkg1_1}
        
        histograms_2 = {'signal': h_signal_2,
                        'bkg1': h_bkg1_2}
        
        fit_data_1 = FitData( h_data_1, histograms_1, fit_boundaries = ( 40, 200 ) )
        fit_data_2 = FitData( h_data_2, histograms_2, fit_boundaries = ( 40, 200 ) )
        
        single_fit_collection = FitDataCollection()
        single_fit_collection.add( fit_data_1 )
        
        collection_1 = FitDataCollection()
        collection_1.add( fit_data_1, 'var1' )
        collection_1.add( fit_data_2, 'var2' )
        
        collection_2 = FitDataCollection()
        collection_2.add( fit_data_1, 'var1' )
        collection_2.add( fit_data_2, 'var2' )
        collection_2.set_normalisation_constraints( {'bkg1':0.5} )
        
        collection_3 = FitDataCollection()
        collection_3.add( fit_data_1, 'var1' )
        collection_3.add( fit_data_2, 'var2' )
        collection_3.set_normalisation_constraints( {'bkg1':0.001} )
        
        self.minuit_fitter = Minuit( single_fit_collection )
        self.minuit_fitter.fit()
        
        self.simultaneous_fit = Minuit( collection_1 )
        self.simultaneous_fit.fit()
        
        
        self.simultaneous_fit_with_constraints = Minuit( collection_2 )
        self.simultaneous_fit_with_constraints.fit()
        
        self.simultaneous_fit_with_bad_constraints = Minuit( collection_3 )
        self.simultaneous_fit_with_bad_constraints.fit()


    def tearDown( self ):
        pass

    def test_normalisation( self ):
        normalisation = self.minuit_fitter.normalisation
        self.assertAlmostEqual( normalisation["data"], N_data, delta = sqrt( N_data ) )
        self.assertAlmostEqual( normalisation["bkg1"], N_bkg1, delta = sqrt( N_bkg1 ) )
        self.assertAlmostEqual( normalisation["signal"], N_signal, delta = sqrt( N_signal ) )
        
    def test_result( self ):
        results = self.minuit_fitter.readResults()
        self.assertAlmostEqual( N_signal_obs * data_scale, results['signal'][0], delta = 2 * results['signal'][1] )
        self.assertAlmostEqual( N_bkg1_obs * data_scale, results['bkg1'][0], delta = 2 * results['bkg1'][1] )
        
    def test_result_simultaneous( self ):
        results = self.simultaneous_fit.readResults()
        self.assertAlmostEqual( N_signal_obs * data_scale, results['signal'][0], delta = 2 * results['signal'][1] )
        self.assertAlmostEqual( N_bkg1_obs * data_scale, results['bkg1'][0], delta = 2 * results['bkg1'][1] )
        
    def test_result_simultaneous_with_constraints( self ):
        results = self.simultaneous_fit_with_constraints.readResults()
        self.assertAlmostEqual( N_signal_obs * data_scale, results['signal'][0], delta = 2 * results['signal'][1] )
        self.assertAlmostEqual( N_bkg1_obs * data_scale, results['bkg1'][0], delta = 2 * results['bkg1'][1] )
        
    def test_result_simultaneous_with_bad_constraints( self ):
        results = self.simultaneous_fit_with_bad_constraints.readResults()
        self.assertNotAlmostEqual( N_signal_obs * data_scale, results['signal'][0], delta = results['signal'][1] )
        self.assertNotAlmostEqual( N_bkg1_obs * data_scale, results['bkg1'][0], delta = results['bkg1'][1] )
        
    def test_relative_error( self ):
        results = self.minuit_fitter.readResults()
        self.assertLess( results['signal'][1] / results['signal'][0], 0.1 )
        self.assertLess( results['bkg1'][1] / results['bkg1'][0], 0.1 )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testTemplates']
    unittest.main()
