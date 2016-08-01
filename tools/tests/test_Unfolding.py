'''
Created on 15 May 2014

@author: senkin
'''
from __future__ import division
import unittest
from rootpy.io import File
from tools.Unfolding import Unfolding, get_unfold_histogram_tuple
from tools.hist_utilities import hist_to_value_error_tuplelist, value_error_tuplelist_to_hist
from tools.ROOT_utils import set_root_defaults
from config.variable_binning import bin_edges

class Test( unittest.TestCase ):

    def setUp( self ):
        # load histograms
        self.input_file = File('tests/data/unfolding_merged_asymmetric.root')
        self.k_value = 3
        self.unfold_method = 'TUnfold'
        self.met_type = 'patType1CorrectedPFMet'
        self.variables = ['MET', 'WPT', 'MT' , 'ST', 'HT']
        self.channels = ['electron', 'muon', 'combined']
        self.dict = {}
        for channel in self.channels:
            self.dict[channel] = {}
            for variable in self.variables:
                self.dict[variable] = {}
                h_truth, h_measured, h_response, _ = get_unfold_histogram_tuple(
                                                            inputfile = self.input_file,
                                                            variable = variable,
                                                            channel = channel,
                                                            met_type = self.met_type)

                unfolding_object = Unfolding( h_truth,
                                       h_measured,
                                       h_response,
                                       k_value = self.k_value,
                                       method = self.unfold_method
                                       )
                
                tau_unfolding_object = Unfolding( h_truth,
                                                  h_measured,
                                                  h_response,
                                                  tau=100,
                                                  k_value= -1,
                                                  method='TUnfold')

                self.dict[channel][variable] = {'h_truth' : h_truth,
                                                'h_measured' : h_measured,
                                                'h_response' : h_response,
                                                'unfolding_object' : unfolding_object,
                                                'tau_unfolding_object': tau_unfolding_object,
                                                }

    def tearDown( self ):
        pass

#     def test_closure( self ):
#         for channel in self.channels:
#             for variable in self.variables:
#                 # closure test
#                 unfolded_result = hist_to_value_error_tuplelist( self.dict[channel][variable]['unfolding_object'].closureTest() )
#                 truth = hist_to_value_error_tuplelist( self.dict[channel][variable]['h_truth'] )
#                 # the difference between the truth and unfolded result should be within the unfolding error
#                 for (value, error), (true_value, _) in zip(unfolded_result, truth):
#                     self.assertAlmostEquals(value, true_value, delta = error)
 
    def test_invalid_zero_data( self ):
        variable = 'MET'
        channel = 'electron'
        pseudo_data = value_error_tuplelist_to_hist( [(0,0)]*( len( bin_edges[variable] ) - 1 ), bin_edges[variable] )
        self.assertRaises(ValueError,  self.dict[channel][variable]['unfolding_object'].unfold, (pseudo_data))
        
    def test_tau_closure(self):
        for channel in self.channels:
            for variable in self.variables:
                data = self.dict[channel][variable]['h_measured']
                truth = hist_to_value_error_tuplelist( self.dict[channel][variable]['h_truth'] )
                unfolded_result = hist_to_value_error_tuplelist(self.dict[channel][variable]['tau_unfolding_object'].unfold(data))
                # the difference between the truth and unfolded result should be within the unfolding error
                for (value, error), (true_value, _) in zip(unfolded_result, truth):
                    self.assertAlmostEquals(value, true_value, delta = error)
#                     print value, '+-', error, '   true:', true_value

    def test_k_to_tau(self):
        data = self.dict['electron']['MET']['h_measured']
        tau_unfolding_object = self.dict['electron']['MET']['tau_unfolding_object']
        # first we need to unfold to get the matrix
        tau_unfolding_object.unfold(data)
        # next we need to get the actual RooUnfold object
        tau = tau_unfolding_object.Impl().kToTau(self.k_value)
        self.assertAlmostEqual(tau, 19., delta = 1)

if __name__ == "__main__":
    set_root_defaults()
    unittest.main()
