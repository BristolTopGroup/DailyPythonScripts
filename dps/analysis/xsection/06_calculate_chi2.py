from dps.utils.ROOT_utils import set_root_defaults
from argparse import ArgumentParser
from dps.config.xsection import XSectionConfig
from dps.utils.pandas_utilities import file_to_df, matrix_from_df, read_tuple_from_file, dict_to_df, df_to_file, df_to_latexFile
from dps.config.latex_labels import variables_latex, measurements_latex
import numpy as np
from ROOT import TMath
import pandas as pd 
from dps.utils.file_utilities import make_folder_if_not_exists
np.set_printoptions(
	precision = 3,
	linewidth = 400,
)

class chi2Info:
	def __init__(self, chi2, ndf, pValue):
		self.chi2 = chi2
		self.ndf = ndf
		self.pValue = pValue

def calculateChi2(measured_xsection,model_xsection,covariance):
	diff = (measured_xsection - model_xsection)
	chi2 = np.transpose( diff ).dot( np.linalg.inv( covariance ) ).dot( diff )
	ndf = len(measured_xsection)
	prob = TMath.Prob( chi2, len(measured_xsection) )
	return chi2Info( chi2, ndf, prob )

def calculateGlobalChi2(modelsForComparing, chi2_Models):
	'''							  2
	(a, b, c).( . . . ).(a) = Chi
			  ( .COV. ) (b) 
			  ( . . . ) (c)
	Between variables assumed to be uncorrelated I think you can just add the chi2 of the correlated bins 
	and increase the NDF.
	'''
	gChi2 = {}
	for model in modelsForComparing:
		chi2_all, ndf_all = 0, 0
		for var, chi2_Info in chi2_Models.iteritems():
			for m, c, n in zip(chi2_Info['Model'], chi2_Info['Chi2'], chi2_Info['NDF']):
				# changed to exact match to avoid double counting PP8 in PP8+Model
				if m == model:
					chi2_all += c
					ndf_all += n
		prob_all = TMath.Prob( chi2_all, ndf_all )
		gChi2[model] = chi2Info( chi2_all, ndf_all, prob_all )
	return gChi2

def calculateChi2ForModels( modelsForComparing, variable, channel, path_to_input, uncertainty_type ):
	# Paths to statistical Covariance/Correlation matrices.
	covariance_filename = '{input_path}/covarianceMatrices/{type}/Total_Covariance_{channel}.txt'.format(input_path=path_to_input, type = uncertainty_type, channel=channel)

	# Convert to numpy matrix and create total
	cov_full = matrix_from_df( file_to_df(covariance_filename) )

	covariance_filename_withMCTheoryUncertainties = '{input_path}/covarianceMatrices/mcUncertainty/{type}/Total_Covariance_{channel}.txt'.format(input_path=path_to_input, type = uncertainty_type, channel=channel)
	cov_full_withMCTHeoryUncertainties = matrix_from_df( file_to_df(covariance_filename_withMCTheoryUncertainties) )

	xsections_filename = '{input_path}/xsection_{type}_{channel}_TUnfold.txt'.format(input_path=path_to_input, type = uncertainty_type, channel=channel)

	# Collect the cross section measured/unfolded results from dataframes
	xsections = read_tuple_from_file( xsections_filename )
	xsection_unfolded    = [ i[0] for i in xsections['TTJets_unfolded'] ]

	xsectionsOfmodels = {}
	chi2OfModels = {}

	for model in modelsForComparing:
		# print "\nModel is {} for {} {}".format(model, uncertainty_type, channel)
		chi2 = None
		xsectionsOfmodels[model] = None
		if 'withMCTheoryUnc' in model:
			# print "With Theory Uncertainties"
			xsectionsOfmodels[model] = np.array( [ i[0] for i in xsections[model.replace('_withMCTheoryUnc','')] ] )
			chi2 = calculateChi2( xsection_unfolded, xsectionsOfmodels[model], cov_full_withMCTHeoryUncertainties)
		else:
			# print "Without Theory Uncertainties"
			xsectionsOfmodels[model] = np.array( [ i[0] for i in xsections[model] ] )
			chi2 = calculateChi2( xsection_unfolded, xsectionsOfmodels[model], cov_full)
		chi2OfModels[model] = chi2

	chi2OfModels_df = pd.DataFrame( {
		'Variable' : np.array( [variable] * len(modelsForComparing) ),
		'Model' : np.array( [model for model in modelsForComparing] ),
		'Chi2' : np.array( [chi2OfModels[model].chi2 for model in modelsForComparing] ),
		'NDF' : np.array( [chi2OfModels[model].ndf for model in modelsForComparing] ),
		'p-Value' : np.array( [chi2OfModels[model].pValue for model in modelsForComparing] ),
		} )

	output_filename = '{input_path}/chi2OfModels_{channel}_{type}.txt'.format(input_path=path_to_input,channel=channel, type = uncertainty_type)
	df_to_file( output_filename, chi2OfModels_df )

	return chi2OfModels_df

def makeLatexTable( chi2, gChi2, outputPath, channel, crossSectionType ):
	'''
	Make the chi2 latex table
	'''
	models = chi2[chi2.keys()[0]]['Model']
	latexHeader = '\\begin{table}\n'
	if crossSectionType == 'normalised':
		latexHeader += '\t\caption{Results of a $\chi^{2}$ test between the normalised cross sections in data and several MC models.}\n'
		latexHeader += '\t\label{tb:Chi2_normalised}\n'
	elif crossSectionType == 'absolute':
		latexHeader += '\t\caption{Results of a $\chi^{2}$ test between the absolute cross sections in data and several MC models.}\n'
		latexHeader += '\t\label{tb:Chi2_absolute}\n'	
	latexHeader += '\t\centering\n'
	latexHeader += '\t\\scriptsize\n'

	latexContent = ''
	latexContent += makeTableContent(chi2, gChi2, models = ["TTJets_powhegPythia8", "TTJets_powhegPythia8_withMCTheoryUnc"], spacing=True)
	latexContent += makeTableContent(chi2, gChi2, models = ["TTJets_powhegHerwig", "TTJets_amcatnloPythia8", "TTJets_madgraphMLM"])

	latexFooter = '\\end{table}\n'
	latexTable = latexHeader+latexContent+latexFooter

	print latexTable
	make_folder_if_not_exists(outputPath)
	file_template = outputPath + '/chi2_{channel}.tex'.format(channel=channel)
	output_file = open(file_template, 'w')
	output_file.write(latexTable)
	output_file.close()

def makeTableContent(chi2, gChi2, models=[], spacing=False):
	'''
	Add sets of chi2 tables
	'''
	latexHeader = '\t\\begin{tabular}{c'
	for i in range(0,len(models)): latexHeader += 'cc'
	latexHeader += '}\n'
	latexHeader += '\t\t\hline\n'
	latexHeader += '\t\t\hline\n'

	model_header = '\t\t&\t'
	label_header = '\t\t&\t'
	for model in chi2[chi2.keys()[0]]['Model']:
		if model in models:
			model_header += ' \multicolumn{{2}}{{c}}{{{model}}} & \t'.format(model=measurements_latex[model])
			label_header += '$\\chi^{2}$ / ndf & p-value &\t'
	model_header = model_header.rstrip().rstrip('&')
	model_header += '\\\\ \n'
	# if 'TTJets_powhegPythia8_withMCTheoryUnc' in models:
	# 	model_header += '\t\t&\t&\t&\t\multicolumn{2}{c}{including simulation theory uncertainties} \\\\ \n'
	# label_header = label_header.rstrip().rstrip('&')
	# label_header += '\\\\ \n'

	fullTable = latexHeader
	fullTable += model_header
	fullTable += label_header
	fullTable += '\t\t\\hline\n'
	for var in chi2:
		lineForVar = '\t\t{var} &\t'.format(var=variables_latex[var])
		df = chi2[var]
		for model in models:
			info = df.loc[df['Model'] == model].iloc[0]

			pValueToPrint = info['p-Value']
			if pValueToPrint < 0.01:
				pValueToPrint = '$<$ 0.01'
			else:
				pValueToPrint = '{0:.2g}'.format(pValueToPrint)

			lineForVar += '{chi2:.2g} / {ndf} &\t {pValue} &\t'.format(chi2=info['Chi2'], ndf=info['NDF'], pValue=pValueToPrint)
		lineForVar = lineForVar.rstrip().rstrip('&')
		lineForVar += '\\\\'

		fullTable += lineForVar
		fullTable += '\n'
	fullTable += '\t\t\\hline\n'
	
	lineForGChi2 = '\t\t All &\t'
	for model in models:
		pValueToPrint = gChi2[model].pValue
		if pValueToPrint < 0.01:
			pValueToPrint = '$<$ 0.01'
		else:
			pValueToPrint = '{0:.2g}'.format(pValueToPrint)
		lineForGChi2 += '{chi2:.3g} / {ndf} &\t {pValue} &\t'.format(chi2=gChi2[model].chi2, ndf=gChi2[model].ndf, pValue=pValueToPrint)
	lineForGChi2 = lineForGChi2.rstrip().rstrip('&')
	lineForGChi2 += '\\\\'

	fullTable += lineForGChi2
	fullTable += '\n\t\t\hline\n'
	if spacing:
		fullTable += '\t\t\\vspace*{0.2cm} \n'
		fullTable += '\t\t\\newline \n'

	tableFooter = '\t\end{tabular}\n'
	fullTable += tableFooter
	return fullTable


def makeChi2Table( chi2, gChi2, outputPath, channel, crossSectionType ):
	'''
	Make a nice dataframe of chi2 to print to screen for debugging
	'''
	print "- "*50
	print "Chi2 for the {} cross sections measured in the {} channel ".format(crossSectionType, channel)
	vs, ms, cs = [], [], []

	for v, chi2_df in chi2.iteritems():
		for m, c in zip(chi2_df['Model'], chi2_df['Chi2']):
			vs.append(v)
			ms.append(m)
			cs.append(round(c, 2))
	# Adding global if required
	for m, gcs in gChi2.iteritems():
		vs.append('Global')
		ms.append(m)
		cs.append(round(gcs.chi2, 2))

	df = pd.DataFrame({
		'Model': ms,
        'Chi2' : cs,
        'Variable': vs
    })

	df = df.pivot(index='Variable', columns='Model', values='Chi2')
	df_to_file(outputPath+'/chi2_{channel}.txt'.format(channel=channel), df)
	print df
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
        default = 'tables/chi2/',
        help    = "Output path for chi2 tables" 
    )
    parser.add_argument( '--variable','-v', 
        dest    = "varToDO",
        default = None,
        help    = "DEBUG: Test a particular variable" 
    )
    args = parser.parse_args()
    return args

if __name__ == '__main__':
	set_root_defaults()
	args = parse_arguments()

	measurement_config      = XSectionConfig( 13 )

	visiblePS               = args.visiblePS
	outputTablePath 		= args.outputTablePath
	modelsForComparing 		= measurement_config.samplesForChi2Comparison
	if 'TTJets_powhegPythia8' in modelsForComparing:
		modelsForComparing.insert(modelsForComparing.index('TTJets_powhegPythia8')+1,'TTJets_powhegPythia8_withMCTheoryUnc')

	phase_space = 'FullPS'
	if visiblePS:
	    phase_space = 'VisiblePS'

	channels = [
		# 'electron', 
		# 'muon', 
		'combined', 
	]
	unc_type = [
		'normalised',
		'absolute',
	]

	for channel in channels:
		print '-'*100
		print 'Channel :',channel
		for utype in unc_type:

			chi2ForVariables = {}
			for variable in measurement_config.variables:
				if args.varToDO and variable != args.varToDO: continue
				if variable == 'abs_lepton_eta': continue

				path_to_input = '{path}/{com}TeV/{variable}/{phase_space}/central/'
				path_to_input = path_to_input.format(
				    path = args.path, 
				    com = 13,
				    variable = variable,
				    phase_space = phase_space,
				)

				chi2ForVariables[variable] = calculateChi2ForModels( modelsForComparing, variable, channel, path_to_input, utype )

			# Calculate the global chi2
			gChi2 = calculateGlobalChi2( modelsForComparing, chi2ForVariables )
			path_to_output = '{path}/{crossSectionType}/'.format(path=outputTablePath, channel=channel,crossSectionType=utype )
			makeLatexTable( chi2=chi2ForVariables, gChi2=gChi2, outputPath=path_to_output, channel=channel, crossSectionType=utype )
			makeChi2Table( chi2=chi2ForVariables, gChi2=gChi2, outputPath=path_to_output, channel=channel, crossSectionType=utype )
