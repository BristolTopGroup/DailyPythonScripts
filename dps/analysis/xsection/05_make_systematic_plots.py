# from __future__ import division  # the result of the division will be always a float
from argparse import ArgumentParser
import dps.utils.pandas_utilities as pu

from dps.config.latex_labels import variables_latex, variables_NonLatex
from dps.config.variable_binning import bin_edges_vis, bin_edges_full
from dps.config.xsection import XSectionConfig
from dps.utils.file_utilities import make_folder_if_not_exists
from dps.utils.hist_utilities import values_and_errors_to_hist, hist_to_value_error_tuplelist

import matplotlib.pyplot as plt
import rootpy.plotting.root2matplotlib as rplt
from dps.config import CMS

# dynamic matplotlib settings
from matplotlib import rc
rc( 'font', **CMS.font )
rc( 'text', usetex = False )

def plot_systematic_uncertainties(systematic_uncertainties, bin_edges, variable, output_folder):
	'''
	Plot the systematic uncertainties
	'''
	x_limits = [bin_edges[0], bin_edges[-1]]
	y_limits = [0,0.6]
	fig_syst = plt.figure( figsize = ( 20, 16 ), dpi = 400, facecolor = 'white' )
	ax_syst = fig_syst.add_subplot(1, 1, 1)
	ax_syst.minorticks_on()
	ax_syst.xaxis.labelpad = 12
	ax_syst.yaxis.labelpad = 12

	error_hists = {}
	stat_hist = None

	for syst, vals in systematic_uncertainties.iteritems():
		if syst == 'statistical':
			stat_hist = values_and_errors_to_hist( vals, [], bin_edges )
		elif syst == 'systematic':
			full_syst_hist = values_and_errors_to_hist( vals, [], bin_edges )
		elif syst == 'central':
			central_hist = values_and_errors_to_hist( vals, [], bin_edges )
		else:
			error_hists[syst] = values_and_errors_to_hist( vals, [], bin_edges )

	plt.tick_params( **CMS.axis_label_major )
	plt.tick_params( **CMS.axis_label_minor )

	colours = ['red', 'blue', 'green', 'chartreuse', 'indigo', 'magenta', 'darkmagenta', 'hotpink', 'cyan', 'darkred', 'darkgoldenrod', 'mediumvioletred', 'mediumspringgreen', 'gold', 'darkgoldenrod', 'slategray', 'dodgerblue', 'cadetblue', 'darkblue', 'seagreen', 'deeppink' ]
	for source, colour in zip (error_hists.keys(), colours):
		hist = error_hists[source]
		hist.linewidth = 4
		hist.color = colour
		rplt.hist( hist, stacked=False, axes = ax_syst, label = source )

	stat_hist.linewidth = 4
	stat_hist.color = 'black'
	stat_hist.linestyle = 'dashed'
	rplt.hist( stat_hist, stacked=False, axes = ax_syst, label = 'stat.' )

	full_syst_hist.linewidth = 4
	full_syst_hist.color = 'black'
	rplt.hist( full_syst_hist, stacked=False, axes = ax_syst, label = 'tot syst.' )

	leg = plt.legend(loc=1,prop={'size':30},ncol=2)
	leg.draw_frame(False)	

	x_title = variables_NonLatex[variable]
	if variable in ['HT', 'MET', 'WPT', 'ST', 'lepton_pt']:
		x_title += ' [GeV]'

	ax_syst.set_xlim( x_limits )
	ax_syst.set_ylim( y_limits )
	plt.xlabel( x_title, CMS.x_axis_title )
	plt.ylabel( 'Relative Uncertainty', CMS.y_axis_title)
	plt.tight_layout()

	file_template = output_folder + '{var}_systematics_{com}TeV.pdf'.format(
		var = variable, 
		com = measurement_config.centre_of_mass_energy,
	)
	fig_syst.savefig(file_template)
	print "Written plots to {f}".format(f = file_template)
	return

if __name__ == '__main__':
	parser = ArgumentParser(__doc__)
	parser.add_argument(
		"-p", 
		"--path", 
		dest="path", 
		default='data/normalisation/background_subtraction',
		help="set path to JSON files"
	)
	parser.add_argument(
		"-o", 
		"--output_folder", 
		dest="output_folder", 
		default='tables/',
		help="set path to save tables"
	)
	parser.add_argument(
		"-v", 
		"--variable", 
		dest="variable", 
		default='MET',
		help="set variable to plot (MET, HT, ST, MT, WPT)"
	)
	parser.add_argument( 
		'--visiblePS', 
		dest = "visiblePS", 
		action = "store_true",
		help = "Unfold to visible phase space" 
	)
	parser.add_argument(
		"-c", 
		"--centre-of-mass-energy", 
		dest="CoM", 
		default=13, 
		type=int,
		help="set the centre of mass energy for analysis. Default = 13 [TeV]"
	)
	parser.add_argument( 
		"-u", 
		"--unfolding_method", 
		dest = "unfolding_method", 
		default = 'TUnfold',
		help = "Unfolding method: TUnfold (default)" 
	)

	args = parser.parse_args()

	path = args.path
	com = args.CoM
	method = args.unfolding_method
	variable = args.variable
	output_folder = args.output_folder
	ps_vis = args.visiblePS
	
	phase_space = 'FullPS'
	bin_edges = bin_edges_full[variable]
	if ps_vis:
		phase_space = 'VisiblePS'
		bin_edges = bin_edges_vis[variable]
	measurement_config = XSectionConfig(com)


	for channel in ['electron', 'muon', 'combined', 'combinedBeforeUnfolding']:  

		input_file = '{basepath}/{com}TeV/{var}/{ps}/central/normalised_xsection_{channel}_{method}_summary_relative.txt'.format(
			basepath = 	path,
			com = 	com,
			var = variable,
			ps = phase_space,
			channel = channel,
			method = method,
		)
		output_folder = 'plots/systematics/{channel}/{ps}/'.format(
			channel = channel,
			ps = phase_space,
		)
		make_folder_if_not_exists(output_folder)

		systematic_uncertainties = pu.file_to_df(input_file)

		plot_systematic_uncertainties(systematic_uncertainties, bin_edges, variable, output_folder)

