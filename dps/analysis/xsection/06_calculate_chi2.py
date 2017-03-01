from dps.utils.ROOT_utils import set_root_defaults
from argparse import ArgumentParser
from dps.config.xsection import XSectionConfig
from dps.utils.pandas_utilities import file_to_df, matrix_from_df, read_tuple_from_file, dict_to_df, df_to_file, df_to_latexFile
from dps.config.latex_labels import variables_latex, measurements_latex
import numpy as np
from ROOT import TMath
import pandas as pd 

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



def calcualteChi2ForModels( modelsForComparing, variable, channel, path_to_input, uncertainty_type ):
	# Paths to statistical Covariance/Correlation matrices.
	covariance_filename = '{input_path}/covarianceMatrices/{type}/Total_Covariance_{channel}.txt'.format(input_path=path_to_input, type = uncertainty_type, channel=channel)
	# Convert to numpy matrix and create total
	cov_full = matrix_from_df( file_to_df(covariance_filename) )

	xsections_filename = '{input_path}/xsection_normalised_{channel}_TUnfold.txt'.format(input_path=path_to_input, channel=channel)

	# Collect the cross section measured/unfolded results from dataframes
	xsections = read_tuple_from_file( xsections_filename )
	xsection_unfolded    = [ i[0] for i in xsections['TTJet_unfolded'] ]

	xsectionsOfmodels = {}
	chi2OfModels = {}
	for model in modelsForComparing:
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

def makeLatexTable( chi2, outputPath, channel ):
	models = chi2[chi2.keys()[0]]['Model']
	model_header = '&\t'
	label_header = '&\t'
	for model in models:
		model_header += ' \multicolumn{{2}}{{c|}}{{{model}}} & \t'.format(model=measurements_latex[model])
		label_header += '$\\chi^{2}$ / ndf & p-value &\t'
	model_header = model_header.rstrip().rstrip('&')
	model_header += '\\\\'
	label_header = label_header.rstrip().rstrip('&')
	label_header += '\\\\'

	fullTable = model_header
	fullTable += '\n'
	fullTable += '\\hline\n'
	fullTable += label_header
	fullTable += '\n'
	fullTable += '\\hline\n'
	for var in chi2:
		lineForVar = '{var} &\t'.format(var=variables_latex[var])
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

	fullTable += '\\hline\n'
	print fullTable

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
    args = parser.parse_args()
    return args

if __name__ == '__main__':
	set_root_defaults()
	args = parse_arguments()

	measurement_config      = XSectionConfig( 13 )

	visiblePS               = args.visiblePS
	outputTablePath 		= args.outputTablePath
	modelsForComparing 		= measurement_config.samplesForChi2Comparison

	phase_space = 'FullPS'
	if visiblePS:
	    phase_space = 'VisiblePS'

	channels = [
		'electron', 
		'muon', 
		'combined', 
		# 'combinedBeforeUnfolding',
	]
	unc_type = [
		'normalised',
		'absolute',
	]

	for channel in channels:
		print 'Channel :',channel
		for utype in unc_type:

			chi2ForVariables = {}
			for variable in measurement_config.variables:
				print variable
				path_to_input = '{path}/{com}TeV/{variable}/{phase_space}/central/'
				path_to_input = path_to_input.format(
				    path = args.path, 
				    com = 13,
				    variable = variable,
				    phase_space = phase_space,
				)
				chi2ForVariables[variable] = calculateChi2ForModels( modelsForComparing, variable, channel, path_to_input )

			makeLatexTable( chi2=chi2ForVariables, outputPath=outputTablePath, channel=channel )
