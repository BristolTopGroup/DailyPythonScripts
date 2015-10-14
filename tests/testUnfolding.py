from tools.Unfolding import Unfolding, get_unfold_histogram_tuple
from rootpy.plotting import Hist, Hist2D
from config import XSectionConfig
from rootpy.io import File
from tools.file_utilities import read_data_from_JSON
from tools.hist_utilities import value_error_tuplelist_to_hist, value_tuplelist_to_hist
from config.variable_binning import bin_edges_vis
from ROOT import RooUnfoldResponse, RooUnfoldSvd, RooUnfoldBayes
from rootpy import asrootpy
from copy import copy
from math import sqrt
from random import gauss

#
# Use your own test input
#

bins = [0,10,15,30,60]

# Truth histogram
h_truth = Hist( bins )
h_truth.SetBinContent(1,400)
h_truth.SetBinContent(2,400)
h_truth.SetBinContent(3,100)
h_truth.SetBinContent(4,5)

# Measured histogram
# If identical to truth (before adding fakes), then there is no inefficiency in your measurement
h_measured = Hist( bins )
h_measured.SetBinContent(1,400)
h_measured.SetBinContent(2,400)
h_measured.SetBinContent(3,100)
h_measured.SetBinContent(4,5)

# Set data equal to measured for this test
h_data = Hist( bins )
h_data.SetBinContent(1,400)
h_data.SetBinContent(2,400)
h_data.SetBinContent(3,100)
h_data.SetBinContent(4,5)

# Fakes
# Add these to the measured and data histograms if you want to include fakes
h_fakes = Hist( bins )
h_fakes.SetBinContent(1,200)
h_fakes.SetBinContent(2,250)
h_fakes.SetBinContent(3,40)
h_fakes.SetBinContent(4,3)

# Add fakes to measured and data
h_measured += h_fakes
h_data += h_fakes

# Construct response matrix
# Should have same number of entries as measured without any fakes
# Set to diagonal for this test
h_response = Hist2D( bins, bins )

bin = h_response.FindBin( 5, 5 )
h_response.SetBinContent( bin, 400 )
h_response.SetBinError( bin, sqrt(h_response.GetBinContent(bin)) )

bin = h_response.FindBin( 12, 12 )
h_response.SetBinContent( bin, 400)
h_response.SetBinError( bin, sqrt(h_response.GetBinContent(bin)) )

bin = h_response.FindBin( 20, 20 )
h_response.SetBinContent( bin, 100 )
h_response.SetBinError( bin, sqrt(h_response.GetBinContent(bin)) )

bin = h_response.FindBin( 50, 50 )
h_response.SetBinContent( bin, 5 )
h_response.SetBinError( bin, sqrt(h_response.GetBinContent(bin)) )

# Set errors in all histograms
for bin in range(0,len(bins)):
	h_truth.SetBinError( bin, sqrt( h_truth.GetBinContent( bin ) ) )
	h_measured.SetBinError( bin, sqrt( h_measured.GetBinContent( bin ) ) )
	h_data.SetBinError(bin, sqrt( h_data.GetBinContent(bin)))


#
# Alternatively use histograms from our main analysis
#

# measurement_config = XSectionConfig( 13 )
# channel = 'electron'
# h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( inputfile = File( measurement_config.unfolding_central, 'read' ),
#                                                                       variable = 'MET',
#                                                                       channel = channel,
#                                                                       met_type = 'patType1CorrectedPFMet',
#                                                                       centre_of_mass = 13,
#                                                                       ttbar_xsection =  measurement_config.ttbar_xsection,
#                                                                       luminosity = measurement_config.luminosity * measurement_config.luminosity_scale,
#                                                                       load_fakes = True,
#                                                                       visiblePS = True,
#                                                                       )


# h_truth_bayes, h_measured_bayes, h_response_bayes, h_fakes_bayes = get_unfold_histogram_tuple( inputfile = File( measurement_config.unfolding_central, 'read' ),
#                                                                       variable = 'MET',
#                                                                       channel = channel,
#                                                                       met_type = 'patType1CorrectedPFMet',
#                                                                       centre_of_mass = 13,
#                                                                       ttbar_xsection =  measurement_config.ttbar_xsection,
#                                                                       luminosity = measurement_config.luminosity * measurement_config.luminosity_scale,
#                                                                       load_fakes = True,
#                                                                       visiblePS = True,
#                                                                       )

# fit_results = read_data_from_JSON( 'data/normalisation/background_subtraction//13TeV/MET/VisiblePS//central/normalisation_%s_patType1CorrectedPFMet.txt' % channel )['TTJet']
# edges = bin_edges_vis['MET']
# h_data = value_error_tuplelist_to_hist( fit_results, edges )


#
# This test takes the data distribution, which is the same underlying distribution as measured in the response matrix
# And varies it within statistical uncertainty (sqrt(N))
# Fakes are removed before unfolding
# Then, the unfolding is performed with SVD and Bayes, and the result for the first bin is stored in a histogram
#

h_svdFirstBin = Hist(100, 200, 800 )
h_bayesFirstBin = Hist(100, 200, 800 )
for i in range(0,1000):
	h_data_toUse = asrootpy( h_data )
	# Vary data within sqrt(N)
	for bin in range(1,h_data_toUse.GetNbinsX()+1):
		binContent = h_data_toUse.GetBinContent(bin)
		binError = h_data_toUse.GetBinError(bin)
		newContent = gauss(binContent,sqrt(binContent))
		if newContent < 0 : newContent = 0
		h_data_toUse.SetBinContent( bin, newContent)
		h_data_toUse.SetBinError( bin, sqrt(newContent))

	h_measured_toUse = asrootpy( h_measured )

	# Remove fakes before unfolding
	h_fakes = h_measured_toUse - h_response.ProjectionX()
	nonFakeRatio = 1 - h_fakes / h_measured_toUse
	h_measured_toUse *= nonFakeRatio / nonFakeRatio
	h_data_toUse *= nonFakeRatio / nonFakeRatio

	# Unfold with SVD
	response = RooUnfoldResponse ( h_measured_toUse, h_truth, h_response )
	svdUnfolding = RooUnfoldSvd( response, h_data_toUse, 0.7 )
	svdUnfolding.SetVerbose(0)
	h_unfolded_data_svd = svdUnfolding.Hreco( 3 )

	# Unfold with Bayes
	response_bayes = RooUnfoldResponse ( h_measured_toUse, h_truth, h_response )
	bayesUnfolding = RooUnfoldBayes( response_bayes, h_data_toUse, 4 )
	h_unfolded_data_bayes = bayesUnfolding.Hreco( 3 )

	# Store result of first bin
	h_svdFirstBin.Fill( h_unfolded_data_svd.GetBinContent(1) )
	h_bayesFirstBin.Fill( h_unfolded_data_bayes.GetBinContent(1) )

# Draw histograms
h_svdFirstBin.Draw()
raw_input('SVD')
h_bayesFirstBin.Draw()
raw_input('Bayes')