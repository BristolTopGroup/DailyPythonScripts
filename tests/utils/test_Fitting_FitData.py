'''
Created on 31 Oct 2012

@author: kreczko
'''
import unittest
from dps.utils.Fitting import FitData, FitDataCollection
from rootpy.plotting import Hist

import numpy as np
from dps.utils.hist_utilities import adjust_overflow_to_limit
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

x_min = 40
x_max = 200

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
        
        h_data_1.Scale(data_scale)
        h_data_2.Scale(data_scale)
        
        self.histograms_1 = {'signal': h_signal_1,
                             'bkg1': h_bkg1_1}
        
        self.histograms_2 = {'signal': h_signal_2,
                             'bkg1': h_bkg1_2}
        
        self.histograms_3 = {'var1': h_signal_1,
                             'bkg1': h_bkg1_1}
        
        self.fit_data_1 = FitData( h_data_1, self.histograms_1, fit_boundaries = ( x_min, x_max ))
        self.fit_data_2 = FitData( h_data_2, self.histograms_2, fit_boundaries = ( x_min, x_max ))
        self.fit_data_3 = FitData( h_data_1, self.histograms_3, fit_boundaries = ( x_min, x_max ))

        self.collection_1 = FitDataCollection()
        self.collection_1.add( self.fit_data_1, 'signal region' )
        self.collection_1.add( self.fit_data_2, 'control region' )
        self.collection_1.set_normalisation_constraints({'bkg1': 0.5})
        
        self.collection_2 = FitDataCollection()
        self.collection_2.add( self.fit_data_1 )
        self.collection_2.add( self.fit_data_2 )
        self.collection_2.set_normalisation_constraints({'bkg1': 0.5})
        
        self.single_collection = FitDataCollection()
        self.single_collection.add( self.fit_data_1 )
        self.single_collection.set_normalisation_constraints({'bkg1': 0.5})
        
        self.non_simultaneous_fit_collection = FitDataCollection()
        self.non_simultaneous_fit_collection.add( self.fit_data_1 )
        self.non_simultaneous_fit_collection.add( self.fit_data_3 )
        
        self.h_data = h_data_1
        self.h_bkg1 = h_bkg1_1
        self.h_signal = h_signal_1
        
    def tearDown( self ):
        pass

    def test_is_valid_for_simultaneous_fit( self ):
        self.assertTrue( self.collection_1.is_valid_for_simultaneous_fit(), msg = 'has_same_n_samples: ' + str(self.collection_1.has_same_n_samples) + ', has_same_n_data: ' + str(self.collection_1.has_same_n_data) )
        self.assertTrue( self.collection_2.is_valid_for_simultaneous_fit(), msg = 'has_same_n_samples: ' + str(self.collection_1.has_same_n_samples) + ', has_same_n_data: ' + str(self.collection_1.has_same_n_data)  )
        self.assertFalse( self.non_simultaneous_fit_collection.is_valid_for_simultaneous_fit() )
        
    def test_samples( self ):
        samples = sorted( self.histograms_1.keys() )
        samples_from_fit_data = sorted( self.fit_data_1.samples )
        samples_from_fit_data_collection = self.collection_1.mc_samples()
        self.assertEqual( samples, samples_from_fit_data )
        self.assertEqual( samples, samples_from_fit_data_collection )
        
    def test_normalisation( self ):
        normalisation = {name:adjust_overflow_to_limit(histogram, x_min, x_max).Integral() for name, histogram in self.histograms_1.iteritems()}
        normalisation_from_fit_data = self.fit_data_1.normalisation
        normalisation_from_single_collection = self.single_collection.mc_normalisation()
        normalisation_from_collection = self.collection_1.mc_normalisation( 'signal region' )
        normalisation_from_collection_1 = self.collection_1.mc_normalisation()['signal region']
        for sample in normalisation.keys():
            self.assertEqual( normalisation[sample], normalisation_from_fit_data[sample] )
            self.assertEqual( normalisation[sample], normalisation_from_single_collection[sample] )
            self.assertEqual( normalisation[sample], normalisation_from_collection[sample] )
            self.assertEqual( normalisation[sample], normalisation_from_collection_1[sample] )
        
        # data normalisation
        normalisation = self.h_data.integral( overflow = True )
        normalisation_from_fit_data = self.fit_data_1.n_data()
        normalisation_from_single_collection = self.single_collection.n_data()
        normalisation_from_collection = self.collection_1.n_data( 'signal region' )
        normalisation_from_collection_1 = self.collection_1.n_data()['signal region']
        self.assertEqual( normalisation, normalisation_from_fit_data )
        self.assertEqual( normalisation, normalisation_from_single_collection )
        self.assertEqual( normalisation, normalisation_from_collection )
        self.assertEqual( normalisation, normalisation_from_collection_1 )
        
        self.assertAlmostEqual(normalisation, self.collection_1.max_n_data(), delta = 1 )
        
    def test_real_data( self ):
        real_data = self.fit_data_1.real_data_histogram()
        self.assertEqual( self.h_data.integral( overflow = True ), real_data.Integral() )
        
    def test_overwrite_warning( self ):
        c = FitDataCollection()
        c.add( self.fit_data_1, 'var1' )
        self.assertRaises( UserWarning, c.add, ( self.fit_data_1, 'var1' ) )
        
    def test_vectors( self ):
        h_signal = adjust_overflow_to_limit( self.h_signal, x_min, x_max )
        h_signal.Scale(1/h_signal.Integral())
        h_bkg1 = adjust_overflow_to_limit( self.h_bkg1, x_min, x_max )
        h_bkg1.Scale(1/h_bkg1.Integral())
        signal = list( h_signal.y() )
        bkg1 = list( h_bkg1.y() )
        
        v_from_fit_data = self.fit_data_1.vectors
        v_from_single_collection = self.single_collection.vectors()
#         v_from_collection = self.collection_1.vectors( 'signal region' )
#         v_from_collection_1 = self.collection_1.vectors()['signal region']
        self.assertEqual(signal, v_from_fit_data['signal'])
        self.assertEqual(bkg1, v_from_fit_data['bkg1'])
        
        self.assertEqual(signal, v_from_single_collection['signal'])
        self.assertEqual(bkg1, v_from_single_collection['bkg1'])
    
    def test_constraints(self):
        constraint_from_single_collection = self.single_collection.constraints()['bkg1']
        self.assertEqual(0.5, constraint_from_single_collection)
        
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testTemplates']
    unittest.main()
