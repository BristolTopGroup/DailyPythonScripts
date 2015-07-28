# general
from __future__ import division
from optparse import OptionParser
# from array import array
# rootpy
from rootpy.io import File
from rootpy.plotting import Hist2D
# DailyPythonScripts
import config.RooUnfold as unfoldCfg
from config.variable_binning import bin_widths, bin_edges, bin_edges_vis
from config import XSectionConfig
from tools.Calculation import calculate_xsection, calculate_normalised_xsection, \
combine_complex_results
from tools.hist_utilities import hist_to_value_error_tuplelist, \
value_error_tuplelist_to_hist
from tools.Unfolding import Unfolding, get_unfold_histogram_tuple
from tools.file_utilities import read_data_from_JSON, write_data_to_JSON
from copy import deepcopy
from tools.ROOT_utils import set_root_defaults

def unfold_results( results, category, channel, tau_value, h_truth, h_measured, h_response, h_fakes, method, visiblePS ):
    global variable, path_to_JSON, options
    edges = bin_edges[variable]
    if visiblePS:
        edges = bin_edges_vis[variable]
    h_data = value_error_tuplelist_to_hist( results, edges )
    unfolding = Unfolding( h_truth, h_measured, h_response, h_fakes, method = method, k_value = -1, tau = tau_value )

    # turning off the unfolding errors for systematic samples
    if not category == 'central':
        unfoldCfg.Hreco = 0
    else:
        unfoldCfg.Hreco = options.Hreco

    h_unfolded_data = unfolding.unfold( h_data )

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

def get_unfolded_normalisation( TTJet_fit_results, category, channel, tau_value, visiblePS ):
    global variable, met_type, path_to_JSON, file_for_unfolding, file_for_powheg_pythia, file_for_powheg_herwig, file_for_ptreweight, files_for_pdfs
    global centre_of_mass, luminosity, ttbar_xsection, load_fakes, method
    global file_for_powhegPythia8, file_for_madgraphMLM, file_for_amcatnlo
    # global file_for_matchingdown, file_for_matchingup
    global file_for_scaledown, file_for_scaleup
    global file_for_massdown, file_for_massup
    global ttbar_generator_systematics, ttbar_theory_systematics, pdf_uncertainties
    global use_ptreweight

    files_for_systematics = {
                             # ttbar_theory_systematic_prefix + 'matchingdown'    :  file_for_matchingdown,
                             # ttbar_theory_systematic_prefix + 'matchingup'      :  file_for_matchingup,
                             ttbar_theory_systematic_prefix + 'scaledown'       :  file_for_scaledown,
                             ttbar_theory_systematic_prefix + 'scaleup'         :  file_for_scaleup,
                             ttbar_theory_systematic_prefix + 'massdown'        :  file_for_massdown,
                             ttbar_theory_systematic_prefix + 'massup'          :  file_for_massup,
                             }

    h_truth, h_measured, h_response, h_fakes = None, None, None, None
    # Systematics where you change the response matrix
    if category in ttbar_generator_systematics :
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( inputfile = files_for_systematics[category],
                                                                              variable = variable,
                                                                              channel = channel,
                                                                              met_type = met_type,
                                                                              centre_of_mass = centre_of_mass,
                                                                              ttbar_xsection = ttbar_xsection,
                                                                              luminosity = luminosity,
                                                                              load_fakes = load_fakes,
                                                                              visiblePS = visiblePS,
                                                                              )
    # Systematics where you change input MC
    else:
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( inputfile = file_for_unfolding,
                                                                              variable = variable,
                                                                              channel = channel,
                                                                              met_type = met_type,
                                                                              centre_of_mass = centre_of_mass,
                                                                              ttbar_xsection = ttbar_xsection,
                                                                              luminosity = luminosity,
                                                                              load_fakes = load_fakes,
                                                                              visiblePS = visiblePS,
                                                                              )

    #
    # THESE ARE FOR GETTING THE HISTOGRAMS FOR COMPARING WITH UNFOLDED DATA
    #

    # h_truth_matchingdown, _, _, _ = get_unfold_histogram_tuple( inputfile = file_for_matchingdown,
    #                                             variable = variable,
    #                                             channel = channel,
    #                                             met_type = met_type,
    #                                             centre_of_mass = centre_of_mass,
    #                                             ttbar_xsection = ttbar_xsection,
    #                                             luminosity = luminosity,
    #                                             load_fakes = load_fakes
    #                                             )
    # h_truth_matchingup, _, _, _ = get_unfold_histogram_tuple( inputfile = file_for_matchingup,
    #                                             variable = variable,
    #                                             channel = channel,
    #                                             met_type = met_type,
    #                                             centre_of_mass = centre_of_mass,
    #                                             ttbar_xsection = ttbar_xsection,
    #                                             luminosity = luminosity,
    #                                             load_fakes = load_fakes
    #                                             )
    h_truth_scaledown, _, _, _ = get_unfold_histogram_tuple( inputfile = file_for_scaledown,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes,
                                                visiblePS = visiblePS,
                                                )
    h_truth_scaleup, _, _, _ = get_unfold_histogram_tuple( inputfile = file_for_scaleup,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes,
                                                visiblePS = visiblePS,
                                                )

    h_truth_massdown, _, _, _ = get_unfold_histogram_tuple( inputfile = file_for_massdown,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes,
                                                visiblePS = visiblePS,
                                                )
    h_truth_massup, _, _, _ = get_unfold_histogram_tuple( inputfile = file_for_massup,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes,
                                                visiblePS = visiblePS,
                                                )

    h_truth_powhegPythia8, _, _, _ = get_unfold_histogram_tuple( inputfile = file_for_powhegPythia8,
                                            variable = variable,
                                            channel = channel,
                                            met_type = met_type,
                                            centre_of_mass = centre_of_mass,
                                            ttbar_xsection = ttbar_xsection,
                                            luminosity = luminosity,
                                            load_fakes = load_fakes,
                                            visiblePS = visiblePS,
                                            )

    h_truth_amcatnlo, _, _, _ = get_unfold_histogram_tuple( inputfile = file_for_amcatnlo,
                                            variable = variable,
                                            channel = channel,
                                            met_type = met_type,
                                            centre_of_mass = centre_of_mass,
                                            ttbar_xsection = ttbar_xsection,
                                            luminosity = luminosity,
                                            load_fakes = load_fakes,
                                            visiblePS = visiblePS,
                                            )

    h_truth_madgraphMLM, _, _, _ = get_unfold_histogram_tuple( inputfile = file_for_madgraphMLM,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes,
                                                visiblePS = visiblePS,
                                                )

    central_results = hist_to_value_error_tuplelist( h_truth )
    # MADGRAPH_ptreweight_results = hist_to_value_error_tuplelist( h_truth_ptreweight )
    # POWHEG_PYTHIA_results = hist_to_value_error_tuplelist( h_truth_POWHEG_PYTHIA )
    # POWHEG_HERWIG_results = hist_to_value_error_tuplelist( h_truth_POWHEG_HERWIG )
    # MCATNLO_results = None
    powhegPythia8_results = hist_to_value_error_tuplelist( h_truth_powhegPythia8 )
    madgraphMLM_results = hist_to_value_error_tuplelist( h_truth_madgraphMLM )
    AMCATNLO_results = hist_to_value_error_tuplelist( h_truth_amcatnlo )

    # matchingdown_results = hist_to_value_error_tuplelist( h_truth_matchingdown )
    # matchingup_results = hist_to_value_error_tuplelist( h_truth_matchingup )
    scaledown_results = hist_to_value_error_tuplelist( h_truth_scaledown )
    scaleup_results = hist_to_value_error_tuplelist( h_truth_scaleup )
    massdown_results = hist_to_value_error_tuplelist( h_truth_massdown )
    massup_results = hist_to_value_error_tuplelist( h_truth_massup )

    TTJet_fit_results_unfolded = unfold_results( TTJet_fit_results,
                                                category,
                                                channel,
                                                tau_value,
                                                h_truth,
                                                h_measured,
                                                h_response,
                                                h_fakes,
                                                method,
                                                visiblePS,
                                                )

    normalisation_unfolded = {
                          'TTJet_measured' : TTJet_fit_results,
                          'TTJet_unfolded' : TTJet_fit_results_unfolded,
                          'powhegPythia8' : powhegPythia8_results,
                          'amcatnlo': AMCATNLO_results,
                          'madgraphMLM':madgraphMLM_results,
                          # 'MADGRAPH_ptreweight': MADGRAPH_ptreweight_results,
                          # # other generators
                          # 'POWHEG_PYTHIA': POWHEG_PYTHIA_results,
                          # 'POWHEG_HERWIG': POWHEG_HERWIG_results,
                          # # systematics
                          # 'matchingdown': matchingdown_results,
                          # 'matchingup': matchingup_results,
                          'scaledown': scaledown_results,
                          'scaleup': scaleup_results,
                          'massdown': massdown_results,
                          'massup': massup_results
                          }
    # if centre_of_mass == 8:
    #     normalisation_unfolded['MCATNLO'] = MCATNLO_results

    return normalisation_unfolded

def calculate_xsections( normalisation, category, channel ):
    global variable, met_type, path_to_JSON
    # calculate the x-sections
    branching_ratio = 0.15
    if channel == 'combined':
        branching_ratio = branching_ratio * 2
    TTJet_xsection = calculate_xsection( normalisation['TTJet_measured'], luminosity, branching_ratio )  # L in pb1
    TTJet_xsection_unfolded = calculate_xsection( normalisation['TTJet_unfolded'], luminosity, branching_ratio )  # L in pb1

    powhegPythia8_xsection = calculate_xsection( normalisation['powhegPythia8'], luminosity, branching_ratio )  # L in pb1
    amcatnlo_xsection = calculate_xsection( normalisation['amcatnlo'], luminosity, branching_ratio )  # L in pb1
    # MADGRAPH_ptreweight_xsection = calculate_xsection( normalisation['MADGRAPH_ptreweight'], luminosity, branching_ratio )  # L in pb1
    # POWHEG_PYTHIA_xsection = calculate_xsection( normalisation['POWHEG_PYTHIA'], luminosity, branching_ratio )  # L in pb1
    # POWHEG_HERWIG_xsection = calculate_xsection( normalisation['POWHEG_HERWIG'], luminosity, branching_ratio )  # L in pb1
    # MCATNLO_xsection = None
    # if centre_of_mass == 8:
    #     MCATNLO_xsection = calculate_xsection( normalisation['MCATNLO'], luminosity, branching_ratio )  # L in pb1
    # matchingdown_xsection = calculate_xsection( normalisation['matchingdown'], luminosity, branching_ratio )  # L in pb1
    # matchingup_xsection = calculate_xsection( normalisation['matchingup'], luminosity, branching_ratio )  # L in pb1
    scaledown_xsection = calculate_xsection( normalisation['scaledown'], luminosity, branching_ratio )  # L in pb1
    scaleup_xsection = calculate_xsection( normalisation['scaleup'], luminosity, branching_ratio )  # L in pb1
    massdown_xsection = calculate_xsection( normalisation['massdown'], luminosity, branching_ratio )  # L in pb1
    massup_xsection = calculate_xsection( normalisation['massup'], luminosity, branching_ratio )  # L in pb1

    madgraphMLM_xsection = calculate_xsection( normalisation['madgraphMLM'], luminosity, branching_ratio )

    xsection_unfolded = {'TTJet_measured' : TTJet_xsection,
                     'TTJet_unfolded' : TTJet_xsection_unfolded,
                     'powhegPythia8' : powhegPythia8_xsection,
                     'amcatnlo': amcatnlo_xsection,
                     'madgraphMLM' : madgraphMLM_xsection,
                     # 'MADGRAPH_ptreweight': MADGRAPH_ptreweight_xsection,
                     # 'POWHEG_PYTHIA': POWHEG_PYTHIA_xsection,
                     # 'POWHEG_HERWIG': POWHEG_HERWIG_xsection,
                     # # systematics
                     # 'matchingdown': matchingdown_xsection,
                     # 'matchingup': matchingup_xsection,
                     'scaledown': scaledown_xsection,
                     'scaleup': scaleup_xsection,
                     'massdown': massdown_xsection,
                     'massup': massup_xsection
                     }
    # if centre_of_mass == 8:
    #     xsection_unfolded['MCATNLO'] =  MCATNLO_xsection

    ### if k_value:
    ###     filename = path_to_JSON + '/xsection_measurement_results/%s/kv%d/%s/xsection_%s.txt' % ( channel, k_value, category, met_type )
    ### elif not channel == 'combined':
    ###     raise ValueError( 'Invalid k-value for variable %s, channel %s, category %s.' % ( variable, channel, category ) )
    ### else:
    filename = path_to_JSON + '/xsection_measurement_results/%s/%s/xsection_%s.txt' % ( channel, category, met_type )

    write_data_to_JSON( xsection_unfolded, filename )

def calculate_normalised_xsections( normalisation, category, channel, normalise_to_one = False ):
    global variable, met_type, path_to_JSON
    TTJet_normalised_xsection = calculate_normalised_xsection( normalisation['TTJet_measured'], bin_widths[variable], normalise_to_one )
    TTJet_normalised_xsection_unfolded = calculate_normalised_xsection( normalisation['TTJet_unfolded'], bin_widths[variable], normalise_to_one )
    powhegPythia8_normalised_xsection = calculate_normalised_xsection( normalisation['powhegPythia8'], bin_widths[variable], normalise_to_one )
    amcatnlo_normalised_xsection = calculate_normalised_xsection( normalisation['amcatnlo'], bin_widths[variable], normalise_to_one )
    # MADGRAPH_ptreweight_normalised_xsection = calculate_normalised_xsection( normalisation['MADGRAPH_ptreweight'], bin_widths[variable], normalise_to_one )
    # POWHEG_PYTHIA_normalised_xsection = calculate_normalised_xsection( normalisation['POWHEG_PYTHIA'], bin_widths[variable], normalise_to_one )
    # POWHEG_HERWIG_normalised_xsection = calculate_normalised_xsection( normalisation['POWHEG_HERWIG'], bin_widths[variable], normalise_to_one )
    # MCATNLO_normalised_xsection = None
    # if centre_of_mass == 8:
    #     MCATNLO_normalised_xsection = calculate_normalised_xsection( normalisation['MCATNLO'], bin_widths[variable], normalise_to_one )
    # matchingdown_normalised_xsection = calculate_normalised_xsection( normalisation['matchingdown'], bin_widths[variable], normalise_to_one )
    # matchingup_normalised_xsection = calculate_normalised_xsection( normalisation['matchingup'], bin_widths[variable], normalise_to_one )
    scaledown_normalised_xsection = calculate_normalised_xsection( normalisation['scaledown'], bin_widths[variable], normalise_to_one )
    scaleup_normalised_xsection = calculate_normalised_xsection( normalisation['scaleup'], bin_widths[variable], normalise_to_one )
    massdown_normalised_xsection = calculate_normalised_xsection( normalisation['massdown'], bin_widths[variable], normalise_to_one )
    massup_normalised_xsection = calculate_normalised_xsection( normalisation['massup'], bin_widths[variable], normalise_to_one )

    madgraphMLM_normalised_xsection = calculate_normalised_xsection( normalisation['madgraphMLM'], bin_widths[variable], normalise_to_one )

    normalised_xsection = {'TTJet_measured' : TTJet_normalised_xsection,
                       'TTJet_unfolded' : TTJet_normalised_xsection_unfolded,
                       'powhegPythia8' : powhegPythia8_normalised_xsection,
                       'amcatnlo': amcatnlo_normalised_xsection,
                       'madgraphMLM' : madgraphMLM_normalised_xsection,
                       # 'MADGRAPH_ptreweight': MADGRAPH_ptreweight_normalised_xsection,
                       # 'POWHEG_PYTHIA': POWHEG_PYTHIA_normalised_xsection,
                       # 'POWHEG_HERWIG': POWHEG_HERWIG_normalised_xsection,
                       # # systematics
                       # 'matchingdown': matchingdown_normalised_xsection,
                       # 'matchingup': matchingup_normalised_xsection,
                       'scaledown': scaledown_normalised_xsection,
                       'scaleup': scaleup_normalised_xsection,
                       'massdown': massdown_normalised_xsection,
                       'massup': massup_normalised_xsection,
                       }
    # if centre_of_mass == 8:
    #     normalised_xsection['MCATNLO'] = MCATNLO_normalised_xsection

    ### if not channel == 'combined':
    ###     filename = path_to_JSON + '/xsection_measurement_results/%s/kv%d/%s/normalised_xsection_%s.txt' % ( channel, k_value, category, met_type )
    ### else:
    filename = path_to_JSON + '/xsection_measurement_results/%s/%s/normalised_xsection_%s.txt' % ( channel, category, met_type )

    if normalise_to_one:
        filename = filename.replace( 'normalised_xsection', 'normalised_to_one_xsection' )
    write_data_to_JSON( normalised_xsection, filename )

if __name__ == '__main__':
    set_root_defaults( msg_ignore_level = 3001 )
    # setup
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data/M3_angle_bl/',
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
                      help = "Unfolding method: RooUnfoldSvd (default), TSVDUnfold, RooUnfoldTUnfold, RooUnfoldInvert, RooUnfoldBinByBin, RooUnfoldBayes" )
    parser.add_option( "-H", "--hreco", type = 'int',
                      dest = "Hreco", default = 2,
                      help = "Hreco parameter for error treatment in RooUnfold" )
    parser.add_option( "-c", "--centre-of-mass-energy", dest = "CoM", default = 13,
                      help = "set the centre of mass energy for analysis. Default = 13 [TeV]", type = int )
    parser.add_option( "-C", "--combine-before-unfolding", dest = "combine_before_unfolding", action = "store_true",
                      help = "Perform combination of channels before unfolding" )
    parser.add_option( "-w", "--write-unfolding-objects", dest = "write_unfolding_objects", action = "store_true",
                      help = "Write out the unfolding objects (D, SV)" )
    parser.add_option( '--test', dest = "test", action = "store_true",
                      help = "Just run the central measurement" )
    parser.add_option( '--ptreweight', dest = "ptreweight", action = "store_true",
                      help = "Use pt-reweighted MadGraph for the measurement" )
    parser.add_option( '--visiblePS', dest = "visiblePS", action = "store_true",
                      help = "Unfold to visible phase space" )

    ( options, args ) = parser.parse_args()
    measurement_config = XSectionConfig( options.CoM )
    run_just_central = options.test
    use_ptreweight = options.ptreweight
    # caching of variables for faster access
    translate_options = measurement_config.translate_options
    ttbar_theory_systematic_prefix = measurement_config.ttbar_theory_systematic_prefix
    vjets_theory_systematic_prefix = measurement_config.vjets_theory_systematic_prefix
    met_systematics = measurement_config.met_systematics
    
    centre_of_mass = options.CoM
    luminosity = measurement_config.luminosity * measurement_config.luminosity_scale
    ttbar_xsection = measurement_config.ttbar_xsection
    path_to_files = measurement_config.path_to_files
    file_for_unfolding = File( measurement_config.unfolding_central, 'read' )

    # Not unfolding with other files at the moment
    ###
    ###    # file_for_powheg_pythia = File( measurement_config.unfolding_powheg_pythia, 'read' )
    ###    # file_for_powheg_herwig = File( measurement_config.unfolding_powheg_herwig, 'read' )
    ###    # file_for_mcatnlo = None
    ###    # if centre_of_mass == 8:
    ###    #     file_for_mcatnlo = File( measurement_config.unfolding_mcatnlo, 'read' )
    ###    # file_for_ptreweight = File ( measurement_config.unfolding_ptreweight, 'read' )
    ###    # files_for_pdfs = { 'PDFWeights_%d' % index : File ( measurement_config.unfolding_pdfweights[index] ) for index in range( 1, 45 ) }
    ###        
    file_for_scaledown = File( measurement_config.unfolding_scale_down, 'read' )
    file_for_scaleup = File( measurement_config.unfolding_scale_up, 'read' )
    ###    # file_for_matchingdown = File( measurement_config.unfolding_matching_down, 'read' )
    ###    # file_for_matchingup = File( measurement_config.unfolding_matching_up, 'read' )
    ###
    file_for_massdown = File( measurement_config.unfolding_mass_down, 'read' )
    file_for_massup = File( measurement_config.unfolding_mass_up, 'read' )
    ###

    file_for_powhegPythia8 = File( measurement_config.unfolding_powheg_pythia8, 'read')
    file_for_amcatnlo = File( measurement_config.unfolding_amcatnlo, 'read')
    file_for_madgraphMLM = File( measurement_config.unfolding_madgraphMLM, 'read')

    variable = options.variable

    tau_value_electron = measurement_config.tau_values_electron[variable]
    tau_value_muon = measurement_config.tau_values_muon[variable]

    visiblePS = options.visiblePS
    phase_space = 'FullPS'
    if visiblePS:
        phase_space = "VisiblePS"

    load_fakes = options.load_fakes
    unfoldCfg.Hreco = options.Hreco
    method = options.unfolding_method
    combine_before_unfolding = options.combine_before_unfolding
    met_type = translate_options[options.metType]
    b_tag_bin = translate_options[options.bjetbin]
    path_to_JSON = '{path}/{com}TeV/{variable}/{phase_space}/'.format( 
            path = options.path,
            com = measurement_config.centre_of_mass_energy,
            variable = variable,
            phase_space = phase_space,
            )

    categories = deepcopy( measurement_config.categories_and_prefixes.keys() )
    # No generator or theory systematics yet
    ttbar_generator_systematics = [ttbar_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    ### vjets_generator_systematics = [vjets_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    categories.extend( ttbar_generator_systematics )
    ### categories.extend( vjets_generator_systematics )

    ### ttbar theory systematics, including pt reweighting and hadronisation systematic
    ### ttbar_theory_systematics = [] #[ ttbar_theory_systematic_prefix + 'ptreweight' ]
    ### ttbar_theory_systematics.extend( [ttbar_theory_systematic_prefix + 'powheg_pythia', ttbar_theory_systematic_prefix + 'powheg_herwig'] )
    ### categories.extend( ttbar_theory_systematics )

    ### Add mass systematics
    ### ttbar_mass_systematics = measurement_config.topMass_systematics
    ### categories.extend( measurement_config.topMass_systematics )

    ### Add k Value systematic
    ### kValue_systematics = measurement_config.kValueSystematic
    ### categories.extend( measurement_config.kValueSystematic )

    ### pdf_uncertainties = ['PDFWeights_%d' % index for index in range( 1, 45 )]
    rate_changing_systematics = [systematic for systematic in measurement_config.rate_changing_systematics_names]
    #  all MET uncertainties except JES as this is already included
    met_uncertainties = [suffix for suffix in measurement_config.met_systematics_suffixes if not 'JetEn' in suffix and not 'JetRes' in suffix]
    all_measurements = deepcopy( categories )
    ### all_measurements.extend( pdf_uncertainties )
    all_measurements.extend( ['QCD_shape'] )
    all_measurements.extend( rate_changing_systematics )

    print 'Performing unfolding for variable', variable
    for category in all_measurements:
        print 'Doing category ',category

        if run_just_central and not category == 'central':
            continue
        # Don't need to consider MET uncertainties for HT
        if variable == 'HT' and (category in measurement_config.met_systematics_suffixes and not category in ['JES_up', 'JES_down', 'JER_up', 'JER_down']):
            continue
        print 'Unfolding category "%s"' % category
        # Setting up systematic MET for JES up/down samples
        met_type = translate_options[options.metType]

        if category == 'JES_up':
            met_type += 'JetEnUp'
        elif category == 'JES_down':
            met_type += 'JetEnDown'
        elif category == 'JER_up':
            met_type += 'JetResUp'
        elif category == 'JER_down':
            met_type += 'JetResDown'
        if category in met_uncertainties and not 'JES' in category and not 'JER' in category:
            met_type += category

        # read fit results from JSON
        electron_file = path_to_JSON + '/' + category + '/normalisation_electron_' + met_type + '.txt'
        muon_file = path_to_JSON + '/' + category + '/normalisation_muon_' + met_type + '.txt'
    #     combined_file = path_to_JSON + '/fit_results/' + category + '/fit_results_combined_' + met_type + '.txt'

        # don't change fit input for ttbar generator/theory systematics and PDF weights
        if category in ttbar_generator_systematics :
            # or category in ttbar_mass_systematics 
                electron_file = path_to_JSON + '/central/normalisation_electron_' + met_type + '.txt'
                muon_file = path_to_JSON + '/central/normalisation_muon_' + met_type + '.txt'
            # combined_file = path_to_JSON + '/central/normalisation_combined_' + met_type + '.txt'
        
        fit_results_electron = read_data_from_JSON( electron_file )
        fit_results_muon = read_data_from_JSON( muon_file )
        # fit_results_combined = read_data_from_JSON( combined_file )
        TTJet_fit_results_electron = fit_results_electron['TTJet']
        TTJet_fit_results_muon = fit_results_muon['TTJet']
        # TTJet_fit_results_combined = fit_results_combined['TTJet']

    #     # change back to original MET type for the unfolding
        met_type = translate_options[options.metType]
    #     # ad-hoc switch for PFMET -> patMETsPFlow
    #     if met_type == 'PFMET':
    #         met_type = 'patMETsPFlow'

        filename = ''

    #     # get unfolded normalisation
        unfolded_normalisation_electron = {}
        unfolded_normalisation_muon = {}

        unfolded_normalisation_electron = get_unfolded_normalisation( TTJet_fit_results_electron, category, 'electron', tau_value_electron, visiblePS = visiblePS )
        filename = path_to_JSON + '/xsection_measurement_results/electron/%s/normalisation_%s.txt' % ( category, met_type )
        write_data_to_JSON( unfolded_normalisation_electron, filename )
        # measure xsection
        calculate_xsections( unfolded_normalisation_electron, category, 'electron' )
        calculate_normalised_xsections( unfolded_normalisation_electron, category, 'electron' )
        calculate_normalised_xsections( unfolded_normalisation_electron, category, 'electron' , True )

        unfolded_normalisation_muon = get_unfolded_normalisation( TTJet_fit_results_muon, category, 'muon', tau_value_muon, visiblePS = visiblePS )
        filename = path_to_JSON + '/xsection_measurement_results/muon/%s/normalisation_%s.txt' % ( category, met_type )
        write_data_to_JSON( unfolded_normalisation_muon, filename )
        # measure xsection
        calculate_xsections( unfolded_normalisation_muon, category, 'muon' )
        calculate_normalised_xsections( unfolded_normalisation_muon, category, 'muon' )
        calculate_normalised_xsections( unfolded_normalisation_muon, category, 'muon' , True )

        # # if combine_before_unfolding:
        # #     unfolded_normalisation_combined = get_unfolded_normalisation( TTJet_fit_results_combined, category, 'combined', k_value_combined )
        # # else:
        unfolded_normalisation_combined = combine_complex_results( unfolded_normalisation_electron, unfolded_normalisation_muon )

        filename = path_to_JSON + '/xsection_measurement_results/combined/%s/normalisation_%s.txt' % ( category, met_type )
        write_data_to_JSON( unfolded_normalisation_combined, filename )
        calculate_xsections( unfolded_normalisation_combined, category, 'combined' )
        calculate_normalised_xsections( unfolded_normalisation_combined, category, 'combined' )
        calculate_normalised_xsections( unfolded_normalisation_combined, category, 'combined' , True )
