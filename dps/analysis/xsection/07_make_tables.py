from argparse import ArgumentParser
from dps.config.xsection import XSectionConfig
from dps.utils.pandas_utilities import file_to_df, round_df
from dps.config.latex_labels import variables_latex, systematics_latex
from dps.config.variable_binning import bin_edges_vis
from dps.utils.file_utilities import make_folder_if_not_exists
import numpy as np

def makeResultLatexTable( xsections_abs, xsections_rel, outputPath, variable, crossSectionType ):
	'''
	Generate and write the Latex table for the cross sections
	'''
	fullTable = ''
	unit = ' '
	unit_inv = ' '

	if variable in ['HT', 'ST', 'MET', 'WPT', 'lepton_pt']:
		unit     += '(GeV)'
		unit_inv     += '\\ensuremath{\\text{(GeV)}^{-1}}'

	dxsec 	 = ' \\ensuremath{{ \\frac{{ 1 }}{{ \\text{{d}}\\sigma }} \\frac{{ \\text{{d}}\\sigma }}{{ \\text{{d}}{var} }} }} '.format(var = variables_latex[variable])

    #########################################################################################################
    ### Round XSection Values
    #########################################################################################################
	xsections_rel['statistical'] = xsections_rel['statistical']*100
	xsections_rel['systematic'] = xsections_rel['systematic']*100
	# xsections_abs = round_df(xsections_abs, 2)
	# xsections_rel = round_df(xsections_rel, 2)

    #########################################################################################################
    ### Table Header
    #########################################################################################################
	latexHeader =  '\\begin{table}\n'
	latexHeader += '\t\centering\n'
	latexHeader += '\t\\begin{tabular}{cccc}\n'
	latexHeader += '\t\t\hline\n'
	latexHeader += '\t\t\hline\n'
	latexHeader += '\t\t{var}'.format(var=variables_latex[variable]) + ' \t& ' + dxsec + ' \t& \ensuremath{\pm} Stat. \t& \ensuremath{\pm} Syst. \\\\ \n'
	if 'absolute' in crossSectionType:
		latexHeader += '\t\t'+unit+' \t& '+unit_inv+' \t& (N) \t& (N) \\\\ \n'
	else:
		latexHeader += '\t\t'+unit+' \t& '+unit_inv+' \t& (\%) \t& (\%) \\\\ \n'
	latexHeader += '\t\t\hline\n'

	fullTable += latexHeader

    #########################################################################################################
    ### Table Content
    #########################################################################################################
	for bin in range (len(bin_edges_vis[variable])-1):
		precision = '{0:g}'
		if 'abs_lepton_eta' in variable:
			precision = '{0:.2f}'

		if 'absolute' in crossSectionType:
			line_for_bin = '\t\t{edge_down}-{edge_up} \t& {val} \t& {stat} \t& {sys} \\\\ \n'.format(
				edge_down = precision.format(bin_edges_vis[variable][bin]),
				edge_up = precision.format(bin_edges_vis[variable][bin+1]),
				val = '{:.3g}'.format(xsections_abs['central'][bin]),
				stat = '{:.3g}'.format(xsections_abs['statistical'][bin]),
				sys = '{:.3g}'.format(xsections_abs['systematic'][bin]),
				# tot = xsections_rel['total'][bin],
			)
		else:
			line_for_bin = '\t\t{edge_down}-{edge_up} \t& {val} \t& {stat} \t& {sys} \\\\ \n'.format(
				edge_down = precision.format(bin_edges_vis[variable][bin]),
				edge_up = precision.format(bin_edges_vis[variable][bin+1]),
				val = '{:.3g}'.format(xsections_abs['central'][bin]),
				stat = '{:.3g}'.format(xsections_rel['statistical'][bin]),
				sys = '{:.3g}'.format(xsections_rel['systematic'][bin]),
				# tot = xsections_rel['total'][bin],
			)

		# REPLACE e^0N WITH x10^N. ONLY WORKS FOR 1 e^ VALUE IN STRING [TO BE IMPROVED]
		if 'e-' in line_for_bin:
			print(line_for_bin)
			power = line_for_bin[line_for_bin.find("e-")+1:].split()[0]
			new = '\\times 10^{{ {} }}'.format(power.replace('0', ''))
			old = 'e'+power
			line_for_bin = line_for_bin.replace(old, new)
			print(line_for_bin)

		fullTable += line_for_bin

    #########################################################################################################
    ### Table Footer
    #########################################################################################################
	tableFooter = '\t\t\hline\n'
	tableFooter += '\t\end{tabular}\n'
	if 'absolute' in crossSectionType:
		tableFooter += '\t\caption{{Results of the {type} differential cross sections with absolute uncertainties in the combined channel with respect to {var}.}}\n'.format(
			type 	= crossSectionType,
			var 	= variables_latex[variable],
		)
	else:
		tableFooter += '\t\caption{{Results of the {type} differential cross sections with relative uncertainties in the combined channel with respect to {var}.}}\n'.format(
			type 	= crossSectionType,
			var 	= variables_latex[variable],
		)
	tableFooter += '\t\label{{tb:xsection_{type}_{var}_combined}}\n'.format(
		type 	= crossSectionType,
		var 	= variable,
	)	
	tableFooter += '\\end{table}\n'
	fullTable += tableFooter
	fullTable += '\clearpage'

    #########################################################################################################
    ### Write Table
    #########################################################################################################
	make_folder_if_not_exists(outputPath)
	file_template = outputPath + '/{var}_XSections.tex'.format(var=variable)
	output_file = open(file_template, 'w')
	output_file.write(fullTable)
	output_file.close()
	print 'Written Results +- Stat +- Systematic'.format(variable)

	return

def makeCondensedSystematicLatexTable(variables, inputPath, input_file_template, outputPath, utype):
	'''
	Make a condensed table of all the (median) systematics
	'''
	d_summarised_syst = {}

	for v in variables:
		systematics = file_to_df(inputPath.replace('VAR_TMP', v)+input_file_template.replace('absolute', 'relative').format(type = utype))
		d_median_variable = {}
		d_median_variable['Min'] = {}
		d_median_variable['Max'] = {}
		d_median_variable['Med'] = {}

		for col in systematics.columns:
			minimum = np.min(systematics[col])*100
			maximum = np.max(systematics[col])*100
			median = np.median(systematics[col])*100
			d_median_variable['Min'][col] = minimum
			d_median_variable['Max'][col] = maximum
			d_median_variable['Med'][col] = median
		d_summarised_syst[v] = d_median_variable
	# print d_summarised_syst

	fullTable 		= ''
	latexHeader 	= ''
	latexTitle 		= ''
	latexContent 	= ''
	latexFooter 	= ''

	latexHeader += '\\begin{landscape}\n'
	latexHeader += '\\begin{table}\n'
	latexHeader += '\t\label{{tb:syst_condensed_combined_{}}}\n'.format(utype)
	latexHeader += '\t\caption{{ The upper and lower bounds, in \%, from each source of systematic uncertainty in the {t} differential cross section, over all bins of the measurement for each variable.  The bounds of the total relative uncertainty over all bins is also shown for each variable.}}\n'.format(t=utype)
	# latexHeader += '\t\\tiny\n'
	latexHeader += '\t\centering\n'
	latexHeader += '\t\\footnotesize\n'
	latexHeader += '\t\\begin{tabular}{lccccccc}\n'
	latexHeader += '\t\t\hline\n'
	latexHeader += '\t\t\hline\n'

	latexTitle += '\t\tRelative Uncertainty Source$(\\%)$\t&\t{}\t&\t{}\t&\t{}\t&\t{}\t&\t{}\t&\t{}\t&\t{}\\\\ \n'.format(
		variables_latex['HT'], 
		variables_latex['ST'], 
		variables_latex['MET'], 
		variables_latex['WPT'], 
		variables_latex['lepton_pt'], 
		variables_latex['abs_lepton_eta'], 
		variables_latex['NJets']
	)
	latexTitle += '\t\t\hline\n'

	for col in systematics.columns:
		if 'central' in col or 'systematic' in col or 'statistical' in col: continue

		HT_low 				= d_summarised_syst['HT']['Min'][col] 
		ST_low 				= d_summarised_syst['ST']['Min'][col] 
		MET_low 			= d_summarised_syst['MET']['Min'][col] 
		WPT_low 			= d_summarised_syst['WPT']['Min'][col] 
		lepton_pt_low	 	= d_summarised_syst['lepton_pt']['Min'][col] 
		abs_lepton_eta_low 	= d_summarised_syst['abs_lepton_eta']['Min'][col] 
		NJets_low 			= d_summarised_syst['NJets']['Min'][col]
		HT_high 			= d_summarised_syst['HT']['Max'][col] 
		ST_high 			= d_summarised_syst['ST']['Max'][col] 
		MET_high 			= d_summarised_syst['MET']['Max'][col] 
		WPT_high 			= d_summarised_syst['WPT']['Max'][col] 
		lepton_pt_high	 	= d_summarised_syst['lepton_pt']['Max'][col] 
		abs_lepton_eta_high = d_summarised_syst['abs_lepton_eta']['Max'][col] 
		NJets_high 			= d_summarised_syst['NJets']['Max'][col]

		# If less than 0.1 replace with '<0.1'
		HT_dp_low = '{:.1f}'
		HT_dp_high = ' - {:.1f}'
		ST_dp_low = '{:.1f}'
		ST_dp_high = ' - {:.1f}'
		MET_dp_low = '{:.1f}'
		MET_dp_high = ' - {:.1f}'
		WPT_dp_low = '{:.1f}'
		WPT_dp_high = ' - {:.1f}'
		lepton_pt_dp_low = '{:.1f}'
		lepton_pt_dp_high = ' - {:.1f}'
		abs_lepton_eta_dp_low = '{:.1f}'
		abs_lepton_eta_dp_high = ' - {:.1f}'
		NJets_dp_low = '{:.1f}'
		NJets_dp_high = ' - {:.1f}'

		if HT_low < 0.1:
			HT_dp_low = '{}'
			HT_low = '$<$0.1'
		if HT_high < 0.1:
			HT_dp_high = '{}'
			HT_high = ''
		if ST_low < 0.1:
			ST_dp_low = '{}'
			ST_low = '$<$0.1'
		if ST_high < 0.1:
			ST_dp_high = '{}'
			ST_high = ''
		if MET_low < 0.1:
			MET_dp_low = '{}'
			MET_low = '$<$0.1'
		if MET_high < 0.1:
			MET_dp_high = '{}'
			MET_high = ''
		if WPT_low < 0.1:
			WPT_dp_low = '{}'
			WPT_low = '$<$0.1'
		if WPT_high < 0.1:
			WPT_dp_high = '{}'
			WPT_high = ''
		if lepton_pt_low < 0.1:
			lepton_pt_dp_low = '{}'
			lepton_pt_low = '$<$0.1'
		if lepton_pt_high < 0.1:
			lepton_pt_dp_high = '{}'
			lepton_pt_high = ''
		if abs_lepton_eta_low < 0.1:
			abs_lepton_eta_dp_low = '{}'
			abs_lepton_eta_low = '$<$0.1'
		if abs_lepton_eta_high < 0.1:
			abs_lepton_eta_dp_high = '{}'
			abs_lepton_eta_high = ''
		if NJets_low < 0.1:
			NJets_dp_low = '{}'
			NJets_low = '$<$0.1'
		if NJets_high < 0.1:
			NJets_dp_high = '{}'
			NJets_high = ''

		latexContent_met = '\t\t{{}}\t&\t{{}}\t&\t{ST_dp_low}{ST_dp_high}\t&\t{MET_dp_low}{MET_dp_high}\t&\t{WPT_dp_low}{WPT_dp_high}\t&\t{{}}\t&\t{{}}\t&\t{{}}\\\\ \n'.format(
			ST_dp_low = ST_dp_low,
			ST_dp_high = ST_dp_high,
			MET_dp_low = MET_dp_low,
			MET_dp_high = MET_dp_high,
			WPT_dp_low = WPT_dp_low,
			WPT_dp_high = WPT_dp_high,
		)
		latexContent_all = '\t\t{{}}\t&\t{HT_dp_low}{HT_dp_high}\t&\t{ST_dp_low}{ST_dp_high}\t&\t{MET_dp_low}{MET_dp_high}\t&\t{WPT_dp_low}{WPT_dp_high}\t&\t{lepton_pt_dp_low}{lepton_pt_dp_high}\t&\t{abs_lepton_eta_dp_low}{abs_lepton_eta_dp_high}\t&\t{NJets_dp_low}{NJets_dp_high}\\\\ \n'.format(
			HT_dp_low = HT_dp_low,
			HT_dp_high = HT_dp_high,
			ST_dp_low = ST_dp_low,
			ST_dp_high = ST_dp_high,
			MET_dp_low = MET_dp_low,
			MET_dp_high = MET_dp_high,
			WPT_dp_low = WPT_dp_low,
			WPT_dp_high = WPT_dp_high,
			lepton_pt_dp_low = lepton_pt_dp_low,
			lepton_pt_dp_high = lepton_pt_dp_high,
			abs_lepton_eta_dp_low = abs_lepton_eta_dp_low,
			abs_lepton_eta_dp_high = abs_lepton_eta_dp_high,
			NJets_dp_low = NJets_dp_low,
			NJets_dp_high = NJets_dp_high,
		)

		if col in measurement_config.systematic_group_met:
			latexContent += latexContent_met.format(
				systematics_latex[col],
				'--',
				ST_low,
				ST_high,
				MET_low,
				MET_high,
				WPT_low,
				WPT_high,
				'--',
				'--',
				'--',
			)
		else:
			latexContent += latexContent_all.format(
				systematics_latex[col],
				HT_low, 
				HT_high, 
				ST_low, 
				ST_high, 
				MET_low, 
				MET_high, 
				WPT_low, 
				WPT_high, 
				lepton_pt_low, 
				lepton_pt_high, 
				abs_lepton_eta_low, 
				abs_lepton_eta_high, 
				NJets_low,
				NJets_high,
			)

	latexContent += '\t\t\hline\n'
	latexContent += '\t\t{}\t&\t{:.1f} - {:.1f}\t&\t{:.1f} - {:.1f}\t&\t{:.1f} - {:.1f}\t&\t{:.1f} - {:.1f}\t&\t{:.1f} - {:.1f}\t&\t{:.1f} - {:.1f}\t&\t{:.1f} - {:.1f}\\\\ \n'.format(
		'Total',
		d_summarised_syst['HT']['Min']['systematic'], 
		d_summarised_syst['HT']['Max']['systematic'], 
		d_summarised_syst['ST']['Min']['systematic'], 
		d_summarised_syst['ST']['Max']['systematic'], 
		d_summarised_syst['MET']['Min']['systematic'], 
		d_summarised_syst['MET']['Max']['systematic'], 
		d_summarised_syst['WPT']['Min']['systematic'], 
		d_summarised_syst['WPT']['Max']['systematic'], 
		d_summarised_syst['lepton_pt']['Min']['systematic'], 
		d_summarised_syst['lepton_pt']['Max']['systematic'], 
		d_summarised_syst['abs_lepton_eta']['Min']['systematic'], 
		d_summarised_syst['abs_lepton_eta']['Max']['systematic'], 
		d_summarised_syst['NJets']['Min']['systematic'],
		d_summarised_syst['NJets']['Max']['systematic'],
	)
	latexContent += '\t\t\hline\n'

	latexFooter += '\t\end{tabular}\n'
	latexFooter += '\\end{table}\n'
	latexFooter += '\\end{landscape}\n'
	latexFooter += '\clearpage'

	fullTable += latexHeader
	fullTable += latexTitle
	fullTable += latexContent
	fullTable += latexFooter

    #########################################################################################################
    ### Write Table
    #########################################################################################################
	make_folder_if_not_exists(outputPath)
	if 'normalised' in utype:
		file_template = outputPath + '/CondensedNormalisedSystematics.tex'
	else: 
		file_template = outputPath + '/CondensedAbsoluteSystematics.tex'
	output_file = open(file_template, 'w')
	output_file.write(fullTable)
	output_file.close()
	print 'Written Median Systematics for all variables'
	return


def makeExpandedSystematicLatexTable( xsections_rel, outputPath, variable ):
	'''
	Generate and write the Latex table for the cross sections
	'''
	fullTable = ''
	unit = ' '
	unit_inv = ' '

	if variable in ['HT', 'ST', 'MET', 'WPT', 'lepton_pt']:
		unit     += '(GeV)'
		unit_inv     += '\\ensuremath{\\text{(GeV)}^{-1}}'

	dxsec 	 = ' \\ensuremath{{ \\frac{{ 1 }}{{ \\text{{d}}\\sigma }} \\frac{{ \\text{{d}}\\sigma }}{{ \\text{{d}}{var} }} }} '.format(var = variables_latex[variable])

    #########################################################################################################
    ### Round XSection Values
    #########################################################################################################
	xsections_rel['statistical'] = xsections_rel['statistical']*100
	xsections_rel['systematic'] = xsections_rel['systematic']*100

	ncols = 'c'*(len(bin_edges_vis[variable]))
    #########################################################################################################
    ### Table Header
    #########################################################################################################

	latexHeader =  '\\begin{landscape}\n'
	latexHeader += '\\begin{table}\n'
	latexHeader += '\t\\tiny\n'
	latexHeader += '\t\centering\n'
	latexHeader += '\t\\begin{{tabular}}{{{}}}\n'.format(ncols)
	latexHeader += '\t\t\hline\n'
	latexHeader += '\t\t\hline\n'

	colHeader = '\t\t{var} '.format(var=variables_latex[variable])
	for bin in range (len(bin_edges_vis[variable])-1):
			colHeader += '\t & \t {edge_down}-{edge_up}'.format(
				edge_down = bin_edges_vis[variable][bin], 
				edge_up = bin_edges_vis[variable][bin+1],
			)
	colHeader += '\\\\ \n'
	colHeader += '\t\t\hline\n'

	fullTable += latexHeader
	fullTable += colHeader

    #########################################################################################################
    ### Table Content
    #########################################################################################################
	for col in xsections_rel.columns:
		if 'central' in col or 'systematic' in col or 'statistical' in col: continue
		line_for_bin = '\t\t'+col.replace('_', '\_')
		for bin in range (len(bin_edges_vis[variable])-1): 
			xsec = xsections_rel[col][bin]*100
			line_for_bin += '\t & \t \ensuremath{{ {:.2g} }}'.format(xsec)
		line_for_bin += ' \\\\ \n'

	# 	# REPLACE e^ WITH x10^. ONLY WORKS FOR 1 e^ VALUE IN STRING [TO BE IMPROVED]
	# 	if 'e-' in line_for_bin:
	# 		power = line_for_bin[line_for_bin.find("e-")+1:].split()[0]
	# 		new = '\\times 10^{{ {} }}'.format(power)
	# 		old = 'e'+power
	# 		line_for_bin = line_for_bin.replace(old, new)

		fullTable += line_for_bin

    #########################################################################################################
    ### Table Footer
    #########################################################################################################
	tableFooter = '\t\t\hline\n'
	tableFooter += '\t\end{tabular}\n'
	tableFooter += '\t\caption{{ Breakdown of the relative uncertainties in the combined channel with respect to {var}.}}\n'.format( var = variables_latex[variable] )
	tableFooter += '\t\label{{tb:syst_{var}_combined}}\n'.format( var = variable )	
	tableFooter += '\\end{table}\n'
	tableFooter += '\\end{landscape}\n'
	fullTable += tableFooter
	fullTable += '\clearpage'

    #########################################################################################################
    ### Write Table
    #########################################################################################################
	make_folder_if_not_exists(outputPath)
	file_template = outputPath + '/{var}_ExpandedXSections.tex'.format(var=variable)
	output_file = open(file_template, 'w')
	output_file.write(fullTable)
	output_file.close()
	print 'Written Full Systematics for {}'.format(variable)

	return


def makeBinningLatexTable():
	'''
	Generate Binning Latex Tables
	'''
	fullTable = ''

	#########################################################################################################
	### Table Header
	#########################################################################################################
	tableHeader =  ''
	tableHeader += '\\begin{table}\n'
	tableHeader += '\t\caption{ A table showing the bin size and resolution in the calculation of the bin sizes for all variables in the combined channel }\n'
	tableHeader += '\t\label{tb:binning_combined}\n'	
	tableHeader += '\t\\tiny\n'
	tableHeader += '\t\centering\n'

	colHeader =  ''
	colHeader += '\t\\begin{tabular}{cccc}\n'
	colHeader += '\t\t\hline\n'
	colHeader += '\t\t\hline\n'
	colHeader += '\t\t  & \t Bin Width \t & \t Resolution \t & $\\frac{\\text{Resolution}}{\\text{Bin Width}}$\\\\ \n'

	#########################################################################################################
	### Table Content
	#########################################################################################################
	tableContent1 = ''
	tableContent2 = ''
	for variable in measurement_config.variables:

		tableContent = ''
		path_to_file = 'unfolding/13TeV/binning_combined_{}.txt'.format(variable)
		binning_params = file_to_df(path_to_file)

		tableContent += '\t\t\\textbf{{{var}}} \t &   &	  & \\\\ \n'.format(var=variables_latex[variable])
		tableContent += '\t\t\hline\n'

		for bin in range (len(bin_edges_vis[variable])-1):
			bin_low = bin_edges_vis[variable][bin]
			bin_high = bin_edges_vis[variable][bin+1]
			bin_width = bin_high - bin_low
			bin_res = binning_params['res'][bin]
			bin_row = bin_res / bin_width

			# Resolution of NJets is always 1
			if 'NJets' in variable:
				bin_res = 1
				bin_row = bin_res / bin_width

			# Insert different rounding here for each variable
			bin_dp = ''
			res_dp = ':.1f'
			row_dp = ':.1f'
			if 'abs_lepton_eta' in variable:
				bin_dp = ':.2f'

			# Tuning table to different d.p for each variable and replacing 0.0 with <0.1.
			tableContent_tmp = ''
			if bin_row < 0.1: 
				bin_row = '$<$ 0.1'
				tableContent_tmp = '\t\t {{{bin_dp}}} - {{{bin_dp}}} \t & \t {{{bin_dp}}} \t & \t {{{res_dp}}} \t & \t {{}} \\\\ \n'.format(
					bin_dp = bin_dp,
					res_dp = res_dp,
				)
				if bin_res < 0.1:
					bin_res = '$<$ 0.1'
					tableContent_tmp = '\t\t {{{bin_dp}}} - {{{bin_dp}}} \t & \t {{{bin_dp}}} \t & \t {{}} \t & \t {{}} \\\\ \n'.format(
						bin_dp = bin_dp,
						res_dp = res_dp,
					)
			else:
				tableContent_tmp = '\t\t {{{bin_dp}}} - {{{bin_dp}}} \t & \t {{{bin_dp}}} \t & \t {{{res_dp}}} \t & \t {{{row_dp}}} \\\\ \n'.format(
					bin_dp = bin_dp,
					res_dp = res_dp,
					row_dp = row_dp,
				)
			
			# Edge Down - Edge Up | Bin Width | Resolution | Resolution / Bin Width
			tableContent += tableContent_tmp.format(
				bin_low, 
				bin_high,
				bin_width,
				bin_res,
				bin_row,
			)

		# For splitting into two tables
		if variable in ['HT', 'ST', 'MET', 'WPT']: tableContent1 += tableContent
		else:  tableContent2 += tableContent

	#########################################################################################################
	### Table Footer
	#########################################################################################################
	colFooter 	= ''
	colFooter 	+= '\t\t\hline\n'
	colFooter 	+= '\t\end{tabular}\n'
	tableFooter = ''
	tableFooter += '\\end{table}\n'
	tableFooter += '\clearpage\n'

	fullTable += tableHeader
	fullTable += colHeader
	fullTable += tableContent1
	fullTable += colFooter
	fullTable += colHeader
	fullTable += tableContent2
	fullTable += colFooter
	fullTable += tableFooter

	#########################################################################################################
	### Write Table
	#########################################################################################################
	outputPath = 'tables/binning/'
	make_folder_if_not_exists(outputPath)
	file_template = outputPath + '/Table_BinningParams.tex'
	output_file = open(file_template, 'w')
	output_file.write(fullTable)
	output_file.close()
	print "Written Binning Table"
	return



def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument( "-p", "--path", 
        dest    = "path", 
        default = 'data/normalisation/background_subtraction/',
        help    = "set path to files containing dataframes" 
    )
    parser.add_argument( '--visiblePS', 
        dest    = "visiblePS", 
        action  = "store_true",
        help    = "Unfold to visible phase space" 
    )
    parser.add_argument( '--outputTablePath','-o', 
        dest    = "outputTablePath",
        default = 'tables/xsections/',
        help    = "Output path for chi2 tables" 
    )
    args = parser.parse_args()
    return args

if __name__ == '__main__':
	args = parse_arguments()

	measurement_config      = XSectionConfig( 13 )
	visiblePS               = args.visiblePS
	outputTablePath 		= args.outputTablePath

	phase_space = 'FullPS'
	if visiblePS:
		phase_space = 'VisiblePS'

	unc_type = [
		'normalised',
		'absolute',
	]

	input_file_template 	= "xsection_{type}_combined_TUnfold_summary_absolute.txt"
	path_to_input_template  = '{path}/{com}TeV/{variable}/{phase_space}/central/'
	path_to_output_template = '{path}/{crossSectionType}/'
	for utype in unc_type:
		for variable in measurement_config.variables:
			print "Writing the {type} {var} cross sections to Latex Tables".format(type = utype, var=variable)
			path_to_output = path_to_output_template.format(
				path=outputTablePath, 
				crossSectionType=utype,
			)
			path_to_input = path_to_input_template.format(
			    path = args.path, 
			    com = 13,
			    variable = variable,
			    phase_space = phase_space,
			)

			# Read cross sections and write tables
			xsections_abs = file_to_df(path_to_input+input_file_template.format(type = utype))
			xsections_rel = file_to_df(path_to_input+input_file_template.replace('absolute', 'relative').format(type = utype))
			
			########################################################################################################################
			### RESULT +- STAT +- SYST
			########################################################################################################################
			makeResultLatexTable( xsections_abs=xsections_abs, xsections_rel=xsections_rel, outputPath=path_to_output, variable=variable, crossSectionType=utype )
			
			########################################################################################################################
			### EXPANDED SYSTEMATIC UNCERTAINTIES (MEDIAN VALUES)
			########################################################################################################################
			makeExpandedSystematicLatexTable( xsections_rel=xsections_rel, outputPath=path_to_output, variable=variable )

		########################################################################################################################
		### CONDENSED SYSTEMATIC UNCERTAINTIES (MEDIAN VALUES)
		########################################################################################################################
		condensed_path_to_input = path_to_input_template.format(
		    path = args.path, 
		    com = 13,
		    variable = 'VAR_TMP',
		    phase_space = phase_space,
		)
		makeCondensedSystematicLatexTable( measurement_config.variables, condensed_path_to_input, input_file_template, 'tables/systematics/', utype )

	########################################################################################################################
	### PURITY/STABILITY/RESOLUTION 
	########################################################################################################################
	makeBinningLatexTable()



