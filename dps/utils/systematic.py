from __future__ import division, print_function
from dps.utils.file_utilities import write_data_to_JSON, deprecated
from dps.utils.Calculation import combine_errors_in_quadrature
from dps.utils.pandas_utilities import read_tuple_from_file, \
dict_to_df, list_to_series, df_to_file, \
divide_by_series, file_to_df, matrix_from_df, \
create_covariance_matrix
from copy import deepcopy
from math import sqrt
import numpy as np

def write_normalised_xsection_measurement(options, measurement, measurement_unfolded, summary = '' ):
    '''
    Writes the list of normalised measurements and normalised unfolded measurements of the form: 
    [Central Value, Lower Systemtic, Upper Systematic] to a json. Different combinations of 
    systematic uncertainty are stored as different json by appending different 'summary'
    '''
    path_to_DF=options['path_to_DF']
    method=options['method']
    channel=options['channel']

    output_file = '{path_to_DF}/central/xsection_normalised_{channel}_{method}_with_errors.txt'
    output_file = output_file.format(
        path_to_DF = path_to_DF,
        channel = channel,
        method = method,
    )
    if not summary == '':
        output_file = output_file.replace( 'with_errors', summary + '_errors' )
    
    output = {'TTJet_measured':measurement, 'TTJet_unfolded': measurement_unfolded}
    
    write_data_to_JSON( output, output_file )

    print("Data written to : ", output_file)
    return

def write_systematic_xsection_measurement(options, systematic, total_syst, summary = '' ):
    '''
    Write systematics to a df.
    '''
    path_to_DF=options['path_to_DF']
    method=options['method']
    channel=options['channel']

    output_file = '{path_to_DF}/central/xsection_normalised_{channel}_{method}_summary_absolute.txt'
    output_file = output_file.format(
        path_to_DF = path_to_DF,
        channel = channel,
        method = method,
    )
    if not summary == '':
        output_file = output_file.replace( 'only', summary )
    
    stats = [stat for value, stat in systematic['central']]
    central = [value for value, stat in systematic['central']]
    syst_total = [syst1 for value, syst1, syst2 in total_syst]
    del systematic['central']

    # Strip signs from dictionary and create dict of Series
    all_uncertainties = {syst : list_to_series( vals[0] ) for syst, vals in systematic.iteritems()}
    # Add the statistical uncertainties
    all_uncertainties['statistical'] = list_to_series( stats )
    # Add the central measurement
    all_uncertainties['central'] = list_to_series( central )
    # Add the total systematic
    all_uncertainties['systematic'] = list_to_series( syst_total )
    # Output to absolute file
    d_abs = dict_to_df(all_uncertainties)
    df_to_file(output_file, d_abs)

    # Create Relative Uncertainties
    output_file = output_file.replace('absolute', 'relative')
    for uncertainty, vals in all_uncertainties.iteritems():
        if uncertainty == 'central': continue
        # Just divide the abs uncertainty by the central value
        all_uncertainties[uncertainty] = divide_by_series(vals, all_uncertainties['central'])
    all_uncertainties['central'] = divide_by_series(all_uncertainties['central'], all_uncertainties['central'])

    d_rel = dict_to_df(all_uncertainties)
    df_to_file(output_file, d_rel)
    return

def append_PDF_uncertainties(all_systematics, minPdfWeight, maxPdfWeight):
    '''
    Replace 'PDF' entry in list of all systematics with actual PDF variations
    '''
    variation = []
    for index in xrange (minPdfWeight, maxPdfWeight):
        variation.append('PDFWeights_'+str(index))
    all_systematics['PDF'] = variation
    return all_systematics


def read_normalised_xsection_measurement(options, category):
    '''
    Returns the normalised measurement and normalised unfolded measurement for 
    the file associated with the variable under study
    '''
    variable=options['variable']
    variables_no_met=options['variables_no_met']
    met_specific_systematics=options['met_specific_systematics']
    path_to_DF=options['path_to_DF']
    method=options['method']
    channel=options['channel']
    filename = '{path}/{category}/xsection_normalised_{channel}_{method}.txt'
    # Disregarding Met Uncertainties if variable does not use MET
    if (category in met_specific_systematics) and (variable in variables_no_met):
        filename = filename.format(
            path = path_to_DF,
            channel = channel,
            category = 'central',
            method = method,
        )
    else:
        filename = filename.format(
            path = path_to_DF,
            channel = channel,
            category = category,
            method = method
        )
    normalised_xsection = read_tuple_from_file( filename )
    measurement = normalised_xsection['TTJet_measured_withoutFakes']
    measurement_unfolded = normalised_xsection['TTJet_unfolded']
    return measurement, measurement_unfolded  


def read_normalised_xsection_systematics(options, variation, is_multiple_sources=False):
    '''
    Returns the list of normalised measurements and normalised unfolded measurements 
    for each systematic category

    variation: current systematic (BJet, PDF etc)
    is_multiple_sources: is variation composed of multiple sources? (PDF : PDFWeight1, ...)
    '''
    systematics = {}
    systematics_unf = {}

    if is_multiple_sources:
        for source in variation:
            src, src_unf = read_normalised_xsection_measurement(options, source)
            systematics[source] = src
            systematics_unf[source] = src_unf  
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
    Returns the normalised cross section measurements for the given list of systematics

    Of the form:
        ['Central'] [Value, Error],
        ['Systematic'] [[Lower Measurement], [Upper Measurement]],
            ||
            ||
           \||/
            \/

    [central]               =   [[x sec, unc], [x sec, unc]...[x sec, unc]] For N Bins
    [Upper Measurement]     =   [[x sec], [x sec]...[x sec]] For N Bins
    [Lower Measurement]     =   [[x sec], [x sec]...[x sec]] For N Bins

    For PDF there is an additional nest for each variation
    '''
    # Copy structure of the systmatic lists in order to replace systematic name with their normailsed x sections
    normalised_systematic_uncertainty_x_sections = deepcopy(list_of_systematics)
    unfolded_normalised_systematic_uncertainty_x_sections = deepcopy(list_of_systematics)

    central_measurement, central_measurement_unfolded = read_normalised_xsection_measurement(options, 'central')
    normalised_systematic_uncertainty_x_sections['central'] = central_measurement
    unfolded_normalised_systematic_uncertainty_x_sections['central'] = central_measurement_unfolded

    for systematic, variation in list_of_systematics.iteritems():
        if (systematic == 'PDF'):
            syst_unc_x_sec, unf_syst_unc_x_sec = read_normalised_xsection_systematics(options, variation, is_multiple_sources=True)
            normalised_systematic_uncertainty_x_sections[systematic] = []
            unfolded_normalised_systematic_uncertainty_x_sections[systematic] = []
            for weight, vals in syst_unc_x_sec.iteritems():
                normalised_systematic_uncertainty_x_sections[systematic].append([weight, vals])
            for weight, vals in unf_syst_unc_x_sec.iteritems():
                unfolded_normalised_systematic_uncertainty_x_sections[systematic].append([weight, vals])

        elif (systematic == 'TTJets_envelope'):
            syst_unc_x_sec, unf_syst_unc_x_sec = read_normalised_xsection_systematics(options, variation, is_multiple_sources=True)
            env_lower, env_upper = get_scale_envelope(options, syst_unc_x_sec)
            unf_env_lower, unf_env_upper = get_scale_envelope(options, unf_syst_unc_x_sec)
            normalised_systematic_uncertainty_x_sections[systematic] = [
                env_lower,
                env_upper,
            ]
            unfolded_normalised_systematic_uncertainty_x_sections[systematic] = [
                unf_env_lower,
                unf_env_upper,
            ]
        else :
            syst_unc_x_sec, unf_syst_unc_x_sec = read_normalised_xsection_systematics(options, variation)
            normalised_systematic_uncertainty_x_sections[systematic] = [
                syst_unc_x_sec['upper'], 
                syst_unc_x_sec['lower'],
            ]
            unfolded_normalised_systematic_uncertainty_x_sections[systematic] = [
                unf_syst_unc_x_sec['upper'], 
                unf_syst_unc_x_sec['lower'],
            ]

    return normalised_systematic_uncertainty_x_sections, unfolded_normalised_systematic_uncertainty_x_sections


def get_scale_envelope(options, d_scale_syst):
    '''
    Calculate the scale envelope for the renormalisation/factorisation/combined systematic uncertainties
    For all up variations in a bin keep the highest
    For all down variations in a bin keep the lowest

    d_scale_syst is a dictionary containing all the Q2 scale variations
    Retrieve the 3 up(down) variations from d_scale_syst and choose max(min) value as the envelope for each bin
    '''
    down_variations = []
    up_variations = []
    envelope_up = []
    envelope_down = []

    # Separate into up/down scale variations
    for scale_variation in d_scale_syst:
        if 'down' in scale_variation:
            down_variations.append(d_scale_syst[scale_variation])
        elif 'up' in scale_variation:
            up_variations.append(d_scale_syst[scale_variation])

    # find min/max
    for v1, v2, v3 in zip (up_variations[0], up_variations[1], up_variations[2]):
        envelope_up.append(max(v1, v2, v3))
    for v1, v2, v3 in zip (down_variations[0], down_variations[1], down_variations[2]):
        envelope_down.append(min(v1, v2, v3))
    return envelope_down, envelope_up


def calculate_total_PDFuncertainty(options, central_measurement, pdf_uncertainty_values):
    '''
    Returns the symmetrised PDF uncertainty. Finds the max of RMS 
    of all the up variations and RMS of all the down variations in a bin.
                
                                                2
                  SUM_Bins (Variation - Central)
    RMS = SQRT ( -------------------------------- )
                                N-1

    Of the form:
        [Uncertainty] for N bins

    pdf_uncertainty_values = [ [[var_1],[vals_1]], [[var_2][vals_2]] ...]
    '''
    number_of_bins = options['number_of_bins']
    pdf_sym = []

    for bin_i in xrange(number_of_bins):
        central = central_measurement[bin_i][0]

        # now to calculate the RMS (sigma) for all PDF variations
        rms = 0
        for pdf_variation in pdf_uncertainty_values:
            variation = pdf_variation[1][bin_i]
            rms += (variation-central)**2
        pdf_sym.append( sqrt( rms / (len(pdf_uncertainty_values)-1) ))
    return pdf_sym  


def get_symmetrised_systematic_uncertainty(options, norm_syst_unc_x_secs ):
    '''
    Returns the symmetrised uncertainties on the normalised cross sections.

    Of the form:
        ['Central'] [[Value][Stat_Uncert]],
        ['Systematic'] [[Sym_Uncert],[Sign]],
            ||
            ||
           \||/
            \/

    Separate uncertainty calculation for PDFs. Need to think how to calc correlation matrices. (i.e. no way to get sign yet)
    Combine PDFs and alphaS systematics
    '''
    normalised_x_sections_with_symmetrised_systematics = deepcopy(norm_syst_unc_x_secs)
    central_measurement = norm_syst_unc_x_secs['central']
    for systematic, variation in norm_syst_unc_x_secs.iteritems():
        if (systematic == 'PDF'):
            # Replace all PDF weights with full PDF combination
            pdf_sym = calculate_total_PDFuncertainty(
                options, 
                central_measurement, 
                variation,
            )
            # TODO Find signs etc... i.e. do proper covariance for PDF
            normalised_x_sections_with_symmetrised_systematics[systematic] = [
                pdf_sym, 
                [0]*len(central_measurement),
            ]  
        elif systematic == 'central':
            normalised_x_sections_with_symmetrised_systematics['central'] = central_measurement
        else:
            upper_measurement = variation[0]
            lower_measurement = variation[1]

            isTopMassSystematic = True if systematic == 'TTJets_mass' else False

            symmetrised_uncertainties, signed_uncertainties = get_symmetrised_errors(
                central_measurement, 
                upper_measurement, 
                lower_measurement, 
                options, 
                isTopMassSystematic,
            )

            normalised_x_sections_with_symmetrised_systematics[systematic] = [
                symmetrised_uncertainties, 
                signed_uncertainties,
            ]         

    # Combine LightJet and BJet Systematics
    bJet = normalised_x_sections_with_symmetrised_systematics['BJet'][0]
    lightJet = normalised_x_sections_with_symmetrised_systematics['LightJet'][0]
    bJet_tot = [combine_errors_in_quadrature([e1, e2]) for e1, e2 in zip(bJet, lightJet)]
    normalised_x_sections_with_symmetrised_systematics['BJet'][0] = bJet_tot

    # Combine PDF with alphaS variations
    alphaS = normalised_x_sections_with_symmetrised_systematics['TTJets_alphaS'][0]
    pdf = normalised_x_sections_with_symmetrised_systematics['PDF'][0]
    pdf_tot = [combine_errors_in_quadrature([e1, e2]) for e1, e2 in zip(alphaS, pdf)]
    normalised_x_sections_with_symmetrised_systematics['PDF'][0] = pdf_tot
    # TODO combine the signs....

    # Now alphaS is combined with pdfs dont need it in dictionary anymore. nor LightJet
    del normalised_x_sections_with_symmetrised_systematics['LightJet']
    del normalised_x_sections_with_symmetrised_systematics['TTJets_alphaS']

    return normalised_x_sections_with_symmetrised_systematics           


def get_symmetrised_errors(central_measurement, upper_measurement, lower_measurement, options, isTopMassSystematic=False ):
    '''
    Returns the symmetric error in each bin for a specific systematic and also the sign of the systematic.
    Sign is used for calculating the covariance matrices. 

    Returns of the form:
        [Symmetric Uncertainties]
        [Signed Uncertainties]

    [symmetrised uncertainty]   = [sym unc, sym unc...sym unc] For N Bins
    [signed uncertainty]        = [sign, sign...sign] For N Bins
    '''
    number_of_bins = len(central_measurement)
    symm_uncerts = []
    sign_uncerts = []

    for c, u, l in zip(central_measurement, upper_measurement, lower_measurement):
        central = c[0] # Getting the measurement, not the stat unc [xsec, unc]
        upper = u
        lower = l

        upper_uncertainty = abs(central - upper)
        lower_uncertainty = abs(central - lower)

        if isTopMassSystematic:
            upper_uncertainty, lower_uncertainty = scaleTopMassSystematic( upper_uncertainty, lower_uncertainty, options['topMasses'], options['topMassUncertainty'] )

        symmetrised_uncertainty = max(upper_uncertainty, lower_uncertainty)
        #  Getting the sign of the uncertainty
        if u == l:
            sign = np.sign( upper - central )
        else:
            sign = np.sign( upper - lower )

        symm_uncerts.append(symmetrised_uncertainty)
        sign_uncerts.append(sign)
    return symm_uncerts, sign_uncerts

def scaleTopMassSystematic( upper_uncertainty, lower_uncertainty, topMasses, topMassUncertainty ):
    '''
    For the top mass systematic, scale the uncertainties to the actual top mass uncertainty.
    i.e. Samples with different top masses do not represent the top mass uncertainty
    '''
    lowMassDifference = topMasses[1] - topMasses[0]
    upMassDifference = topMasses[2] - topMasses[1]

    upper_uncertainty *= topMassUncertainty / upMassDifference
    lower_uncertainty *= topMassUncertainty / lowMassDifference

    return upper_uncertainty, lower_uncertainty

@deprecated
def get_sign(central, upper, lower, upper_variation, lower_variation):
    '''
    Currently Obsolete.
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
    Returns the measurement with the total symmetrised systematic uncertainties 
    Of the form:
        [central] [syst_unc up] [syst_unc down]

    [central]           = [x sec, x sec,... x sec]
    [syst_unc up]       = [sys unc, sys unc,... sys unc]
    [syst_unc down]     = [sys unc, sys unc,... sys unc] 
    For N Bins

    TODO Should we output something like [central] [stat_unc] [syst_unc] instead?

    '''
    number_of_bins = options['number_of_bins']
    measurement_with_total_uncertainty = []
    for bin_i in range( 0, number_of_bins ):
        sys_unc = 0
        central = x_sec_with_symmetrised_systematics['central'][bin_i] # Still [Value, Error]
        for systematic, measurement in x_sec_with_symmetrised_systematics.iteritems():
            if (systematic == 'central'): continue
            sys_unc += measurement[0][bin_i]**2
        measurement_with_total_uncertainty.append( [central[0], sqrt(sys_unc), sqrt(sys_unc)] )
    return measurement_with_total_uncertainty

def print_dictionary(title, dictionary_to_print):
    '''
    Prints dictionaries in a nicer form
    TODO Maybe think how pandas can be incorporated into 03...
    '''
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    print ()
    print ('-'*100)
    print (title)
    print ('-'*100)
    pp.pprint(dictionary_to_print)
    print ()
    return

# ------------------------------------------------------------------------------------------------------------------
# COVARIANCE MATRICES
# ------------------------------------------------------------------------------------------------------------------

def generate_covariance_matrices(options, x_sec_with_symmetrised_systematics):
    '''
    Iterates through each group of systematics generating and plotting the covariance matrix of the systematic
    '''
    number_of_bins=options['number_of_bins']    
    variable = options['variable']
    channel = options['channel']
    statistic = x_sec_with_symmetrised_systematics['central'] # [Value, Stat]
    all_covariance_matrices = []
    table_outfile_tmp = 'tables/covariance_matrices/{ch}/{var}/{sys}_{label}_matrix.txt'

    for syst_name, measurement in x_sec_with_symmetrised_systematics.iteritems():
        if syst_name == 'central': continue
        # Outputfile

        systematic = measurement[0]
        sign = measurement[1]

        # Create the matrices in numpy.matrix format
        covariance_matrix, correlation_matrix = generate_covariance_matrix(number_of_bins, systematic, sign)
        all_covariance_matrices.append(covariance_matrix)
        all_correlation_matrices.append(correlation_matrix)

        # Convert the matrices to DF format, output and plot them
        table_outfile = table_outfile_tmp.format( ch=channel, sys=syst_name, var=variable, label='Covariance')
        create_covariance_matrix(covariance_matrix, table_outfile)
        make_covariance_plot(options, syst_name, covariance_matrix)
        table_outfile = table_outfile_tmp.format( ch=channel, sys=syst_name, var=variable, label='Correlation')
        create_covariance_matrix(correlation_matrix, table_outfile)
        make_covariance_plot(options, syst_name, correlation_matrix, label='Correlation')

    generate_total_covariance(options, all_covariance_matrices, all_correlation_matrices)

    return

def generate_covariance_matrix(number_of_bins, systematic, sign):
    '''
    Variance_ii = (Unc_i) * (Unc_i)
    Covariance_ij = (Sign_i*Unc_i) * (Sign_j*Unc_j)
    Correlation_ij = (Sign_i*Unc_i) * (Sign_j*Unc_j)
                    ---------------------------------
                             (Unc_i * Unc_j)
    Returns the matrices in the form of a numpy matrix    
    '''
    cov_matrix = []
    cor_matrix = []
    for bin_i in xrange(number_of_bins):
        cov_matrix_row=[]
        cor_matrix_row=[]
        for bin_j in xrange(number_of_bins):
            uncertainty_i   = systematic[bin_i]
            uncertainty_j   = systematic[bin_j]
            sign_i          = sign[bin_i]
            sign_j          = sign[bin_j]   
            cov_ij          = (sign_i*uncertainty_i)*(sign_j*uncertainty_j)
            cor_ij          = cov_ij/(uncertainty_i*uncertainty_j)

            cor_matrix_row.append(cor_ij)
            cov_matrix_row.append(cov_ij)
        cor_matrix.append(cor_matrix_row)
        cov_matrix.append(cov_matrix_row)

    covariance_matrix = np.matrix(cov_matrix)
    correlation_matrix = np.matrix(cor_matrix)
    return covariance_matrix, correlation_matrix

def generate_total_covariance(options, all_covariances, all_correlations):
    '''
    Add covariances together for total covariance matrix

    Cov_tot = Cov_stat + Cov_PDF + Cov_BJet ...
    Similarly for Correlation
    '''
    # Paths to statistical Covariance/Correlation matrices.
    filepath_tmp='tables/covariance_matrices/{ch}/{var}/Stat_{label}_matrix.txt'.
    cov_path=filepath_tmp.format(ch=options['channel'], var=options['variable'],
        label='Covariance')
    cor_path=filepath_tmp.format(ch=options['channel'], var=options['variable'],
        label='Correlation')

    # Convert to numpy matrix and create total
    cov_stat = file_to_df(cov_path)
    cov_stat = matrix_from_df(cov_stat)
    cov_tot = cov_stat
    for m in all_covariances:
        cov_tot+=m

    cor_stat = file_to_df(cor_path)
    cor_stat = matrix_from_df(cor_stat)
    cor_tot = cor_stat
    for m in all_correlations:
        cor_tot+=m

    # Paths to output total Covariance/Correlation matrices.
    table_outfile_tmp = 'tables/covariance_matrices/{ch}/{var}/Total_{label}_matrix.txt'
    cov_outfile = table_outfile_tmp.format(ch=options['channel'], var=options['variable'], 
        label='Covariance')
    cor_outfile = table_outfile_tmp.format(ch=options['channel'], var=options['variable'], 
        label='Covariance')

    # Save the total matrices
    create_covariance_matrix( cov_tot, table_outfile )
    create_covariance_matrix( cor_tot, table_outfile )

    # Plot the total matrices
    make_covariance_plot( options, 'Stat', cov_stat, label='Covariance' )
    make_covariance_plot( options, 'Total', cov_tot, label='Covariance' )
    make_covariance_plot( options, 'Stat', cor_stat, label='Correlation' )
    make_covariance_plot( options, 'Total', cor_tot, label='Correlation' )
    return

def make_covariance_plot( options, syst_name, matrix, label='Covariance' ):    
    '''
    Take the matrix in list form and bin edges in list form to create a TH2F of the covariance matrix
    Saves to plots/covariance_matrices/{PhaseSpace}/{Channel}/{Variable}/
    '''
    from dps.config.variable_binning import bin_edges_vis
    from dps.utils.file_utilities import make_folder_if_not_exists
    import matplotlib as mpl
    mpl.use( 'agg' )

    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    my_cmap = cm.get_cmap( 'jet' )

    matrix_max = matrix.max()
    matrix_min = matrix.min()

    if( matrix_max == 0):
        return

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.set_aspect('equal')
    plt.imshow(matrix, interpolation='nearest', cmap = my_cmap )

    plt.colorbar()
    plt.tight_layout()
    plt.show()

    variable = options['variable']
    channel = options['channel']
    phase_space = options['phase_space']

    # Output folder of covariance matrices
    covariance_matrix_output_path = 'plots/covariance_matrices/{phase_space}/{channel}/{variable}/'
    covariance_matrix_output_path = covariance_matrix_output_path.format(
        variable = variable,
        channel = channel,
        phase_space = phase_space,
        )
    make_folder_if_not_exists(covariance_matrix_output_path)
    plt.savefig(covariance_matrix_output_path+syst_name+'_'+label+'_matrix.pdf')
