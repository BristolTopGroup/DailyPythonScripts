from tools.file_utilities import make_folder_if_not_exists, read_data_from_JSON
make_folder_if_not_exists('hepdata')
from dps.config.variable_binning import bin_edges_vis
from dps.config.latex_labels import variables_latex
from dps.config.xsection import XSectionConfig
from dps.utils.pandas_utilities import file_to_df, matrix_from_df
import os.path
import numpy as np

measurement_config = XSectionConfig(13)

regularisations = {
		'regularised' :	'/scratch/db0268/DPS/DPSTestingGround/DailyPythonScripts/data_X_allFixes/normalisation/background_subtraction/',
		'unregularised' : '/scratch/db0268/DPS/DPSTestingGround/DailyPythonScripts/data_X_allFixes_allTau0/normalisation/background_subtraction/'
		}

normalisations = ['normalised','absolute']

variableHeaders = {
	'MET' : 'name: "{variable}", units: GEV'.format(variable=variables_latex['MET']),
	'HT' : 'name: "{variable}", units: GEV'.format(variable=variables_latex['HT']),
	'ST' : 'name: "{variable}", units: GEV'.format(variable=variables_latex['ST']),
	'WPT' : 'name: "{variable}", units: GEV'.format(variable=variables_latex['WPT']),
	'NJets' : 'name: "{variable}"'.format(variable=variables_latex['NJets']),
	'lepton_pt' : 'name: "{variable}", units: GEV'.format(variable=variables_latex['lepton_pt']),
	'abs_lepton_eta_coarse' : 'name: "{variable}"'.format(variable=variables_latex['abs_lepton_eta_coarse'])
}

for v, h in variableHeaders.iteritems():
	variableHeaders[v] = h.replace('\\','\\\\')

normCrossSectionTemplate = '$\\frac{{1}}{{\sigma}}  \\frac{{d\sigma}}{{d {variable} }}$'
absCrossSectionTemplate = '$\\frac{{d\sigma}}{{d {variable} }}$'
crossSectionLabel = {
	'normalised' : {
		'MET' : 'name: "{label}", units: "{unit}"'.format( label=normCrossSectionTemplate.format(variable=variables_latex['MET']), unit=' $\mathrm{GeV}^{-1}$'),
		'HT' : 'name: "{label}", units: "{unit}"'.format( label=normCrossSectionTemplate.format(variable=variables_latex['HT']), unit=' $\mathrm{GeV}^{-1}$'),
		'ST' : 'name: "{label}", units: "{unit}"'.format( label=normCrossSectionTemplate.format(variable=variables_latex['ST']), unit=' $\mathrm{GeV}^{-1}$'),
		'WPT' : 'name: "{label}", units: "{unit}"'.format( label=normCrossSectionTemplate.format(variable=variables_latex['WPT']), unit=' $\mathrm{GeV}^{-1}$'),
		'NJets' : 'name: "{label}", units: "{unit}"'.format( label=normCrossSectionTemplate.format(variable=variables_latex['NJets']), unit=''),
		'lepton_pt' : 'name: "{label}", units: "{unit}"'.format( label=normCrossSectionTemplate.format(variable=variables_latex['lepton_pt']), unit = ' $\mathrm{GeV}^{-1}$'),
		'abs_lepton_eta_coarse' : 'name: "{label}", units: "{unit}"'.format( label=normCrossSectionTemplate.format(variable=variables_latex['abs_lepton_eta_coarse']), unit=''),
	},
	'absolute' : {
		'MET' : 'name: "{label}", units: "{unit}"'.format( label = absCrossSectionTemplate.format(variable=variables_latex['MET']), unit = ' $\mathrm{pb GeV}^{-1}$' ),
		'HT' : 'name: "{label}", units: "{unit}"'.format( label = absCrossSectionTemplate.format(variable=variables_latex['HT']), unit = ' $\mathrm{pb GeV}^{-1}$'),
		'ST' : 'name: "{label}", units: "{unit}"'.format( label = absCrossSectionTemplate.format(variable=variables_latex['ST']), unit = ' $\mathrm{pb GeV}^{-1}$'),
		'WPT' : 'name: "{label}", units: "{unit}"'.format( label = absCrossSectionTemplate.format(variable=variables_latex['WPT']), unit = ' $\mathrm{pb GeV}^{-1}$'),
		'NJets' : 'name: "{label}", units: "{unit}"'.format( label = absCrossSectionTemplate.format(variable=variables_latex['NJets']), unit = ' pb'),
		'lepton_pt' : 'name: "{label}", units: "{unit}"'.format( label = absCrossSectionTemplate.format(variable=variables_latex['lepton_pt']), unit = ' $\mathrm{pb GeV}^{-1}$'),
		'abs_lepton_eta_coarse' : 'name: "{label}", units: "{unit}"'.format( label = absCrossSectionTemplate.format(variable=variables_latex['abs_lepton_eta_coarse']), unit = ' pb'),
	}
}

for n, vars in crossSectionLabel.iteritems():
	for v, l in vars.iteritems():
		vars[v] = l.replace('\\','\\\\')


variables = [
	'MET',
	'HT',
	'ST',
	'WPT',
	'NJets',
	'lepton_pt',
	'abs_lepton_eta_coarse'
]

for regularisation, path in regularisations.iteritems():
	for variable in measurement_config.variables:
		if variable not in variables:continue
		for normalisation in normalisations:

			input_file 	= "xsection_{normalisation}_combined_TUnfold_summary_absolute.txt".format(normalisation=normalisation)
			path_to_input  = '{path}/13TeV/{variable}/VisiblePS/central/'.format(
				path = path,
				variable = variable,
				)
			unfolded_xsections_with_absolute_uncertainties = file_to_df( path_to_input+input_file )
			xsections = unfolded_xsections_with_absolute_uncertainties['central']
			statistical = unfolded_xsections_with_absolute_uncertainties['statistical']
			systematic = unfolded_xsections_with_absolute_uncertainties['systematic']
			total_uncertainty = np.sqrt( statistical * statistical + systematic * systematic )


			edges = bin_edges_vis[variable]
			outYAML = ''
			outYAML += 'independent_variables:\n'
			outYAML += '- header: {{ {header} }}\n'.format( header=variableHeaders[variable])
			outYAML += '  values:\n'

			for i_xsec in range ( 0, len( xsections ) ):
				outYAML += '  - {{ low: {low}, high: {high} }}\n'.format(low=edges[i_xsec],high=edges[i_xsec+1])

			outYAML += 'dependent_variables:\n'
			outYAML += '- header: {{ {header} }}\n'.format( header=crossSectionLabel[normalisation][variable])
			outYAML += '  qualifiers :\n'
			outYAML += '  - {name: RE, value: P P --> TOP TOPBAR X}\n'
			outYAML += '  - {name: SQRT(S), units: GEV, value: 13000}\n'
			outYAML += '  values :\n'

			for i_xsec in range ( 0, len( xsections ) ):
				outYAML += '  - value: {value}\n'.format(value=xsections[i_xsec])
				outYAML += '    errors:\n'
				outYAML += '    - {{ symerror: {unc}, label: stat }}\n'.format(unc=statistical[i_xsec])
				outYAML += '    - {{ symerror: {unc}, label: sys }}\n'.format(unc=systematic[i_xsec])

			outputFileName = 'hepdata/{normalisation}_xsection_{variable}.yaml'.format(normalisation = normalisation, variable=variable)
			if variable == 'abs_lepton_eta_coarse':
				outputFileName = 'hepdata/{normalisation}_xsection_abs_lepton_eta.yaml'.format(normalisation = normalisation)

			if regularisation == 'unregularised':
				outputFileName = outputFileName.replace('xsection','unregularised_xsection')

			outputFile = open(outputFileName,'w')
			outputFile.write(outYAML)
			outputFile.close()


			# Covariance matrices
			input_file 	= "Total_Covariance_combined.txt".format(normalisation=normalisation)
			path_to_input  = '{path}/13TeV/{variable}/VisiblePS/central/covarianceMatrices/{normalisation}/'.format(
				path = path,
				variable = variable,
				normalisation=normalisation
				)
			covariance = matrix_from_df( file_to_df( path_to_input+input_file ) )

			outYAMLCovariance = 'independent_variables:\n'
			outYAMLCovariance += '- header: {{ {header} }}\n'.format( header=variableHeaders[variable])
			outYAMLCovariance += '  values:\n'

			for i_xsec in range ( 0, len( xsections ) ):
				for j_xsec in range( 0, len(xsections) ):
					outYAMLCovariance += '  - {{ low: {low}, high: {high} }}\n'.format(low=edges[i_xsec],high=edges[i_xsec+1])

			outYAMLCovariance += '- header: {{ {header} }}\n'.format( header=variableHeaders[variable])
			outYAMLCovariance += '  values:\n'

			for i_xsec in range ( 0, len( xsections ) ):
				for j_xsec in range( 0, len(xsections) ):
					outYAMLCovariance += '  - {{ low: {low}, high: {high} }}\n'.format(low=edges[j_xsec],high=edges[j_xsec+1])

			outYAMLCovariance += 'dependent_variables:\n'
			outYAMLCovariance += '- header: {name: Covariance}\n'
			outYAMLCovariance += '  values :\n'

	 		for i_xsec in range ( 0, covariance.shape[0] ):
				for j_xsec in range( 0, covariance.shape[0] ):
					# print '{} {:.5E}'.format( covariance[i_xsec][j_xsec], covariance[i_xsec][j_xsec])
					outYAMLCovariance += '  - {{value: {:.8g} }}\n'.format(covariance[i_xsec][j_xsec])


			outputFileName = 'hepdata/{normalisation}_xsection_{variable}_covariance.yaml'.format(normalisation = normalisation, variable=variable)
			if variable == 'abs_lepton_eta_coarse':
				outputFileName = 'hepdata/{normalisation}_xsection_abs_lepton_eta_covariance.yaml'.format(normalisation = normalisation)

			if regularisation == 'unregularised':
				outputFileName = outputFileName.replace('xsection','unregularised_xsection')

			outputFile = open(outputFileName,'w')
			outputFile.write(outYAMLCovariance)
			outputFile.close()
