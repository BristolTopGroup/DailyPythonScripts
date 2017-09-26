from tools.file_utilities import make_folder_if_not_exists, read_data_from_JSON
from dps.config.variable_binning import bin_edges_vis
from dps.config.xsection import XSectionConfig
from dps.utils.pandas_utilities import file_to_df

import numpy as np

measurement_config = XSectionConfig(13)

path = '/storage/ec6821/DailyPythonScripts/new/DailyPythonScripts/data/normalisation/background_subtraction/'

normalised_number = {
			'MET' : '01',
			'HT' : '02',
			'ST' : '03',
			'WPT' : '04',
			'NJets' : '05',
			'lepton_pt' : '06',
			'abs_lepton_eta_coarse' : '07',
}

absolute_number = {
			'MET' : '08',
			'HT' : '09',
			'ST' : '10',
			'WPT' : '11',
			'NJets' : '12',
			'lepton_pt' : '13',
			'abs_lepton_eta_coarse' : '14',
}

print '---> Normalised cross sections\n'

for variable in measurement_config.variables:
	if variable not in normalised_number.keys(): continue

	input_file 	= "xsection_normalised_combined_TUnfold_summary_absolute.txt"
	path_to_input  = '{path}/13TeV/{variable}/VisiblePS/central/'.format(
		path = path,
		variable = variable,
		)

	normalised_unfolded_xsections_with_absolute_uncertainties = file_to_df( path_to_input+input_file )
	xsections = normalised_unfolded_xsections_with_absolute_uncertainties['central']
	statistical = normalised_unfolded_xsections_with_absolute_uncertainties['statistical']
	systematic = normalised_unfolded_xsections_with_absolute_uncertainties['systematic']
	total_uncertainty = np.sqrt( statistical * statistical + systematic * systematic )


	edges = bin_edges_vis[variable]


	print "# BEGIN YODA_SCATTER2D /CMS_2017_PAS_TOP_16_014/d%s-x01-y01" % normalised_number[variable]
	print "Path=/CMS_2017_PAS_TOP_16_014/d%s-x01-y01" % normalised_number[variable]
	print "Type=Scatter2D"
	print "# xval   xerr-   xerr+   yval  yerr-   yerr+"

	for i_xsec in range ( 0, len( xsections ) ):
		xsec = xsections[i_xsec]
		xsec_unc = total_uncertainty[i_xsec]
		xlow = edges[i_xsec]
		xup = edges[i_xsec+1]
		xwidth = xup - xlow
		xcentre = xlow + xwidth / 2

		line = '{xcentre} {xerr_down} {xerr_up} {y} {yerr_down} {yerr_up}'.format(
			xcentre = xcentre,
			xerr_down = xwidth / 2, 
			xerr_up = xwidth / 2,
			y = xsec,
			yerr_down = xsec_unc,
			yerr_up = xsec_unc
			)

		print line
	print "# END YODA_SCATTER2D"
	print "\n"

print '---> Absolute cross sections\n'

for variable in measurement_config.variables:
	if variable not in absolute_number.keys(): continue

	input_file 	= "xsection_absolute_combined_TUnfold_summary_absolute.txt"
	path_to_input  = '{path}/13TeV/{variable}/VisiblePS/central/'.format(
		path = path,
		variable = variable,
		)

	absolute_unfolded_xsections_with_absolute_uncertainties = file_to_df( path_to_input+input_file )
	xsections = absolute_unfolded_xsections_with_absolute_uncertainties['central']
	statistical = absolute_unfolded_xsections_with_absolute_uncertainties['statistical']
	systematic = absolute_unfolded_xsections_with_absolute_uncertainties['systematic']
	total_uncertainty = np.sqrt( statistical * statistical + systematic * systematic )


	edges = bin_edges_vis[variable]


	print "# BEGIN YODA_SCATTER2D /CMS_2017_PAS_TOP_16_014/d%s-x01-y01" % absolute_number[variable]
	print "Path=/CMS_2017_PAS_TOP_16_014/d%s-x01-y01" % absolute_number[variable]
	print "Type=Scatter2D"
	print "# xval   xerr-   xerr+   yval  yerr-   yerr+"

	for i_xsec in range ( 0, len( xsections ) ):
		xsec = xsections[i_xsec]
		xsec_unc = total_uncertainty[i_xsec]
		xlow = edges[i_xsec]
		xup = edges[i_xsec+1]
		xwidth = xup - xlow
		xcentre = xlow + xwidth / 2

		line = '{xcentre} {xerr_down} {xerr_up} {y} {yerr_down} {yerr_up}'.format(
			xcentre = xcentre,
			xerr_down = xwidth / 2, 
			xerr_up = xwidth / 2,
			y = xsec,
			yerr_down = xsec_unc,
			yerr_up = xsec_unc
			)

		print line
	print "# END YODA_SCATTER2D"
	print "\n"

print '---> Powheg Pythia8 normalised cross section\n'
for variable in measurement_config.variables:
	if variable not in normalised_number.keys(): continue

	input_file 	= "xsection_normalised_combined_TUnfold.txt"
	path_to_input  = '{path}/13TeV/{variable}/VisiblePS/central/'.format(
		path = path,
		variable = variable,
		)

	normalised_unfolded_xsections = file_to_df( path_to_input+input_file )
	xsections_PP8 = normalised_unfolded_xsections['TTJets_powhegPythia8']
	edges = bin_edges_vis[variable]

	print "# BEGIN YODA_SCATTER2D /CMS_2017_PAS_TOP_16_014/d%s-x01-y01" % normalised_number[variable]
	print "Path=/CMS_2017_PAS_TOP_16_014/d%s-x01-y01" % normalised_number[variable]
	print "Type=Scatter2D"
	print "# xval   xerr-   xerr+   yval  yerr-   yerr+"

	for i_xsec in range ( 0, len( xsections_PP8 ) ):
		xsec = xsections_PP8[i_xsec]
		xsec_unc = 0
		xlow = edges[i_xsec]
		xup = edges[i_xsec+1]
		xwidth = xup - xlow
		xcentre = xlow + xwidth / 2

		line = '{xcentre} {xerr_down} {xerr_up} {y} {yerr_down} {yerr_up}'.format(
			xcentre = xcentre,
			xerr_down = xwidth / 2, 
			xerr_up = xwidth / 2,
			y = xsec,
			yerr_down = xsec_unc,
			yerr_up = xsec_unc
			)

		print line
	print "# END YODA_SCATTER2D"
	print "\n"

print '---> Powheg Pythia8 absolute cross section\n'
for variable in measurement_config.variables:
	if variable not in absolute_number.keys(): continue

	input_file 	= "xsection_absolute_combined_TUnfold.txt"
	path_to_input  = '{path}/13TeV/{variable}/VisiblePS/central/'.format(
		path = path,
		variable = variable,
		)

	absolute_unfolded_xsections = file_to_df( path_to_input+input_file )
	xsections_PP8 = absolute_unfolded_xsections['TTJets_powhegPythia8']
	edges = bin_edges_vis[variable]

	print "# BEGIN YODA_SCATTER2D /CMS_2017_PAS_TOP_16_014/d%s-x01-y01" % absolute_number[variable]
	print "Path=/CMS_2017_PAS_TOP_16_014/d%s-x01-y01" % absolute_number[variable]
	print "Type=Scatter2D"
	print "# xval   xerr-   xerr+   yval  yerr-   yerr+"

	for i_xsec in range ( 0, len( xsections_PP8 ) ):
		xsec = xsections_PP8[i_xsec]
		xsec_unc = 0
		xlow = edges[i_xsec]
		xup = edges[i_xsec+1]
		xwidth = xup - xlow
		xcentre = xlow + xwidth / 2

		line = '{xcentre} {xerr_down} {xerr_up} {y} {yerr_down} {yerr_up}'.format(
			xcentre = xcentre,
			xerr_down = xwidth / 2, 
			xerr_up = xwidth / 2,
			y = xsec,
			yerr_down = xsec_unc,
			yerr_up = xsec_unc
			)

		print line
	print "# END YODA_SCATTER2D"
	print "\n"
