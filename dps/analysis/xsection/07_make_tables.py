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
		if 'absolute' in crossSectionType:
			line_for_bin = '\t\t{edge_down}-{edge_up} \t& {val} \t& {stat} \t& {sys} \\\\ \n'.format(
				edge_down = '\ensuremath{{ {0:g} }}'.format(bin_edges_vis[variable][bin]),
				edge_up = '\ensuremath{{ {0:g} }}'.format(bin_edges_vis[variable][bin+1]),
				val = '\ensuremath{{ {:.3g} }}'.format(xsections_abs['central'][bin]),
				stat = '\ensuremath{{ {:.3g} }}'.format(xsections_abs['statistical'][bin]),
				sys = '\ensuremath{{ {:.3g} }}'.format(xsections_abs['systematic'][bin]),
				# tot = xsections_rel['total'][bin],
			)
		else:
			line_for_bin = '\t\t{edge_down}-{edge_up} \t& {val} \t& {stat} \t& {sys} \\\\ \n'.format(
				edge_down = '\ensuremath{{ {0:g} }}'.format(bin_edges_vis[variable][bin]),
				edge_up = '\ensuremath{{ {0:g} }}'.format(bin_edges_vis[variable][bin+1]),
				val = '\ensuremath{{ {:.3g} }}'.format(xsections_abs['central'][bin]),
				stat = '\ensuremath{{ {:.3g} }}'.format(xsections_rel['statistical'][bin]),
				sys = '\ensuremath{{ {:.3g} }}'.format(xsections_rel['systematic'][bin]),
				# tot = xsections_rel['total'][bin],
			)

		# REPLACE e^ WITH x10^. ONLY WORKS FOR 1 e^ VALUE IN STRING [TO BE IMPROVED]
		if 'e-' in line_for_bin:
			power = line_for_bin[line_for_bin.find("e-")+1:].split()[0]
			new = '\\times 10^{{ {} }}'.format(power)
			old = 'e'+power
			line_for_bin = line_for_bin.replace(old, new)

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
	return

def makeCondensedSystematicLatexTable(variables, inputPath, input_file_template, outputPath):
	'''
	Make a condensed table of all the (median) systematics
	'''
	d_summarised_syst = {}

	for v in variables:
		xsections_rel = file_to_df(inputPath.replace('VAR_TMP', v)+input_file_template.replace('absolute', 'relative').format(type = 'normalised'))
		d_median_variable = {}
		for col in xsections_rel.columns:
			print xsections_rel[col]
			print np.median(xsections_rel[col])
			median = np.median(xsections_rel[col])*100
			print median
			d_median_variable[col] = median
		d_summarised_syst[v] = d_median_variable
	print d_summarised_syst

	fullTable 		= ''
	latexHeader 	= ''
	latexTitle 		= ''
	latexContent 	= ''
	latexFooter 	= ''

	latexHeader += '\\begin{table}\n'
	# latexHeader += '\t\\tiny\n'
	latexHeader += '\t\centering\n'
	latexHeader += '\t\\begin{tabular}{lccccccc}\n'
	latexHeader += '\t\t\hline\n'
	latexHeader += '\t\t\hline\n'

	latexTitle += '\t\tRelative Uncertainty Source\ensuremath{(\\%)}\t&\t{}\t&\t{}\t&\t{}\t&\t{}\t&\t{}\t&\t{}\t&\t{}\\\\ \n'.format(
		variables_latex['HT'], 
		variables_latex['ST'], 
		variables_latex['MET'], 
		variables_latex['WPT'], 
		variables_latex['lepton_pt'], 
		variables_latex['abs_lepton_eta'], 
		variables_latex['NJets']
	)
	latexTitle += '\t\t\hline\n'

	for col in xsections_rel.columns:
		if 'central' in col or 'systematic' in col or 'statistical' in col: continue
		latexContent += '\t\t{}\t&\t{:.2f}\t&\t{:.2f}\t&\t{:.2f}\t&\t{:.2f}\t&\t{:.2f}\t&\t{:.2f}\t&\t{:.2f}\\\\ \n'.format(
		systematics_latex[col],
		d_summarised_syst['HT'][col], 
		d_summarised_syst['ST'][col], 
		d_summarised_syst['MET'][col], 
		d_summarised_syst['WPT'][col], 
		d_summarised_syst['lepton_pt'][col], 
		d_summarised_syst['abs_lepton_eta'][col], 
		d_summarised_syst['NJets'][col],
	)
	latexContent += '\t\t\hline\n'
	latexContent += '\t\t{}\t&\t{:.2f}\t&\t{:.2f}\t&\t{:.2f}\t&\t{:.2f}\t&\t{:.2f}\t&\t{:.2f}\t&\t{:.2f}\\\\ \n'.format(
		'Total',
		d_summarised_syst['HT']['systematic'], 
		d_summarised_syst['ST']['systematic'], 
		d_summarised_syst['MET']['systematic'], 
		d_summarised_syst['WPT']['systematic'], 
		d_summarised_syst['lepton_pt']['systematic'], 
		d_summarised_syst['abs_lepton_eta']['systematic'], 
		d_summarised_syst['NJets']['systematic'],
	)
	latexContent += '\t\t\hline\n'

	latexFooter += '\t\end{tabular}\n'
	latexFooter += '\t\caption{ Summary}\n'
	latexFooter += '\t\label{tb:syst_condensed_combined}\n'
	latexFooter += '\\end{table}\n'
	latexFooter += '\clearpage'

	fullTable += latexHeader
	fullTable += latexTitle
	fullTable += latexContent
	fullTable += latexFooter

    #########################################################################################################
    ### Write Table
    #########################################################################################################
	make_folder_if_not_exists(outputPath)
	file_template = outputPath + '/CondensedSystematics.tex'
	output_file = open(file_template, 'w')
	output_file.write(fullTable)
	output_file.close()
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
	colHeader += '\t\\begin{tabular}{ccc}\n'
	colHeader += '\t\t\hline\n'
	colHeader += '\t\t\hline\n'
	colHeader += '\t\t  & \t Bin Width \t & \t Resolution \\\\ \n'

	#########################################################################################################
	### Table Content
	#########################################################################################################
	tableContent1 = ''
	tableContent2 = ''
	for variable in measurement_config.variables:
		tableContent = ''
		path_to_file = 'unfolding/13TeV/binning_combined_{}.txt'.format(variable)
		binning_params = file_to_df(path_to_file)

		tableContent += '\t\t\\textbf{{{var}}} \t &   &  \\\\ \n'.format(var=variables_latex[variable])
		tableContent += '\t\t\hline\n'

		for bin in range (len(bin_edges_vis[variable])-1):
			tableContent += '\t\t {edge_down}-{edge_up} \t & {bin_width} & {r} \\\\ \n'.format(
				edge_down = bin_edges_vis[variable][bin], 
				edge_up = bin_edges_vis[variable][bin+1],
				bin_width = bin_edges_vis[variable][bin+1]-bin_edges_vis[variable][bin],
				r = binning_params['Resolution'][bin],
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
			# makeResultLatexTable( xsections_abs=xsections_abs, xsections_rel=xsections_rel, outputPath=path_to_output, variable=variable, crossSectionType=utype )
			makeExpandedSystematicLatexTable( xsections_rel=xsections_rel, outputPath=path_to_output, variable=variable )

	# ########################################################################################################################
	# ### CONDENSED SYSTEMATIC UNCERTAINTIES (MEDIAN VALUES)
	# ########################################################################################################################
	# condensed_path_to_input = path_to_input_template.format(
	#     path = args.path, 
	#     com = 13,
	#     variable = 'VAR_TMP',
	#     phase_space = phase_space,
	# )
	# makeCondensedSystematicLatexTable( measurement_config.variables, condensed_path_to_input, input_file_template, 'tables/systematics/' )


	########################################################################################################################
	### PURITY/STABILITY/RESOLUTION 
	########################################################################################################################
	makeBinningLatexTable()



