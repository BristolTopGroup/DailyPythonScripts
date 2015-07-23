'''
Created on 21 Jul 2015

@author: phxlk
'''
import unittest
from rootpy.io import File
from tests.data import create_test_tree, create_test_hist
import tools.input as ti


class Test(unittest.TestCase):

    def setUp(self):
        f = File('test.root', 'recreate')
        tree = create_test_tree()
        h = create_test_hist()
        h.write()
        tree.write()
        f.write()
        f.Close()

    def tearDown(self):
        pass

    def testValidityTreeInput(self):
        i = ti.Input(input_file='test.root',
                  tree='test',
                  branch='x',
                  selection='1',
                  weight_branch='1')
        self.assertTrue(i.isValid())

    def testValidityHistInput(self):
        i = ti.Input(input_file='test.root',
                  hist='test_hist',
                  )
        self.assertTrue(i.isValid())

    def testFailValidityTreeInput(self):
        i = ti.Input(input_file='doesnotexist.root',
                  tree='test',
                  branch='x',
                  selection='1',
                  weight_branch='1')
        self.assertFalse(i.isValid())

    def testFailValidityHistInput(self):
        i = ti.Input(input_file='test.root',
                  hist='doesnotexist',
                  )
        self.assertFalse(i.isValid())

    def testReadHist(self):
        i = ti.Input(input_file='test.root',
                  hist='test_hist',
                  )
        h = i.read()
        h_test = create_test_hist()
        self.assertEqual(h.nbins(), h_test.nbins())

    def testReadTree(self):
        i = ti.Input(input_file='test.root',
                  tree='test',
                  branch='x',
                  selection='1',
                  weight_branch='1',
                  n_bins=10,
                  x_min=0,
                  x_max=10,
                  )
        h = i.read()
        self.assertEqual(h.nbins(), 10)

    def testToDict1(self):
        i = ti.Input(input_file='test.root',
                  hist='test_hist',
                  )
        d = i.toDict()
        self.assertEqual(d, {'input_file': 'test.root', 'hist': 'test_hist'})

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
