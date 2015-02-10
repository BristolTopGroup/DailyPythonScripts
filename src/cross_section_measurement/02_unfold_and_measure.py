# general
from __future__ import division
from optparse import OptionParser
import os
# from array import array
# rootpy
from rootpy.io import File
from rootpy.plotting import Hist2D
# DailyPythonScripts
import config.RooUnfold as unfoldCfg
from config.variable_binning import bin_widths, bin_edges
from config import XSectionConfig
from tools.Calculation import calculate_xsection, calculate_normalised_xsection, \
combine_complex_results
from tools.hist_utilities import hist_to_value_error_tuplelist, \
value_error_tuplelist_to_hist
from tools.Unfolding import Unfolding, get_unfold_histogram_tuple
from tools.file_utilities import read_data_from_JSON, write_data_to_JSON, \
make_folder_if_not_exists
from copy import deepcopy
from tools.ROOT_utils import set_root_defaults

def unfold_results( results, category, channel, k_value, h_truth, h_measured, h_response, h_fakes, method ):
    global variable, path_to_JSON, options
    h_data = value_error_tuplelist_to_hist( results, bin_edges[variable] )
    unfolding = Unfolding( h_truth, h_measured, h_response, h_fakes, method = method, k_value = k_value )
    
    # turning off the unfolding errors for systematic samples
    if not category == 'central':
        unfoldCfg.Hreco = 0
    else:
        unfoldCfg.Hreco = options.Hreco
        
    h_unfolded_data = unfolding.unfold( h_data )
    
    if options.write_unfolding_objects:
        # export the D and SV distributions
        SVD_path = path_to_JSON + '/unfolding_objects/' + channel + '/kv_' + str( k_value ) + '/'
        make_folder_if_not_exists( SVD_path )
        if method == 'TSVDUnfold':
            SVDdist = File( SVD_path + method + '_SVDdistributions_' + category + '.root', 'recreate' )
            directory = SVDdist.mkdir( 'SVDdist' )
            directory.cd()
            unfolding.unfoldObject.GetD().Write()
            unfolding.unfoldObject.GetSV().Write()
            #    unfolding.unfoldObject.GetUnfoldCovMatrix(data_covariance_matrix(h_data), unfoldCfg.SVD_n_toy).Write()
            SVDdist.Close()
        else:
            SVDdist = File( SVD_path + method + '_SVDdistributions_Hreco' + str( unfoldCfg.Hreco ) + '_' + category + '.root', 'recreate' )
            directory = SVDdist.mkdir( 'SVDdist' )
            directory.cd()
            unfolding.unfoldObject.Impl().GetD().Write()
            unfolding.unfoldObject.Impl().GetSV().Write()
            h_truth.Write()
            h_measured.Write()
            h_response.Write()
            #    unfolding.unfoldObject.Impl().GetUnfoldCovMatrix(data_covariance_matrix(h_data), unfoldCfg.SVD_n_toy).Write()
            SVDdist.Close()
    
        # export the whole unfolding object if it doesn't exist
        if method == 'TSVDUnfold':
            unfolding_object_file_name = SVD_path + method + '_unfoldingObject_' + category + '.root'
        else:
            unfolding_object_file_name = SVD_path + method + '_unfoldingObject_Hreco' + str( unfoldCfg.Hreco ) + '_' + category + '.root'
        if not os.path.isfile( unfolding_object_file_name ):
            unfoldingObjectFile = File( unfolding_object_file_name, 'recreate' )
            directory = unfoldingObjectFile.mkdir( 'unfoldingObject' )
            directory.cd()
            if method == 'TSVDUnfold':
                unfolding.unfoldObject.Write()
            else:
                unfolding.unfoldObject.Impl().Write()
            unfoldingObjectFile.Close()
    
    del unfolding
    return hist_to_value_error_tuplelist( h_unfolded_data )

def data_covariance_matrix( data ):
    values = list( data )
    get_bin_error = data.GetBinError
    cov_matrix = Hist2D( len( values ), -10, 10, len( values ), -10, 10, type = 'D' )
    for bin_i in range( len( values ) ):
        error = get_bin_error( bin_i + 1 )
        cov_matrix.SetBinContent( bin_i + 1, bin_i + 1, error * error )
    return cov_matrix

def get_unfolded_normalisation( TTJet_fit_results, category, channel, k_value ):
    global variable, met_type, path_to_JSON, file_for_unfolding, file_for_powheg_pythia, file_for_powheg_herwig, file_for_ptreweight, files_for_pdfs
    global centre_of_mass, luminosity, ttbar_xsection, load_fakes, method
    if centre_of_mass == 8:
        global file_for_mcatnlo
    global file_for_matchingdown, file_for_matchingup, file_for_scaledown, file_for_scaleup
    global file_for_massdown, file_for_massup
    global ttbar_generator_systematics, ttbar_theory_systematics, pdf_uncertainties
    global use_ptreweight

    files_for_systematics = {
                             ttbar_theory_systematic_prefix + 'matchingdown':file_for_matchingdown,
                             ttbar_theory_systematic_prefix + 'matchingup':file_for_matchingup,
                             ttbar_theory_systematic_prefix + 'scaledown':file_for_scaledown,
                             ttbar_theory_systematic_prefix + 'scaleup':file_for_scaleup,
                             ttbar_theory_systematic_prefix + 'massdown':file_for_massdown,
                             ttbar_theory_systematic_prefix + 'massup':file_for_massup,
                             ttbar_theory_systematic_prefix + 'powheg_pythia':file_for_powheg_pythia,
                             ttbar_theory_systematic_prefix + 'powheg_herwig':file_for_powheg_herwig,
                             ttbar_theory_systematic_prefix + 'ptreweight':file_for_ptreweight,
                             }
    
    h_truth, h_measured, h_response, h_fakes = None, None, None, None
    if category in ttbar_generator_systematics or category in ttbar_theory_systematics or category in ttbar_mass_systematics:
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( inputfile = files_for_systematics[category],
                                                                              variable = variable,
                                                                              channel = channel,
                                                                              met_type = met_type,
                                                                              centre_of_mass = centre_of_mass,
                                                                              ttbar_xsection = ttbar_xsection,
                                                                              luminosity = luminosity,
                                                                              load_fakes = load_fakes
                                                                              )
    elif category in pdf_uncertainties:
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( inputfile = files_for_pdfs[category],
                                                                              variable = variable,
                                                                              channel = channel,
                                                                              met_type = met_type,
                                                                              centre_of_mass = centre_of_mass,
                                                                              ttbar_xsection = ttbar_xsection,
                                                                              luminosity = luminosity,
                                                                              load_fakes = load_fakes
                                                                              )
    elif use_ptreweight:
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( inputfile = file_for_ptreweight,
                                                                              variable = variable,
                                                                              channel = channel,
                                                                              met_type = met_type,
                                                                              centre_of_mass = centre_of_mass,
                                                                              ttbar_xsection = ttbar_xsection,
                                                                              luminosity = luminosity,
                                                                              load_fakes = load_fakes
                                                                              )
    else:
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( inputfile = file_for_unfolding,
                                                                              variable = variable,
                                                                              channel = channel,
                                                                              met_type = met_type,
                                                                              centre_of_mass = centre_of_mass,
                                                                              ttbar_xsection = ttbar_xsection,
                                                                              luminosity = luminosity,
                                                                              load_fakes = load_fakes
                                                                              )

    h_truth_POWHEG_PYTHIA, _, _, _ = get_unfold_histogram_tuple( inputfile = file_for_powheg_pythia,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes
                                                )
    h_truth_POWHEG_HERWIG, _, _, _ = get_unfold_histogram_tuple( inputfile = file_for_powheg_herwig,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes
                                                )
    if centre_of_mass == 8:
        h_truth_MCATNLO, _, _, _ = get_unfold_histogram_tuple( inputfile = file_for_mcatnlo,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes
                                                )
    h_truth_matchingdown, _, _, _ = get_unfold_histogram_tuple( inputfile = file_for_matchingdown,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes
                                                )
    h_truth_matchingup, _, _, _ = get_unfold_histogram_tuple( inputfile = file_for_matchingup,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes
                                                )
    h_truth_scaledown, _, _, _ = get_unfold_histogram_tuple( inputfile = file_for_scaledown,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes
                                                )
    h_truth_scaleup, _, _, _ = get_unfold_histogram_tuple( inputfile = file_for_scaleup,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes
                                                )
    h_truth_ptreweight, _, _, _ = get_unfold_histogram_tuple(
                                                inputfile = file_for_ptreweight,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes
                                                )

    MADGRAPH_results = hist_to_value_error_tuplelist( h_truth )
    MADGRAPH_ptreweight_results = hist_to_value_error_tuplelist( h_truth_ptreweight )
    POWHEG_PYTHIA_results = hist_to_value_error_tuplelist( h_truth_POWHEG_PYTHIA )
    POWHEG_HERWIG_results = hist_to_value_error_tuplelist( h_truth_POWHEG_HERWIG )
    if centre_of_mass == 8:
        MCATNLO_results = hist_to_value_error_tuplelist( h_truth_MCATNLO )
    
    matchingdown_results = hist_to_value_error_tuplelist( h_truth_matchingdown )
    matchingup_results = hist_to_value_error_tuplelist( h_truth_matchingup )
    scaledown_results = hist_to_value_error_tuplelist( h_truth_scaledown )
    scaleup_results = hist_to_value_error_tuplelist( h_truth_scaleup )

    TTJet_fit_results_unfolded = unfold_results( TTJet_fit_results,
                                                category,
                                                channel,
                                                k_value,
                                                h_truth,
                                                h_measured,
                                                h_response,
                                                h_fakes,
                                                method
                                                )
        
    if centre_of_mass == 8:
        normalisation_unfolded = {
                              'TTJet_measured' : TTJet_fit_results,
                              'TTJet_unfolded' : TTJet_fit_results_unfolded,
                              'MADGRAPH': MADGRAPH_results,
                              'MADGRAPH_ptreweight': MADGRAPH_ptreweight_results,
                              # other generators
                              'POWHEG_PYTHIA': POWHEG_PYTHIA_results,
                              'POWHEG_HERWIG': POWHEG_HERWIG_results,
                              'MCATNLO': MCATNLO_results,
                              # systematics
                              'matchingdown': matchingdown_results,
                              'matchingup': matchingup_results,
                              'scaledown': scaledown_results,
                              'scaleup': scaleup_results
                              }
    else:
        normalisation_unfolded = {
                              'TTJet_measured' : TTJet_fit_results,
                              'TTJet_unfolded' : TTJet_fit_results_unfolded,
                              'MADGRAPH': MADGRAPH_results,
                              'MADGRAPH_ptreweight': MADGRAPH_ptreweight_results,
                              # other generators
                              'POWHEG_PYTHIA': POWHEG_PYTHIA_results,
                              'POWHEG_HERWIG': POWHEG_HERWIG_results,
                              # systematics
                              'matchingdown': matchingdown_results,
                              'matchingup': matchingup_results,
                              'scaledown': scaledown_results,
                              'scaleup': scaleup_results
                              }
    return normalisation_unfolded
    
def calculate_xsections( normalisation, category, channel, k_value = None ):
    global variable, met_type, path_to_JSON
    # calculate the x-sections
    branching_ratio = 0.15
    if channel == 'combined':
        branching_ratio = branching_ratio * 2
    TTJet_xsection = calculate_xsection( normalisation['TTJet_measured'], luminosity, branching_ratio )  # L in pb1
    TTJet_xsection_unfolded = calculate_xsection( normalisation['TTJet_unfolded'], luminosity, branching_ratio )  # L in pb1
    MADGRAPH_xsection = calculate_xsection( normalisation['MADGRAPH'], luminosity, branching_ratio )  # L in pb1
    MADGRAPH_ptreweight_xsection = calculate_xsection( normalisation['MADGRAPH_ptreweight'], luminosity, branching_ratio )  # L in pb1
    POWHEG_PYTHIA_xsection = calculate_xsection( normalisation['POWHEG_PYTHIA'], luminosity, branching_ratio )  # L in pb1
    POWHEG_HERWIG_xsection = calculate_xsection( normalisation['POWHEG_HERWIG'], luminosity, branching_ratio )  # L in pb1
    if centre_of_mass == 8:
        MCATNLO_xsection = calculate_xsection( normalisation['MCATNLO'], luminosity, branching_ratio )  # L in pb1
    matchingdown_xsection = calculate_xsection( normalisation['matchingdown'], luminosity, branching_ratio )  # L in pb1
    matchingup_xsection = calculate_xsection( normalisation['matchingup'], luminosity, branching_ratio )  # L in pb1
    scaledown_xsection = calculate_xsection( normalisation['scaledown'], luminosity, branching_ratio )  # L in pb1
    scaleup_xsection = calculate_xsection( normalisation['scaleup'], luminosity, branching_ratio )  # L in pb1
    
    if centre_of_mass == 8:
        xsection_unfolded = {'TTJet_measured' : TTJet_xsection,
                         'TTJet_unfolded' : TTJet_xsection_unfolded,
                         'MADGRAPH': MADGRAPH_xsection,
                         'MADGRAPH_ptreweight': MADGRAPH_ptreweight_xsection,
                         'POWHEG_PYTHIA': POWHEG_PYTHIA_xsection,
                         'POWHEG_HERWIG': POWHEG_HERWIG_xsection,
                         'MCATNLO': MCATNLO_xsection,
                         # systematics
                         'matchingdown': matchingdown_xsection,
                         'matchingup': matchingup_xsection,
                         'scaledown': scaledown_xsection,
                         'scaleup': scaleup_xsection
                         }
    else:
        xsection_unfolded = {'TTJet_measured' : TTJet_xsection,
                         'TTJet_unfolded' : TTJet_xsection_unfolded,
                         'MADGRAPH': MADGRAPH_xsection,
                         'MADGRAPH_ptreweight': MADGRAPH_ptreweight_xsection,
                         'POWHEG_PYTHIA': POWHEG_PYTHIA_xsection,
                         'POWHEG_HERWIG': POWHEG_HERWIG_xsection,
                         # systematics
                         'matchingdown': matchingdown_xsection,
                         'matchingup': matchingup_xsection,
                         'scaledown': scaledown_xsection,
                         'scaleup': scaleup_xsection
                         }
    if k_value:
        filename = path_to_JSON + '/xsection_measurement_results/%s/kv%d/%s/xsection_%s.txt' % ( channel, k_value, category, met_type )
    elif not channel == 'combined':
        raise ValueError( 'Invalid k-value for variable %s, channel %s, category %s.' % ( variable, channel, category ) )
    else:
        filename = path_to_JSON + '/xsection_measurement_results/%s/%s/xsection_%s.txt' % ( channel, category, met_type )

    write_data_to_JSON( xsection_unfolded, filename )
    
def calculate_normalised_xsections( normalisation, category, channel, k_value = None, normalise_to_one = False ):
    global variable, met_type, path_to_JSON
    TTJet_normalised_xsection = calculate_normalised_xsection( normalisation['TTJet_measured'], bin_widths[variable], normalise_to_one )
    TTJet_normalised_xsection_unfolded = calculate_normalised_xsection( normalisation['TTJet_unfolded'], bin_widths[variable], normalise_to_one )
    MADGRAPH_normalised_xsection = calculate_normalised_xsection( normalisation['MADGRAPH'], bin_widths[variable], normalise_to_one )
    MADGRAPH_ptreweight_normalised_xsection = calculate_normalised_xsection( normalisation['MADGRAPH_ptreweight'], bin_widths[variable], normalise_to_one )
    POWHEG_PYTHIA_normalised_xsection = calculate_normalised_xsection( normalisation['POWHEG_PYTHIA'], bin_widths[variable], normalise_to_one )
    POWHEG_HERWIG_normalised_xsection = calculate_normalised_xsection( normalisation['POWHEG_HERWIG'], bin_widths[variable], normalise_to_one )
    if centre_of_mass == 8:
        MCATNLO_normalised_xsection = calculate_normalised_xsection( normalisation['MCATNLO'], bin_widths[variable], normalise_to_one )
    matchingdown_normalised_xsection = calculate_normalised_xsection( normalisation['matchingdown'], bin_widths[variable], normalise_to_one )
    matchingup_normalised_xsection = calculate_normalised_xsection( normalisation['matchingup'], bin_widths[variable], normalise_to_one )
    scaledown_normalised_xsection = calculate_normalised_xsection( normalisation['scaledown'], bin_widths[variable], normalise_to_one )
    scaleup_normalised_xsection = calculate_normalised_xsection( normalisation['scaleup'], bin_widths[variable], normalise_to_one )
    
    if centre_of_mass == 8:
        normalised_xsection = {'TTJet_measured' : TTJet_normalised_xsection,
                           'TTJet_unfolded' : TTJet_normalised_xsection_unfolded,
                           'MADGRAPH': MADGRAPH_normalised_xsection,
                           'MADGRAPH_ptreweight': MADGRAPH_ptreweight_normalised_xsection,
                           'POWHEG_PYTHIA': POWHEG_PYTHIA_normalised_xsection,
                           'POWHEG_HERWIG': POWHEG_HERWIG_normalised_xsection,
                           'MCATNLO': MCATNLO_normalised_xsection,
                           # systematics
                           'matchingdown': matchingdown_normalised_xsection,
                           'matchingup': matchingup_normalised_xsection,
                           'scaledown': scaledown_normalised_xsection,
                           'scaleup': scaleup_normalised_xsection
                           }
    else:
        normalised_xsection = {'TTJet_measured' : TTJet_normalised_xsection,
                           'TTJet_unfolded' : TTJet_normalised_xsection_unfolded,
                           'MADGRAPH': MADGRAPH_normalised_xsection,
                           'MADGRAPH_ptreweight': MADGRAPH_ptreweight_normalised_xsection,
                           'POWHEG_PYTHIA': POWHEG_PYTHIA_normalised_xsection,
                           'POWHEG_HERWIG': POWHEG_HERWIG_normalised_xsection,
                           # systematics
                           'matchingdown': matchingdown_normalised_xsection,
                           'matchingup': matchingup_normalised_xsection,
                           'scaledown': scaledown_normalised_xsection,
                           'scaleup': scaleup_normalised_xsection
                           }
    
    if not channel == 'combined':
        filename = path_to_JSON + '/xsection_measurement_results/%s/kv%d/%s/normalised_xsection_%s.txt' % ( channel, k_value, category, met_type )        
    else:
        filename = path_to_JSON + '/xsection_measurement_results/%s/%s/normalised_xsection_%s.txt' % ( channel, category, met_type )
    
    if normalise_to_one:
        filename = filename.replace( 'normalised_xsection', 'normalised_to_one_xsection' )
    write_data_to_JSON( normalised_xsection, filename )

if __name__ == '__main__':
    set_root_defaults( msg_ignore_level = 3001 )
    # setup
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data/',
                      help = "set path to JSON files" )
    parser.add_option( "-v", "--variable", dest = "variable", default = 'MET',
                      help = "set the variable to analyse (MET, HT, ST, MT)" )
    parser.add_option( "-b", "--bjetbin", dest = "bjetbin", default = '2m',
                      help = "set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m" )
    parser.add_option( "-m", "--metType", dest = "metType", default = 'type1',
                      help = "set MET type for analysis of MET, ST or MT" )
    parser.add_option( "-f", "--load_fakes", dest = "load_fakes", action = "store_true",
                      help = "Load fakes histogram and perform manual fake subtraction in TSVDUnfold" )
    parser.add_option( "-u", "--unfolding_method", dest = "unfolding_method", default = 'RooUnfoldSvd',
                      help = "Unfolding method: RooUnfoldSvd (default), TSVDUnfold, TopSVDUnfold, RooUnfoldTUnfold, RooUnfoldInvert, RooUnfoldBinByBin, RooUnfoldBayes" )
    parser.add_option( "-H", "--hreco", type = 'int',
                      dest = "Hreco", default = 2,
                      help = "Hreco parameter for error treatment in RooUnfold" )
    parser.add_option( "-c", "--centre-of-mass-energy", dest = "CoM", default = 8,
                      help = "set the centre of mass energy for analysis. Default = 8 [TeV]", type = int )
    parser.add_option( "-C", "--combine-before-unfolding", dest = "combine_before_unfolding", action = "store_true",
                      help = "Perform combination of channels before unfolding" )
    parser.add_option( "-w", "--write-unfolding-objects", dest = "write_unfolding_objects", action = "store_true",
                      help = "Write out the unfolding objects (D, SV)" )
    parser.add_option( '--test', dest = "test", action = "store_true",
                      help = "Just run the central measurement" )
    parser.add_option( '--ptreweight', dest = "ptreweight", action = "store_true",
                      help = "Use pt-reweighted MadGraph for the measurement" )
    
    
    ( options, args ) = parser.parse_args()
    measurement_config = XSectionConfig( options.CoM )
    run_just_central = options.test
    use_ptreweight = options.ptreweight
    # caching of variables for faster access
    translate_options = measurement_config.translate_options
    ttbar_theory_systematic_prefix = measurement_config.ttbar_theory_systematic_prefix
    vjets_theory_systematic_prefix = measurement_config.vjets_theory_systematic_prefix
    met_systematics_suffixes = measurement_config.met_systematics_suffixes
    
    centre_of_mass = options.CoM
    luminosity = measurement_config.luminosity * measurement_config.luminosity_scale
    ttbar_xsection = measurement_config.ttbar_xsection
    path_to_files = measurement_config.path_to_files
    
    file_for_unfolding = File( measurement_config.unfolding_madgraph, 'read' )
    file_for_powheg_pythia = File( measurement_config.unfolding_powheg_pythia, 'read' )
    file_for_powheg_herwig = File( measurement_config.unfolding_powheg_herwig, 'read' )
    if centre_of_mass == 8:
        file_for_mcatnlo = File( measurement_config.unfolding_mcatnlo, 'read' )
    file_for_ptreweight = File ( measurement_config.unfolding_ptreweight, 'read' )
    files_for_pdfs = { 'PDFWeights_%d' % index : File ( measurement_config.unfolding_pdfweights[index] ) for index in range( 1, 45 ) }
        
    file_for_scaledown = File( measurement_config.unfolding_scale_down, 'read' )
    file_for_scaleup = File( measurement_config.unfolding_scale_up, 'read' )
    file_for_matchingdown = File( measurement_config.unfolding_matching_down, 'read' )
    file_for_matchingup = File( measurement_config.unfolding_matching_up, 'read' )

    file_for_massdown = File( measurement_config.unfolding_mass_down, 'read' )
    file_for_massup = File( measurement_config.unfolding_mass_up, 'read' )

    variable = options.variable
    k_value_electron_central = measurement_config.k_values_electron[variable]
    k_value_muon_central = measurement_config.k_values_muon[variable]
    k_value_combined_central = measurement_config.k_values_combined[variable]
    load_fakes = options.load_fakes
    unfoldCfg.Hreco = options.Hreco
    method = options.unfolding_method
    combine_before_unfolding = options.combine_before_unfolding
    met_type = translate_options[options.metType]
    b_tag_bin = translate_options[options.bjetbin]
    path_to_JSON = options.path + '/' + str( measurement_config.centre_of_mass_energy ) + 'TeV/' + variable + '/'
    
    categories = deepcopy( measurement_config.categories_and_prefixes.keys() )
    ttbar_generator_systematics = [ttbar_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    vjets_generator_systematics = [vjets_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    categories.extend( ttbar_generator_systematics )
    categories.extend( vjets_generator_systematics )

    # ttbar theory systematics, including pt reweighting and hadronisation systematic
    ttbar_theory_systematics = [] #[ ttbar_theory_systematic_prefix + 'ptreweight' ]
    ttbar_theory_systematics.extend( [ttbar_theory_systematic_prefix + 'powheg_pythia', ttbar_theory_systematic_prefix + 'powheg_herwig'] )
    categories.extend( ttbar_theory_systematics )

    # Add mass systematics
    ttbar_mass_systematics = measurement_config.topMass_systematics
    categories.extend( measurement_config.topMass_systematics )

    # Add k Value systematic
    kValue_systematics = measurement_config.kValueSystematic
    categories.extend( measurement_config.kValueSystematic )

    pdf_uncertainties = ['PDFWeights_%d' % index for index in range( 1, 45 )]
    rate_changing_systematics = [systematic + '+' for systematic in measurement_config.rate_changing_systematics.keys()]
    rate_changing_systematics.extend( [systematic + '-' for systematic in measurement_config.rate_changing_systematics.keys()] )

    # all MET uncertainties except JES as this is already included
    met_uncertainties = [met_type + suffix for suffix in met_systematics_suffixes if not 'JetEn' in suffix and not 'JetRes' in suffix]
    all_measurements = deepcopy( categories )
    all_measurements.extend( pdf_uncertainties )
    all_measurements.extend( met_uncertainties )
    all_measurements.extend( ['QCD_shape'] )
    all_measurements.extend( rate_changing_systematics )

    print 'Performing unfolding for variable', variable
    for category in all_measurements:
        if run_just_central and not category == 'central':
            continue
        if variable == 'HT' and category in met_uncertainties:
            continue
        print 'Unfolding category "%s"' % category
        # Setting up systematic MET for JES up/down samples
        met_type = translate_options[options.metType]
        
        if category == 'JES_up':
            met_type += 'JetEnUp'
            if met_type == 'PFMETJetEnUp':
                met_type = 'patPFMetJetEnUp'
        elif category == 'JES_down':
            met_type += 'JetEnDown'
            if met_type == 'PFMETJetEnDown':
                met_type = 'patPFMetJetEnDown'

        # Choose k Value
        k_value_electron = k_value_electron_central
        k_value_muon = k_value_muon_central
        k_value_combined = k_value_combined_central
        if category == 'kValue_up':
          k_value_electron = k_value_electron_central+1
          k_value_muon = k_value_muon_central+1
          k_value_combined = k_value_combined_central+1
        elif category == 'kValue_down':         
          k_value_electron = k_value_electron_central-1
          if k_value_electron < 2 : k_value_electron = 2
          k_value_muon = k_value_muon_central-1
          if k_value_muon < 2 : k_value_muon = 2
          k_value_combined = k_value_combined_central-1
          if k_value_combined < 2 : k_value_combined = 2

        # read fit results from JSON
        electron_file = path_to_JSON + '/fit_results/' + category + '/fit_results_electron_' + met_type + '.txt'
        muon_file = path_to_JSON + '/fit_results/' + category + '/fit_results_muon_' + met_type + '.txt'
        combined_file = path_to_JSON + '/fit_results/' + category + '/fit_results_combined_' + met_type + '.txt'

        # don't change fit input for ttbar generator/theory systematics and PDF weights
        if category in ttbar_generator_systematics or category in ttbar_theory_systematics or category in pdf_uncertainties or category in ttbar_mass_systematics or category in kValue_systematics:
            electron_file = path_to_JSON + '/fit_results/central/fit_results_electron_' + met_type + '.txt'
            muon_file = path_to_JSON + '/fit_results/central/fit_results_muon_' + met_type + '.txt'
            combined_file = path_to_JSON + '/fit_results/central/fit_results_combined_' + met_type + '.txt'
        
        fit_results_electron = read_data_from_JSON( electron_file )
        fit_results_muon = read_data_from_JSON( muon_file )
        fit_results_combined = read_data_from_JSON( combined_file )
        TTJet_fit_results_electron = fit_results_electron['TTJet']
        TTJet_fit_results_muon = fit_results_muon['TTJet']
        TTJet_fit_results_combined = fit_results_combined['TTJet']
        
        # change back to original MET type for the unfolding
        met_type = translate_options[options.metType]
        # ad-hoc switch for PFMET -> patMETsPFlow
        if met_type == 'PFMET':
            met_type = 'patMETsPFlow'
        
        filename = ''

        # get unfolded normalisation
        unfolded_normalisation_electron = get_unfolded_normalisation( TTJet_fit_results_electron, category, 'electron', k_value_electron )
        unfolded_normalisation_muon = get_unfolded_normalisation( TTJet_fit_results_muon, category, 'muon', k_value_muon )
        if combine_before_unfolding:
            unfolded_normalisation_combined = get_unfolded_normalisation( TTJet_fit_results_combined, category, 'combined', k_value_combined )
        else:
            unfolded_normalisation_combined = combine_complex_results( unfolded_normalisation_electron, unfolded_normalisation_muon )

        filename = path_to_JSON + '/xsection_measurement_results/electron/kv%d/%s/normalisation_%s.txt' % ( k_value_electron_central, category, met_type )
        write_data_to_JSON( unfolded_normalisation_electron, filename )
        filename = path_to_JSON + '/xsection_measurement_results/muon/kv%d/%s/normalisation_%s.txt' % ( k_value_muon_central, category, met_type )
        write_data_to_JSON( unfolded_normalisation_muon, filename )
        filename = path_to_JSON + '/xsection_measurement_results/combined/%s/normalisation_%s.txt' % ( category, met_type )
        write_data_to_JSON( unfolded_normalisation_combined, filename )
        
        if measurement_config.include_higgs:
            # now the same for the Higgs
            Higgs_fit_results_electron = fit_results_electron['Higgs']
            Higgs_fit_results_muon = fit_results_muon['Higgs']
            Higgs_fit_results_combined = fit_results_combined['Higgs']
            unfolded_normalisation_electron_higgs = get_unfolded_normalisation( fit_results_electron['Higgs'], category, 'electron', k_value_electron )
            unfolded_normalisation_muon_higgs = get_unfolded_normalisation( fit_results_muon['Higgs'], category, 'muon', k_value_muon )
            if combine_before_unfolding:
                unfolded_normalisation_combined_higgs = get_unfolded_normalisation( fit_results_combined['Higgs'], category, 'combined', k_value_combined )
            else:
                unfolded_normalisation_combined_higgs = combine_complex_results( unfolded_normalisation_electron_higgs, unfolded_normalisation_muon_higgs )
    
            filename = path_to_JSON + '/xsection_measurement_results/electron/kv%d/%s/normalisation_%s_Higgs.txt' % ( k_value_electron_central, category, met_type )
            write_data_to_JSON( unfolded_normalisation_electron_higgs, filename )
            filename = path_to_JSON + '/xsection_measurement_results/muon/kv%d/%s/normalisation_%s_Higgs.txt' % ( k_value_muon_central, category, met_type )
            write_data_to_JSON( unfolded_normalisation_muon_higgs, filename )
            filename = path_to_JSON + '/xsection_measurement_results/combined/%s/normalisation_%s_Higgs.txt' % ( category, met_type )
            write_data_to_JSON( unfolded_normalisation_combined_higgs, filename )

        # measure xsection
        calculate_xsections( unfolded_normalisation_electron, category, 'electron', k_value_electron_central )
        calculate_xsections( unfolded_normalisation_muon, category, 'muon', k_value_muon_central )
        calculate_xsections( unfolded_normalisation_combined, category, 'combined' )
        
        calculate_normalised_xsections( unfolded_normalisation_electron, category, 'electron', k_value_electron_central )
        calculate_normalised_xsections( unfolded_normalisation_muon, category, 'muon', k_value_muon_central )
        calculate_normalised_xsections( unfolded_normalisation_combined, category, 'combined' )
        
        normalise_to_one = True
        calculate_normalised_xsections( unfolded_normalisation_electron, category, 'electron', k_value_electron_central, normalise_to_one )
        calculate_normalised_xsections( unfolded_normalisation_muon, category, 'muon', k_value_muon_central, normalise_to_one )
        calculate_normalised_xsections( unfolded_normalisation_combined, category, 'combined', normalise_to_one )
