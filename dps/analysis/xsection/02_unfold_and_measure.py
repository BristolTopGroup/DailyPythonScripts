# general
from __future__ import division
from optparse import OptionParser
# from array import array
# rootpy
from rootpy.io import File
from rootpy.plotting import Hist2D
# DailyPythonScripts
import dps.config.unfold as unfoldCfg
from dps.config.variable_binning import bin_widths, bin_widths_visiblePS, reco_bin_edges_full, reco_bin_edges_vis
from dps.config.xsection import XSectionConfig
from dps.utils.Calculation import calculate_xsection, calculate_normalised_xsection, \
combine_complex_results
from dps.utils.hist_utilities import hist_to_value_error_tuplelist, \
value_error_tuplelist_to_hist
from dps.utils.Unfolding import Unfolding, get_unfold_histogram_tuple, removeFakes
from dps.utils.file_utilities import read_data_from_JSON, write_data_to_JSON
from copy import deepcopy
from dps.utils.ROOT_utils import set_root_defaults
# from ROOT import TGraph, TSpline3, TUnfoldDensity

def unfold_results( results, category, channel, tau_value, h_truth, h_measured, h_response, h_fakes, method, visiblePS ):
    global variable, path_to_JSON, options
    edges = reco_bin_edges_full[variable]
    if visiblePS:
        edges = reco_bin_edges_vis[variable]
    h_data = value_error_tuplelist_to_hist( results, edges )

    # Remove fakes before unfolding
    h_data = removeFakes( h_measured, h_fakes, h_data )

    unfolding = Unfolding( h_data, h_truth, h_measured, h_response, h_fakes, method = method, tau = tau_value )

    # turning off the unfolding errors for systematic samples
    if not category == 'central':
        unfoldCfg.error_treatment = 0
    else:
        unfoldCfg.error_treatment = options.error_treatment

    h_unfolded_data = unfolding.unfold()
    # print "h_response bin edges : ", h_response
    # print "h_unfolded_data bin edges : ", h_unfolded_data

    del unfolding
    return hist_to_value_error_tuplelist( h_unfolded_data ), hist_to_value_error_tuplelist( h_data )

def data_covariance_matrix( data ):
    values = list( data )
    get_bin_error = data.GetBinError
    cov_matrix = Hist2D( len( values ), -10, 10, len( values ), -10, 10, type = 'D' )
    for bin_i in range( len( values ) ):
        error = get_bin_error( bin_i + 1 )
        cov_matrix.SetBinContent( bin_i + 1, bin_i + 1, error * error )
    return cov_matrix

def get_unfolded_normalisation( TTJet_normalisation_results, category, channel, tau_value, visiblePS ):
    global centre_of_mass, luminosity, ttbar_xsection, method, variable, path_to_JSON
    global file_for_unfolding, file_for_ptreweight, files_for_pdfs
    global file_for_powhegPythia8, file_for_powheg_herwig, file_for_madgraphMLM, file_for_amcatnlo, file_for_amcatnlo_herwig
    global file_for_scaledown, file_for_scaleup
    global file_for_massdown, file_for_massup
    global pdf_uncertainties
    # Add in this option?
    global use_ptreweight

    files_for_systematics = {
        'TTJets_scaledown'       	   :  file_for_scaledown,
        'TTJets_scaleup'         	   :  file_for_scaleup,
        'TTJets_massdown'        	   :  file_for_massdown,
        'TTJets_massup'          	   :  file_for_massup,
       
        'TTJets_factorisationdown'	 :  file_for_factorisationdown,
        'TTJets_factorisationup'   	 :  file_for_factorisationup,
        'TTJets_renormalisationdown' :  file_for_renormalisationdown,
        'TTJets_renormalisationup'   :  file_for_renormalisationup,
        'TTJets_combineddown'     	 :  file_for_combineddown,
        'TTJets_combinedup'          :  file_for_combinedup,
        'TTJets_alphaSdown'			     :  file_for_alphaSdown,
        'TTJets_alphaSup'   			   :  file_for_alphaSup,

        'JES_down'                   :  file_for_jesdown,
        'JES_up'                     :  file_for_jesup,

        'JER_down'                   :  file_for_jerdown,
        'JER_up'                     :  file_for_jerup,

        'BJet_up'                    :  file_for_bjetup,
        'BJet_down'                  :  file_for_bjetdown,

        'LightJet_up'                :  file_for_lightjetup,
        'LightJet_down'              :  file_for_lightjetdown,

        'TTJets_hadronisation'       :  file_for_powheg_herwig,
        'TTJets_NLOgenerator'        :  file_for_amcatnlo,

        'ElectronEnUp'               :  file_for_ElectronEnUp,
        'ElectronEnDown'             :  file_for_ElectronEnDown,
        'MuonEnUp'                   :  file_for_MuonEnUp,
        'MuonEnDown'                 :  file_for_MuonEnDown,
        'TauEnUp'                    :  file_for_TauEnUp,
        'TauEnDown'                  :  file_for_TauEnDown,
        'UnclusteredEnUp'            :  file_for_UnclusteredEnUp,
        'UnclusteredEnDown'          :  file_for_UnclusteredEnDown,

        'Muon_up'                    :  file_for_LeptonUp,
        'Muon_down'                  :  file_for_LeptonDown,
        'Electron_up'                :  file_for_LeptonUp,
        'Electron_down'              :  file_for_LeptonDown,

        'PileUp_up'                  :  file_for_PUUp,
        'PileUp_down'                :  file_for_PUDown,
    }

    h_truth, h_measured, h_response, h_fakes = None, None, None, None

    # Systematics where you change the response matrix
    if category in files_for_systematics :
        print 'Doing category',category,'by changing response matrix'
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( 
            inputfile = files_for_systematics[category],
            variable = variable,
            channel = channel,
            centre_of_mass = centre_of_mass,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
    elif category in pdf_uncertainties:
        print 'Doing category',category,'by changing response matrix'
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( 
            inputfile = files_for_pdfs[category],
            variable = variable,
            channel = channel,
            centre_of_mass = centre_of_mass,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
    # Central and systematics where you just change input MC
    else:
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( 
            inputfile = file_for_unfolding,
            variable = variable,
            channel = channel,
            centre_of_mass = centre_of_mass,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )

    # Unfold current normalisation measurements  
    TTJet_normalisation_results_unfolded, TTJet_normalisation_results_withoutFakes = unfold_results( 
        TTJet_normalisation_results,
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

    # Store measurements
    normalisation_unfolded = {
        'TTJet_measured' : TTJet_normalisation_results,
        'TTJet_measured_withoutFakes' : TTJet_normalisation_results_withoutFakes,
        'TTJet_unfolded' : TTJet_normalisation_results_unfolded
    }

    # Return truth of different generators for comparison to data in 04
    if category == 'central':
        h_truth_massdown, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = file_for_massdown,
            variable = variable,
            channel = channel,
            centre_of_mass = centre_of_mass,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_massup, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = file_for_massup,
            variable = variable,
            channel = channel,
            centre_of_mass = centre_of_mass,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_powhegPythia8, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = file_for_powhegPythia8,
            variable = variable,
            channel = channel,
            centre_of_mass = centre_of_mass,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_amcatnlo, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = file_for_amcatnlo,
            variable = variable,
            channel = channel,
            centre_of_mass = centre_of_mass,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_madgraphMLM, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = file_for_madgraphMLM,
            variable = variable,
            channel = channel,
            centre_of_mass = centre_of_mass,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_powheg_herwig, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = file_for_powheg_herwig,
            variable = variable,
            channel = channel,
            centre_of_mass = centre_of_mass,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        # h_truth_amcatnlo_herwig, _, _, _ = get_unfold_histogram_tuple( 
        #     inputfile = file_for_amcatnlo_herwig,
        #     variable = variable,
        #     channel = channel,
        #     centre_of_mass = centre_of_mass,
        #     ttbar_xsection = ttbar_xsection,
        #     luminosity = luminosity,
        #     load_fakes = True,
        #     visiblePS = visiblePS,
        # )
    
        powhegPythia8_results = hist_to_value_error_tuplelist( h_truth_powhegPythia8 )
        madgraphMLM_results = hist_to_value_error_tuplelist( h_truth_madgraphMLM )
        amcatnloPythia8_results = hist_to_value_error_tuplelist( h_truth_amcatnlo )
        powheg_herwig_results = hist_to_value_error_tuplelist( h_truth_powheg_herwig )
        # amcatnlo_herwig_results = hist_to_value_error_tuplelist( h_truth_amcatnlo_herwig )

        massdown_results = hist_to_value_error_tuplelist( h_truth_massdown )
        massup_results = hist_to_value_error_tuplelist( h_truth_massup )

        normalisation_unfolded['powhegPythia8'] =  powhegPythia8_results
        normalisation_unfolded['amcatnlo'] =  amcatnloPythia8_results
        normalisation_unfolded['madgraphMLM'] = madgraphMLM_results
        normalisation_unfolded['powhegHerwig'] =  powheg_herwig_results
        # normalisation_unfolded['amcatnloHerwig'] =  amcatnlo_herwig_results

        normalisation_unfolded['massdown'] =  massdown_results
        normalisation_unfolded['massup'] =  massup_results

    return normalisation_unfolded

def calculate_xsections( normalisation, category, channel ):
    global variable, path_to_JSON
    # calculate the x-sections
    branching_ratio = 0.15
    if 'combined' in channel:
        branching_ratio = branching_ratio * 2
    TTJet_xsection = calculate_xsection( normalisation['TTJet_measured'], luminosity, branching_ratio )  # L in pb1
    TTJet_withoutFakes_xsection = calculate_xsection( normalisation['TTJet_measured_withoutFakes'], luminosity, branching_ratio )  # L in pb1
    TTJet_xsection_unfolded = calculate_xsection( normalisation['TTJet_unfolded'], luminosity, branching_ratio )  # L in pb1

    xsection_unfolded = {
      'TTJet_measured' : TTJet_xsection,
      'TTJet_measured_withoutFakes' : TTJet_withoutFakes_xsection,
      'TTJet_unfolded' : TTJet_xsection_unfolded,
    }

    if category == 'central':
        powhegPythia8_xsection = calculate_xsection( normalisation['powhegPythia8'], luminosity, branching_ratio )  # L in pb1
        amcatnlo_xsection = calculate_xsection( normalisation['amcatnlo'], luminosity, branching_ratio )  # L in pb1
        powhegHerwig_xsection = calculate_xsection( normalisation['powhegHerwig'], luminosity, branching_ratio )  # L in pb1
        # amcatnloHerwig_xsection = calculate_xsection( normalisation['amcatnloHerwig'], luminosity, branching_ratio )  # L in pb1
        madgraphMLM_xsection = calculate_xsection( normalisation['madgraphMLM'], luminosity, branching_ratio )

        massdown_xsection = calculate_xsection( normalisation['massdown'], luminosity, branching_ratio )  # L in pb1
        massup_xsection = calculate_xsection( normalisation['massup'], luminosity, branching_ratio )  # L in pb1

        xsection_unfolded['powhegPythia8'] =  powhegPythia8_xsection
        xsection_unfolded['amcatnlo'] =  amcatnlo_xsection
        xsection_unfolded['madgraphMLM'] =  madgraphMLM_xsection
        xsection_unfolded['powhegHerwig'] =  powhegHerwig_xsection
        # xsection_unfolded['amcatnloHerwig'] =  amcatnloHerwig_xsection

        xsection_unfolded['massdown'] =  massdown_xsection
        xsection_unfolded['massup'] =  massup_xsection

    file_template = '{path_to_JSON}/{category}/xsection_{channel}_{method}.txt'
    filename = file_template.format(
        path_to_JSON = path_to_JSON,
        category = category,
        channel = channel,
        method = method,
    )
    write_data_to_JSON( xsection_unfolded, filename )
    return

def calculate_normalised_xsections( normalisation, category, channel, normalise_to_one = False ):
    global variable, path_to_JSON, phase_space

    binWidths = None
    if phase_space == 'VisiblePS':
        binWidths = bin_widths_visiblePS
    elif phase_space == 'FullPS':
        binWidths = bin_widths

    TTJet_normalised_xsection = calculate_normalised_xsection( normalisation['TTJet_measured'], binWidths[variable], normalise_to_one )
    TTJet_withoutFakes_normalised_xsection = calculate_normalised_xsection( normalisation['TTJet_measured_withoutFakes'], binWidths[variable], normalise_to_one )
    TTJet_normalised_xsection_unfolded = calculate_normalised_xsection( normalisation['TTJet_unfolded'], binWidths[variable], normalise_to_one )

    normalised_xsection = {'TTJet_measured' : TTJet_normalised_xsection,
                           'TTJet_measured_withoutFakes' : TTJet_withoutFakes_normalised_xsection,
                           'TTJet_unfolded' : TTJet_normalised_xsection_unfolded
                           }

    if category == 'central':
        powhegPythia8_normalised_xsection = calculate_normalised_xsection( normalisation['powhegPythia8'], binWidths[variable], normalise_to_one )
        amcatnlo_normalised_xsection = calculate_normalised_xsection( normalisation['amcatnlo'], binWidths[variable], normalise_to_one )
        powhegHerwig_normalised_xsection = calculate_normalised_xsection( normalisation['powhegHerwig'], binWidths[variable], normalise_to_one )
        # amcatnloHerwig_normalised_xsection = calculate_normalised_xsection( normalisation['amcatnloHerwig'], binWidths[variable], normalise_to_one )
        madgraphMLM_normalised_xsection = calculate_normalised_xsection( normalisation['madgraphMLM'], binWidths[variable], normalise_to_one )

        massdown_normalised_xsection = calculate_normalised_xsection( normalisation['massdown'], binWidths[variable], normalise_to_one )
        massup_normalised_xsection = calculate_normalised_xsection( normalisation['massup'], binWidths[variable], normalise_to_one )

        normalised_xsection['powhegPythia8'] = powhegPythia8_normalised_xsection
        normalised_xsection['amcatnlo'] = amcatnlo_normalised_xsection
        normalised_xsection['madgraphMLM' ] = madgraphMLM_normalised_xsection
        normalised_xsection['powhegHerwig'] = powhegHerwig_normalised_xsection
        # normalised_xsection['amcatnloHerwig'] = amcatnloHerwig_normalised_xsection

        normalised_xsection['massdown'] = massdown_normalised_xsection
        normalised_xsection['massup'] = massup_normalised_xsection

    file_template = '{path_to_JSON}/{category}/xsection_normalised_{channel}_{method}.txt'
    filename = file_template.format(
        path_to_JSON = path_to_JSON,
        category = category,
        channel = channel,
        method = method,
    )

    if normalise_to_one:
        filename = filename.replace( 'xsection_normalised', 'xsection_normalised_to_one' )
    write_data_to_JSON( normalised_xsection, filename )

if __name__ == '__main__':
    set_root_defaults( msg_ignore_level = 3001 )
    # setup
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data/normalisation/background_subtraction/',
                      help = "set path to JSON files" )
    parser.add_option( "-v", "--variable", dest = "variable", default = 'MET',
                      help = "set the variable to analyse (MET, HT, ST, MT)" )
    parser.add_option( "-b", "--bjetbin", dest = "bjetbin", default = '2m',
                      help = "set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m" )
    parser.add_option( "-m", "--metType", dest = "metType", default = 'type1',
                      help = "set MET type for analysis of MET, ST or MT" )
    parser.add_option( "-u", "--unfolding_method", dest = "unfolding_method", default = 'TUnfold',
                      help = "Unfolding method: RooUnfoldSvd (default), TSVDUnfold, RooUnfoldTUnfold, RooUnfoldInvert, RooUnfoldBinByBin, RooUnfoldBayes" )
    parser.add_option( "-e", "--error_treatment", type = 'int',
                      dest = "error_treatment", default = unfoldCfg.error_treatment,
                      help = "parameter for error treatment in RooUnfold" )
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
    
    centre_of_mass = options.CoM
    luminosity = measurement_config.luminosity * measurement_config.luminosity_scale
    ttbar_xsection = measurement_config.ttbar_xsection
    path_to_files = measurement_config.path_to_files
    file_for_unfolding = File( measurement_config.unfolding_central, 'read' )

    files_for_pdfs = { 'PDFWeights_%d' % (index) : File ( measurement_config.unfolding_pdfweights[index] ) for index in range( 0, 100 ) }

    ###
    file_for_scaledown = File( measurement_config.unfolding_scale_down, 'read' )
    file_for_scaleup = File( measurement_config.unfolding_scale_up, 'read' )
   	###
    file_for_renormalisationdown = File( measurement_config.unfolding_renormalisation_down, 'read' )
    file_for_renormalisationup = File( measurement_config.unfolding_renormalisation_up, 'read' )    
    file_for_factorisationdown = File( measurement_config.unfolding_factorisation_down, 'read' )
    file_for_factorisationup = File( measurement_config.unfolding_factorisation_up, 'read' )
    file_for_combineddown = File( measurement_config.unfolding_combined_down, 'read' )
    file_for_combinedup = File( measurement_config.unfolding_combined_up, 'read' )
    file_for_alphaSdown = File( measurement_config.unfolding_alphaS_down, 'read' )
    file_for_alphaSup = File( measurement_config.unfolding_alphaS_up, 'read' )
    ###
    file_for_massdown = File( measurement_config.unfolding_mass_down, 'read' )
    file_for_massup = File( measurement_config.unfolding_mass_up, 'read' )
    file_for_jesdown = File( measurement_config.unfolding_jes_down, 'read' )
    file_for_jesup = File( measurement_config.unfolding_jes_up, 'read' )
    ###
    file_for_jerdown = File( measurement_config.unfolding_jer_down, 'read' )
    file_for_jerup = File( measurement_config.unfolding_jer_up, 'read' )
    ###
    file_for_bjetdown = File( measurement_config.unfolding_bjet_down, 'read' )
    file_for_bjetup = File( measurement_config.unfolding_bjet_up, 'read' )
    ###
    file_for_lightjetdown = File( measurement_config.unfolding_lightjet_down, 'read' )
    file_for_lightjetup = File( measurement_config.unfolding_lightjet_up, 'read' )
    ###
    file_for_LeptonDown = File( measurement_config.unfolding_Lepton_down, 'read' )
    file_for_LeptonUp = File( measurement_config.unfolding_Lepton_up, 'read' )
    ###
    file_for_ElectronEnDown = File( measurement_config.unfolding_ElectronEn_down, 'read' )
    file_for_ElectronEnUp = File( measurement_config.unfolding_ElectronEn_up, 'read' )
    ###
    file_for_MuonEnDown = File( measurement_config.unfolding_MuonEn_down, 'read' )
    file_for_MuonEnUp = File( measurement_config.unfolding_MuonEn_up, 'read' )
    ###
    file_for_TauEnDown = File( measurement_config.unfolding_TauEn_down, 'read' )
    file_for_TauEnUp = File( measurement_config.unfolding_TauEn_up, 'read' )
    ###
    file_for_UnclusteredEnDown = File( measurement_config.unfolding_UnclusteredEn_down, 'read' )
    file_for_UnclusteredEnUp = File( measurement_config.unfolding_UnclusteredEn_up, 'read' )
    ###
    file_for_PUUp = File( measurement_config.unfolding_PUSystematic_up, 'read')
    file_for_PUDown = File( measurement_config.unfolding_PUSystematic_down, 'read')

    file_for_powhegPythia8 = File( measurement_config.unfolding_powheg_pythia8, 'read')
    file_for_amcatnlo = File( measurement_config.unfolding_amcatnlo, 'read')
    # file_for_amcatnlo_herwig = File( measurement_config.unfolding_amcatnlo_herwig, 'read')
    file_for_madgraphMLM = File( measurement_config.unfolding_madgraphMLM, 'read')
    file_for_powheg_herwig = File( measurement_config.unfolding_powheg_herwig, 'read' )

    variable = options.variable

    tau_value_electron = measurement_config.tau_values_electron[variable]
    tau_value_muon = measurement_config.tau_values_muon[variable]
    tau_value_combined = measurement_config.tau_values_combined[variable]

    visiblePS = options.visiblePS
    phase_space = 'FullPS'
    if visiblePS:
        phase_space = "VisiblePS"

    unfoldCfg.error_treatment = options.error_treatment
    method = options.unfolding_method
    combine_before_unfolding = options.combine_before_unfolding
    b_tag_bin = translate_options[options.bjetbin]
    path_to_JSON = '{path}/{com}TeV/{variable}/{phase_space}/'.format( 
            path = options.path,
            com = measurement_config.centre_of_mass_energy,
            variable = variable,
            phase_space = phase_space,
            )

    all_measurements = deepcopy( measurement_config.measurements_and_prefixes.keys() )
    
    # ### ttbar pt reweightingng systematic
    # ttbar_theory_systematics = [] #[ 'TTJets_ptreweight' ]
    # all_measurements.extend( ttbar_theory_systematics )

    pdf_uncertainties = ['PDFWeights_%d' % index for index in range( 0, 100 )]
    all_measurements.extend( pdf_uncertainties )


    print 'Performing unfolding for variable', variable
    for category in all_measurements:
        if run_just_central and not category == 'central':
            continue
        # Don't need to consider MET uncertainties for HT, abs_lepton_eta, lepton_pt and NJets
        if ( variable in measurement_config.variables_no_met ) and (category in measurement_config.met_specific_systematics):
            continue
        print 'Unfolding category "%s"' % category

        # read normalisation results from JSON
        electron_file = path_to_JSON + '/' + category + '/normalisation_electron.txt'
        muon_file = path_to_JSON + '/' + category + '/normalisation_muon.txt'

        # don't change normalisation input for ttbar generator/theory systematics and PDF weights
        # For systematics not run in 01 [PDF and TTJet_] then use the central normalisations
        if ttbar_theory_systematic_prefix in category or category in pdf_uncertainties:
            electron_file = path_to_JSON + '/central/normalisation_electron.txt'
            muon_file = path_to_JSON + '/central/normalisation_muon.txt'
            # combined_file = path_to_JSON + '/central/normalisation_combined.txt'           

        # Read the normalisations
        normalisation_results_electron = None
        normalisation_results_muon = None
        if category == 'Muon_up' or category == 'Muon_down':
            normalisation_results_electron = read_data_from_JSON( path_to_JSON + '/central/normalisation_electron.txt' )
            normalisation_results_muon = read_data_from_JSON( muon_file )
        elif category == 'Electron_up' or category == 'Electron_down':
            normalisation_results_electron = read_data_from_JSON( electron_file )
            normalisation_results_muon = read_data_from_JSON( path_to_JSON + '/central/normalisation_muon.txt' )
        else:
            normalisation_results_electron = read_data_from_JSON( electron_file )
            normalisation_results_muon = read_data_from_JSON( muon_file )

        # Combine the normalisations (beforeUnfolding)
        normalisation_results_combined = combine_complex_results(normalisation_results_electron, normalisation_results_muon)
        TTJet_normalisation_results_electron = normalisation_results_electron['TTJet']
        TTJet_normalisation_results_muon = normalisation_results_muon['TTJet']
        TTJet_normalisation_results_combined = normalisation_results_combined['TTJet']

        file_template = '{path_to_JSON}/{category}/unfolded_normalisation_{channel}_{method}.txt'
        filename = ''

        # get unfolded normalisations and xsections
        unfolded_normalisation_electron = {}
        unfolded_normalisation_muon = {}


        # Electron channel
        channel = 'electron'
        unfolded_normalisation_electron = get_unfolded_normalisation( 
            TTJet_normalisation_results_electron, 
            category, 
            channel, 
            tau_value_electron, 
            visiblePS = visiblePS 
        )
        filename = file_template.format(
            path_to_JSON = path_to_JSON,
            category = category,
            channel = channel,
            method = method,
        )
        write_data_to_JSON( unfolded_normalisation_electron, filename )
        # measure xsection
        calculate_xsections( unfolded_normalisation_electron, category, channel )
        calculate_normalised_xsections( unfolded_normalisation_electron, category, channel )
        calculate_normalised_xsections( unfolded_normalisation_electron, category, channel , True )


        # Muon channel
        channel = 'muon'
        unfolded_normalisation_muon = get_unfolded_normalisation( 
            TTJet_normalisation_results_muon, 
            category, 
            channel, 
            tau_value_muon, 
            visiblePS = visiblePS 
        )
        filename = file_template.format(
            path_to_JSON = path_to_JSON,
            category = category,
            channel = channel,
            method = method,
        )
        write_data_to_JSON( unfolded_normalisation_muon, filename )
        # measure xsection
        calculate_xsections( unfolded_normalisation_muon, category, channel )
        calculate_normalised_xsections( unfolded_normalisation_muon, category, channel )
        calculate_normalised_xsections( unfolded_normalisation_muon, category, channel , True )


        # Results where the channels are combined after unfolding
        unfolded_normalisation_combined = combine_complex_results( unfolded_normalisation_electron, unfolded_normalisation_muon )
        channel = 'combined'
        filename = file_template.format(
            path_to_JSON = path_to_JSON,
            category = category,
            channel = channel,
            method = method,
        )
        write_data_to_JSON( unfolded_normalisation_combined, filename )
        # measure xsection
        calculate_xsections( unfolded_normalisation_combined, category, channel )
        calculate_normalised_xsections( unfolded_normalisation_combined, category, channel )
        calculate_normalised_xsections( unfolded_normalisation_combined, category, channel , True )


        # Results where the channels are combined before unfolding (the 'combined in the response matrix')
        unfolded_normalisation_combinedBeforeUnfolding = get_unfolded_normalisation(
            TTJet_normalisation_results_combined,
            category,
            'combined', 
            tau_value=tau_value_combined,
            visiblePS=visiblePS,
        )
        channel = 'combinedBeforeUnfolding'
        filename = file_template.format(
                            path_to_JSON = path_to_JSON,
                            category = category,
                            channel = channel,
                            method = method,
                            )
        write_data_to_JSON( unfolded_normalisation_combinedBeforeUnfolding, filename )
        # measure xsection
        calculate_xsections( unfolded_normalisation_combinedBeforeUnfolding, category, channel )
        calculate_normalised_xsections( unfolded_normalisation_combinedBeforeUnfolding, category, channel )
        calculate_normalised_xsections( unfolded_normalisation_combinedBeforeUnfolding, category, channel , True )
