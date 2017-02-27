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
from operator import itemgetter

# rc( 'font', **CMS.font )
# rc( 'text', usetex = False )

def plot_systematic_uncertainties(systematic_uncertainties, bin_edges, variable, output_folder, subcategories = [], subname = '', plot_largest = False):
	'''
	Plot the systematic uncertainties
	'''
	print subcategories
	if not subcategories: subcategories = systematic_uncertainties.keys()

	x_limits = [bin_edges[0], bin_edges[-1]]
	# y_limits = [-0.6,0.6]
	y_limits = [0,0.4]

	fig_syst = plt.figure( figsize = ( 20, 16 ), dpi = 400, facecolor = 'white' )
	ax_syst = fig_syst.add_subplot(1, 1, 1)
	ax_syst.minorticks_on()
	ax_syst.xaxis.labelpad = 12
	ax_syst.yaxis.labelpad = 12

	error_hists_up = {}
	error_hists_down = {}
	stat_hist = None

	for syst, vals in systematic_uncertainties.iteritems():
		if syst == 'central': 
			n = len(systematic_uncertainties[syst])
			continue
		elif syst == 'statistical':
			stat_hist_up = values_and_errors_to_hist( vals, [], bin_edges )
			stat_hist_down = values_and_errors_to_hist( -vals, [], bin_edges )
		elif syst == 'systematic':
			syst_hist_up = values_and_errors_to_hist( vals, [], bin_edges )
			syst_hist_down = values_and_errors_to_hist( -vals, [], bin_edges )
		elif syst in subcategories:
			error_hists_up[syst] = values_and_errors_to_hist( vals, [], bin_edges )
			error_hists_down[syst] = values_and_errors_to_hist( -vals, [], bin_edges )
		else: continue

	if plot_largest:
		largest_syst = []
		for bin_i in range( n ):
			high = []
			for syst, vals in systematic_uncertainties.iteritems():
				if syst == 'central': continue
				if syst == 'statistical': continue
				if syst == 'systematic': continue
				high.append([syst,vals[bin_i]])
			high = sorted(high, key = itemgetter(1), reverse=True)
			# Retrieve highest systematics
			if high[0][0] not in largest_syst: largest_syst.append(high[0][0])
			elif high[1][0] not in largest_syst: largest_syst.append(high[1][0])
			else: continue

	rplt.fill_between( syst_hist_up, syst_hist_down, color = 'yellow', label='Syst.' )
	rplt.fill_between( stat_hist_down, stat_hist_up, color = 'grey', label='Stat.' )

	plt.tick_params( **CMS.axis_label_major )
	plt.tick_params( **CMS.axis_label_minor )

	colours = ['red', 'blue', 'green', 'chartreuse', 'indigo', 'magenta', 'darkmagenta', 'hotpink', 'cyan', 'darkred', 'darkgoldenrod', 'mediumvioletred', 'mediumspringgreen', 'gold', 'darkgoldenrod', 'slategray', 'dodgerblue', 'cadetblue', 'darkblue', 'seagreen', 'deeppink', 'deepskyblue' ]
	# if len(colours) < len(error_hists.keys()):
	# 	print '---> Need to add more colours!!!'

	for error_hists in [error_hists_up, error_hists_down]:
		for i, source, in enumerate(error_hists.keys()):
			hist = error_hists[source]
			hist.linewidth = 4
			hist.color = colours[i]
			if plot_largest:
				if source not in largest_syst:
					hist.linestyle = 'dashed'
					hist.alpha = 0.4	
					hist.linewidth = 2
			# Only label systematic once
			if error_hists == error_hists_up:
				rplt.hist( hist, stacked=False, label = source )
			else:
				rplt.hist( hist, stacked=False, label = '' )

	leg = plt.legend(loc='upper right',prop={'size':25},ncol=3)
	# leg = plt.legend(loc='upper right',prop={'size':20},ncol=4)
	leg.draw_frame(False)	

	x_title = variables_NonLatex[variable]
	if variable in ['HT', 'MET', 'WPT', 'ST', 'lepton_pt']:
		x_title += ' [GeV]'

	ax_syst.set_xlim( x_limits )
	ax_syst.set_ylim( y_limits )
	plt.xlabel( x_title, CMS.x_axis_title )
	plt.ylabel( 'Relative Uncertainty', CMS.y_axis_title)

	template = '%.1f fb$^{-1}$ (%d TeV)'
	label = template % ( measurement_config.new_luminosity/1000, measurement_config.centre_of_mass_energy)
	plt.title( label,loc='right', **CMS.title )

	logo_location = (0.05, 0.98)
	prelim_location = (0.05, 0.92)
	channel_location = ( 0.05, 0.86)
	# plt.text(logo_location[0], logo_location[1], 
	# 	"CMS", 
	# 	transform=ax_syst.transAxes, 
	# 	fontsize=42,
	# 	verticalalignment='top',
	# 	horizontalalignment='left'
	# )
	# # preliminary
	# plt.text(prelim_location[0], prelim_location[1], 
	# 	r"\emph{Preliminary}",
	# 	transform=ax_syst.transAxes, 
	# 	fontsize=42,
	# 	verticalalignment='top',
	# 	horizontalalignment='left'
	# )
	# # channel text
	# plt.text(channel_location[0], channel_location[1], 
	# 	r"\emph{%s}" % channel, 
	# 	transform=ax_syst.transAxes, 
	# 	fontsize=40,
	# 	verticalalignment='top',
	# 	horizontalalignment='left'
	# )

	plt.tight_layout()

	file_template = output_folder + '{var}_systematics_{com}TeV'.format(
		var = variable, 
		com = measurement_config.centre_of_mass_energy,
	)
	if subname: file_template = file_template + '_' + subname
	file_template += '.pdf'
	fig_syst.savefig(file_template)
	print "Written plots to {f}".format(f = file_template)
	# plt.show()
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
	# for keys in measurement_config.rate_changing_systematics_values.keys():
	# 	print keys
	# 	print measurement_config.rate_changing_systematics_values[keys].scale

    unc_type = [
        'normalised',
        'absolute',
    ]

	for channel in ['electron', 'muon', 'combined', 'combinedBeforeUnfolding']:  
		if channel != 'combined':continue
        for utype in unc_type:
			input_file = '{basepath}/{com}TeV/{var}/{ps}/central/xsection_{type}_{channel}_{method}_summary_relative.txt'.format(
				basepath = 	path,
				com = 	com,
				var = variable,
				ps = phase_space,
				channel = channel,
				method = method,
				type = utype,
			)
			output_folder = 'plots/systematics/{channel}/{ps}/{type}/'.format(
				channel = channel,
				ps = phase_space,
				type = utype,
			)
			make_folder_if_not_exists(output_folder)

			systematic_uncertainties = pu.file_to_df(input_file)

			# any group of systematics you want to plot
			l_xsec = []
			l_mc = []
			l_weight = []
			l_met = []
			l_shape = []
			for k in systematic_uncertainties.keys():
				if 'cross_section' in k:  l_xsec.append(k)
				elif 'TTJets_' in k:  l_mc.append(k)
				elif ('Electron' in k or 'Muon' in k or 'PileUp' in k or 'luminosity' in k or 'BJet' in k) and 'En' not in k: l_weight.append(k) 
				elif 'En' in k: l_met.append(k) 
				elif 'JES' in k or 'JER' in k or 'QCD_shape' in k or 'PDF' in k: l_shape.append(k) 
				else : print ' Not including {}'.format(k)

			# # Plot them
			plot_systematic_uncertainties(systematic_uncertainties, bin_edges, variable, output_folder)
			plot_systematic_uncertainties(systematic_uncertainties, bin_edges, variable, output_folder, plot_largest = True, subname = 'largest')
			plot_systematic_uncertainties(systematic_uncertainties, bin_edges, variable, output_folder,l_xsec, "xsection")
			plot_systematic_uncertainties(systematic_uncertainties, bin_edges, variable, output_folder,l_mc, "mc")
			plot_systematic_uncertainties(systematic_uncertainties, bin_edges, variable, output_folder,l_weight, "weight")
			plot_systematic_uncertainties(systematic_uncertainties, bin_edges, variable, output_folder,l_met, "met")
			plot_systematic_uncertainties(systematic_uncertainties, bin_edges, variable, output_folder,l_shape, "shape")
