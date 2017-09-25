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
from dps.utils.file_utilities import make_folder_if_not_exists
from dps.config.latex_labels import variables_latex

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

def create_latex_tables(d_bottom_line_test):
	'''
	Create latex output for bottom line test
	'''
	for var, d_ch_bottomline in d_bottom_line_test.iteritems():
		isFirstChannel = True
		fullTable = ''
		latexHeader =  '\\begin{landscape}\n'
		latexHeader += '\\begin{table}[!htbp]\n'
		latexHeader += '\t\centering\n'
		latexHeader += '\t\\tiny\n'
		fullTable 	+= latexHeader
		for ch, d_bottomline in d_ch_bottomline.iteritems():
			ncols = 'c'*(len(d_bottomline['Smeared']['N_DATA'])+2)


			latexColHeader 	= '\t\\begin{{tabular}}{{{}}}\n'.format(ncols)
			latexColHeader 	+= '\t\t\hline\n'
			latexColHeader 	+= '\t\t\hline\n'
			latexColHeader 	+= '\t\t{var} '.format(var=variables_latex[var])
			for bin in range (len(bin_edges_vis[var])-1):
				latexColHeader += '\t & \t {edge_down}-{edge_up}'.format(
					edge_down = bin_edges_vis[var][bin], 
					edge_up = bin_edges_vis[var][bin+1],
				)
			latexColHeader 	+= '\t & \ensuremath{\chi^{2}}'
			latexColHeader 	+= '\\\\ \n'
			latexColHeader 	+= '\t\t\hline\n'
			fullTable 		+= latexColHeader

			latexContent = ''
			latexContent += '\t\tData '
			for a in d_bottomline['Smeared']['N_DATA']:
				latexContent += '\t & \t {val}'.format( val = '{:.1f}'.format(a) )
			latexContent += '\t & \\\\ \n'

			latexContent += '\t\tSmeared MC'
			for a in d_bottomline['Smeared']['N_MC']:
				latexContent += '\t & \t {val}'.format( val = '{:.1f}'.format(a) )
			latexContent += '\t & {chi2} \\\\ \n'.format( chi2 = '{:.1f}'.format(d_bottomline['Smeared']['Chi2'].item(0)))

			latexContent += '\t\tUnfolded Data'
			for a in d_bottomline['Unfolded']['N_DATA']:
				latexContent += '\t & \t {val}'.format( val = '{:.1f}'.format(a) )
			latexContent += '\t & \\\\ \n'

			latexContent += '\t\tTrue MC'
			for a in d_bottomline['Unfolded']['N_MC']:
				latexContent += '\t & \t {val}'.format( val = '{:.1f}'.format(a) )
			latexContent += '\t & {chi2} \\\\ \n'.format( chi2 = '{:.1f}'.format(d_bottomline['Unfolded']['Chi2'].item(0)))
			fullTable 		+= latexContent

			latexFooter = '\t\t\hline\n'
			latexFooter += '\t\end{tabular}\n'
			latexFooter += '\t\caption{{ Bottom line test of the unfolding for {var} in the {ch} channel.}}\n'.format( var = variables_latex[var], ch=ch )
			latexFooter += '\t\label{{tb:bottomline_{var}_{ch}}}\n'.format( var = var, ch=ch )	
			if isFirstChannel:
				isFirstChannel = False
				latexFooter += '\t\\vspace*{1cm} \n'
				latexFooter += '\t\\newline \n'
				fullTable	+= latexFooter
			else:
				fullTable 	+= latexFooter
		
		latexTableFooter 	= '\\end{table}\n'
		latexTableFooter 	+= '\\end{landscape}\n'
		fullTable 			+= latexTableFooter
		print fullTable

		#########################################################################################################
		### Write Table
		#########################################################################################################
		make_folder_if_not_exists('tables/bottomline')
		file_template = 'tables/bottomline/{var}_bottomlinetest.tex'.format(var=var)
		output_file = open(file_template, 'w')
		output_file.write(fullTable)
		output_file.close()
		print 'Written Bottom Line Test for {} in the {} channel'.format(var, ch)

def main():
	'''
	'''
	debug  = False
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
	d_bottom_line_test = {}
	for var in config.variables:
		d_bottom_line_test[var] = {}
		for ch in channel:
			d_bottom_line_test[var][ch] = {}
			opts['variable'] 			= var
			opts['channel'] 			= ch
			# if 'electron' not in ch: continue 
			# if 'HT' not in var: continue

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
			d_bottom_line_test[var][ch]['Unfolded'] = {
				'N_MC' 		: unfolded_mc,
				'N_DATA' 	: unfolded_data,
				'Chi2' 		: unfolded_chi,
				'NDF' 		: unfolded_ndf,
				'P_VALUE'	: unfolded_pvalue,
			}

			# Get smeared data and rebin
			# ut.h_refolded_smeared = unfolding.refold()
			# ut.h_refolded_smeared = ut.h_refolded_smeared.rebinned(2)
			ut.h_data_smeared_no_fakes = ut.h_data_smeared_no_fakes.rebinned(2)
			ut.h_mc_smeared = ut.h_mc_smeared.rebinned(2)

			# Reconstructed level covariance matrices, data and mc ==> chi2
			smeared_covariance = np.matrix(np.diag( [e**2 for (v,e) in hist_to_value_error_tuplelist(ut.h_data_smeared_no_fakes)] ) ) + np.matrix(np.diag( [e**2 for (v,e) in hist_to_value_error_tuplelist(ut.h_data_smeared_no_fakes)] ) )
			# smeared_data = np.array(hist_to_value_list(ut.h_refolded_smeared))
			smeared_data = np.array(hist_to_value_list(ut.h_data_smeared_no_fakes))
			smeared_mc = np.array(hist_to_value_list(ut.h_mc_smeared))
			smeared_chi, smeared_ndf, smeared_pvalue = calculateChi2(smeared_data, smeared_mc, smeared_covariance)
			d_bottom_line_test[var][ch]['Smeared'] = {
				'N_MC' 		: smeared_mc,
				'N_DATA' 	: smeared_data,
				'Chi2' 		: smeared_chi,
				'NDF' 		: smeared_ndf,
				'P_VALUE'	: smeared_pvalue,
			}
			if debug:
				print ""
				print "="*160
				print "Bottom Line Test for {} in the {} Channel".format(var,ch)
				print '- '*80
				print ""
				print unfolded_data
				print unfolded_mc
				print unfolded_covariance
				print ""
				print 'Unfolded Level Chi2 : {}|{}; p={}'.format(unfolded_chi, unfolded_ndf, unfolded_pvalue)
				print '-'*160
				print smeared_data
				print smeared_mc
				print smeared_covariance
				print ""
				print 'Smeared Level Chi2 : {}|{}; p={}'.format(smeared_chi, smeared_ndf, smeared_pvalue)
				print "="*160
	create_latex_tables(d_bottom_line_test)
if __name__ == '__main__':
	main()
			