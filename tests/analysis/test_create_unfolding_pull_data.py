'''
Created on 14 Jul 2015

@author: phxlk
'''
import unittest
from dps.analysis.unfolding_tests.create_unfolding_pull_data import create_run_matrix


class Test(unittest.TestCase):

    @unittest.skip('reported: https://github.com/BristolTopGroup/DailyPythonScripts/issues/332')
    def testRun_matrixSimple(self):
        m = create_run_matrix(10, 10)
        self.assertEqual(len(list(m)), 10 * 10)
        for mc, data in m:
            self.assertGreaterEqual(mc, 1)
            self.assertGreaterEqual(data, 1)
            self.assertLessEqual(mc, 10)
            self.assertLessEqual(data, 10)

    @unittest.skip('reported: https://github.com/BristolTopGroup/DailyPythonScripts/issues/332')
    def testRun_matrixWithOffset(self):
        m = list(create_run_matrix(10, 10))
        self.assertEqual(len(m), 10 * 10)
        for mc, data in m:
            self.assertGreaterEqual(mc, 5)
            self.assertGreaterEqual(data, 5)
            self.assertLessEqual(mc, 15)
            self.assertLessEqual(data, 15)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCreate_run_matrix']
    unittest.main()
