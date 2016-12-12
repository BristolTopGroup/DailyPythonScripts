# general
from __future__ import division
from argparse import ArgumentParser
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
from dps.utils.ROOT_utils import set_root_defaults
from dps.utils.pandas_utilities import read_tuple_from_file, write_tuple_to_df
from copy import deepcopy

def get_unfolding_files(measurement_config):
    '''
    Return the set of unfolding files to use
    '''
    unfolding_files = {}

    unfolding_files['file_for_unfolding']           = File( measurement_config.unfolding_central, 'read' )

    unfolding_files['files_for_pdfs']               = { 
        'PDFWeights_%d' % (index) : File ( measurement_config.unfolding_pdfweights[index] ) for index in range( 0, 100 ) 
    }

    unfolding_files['file_for_scaledown']           = File( measurement_config.unfolding_scale_down, 'read' )
    unfolding_files['file_for_scaleup']             = File( measurement_config.unfolding_scale_up, 'read' )

    unfolding_files['file_for_renormalisationdown'] = File( measurement_config.unfolding_renormalisation_down, 'read' )
    unfolding_files['file_for_renormalisationup']   = File( measurement_config.unfolding_renormalisation_up, 'read' )    
    unfolding_files['file_for_factorisationdown']   = File( measurement_config.unfolding_factorisation_down, 'read' )
    unfolding_files['file_for_factorisationup']     = File( measurement_config.unfolding_factorisation_up, 'read' )
    unfolding_files['file_for_combineddown']        = File( measurement_config.unfolding_combined_down, 'read' )
    unfolding_files['file_for_combinedup']          = File( measurement_config.unfolding_combined_up, 'read' )
    unfolding_files['file_for_alphaSdown']          = File( measurement_config.unfolding_alphaS_down, 'read' )
    unfolding_files['file_for_alphaSup']            = File( measurement_config.unfolding_alphaS_up, 'read' )

    unfolding_files['file_for_massdown']            = File( measurement_config.unfolding_mass_down, 'read' )
    unfolding_files['file_for_massup']              = File( measurement_config.unfolding_mass_up, 'read' )

    unfolding_files['file_for_jesdown']             = File( measurement_config.unfolding_jes_down, 'read' )
    unfolding_files['file_for_jesup']               = File( measurement_config.unfolding_jes_up, 'read' )
    unfolding_files['file_for_jerdown']             = File( measurement_config.unfolding_jer_down, 'read' )
    unfolding_files['file_for_jerup']               = File( measurement_config.unfolding_jer_up, 'read' )

    unfolding_files['file_for_bjetdown']            = File( measurement_config.unfolding_bjet_down, 'read' )
    unfolding_files['file_for_bjetup']              = File( measurement_config.unfolding_bjet_up, 'read' )
    unfolding_files['file_for_lightjetdown']        = File( measurement_config.unfolding_lightjet_down, 'read' )
    unfolding_files['file_for_lightjetup']          = File( measurement_config.unfolding_lightjet_up, 'read' )

    unfolding_files['file_for_LeptonDown']          = File( measurement_config.unfolding_Lepton_down, 'read' )
    unfolding_files['file_for_LeptonUp']            = File( measurement_config.unfolding_Lepton_up, 'read' )

    unfolding_files['file_for_ElectronEnDown']      = File( measurement_config.unfolding_ElectronEn_down, 'read' )
    unfolding_files['file_for_ElectronEnUp']        = File( measurement_config.unfolding_ElectronEn_up, 'read' )
    unfolding_files['file_for_MuonEnDown']          = File( measurement_config.unfolding_MuonEn_down, 'read' )
    unfolding_files['file_for_MuonEnUp']            = File( measurement_config.unfolding_MuonEn_up, 'read' )
    unfolding_files['file_for_TauEnDown']           = File( measurement_config.unfolding_TauEn_down, 'read' )
    unfolding_files['file_for_TauEnUp']             = File( measurement_config.unfolding_TauEn_up, 'read' )
    unfolding_files['file_for_UnclusteredEnDown']   = File( measurement_config.unfolding_UnclusteredEn_down, 'read' )
    unfolding_files['file_for_UnclusteredEnUp']     = File( measurement_config.unfolding_UnclusteredEn_up, 'read' )

    unfolding_files['file_for_PUUp']                = File( measurement_config.unfolding_PUSystematic_up, 'read')
    unfolding_files['file_for_PUDown']              = File( measurement_config.unfolding_PUSystematic_down, 'read')

    unfolding_files['file_for_powhegPythia8']       = File( measurement_config.unfolding_powheg_pythia8, 'read')
    unfolding_files['file_for_amcatnlo']            = File( measurement_config.unfolding_amcatnlo, 'read')
    unfolding_files['file_for_amcatnlo_herwig']     = File( measurement_config.unfolding_amcatnlo_herwig, 'read')
    unfolding_files['file_for_madgraphMLM']         = File( measurement_config.unfolding_madgraphMLM, 'read')
    unfolding_files['file_for_powheg_herwig']       = File( measurement_config.unfolding_powheg_herwig, 'read' )
    return unfolding_files


def unfold_results( results, category, channel, tau_value, h_truth, h_measured, h_response, h_fakes, method, visiblePS ):
    global variable, path_to_DF, args
    edges = reco_bin_edges_full[variable]
    if visiblePS:
        edges = reco_bin_edges_vis[variable]
    h_data = value_error_tuplelist_to_hist( results, edges )

    # Remove fakes before unfolding
    h_data_no_fakes = removeFakes( h_measured, h_fakes, h_data )

    # unfold
    unfolding = Unfolding( h_data_no_fakes, h_truth, h_measured, h_response, h_fakes, method = method, tau = tau_value )

    # turning off the unfolding errors for systematic samples
    if not category == 'central':
        unfoldCfg.error_treatment = 0
    else:
        unfoldCfg.error_treatment = args.error_treatment

    h_unfolded_data = unfolding.unfold()
    # print "h_response bin edges : ", h_response
    # print "h_unfolded_data bin edges : ", h_unfolded_data
    h_data_no_fakes = h_data_no_fakes.rebinned(2)
    h_data = h_data.rebinned(2)

    del unfolding
    return hist_to_value_error_tuplelist( h_data ), hist_to_value_error_tuplelist( h_unfolded_data ), hist_to_value_error_tuplelist( h_data_no_fakes )

# def data_covariance_matrix( data ):
#     values = list( data )
#     get_bin_error = data.GetBinError
#     cov_matrix = Hist2D( len( values ), -10, 10, len( values ), -10, 10, type = 'D' )
#     for bin_i in range( len( values ) ):
#         error = get_bin_error( bin_i + 1 )
#         cov_matrix.SetBinContent( bin_i + 1, bin_i + 1, error * error )
#     return cov_matrix

def get_unfolded_normalisation( TTJet_normalisation_results, category, channel, tau_value, visiblePS ):
    global com, luminosity, ttbar_xsection, method, variable, path_to_DF
    global unfolding_files, file_for_ptreweight

    # Add in this option?
    global use_ptreweight
    files_for_systematics = {
        'TTJets_scaledown'       	 :  unfolding_files['file_for_scaledown'],
        'TTJets_scaleup'         	 :  unfolding_files['file_for_scaleup'],
        'TTJets_massdown'        	 :  unfolding_files['file_for_massdown'],
        'TTJets_massup'          	 :  unfolding_files['file_for_massup'],
       
        'TTJets_factorisationdown'	 :  unfolding_files['file_for_factorisationdown'],
        'TTJets_factorisationup'   	 :  unfolding_files['file_for_factorisationup'],
        'TTJets_renormalisationdown' :  unfolding_files['file_for_renormalisationdown'],
        'TTJets_renormalisationup'   :  unfolding_files['file_for_renormalisationup'],
        'TTJets_combineddown'     	 :  unfolding_files['file_for_combineddown'],
        'TTJets_combinedup'          :  unfolding_files['file_for_combinedup'],
        'TTJets_alphaSdown'			 :  unfolding_files['file_for_alphaSdown'],
        'TTJets_alphaSup'   	     :  unfolding_files['file_for_alphaSup'],

        'JES_down'                   :  unfolding_files['file_for_jesdown'],
        'JES_up'                     :  unfolding_files['file_for_jesup'],

        'JER_down'                   :  unfolding_files['file_for_jerdown'],
        'JER_up'                     :  unfolding_files['file_for_jerup'],

        'BJet_up'                    :  unfolding_files['file_for_bjetup'],
        'BJet_down'                  :  unfolding_files['file_for_bjetdown'],

        'LightJet_up'                :  unfolding_files['file_for_lightjetup'],
        'LightJet_down'              :  unfolding_files['file_for_lightjetdown'],

        'TTJets_hadronisation'       :  unfolding_files['file_for_powheg_herwig'],
        'TTJets_NLOgenerator'        :  unfolding_files['file_for_amcatnlo'],

        'ElectronEnUp'               :  unfolding_files['file_for_ElectronEnUp'],
        'ElectronEnDown'             :  unfolding_files['file_for_ElectronEnDown'],
        'MuonEnUp'                   :  unfolding_files['file_for_MuonEnUp'],
        'MuonEnDown'                 :  unfolding_files['file_for_MuonEnDown'],
        'TauEnUp'                    :  unfolding_files['file_for_TauEnUp'],
        'TauEnDown'                  :  unfolding_files['file_for_TauEnDown'],
        'UnclusteredEnUp'            :  unfolding_files['file_for_UnclusteredEnUp'],
        'UnclusteredEnDown'          :  unfolding_files['file_for_UnclusteredEnDown'],

        'Muon_up'                    :  unfolding_files['file_for_LeptonUp'],
        'Muon_down'                  :  unfolding_files['file_for_LeptonDown'],
        'Electron_up'                :  unfolding_files['file_for_LeptonUp'],
        'Electron_down'              :  unfolding_files['file_for_LeptonDown'],

        'PileUp_up'                  :  unfolding_files['file_for_PUUp'],
        'PileUp_down'                :  unfolding_files['file_for_PUDown'],
    }

    h_truth, h_measured, h_response, h_fakes = None, None, None, None

    # Uncertainties by changing the response matrix
    if category in files_for_systematics :
        print 'Doing category',category,'by changing response matrix'
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( 
            inputfile = files_for_systematics[category],
            variable = variable,
            channel = channel,
            com = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
    # PDF Uncertainties
    elif category in pdf_uncertainties:
        print 'Doing category',category,'by changing response matrix'
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( 
            inputfile = unfolding_files['files_for_pdfs'][category],
            variable = variable,
            channel = channel,
            com = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
    # Central and systematics where you just change input MC
    else:
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( 
            inputfile = unfolding_files['file_for_unfolding'],
            variable = variable,
            channel = channel,
            com = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )

    # Unfold current normalisation measurements  
    TTJet_normalisation_results, TTJet_normalisation_results_unfolded, TTJet_normalisation_results_withoutFakes = unfold_results( 
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

    # Store TTJet yields after background subtraction, after background subtraction without fakes and after Unfolding
    normalisation_unfolded = {
        'TTJet_measured'                : TTJet_normalisation_results,
        'TTJet_measured_withoutFakes'   : TTJet_normalisation_results_withoutFakes,
        'TTJet_unfolded'                : TTJet_normalisation_results_unfolded,
    }

    # Return truth of different generators for comparison to data in 04
    if category == 'central':
        h_truth_massdown, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = file_for_massdown,
            variable = variable,
            channel = channel,
            com = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_massup, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = file_for_massup,
            variable = variable,
            channel = channel,
            com = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_powhegPythia8, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = file_for_powhegPythia8,
            variable = variable,
            channel = channel,
            com = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_amcatnlo, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = file_for_amcatnlo,
            variable = variable,
            channel = channel,
            com = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_madgraphMLM, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = file_for_madgraphMLM,
            variable = variable,
            channel = channel,
            com = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_powheg_herwig, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = file_for_powheg_herwig,
            variable = variable,
            channel = channel,
            com = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
    
        normalisation_unfolded['powhegPythia8'] = hist_to_value_error_tuplelist( h_truth_powhegPythia8 )
        normalisation_unfolded['amcatnlo']      = hist_to_value_error_tuplelist( h_truth_madgraphMLM )
        normalisation_unfolded['madgraphMLM']   = hist_to_value_error_tuplelist( h_truth_amcatnlo )
        normalisation_unfolded['powhegHerwig']  = hist_to_value_error_tuplelist( h_truth_powheg_herwig )

        normalisation_unfolded['massdown']      = hist_to_value_error_tuplelist( h_truth_massdown )
        normalisation_unfolded['massup']        = hist_to_value_error_tuplelist( h_truth_massup )

    # Write all normalisations in unfolded binning scheme to dataframes
    file_template = '{path_to_DF}/{category}/unfolded_normalisation_{channel}_{method}.txt'
    write_02(normalisation_unfolded, file_template, path_to_DF, category, channel, method)
    return normalisation_unfolded


def calculate_xsections( normalisation, category, channel ):
    '''
    Calculate the xsection
    '''
    global variable, path_to_DF
    # calculate the x-sections
    branching_ratio = 0.15
    if 'combined' in channel:
        branching_ratio = branching_ratio * 2

    xsection_unfolded = {}
    xsection_unfolded['TTJet_measured'] = calculate_xsection( 
        normalisation['TTJet_measured'], 
        luminosity,  # L in pb1
        branching_ratio 
    )  
    xsection_unfolded['TTJet_measured_withoutFakes'] = calculate_xsection( 
        normalisation['TTJet_measured_withoutFakes'], 
        luminosity, 
        branching_ratio 
    ) 
    xsection_unfolded['TTJet_unfolded'] = calculate_xsection( 
        normalisation['TTJet_unfolded'], 
        luminosity, 
        branching_ratio 
    )

    if category == 'central':
        xsection_unfolded['powhegPythia8'] = calculate_xsection( 
            normalisation['powhegPythia8'], 
            luminosity, 
            branching_ratio 
        )
        xsection_unfolded['amcatnlo'] = calculate_xsection( 
            normalisation['amcatnlo'], 
            luminosity, 
            branching_ratio 
        )
        xsection_unfolded['madgraphMLM'] = calculate_xsection( 
            normalisation['powhegHerwig'], 
            luminosity, 
            branching_ratio 
        )
        xsection_unfolded['powhegHerwig'] = calculate_xsection( 
            normalisation['madgraphMLM'], 
            luminosity, 
            branching_ratio 
        )

        xsection_unfolded['massdown'] = calculate_xsection( 
            normalisation['massdown'], 
            luminosity, 
            branching_ratio 
        )
        xsection_unfolded['massup'] = calculate_xsection( 
            normalisation['massup'], 
            luminosity, 
            branching_ratio 
        )

    file_template = '{path_to_DF}/{category}/xsection_{channel}_{method}.txt'
    write_02(xsection_unfolded, file_template, path_to_DF, category, channel, method)
    return

def calculate_normalised_xsections( normalisation, category, channel, normalise_to_one = False ):
    '''
    Calculate the normalised cross sections
    '''
    global variable, path_to_DF, phase_space

    binWidths = None
    if phase_space == 'VisiblePS':
        binWidths = bin_widths_visiblePS
    elif phase_space == 'FullPS':
        binWidths = bin_widths
    
    normalised_xsection = {}
    normalised_xsection['TTJet_measured'] = calculate_normalised_xsection( 
        normalisation['TTJet_measured'], 
        binWidths[variable], 
        normalise_to_one 
    )
    normalised_xsection['TTJet_measured_withoutFakes'] = calculate_normalised_xsection( 
        normalisation['TTJet_measured_withoutFakes'], 
        binWidths[variable], 
        normalise_to_one 
    )
    normalised_xsection['TTJet_unfolded'] = calculate_normalised_xsection( 
        normalisation['TTJet_unfolded'], 
        binWidths[variable], 
        normalise_to_one 
    )

    if category == 'central':
        normalised_xsection['massdown'] = calculate_normalised_xsection( 
            normalisation['powhegPythia8'], 
            binWidths[variable], 
            normalise_to_one, 
        )
        normalised_xsection['massdown'] = calculate_normalised_xsection( 
            normalisation['amcatnlo'], 
            binWidths[variable], 
            normalise_to_one, 
        )
        normalised_xsection['massdown'] = calculate_normalised_xsection( 
            normalisation['powhegHerwig'], 
            binWidths[variable], 
            normalise_to_one, 
        )
        normalised_xsection['massdown'] = calculate_normalised_xsection( 
            normalisation['madgraphMLM'], 
            binWidths[variable], 
            normalise_to_one, 
        )

        normalised_xsection['massdown'] = calculate_normalised_xsection( 
            normalisation['massdown'], 
            binWidths[variable], 
            normalise_to_one, 
        )
        normalised_xsection['massdown'] = calculate_normalised_xsection( 
            normalisation['massup'], 
            binWidths[variable], 
            normalise_to_one, 
        )

    file_template = '{path_to_DF}/{category}/xsection_normalised_{channel}_{method}.txt'
    if normalise_to_one:
        file_template = file_template.replace( 'xsection_normalised', 'xsection_normalised_to_one' )
    write_02(normalised_xsection, file_template, path_to_DF, category, channel, method)

def write_02(tuple_out, f_temp, path_to_DF, category, channel, method):
    f = f_temp.format(
        path_to_DF = path_to_DF,
        category = category,
        channel = channel,
        method = method,
    )
    write_tuple_to_df( tuple_out, f )
    return f

def parse_arguments():
    parser = ArgumentParser(__doc__)
    parser.add_argument( "-p", "--path", dest = "path", default = 'data/normalisation/background_subtraction/',
                      help = "set path to JSON files" )
    parser.add_argument( "-v", "--variable", dest = "variable", default = 'MET',
                      help = "set the variable to analyse (MET, HT, ST, MT)" )
    parser.add_argument( "-u", "--unfolding_method", dest = "unfolding_method", default = 'TUnfold',
                      help = "Unfolding method: TUnfold" )
    parser.add_argument( "-e", "--error_treatment", type = int,
                      dest = "error_treatment", default = unfoldCfg.error_treatment,
                      help = "parameter for error treatment in RooUnfold")
    parser.add_argument( "-c", "--centre-of-mass-energy", dest = "com", default = 13,
                      help = "set the centre of mass energy for analysis. Default = 13 [TeV]", type = int )
    parser.add_argument( "-C", "--combine-before-unfolding", dest = "combine_before_unfolding", action = "store_true",
                      help = "Perform combination of channels before unfolding" )
    parser.add_argument( '--test', dest = "test", action = "store_true",
                      help = "Just run the central measurement" )
    parser.add_argument( '--ptreweight', dest = "ptreweight", action = "store_true",
                      help = "Use pt-reweighted MadGraph for the measurement" )
    parser.add_argument( '--visiblePS', dest = "visiblePS", action = "store_true",
                      help = "Unfold to visible phase space" )
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    set_root_defaults( msg_ignore_level = 3001 )
    # setup
    args = parse_arguments()

    # Cache arguments
    run_just_central            = args.test
    use_ptreweight              = args.ptreweight
    variable                    = args.variable
    com                         = args.com
    unfoldCfg.error_treatment   = args.error_treatment
    method                      = args.unfolding_method
    combine_before_unfolding    = args.combine_before_unfolding
    visiblePS                   = args.visiblePS

    # Cache arguments from xsection config
    measurement_config  = XSectionConfig( com )
    luminosity          = measurement_config.luminosity * measurement_config.luminosity_scale
    ttbar_xsection      = measurement_config.ttbar_xsection
    tau_value_electron  = measurement_config.tau_values_electron[variable]
    tau_value_muon      = measurement_config.tau_values_muon[variable]
    tau_value_combined  = measurement_config.tau_values_combined[variable]

    phase_space = 'FullPS'
    if visiblePS:
        phase_space = "VisiblePS"

    unfolding_files = get_unfolding_files(measurement_config)
    path_to_DF = 'TESTING/{path}/{com}TeV/{variable}/{phase_space}/'.format( 
        path = args.path,
        com = measurement_config.com_energy,
        variable = variable,
        phase_space = phase_space,
    )

    # Core Systematics
    all_measurements    = deepcopy( measurement_config.measurements )
    # Adding PDF Systematics
    pdf_uncertainties   = ['PDFWeights_%d' % index for index in range( 0, 100 )]
    all_measurements.extend( pdf_uncertainties )
    # # TTBar Reweighting Systematics
    # ttbar_theory_systematics = [ 'TTJets_ptreweight', 'TTJets_etareweight' ]
    # all_measurements.extend( ttbar_theory_systematics )

    print 'Performing unfolding for variable', variable
    for category in all_measurements:
        if run_just_central and not category == 'central': 
            continue
        if ( variable in measurement_config.variables_no_met ) and (category in measurement_config.met_specific_systematics):
            continue
        print 'Unfolding category "%s"' % category

        # read normalisation results from JSON
        electron_file   = path_to_DF + '/' + category + '/normalisation_electron.txt'
        muon_file       = path_to_DF + '/' + category + '/normalisation_muon.txt'
        combined_file   = path_to_DF + '/' + category + '/normalisation_combined.txt'

        # don't change normalisation input for ttbar generator/theory systematics and PDF weights
        # For systematics not run in 01 [PDF and TTJet_] then use the central normalisations
        if category not in measurement_config.normalisation_systematics:
            electron_file   = path_to_DF + '/central/normalisation_electron.txt'
            muon_file       = path_to_DF + '/central/normalisation_muon.txt'
            combined_file   = path_to_DF + '/central/normalisation_combined.txt'           

        # Read the normalisations
        normalisation_results_electron  = None
        normalisation_results_muon      = None
        normalisation_results_combined  = None

        # Read the normalisation files
        # For LeptonUp/Down return other lepton type to central normailsation
        # THINK HOW TO READ MUON:ELECTRON/UP:DOWN WITH COMBINEDBEFOREUNFOLDING
        if category == 'Muon_up' or category == 'Muon_down':
            normalisation_results_electron  = read_tuple_from_file( path_to_DF + '/central/normalisation_electron.txt' )
            normalisation_results_muon      = read_tuple_from_file( muon_file )
            # normalisation_results_combined = read_tuple_from_file( combined_file )
        elif category == 'Electron_up' or category == 'Electron_down':
            normalisation_results_electron  = read_tuple_from_file( electron_file )
            normalisation_results_muon      = read_tuple_from_file( path_to_DF + '/central/normalisation_muon.txt' )
            # normalisation_results_combined = read_tuple_from_file( combined_file )
        else:
            normalisation_results_electron  = read_tuple_from_file( electron_file )
            normalisation_results_muon      = read_tuple_from_file( muon_file )
            # normalisation_results_combined  = read_tuple_from_file( combined_file )

        # Combine the normalisations (beforeUnfolding)
        # normalisation_results_combined = combine_complex_results(normalisation_results_electron, normalisation_results_muon)
        # TTJet_normalisation_results_electron = normalisation_results_electron['TTJet']
        TTJet_normalisation_results_muon = normalisation_results_muon['TTJet']
        # TTJet_normalisation_results_combined = normalisation_results_combined['TTJet']

        # # get unfolded normalisations and xsections
        unfolded_normalisation_electron                 = {}
        unfolded_normalisation_muon                     = {}
        unfolded_normalisation_combined                 = {}
        unfolded_normalisation_combinedBeforeUnfolding  = {}


        # # Electron channel
        # channel = 'electron'
        # unfolded_normalisation_electron = get_unfolded_normalisation( 
        #     TTJet_normalisation_results_electron, 
        #     category, 
        #     channel, 
        #     tau_value_electron, 
        #     visiblePS = visiblePS 
        # )
        # # measure xsection
        # calculate_xsections( unfolded_normalisation_electron, category, channel )
        # calculate_normalised_xsections( unfolded_normalisation_electron, category, channel )
        # calculate_normalised_xsections( unfolded_normalisation_electron, category, channel , True )

        # Muon channel
        channel = 'muon'
        unfolded_normalisation_muon = get_unfolded_normalisation( 
            TTJet_normalisation_results_muon, 
            category, 
            channel, 
            tau_value_muon, 
            visiblePS = visiblePS 
        )
        # measure xsection
        calculate_xsections( unfolded_normalisation_muon, category, channel )
        calculate_normalised_xsections( unfolded_normalisation_muon, category, channel )
        calculate_normalised_xsections( unfolded_normalisation_muon, category, channel , True )

        # # Results where the channels are combined before unfolding (the 'combined in the response matrix')
        # channel = 'combinedBeforeUnfolding'
        # unfolded_normalisation_combinedBeforeUnfolding = get_unfolded_normalisation(
        #     TTJet_normalisation_results_combined,
        #     category,
        #     'combined', 
        #     tau_value=tau_value_combined,
        #     visiblePS=visiblePS,
        # )
        # # measure xsection
        # calculate_xsections( unfolded_normalisation_combinedBeforeUnfolding, category, channel )
        # calculate_normalised_xsections( unfolded_normalisation_combinedBeforeUnfolding, category, channel )
        # calculate_normalised_xsections( unfolded_normalisation_combinedBeforeUnfolding, category, channel , True )

        # # Results where the channels are combined after unfolding
        # channel = 'combined'
        # unfolded_normalisation_combined = combine_complex_results( unfolded_normalisation_electron, unfolded_normalisation_muon )
        # # measure xsection
        # calculate_xsections( unfolded_normalisation_combined, category, channel )
        # calculate_normalised_xsections( unfolded_normalisation_combined, category, channel )
        # calculate_normalised_xsections( unfolded_normalisation_combined, category, channel , True )



