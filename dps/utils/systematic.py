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
from dps.config.variable_binning import bin_edges_vis
from dps.utils.file_utilities import make_folder_if_not_exists
from dps.config import CMS
from dps.config.latex_labels import variables_latex, variables_NonLatex
from dps.config.xsection import XSectionConfig
from copy import deepcopy
from itertools import product
measurement_config = XSectionConfig( 13 )
template = '%.1f fb$^{-1}$ (%d TeV)'
title = template % ( measurement_config.new_luminosity/1000, measurement_config.centre_of_mass_energy)

import matplotlib as mpl
mpl.use( 'agg' )

import matplotlib.pyplot as plt
import matplotlib.cm as cm
my_cmap = cm.get_cmap( 'bwr' )
import gc

from matplotlib import rc
rc( 'font', **CMS.font )
rc( 'text', usetex = True )

np.set_printoptions(
    precision = 3,
    linewidth = 400,
)
# from memory_profiler import profile
# fp=open('memory_profiler.log','w')

# @profile(stream=fp)
def write_systematic_xsection_measurement(options, systematic, total_syst, summary = '' ):
    '''
    Write systematics to a df.
    '''
    path_to_DF  = options['path_to_DF']
    method      = options['method']
    channel     = options['channel']
    norm        = options['normalisation_type']

    output_file_temp = '{path_to_DF}/central/xsection_{norm}_{channel}_{method}_summary_{unctype}.txt'
    output_file = output_file_temp.format(
        path_to_DF  = path_to_DF,
        channel     = channel,
        method      = method,
        norm        = norm,
        unctype     = 'absolute',
    )
 
    stats       = [stat  for value, stat in systematic['central']]
    central     = [value for value, stat in systematic['central']]
    syst_total  = [syst1 for value, syst1, syst2 in total_syst]
    del systematic['central']

    # Strip signs from dictionary and create dict of Series
    all_uncertainties = {syst : list_to_series( vals[0] ) for syst, vals in systematic.iteritems()}
    # Add the statistical uncertainties
    all_uncertainties['statistical']    = list_to_series( stats )
    # Add the central measurement
    all_uncertainties['central']        = list_to_series( central )
    # Add the total systematic
    all_uncertainties['systematic']     = list_to_series( syst_total )

    # Output to absolute file
    d_abs = dict_to_df(all_uncertainties)
    df_to_file(output_file, d_abs)

    # Create Relative Uncertainties
    output_file = output_file_temp.format(
        path_to_DF  = path_to_DF,
        channel     = channel,
        method      = method,
        norm        = norm,
        unctype     = 'relative',
    )
    for uncertainty, vals in all_uncertainties.iteritems():
        if uncertainty == 'central': continue
        # Just divide the abs uncertainty by the central value
        all_uncertainties[uncertainty] = divide_by_series(vals, all_uncertainties['central'])
    all_uncertainties['central'] = divide_by_series(all_uncertainties['central'], all_uncertainties['central'])

    d_rel = dict_to_df(all_uncertainties)
    df_to_file(output_file, d_rel)
    return

# @profile(stream=fp)
def append_PDF_uncertainties(all_systematics, pdfset=''):
    '''
    Replace 'PDF' entry in list of all systematics with actual PDF variations
    pdfset= CT14 or MMHT14
    '''
    minPdfWeight = measurement_config.pdfWeightMin 
    maxPdfWeight = measurement_config.pdfWeightMax

    pdf = ''
    if pdfset:
        pdf = pdfset
        if 'CT14' in pdfset:
            maxPdfWeight = measurement_config.ct14WeightMax
        elif 'MMHT14' in pdfset:
            maxPdfWeight = measurement_config.mmht14WeightMax
        else:
            print("Unknown PDFSet")
    else:
        pdf = 'PDF'

    variation = []
    for index in xrange (minPdfWeight, maxPdfWeight):
        variation.append(pdf+'Weights_'+str(index))
    all_systematics[pdf] = variation
    return all_systematics

def remove_MET_uncertainties(all_systematics):
    '''
    Remove MET uncertainty calculations from MET independent measurements
    '''
    del all_systematics['ElectronEn']
    del all_systematics['MuonEn']
    del all_systematics['TauEn']
    del all_systematics['UnclusteredEn']
    return all_systematics

# @profile(stream=fp)
def read_xsection_measurement(options, category):
    '''
    Returns the normalised measurement and normalised unfolded measurement for 
    the file associated with the variable under study
    '''
    variable                    = options['variable']
    variables_no_met            = options['variables_no_met']
    met_specific_systematics    = options['met_specific_systematics']
    path_to_DF                  = options['path_to_DF']
    method                      = options['method']
    channel                     = options['channel']
    norm                        = options['normalisation_type']

    filename = '{path}/{category}/xsection_{norm}_{channel}_{method}.txt'
    # Disregarding Met Uncertainties if variable does not use MET
    if (category in met_specific_systematics) and (variable in variables_no_met):
        filename = filename.format(
            path        = path_to_DF,
            channel     = channel,
            category    = 'central',
            method      = method,
            norm        = norm,
        )
    else:
        filename = filename.format(
            path        = path_to_DF,
            channel     = channel,
            category    = category,
            method      = method,
            norm        = norm,
        )

    measurement = read_tuple_from_file( filename )

    xsection_unfolded = measurement['TTJets_unfolded']

    if category is 'central':
        theoryUncertaintySources = options['mcTheoryUncertainties']
        xsection_mc = { 'central' : measurement['TTJets_powhegPythia8' ]}
        for source in theoryUncertaintySources:
            variations = theoryUncertaintySources[source]
            if source is 'TTJets_scale':
            # if source is 'TTJets_scale' or source is 'TTJets_CR':
                scale_xsections = {}
                for variation in variations:
                    xsectionWithUncertainty = measurement[variation]
                    for i in range(0,len(xsectionWithUncertainty)):
                        xsectionWithUncertainty[i] = xsectionWithUncertainty[i][0]
                    scale_xsections[variation] = xsectionWithUncertainty
                scale_envelope_lower, scale_envelope_upper = get_scale_envelope(scale_xsections, measurement['TTJets_powhegPythia8' ])
                xsection_mc[source] = [
                                        scale_envelope_lower,
                                        scale_envelope_upper,
                                        ]
                pass
            else:
                xsectionWithUncertainty_lower = deepcopy( measurement[variations[0]] )
                xsectionWithUncertainty_upper = deepcopy( measurement[variations[1]] )

                for i in range(0,len(xsectionWithUncertainty_lower)):
                    xsectionWithUncertainty_lower[i] = xsectionWithUncertainty_lower[i][0]
                    xsectionWithUncertainty_upper[i] = xsectionWithUncertainty_upper[i][0]

                xsection_mc[source] = [ 
                                        xsectionWithUncertainty_lower,
                                        xsectionWithUncertainty_upper,
                                        ]

        return xsection_unfolded, xsection_mc

    return xsection_unfolded  

def get_mc_data_difference(options, mc_xsections, data_xsections):

    central_mc = mc_xsections['central']
    central_data = data_xsections['central']

    uncertainty_sources = data_xsections.keys()

    data_mc_difference = {}

    for source in uncertainty_sources:
        # Difference between up-up, down-down and central-central for unfolded-ttbarPP8
        if source in mc_xsections.keys():
            if 'central' in source:
                data_mc_difference[source] = []
                for i in range(0,len(data_xsections[source])):
                    diff = []
                    diff.append(data_xsections[source][i][0] - mc_xsections[source][i][0])
                    diff.append(combine_errors_in_quadrature([data_xsections[source][i][1], mc_xsections[source][i][1]]))
                    data_mc_difference[source].append(diff)
            else:
                data_mc_difference[source] = []
                for i in range(0,len(data_xsections[source])):
                    diff = []
                    for j in range(0, len( data_xsections[source][i] )):
                        diff.append( data_xsections[source][i][j] - mc_xsections[source][i][j] )
                    data_mc_difference[source].append( diff )
        # Differnece between pdf variation (unfolded) and PP8
        elif source is 'PDF':
            data_mc_difference[source] = []
            for pdfVariation in data_xsections[source]:
                pdfDiff = []
                for i in range(0,len(pdfVariation[-1])):
                    pdfDiff.append( pdfVariation[1][i] - central_mc[i][0] )
                data_mc_difference[source].append( [pdfVariation[0], pdfDiff] )
        else:
            data_mc_difference[source] = []
            for i in range(0,len(data_xsections[source])):
                diff = []
                for j in range(0, len( data_xsections[source][i] )):
                    diff.append( data_xsections[source][i][j] - central_mc[j][0] )
                data_mc_difference[source].append( diff )

    return data_mc_difference

# @profile(stream=fp)
def read_xsection_systematics(options, variation, is_multiple_sources=False):
    '''
    Returns the list of normalised measurements and normalised unfolded measurements 
    for each systematic category

    variation: current systematic (BJet, PDF etc)
    is_multiple_sources: is variation composed of multiple sources? (PDF : PDFWeight1, ...)
    '''
    systematics_unf = {}

    if is_multiple_sources:
        for source in variation:
            src_unf = read_xsection_measurement(options, source)
            systematics_unf[source] = src_unf  
    else:
        upper_variation = variation[0]
        lower_variation = variation[1]
        systematic_up_unf = read_xsection_measurement(options, upper_variation)
        systematic_down_unf = read_xsection_measurement(options, lower_variation)     
        systematics_unf['lower'] = systematic_down_unf
        systematics_unf['upper'] = systematic_up_unf

    systematics_unf = get_systematic_measured_values_only(options, systematics_unf)   
    return systematics_unf


# @profile(stream=fp)
def get_systematic_measured_values_only(options, syst_xsecs_and_errs):
    '''
    When retreiveing systematic uncertainties they come in form [Value, Error]. 
    This strips the Errors.
    '''
    number_of_bins=options['number_of_bins']
    for variation, xsec_and_error in syst_xsecs_and_errs.iteritems():
        for bin_i in xrange(number_of_bins):
            x_sec = xsec_and_error[bin_i][0]
            xsec_and_error[bin_i] = x_sec
    return syst_xsecs_and_errs

# @profile(stream=fp)
def get_cross_sections(options, list_of_systematics):
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
    [Upper Measurement]     =   [x sec,  x sec, ... x sec] For N Bins
    [Lower Measurement]     =   [x sec,  x sec, ... x sec] For N Bins

    For PDF there is an additional nest for each variation
    '''
    # Copy structure of the systmatic lists in order to replace systematic name with their normailsed x sections
    unfolded_systematic_uncertainty_x_sections = deepcopy(list_of_systematics)
    central_measurement_unfolded, mc_xsection_variations = read_xsection_measurement(options, 'central')
    unfolded_systematic_uncertainty_x_sections['central'] = central_measurement_unfolded

    for systematic, variation in list_of_systematics.iteritems():
        if (systematic in ['PDF', 'CT14', 'MMHT14']):
            unf_syst_unc_x_sec = read_xsection_systematics(options, variation, is_multiple_sources=True)
            unfolded_systematic_uncertainty_x_sections[systematic] = []
            for weight, vals in unf_syst_unc_x_sec.iteritems():
                unfolded_systematic_uncertainty_x_sections[systematic].append([weight, vals])
        # elif (systematic == 'TTJets_scale' or systematic == 'TTJets_CR'):
        elif (systematic == 'TTJets_scale'):
            unf_syst_unc_x_sec = read_xsection_systematics(options, variation, is_multiple_sources=True)
            unf_env_lower, unf_env_upper = get_scale_envelope(unf_syst_unc_x_sec, central_measurement_unfolded)
            unfolded_systematic_uncertainty_x_sections[systematic] = [
                unf_env_lower,
                unf_env_upper,
            ]
        else :
            unf_syst_unc_x_sec = read_xsection_systematics(options, variation)
            unfolded_systematic_uncertainty_x_sections[systematic] = [
                unf_syst_unc_x_sec['lower'],
                unf_syst_unc_x_sec['upper'], 
            ]

    return unfolded_systematic_uncertainty_x_sections, mc_xsection_variations

# @profile(stream=fp)
def get_scale_envelope(d_scale_syst, central):
    '''
    Calculate the scale envelope for the renormalisation/factorisation/combined systematic uncertainties
    For all up variations in a bin keep the highest
    For all down variations in a bin keep the lowest

    Also scale fsr variations in PS down from * or / 2 to * or / sqrt(2)

    d_scale_syst is a dictionary containing all the scale variations
    Retrieve the up(down) variations from d_scale_syst and choose max(min) value as the envelope for each bin

    Need to store xsection giving largest difference to central, not just largest xsection
    '''
    import pandas as pd

    central = [c[0] for c in central]
    down = pd.DataFrame()
    up = pd.DataFrame()
    down['central'] = central
    up['central'] = central

    # Separate into up/down scale variations
    for scale_variation in d_scale_syst:
        scaleToAppend = []
        # Scale fsr in PS systematic
        if 'TTJets_fsrdown' in scale_variation or 'TTJets_fsrup' in scale_variation:
            scaleToAppend = scaleFSR(d_scale_syst[scale_variation], central)
        else:
            scaleToAppend = d_scale_syst[scale_variation]

        if 'down' in scale_variation:
            down[scale_variation] = scaleToAppend
        elif 'up' in scale_variation:
            up[scale_variation] = scaleToAppend
        else:
            down[scale_variation] = scaleToAppend
            up[scale_variation] = scaleToAppend

    down_diff = down.subtract(central, axis='index')
    down_diff = down_diff.abs()
    down_diff['max'] = down_diff.max(axis = 1)
    down_diff['index'] = down_diff.idxmax(axis = 1)
    scale = []
    for i, index in enumerate(down_diff['index']):
        scale.append(down[index][i])
    down['envelope_down']=scale


    up_diff = up.subtract(central, axis='index')
    up_diff = up_diff.abs()
    up_diff['max'] = up_diff.max(axis = 1)
    up_diff['index'] = up_diff.idxmax(axis = 1)
    scale = []
    for i, index in enumerate(up_diff['index']):
        scale.append(up[index][i])
    up['envelope_up']=scale

    return down['envelope_down'], up['envelope_up']

def scaleFSR(scale_variation, central):
    '''
    Scale the fsr
    '''
    scaled_fsr = []
    scale = sqrt(2) / 2
    i=0
    for variation, c in zip( scale_variation, central ):
        diff = ( variation - c ) * scale
        # scaled_fsr.append(c + diff)
        scale_variation[i] = c + diff
        i+=1

    return scale_variation

# @profile(stream=fp)
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
    pdf_sign = []

    for bin_i in xrange(number_of_bins):
        central = central_measurement[bin_i][0]

        # now to calculate the RMS (sigma) for all PDF variations
        rms = 0
        mean = 0
        for pdf_variation in pdf_uncertainty_values:
            variation = pdf_variation[1][bin_i]
            rms += (variation-central)**2
            mean += (variation-central)
        pdf_sym.append( sqrt( rms / (len(pdf_uncertainty_values)-1) ))
        pdf_sign.append( np.sign( mean / len(pdf_uncertainty_values) ) )
    return pdf_sym, pdf_sign


# @profile(stream=fp)
def get_symmetrised_systematic_uncertainty( options, syst_unc_x_secs ):
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
    xsections_with_symmetrised_systematics = deepcopy(syst_unc_x_secs)
    xsections_with_uncertainties_and_covariance = {}
    central_measurement = syst_unc_x_secs['central']
    d_Cov_Cor = {}
    for systematic, variation in syst_unc_x_secs.iteritems():
        if (systematic in ['PDF', 'CT14', 'MMHT14']):
            # Replace all PDF weights with full PDF combination
            pdf_sym, pdf_sign = calculate_total_PDFuncertainty(
                options, 
                central_measurement, 
                variation,
            )
            xsections_with_symmetrised_systematics[systematic] = [
                pdf_sym, 
                pdf_sign
            ]
        elif systematic == 'central':
            xsections_with_symmetrised_systematics['central'] = central_measurement
            xsections_with_uncertainties_and_covariance['central'] = central_measurement
        else:
            lower_measurement = variation[0]
            upper_measurement = variation[1]

            isTopMassSystematic = True if systematic == 'TTJets_mass' else False

            # The commented code in the remainder of this function
            # is used to calcualte the uncertainties and covariance
            # by taking the maximum uncertainty in each bin
            # symmetrised_uncertainties, signed_uncertainties = get_symmetrised_errors(
            #     central_measurement, 
            #     upper_measurement, 
            #     lower_measurement, 
            #     options, 
            #     isTopMassSystematic,
            #     systematic
            # )

            # xsections_with_symmetrised_systematics[systematic] = [
            #     symmetrised_uncertainties, 
            #     signed_uncertainties,
            # ]     

            # This code replace the previous lines (similar for the rest of this function)
            # and calculates the uncertainty and covariance by averaging the up/down
            # variations of each source
            # If only one variation is available (e.g. a colour reconnection sample)
            # then it will give identical results to the previous method
            symmetrised_uncertainties, covariance_matrix = get_average_covariance_matrix(
                central_measurement,
                upper_measurement,
                lower_measurement,
                options,
                isTopMassSystematic,
                systematic
                )

            xsections_with_uncertainties_and_covariance[systematic] = [
                symmetrised_uncertainties, 
                covariance_matrix,
            ]
            d_Cov_Cor[systematic] = [ covariance_matrix, correlation_from_covariance(covariance_matrix) ]

    # Add the inputMC statistics
    # xsections_with_symmetrised_systematics['inputMC'], _ = add_inputMC_systematic(options)
    inputMCUncertainties, inputMCCovariance = add_inputMC_systematic(options)
    xsections_with_uncertainties_and_covariance['inputMC'] = [ inputMCUncertainties[0], inputMCCovariance ]
    d_Cov_Cor['inputMC'] = inputMCCovariance

    # # Generate the Covariance Matrices
    # d_Cov_Cor = generate_covariance_matrices(
    #     options, 
    #     xsections_with_symmetrised_systematics
    # )

    # Combine Covariance Matrices
    # if  'BJet' in xsections_with_symmetrised_systematics and 'LightJet' in xsections_with_symmetrised_systematics:
    #     # Combine LightJet and BJet Systematics
    #     bJet = xsections_with_symmetrised_systematics['BJet'][0]
    #     lightJet = xsections_with_symmetrised_systematics['LightJet'][0]
    #     bJet_tot = [combine_errors_in_quadrature([e1, e2]) for e1, e2 in zip(bJet, lightJet)]
    #     xsections_with_symmetrised_systematics['BJet'][0] = bJet_tot
    #     del xsections_with_symmetrised_systematics['LightJet']

    #     # Combine the covariance matrices
    #     l_Cov = [d_Cov_Cor['BJet'][0], d_Cov_Cor['LightJet'][0]]
    #     d_Cov_Cor['BJet'] = combine_covariance_matrices(l_Cov)
    #     del d_Cov_Cor['LightJet']
    if  'BJet' in xsections_with_uncertainties_and_covariance and 'LightJet' in xsections_with_uncertainties_and_covariance:
        # Combine LightJet and BJet Systematics
        bJet = xsections_with_uncertainties_and_covariance['BJet'][0]
        lightJet = xsections_with_uncertainties_and_covariance['LightJet'][0]
        bJet_tot = [combine_errors_in_quadrature([e1, e2]) for e1, e2 in zip(bJet, lightJet)]
        xsections_with_uncertainties_and_covariance['BJet'][0] = bJet_tot
        del xsections_with_uncertainties_and_covariance['LightJet']

        # Combine the covariance matrices
        l_Cov = [d_Cov_Cor['BJet'][0], d_Cov_Cor['LightJet'][0]]
        d_Cov_Cor['BJet'] = combine_covariance_matrices(l_Cov)
        del d_Cov_Cor['LightJet']

    # if 'PDF' in xsections_with_symmetrised_systematics and 'TTJets_alphaS' in xsections_with_symmetrised_systematics:
    #     # Combine PDF with alphaS variations
    #     pdf = xsections_with_symmetrised_systematics['PDF'][0]
    #     alphaS = xsections_with_symmetrised_systematics['TTJets_alphaS'][0]
    #     pdf_tot = [combine_errors_in_quadrature([e1, e2]) for e1, e2 in zip(alphaS, pdf)]
    #     xsections_with_symmetrised_systematics['PDF'][0] = pdf_tot
    #     del xsections_with_symmetrised_systematics['TTJets_alphaS']

    #     # Combine the covariance matrices
    #     l_Cov = [d_Cov_Cor['PDF'][0], d_Cov_Cor['TTJets_alphaS'][0]]
    #     d_Cov_Cor['PDF'] = combine_covariance_matrices(l_Cov)
    #     del d_Cov_Cor['TTJets_alphaS']
    if 'PDF' in xsections_with_uncertainties_and_covariance and 'TTJets_alphaS' in xsections_with_uncertainties_and_covariance:
        # Combine PDF with alphaS variations
        pdf = xsections_with_uncertainties_and_covariance['PDF'][0]
        alphaS = xsections_with_uncertainties_and_covariance['TTJets_alphaS'][0]
        pdf_tot = [combine_errors_in_quadrature([e1, e2]) for e1, e2 in zip(alphaS, pdf)]
        xsections_with_uncertainties_and_covariance['PDF'][0] = pdf_tot
        del xsections_with_uncertainties_and_covariance['TTJets_alphaS']

        # Combine the covariance matrices
        l_Cov = [d_Cov_Cor['PDF'][0], d_Cov_Cor['TTJets_alphaS'][0]]
        d_Cov_Cor['PDF'] = combine_covariance_matrices(l_Cov)
        del d_Cov_Cor['TTJets_alphaS']

    # Create covariance matrices
    d_Cov_Cor['Stat'] = add_covariance( options, d_Cov_Cor, addStat = True )
    d_Cov_Cor['inputMC'] = add_covariance( options, d_Cov_Cor, addInputMCStat = True )
    d_Cov_Cor['Total'] = add_covariance( options, d_Cov_Cor, addTotal = True )
    save_covariance_matrices( options, d_Cov_Cor )
    return xsections_with_uncertainties_and_covariance           


def get_average_covariance_matrix( central_measurement, upper_measurement, lower_measurement, options, isTopMassSystematic, systematic ) :
    '''
    Calculates the covariance matrix for each source, by averaging the up/down variations in each bin:
        C(i,j) = 1 / 2 * ( up(i) * up(j) + down(i) * down(j) )

        Returns the covariance matrix, and the uncertainties in each bin (which are just the sqrt of the diagonal elements)

    '''

    number_of_bins = len(central_measurement)
    bin_indices = range(number_of_bins)
    covariance_matrix  = np.matrix( np.zeros( ( number_of_bins, number_of_bins ) ) )
    for i, j in product( bin_indices, bin_indices ):
        central_i = central_measurement[i][0]
        central_j = central_measurement[j][0]

        upper_variation_i = central_i - upper_measurement[i]
        upper_variation_j = central_j - upper_measurement[j]

        lower_variation_i = central_i - lower_measurement[i]
        lower_variation_j = central_j - lower_measurement[j]

        if isTopMassSystematic:
            upper_variation_i, lower_variation_i = scaleTopMassSystematic( upper_variation_i, lower_variation_i, options['topMasses'], options['topMassUncertainty'] )
            upper_variation_j, lower_variation_j = scaleTopMassSystematic( upper_variation_j, lower_variation_j, options['topMasses'], options['topMassUncertainty'] )


        covariance_ij = 0.5 * ( upper_variation_i * upper_variation_j + lower_variation_i * lower_variation_j )

        covariance_matrix[i,j] = covariance_ij

    # Extract uncertainties (for compatability later on)
    uncertainties = []
    for i in bin_indices:
        uncertainties.append( np.sqrt( covariance_matrix[i,i] ) )

    return uncertainties, covariance_matrix

# @profile(stream=fp)
def get_symmetrised_errors(central_measurement, upper_measurement, lower_measurement, options, isTopMassSystematic=False, systematic=None ):
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

# @profile(stream=fp)
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

# @profile(stream=fp)
def get_measurement_with_total_systematic_uncertainty(options, xsec_with_symmetrised_systematics):
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
        central = xsec_with_symmetrised_systematics['central'][bin_i] # Still [Value, Error]
        for systematic, measurement in xsec_with_symmetrised_systematics.iteritems():
            if systematic in ['central','CT14', 'MMHT14']: continue
            sys_unc += measurement[0][bin_i]**2

        measurement_with_total_uncertainty.append( [central[0], np.sqrt(sys_unc), np.sqrt(sys_unc)] )
    return measurement_with_total_uncertainty


# ------------------------------------------------------------------------------------------------------------------
# COVARIANCE MATRICES
# ------------------------------------------------------------------------------------------------------------------
### Generate Base Covariances
def generate_covariance_matrices(options, xsec_with_symmetrised_systematics):
    '''
    Generates the list of base covariance matrices
    '''
    number_of_bins  = options['number_of_bins']    

    d_Cov_Cor       = {}
    for syst, measurement in xsec_with_symmetrised_systematics.iteritems():
        if syst in ['central','CT14', 'MMHT14']: continue
        if syst in ['inputMC']: continue

        systematic  = measurement[0]
        sign        = measurement[1]

        # Create the matrices in numpy.matrix format
        covariance_matrix, correlation_matrix = generate_covariance_matrix(number_of_bins, systematic, sign, syst)
        d_Cov_Cor[syst] = [covariance_matrix, correlation_matrix]
    return d_Cov_Cor

def generate_covariance_matrix(number_of_bins, systematic, sign, syst):
    '''
    Variance_ii = (Unc_i) * (Unc_i)
    Covariance_ij = (Sign_i*Unc_i) * (Sign_j*Unc_j)
    Correlation_ij = (Sign_i*Unc_i) * (Sign_j*Unc_j)
                    ---------------------------------
                             (Unc_i * Unc_j)
    Returns the matrices in the form of a numpy matrix    
    '''
    # Create covariance matrix from signs and uncertainties
    covariance_matrix  = np.matrix( np.zeros( ( number_of_bins, number_of_bins ) ) )
    for i in range( 0, number_of_bins ):
        for j in range(0, number_of_bins ):
            covariance_matrix[i,j] = (sign[i]*systematic[i]) *  (sign[j]*systematic[j])

    # Create correlation matrix from covariance matrix
    correlation_matrix = correlation_from_covariance(covariance_matrix)

    return covariance_matrix, correlation_matrix

def correlation_from_covariance(covariance_matrix):
    '''
    Return the correlation matrix from the covariance matrix
    '''
    # Create correlation matrix from covariance matrix
    correlation_matrix = np.matrix( np.zeros( ( covariance_matrix.shape[0], covariance_matrix.shape[1] ) ) )
    for i in range( 0, covariance_matrix.shape[0] ):
        for j in range(0, covariance_matrix.shape[1] ):
            if ( covariance_matrix[i,i] * covariance_matrix[j,j] == 0 ):
                correlation_matrix[i,j] = 0
            else:
                correlation_matrix[i,j] = covariance_matrix[i,j] / sqrt( covariance_matrix[i,i] * covariance_matrix[j,j] )
    return correlation_matrix

### Add Covariances
def combine_covariance_matrices(l_cov):
    '''
    Return combined covariance matrices and resulting correlation matrix
    '''
    cov_combined = np.matrix( np.zeros( ( l_cov[0].shape[0], l_cov[0].shape[1] ) ) ) # Initialise
    for cov in l_cov:
        cov_combined+=cov

    cor_combined = correlation_from_covariance(cov_combined)

    return [cov_combined, cor_combined]

def add_covariance(options, d_Cov_Cor, addStat=False, addInputMCStat=False, addTotal=False):
    '''
    Add covariances together for total covariance matrix

    Cov_tot = Cov_stat + Cov_PDF + Cov_BJet ...
    Similarly for Correlation
    '''
    # Convert to numpy matrix and create total
    if addStat:
        covariance_template = '{path_to_DF}/central/covarianceMatrices/{norm}/Stat_{norm}Xsection_{label}_{channel}.txt'
        cov_path=covariance_template.format(
            norm=options['normalisation_type'], 
            path_to_DF=options['path_to_DF'], 
            channel=options['channel'], 
            label='Covariance',
        )
        cor_path = cov_path.replace('Covariance', 'Correlation')

        cov_stat = file_to_df(cov_path)
        cor_stat = file_to_df(cor_path)
        cov_stat = matrix_from_df(cov_stat)
        cor_stat = matrix_from_df(cor_stat)
        return [cov_stat, cor_stat]

    # inputMC covariance matrix
    if addInputMCStat:
        _, cov_inputMC = add_inputMC_systematic(options)
        cor_inputMC = correlation_from_covariance(cov_inputMC)
        return [cov_inputMC, cor_inputMC]

    if addTotal:
        number_of_bins = options['number_of_bins']
        cov_tot  = np.matrix( np.zeros( ( number_of_bins, number_of_bins ) ) )
        for syst, cov_cor in d_Cov_Cor.iteritems():
            cov_tot += cov_cor[0]
        cor_tot = correlation_from_covariance(cov_tot)
        return [cov_tot, cor_tot]
    return None

def add_inputMC_systematic(options):
    '''
    Add a systematic uncertainty based on the input MC distribution for unfolding
    '''
    unc, sign = 0, 0
    # Paths to statistical Covariance/Correlation matrices.
    covariance_template = '{path_to_DF}/central/covarianceMatrices/{norm}/Stat_{norm}Xsection_inputMC_{label}_{channel}.txt'
    cov_path=covariance_template.format(
        norm=options['normalisation_type'], 
        path_to_DF=options['path_to_DF'], 
        channel=options['channel'], 
        label='Covariance',
    )
    # Convert to numpy matrix and create total
    cov_inputMC = file_to_df(cov_path)
    cov_inputMC = matrix_from_df(cov_inputMC)
    unc2 = np.diagonal(cov_inputMC)
    unc = np.sqrt(unc2)

    # Retain structure
    sign = np.zeros(len(unc))

    return [unc, sign], cov_inputMC

### OUTPUT COVARIANCES
def save_covariance_matrices(options, d_Cov_Cor_matrices):
    '''
    Save covariance matrices
    '''
    path_to_DF      = options['path_to_DF']
    channel         = options['channel']
    norm            = options['normalisation_type']

    covariance_output_template  = '{path_to_DF}/central/covarianceMatrices/{norm}/{sys}_{label}_{channel}.txt'
    if options['mcUncertainty']:
        covariance_output_template  = '{path_to_DF}/central/covarianceMatrices/mcUncertainty/{norm}/{sys}_{label}_{channel}.txt'

    for syst, cov_cor in d_Cov_Cor_matrices.iteritems():
        cov = cov_cor[0]
        cor = cov_cor[1]

        # Convert the matrices to DF format, output and plot them
        table_outfile = covariance_output_template.format( 
            path_to_DF=path_to_DF, 
            sys=syst, 
            channel=channel, 
            label='Covariance',
            norm=norm,
        )
        create_covariance_matrix(cov, table_outfile)
        table_outfile = table_outfile.replace("Covariance", "Correlation")
        create_covariance_matrix(cor, table_outfile)

        if syst == 'Total':
            make_covariance_plot(options, syst, cov, label='Covariance')
            make_covariance_plot(options, syst, cor, label='Correlation')
        # make_covariance_plot(options, syst, cov, label='Covariance')
        # make_covariance_plot(options, syst, cor, label='Correlation')
    return

def make_covariance_plot( options, syst_name, matrix, label='Covariance' ):    
    '''
    Take the matrix in list form and bin edges in list form to create a TH2F of the covariance matrix
    Saves to plots/covariance_matrices/{PhaseSpace}/{Channel}/{Variable}/
    '''
    variable = options['variable']
    channel = options['channel']
    phase_space = options['phase_space']
    norm=options['normalisation_type']

    matrix_max = matrix.max()
    matrix_min = matrix.min()

    if( matrix_max == 0):
        return

    fig = plt.figure( figsize = CMS.figsize, dpi = CMS.dpi, facecolor = CMS.facecolor )
    ax = fig.add_subplot(1,1,1)
    ax.set_aspect('equal')
    if label=='Correlation':
        im=plt.imshow(matrix, interpolation='nearest', cmap = my_cmap, vmin = -1, vmax = 1 )
    else:
        im=plt.imshow(matrix, interpolation='nearest', cmap = my_cmap )

    plt_title = variables_latex[variable]+' '+title
    if variable in ['HT', 'MET', 'WPT', 'ST', 'lepton_pt']:
        plt_title += ' [GeV]'

    ax.invert_yaxis()

    x_title = 'Bin i'
    y_title = 'Bin j'
    plt.title( plt_title,loc='right', **CMS.title )
    plt.xlabel( x_title, CMS.x_axis_title )
    plt.ylabel( y_title, CMS.y_axis_title )
    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor ) 
    plt.colorbar(im,fraction=0.046, pad=0.04)
    plt.tight_layout()

    # Output folder of covariance matrices
    covariance_matrix_output_path = 'plots/covariance_matrices/{phase_space}/{channel}/{norm}/'
    if options['mcUncertainty']:
        covariance_matrix_output_path = 'plots/covariance_matrices/mcUncertainty/{phase_space}/{channel}/{norm}/'
    covariance_matrix_output_path = covariance_matrix_output_path.format(
        channel = channel,
        phase_space = phase_space,
        norm = norm,
        )
    make_folder_if_not_exists(covariance_matrix_output_path)
    plt.savefig(covariance_matrix_output_path+syst_name+'_'+variable+'_'+label+'_matrix.pdf')
    fig.clf()
    plt.close()
    gc.collect()


# ------------------------------------------------------------------------------------------------------------------
# HELPER
# ------------------------------------------------------------------------------------------------------------------

# @profile(stream=fp)
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
