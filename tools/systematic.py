from __future__ import division, print_function
from tools.file_utilities import read_data_from_JSON, write_data_to_JSON
from copy import deepcopy
from math import sqrt

def write_normalised_xsection_measurement(options, measurement, measurement_unfolded, summary = '' ):
    '''
    Writes the list of normalised measurements and normalised unfolded measurements of the form: 
    [Central Value, Lower Systemtic, Upper Systematic] to a json. Different combinations of 
    systematic uncertainty are stored as different json by appending different 'summary'
    '''
    path_to_JSON=options['path_to_JSON']
    method=options['method']
    channel=options['channel']

    output_file = '{path_to_JSON}/TEST/central/normalised_xsection_{channel}_{method}_with_errors.txt'
    output_file = output_file.format(
                    path_to_JSON = path_to_JSON,
                    channel = channel,
                    method = method,
                    )
    
    if not summary == '':
        output_file = output_file.replace( 'with_errors', summary + '_errors' )
    
    output = {'TTJet_measured':measurement, 'TTJet_unfolded': measurement_unfolded}
    
    write_data_to_JSON( output, output_file )

    print("Data written to : ", output_file)

# def print_systematic_categories(all_uncertainties):
#     '''
#     Allows for the contents of each systematic category to be printed to the terminal
#     '''
#     for key, list_of_uncertainties in all_uncertainties.iteritems():
#         print("The {key} uncertainty group contains :\n{list_of_uncertainties}\n".format(
#             key=key, 
#             list_of_uncertainties=list_of_uncertainties, 
#             ) 
#         )
#     return

def append_PDF_uncertainties(all_systematics):
    '''
    Replace 'PDF' entry in list of all systematics with actual PDF variations
    '''
    variation = []
    for index in xrange (0, 100):
        variation.append('PDFWeights_'+str(index))
    all_systematics['PDF'] = variation
    return all_systematics

def read_normalised_xsection_measurement(options, category):
    '''
    Returns the normalised measurement and normalised unfolded measurement for 
    the file associated with the variable under study
    '''
    # print(options['channel'])
    variable=options['variable']
    variables_no_met=options['variables_no_met']
    met_specific_systematics=options['met_specific_systematics']
    path_to_JSON=options['path_to_JSON']
    method=options['method']
    channel=options['channel']
    filename = '{path}/{category}/normalised_xsection_{channel}_{method}.txt'
    # Disregarding Met Uncertainties if variable does not use MET
    if (category in met_specific_systematics) and (variable in variables_no_met):
        filename = filename.format(
            path = path_to_JSON,
            channel = channel,
            category = 'central',
            method = method,
        )
    else:
        filename = filename.format(
            path = path_to_JSON,
            channel = channel,
            category = category,
            method = method
        )
    # print(filename) 
    normalised_xsection = read_data_from_JSON( filename )
    measurement = normalised_xsection['TTJet_measured']#should this be measured without fakes???
    measurement_unfolded = normalised_xsection['TTJet_unfolded']
    return measurement, measurement_unfolded  

def read_normalised_xsection_systematics(options, variation, isPDF=False):
    '''
    Returns the list of normalised measurements and normalised unfolded measurements 
    for each systematic category
    '''
    systematics = {}
    systematics_unf = {}

    if isPDF:
        for PDF_Weight in variation:
            pdf_weight, pdf_weight_unf = read_normalised_xsection_measurement(options, PDF_Weight)
            systematics[PDF_Weight] = pdf_weight
            systematics_unf[PDF_Weight] = pdf_weight_unf  
    else:
        upper_variation = variation[0]
        lower_variation = variation[1]
        systematic_up, systematic_up_unf = read_normalised_xsection_measurement(options, upper_variation)
        systematic_down, systematic_down_unf = read_normalised_xsection_measurement(options, lower_variation)
        systematics['lower'] = systematic_down
        systematics['upper'] = systematic_up        
        systematics_unf['lower'] = systematic_down_unf
        systematics_unf['upper'] = systematic_up_unf

    systematics = get_systematic_measured_values_only(options, systematics)   
    systematics_unf = get_systematic_measured_values_only(options, systematics_unf)   
    return systematics, systematics_unf

def get_systematic_measured_values_only(options, syst_x_secs_and_errs):
    '''
    When retreiveing systematic uncertainties they come in form [Value, Error]. 
    This strips the Errors.
    '''
    number_of_bins=options['number_of_bins']
    for variation, x_sec_and_error in syst_x_secs_and_errs.iteritems():
        for bin_i in xrange(number_of_bins):
            x_sec = x_sec_and_error[bin_i][0]
            x_sec_and_error[bin_i] = x_sec
    return syst_x_secs_and_errs


def get_normalised_cross_sections(options, list_of_systematics):
    '''
    Gets the normalised cross sections in the form:
    Group of Systematics : { List of Systematics in Group : [[central], [upper], [lower]]}
        [central] = [[x sec, unc], [x sec, unc]...[x sec, unc]] For N Bins
        [upper]   = [[x sec], [x sec]...[x sec]] For N Bins
        [lower]   = [[x sec], [x sec]...[x sec]] For N Bins
    '''
    # Copy structure of the systmatic lists in order to replace systematic name with their normailsed x sections
    normalised_systematic_uncertainty_x_sections = deepcopy(list_of_systematics)
    unfolded_normalised_systematic_uncertainty_x_sections = deepcopy(list_of_systematics)

    central_measurement, central_measurement_unfolded = read_normalised_xsection_measurement(options, 'central')
    for group_of_systematics, systematics_in_list in list_of_systematics.iteritems():
        for systematic, variation in systematics_in_list.iteritems():
            normalised_systematic_uncertainty_x_sections[group_of_systematics][systematic] = [central_measurement]
            unfolded_normalised_systematic_uncertainty_x_sections[group_of_systematics][systematic] = [central_measurement]
            if (systematic == 'PDF'):
                syst_unc_x_sec, unf_syst_unc_x_sec = read_normalised_xsection_systematics(options, variation, isPDF=True)

                # Get full PDF combination
                pdf_total_lower, pdf_total_upper = calculate_total_PDFuncertainty(options, central_measurement, syst_unc_x_sec)
                unf_pdf_total_lower, unf_pdf_total_upper = calculate_total_PDFuncertainty(options, central_measurement_unfolded, unf_syst_unc_x_sec)

                for PDF_Weight in variation:
                    normalised_systematic_uncertainty_x_sections[group_of_systematics][systematic].append(syst_unc_x_sec[PDF_Weight])
                    unfolded_normalised_systematic_uncertainty_x_sections[group_of_systematics][systematic].append(unf_syst_unc_x_sec[PDF_Weight])
                normalised_systematic_uncertainty_x_sections[group_of_systematics]['PDF_Combined'] = \
                    [central_measurement, pdf_total_upper, pdf_total_lower]
                unfolded_normalised_systematic_uncertainty_x_sections[group_of_systematics]['PDF_Combined'] = \
                    [central_measurement_unfolded, unf_pdf_total_upper, unf_pdf_total_lower]
            else:
                syst_unc_x_sec, unf_syst_unc_x_sec = read_normalised_xsection_systematics(options, variation)
                normalised_systematic_uncertainty_x_sections[group_of_systematics][systematic].append(syst_unc_x_sec['upper'])
                normalised_systematic_uncertainty_x_sections[group_of_systematics][systematic].append(syst_unc_x_sec['lower'])
                unfolded_normalised_systematic_uncertainty_x_sections[group_of_systematics][systematic].append(unf_syst_unc_x_sec['upper'])
                unfolded_normalised_systematic_uncertainty_x_sections[group_of_systematics][systematic].append(unf_syst_unc_x_sec['lower'])
    # print(normalised_systematic_uncertainty_x_sections)
    return normalised_systematic_uncertainty_x_sections, unfolded_normalised_systematic_uncertainty_x_sections

def calculate_total_PDFuncertainty(options, central_measurement, pdf_uncertainty_values={}):
    '''
    Calculates the appropriate lower and upper PDF uncertainty
    @param central_measurement: measurement from central PDF weight
    @param pdf_uncertainty_values: dictionary of measurements with different PDF weights; 
                                    format {PDFWeights_%d: measurement}
    '''
    number_of_bins = options['number_of_bins']
    pdf_min = []
    pdf_max = []
    
    # split PDF uncertainties into downwards (negative) and upwards (positive) components
    for bin_i in xrange(number_of_bins):
        negative = []
        positive = []
        central = central_measurement[bin_i][0]
        for index in range(0, 100):
            pdf_weight = 'PDFWeights_%d' % index
            pdf_uncertainty = pdf_uncertainty_values[pdf_weight][bin_i]
            if index % 2 == 0:  # even == negative
                negative.append(pdf_uncertainty)
            else:
                positive.append(pdf_uncertainty)
                
        pdf_max.append(sqrt(sum(max(x - central, y - central, 0) ** 2 for x, y in zip(negative, positive))))
        pdf_min.append(sqrt(sum(max(central - x, central - y, 0) ** 2 for x, y in zip(negative, positive))))

    return pdf_min, pdf_max  

def get_symmetrised_systematic_uncertainty(norm_syst_unc_x_secs):
    '''
    Gets the symmetrised normalised cross sections uncertainties in the form:
    Group of Systematics : { List of Systematics in Group : [[central], [symmetrised uncertainty], [signed uncertainty]]}
        [central]                   = [[x sec, unc], [x sec, unc]...[x sec, unc]] For N Bins
        [symmetrised uncertainty]   = [sym unc, sym unc...sym unc] For N Bins
        [signed uncertainty]        = [sign, sign...sign] For N Bins
    '''
    normalised_x_sections_with_symmetrised_systematics = deepcopy(norm_syst_unc_x_secs)
    for group_of_systematics, systematics_in_list in norm_syst_unc_x_secs.iteritems():
        for systematic, variation in systematics_in_list.iteritems():
            # Don't need 'PDF' now we have 'PDF_Combined'
            if systematic == 'PDF': continue
            central_measurement = variation[0]
            upper_measurement = variation[1]
            lower_measurement = variation[2]
            symmetrised_uncertainties, signed_uncertainties = get_symmetrised_errors(central_measurement, upper_measurement, lower_measurement)

            normalised_x_sections_with_symmetrised_systematics[group_of_systematics][systematic] = \
                [central_measurement, symmetrised_uncertainties, signed_uncertainties] 
    return normalised_x_sections_with_symmetrised_systematics           

def get_symmetrised_errors(central_measurement, upper_measurement, lower_measurement):
    '''
    Returns the symmetric error in each bin for a specific systematic and also the sign of the systematic.
    Sign is used for calculating the covariance matrices. Returns of the form:
    [Symmetric Uncertainties],[Signed Uncertainties]
        [symmetrised uncertainty]   = [sym unc, sym unc...sym unc] For N Bins
        [signed uncertainty]        = [sign, sign...sign] For N Bins
    '''
    number_of_bins = len(central_measurement)
    symm_uncerts = []
    sign_uncerts = []

    for c, u, l in zip(central_measurement, upper_measurement, lower_measurement):
        central = c[0] # Getting the measurement, not the error [xsec, unc]
        upper = u
        lower = l

        upper_uncertainty = abs(central - upper)
        lower_uncertainty = abs(central - lower)
        symmetrised_uncertainty = max(upper_uncertainty, lower_uncertainty)
        #  Getting the sign of the uncertainty
        sign = get_sign(central, upper, lower, upper_uncertainty, lower_uncertainty)
        symm_uncerts.append(symmetrised_uncertainty)
        sign_uncerts.append(sign)
    return symm_uncerts, sign_uncerts

def get_sign(central, upper, lower, upper_variation, lower_variation):
    '''
    Returns the sign of the uncertainty - i.e. was the upper variation bigger than the lower variation
    Returns 0 if the systematic is symmetrical
    '''
    if ((upper_variation > lower_variation) and (upper > central) ): return 1
    elif ((upper_variation > lower_variation) and (upper < central) ): return -1
    elif ((lower_variation > upper_variation) and (lower > central) ): return -1
    elif ((lower_variation > upper_variation) and (lower < central) ): return 1
    else: return 0

def get_measurement_with_total_systematic_uncertainty(options, x_sec_with_symmetrised_systematics):
    '''
    Returns the measurement with the total symmetrised systematic uncertainties of the form:
    Group of Systematics : [central value][central uncertainty][symmetrised systematic uncertainty+][symmetrised systematic uncertainty-]
        [central value]                         = [[x sec, unc], [x sec, unc],... [x sec, unc]] For N Bins
        [symmetrised systematic uncertainty+]   = [central unc, central unc,... central unc] For N Bins
        [symmetrised systematic uncertainty-]   = [sys unc, sys unc,... sys unc] For N Bins
    '''
    measurement_with_total_uncertainty = {}
    number_of_bins = options['number_of_bins']
    for group_of_systematics, systematics_in_list in x_sec_with_symmetrised_systematics.iteritems():
        sys_unc = 0
        tmp_meas = []
        for bin_i in range( 0, number_of_bins ):
            for systematic, measurement in systematics_in_list.iteritems():
                central = measurement[0][bin_i] # Still [Value, Error]
                sys_unc += measurement[1][bin_i]**2
                # sign = measurement[2][bin_i]
            tmp_meas.append( [central[0], sqrt(sys_unc), sqrt(sys_unc)] )
        measurement_with_total_uncertainty[group_of_systematics] = tmp_meas
        print(measurement_with_total_uncertainty)
    return measurement_with_total_uncertainty

                # MAYBE do this with a entry by entry list using \t???
# def print_normalised_measurements(all_normalised_measurements):
#     '''
#     Allows for printing of the normalised measurements for the cross section
#     '''
#     for syst_category, measurements in all_normalised_measurements.iteritems():
#         print( "Type of systematics being looked at is '{syst_category}'".format(syst_category=syst_category) )
#         for key, list_of_norm_xsec_meas in measurements.iteritems():
#             print("\nThe {key} normalised cross section measurements is :\n  {list_of_norm_xsec_meas}\n ".format(
#                 key=key, 
#                 list_of_norm_xsec_meas=list_of_norm_xsec_meas)
#             ) 
#     return

