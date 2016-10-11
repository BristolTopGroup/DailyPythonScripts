'''
Created on 31 Oct 2012

@author: kreczko
'''
import unittest
from rootpy.plotting import Hist, Hist2D
from dps.utils.hist_utilities import fix_overflow

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


class Test( unittest.TestCase ):


    def setUp( self ):
        

        # create histograms
        self.h1 = Hist( 60, 40, 100, title = '1D' )
        self.h2 = Hist2D( 60, 40, 100, 100, 40, 140 )
    
        # fill the histograms with our distributions
        map( self.h1.Fill, x1 )
        self.h2.fill_array( np.random.multivariate_normal( 
                                    mean = ( 100, 140 ),
                                    cov = np.arange( 4 ).reshape( 2, 2 ),
                                    size = ( int( 1E6 ), ) ) 
                        )
#         map(h2.Fill, (x1, x2, 1))
        

    def tearDown( self ):
        pass

    def test_overflow_1D( self ):
        last_bin = self.h1.nbins()
        overflow_bin = last_bin + 1
        overflow = self.h1.GetBinContent( overflow_bin )
        last_bin_content = self.h1.GetBinContent( last_bin )
        
        self.assertGreater( overflow, 0, '1D hist: No overflow present, wrong setup.' )
        h1 = fix_overflow( self.h1 )
        
        self.assertEqual( h1.GetBinContent( overflow_bin ), 0., '1D hist: Overflow bin is not 0.' )
        self.assertEqual( h1.GetBinContent( last_bin ), last_bin_content + overflow, '1D hist: last bin is not correct.' )
        
    def test_overflow_2D( self ):
        before_fix = check_overflow_in_2DHist(self.h2)
        has_overflow_in_x = before_fix['has_overflow_in_x']
        has_overflow_in_y = before_fix['has_overflow_in_y']
                
        self.assertGreater(has_overflow_in_x, 0, '2D hist: No overflow in x present, wrong setup.')
        self.assertGreater(has_overflow_in_y, 0, '2D hist: No overflow in y present, wrong setup.')
        
        h2 = fix_overflow( self.h2 )
        
        after_fix = check_overflow_in_2DHist(h2)
        has_overflow_in_x = after_fix['has_overflow_in_x']
        has_overflow_in_y = after_fix['has_overflow_in_y']
        # check if overflow has been reset
        self.assertEqual( has_overflow_in_x, 0, '2D hist: Overflow in x is not 0.' )
        self.assertEqual( has_overflow_in_y, 0, '2D hist: Overflow in y is not 0.' )
        # now check if new last bin content is equal to the old one plus overflow
        overflow_x_before = before_fix['overflow_x']
        overflow_y_before = before_fix['overflow_y']
        last_bin_content_x_before = before_fix['last_bin_content_x']
        last_bin_content_y_before = before_fix['last_bin_content_y']
        last_bin_content_x_after = after_fix['last_bin_content_x']
        last_bin_content_y_after = after_fix['last_bin_content_y']
        check_last_bin_content_x = [overflow + last_bin_content for overflow,last_bin_content in zip(overflow_x_before, last_bin_content_x_before)]
        check_last_bin_content_y = [overflow + last_bin_content for overflow,last_bin_content in zip(overflow_y_before, last_bin_content_y_before)]
        # remember, the last item in each list is actually the overflow, which should be 0 and the above calculation is not correct.
        self.assertTrue(check_equal_lists(check_last_bin_content_x[:-2], last_bin_content_x_after[:-2]), '2D hist: last bins in x are not correct.')
        self.assertTrue(check_equal_lists(check_last_bin_content_y[:-2], last_bin_content_y_after[:-2]), '2D hist: last bins in y are not correct.')
    
def check_overflow_in_2DHist(hist):
    last_bin_x = hist.nbins()
    overflow_bin_x = last_bin_x + 1
    last_bin_y = hist.nbins(axis=1)
    overflow_bin_y = last_bin_y + 1
    
    has_overflow_in_x = 0
    has_overflow_in_y = 0
    overflow_x = []
    overflow_y = []
    last_bin_content_x = []
    last_bin_content_y = []
    # first check the y overflows
    # range(start, end) returns (start ... end -1)
    for x in range(1, overflow_bin_x + 1):
        overflow = hist.GetBinContent(x, overflow_bin_y)
        if overflow > 0:
            has_overflow_in_y += 1
        overflow_y.append(overflow)
        last_bin_content_y.append(hist.GetBinContent(x, last_bin_y))
        
    for y in range(1, overflow_bin_y + 1):
        overflow = hist.GetBinContent(overflow_bin_x, y)
        overflow_x.append(overflow)
        last_bin_content_x.append(hist.GetBinContent(last_bin_x, y))
        if overflow > 0:
            has_overflow_in_x += 1
            
    result = {
              'has_overflow_in_x':has_overflow_in_x,
              'has_overflow_in_y':has_overflow_in_y,
              'overflow_x': overflow_x,
              'overflow_y': overflow_y,
              'last_bin_content_x': last_bin_content_x,
              'last_bin_content_y': last_bin_content_y,
              }
    return result

def check_equal_lists(list1, list2):
    return len(list1) == len(list2) and sorted(list1) == sorted(list2)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testTemplates']
    import nose2
    nose2.main()
