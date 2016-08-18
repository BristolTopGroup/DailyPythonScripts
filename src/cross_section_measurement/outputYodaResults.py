from tools.file_utilities import make_folder_if_not_exists, read_data_from_JSON
from config.variable_binning import bin_edges


# measurement_config = XSectionConfig(13)

path = 'data/normalisation/background_subtraction/'
variables = bin_edges.keys()

number = {
			'MET' : '5',
			'HT' : '6',
			'ST' : '7',
			'WPT' : '8'
}

kvalues = {
			'MET' : '3',
			'HT' : '3',
			'ST' : '4',
			'WPT' : '3'
}
	
for variable in variables:
	if variable == 'MT': continue
	# if variable != 'HT' : continue
	print variable
	# path_to_JSON = '{path}/{com}TeV/{variable}/xsection_measurement_results/combined/central/normalised_xsection_patType1CorrectedPFMet.txt'
	path_to_JSON = '{path}/{com}TeV/{variable}/xsection_measurement_results/muon/kv{kValue}/central/normalised_xsection_patType1CorrectedPFMet.txt'
	filename = path_to_JSON.format(path = path, com = 8,
	                                   variable = variable,
	                                   kValue = kvalues[variable]
	                                   )

	normalised_xsection_unfolded = read_data_from_JSON( filename )

	xsections = normalised_xsection_unfolded['MADGRAPH']

    # h_normalised_xsection_MADGRAPH = value_error_tuplelist_to_hist( normalised_xsection_unfolded['MADGRAPH'], bin_edges[variable] )

	# file_template = '{path}/{category}/{name}_{channel}_{method}{suffix}.txt'
	# filename = file_template.format(
	# 			path = path_to_JSON,
	# 			category = 'central',
	# 			name = 'normalised_xsection',
	# 			channel = 'combined',
	# 			method = 'RooUnfoldSvd',
	# 			suffix = '',
	# 			)
	# normalised_xsection_unfolded = read_data_from_JSON( filename )

	# # xsections = normalised_xsection_measured_unfolded['unfolded_with_systematics']
	# xsections = normalised_xsection_unfolded['powhegPythia8']


	edges = bin_edges[variable]



	print "# BEGIN YODA_SCATTER2D /CMS_2016_I1473674/d0%s-x01-y01" % number[variable]
	print "Path=/CMS_2016_I1473674/d0%s-x01-y01" % number[variable]
	print "Type=Scatter2D"
	print "# xval   xerr-   xerr+   yval  yerr-   yerr+"

	for i_xsec in range ( 0, len( xsections ) ):
		xsec = xsections[i_xsec][0]
		xsec_error = xsections[i_xsec][1]
		xlow = edges[i_xsec]
		xup = edges[i_xsec+1]
		xwidth = xup - xlow
		xcentre = xlow + xwidth / 2

		line = '{xcentre} {xerr_down} {xerr_up} {y} {yerr_down} {yerr_up}'.format(
			xcentre = xcentre,
			xerr_down = xwidth / 2, 
			xerr_up = xwidth / 2,
			y = xsec,
			yerr_down = xsec_error,
			yerr_up = xsec_error
			)

		print line
	print "# END YODA_SCATTER2D"
	print "\n"
