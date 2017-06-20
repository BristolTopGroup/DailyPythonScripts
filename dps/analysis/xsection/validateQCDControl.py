from dps.utils.file_utilities import get_files_in_path, read_data_from_JSON
from dps.utils.measurement import Measurement
from dps.utils.ROOT_utils import set_root_defaults
from dps.utils.hist_utilities import clean_control_region
from dps.config.xsection import XSectionConfig
from rootpy.plotting import Canvas, Pad
from dps.utils.file_utilities import make_folder_if_not_exists
from dps.config.latex_labels import variables_latex, variables_NonLatex
from uncertainties import ufloat
import ROOT as r

from dps.utils.pandas_utilities import file_to_df
import matplotlib.pyplot as plt
import rootpy.plotting.root2matplotlib as rplt
from dps.config import CMS
import matplotlib.gridspec as gridspec

plt.rc('text', usetex=True)

def getControlRegionHistogramsFromFile(file):
	config = read_data_from_JSON(file)
	measurement = Measurement( config )
	return measurement.cr_histograms

def rebinHists( hists ):
	for h in hists:
		hists[h].Rebin(2)

set_root_defaults( set_batch=True)

measurement_config  = XSectionConfig( 13 )

channel =  ['electron', 'muon']

# for variable in measurement_config.variables:
# 	print variable

# 	central_control_histograms_path = 'data/normalisation/background_subtraction/13TeV/{var}/VisiblePS/central/normalisation_{channel}.txt'.format(
# 		var=variable,
# 		channel=ch,
# 	)
# 	other_control_histograms_path = central_control_histograms_path.replace('central', 'QCD_other_control_region')

# 	central_control_histograms_path = file_to_df(central_control_histograms_path)
# 	other_control_histograms_path = file_to_df(other_control_histograms_path)

for ch in channel:
	for variable in measurement_config.variables:
		print variable
		measurement_filepath = 'config/measurements/background_subtraction/13TeV/{channel}/{var}/VisiblePS/'.format(var=variable, channel=ch)

		# Get all config files in measurement_filepath
		central_file = measurement_filepath + 'central.json' 
		other_qcd_control_file = measurement_filepath + 'QCD_other_control_region.json' 

		central_control_histograms = getControlRegionHistogramsFromFile(central_file)
		other_control_histograms = getControlRegionHistogramsFromFile(other_qcd_control_file)

		# rebinHists( central_control_histograms )
		# rebinHists( other_control_histograms )
		qcd_from_data_in_central = clean_control_region(
		    central_control_histograms,
		    subtract=['TTBar', 'V+Jets', 'SingleTop']
		)

		qcd_mc_integral_in_central, u_central = central_control_histograms['QCD'].integral(overflow=True, error=True)
		qcd_mc_integral_in_central = ufloat( qcd_mc_integral_in_central, u_central )

		qcd_from_data_in_other = clean_control_region(
		    other_control_histograms,
		    subtract=['TTBar', 'V+Jets', 'SingleTop']
		)

		qcd_mc_integral_in_other, u_other = other_control_histograms['QCD'].integral(overflow=True, error=True)
		qcd_mc_integral_in_other = ufloat( qcd_mc_integral_in_other, u_other)

		transfer_from_central_to_other = qcd_mc_integral_in_other / qcd_mc_integral_in_central

		print 'Transfer factor :', transfer_from_central_to_other

		qcd_estimate_from_central = qcd_from_data_in_central.Clone('estimate')

		# transferFactorHist = qcd_estimate_from_central.Clone('transferFactor')
		# for i in range(0,transferFactorHist.GetNbinsX()+1):
		# 	transferFactorHist.SetBinContent(i,transfer_from_central_to_other.nominal_value)
		# 	transferFactorHist.SetBinError(i, transfer_from_central_to_other.std_dev)

		qcd_estimate_from_central.Scale(transfer_from_central_to_other.nominal_value)
		# qcd_estimate_from_central.Multiply( transferFactorHist )


		fig = plt.figure( figsize = ( 20, 16 ), dpi = 400, facecolor = 'white' )

		gs = gridspec.GridSpec( 2, 1, height_ratios = [5, 2] )
		ax = plt.subplot( gs[0] )

		template = '%.1f fb$^{-1}$ (%d TeV)'
		label = template % ( measurement_config.new_luminosity/1000., measurement_config.centre_of_mass_energy)
		plt.title( label,loc='right', **CMS.title )

		ax.minorticks_on()
		ax.xaxis.labelpad = 12
		ax.yaxis.labelpad = 12
		plt.tick_params( **CMS.axis_label_major )
		plt.tick_params( **CMS.axis_label_minor )

		qcd_from_data_in_other.linewidth = 8
		qcd_from_data_in_other.markersize = 4
		qcd_from_data_in_other.color = 'blue'
		qcd_from_data_in_other.linestyle = 'solid'

		qcd_estimate_from_central.linewidth = 8
		qcd_estimate_from_central.markersize = 4
		qcd_estimate_from_central.color = 'green'
		qcd_estimate_from_central.linestyle = 'dashed'

		other_control_histograms['QCD'].linewidth = 8
		other_control_histograms['QCD'].markersize = 4
		other_control_histograms['QCD'].color = 'red'
		other_control_histograms['QCD'].linestyle = 'dotted'

		rplt.hist(qcd_from_data_in_other, stacked=False, axes = ax, label = 'Background subtracted QCD Data in alternate CR')
		rplt.hist(qcd_estimate_from_central, stacked=False, axes = ax, label = 'QCD estimate from the nominal CR')
		rplt.hist(other_control_histograms['QCD'], stacked=False, axes = ax, label = 'QCD MC in alternate CR')
		rplt.errorbar(qcd_from_data_in_other, axes = ax, label = '')
		rplt.errorbar(qcd_estimate_from_central, axes = ax, label = '')
		rplt.errorbar(other_control_histograms['QCD'], axes = ax, label = '')

		leg = plt.legend(
			loc='best',
			prop = {'size':26},	
		)
		leg.draw_frame(False)	
		plt.ylabel( 'Events', CMS.y_axis_title)

		ax2 = plt.subplot( gs[1] )
		plt.setp( ax.get_xticklabels(), visible = False )

		ax2.minorticks_on()
		ax2.xaxis.labelpad = 12
		ax2.yaxis.labelpad = 12
		ax2.set_ylim( ymin = 0, ymax = 2 )

		plt.tick_params( **CMS.axis_label_major )
		plt.tick_params( **CMS.axis_label_minor )

		ratio = qcd_from_data_in_other / qcd_estimate_from_central
		ratio.linewidth = 4
		ratio.color = 'blue'
		ratio.linestyle = 'solid'
		rplt.hist(ratio, axes = ax2)

		x_title = r''
		x_title += variables_latex[variable]
		if variable in ['HT', 'MET', 'WPT', 'ST', 'lepton_pt']:
			x_title += ' [GeV]'
		plt.ylabel( r'\ensuremath{ \frac{ Data }{ Estimate } }', CMS.y_axis_title)
		plt.xlabel( x_title, CMS.x_axis_title )

		plt.tight_layout()

		outputFileName = 'plots/QCDvalidation/{var}_{channel}.pdf'.format( var=variable, channel=ch )
		fig.savefig(outputFileName)
