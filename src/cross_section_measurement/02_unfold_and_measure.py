# general
from __future__ import division
from optparse import OptionParser
import os
# from array import array
# rootpy
from rootpy import asrootpy
from rootpy.io import File
from rootpy.plotting import Hist2D
# DailyPythonScripts
from tools.Calculation import calculate_xsection, calculate_normalised_xsection, combine_complex_results
from tools.hist_utilities import hist_to_value_error_tuplelist, value_error_tuplelist_to_hist
from tools.Unfolding import Unfolding, get_unfold_histogram_tuple
from tools.file_utilities import read_data_from_JSON, write_data_to_JSON, make_folder_if_not_exists
from config.cross_section_measurement_common import translate_options
import config.RooUnfold as unfoldCfg
from copy import deepcopy

def unfold_results(results, category, channel, h_truth, h_measured, h_response, h_fakes, method):
    global variable, path_to_JSON
    h_data = value_error_tuplelist_to_hist(results, bin_edges[variable])
    unfolding = Unfolding(h_truth, h_measured, h_response, h_fakes, method=method, k_value=unfoldCfg.SVD_k_value)
    
    # turning off the unfolding errors for systematic samples
    if not category == 'central':
        unfoldCfg.Hreco = 0
    else:
        unfoldCfg.Hreco = options.Hreco
        
    h_unfolded_data = unfolding.unfold(h_data)
    
    # export the D and SV distributions
    SVD_path = path_to_JSON + '/unfolding_objects/' + channel + '/kv_' + str(unfoldCfg.SVD_k_value) + '/'
    make_folder_if_not_exists(SVD_path)
    if method == 'TSVDUnfold':
        SVDdist = File(SVD_path + method + '_SVDdistributions_' + category + '.root', 'recreate')
        directory = SVDdist.mkdir('SVDdist')
        directory.cd()
        unfolding.unfoldObject.GetD().Write()
        unfolding.unfoldObject.GetSV().Write()
        #    unfolding.unfoldObject.GetUnfoldCovMatrix(data_covariance_matrix(h_data), unfoldCfg.SVD_n_toy).Write()
        SVDdist.Close()
    else:
        SVDdist = File(SVD_path + method + '_SVDdistributions_Hreco' + str(unfoldCfg.Hreco) + '_' + category + '.root', 'recreate')
        directory = SVDdist.mkdir('SVDdist')
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
        unfolding_object_file_name = SVD_path + method + '_unfoldingObject_Hreco' + str(unfoldCfg.Hreco) + '_' + category + '.root'
    if not os.path.isfile(unfolding_object_file_name):
        unfoldingObjectFile = File(unfolding_object_file_name, 'recreate')
        directory = unfoldingObjectFile.mkdir('unfoldingObject')
        directory.cd()
        if method == 'TSVDUnfold':
            unfolding.unfoldObject.Write()
        else:
            unfolding.unfoldObject.Impl().Write()
        unfoldingObjectFile.Close()
    
    del unfolding
    return hist_to_value_error_tuplelist(h_unfolded_data)

def data_covariance_matrix(data):
    values = list(data)
    get_bin_error = data.GetBinError
    cov_matrix = Hist2D(len(values), -10, 10, len(values), -10, 10, type='D')
    for bin_i in range(len(values)):
        error = get_bin_error(bin_i + 1)
        cov_matrix.SetBinContent(bin_i + 1, bin_i + 1, error * error)
    return cov_matrix

def get_unfolded_normalisation(TTJet_fit_results, category, channel):
    global variable, met_type, path_to_JSON, file_for_unfolding, file_for_powheg, file_for_mcatnlo 
    global centre_of_mass, luminosity, ttbar_xsection, load_fakes, method
    global file_for_matchingdown, file_for_matchingup, file_for_scaledown, file_for_scaleup
    global ttbar_generator_systematics

    files_for_systematics = {
                             ttbar_theory_systematic_prefix + 'matchingdown':file_for_matchingdown,
                             ttbar_theory_systematic_prefix + 'matchingup':file_for_matchingup,
                             ttbar_theory_systematic_prefix + 'scaledown':file_for_scaledown,
                             ttbar_theory_systematic_prefix + 'scaleup':file_for_scaleup,
                             }
    
    h_truth, h_measured, h_response, h_fakes = None, None, None, None
    if category in ttbar_generator_systematics and not 'ptreweight' in category:
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple(inputfile = files_for_systematics[category],
                                                                              variable = variable,
                                                                              channel = channel,
                                                                              met_type = met_type,
                                                                              centre_of_mass = centre_of_mass,
                                                                              ttbar_xsection = ttbar_xsection,
                                                                              luminosity = luminosity,
                                                                              load_fakes = load_fakes
                                                                              )

    elif 'mcatnlo_matrix' in category:
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple(inputfile = file_for_mcatnlo,
                                                                              variable = variable,
                                                                              channel = channel,
                                                                              met_type = met_type,
                                                                              centre_of_mass = centre_of_mass,
                                                                              ttbar_xsection = ttbar_xsection,
                                                                              luminosity = luminosity,
                                                                              load_fakes = load_fakes
                                                                              )
    else:
        h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple(inputfile = file_for_unfolding,
                                                                              variable = variable,
                                                                              channel = channel,
                                                                              met_type = met_type,
                                                                              centre_of_mass = centre_of_mass,
                                                                              ttbar_xsection = ttbar_xsection,
                                                                              luminosity = luminosity,
                                                                              load_fakes = load_fakes
                                                                              )

    h_truth_POWHEG, _, _, _ = get_unfold_histogram_tuple(inputfile = file_for_powheg,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes
                                                )
    h_truth_MCATNLO, _, _, _ = get_unfold_histogram_tuple(inputfile = file_for_mcatnlo,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes
                                                )
    h_truth_matchingdown, _, _, _ = get_unfold_histogram_tuple(inputfile = file_for_matchingdown,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes
                                                )
    h_truth_matchingup, _, _, _ = get_unfold_histogram_tuple(inputfile = file_for_matchingup,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes
                                                )
    h_truth_scaledown, _, _, _ = get_unfold_histogram_tuple(inputfile = file_for_scaledown,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes
                                                )
    h_truth_scaleup, _, _, _ = get_unfold_histogram_tuple(inputfile = file_for_scaleup,
                                                variable = variable,
                                                channel = channel,
                                                met_type = met_type,
                                                centre_of_mass = centre_of_mass,
                                                ttbar_xsection = ttbar_xsection,
                                                luminosity = luminosity,
                                                load_fakes = load_fakes
                                                )

    MADGRAPH_results = hist_to_value_error_tuplelist(h_truth)
    POWHEG_results = hist_to_value_error_tuplelist(h_truth_POWHEG)
    MCATNLO_results = hist_to_value_error_tuplelist(h_truth_MCATNLO)
    
    matchingdown_results = hist_to_value_error_tuplelist(h_truth_matchingdown)
    matchingup_results = hist_to_value_error_tuplelist(h_truth_matchingup)
    scaledown_results = hist_to_value_error_tuplelist(h_truth_scaledown)
    scaleup_results = hist_to_value_error_tuplelist(h_truth_scaleup)

    TTJet_fit_results_unfolded = unfold_results(TTJet_fit_results,
                                                category,
                                                channel,
                                                h_truth,
                                                h_measured,
                                                h_response,
                                                h_fakes,
                                                method
                                                )
        
    normalisation_unfolded = {
                              'TTJet_measured' : TTJet_fit_results,
                              'TTJet_unfolded' : TTJet_fit_results_unfolded,
                              'MADGRAPH': MADGRAPH_results,
                              # other generators
                              'POWHEG': POWHEG_results,
                              'MCATNLO': MCATNLO_results,
                              # systematics
                              'matchingdown': matchingdown_results,
                              'matchingup': matchingup_results,
                              'scaledown': scaledown_results,
                              'scaleup': scaleup_results
                              }
    
    return normalisation_unfolded
    
def calculate_xsections(normalisation, category, channel):
    global variable, met_type, path_to_JSON
    # calculate the x-sections
    branching_ratio = 0.15
    if channel == 'combined':
        branching_ratio = branching_ratio * 2
    TTJet_xsection = calculate_xsection(normalisation['TTJet_measured'], luminosity, branching_ratio)  # L in pb1
    TTJet_xsection_unfolded = calculate_xsection(normalisation['TTJet_unfolded'], luminosity, branching_ratio)  # L in pb1
    MADGRAPH_xsection = calculate_xsection(normalisation['MADGRAPH'], luminosity, branching_ratio)  # L in pb1
    POWHEG_xsection = calculate_xsection(normalisation['POWHEG'], luminosity, branching_ratio)  # L in pb1
    MCATNLO_xsection = calculate_xsection(normalisation['MCATNLO'], luminosity, branching_ratio)  # L in pb1
    matchingdown_xsection = calculate_xsection(normalisation['matchingdown'], luminosity, branching_ratio)  # L in pb1
    matchingup_xsection = calculate_xsection(normalisation['matchingup'], luminosity, branching_ratio)  # L in pb1
    scaledown_xsection = calculate_xsection(normalisation['scaledown'], luminosity, branching_ratio)  # L in pb1
    scaleup_xsection = calculate_xsection(normalisation['scaleup'], luminosity, branching_ratio)  # L in pb1
    
    xsection_unfolded = {'TTJet_measured' : TTJet_xsection,
                         'TTJet_unfolded' : TTJet_xsection_unfolded,
                         'MADGRAPH': MADGRAPH_xsection,
                         'POWHEG': POWHEG_xsection,
                         'MCATNLO': MCATNLO_xsection,
                         # systematics
                         'matchingdown': matchingdown_xsection,
                         'matchingup': matchingup_xsection,
                         'scaledown': scaledown_xsection,
                         'scaleup': scaleup_xsection
                         }
    write_data_to_JSON(xsection_unfolded, path_to_JSON + '/xsection_measurement_results' + '/kv' + str(unfoldCfg.SVD_k_value) + '/' + category + '/xsection_' + channel + '_' + met_type + '.txt')
    
def calculate_normalised_xsections(normalisation, category, channel, normalise_to_one=False):
    global variable, met_type, path_to_JSON
    TTJet_normalised_xsection = calculate_normalised_xsection(normalisation['TTJet_measured'], bin_widths[variable], normalise_to_one)
    TTJet_normalised_xsection_unfolded = calculate_normalised_xsection(normalisation['TTJet_unfolded'], bin_widths[variable], normalise_to_one)
    MADGRAPH_normalised_xsection = calculate_normalised_xsection(normalisation['MADGRAPH'], bin_widths[variable], normalise_to_one)
    POWHEG_normalised_xsection = calculate_normalised_xsection(normalisation['POWHEG'], bin_widths[variable], normalise_to_one)
    MCATNLO_normalised_xsection = calculate_normalised_xsection(normalisation['MCATNLO'], bin_widths[variable], normalise_to_one)
    matchingdown_normalised_xsection = calculate_normalised_xsection(normalisation['matchingdown'], bin_widths[variable], normalise_to_one)
    matchingup_normalised_xsection = calculate_normalised_xsection(normalisation['matchingup'], bin_widths[variable], normalise_to_one)
    scaledown_normalised_xsection = calculate_normalised_xsection(normalisation['scaledown'], bin_widths[variable], normalise_to_one)
    scaleup_normalised_xsection = calculate_normalised_xsection(normalisation['scaleup'], bin_widths[variable], normalise_to_one)
    
    normalised_xsection = {'TTJet_measured' : TTJet_normalised_xsection,
                           'TTJet_unfolded' : TTJet_normalised_xsection_unfolded,
                           'MADGRAPH': MADGRAPH_normalised_xsection,
                           'POWHEG': POWHEG_normalised_xsection,
                           'MCATNLO': MCATNLO_normalised_xsection,
                           # systematics
                           'matchingdown': matchingdown_normalised_xsection,
                           'matchingup': matchingup_normalised_xsection,
                           'scaledown': scaledown_normalised_xsection,
                           'scaleup': scaleup_normalised_xsection
                           }
    
    filename = path_to_JSON + '/xsection_measurement_results' + '/kv' + str(unfoldCfg.SVD_k_value) + '/' + category + '/normalised_xsection_' + channel + '_' + met_type + '.txt'
    if normalise_to_one:
        filename = filename.replace('normalised_xsection', 'normalised_to_one_xsection')
    write_data_to_JSON(normalised_xsection, filename)

if __name__ == '__main__':
    from ROOT import gROOT
    gROOT.SetBatch( True )
    gROOT.ProcessLine( 'gErrorIgnoreLevel = 3001;' )
    # setup
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data/',
                  help="set path to JSON files")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                      help="set the variable to analyse (MET, HT, ST, MT)")
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                      help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type for analysis of MET, ST or MT")
    parser.add_option("-k", "--k_value", type='int',
                      dest="k_value", default=4,
                      help="k-value for SVD unfolding")
    parser.add_option("-f", "--load_fakes", dest="load_fakes", action="store_true",
                      help="Load fakes histogram and perform manual fake subtraction in TSVDUnfold")
    parser.add_option("-u", "--unfolding_method", dest="unfolding_method", default = 'RooUnfoldSvd',
                      help="Unfolding method: RooUnfoldSvd (default), TSVDUnfold, TopSVDUnfold, RooUnfoldTUnfold, RooUnfoldInvert, RooUnfoldBinByBin, RooUnfoldBayes")
    parser.add_option("-H", "--hreco", type='int',
                      dest="Hreco", default=2,
                      help="Hreco parameter for error treatment in RooUnfold")
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=8,
                      help="set the centre of mass energy for analysis. Default = 8 [TeV]", type=int)
    
    
    (options, args) = parser.parse_args()
    from config.cross_section_measurement_common import met_systematics_suffixes, translate_options, ttbar_theory_systematic_prefix, vjets_theory_systematic_prefix
    
    if options.CoM == 8:
        from config.variable_binning_8TeV import bin_widths, bin_edges
        import config.cross_section_measurement_8TeV as measurement_config
    elif options.CoM == 7:
        from config.variable_binning_7TeV import bin_widths, bin_edges
        import config.cross_section_measurement_7TeV as measurement_config
    else:
        import sys
        sys.exit('Unknown centre of mass energy')
    
    centre_of_mass = options.CoM
    luminosity = measurement_config.luminosity * measurement_config.luminosity_scale
    ttbar_xsection = measurement_config.ttbar_xsection
    path_to_files = measurement_config.path_to_files
    
    file_for_unfolding = File(measurement_config.unfolding_madgraph_file, 'read')
    file_for_powheg = File(measurement_config.unfolding_powheg, 'read')
    file_for_mcatnlo = File(measurement_config.unfolding_mcatnlo, 'read')
        
    file_for_scaledown = File(measurement_config.unfolding_scale_down, 'read')
    file_for_scaleup = File(measurement_config.unfolding_scale_up, 'read')
    file_for_matchingdown = File(measurement_config.unfolding_matching_down, 'read')
    file_for_matchingup = File(measurement_config.unfolding_matching_up, 'read')
    variable = options.variable
    unfoldCfg.SVD_k_value = options.k_value
    load_fakes = options.load_fakes
    unfoldCfg.Hreco = options.Hreco
    method = options.unfolding_method
    met_type = translate_options[options.metType]
    b_tag_bin = translate_options[options.bjetbin]
    path_to_JSON = options.path + '/' + str(measurement_config.centre_of_mass) + 'TeV/' + variable + '/'
    
    categories = deepcopy(measurement_config.categories_and_prefixes.keys())
    ttbar_generator_systematics = [ttbar_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    ttbar_generator_systematics.append(ttbar_theory_systematic_prefix + 'ptreweight')
    vjets_generator_systematics = [vjets_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
    categories.extend(ttbar_generator_systematics)
    categories.extend(vjets_generator_systematics)
    
    pdf_uncertainties = ['PDFWeights_%d' % index for index in range(1, 45)]
    # all MET uncertainties except JES as this is already included
    met_uncertainties = [met_type + suffix for suffix in met_systematics_suffixes if not 'JetEn' in suffix and not 'JetRes' in suffix]
    all_measurements = deepcopy(categories)
    all_measurements.extend(pdf_uncertainties)
    all_measurements.extend(met_uncertainties)
    all_measurements.extend(['QCD_shape', ttbar_theory_systematic_prefix + 'mcatnlo', ttbar_theory_systematic_prefix + 'mcatnlo_matrix'])
    
    for category in all_measurements:
        if variable == 'HT' and category in met_uncertainties:
            continue
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
        
        # read fit results from JSON
        electron_file = path_to_JSON + '/fit_results/' + category + '/fit_results_electron_' + met_type + '.txt'
        muon_file = path_to_JSON + '/fit_results/' + category + '/fit_results_muon_' + met_type + '.txt'
        if category == ttbar_theory_systematic_prefix + 'mcatnlo_matrix':
            electron_file = path_to_JSON + '/fit_results/' + ttbar_theory_systematic_prefix + 'mcatnlo' + '/fit_results_electron_' + met_type + '.txt'
            muon_file = path_to_JSON + '/fit_results/' + ttbar_theory_systematic_prefix + 'mcatnlo' + '/fit_results_muon_' + met_type + '.txt'
        
        fit_results_electron = read_data_from_JSON(electron_file)
        fit_results_muon = read_data_from_JSON(muon_file)
        TTJet_fit_results_electron = fit_results_electron['TTJet']
        TTJet_fit_results_muon = fit_results_muon['TTJet']
        Higgs_fit_results_electron = fit_results_electron['Higgs']
        Higgs_fit_results_muon = fit_results_muon['Higgs']
        
        # change back to original MET type for the unfolding
        met_type = translate_options[options.metType]
        # ad-hoc switch for PFMET -> patMETsPFlow
        if met_type == 'PFMET':
            met_type = 'patMETsPFlow'
        
        # get unfolded normalisation
        unfolded_normalisation_electron = get_unfolded_normalisation(TTJet_fit_results_electron, category, 'electron')
        unfolded_normalisation_muon = get_unfolded_normalisation(TTJet_fit_results_muon, category, 'muon')
        
        unfolded_normalisation_combined = combine_complex_results(unfolded_normalisation_electron, unfolded_normalisation_muon)
        write_data_to_JSON(unfolded_normalisation_electron,
                           path_to_JSON + '/xsection_measurement_results' + '/kv' + str(unfoldCfg.SVD_k_value) + '/' + category + '/normalisation_electron_' + met_type + '.txt')
        write_data_to_JSON(unfolded_normalisation_muon,
                           path_to_JSON + '/xsection_measurement_results' + '/kv' + str(unfoldCfg.SVD_k_value) + '/' + category + '/normalisation_muon_' + met_type + '.txt')
        write_data_to_JSON(unfolded_normalisation_combined,
                           path_to_JSON + '/xsection_measurement_results' + '/kv' + str(unfoldCfg.SVD_k_value) + '/' + category + '/normalisation_combined_' + met_type + '.txt')
        
        # now the same for the Higgs
        unfolded_normalisation_electron_higgs = get_unfolded_normalisation(Higgs_fit_results_electron, category, 'electron')
        unfolded_normalisation_muon_higgs = get_unfolded_normalisation(Higgs_fit_results_muon, category, 'muon')
        
        unfolded_normalisation_combined_higgs = combine_complex_results(unfolded_normalisation_electron_higgs, unfolded_normalisation_muon_higgs)
        write_data_to_JSON(unfolded_normalisation_electron_higgs,
                           path_to_JSON + '/xsection_measurement_results' + '/kv' + str(unfoldCfg.SVD_k_value) + '/' + category + '/normalisation_electron_' + met_type + '_Higgs.txt')
        write_data_to_JSON(unfolded_normalisation_muon_higgs,
                           path_to_JSON + '/xsection_measurement_results' + '/kv' + str(unfoldCfg.SVD_k_value) + '/' + category + '/normalisation_muon_' + met_type + '_Higgs.txt')
        write_data_to_JSON(unfolded_normalisation_combined_higgs,
                           path_to_JSON + '/xsection_measurement_results' + '/kv' + str(unfoldCfg.SVD_k_value) + '/' + category + '/normalisation_combined_' + met_type + '_Higgs.txt')
        # measure xsection
        calculate_xsections(unfolded_normalisation_electron, category, 'electron')
        calculate_xsections(unfolded_normalisation_muon, category, 'muon')
        calculate_xsections(unfolded_normalisation_combined, category, 'combined')
        
        calculate_normalised_xsections(unfolded_normalisation_electron, category, 'electron')
        calculate_normalised_xsections(unfolded_normalisation_muon, category, 'muon')
        calculate_normalised_xsections(unfolded_normalisation_combined, category, 'combined')
        
        normalise_to_one = True
        calculate_normalised_xsections(unfolded_normalisation_electron, category, 'electron', normalise_to_one)
        calculate_normalised_xsections(unfolded_normalisation_muon, category, 'muon', normalise_to_one)
        calculate_normalised_xsections(unfolded_normalisation_combined, category, 'combined', normalise_to_one)
