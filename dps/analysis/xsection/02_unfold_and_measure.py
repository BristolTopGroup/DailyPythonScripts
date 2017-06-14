# general
from __future__ import division
from argparse import ArgumentParser
# rootpy
from rootpy.io import File

# DailyPythonScripts
import dps.config.unfold as unfoldCfg
from dps.config.variable_binning import bin_widths, bin_widths_visiblePS, reco_bin_edges_full, reco_bin_edges_vis
from dps.config.xsection import XSectionConfig
from dps.utils.Calculation import calculate_xsection, calculate_normalised_xsection, \
combine_complex_results
from dps.utils.hist_utilities import hist_to_value_error_tuplelist, \
value_error_tuplelist_to_hist
from dps.utils.Unfolding import Unfolding, get_unfold_histogram_tuple, removeFakes, \
plot_probability_matrix
from dps.utils.ROOT_utils import set_root_defaults
from dps.utils.pandas_utilities import read_tuple_from_file, write_tuple_to_df, combine_complex_df, \
create_covariance_matrix

from numpy import array, sqrt
from copy import deepcopy

def get_unfolding_files(measurement_config):
    '''
    Return the set of unfolding files to use
    '''
    unfolding_files = {}

    unfolding_files['file_for_unfolding']           = File( measurement_config.unfolding_central, 'read' )

    unfolding_files['files_for_pdfs']               = { 
        'PDFWeights_%d' % (index) : File ( measurement_config.unfolding_pdfweights[index] ) for index in range( measurement_config.pdfWeightMin, measurement_config.pdfWeightMax ) 
    }
    unfolding_files['files_for_ct14pdfs']           = { 
        'CT14Weights_%d' % (index) : File ( measurement_config.unfolding_CT14weights[index] ) for index in range( measurement_config.pdfWeightMin, measurement_config.ct14WeightMax ) 
    }
    unfolding_files['files_for_mmht14pdfs']         = { 
        'MMHT14Weights_%d' % (index) : File ( measurement_config.unfolding_MMHT14weights[index] ) for index in range( measurement_config.pdfWeightMin, measurement_config.mmht14WeightMax ) 
    }

    unfolding_files['file_for_renormalisationdown'] = File( measurement_config.unfolding_renormalisation_down, 'read' )
    unfolding_files['file_for_renormalisationup']   = File( measurement_config.unfolding_renormalisation_up, 'read' )    
    unfolding_files['file_for_factorisationdown']   = File( measurement_config.unfolding_factorisation_down, 'read' )
    unfolding_files['file_for_factorisationup']     = File( measurement_config.unfolding_factorisation_up, 'read' )
    unfolding_files['file_for_combineddown']        = File( measurement_config.unfolding_combined_down, 'read' )
    unfolding_files['file_for_combinedup']          = File( measurement_config.unfolding_combined_up, 'read' )
    unfolding_files['file_for_alphaSdown']          = File( measurement_config.unfolding_alphaS_down, 'read' )
    unfolding_files['file_for_alphaSup']            = File( measurement_config.unfolding_alphaS_up, 'read' )

    unfolding_files['file_for_hdampdown']          = File( measurement_config.unfolding_hdamp_down, 'read' )
    unfolding_files['file_for_hdampup']            = File( measurement_config.unfolding_hdamp_up, 'read' )

    unfolding_files['file_for_erdOn']            = File( measurement_config.unfolding_erdOn, 'read' )
    unfolding_files['file_for_QCDbased_erdOn']            = File( measurement_config.unfolding_QCDbased_erdOn, 'read' )
    # unfolding_files['file_for_GluonMove']            = File( measurement_config.unfolding_GluonMove, 'read' )

    unfolding_files['file_for_semiLepBrdown']          = File( measurement_config.unfolding_semiLepBr_down, 'read' )
    unfolding_files['file_for_semiLepBrup']            = File( measurement_config.unfolding_semiLepBr_up, 'read' )

    unfolding_files['file_for_fragdown']          = File( measurement_config.unfolding_frag_down, 'read' )
    unfolding_files['file_for_fragup']            = File( measurement_config.unfolding_frag_up, 'read' )
    unfolding_files['file_for_petersonFrag']            = File( measurement_config.unfolding_petersonFrag, 'read' )

    unfolding_files['file_for_isrdown']             = File( measurement_config.unfolding_isr_down, 'read' )
    unfolding_files['file_for_isrup']               = File( measurement_config.unfolding_isr_up, 'read' )
    unfolding_files['file_for_fsrdown']             = File( measurement_config.unfolding_fsr_down, 'read' )
    unfolding_files['file_for_fsrup']               = File( measurement_config.unfolding_fsr_up, 'read' )
    unfolding_files['file_for_uedown']              = File( measurement_config.unfolding_ue_down, 'read' )
    unfolding_files['file_for_ueup']                = File( measurement_config.unfolding_ue_up, 'read' )

    unfolding_files['file_for_topPtSystematic']     = File( measurement_config.unfolding_topPtSystematic, 'read' )

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

    unfolding_files['file_for_ptreweight']          = File( measurement_config.unfolding_ptreweight, 'read' )

    unfolding_files['file_for_powhegPythia8']       = File( measurement_config.unfolding_powheg_pythia8, 'read')
    unfolding_files['file_for_amcatnlo']            = File( measurement_config.unfolding_amcatnlo, 'read')
    unfolding_files['file_for_madgraphMLM']         = File( measurement_config.unfolding_madgraphMLM, 'read')
    unfolding_files['file_for_powheg_herwig']       = File( measurement_config.unfolding_powheg_herwig, 'read' )
    return unfolding_files


def unfold_results( results, category, channel, tau_value, h_truth, h_measured, h_response, h_fakes, method, visiblePS ):
    global variable, path_to_DF, args

    edges = reco_bin_edges_full[variable]
    if visiblePS:
        edges = reco_bin_edges_vis[variable]

    h_data = value_error_tuplelist_to_hist( results, edges )

    # Rebin original TTJet_Measured in terms of final binning (h_data is later replaced with h_data_no_fakes)
    h_data_rebinned = h_data.rebinned(2)

    # Remove fakes before unfolding
    h_data_no_fakes = removeFakes( h_measured, h_fakes, h_data )

    # print 'Integral of data and response matrix'
    # print category
    # print h_data_no_fakes.Integral()
    # print h_response.ProjectionX('px',1).Integral()
    # print 'Ratio : ', h_data_no_fakes.Integral() / h_response.ProjectionX('px',1).Integral()
    h_response.Scale( h_data_no_fakes.Integral() / h_response.ProjectionX('px',1).Integral() )
    # print 'New ratio : ', h_data_no_fakes.Integral() / h_response.ProjectionX('px',1).Integral()

    # unfold
    unfolding = Unfolding( h_data_no_fakes, h_truth, h_measured, h_response, h_fakes, method = method, tau = tau_value )

    # turning off the unfolding errors for systematic samples
    if not category == 'central':
        unfoldCfg.error_treatment = 0
    else:
        unfoldCfg.error_treatment = args.error_treatment

    h_unfolded_data = unfolding.unfold()
    h_data_no_fakes = h_data_no_fakes.rebinned(2)
    covariance_matrix = None
    inputMC_covariance_matrix = None
    if category == 'central':
        # Return the Probabiliy Matrix
        probability_matrix = unfolding.return_probability_matrix()
        plot_probability_matrix(probability_matrix, variable, channel )

        # Return the covariance matrices (They have been normailsed)
        covariance_matrix, correlation_matrix, inputMC_covariance_matrix = unfolding.get_covariance_matrix()

        # Write data statistical covariance matrices
        covariance_output_template = '{path_to_DF}/central/covarianceMatrices/unfoldedNumberOfEvents/{cat}_{label}_{channel}.txt'
        channelForOutputFile = channel
        if channel == 'combined':
            channelForOutputFile = 'combinedBeforeUnfolding'
        # Unfolded number of events
        table_outfile=covariance_output_template.format( path_to_DF=path_to_DF, channel = channelForOutputFile, label='Covariance', cat='Stat_unfoldedNormalisation' )
        create_covariance_matrix( covariance_matrix, table_outfile)
        table_outfile=covariance_output_template.format( path_to_DF=path_to_DF, channel = channelForOutputFile, label='Correlation', cat='Stat_unfoldedNormalisation' )
        create_covariance_matrix( correlation_matrix, table_outfile)
        table_outfile=covariance_output_template.format( path_to_DF=path_to_DF, channel = channelForOutputFile, label='Covariance', cat='Stat_inputMC' )
        create_covariance_matrix( covariance_matrix, table_outfile)
    del unfolding
    return hist_to_value_error_tuplelist( h_data_rebinned ), hist_to_value_error_tuplelist( h_unfolded_data ), hist_to_value_error_tuplelist( h_data_no_fakes ), covariance_matrix, inputMC_covariance_matrix

def get_unfolded_normalisation( TTJet_normalisation_results, category, channel, tau_value, visiblePS ):
    global com, luminosity, ttbar_xsection, method, variable, path_to_DF
    global unfolding_files, additionalPDFSets

    files_for_systematics = {

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

        'TTJets_hdampdown'        :  unfolding_files['file_for_hdampdown'],
        'TTJets_hdampup'          :  unfolding_files['file_for_hdampup'],
        'TTJets_semiLepBrdown'        :  unfolding_files['file_for_semiLepBrdown'],
        'TTJets_semiLepBrup'          :  unfolding_files['file_for_semiLepBrup'],
        'TTJets_fragdown'        :  unfolding_files['file_for_fragdown'],
        'TTJets_fragup'          :  unfolding_files['file_for_fragup'],
        'TTJets_petersonFrag'          :  unfolding_files['file_for_petersonFrag'],
        'TTJets_erdOn'          :  unfolding_files['file_for_erdOn'],
        'TTJets_QCDbased_erdOn'          :  unfolding_files['file_for_QCDbased_erdOn'],
        # 'TTJets_GluonMove'          :  unfolding_files['file_for_GluonMove'],

        'TTJets_isrdown'             :  unfolding_files['file_for_isrdown'],
        'TTJets_isrup'               :  unfolding_files['file_for_isrup'],
        'TTJets_fsrdown'             :  unfolding_files['file_for_fsrdown'],
        'TTJets_fsrup'               :  unfolding_files['file_for_fsrup'],
        'TTJets_uedown'              :  unfolding_files['file_for_uedown'],
        'TTJets_ueup'                :  unfolding_files['file_for_ueup'],

        'TTJets_topPt'               :  unfolding_files['file_for_topPtSystematic'],

        'JES_down'                   :  unfolding_files['file_for_jesdown'],
        'JES_up'                     :  unfolding_files['file_for_jesup'],

        'JER_down'                   :  unfolding_files['file_for_jerdown'],
        'JER_up'                     :  unfolding_files['file_for_jerup'],

        'BJet_up'                    :  unfolding_files['file_for_bjetup'],
        'BJet_down'                  :  unfolding_files['file_for_bjetdown'],

        'LightJet_up'                :  unfolding_files['file_for_lightjetup'],
        'LightJet_down'              :  unfolding_files['file_for_lightjetdown'],

        'TTJets_hadronisation'       :  unfolding_files['file_for_powheg_herwig'],

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

        'Top_Pt_reweight'            :  unfolding_files['file_for_ptreweight'],

    }

    h_truth, h_measured, h_response, h_fakes = None, None, None, None

    # Uncertainties by changing the response matrix
    if category in files_for_systematics :
        print 'Doing category',category,'by changing response matrix'
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( 
            inputfile = files_for_systematics[category],
            variable = variable,
            channel = channel,
            centre_of_mass = com,
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
            centre_of_mass = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
    elif additionalPDFSets and category in ct14_uncertainties :
        print 'Doing category',category,'by changing response matrix'
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( 
            inputfile = unfolding_files['files_for_ct14pdfs'][category],
            variable = variable,
            channel = channel,
            centre_of_mass = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
    elif additionalPDFSets and category in mmht14_uncertainties :
        print 'Doing category',category,'by changing response matrix'
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple( 
            inputfile = unfolding_files['files_for_mmht14pdfs'][category],
            variable = variable,
            channel = channel,
            centre_of_mass = com,
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
            centre_of_mass = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )

    # Unfold current normalisation measurements  
    TTJet_normalisation_results, TTJet_normalisation_results_unfolded, TTJet_normalisation_results_withoutFakes, covariance_matrix, inputMC_covariance_matrix = unfold_results( 
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
            inputfile = unfolding_files['file_for_massdown'],
            variable = variable,
            channel = channel,
            centre_of_mass = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_massup, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = unfolding_files['file_for_massup'],
            variable = variable,
            channel = channel,
            centre_of_mass = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_fsrdown, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = unfolding_files['file_for_fsrdown'],
            variable = variable,
            channel = channel,
            centre_of_mass = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_fsrup, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = unfolding_files['file_for_fsrup'],
            variable = variable,
            channel = channel,
            centre_of_mass = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_isrdown, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = unfolding_files['file_for_isrdown'],
            variable = variable,
            channel = channel,
            centre_of_mass = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_isrup, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = unfolding_files['file_for_isrup'],
            variable = variable,
            channel = channel,
            centre_of_mass = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_uedown, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = unfolding_files['file_for_uedown'],
            variable = variable,
            channel = channel,
            centre_of_mass = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_ueup, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = unfolding_files['file_for_ueup'],
            variable = variable,
            channel = channel,
            centre_of_mass = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )

        h_truth_powhegPythia8, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = unfolding_files['file_for_powhegPythia8'],
            variable = variable,
            channel = channel,
            centre_of_mass = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_amcatnlo, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = unfolding_files['file_for_amcatnlo'],
            variable = variable,
            channel = channel,
            centre_of_mass = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_madgraphMLM, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = unfolding_files['file_for_madgraphMLM'],
            variable = variable,
            channel = channel,
            centre_of_mass = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
        h_truth_powheg_herwig, _, _, _ = get_unfold_histogram_tuple( 
            inputfile = unfolding_files['file_for_powheg_herwig'],
            variable = variable,
            channel = channel,
            centre_of_mass = com,
            ttbar_xsection = ttbar_xsection,
            luminosity = luminosity,
            load_fakes = True,
            visiblePS = visiblePS,
        )
    
        normalisation_unfolded['powhegPythia8'] = hist_to_value_error_tuplelist( h_truth_powhegPythia8 )
        normalisation_unfolded['amcatnlo']      = hist_to_value_error_tuplelist( h_truth_amcatnlo )
        normalisation_unfolded['madgraphMLM']   = hist_to_value_error_tuplelist( h_truth_madgraphMLM )
        normalisation_unfolded['powhegHerwig']  = hist_to_value_error_tuplelist( h_truth_powheg_herwig )

        normalisation_unfolded['massdown']      = hist_to_value_error_tuplelist( h_truth_massdown )
        normalisation_unfolded['massup']        = hist_to_value_error_tuplelist( h_truth_massup )
        normalisation_unfolded['isrdown']       = hist_to_value_error_tuplelist( h_truth_isrdown )
        normalisation_unfolded['isrup']         = hist_to_value_error_tuplelist( h_truth_isrup )
        normalisation_unfolded['fsrdown']       = hist_to_value_error_tuplelist( h_truth_fsrdown )
        normalisation_unfolded['fsrup']         = hist_to_value_error_tuplelist( h_truth_fsrup )
        normalisation_unfolded['uedown']        = hist_to_value_error_tuplelist( h_truth_uedown )
        normalisation_unfolded['ueup']          = hist_to_value_error_tuplelist( h_truth_ueup )

    # Write all normalisations in unfolded binning scheme to dataframes
    file_template = '{path_to_DF}/{category}/unfolded_normalisation_{channel}_{method}.txt'
    channelForOutputFile = channel
    if channel == 'combined':
        channelForOutputFile = 'combinedBeforeUnfolding'
    write_02(normalisation_unfolded, file_template, path_to_DF, category, channelForOutputFile, method)
    return normalisation_unfolded, covariance_matrix, inputMC_covariance_matrix


def calculate_xsections( normalisation, category, channel, covariance_matrix=None, input_mc_covariance_matrix=None ):
    '''
    Calculate the xsection
    '''
    global variable, path_to_DF

    # calculate the x-sections
    branching_ratio = 1
    # if 'combined' in channel:
    #     branching_ratio = branching_ratio * 2

    binWidths = None
    if phase_space == 'VisiblePS':
        binWidths = bin_widths_visiblePS
    elif phase_space == 'FullPS':
        binWidths = bin_widths
    
    xsection_unfolded = {}
    xsection_unfolded['TTJet_measured'], _, _, _ = calculate_xsection( 
        normalisation['TTJet_measured'],
        binWidths[variable],
        luminosity,  # L in pb1
        branching_ratio 
    )  
    xsection_unfolded['TTJet_measured_withoutFakes'], _, _, _ = calculate_xsection( 
        normalisation['TTJet_measured_withoutFakes'],
        binWidths[variable],
        luminosity, 
        branching_ratio 
    ) 
    xsection_unfolded['TTJet_unfolded'], absolute_covariance_matrix, absolute_correlation_matrix, absolute_inputMC_covariance_matrix = calculate_xsection( 
        normalisation['TTJet_unfolded'],
        binWidths[variable],
        luminosity, 
        branching_ratio,
        covariance_matrix,
        input_mc_covariance_matrix, 
    )

    covariance_output_template = '{path_to_DF}/central/covarianceMatrices/absolute/{cat}_{label}_{channel}.txt'
    if not covariance_matrix is None:
        # Unfolded number of events
        table_outfile=covariance_output_template.format( path_to_DF=path_to_DF, channel = channel, label='Covariance', cat='Stat_absoluteXsection' )
        create_covariance_matrix( absolute_covariance_matrix, table_outfile)
        table_outfile=covariance_output_template.format( path_to_DF=path_to_DF, channel = channel, label='Correlation', cat='Stat_absoluteXsection' )
        create_covariance_matrix( absolute_correlation_matrix, table_outfile )
    if not input_mc_covariance_matrix is None:
        table_outfile=covariance_output_template.format( path_to_DF=path_to_DF, channel = channel, label='Covariance', cat='Stat_absoluteXsection_inputMC' )
        create_covariance_matrix( absolute_inputMC_covariance_matrix, table_outfile )
    if category == 'central':
        xsection_unfolded['powhegPythia8'], _, _, _ = calculate_xsection( 
            normalisation['powhegPythia8'],
            binWidths[variable],
            luminosity, 
            branching_ratio 
        )

        xsection_unfolded['amcatnlo'], _, _, _ = calculate_xsection( 
            normalisation['amcatnlo'],
            binWidths[variable],
            luminosity, 
            branching_ratio 
        )

        xsection_unfolded['powhegHerwig'], _, _, _ = calculate_xsection( 
            normalisation['powhegHerwig'],
            binWidths[variable],
            luminosity, 
            branching_ratio 
        )

        xsection_unfolded['madgraphMLM'], _, _, _ = calculate_xsection( 
            normalisation['madgraphMLM'],
            binWidths[variable],
            luminosity, 
            branching_ratio 
        )

        xsection_unfolded['massdown'], _, _, _ = calculate_xsection( 
            normalisation['massdown'],
            binWidths[variable],
            luminosity, 
            branching_ratio 
        )
        xsection_unfolded['massup'], _, _, _ = calculate_xsection( 
            normalisation['massup'],
            binWidths[variable],
            luminosity, 
            branching_ratio 
        )
        xsection_unfolded['isrdown'], _, _, _ = calculate_xsection( 
            normalisation['isrdown'],
            binWidths[variable],
            luminosity, 
            branching_ratio 
        )
        xsection_unfolded['isrup'], _, _, _ = calculate_xsection( 
            normalisation['isrup'],
            binWidths[variable],
            luminosity, 
            branching_ratio 
        )
        xsection_unfolded['fsrdown'], _, _, _ = calculate_xsection( 
            normalisation['fsrdown'],
            binWidths[variable],
            luminosity, 
            branching_ratio 
        )
        xsection_unfolded['fsrup'], _, _, _ = calculate_xsection( 
            normalisation['fsrup'],
            binWidths[variable],
            luminosity, 
            branching_ratio 
        )
        xsection_unfolded['uedown'], _, _, _ = calculate_xsection( 
            normalisation['uedown'],
            binWidths[variable],
            luminosity, 
            branching_ratio 
        )
        xsection_unfolded['ueup'], _, _, _ = calculate_xsection( 
            normalisation['ueup'],
            binWidths[variable],
            luminosity, 
            branching_ratio 
        )


    file_template = '{path_to_DF}/{category}/xsection_absolute_{channel}_{method}.txt'
    write_02(xsection_unfolded, file_template, path_to_DF, category, channel, method)
    return

def calculate_normalised_xsections( normalisation, category, channel, normalise_to_one = False, covariance_matrix=None, input_mc_covariance_matrix=None ):
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
    normalised_xsection['TTJet_measured'], _, _, _ = calculate_normalised_xsection( 
        normalisation['TTJet_measured'], 
        binWidths[variable], 
        normalise_to_one 
    )
    normalised_xsection['TTJet_measured_withoutFakes'], _, _, _ = calculate_normalised_xsection( 
        normalisation['TTJet_measured_withoutFakes'], 
        binWidths[variable], 
        normalise_to_one 
    )
    normalised_xsection['TTJet_unfolded'], normalised_covariance_matrix, normalised_correlation_matrix, normalised_inputMC_covariance_matrix = calculate_normalised_xsection( 
        normalisation['TTJet_unfolded'], 
        binWidths[variable], 
        normalise_to_one,
        covariance_matrix, 
        input_mc_covariance_matrix, 
    )
    
    covariance_output_template = '{path_to_DF}/central/covarianceMatrices/normalised/{cat}_{label}_{channel}.txt'
    if not covariance_matrix is None:
        # Unfolded number of events
        table_outfile=covariance_output_template.format( path_to_DF=path_to_DF, channel = channel, label='Covariance', cat='Stat_normalisedXsection' )
        create_covariance_matrix( normalised_covariance_matrix, table_outfile)
        table_outfile=covariance_output_template.format( path_to_DF=path_to_DF, channel = channel, label='Correlation', cat='Stat_normalisedXsection' )
        create_covariance_matrix( normalised_correlation_matrix, table_outfile )
    if not input_mc_covariance_matrix is None:
        table_outfile=covariance_output_template.format( path_to_DF=path_to_DF, channel = channel, label='Covariance', cat='Stat_normalisedXsection_inputMC' )
        create_covariance_matrix( normalised_inputMC_covariance_matrix, table_outfile )

    if category == 'central':
        normalised_xsection['powhegPythia8'], _, _, _ = calculate_normalised_xsection( 
            normalisation['powhegPythia8'], 
            binWidths[variable], 
            normalise_to_one, 
        )
        normalised_xsection['amcatnlo'], _, _, _ = calculate_normalised_xsection( 
            normalisation['amcatnlo'], 
            binWidths[variable], 
            normalise_to_one, 
        )
        normalised_xsection['powhegHerwig'], _, _, _ = calculate_normalised_xsection( 
            normalisation['powhegHerwig'], 
            binWidths[variable], 
            normalise_to_one, 
        )
        normalised_xsection['madgraphMLM'], _, _, _ = calculate_normalised_xsection( 
            normalisation['madgraphMLM'], 
            binWidths[variable], 
            normalise_to_one, 
        )

        normalised_xsection['massdown'], _, _, _ = calculate_normalised_xsection( 
            normalisation['massdown'], 
            binWidths[variable], 
            normalise_to_one, 
        )
        normalised_xsection['massup'], _, _, _ = calculate_normalised_xsection( 
            normalisation['massup'], 
            binWidths[variable], 
            normalise_to_one, 
        )
        normalised_xsection['isrdown'], _, _, _ = calculate_normalised_xsection( 
            normalisation['isrdown'], 
            binWidths[variable], 
            normalise_to_one, 
        )
        normalised_xsection['isrup'], _, _, _ = calculate_normalised_xsection( 
            normalisation['isrup'], 
            binWidths[variable], 
            normalise_to_one, 
        )
        normalised_xsection['fsrdown'], _, _, _ = calculate_normalised_xsection( 
            normalisation['fsrdown'], 
            binWidths[variable], 
            normalise_to_one, 
        )
        normalised_xsection['fsrup'], _, _, _ = calculate_normalised_xsection( 
            normalisation['fsrup'], 
            binWidths[variable], 
            normalise_to_one, 
        )
        normalised_xsection['uedown'], _, _, _ = calculate_normalised_xsection( 
            normalisation['uedown'], 
            binWidths[variable], 
            normalise_to_one, 
        )
        normalised_xsection['ueup'], _, _, _ = calculate_normalised_xsection( 
            normalisation['ueup'], 
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
    parser.add_argument( '-a', dest = "additionalPDFSets", action = "store_true",
                      help = "Add the CT14 and MMHT14 PDF sets" )
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
    additionalPDFSets           = args.additionalPDFSets

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
    path_to_DF = '{path}/{com}TeV/{variable}/{phase_space}/'.format( 
        path = args.path,
        com = com,
        variable = variable,
        phase_space = phase_space,
    )

    # Core Systematics
    all_measurements    = deepcopy( measurement_config.measurements )
    # Adding PDF Systematics
    pdf_uncertainties   = ['PDFWeights_%d' % index for index in range(measurement_config.pdfWeightMin, measurement_config.pdfWeightMax )]
    all_measurements.extend( pdf_uncertainties )
    if additionalPDFSets:
        ct14_uncertainties   = ['CT14Weights_%d' % index for index in range(measurement_config.pdfWeightMin, measurement_config.ct14WeightMax )]
        mmht14_uncertainties   = ['MMHT14Weights_%d' % index for index in range(measurement_config.pdfWeightMin, measurement_config.mmht14WeightMax )]
        all_measurements.extend( ct14_uncertainties )
        all_measurements.extend( mmht14_uncertainties )
    # # TTBar Reweighting Systematics
    # ttbar_theory_systematics = [ 'TTJets_ptreweight', 'TTJets_etareweight' ]
    # all_measurements.extend( ttbar_theory_systematics )

    print 'Performing unfolding for variable', variable
    for category in all_measurements:
        if run_just_central and not category == 'central': 
            continue
        if ( variable in measurement_config.variables_no_met ) and (category in measurement_config.met_specific_systematics):
            continue
        print 'Unfolding category {}'.format(category)

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
        elif category == 'Electron_up' or category == 'Electron_down':
            normalisation_results_electron  = read_tuple_from_file( electron_file )
            normalisation_results_muon      = read_tuple_from_file( path_to_DF + '/central/normalisation_muon.txt' )
        else:
            normalisation_results_electron  = read_tuple_from_file( electron_file )
            normalisation_results_muon      = read_tuple_from_file( muon_file )

        # Combine the normalisations (beforeUnfolding)
        normalisation_results_combined = combine_complex_df(normalisation_results_electron, normalisation_results_muon)
        TTJet_normalisation_results_electron = normalisation_results_electron['TTJet']
        TTJet_normalisation_results_muon = normalisation_results_muon['TTJet']
        TTJet_normalisation_results_combined = normalisation_results_combined['TTJet']

        # # get unfolded normalisations and xsections
        unfolded_normalisation_electron                 = {}
        unfolded_normalisation_muon                     = {}
        unfolded_normalisation_combined                 = {}
        unfolded_normalisation_combinedBeforeUnfolding  = {}

        # Electron channel
        channel = 'electron'
        unfolded_normalisation_electron, covariance_electron, inputMC_covariance_electron = get_unfolded_normalisation( 
            TTJet_normalisation_results_electron, 
            category, 
            channel, 
            tau_value_electron, 
            visiblePS = visiblePS 
        )

        # measure xsection
        calculate_xsections( unfolded_normalisation_electron, category, channel, covariance_matrix=covariance_electron, input_mc_covariance_matrix = inputMC_covariance_electron  )
        calculate_normalised_xsections( unfolded_normalisation_electron, category, channel, covariance_matrix=covariance_electron, input_mc_covariance_matrix = inputMC_covariance_electron )
        calculate_normalised_xsections( unfolded_normalisation_electron, category, channel , True )

        # Muon channel
        channel = 'muon'
        unfolded_normalisation_muon, covariance_muon, inputMC_covariance_muon = get_unfolded_normalisation( 
            TTJet_normalisation_results_muon, 
            category, 
            channel, 
            tau_value_muon, 
            visiblePS = visiblePS 
        )
        # measure xsection
        calculate_xsections( unfolded_normalisation_muon, category, channel, covariance_matrix=covariance_muon, input_mc_covariance_matrix = inputMC_covariance_muon  )
        calculate_normalised_xsections( unfolded_normalisation_muon, category, channel, covariance_matrix=covariance_muon, input_mc_covariance_matrix = inputMC_covariance_muon )
        calculate_normalised_xsections( unfolded_normalisation_muon, category, channel , True )

        # Results where the channels are combined before unfolding (the 'combined in the response matrix')
        channel = 'combinedBeforeUnfolding'
        unfolded_normalisation_combinedBeforeUnfolding, covariance_combinedBeforeUnfolding, inputMC_covariance_combinedBeforeUnfolding = get_unfolded_normalisation(
            TTJet_normalisation_results_combined,
            category,
            'combined', 
            tau_value=tau_value_combined,
            visiblePS=visiblePS,
        )
        # measure xsection
        calculate_xsections( unfolded_normalisation_combinedBeforeUnfolding, category, channel, covariance_matrix=covariance_combinedBeforeUnfolding, input_mc_covariance_matrix = inputMC_covariance_combinedBeforeUnfolding  )
        calculate_normalised_xsections( unfolded_normalisation_combinedBeforeUnfolding, category, channel, covariance_matrix=covariance_combinedBeforeUnfolding, input_mc_covariance_matrix = inputMC_covariance_combinedBeforeUnfolding )
        calculate_normalised_xsections( unfolded_normalisation_combinedBeforeUnfolding, category, channel , True )

        # Results where the channels are combined after unfolding
        channel = 'combined'
        unfolded_normalisation_combined = combine_complex_results( unfolded_normalisation_electron, unfolded_normalisation_muon )
        covariance_combined = None
        inputMC_covariance_combined = None
        if not covariance_electron is None and not covariance_muon is None:
            covariance_combined = covariance_electron + covariance_muon
        if not inputMC_covariance_electron is None and not inputMC_covariance_muon is None:
            inputMC_covariance_combined = inputMC_covariance_electron + inputMC_covariance_muon
        # measure xsection
        calculate_xsections( unfolded_normalisation_combined, category, channel, covariance_matrix=covariance_combined, input_mc_covariance_matrix = inputMC_covariance_combined  )
        calculate_normalised_xsections( unfolded_normalisation_combined, category, channel, covariance_matrix=covariance_combined, input_mc_covariance_matrix = inputMC_covariance_combined )
        calculate_normalised_xsections( unfolded_normalisation_combined, category, channel , True )



