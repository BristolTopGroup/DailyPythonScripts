'''
Created on 21 Jul 2015

@author: phxlk
'''
import unittest
from rootpy.tree import Tree
from .data import create_test_hist
from rootpy.io.file import File
from random import gauss

class Test(unittest.TestCase):


    def setUp(self):
        with File.open ('test.root', 'recreate') as f:
            f.mkdir('TTbar_plus_X_analysis/EPlusJets/Ref selection', recurse=True)
            f.cd('TTbar_plus_X_analysis/EPlusJets/Ref selection')
            tree = Tree("test")
            tree.create_branches(
                {'x': 'F',
                 'y': 'F',
                 'z': 'F',
                 'i': 'I',
                 'EventWeight': "F"})
            for i in xrange(10000):
                tree.x = gauss(.5, 1.)
                tree.y = gauss(.3, 2.)
                tree.z = gauss(13., 42.)
                tree.i = i
                tree.EventWeight = 1.
                tree.fill()
            f.write()
            h = create_test_hist()
            h.write()
            tree.write()
            f.write()
            f.Close()


    def tearDown(self):
        pass


    def testDirectoryWithSpace(self):
        '''
            Reported and fixed:
            https://github.com/rootpy/rootpy/issues/663
        '''
        with File.open('test.root') as f:
            self.assertTrue(f.__contains__('TTbar_plus_X_analysis/EPlusJets/Ref selection'))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    import nose2
    nose2.main()