from config import XSectionConfig
from copy import deepcopy
from tools.file_utilities import read_xsection_measurement_results_with_errors
from config.variable_binning import variable_bins_latex
from tools.Calculation import calculate_lower_and_upper_PDFuncertainty, calculate_lower_and_upper_systematics
from numpy import median

measurement_config = XSectionConfig( 13 )
translate_options = measurement_config.translate_options

ttbar_theory_systematic_prefix = measurement_config.ttbar_theory_systematic_prefix

phase_space = 'VisiblePS'
method = 'RooUnfoldSvd'

categories_and_prefixes = measurement_config.categories_and_prefixes
categories = deepcopy(categories_and_prefixes.keys())
ttbar_generator_systematics = [ttbar_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
categories.extend(ttbar_generator_systematics)
pdf_uncertainties = ['PDF_total_lower', 'PDF_total_upper']
new_uncertainties = ['QCD_shape']
rate_changing_systematics = measurement_config.rate_changing_systematics_names
all_measurements = deepcopy(categories)
all_measurements.extend(pdf_uncertainties)
all_measurements.extend(new_uncertainties)
all_measurements.extend(rate_changing_systematics)

met_type = translate_options['type1']

allErrors = {}
for variable in variable_bins_latex:
	path_to_JSON = '{path}/{com}TeV/{variable}/{phase_space}/'
	path_to_JSON = path_to_JSON.format(path = 'data/normalisation/background_subtraction/', com = 13,
	                                   variable = variable,
	                                   phase_space = phase_space,
	                                   )

	normalised_xsection_measured_unfolded, normalised_xsection_measured_errors, normalised_xsection_unfolded_errors = read_xsection_measurement_results_with_errors(path_to_JSON, variable, met_type, phase_space, method, 'combined')

	central_values = [ normalised_xsection_measured_unfolded['unfolded'][x][0] for x in range(0,len(normalised_xsection_measured_unfolded['unfolded'])) ]

	for cat in normalised_xsection_unfolded_errors:
		if cat in all_measurements:
			if cat in allErrors.keys():
				allErrors[cat] += [ abs ( a / b ) for a,b in zip(normalised_xsection_unfolded_errors[cat], central_values ) ]
			else:
				allErrors[cat] = [ abs( a / b ) for a,b in zip(normalised_xsection_unfolded_errors[cat], central_values ) ]

# print allErrors
for cat in all_measurements:#['TTJets_NLOgenerator', 'QCD_cross_section-', 'QCD_cross_section+', 'TTJets_hadronisation']:
	maxError = max([abs(x) for x in allErrors[cat]])*100
	medianError = median([abs(x) for x in allErrors[cat]])*100
	print '%s %.2g, %.2g' % (cat, maxError, medianError)
