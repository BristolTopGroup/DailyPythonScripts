from make_unfolding_pull_plots import *
import os
from config import XSectionConfig
from config.variable_binning import bin_edges
from optparse import OptionParser
from rootpy.plotting import Graph
from rootpy import asrootpy
from ROOT import TGraphAsymmErrors, TGraph
from matplotlib.ticker import FormatStrFormatter
import rootpy.plotting.root2matplotlib as rplt

def getkValueRange( inputFolder ):
	dirContents = os.listdir( inputFolder )
	kValues = []
	for i in dirContents:
		kValues.append( int(i.split('_')[-1]) )
	return kValues

if __name__ == "__main__":
	set_root_defaults()
	parser = OptionParser()
	parser.add_option("-v", "--variable", dest="variable", default='MET',
	                  help="set the variable to analyse (MET, HT, ST, MT, WPT)")
	parser.add_option("-s", "--centre-of-mass-energy", dest="CoM", default=8,
	                  help="set the centre of mass energy for analysis. Default = 8 [TeV]", type=int)
	parser.add_option("-i", "--input-folder", type='string',
	                  dest="input_folder", help="location of the pull data")
	parser.add_option("-o", "--output",
	                  dest="output_folder", default='plots/unfolding_pulls',
	                  help="output folder for unfolding pull plots")
	parser.add_option("-c", "--channel", type='string',
	                  dest="channel", default='combined',
	                  help="channel to be analysed: electron|muon|combined")

	(options, args) = parser.parse_args()
	measurement_config = XSectionConfig(options.CoM)
	
	if not options.input_folder:
	    sys.exit('No input folder specified. Please do so manually using -i option.')

	centre_of_mass = options.CoM
	variable = options.variable
	channel = options.channel
	output_folder_base = options.output_folder + '/' + str(centre_of_mass) + 'TeV/' + variable + '/' + channel + '/'
	make_folder_if_not_exists(output_folder_base)
	output_formats = ['pdf']
	input_folder = options.input_folder+'/' + str(centre_of_mass) + 'TeV/' + variable + '/35_input_toy_mc/'
	print input_folder

	bins = array('d', bin_edges[variable])
	nbins = len(bins) - 1

	kValues = sorted( getkValueRange( input_folder ) )

	sigmaForEachK = []

	for k in kValues:
		if k is 1:
			continue

		output_folder = output_folder_base + '/kv' + str(k) + '/'
		make_folder_if_not_exists(output_folder)

		print 'Producing unfolding pull plots for %s variable, k-value of %d, channel: %s. \nOutput folder: %s' % (variable, k, channel, output_folder)

		files = glob(input_folder + '/k_value_' + str(k) + '/*_' + channel + '*_*.txt')
		if not files:
		    sys.exit('No *.txt files found in input directory.')
		
		pulls = get_data(files, subset='pull')

		maxSigma = 0
		minSigma = 100
		for bin_i in range (0, nbins):
		    fitResults = plot_pull(pulls, centre_of_mass, channel, variable, k, output_folder, output_formats, bin_index = bin_i, n_bins = nbins)
		    if fitResults.sigma > maxSigma: maxSigma = fitResults.sigma
		    if fitResults.sigma < minSigma: minSigma = fitResults.sigma

		# #plot all bins
		allBinsFitResults = plot_pull(pulls, centre_of_mass, channel, variable, k, output_folder, output_formats )

		allBinsSigma = allBinsFitResults.sigma
		sigmaForEachK.append( [k,allBinsSigma, maxSigma, minSigma])
		print 'All bins sigma :',allBinsFitResults.sigma
		print 'Max/min sigma :',maxSigma,minSigma
		print 'Spread :',maxSigma-minSigma
		del pulls #deleting to make space in memory
	print '\n'

	kValues = list( zip(*sigmaForEachK)[0] )
	kValuesup = []
	kValuesdown = []
	sigmas = list( zip(*sigmaForEachK)[1] )
	sigmaups = list( zip(*sigmaForEachK)[2] )
	sigmadowns = list( zip(*sigmaForEachK)[3] )
	spread = []

	for i in range(0,len(sigmas)):
		spread.append( ( sigmaups[i] - sigmadowns[i] ) / sigmas[i] )
		sigmaups[i] = sigmaups[i] - sigmas[i]
		sigmadowns[i] = sigmas[i] - sigmadowns[i]
		kValuesup.append(0.5)
		kValuesdown.append(0.5)
	print spread
	kValueChoice = spread.index(min(spread))
	print kValueChoice

	graph = asrootpy(TGraphAsymmErrors(len(sigmas), array('d',kValues), array('d',sigmas),array('d',kValuesdown), array('d',kValuesup), array('d',sigmadowns), array('d',sigmaups)))
	graphSpread = asrootpy(TGraphAsymmErrors(len(sigmas), array('d',kValues), array('d',spread),array('d',kValuesdown), array('d',kValuesup), array('d',sigmadowns), array('d',sigmaups)))

	# plot with matplotlib
	plt.figure(figsize=(20, 16), dpi=200, facecolor='white')

	ax0 = plt.axes()
	ax0.minorticks_on()
	ax0.grid(True, 'major', linewidth=2)
	ax0.grid(True, 'minor')
	plt.tick_params(**CMS.axis_label_major)
	plt.tick_params(**CMS.axis_label_minor)
	
	ax0.xaxis.set_major_formatter(FormatStrFormatter('%d'))
	ax0.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
	ax0.xaxis.labelpad = 11
	
	rplt.errorbar(graph, xerr=True, emptybins=True, axes=ax0, marker = 'o', ms = 15, mew=3, lw = 2)
	rplt.errorbar(graphSpread, xerr=False, yerr=False, axes=ax0, linestyle='-', marker = 's', ms = 10, mew=1, lw = 2)

	for output_format in output_formats:
		print output_folder_base
		plt.savefig(output_folder_base + '/TESTGRAPH' + '.' + output_format)  

	print kValues
	print kValuesup
	print kValuesdown
	print sigmas
	print sigmaups
	print sigmadowns
	print sigmaForEachK
    