from argparse import ArgumentParser
from dps.config.latex_labels import samples_latex, channel_latex, variables_latex
from dps.config.variable_binning import control_plots_bins
from dps.config.histogram_colours import histogram_colours as colours
from dps.config.xsection import XSectionConfig
from dps.utils.file_utilities import make_folder_if_not_exists
from dps.utils.plotting import make_data_mc_comparison_plot, make_shape_comparison_plot, \
Histogram_properties
from dps.utils.hist_utilities import prepare_histograms, clean_control_region
from dps.utils.ROOT_utils import get_histograms_from_trees, set_root_defaults
from dps.utils.latex import setup_matplotlib
from dps.utils.pandas_utilities import dict_to_df, df_to_file
from uncertainties import ufloat
setup_matplotlib()

def plotHistograms(
		histogram_files, 
		var_to_plot,
		output_folder):
	'''
	'''
	global measurement_config

	weightBranchSignalRegion  = 'EventWeight * PUWeight * BJetWeight'
	weightBranchControlRegion = 'EventWeight'

	# Names of QCD regions to use
	qcd_data_region             = ''
	qcd_data_region_electron    = 'QCD non iso e+jets'
	qcd_data_region_muon        = 'QCD non iso mu+jets 1p5to3'

	sr_e_tree = 'TTbar_plus_X_analysis/EPlusJets/Ref selection/AnalysisVariables'
	sr_mu_tree = 'TTbar_plus_X_analysis/MuPlusJets/Ref selection/AnalysisVariables'
	cr_e_tree = 'TTbar_plus_X_analysis/EPlusJets/{}/AnalysisVariables'.format(qcd_data_region_electron)
	cr_mu_tree = 'TTbar_plus_X_analysis/MuPlusJets/{}/AnalysisVariables'.format(qcd_data_region_muon)
	
	print "Trees : "
	print "\t {}".format(sr_e_tree)
	print "\t {}".format(sr_mu_tree)
	print "\t {}".format(cr_e_tree)
	print "\t {}".format(cr_mu_tree)

	histogram_files_electron            = dict(histogram_files)
	histogram_files_electron['data']    = measurement_config.data_file_electron
	histogram_files_electron['QCD']     = measurement_config.electron_QCD_MC_trees

	histogram_files_muon                = dict(histogram_files)
	histogram_files_muon['data']        = measurement_config.data_file_muon
	histogram_files_muon['QCD']         = measurement_config.muon_QCD_MC_trees

	signal_region_hists = {}
	control_region_hists = {}

	for var in var_to_plot:
		selectionSignalRegion = '{} >= 0'.format(var)

		# Print all the weights applied to this plot 
		print "Variable : {}".format(var)
		print "Weight applied : {}".format(weightBranchSignalRegion)
		print "Selection applied : {}".format(selectionSignalRegion)

		histograms_electron = get_histograms_from_trees( 
			trees = [sr_e_tree], 
			branch = var, 
			weightBranch = weightBranchSignalRegion + ' * ElectronEfficiencyCorrection', 
			files = histogram_files_electron, 
			nBins = 20, 
			xMin = control_plots_bins[var][0], 
			xMax = control_plots_bins[var][-1], 
			selection = selectionSignalRegion 
		)
		histograms_muon = get_histograms_from_trees( 
			trees = [sr_mu_tree], 
			branch = var, 
			weightBranch = weightBranchSignalRegion + ' * MuonEfficiencyCorrection', 
			files = histogram_files_muon, 
			nBins = 20, 
			xMin = control_plots_bins[var][0], 
			xMax = control_plots_bins[var][-1], 
			selection = selectionSignalRegion 
		)
		histograms_electron_QCDControlRegion = get_histograms_from_trees( 
			trees = [cr_e_tree], 
			branch = var, 
			weightBranch = weightBranchControlRegion, 
			files = histogram_files_electron, 
			nBins = 20, 
			xMin = control_plots_bins[var][0], 
			xMax = control_plots_bins[var][-1], 
			selection = selectionSignalRegion 
		)
		histograms_muon_QCDControlRegion     = get_histograms_from_trees( 
			trees = [cr_mu_tree], 
			branch = var, 
			weightBranch = weightBranchControlRegion, 
			files = histogram_files_muon, 
			nBins = 20, 
			xMin = control_plots_bins[var][0], 
			xMax = control_plots_bins[var][-1], 
			selection = selectionSignalRegion 
		)

		# Combine the electron and muon histograms
		for sample in histograms_electron:
			h_electron = histograms_electron[sample][sr_e_tree]
			h_muon     = histograms_muon[sample][sr_mu_tree]
			h_qcd_electron = histograms_electron_QCDControlRegion[sample][cr_e_tree]
			h_qcd_muon     = histograms_muon_QCDControlRegion[sample][cr_mu_tree]

			signal_region_hists[sample] = h_electron + h_muon
			control_region_hists[sample] = h_qcd_electron + h_qcd_muon

		# NORMALISE TO LUMI
		prepare_histograms( 
			signal_region_hists, 
			scale_factor = measurement_config.luminosity_scale 
		)
		prepare_histograms( 
			control_region_hists, 
			scale_factor = measurement_config.luminosity_scale 
		)

		# BACKGROUND SUBTRACTION FOR QCD
		qcd_from_data = None
		qcd_from_data = clean_control_region( 
			control_region_hists,
			subtract = ['TTJet', 'V+Jets', 'SingleTop'] 
		)

		# DATA DRIVEN QCD
		nBins = signal_region_hists['QCD'].GetNbinsX()
		n, error = signal_region_hists['QCD'].integral(0,nBins+1,error=True)
		n_qcd_predicted_mc_signal = ufloat( n, error)

		n, error = control_region_hists['QCD'].integral(0,nBins+1,error=True)
		n_qcd_predicted_mc_control = ufloat( n, error)

		n, error = qcd_from_data.integral(0,nBins+1,error=True)
		n_qcd_control_region = ufloat( n, error)

		dataDrivenQCDScale = n_qcd_predicted_mc_signal / n_qcd_predicted_mc_control
		qcd_from_data.Scale( dataDrivenQCDScale.nominal_value )
		signal_region_hists['QCD'] = qcd_from_data

		# PLOTTING
		histograms_to_draw = []
		histogram_lables   = []
		histogram_colors   = []

		histograms_to_draw = [
			# signal_region_hists['data'], 
			# qcd_from_data,
			# signal_region_hists['V+Jets'],
			signal_region_hists['SingleTop'],
			signal_region_hists['ST_s'],
			signal_region_hists['ST_t'],
			signal_region_hists['ST_tW'],
			signal_region_hists['STbar_t'],
			signal_region_hists['STbar_tW'],
			# signal_region_hists['TTJet'],
		]
		histogram_lables   = [
			'data',
			# 'QCD', 
			# 'V+Jets', 
			# 'Single-Top', 
			'ST-s', 
			'ST-t', 
			'ST-tW', 
			'STbar-t', 
			'STbar-tW', 
			# samples_latex['TTJet'],
		]
		histogram_colors   = [
			colours['data'], 
			# colours['QCD'], 
			# colours['V+Jets'], 
			# colours['Single-Top'],
			colours['ST_s'],
			colours['ST_t'],
			colours['ST_tW'],
			colours['STbar_t'],
			colours['STbar_tW'], 
			# colours['TTJet'],
		]

		# Find maximum y of samples
		maxData = max( list(signal_region_hists['SingleTop'].y()) )
		y_limits = [0, maxData * 1.5]
		log_y = False
		if log_y:
			y_limits = [0.1, maxData * 100 ]

		# Lumi title of plots
		title_template = '%.1f fb$^{-1}$ (%d TeV)'
		title = title_template % ( measurement_config.new_luminosity/1000., measurement_config.centre_of_mass_energy )
		x_axis_title = '$%s$ [GeV]' % variables_latex[var]
		y_axis_title = 'Events/(%i GeV)' % binWidth(control_plots_bins[var])

		# More histogram settings to look semi decent
		histogram_properties = Histogram_properties()
		histogram_properties.name                   = var + '_with_ratio'
		histogram_properties.title                  = title
		histogram_properties.x_axis_title           = x_axis_title
		histogram_properties.y_axis_title           = y_axis_title
		histogram_properties.x_limits               = control_plots_bins[var]
		histogram_properties.y_limits               = y_limits
		histogram_properties.y_max_scale            = 1.4
		histogram_properties.xerr                   = None
		histogram_properties.emptybins              = True
		histogram_properties.additional_text        = channel_latex['combined']
		histogram_properties.legend_location        = ( 0.9, 0.73 )
		histogram_properties.cms_logo_location      = 'left'
		histogram_properties.preliminary            = True
		histogram_properties.set_log_y              = log_y
		histogram_properties.legend_color           = False
		histogram_properties.ratio_y_limits     	= [0.1,1.9]
		if log_y: histogram_properties.name += '_logy'
		loc = histogram_properties.legend_location
		histogram_properties.legend_location = ( loc[0], loc[1] + 0.05 )

		make_data_mc_comparison_plot( 
			histograms_to_draw, 
			histogram_lables, 
			histogram_colors,
			histogram_properties, 
			save_folder = output_folder,
			show_ratio = True, 
		)

		histogram_properties.name                   = var + '_ST_TTJet_Shape'
		if log_y: histogram_properties.name += '_logy'
		histogram_properties.y_axis_title           = 'Normalised Distribution'
		histogram_properties.y_limits               = [0,0.5]

		make_shape_comparison_plot( 
			shapes = [
				signal_region_hists['TTJet'],
				signal_region_hists['ST_t'],
				signal_region_hists['ST_tW'],
				signal_region_hists['ST_s'],
				signal_region_hists['STbar_t'],
				signal_region_hists['STbar_tW'], 
			],
			names = [
				samples_latex['TTJet'],
				'Single-Top t channel',
				'Single-Top tW channel',
				'Single-Top s channel',
				'Single-AntiTop t channel',
				'Single-AntiTop tW channel',
			],
			colours = [
				colours['TTJet'],
				colours['ST_t'],
				colours['ST_tW'],
				colours['ST_s'],
				colours['STbar_t'],
				colours['STbar_tW'],
			],
			histogram_properties = histogram_properties,
			save_folder = output_folder,
			fill_area = False,
			add_error_bars = False,
			save_as = ['pdf'],
			make_ratio = True, 
			alpha = 1,
		)
		print_output(signal_region_hists, output_folder, var, 'combined')
	return

def binWidth(binning):
	return  ( binning[-1] - binning[0] ) / ( len(binning)-1 )

def parse_arguments():
	parser = ArgumentParser(__doc__)
	parser.add_argument( "-o", "--output_folder", 
		dest = "output_folder", 
		default = 'plots/control_plots/',
		help = "set path to save plots" 
	)
	args = parser.parse_args()
	return args

def print_output(signal_region_hists, output_folder_to_use, branchName, channel):
	'''Printout on normalisation of different samples to screen and table'''
	print 'Normalisation after selection'
	print 'Single Top :', signal_region_hists['SingleTop'].integral(overflow=True)
	print 'ST s       :', signal_region_hists['ST_s'].integral(overflow=True)
	print 'ST t       :', signal_region_hists['ST_t'].integral(overflow=True)
	print 'ST tW      :', signal_region_hists['ST_tW'].integral(overflow=True)
	print 'STbar t    :', signal_region_hists['STbar_t'].integral(overflow=True)
	print 'STbar tW   :', signal_region_hists['STbar_tW'].integral(overflow=True)
	print '-'*60
	mcSum = signal_region_hists['ST_s'].integral(overflow=True) + signal_region_hists['ST_t'].integral(overflow=True) + signal_region_hists['ST_tW'].integral(overflow=True) + signal_region_hists['STbar_t'].integral(overflow=True) + signal_region_hists['STbar_tW'].integral(overflow=True)
	print 'Total DATA :', signal_region_hists['SingleTop'].integral(overflow=True)
	print 'Total MC   :', mcSum
	print '='*60

	output_folder = output_folder_to_use + 'tables/'
	make_folder_if_not_exists(output_folder)

	summary = {}
	summary['SingleTop']    = []
	summary['ST_s']        	= []
	summary['ST_t']    		= []
	summary['ST_tW']       	= []
	summary['STbar_t']      = []
	summary['STbar_tW']     = []
	summary['TotalMC']      = []
	summary['DataToMC']     = []

	# Bin by Bin
	for bin in signal_region_hists['SingleTop'].bins_range():
		ST      = signal_region_hists['SingleTop'].integral(xbin1=bin, xbin2=bin, overflow=True)
		ST_s      = signal_region_hists['ST_s'].integral(xbin1=bin, xbin2=bin, overflow=True)
		ST_t      = signal_region_hists['ST_t'].integral(xbin1=bin, xbin2=bin, overflow=True)
		ST_tW      = signal_region_hists['ST_tW'].integral(xbin1=bin, xbin2=bin, overflow=True)
		STbar_t      = signal_region_hists['STbar_t'].integral(xbin1=bin, xbin2=bin, overflow=True)
		STbar_tW      = signal_region_hists['STbar_tW'].integral(xbin1=bin, xbin2=bin, overflow=True)

		totalMC = ST_s + ST_t + ST_tW + STbar_t + STbar_tW
		if totalMC > 0:
			dataToMC = ST / totalMC
		else:
			dataToMC = -99
		summary['SingleTop'].append(ST)
		summary['ST_s'].append(ST_s)
		summary['ST_t'].append(ST_t)
		summary['ST_tW'].append(ST_tW)
		summary['STbar_t'].append(STbar_t)
		summary['STbar_tW'].append(STbar_tW)
		summary['TotalMC'].append(totalMC)
		summary['DataToMC'].append(dataToMC)

	# Total
	ST      = signal_region_hists['SingleTop'].integral(overflow=True)
	ST_s      = signal_region_hists['ST_s'].integral(overflow=True)
	ST_t      = signal_region_hists['ST_t'].integral(overflow=True)
	ST_tW      = signal_region_hists['ST_tW'].integral(overflow=True)
	STbar_t      = signal_region_hists['STbar_t'].integral(overflow=True)
	STbar_tW      = signal_region_hists['STbar_tW'].integral(overflow=True)

	totalMC = ST_s + ST_t + ST_tW + STbar_t + STbar_tW
	if totalMC > 0:
		dataToMC = ST / totalMC
	else:
		dataToMC = -99
	summary['SingleTop'].append(ST)
	summary['ST_s'].append(ST_s)
	summary['ST_t'].append(ST_t)
	summary['ST_tW'].append(ST_tW)
	summary['STbar_t'].append(STbar_t)
	summary['STbar_tW'].append(STbar_tW)
	summary['TotalMC'].append(totalMC)
	summary['DataToMC'].append(dataToMC)

	order=['SingleTop', 'ST_s', 'ST_t', 'ST_tW', 'STbar_t', 'STbar_tW', 'TotalMC', 'DataToMC']

	d = dict_to_df(summary)
	d = d[order]
	df_to_file(output_folder+channel+'_'+branchName+'.txt', d)
	return

if __name__ == '__main__':
	set_root_defaults()
	args = parse_arguments()

	measurement_config = XSectionConfig( 13 )

	histogram_files = {
		'TTJet'     : measurement_config.ttbar_trees,
		'V+Jets'    : measurement_config.VJets_trees,
		'QCD'       : measurement_config.electron_QCD_MC_trees,
		'SingleTop' : measurement_config.SingleTop_trees,
		'ST_s'      : measurement_config.st_s_trees,
		'ST_t'      : measurement_config.st_t_trees,
		'ST_tW'     : measurement_config.st_tW_trees,
		'STbar_t'   : measurement_config.stbar_t_trees,
		'STbar_tW'  : measurement_config.stbar_tW_trees,
	}

	include_plots = [
		'WPT',
		'MET',
		'ST',
	]

	selection = 'Ref selection'
	output_folder_tmp = '{base}/Nominal/STComparison/{sel}/'.format(
		base = args.output_folder,
		sel = selection.replace(" ", "_"),
	)
	output_folder = output_folder_tmp
	make_folder_if_not_exists(output_folder)
	
	plotHistograms(histogram_files, include_plots, output_folder)

