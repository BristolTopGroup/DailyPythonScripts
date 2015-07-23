'''
Created on 14 Jul 2015

@author: phxlk
'''
import unittest
import src.unfolding_tests.create_unfolding_pull_data as pull


class Test(unittest.TestCase):

    def testRun_matrixSimple(self):
        m = pull.create_run_matrix(10, 10, 0, 0)
        self.assertEqual(len(list(m)), 10 * 10)
        for mc, data in m:
            self.assertGreaterEqual(mc, 1)
            self.assertGreaterEqual(data, 1)
            self.assertLessEqual(mc, 10)
            self.assertLessEqual(data, 10)

    def testRun_matrixWithOffset(self):
        m = list(pull.create_run_matrix(10, 10, 5, 5))
        self.assertEqual(len(m), 10 * 10)
        for mc, data in m:
            self.assertGreaterEqual(mc, 5)
            self.assertGreaterEqual(data, 5)
            self.assertLessEqual(mc, 15)
            self.assertLessEqual(data, 15)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCreate_run_matrix']
    unittest.main()
