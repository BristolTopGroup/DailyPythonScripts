'''
Created on 21 Jul 2015

@author: phxlk
'''
import unittest
from tests.data import create_test_hist, create_test_tree
from rootpy.io.file import File

class Test(unittest.TestCase):


    def setUp(self):
        f = File('test.root', 'recreate')
        f.mkdir('TTbar_plus_X_analysis/EPlusJets/Ref selection', recurse=True)
        f.cd('TTbar_plus_X_analysis/EPlusJets/Ref selection')
        tree = create_test_tree()
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