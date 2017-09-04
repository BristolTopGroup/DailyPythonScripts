'''
    This module creates the bottom line tests for each variable & 
    channel (electron, muon, combined). 
'''
from rootpy.io import File

from dps.config.variable_binning import bin_edges_vis, bin_widths_visiblePS, reco_bin_edges_vis
from dps.utils.Unfolding import Unfolding, get_unfold_histogram_tuple, removeFakes
from dps.utils.hist_utilities import hist_to_value_error_tuplelist, value_error_tuplelist_to_hist, values_and_errors_to_hist, hist2d_to_binEdges_list, hist_to_value_list, matrix_to_hist2d
from dps.utils.Calculation import calculate_normalised_xsection
from dps.config.xsection import XSectionConfig
# from dps.utils.plotting import Histogram_properties
from dps.config import latex_labels
from rootpy import asrootpy
from root_numpy import hist2array
from collections import OrderedDict
from dps.utils.latex import setup_matplotlib
from dps.utils.pandas_utilities import file_to_df, read_tuple_from_file, dict_to_df, matrix_from_df
import matplotlib.pyplot as plt
from ROOT import TMath

import numpy as np
np.set_printoptions(
	precision = 3,
	linewidth = 400,
)

class UnfoldingTest(object):
    '''
        Class for storing input configuration, and for getting and storing response matrix histograms
    '''    
    def __init__( self, opts ):
    	# Response Matrices
		t, m, r, f = get_unfold_histogram_tuple(
		    inputfile=opts['file_for_response'],
		    variable=opts['variable'],
		    channel=opts['channel'],
		    centre_of_mass=opts['config'].centre_of_mass_energy,
		    ttbar_xsection=opts['config'].ttbar_xsection,
		    luminosity=opts['config'].luminosity,
		    load_fakes=True,
		    visiblePS=True,
		)
		self.h_truth = asrootpy ( t )
		self.h_response = asrootpy ( r )
		self.h_measured = asrootpy ( m )
		self.h_fakes = asrootpy ( f )
		self.h_data_smeared = None
		self.h_mc_smeared = None
		self.h_data_smeared_no_fakes = None
		self.h_data_particleLevel = None
		self.h_mc_particleLevel = self.h_truth
		self.h_refolded_smeared = None
		# self.h_truthInverse = asrootpy ( it )
		# self.h_responseInverse = invertResponse(ir)


		# print np.matrix( hist2array( self.h_response )).shape()
		# print np.matrix( hist2array( self.h_responseInverse )).shape()

		# self.h_responseInverse = asrootpy ( ir )
		# self.h_measuredInverse = asrootpy ( im )
		# self.h_fakes = asrootpy ( f )



		# print "Truth"
		# print np.array(list(self.h_truth.y()))
		# print "Measured"
		# print np.array(list(self.h_measured.y()))
		# print "Inverted Truth"
		# print np.array(list(self.h_truthInverse.y()))
		# print "Inverted Measured"
		# print np.array(list(self.h_measuredInverse.y()))

    	# Tau Values
		tau_value = None
		if 'electron' in opts['channel']:
			tau_value = opts['config'].tau_values_electron[opts['variable']]
		elif 'muon' in opts['channel']:
			tau_value = opts['config'].tau_values_muon[opts['variable']]
		else:
			print 'Running bizarre channel (or combined)'
		self.tau = tau_value

    def get_histograms( self ):
        return self.h_data, self.h_truth, self.h_measured, self.h_response, self.h_responseInverse, self.h_fakes

def calculateChi2(data,model,covariance):
	diff = (data - model)
	chi2 = np.transpose( diff ).dot( np.linalg.inv( covariance ) ).dot( diff )
	ndf = len(data)
	prob = TMath.Prob( chi2, ndf )
	return chi2, ndf, prob 


def main():
	'''
	'''
	config = XSectionConfig(13)

	file_for_smeared_space_template = 'data/normalisation/background_subtraction/13TeV/{var}/VisiblePS/central/normalisation_{ch}.txt'
	file_for_smeared_covariance_template = 'data/normalisation/background_subtraction/13TeV/{var}/VisiblePS/central/covarianceMatrices/unfoldedNumberOfEvents/Stat_unfoldedNormalisation_Covariance_{ch}.txt'
	file_for_unfolded_space_template = 'data/normalisation/background_subtraction/13TeV/{var}/VisiblePS/central/unfolded_normalisation_{ch}_TUnfold.txt'
	file_for_unfolded_stat_covariance_template = 'data/normalisation/background_subtraction/13TeV/{var}/VisiblePS/central/covarianceMatrices/unfoldedNumberOfEvents/Stat_unfoldedNormalisation_Covariance_{ch}.txt'
	file_for_unfolded_mcstat_covariance_template = 'data/normalisation/background_subtraction/13TeV/{var}/VisiblePS/central/covarianceMatrices/unfoldedNumberOfEvents/Stat_inputMC_Covariance_{ch}.txt'

	file_for_response = File(config.unfolding_central, 'read')

	opts = {}
	opts['file_for_response'] = file_for_response
	opts['config'] 			  = config

	channel = [
		'electron',
		'muon',
	]
	for ch in channel:
		for var in config.variables:
			opts['variable'] 			= var
			opts['channel'] 			= ch
			# if 'electron' not in ch: continue 
			# if 'HT' not in var: continue
			print ""
			print "="*160
			print "Bottom Line Test for {} in the {} Channel".format(var,ch)
			print '- '*80
			print ""

			# File for unfolding
			file_for_smeared_space = file_for_smeared_space_template.format( var = var, ch = ch )
			edges = reco_bin_edges_vis[var]
			ut = UnfoldingTest(opts)

			# Get raw Data and TTBar MC 
			smeared_space = read_tuple_from_file(file_for_smeared_space)
			smeared_data = smeared_space['TTJet']
			smeared_mc = smeared_space['TTJet_MC']

			# Histofy them and remove Fakes
			ut.h_data_smeared = value_error_tuplelist_to_hist( smeared_data, edges )
			ut.h_mc_smeared = value_error_tuplelist_to_hist( smeared_mc, edges )
			ut.h_data_smeared_no_fakes = removeFakes( ut.h_measured, ut.h_fakes, ut.h_data_smeared )

			# Normalise response and unfold
			ut.h_response.Scale( ut.h_data_smeared_no_fakes.Integral() / ut.h_response.ProjectionX('px',1).Integral() )
			unfolding = Unfolding( ut.h_data_smeared_no_fakes, ut.h_truth, ut.h_measured, ut.h_response, ut.h_fakes, tau = ut.tau )
			ut.h_data_particleLevel = unfolding.unfold()

			# Particle level covariance matrices, data and mc ==> chi2
			unfolded_statCov, _, unfolded_mcStatCov = unfolding.get_covariance_matrix()
			unfolded_covariance = unfolded_statCov + unfolded_mcStatCov
			unfolded_data = np.array(hist_to_value_list(ut.h_data_particleLevel))
			unfolded_mc = np.array(hist_to_value_list(ut.h_mc_particleLevel))
			unfolded_chi, unfolded_ndf, unfolded_pvalue = calculateChi2(unfolded_data, unfolded_mc, unfolded_covariance)

			print unfolded_data
			print unfolded_mc
			print unfolded_covariance
			print ""
			print 'Unfolded Level Chi2 : {}'.format(unfolded_chi)
			print '-'*160

			# Get smeared data and rebin
			ut.h_refolded_smeared = unfolding.refold()
			ut.h_refolded_smeared = ut.h_refolded_smeared.rebinned(2)
			ut.h_mc_smeared = ut.h_mc_smeared.rebinned(2)

			# Reconstructed level covariance matrices, data and mc ==> chi2
			smeared_covariance = np.matrix(np.diag( [e**2 for (v,e) in hist_to_value_error_tuplelist(ut.h_refolded_smeared)] ) )
			smeared_data = np.array(hist_to_value_list(ut.h_refolded_smeared))
			smeared_mc = np.array(hist_to_value_list(ut.h_mc_smeared))
			smeared_chi, smeared_ndf, smeared_pvalue = calculateChi2(smeared_data, smeared_mc, smeared_covariance)

			print np.array(hist_to_value_list(ut.h_data_smeared_no_fakes.rebinned(2)))
			print smeared_data
			print smeared_mc
			print smeared_covariance
			print ""
			print 'Smeared Level Chi2 : {}'.format(smeared_chi)
			print "="*160




			# Unfolded Level Data: Y (unfolded)
			# Unfolded Level MC: Y (truth from response)
			# Unfolded Covariance: Data Stat + MC Stat Y
			# Smeared Level Data: Y (Unfolded/Refolded Data)
			# Smeared Level MC: N ()
			# Smeared Covariance: Just diagonal unc on refolded? data



			# file_for_smeared_space = file_for_smeared_space_template.format( var = var, ch = ch )
			# file_for_smeared_covariance = file_for_smeared_covariance_template.format( var = var, ch = ch )

			# smeared_space = file_to_df(file_for_smeared_space)
			# smeared_covariance = matrix_from_df(file_to_df(file_for_smeared_covariance))

			# smeared_data = smeared_space['TTJet']
			# smeared_mc = smeared_space['TTJet_MC']
			# smeared_data = np.array( [ smeared_data[i]+smeared_data[i+1] for i in range(0, len(smeared_data), 2)] )
			# smeared_mc = np.array([smeared_mc[i]+smeared_mc[i+1] for i in range(0, len(smeared_mc), 2)] )
			# print '-'*160
			# print 'Data : '
			# print smeared_data
			# print '-'*160
			# print 'Smeared MC : '
			# print smeared_mc
			# print '-'*160
			# print 'Statistical Covariance : '
			# print smeared_covariance
			# s_chi, s_ndf, s_pvalue = calculateChi2(smeared_data, smeared_mc, smeared_covariance)
			# print '-'*160
			# print 'Smeared Level Chi2 : '
			# print s_chi
			# print '-'*160

			# print ''

			# file_for_unfolded_space = file_for_unfolded_space_template.format( var = var, ch = ch )
			# file_for_unfolded_covariance = file_for_unfolded_covariance_template.format( var = var, ch = ch )
			# unfolded_space = file_to_df(file_for_unfolded_space)
			# unfolded_covariance = matrix_from_df(file_to_df(file_for_unfolded_covariance))
			# unfolded_data = np.array(unfolded_space['TTJets_unfolded'])
			# unfolded_mc = np.array(unfolded_space['TTJets_powhegPythia8'])
			# print '-'*160
			# print 'Unfolded Data : '
			# print unfolded_data
			# print '-'*160
			# print 'Particle Level MC : '
			# print unfolded_mc
			# print '-'*160
			# print 'Some Matrix as Yet Unknown : '
			# print unfolded_covariance
			# u_chi, u_ndf, u_pvalue = calculateChi2(unfolded_data, unfolded_mc, unfolded_covariance)
			# print '-'*160
			# print 'Unfolded Level Chi2 : '
			# print u_chi
			# print '-'*160




if __name__ == '__main__':
	main()
			