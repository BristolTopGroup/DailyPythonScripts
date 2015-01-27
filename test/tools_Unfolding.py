'''
Created on 15 May 2014

@author: senkin
'''
from __future__ import division
import unittest
import importlib
from rootpy.io import File
from tools.Unfolding import Unfolding, get_unfold_histogram_tuple
from tools.hist_utilities import hist_to_value_error_tuplelist, value_error_tuplelist_to_hist
from tools.ROOT_utils import set_root_defaults
from tools.file_utilities import read_data_from_JSON
from config.variable_binning import bin_edges

class Test( unittest.TestCase ):

    def setUp( self ):
        # load histograms
        self.input_file = File('test/data/unfolding_merged_asymmetric.root')
        self.k_value = 3
        self.unfold_method = 'RooUnfoldSvd'
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

                self.dict[channel][variable] = {'h_truth' : h_truth,
                                                'h_measured' : h_measured,
                                                'h_response' : h_response,
                                                'unfolding_object' : unfolding_object
                                                }

    def tearDown( self ):
        pass

    def test_closure( self ):
        for channel in self.channels:
            for variable in self.variables:
                # closure test
                unfolded_result = hist_to_value_error_tuplelist( self.dict[channel][variable]['unfolding_object'].closureTest() )
                truth = hist_to_value_error_tuplelist( self.dict[channel][variable]['h_truth'] )
                # the difference between the truth and unfolded result should be within the unfolding error
                for (value, error), (true_value, _) in zip(unfolded_result, truth):
                    self.assertAlmostEquals(value, true_value, delta = error)

    def test_invalid_zero_data( self ):
        variable = 'MET'
        channel = 'electron'
        pseudo_data = value_error_tuplelist_to_hist( [(0,0)]*( len( bin_edges[variable] ) - 1 ), bin_edges[variable] )
        self.assertRaises(ValueError,  self.dict[channel][variable]['unfolding_object'].unfold, (pseudo_data))

if __name__ == "__main__":
    set_root_defaults()
    unittest.main()
