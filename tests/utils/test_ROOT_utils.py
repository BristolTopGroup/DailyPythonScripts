import unittest

import dps.utils.ROOT_utils as ru
from ..data import create_test_tree



class Test(unittest.TestCase):

    def setUp(self):
        create_test_tree('test.root')

    def tearDown(self):
        pass

    def test_get_histogram_from_tree(self):
        hist = ru.get_histogram_from_tree(
                                       tree = 'test',
                                       branch = 'x',
                                       weight_branches = ['z'],
                                       selection_branches = ['i'],
                                       input_file = 'test.root',
                                       n_bins = 10,
                                       x_min = -1,
                                       x_max = 1,
                                       selection = ' 10 < i < 1000',
                                       )
        self.assertEqual(hist.nbins(), 10)
#         from rootpy.interactive.rootwait import wait
#         hist.Draw()
#         wait()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
