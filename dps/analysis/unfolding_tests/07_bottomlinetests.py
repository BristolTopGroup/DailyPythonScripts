'''
    This module creates the bottom line tests for each variable & 
    channel (electron, muon, combined). 
'''
from rootpy.io import File

from dps.config.variable_binning import bin_edges_vis, bin_widths_visiblePS, reco_bin_edges_vis
from dps.utils.Unfolding import Unfolding, get_unfold_histogram_tuple
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
		t, m, r, _ = get_unfold_histogram_tuple(
		    inputfile=opts['file_for_response'],
		    variable=opts['variable'],
		    channel=opts['channel'],
		    centre_of_mass=opts['config'].centre_of_mass_energy,
		    ttbar_xsection=opts['config'].ttbar_xsection,
		    luminosity=opts['config'].luminosity,
		    load_fakes=False,
		    visiblePS=True,
		)
		# it, im, ir, _ = get_unfold_histogram_tuple(
		#     inputfile=opts['file_for_responseInverse'],
		#     variable=opts['variable'],
		#     channel=opts['channel'],
		#     centre_of_mass=opts['config'].centre_of_mass_energy,
		#     ttbar_xsection=opts['config'].ttbar_xsection,
		#     luminosity=opts['config'].luminosity,
		#     load_fakes=False,
		#     visiblePS=True,
		# )
		self.h_truth = asrootpy ( t )
		self.h_response = asrootpy ( r )
		self.h_measured = asrootpy ( m )
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


	def calculateChi2(truth,measured,covariance):
		diff = (truth - measured)
		chi2 = np.transpose( diff ).dot( np.linalg.inv( covariance ) ).dot( diff )
		ndf = len(truth)
		prob = TMath.Prob( chi2, len(truth) )
		return chi2Info( chi2, ndf, prob )

        chi2 = 99999999, 0
        if self.unfolded_data and self.truth:
            diff = self.truth - self.unfolded_data
            values = list(diff)
            errors = []
            for bin_i in range(len(values)):
                errors.append(diff.GetBinError(bin_i + 1))
            values = [abs(value) for value in values]
            errorsSquared = [error * error for error in errors]
            value = sum(values)
            error = sqrt(sum(errorsSquared))
            chi2 = value, error
        return chi2

def invertResponse(response):
	'''
	Invert the response. AKA swap gen vs reco axes in response histogram
	'''
	inverted_response = None

	xedges, yedges = hist2d_to_binEdges_list(response)
	response_matrix = np.matrix( hist2array(response, include_overflow=False, return_edges=False ) )
	inverted_response_matrix = np.transpose(response_matrix)
	inverted_response = matrix_to_hist2d(inverted_response_matrix, yedges, xedges )
	print "Response"
	print response_matrix
	print "Inverted Response"
	print hist2array(inverted_response)

	return inverted_response

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
	file_for_unfolded_covariance_template = 'data/normalisation/background_subtraction/13TeV/{var}/VisiblePS/central/covarianceMatrices/unfoldedNumberOfEvents/Stat_unfoldedNormalisation_Covariance_{ch}.txt'

	# file_for_response = File(config.unfolding_central, 'read')
	# file_for_responseInverse = File(config.unfolding_responseInverse, 'read')

	channel = [
		'electron',
		'muon',
	]
	for ch in channel:
		for var in config.variables:
			if 'electron' not in ch: continue 
			if 'HT' not in var: continue
			file_for_smeared_space = file_for_smeared_space_template.format( var = var, ch = ch )
			file_for_smeared_covariance = file_for_smeared_covariance_template.format( var = var, ch = ch )

			smeared_space = file_to_df(file_for_smeared_space)
			smeared_covariance = matrix_from_df(file_to_df(file_for_smeared_covariance))

			smeared_data = smeared_space['TTJet']
			smeared_mc = smeared_space['TTJet_MC']
			smeared_data = np.array( [ smeared_data[i]+smeared_data[i+1] for i in range(0, len(smeared_data), 2)] )
			smeared_mc = np.array([smeared_mc[i]+smeared_mc[i+1] for i in range(0, len(smeared_mc), 2)] )
			print '-'*160
			print 'Data : '
			print smeared_data
			print '-'*160
			print 'Smeared MC : '
			print smeared_mc
			print '-'*160
			print 'Statistical Covariance : '
			print smeared_covariance
			s_chi, s_ndf, s_pvalue = calculateChi2(smeared_data, smeared_mc, smeared_covariance)
			print '-'*160
			print 'Smeared Level Chi2 : '
			print s_chi
			print '-'*160

			print ''

			file_for_unfolded_space = file_for_unfolded_space_template.format( var = var, ch = ch )
			file_for_unfolded_covariance = file_for_unfolded_covariance_template.format( var = var, ch = ch )
			unfolded_space = file_to_df(file_for_unfolded_space)
			unfolded_covariance = matrix_from_df(file_to_df(file_for_unfolded_covariance))
			unfolded_data = np.array(unfolded_space['TTJets_unfolded'])
			unfolded_mc = np.array(unfolded_space['TTJets_powhegPythia8'])
			print '-'*160
			print 'Unfolded Data : '
			print unfolded_data
			print '-'*160
			print 'Particle Level MC : '
			print unfolded_mc
			print '-'*160
			print 'Some Matrix as Yet Unknown : '
			print unfolded_covariance
			u_chi, u_ndf, u_pvalue = calculateChi2(unfolded_data, unfolded_mc, unfolded_covariance)
			print '-'*160
			print 'Unfolded Level Chi2 : '
			print u_chi
			print '-'*160




if __name__ == '__main__':
	main()
			