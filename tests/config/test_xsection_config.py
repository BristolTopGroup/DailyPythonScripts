'''
Created on 14 May 2014

@author: kreczko
'''
import unittest
from dps.config.xsection import XSectionConfig
from __builtin__ import getattr


class Test(unittest.TestCase):

    def setUp(self):
#         self.config_7TeV = XSectionConfig(centre_of_mass_energy=7)
#         self.config_8TeV = XSectionConfig(centre_of_mass_energy=8)
        self.config_13TeV = XSectionConfig(centre_of_mass_energy=13)

    def test_current_analysis_path(self):
        self.assertTrue(XSectionConfig.current_analysis_path.endswith('/'))

    def test_paths(self):
        self.assertTrue(XSectionConfig.current_analysis_path.endswith('/'))
#         self.assertTrue(self.config_7TeV.path_to_files.endswith('/'))
#         self.assertTrue(
#             self.config_7TeV.path_to_unfolding_histograms.endswith('/'))
#         self.assertTrue(self.config_8TeV.path_to_files.endswith('/'))

#         self.assertTrue('7TeV' in self.config_7TeV.path_to_files)
#         self.assertTrue('8TeV' in self.config_8TeV.path_to_files)
        self.assertTrue('13TeV' in self.config_13TeV.path_to_files)

        unfolding_files = ['unfolding_powheg_pythia_raw', 'unfolding_powheg_herwig_raw',
                           'unfolding_mcatnlo_raw', 'unfolding_scale_down_raw',
                           'unfolding_scale_up_raw', 'unfolding_matching_down_raw',
                           'unfolding_matching_up_raw', ]
#         for u_file in unfolding_files:
#             full_path = getattr(self.config_7TeV, u_file)
#             self.assertEqual(full_path.count('7TeV'), 2)
#             full_path = getattr(self.config_8TeV, u_file)
#             self.assertEqual(full_path.count('8TeV'), 2)

    def test_invalid_centre_of_mass_energy(self):
        self.assertRaises(AttributeError, XSectionConfig, (1232))

#     def test_luminosity(self):
#         self.assertEqual(self.config_7TeV.luminosity, 5050)
#         self.assertEqual(self.config_8TeV.luminosity, 19584)
#         self.assertEqual(self.config_8TeV.luminosity, 19584)

    def test_parameters(self):
        for param in XSectionConfig.parameters:
            self.assertTrue(
                hasattr(self.config_13TeV, param), 'Parameter ' + param + ' not found.')


if __name__ == "__main__":
    unittest.main()
