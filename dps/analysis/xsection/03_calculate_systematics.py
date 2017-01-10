
'''
Created on 10 April 2013

@author: kreczko

This module produces several results for the three channels (electron, muon, combined):
1) central measurement with error =  sqrt([combined systematic uncertainties]^2 + [unfolding]^2)
2) all systematics evaluated with respect to central: up & down shifts, MET summary, PDF summary, Total up & down
3) additional result for MET systematics
4) additional result for PDF systematics
5) additional result for TTJet theory systematic (so we can compare to them!)

1) + existing result can be used for the final plots
2) can be used to compare systematics (both in tables and plots)
3) + 4) for more fine-grained analysis
'''
from argparse import ArgumentParser
from dps.config.xsection import XSectionConfig
from dps.config.variable_binning import bin_edges_vis
from dps.utils.systematic import append_PDF_uncertainties, print_dictionary,\
    get_normalised_cross_sections, get_symmetrised_systematic_uncertainty,\
    generate_covariance_matrices,\
    get_measurement_with_total_systematic_uncertainty,\
    write_normalised_xsection_measurement,\
    write_systematic_xsection_measurement

def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument( "-p", "--path", 
        dest = "path", 
        default = 'data/normalisation/background_subtraction/',
        help = "set path to JSON files" )
    parser.add_argument( "-v", "--variable", 
        dest = "variable", 
        default = 'MET',
        help = "set variable to plot (MET, HT, ST, MT)" )
    parser.add_argument( "-c", "--centre-of-mass-energy", 
        dest = "CoM", 
        default = 13, type = int,
        help = "set the centre of mass energy for analysis. Default = 13 [TeV]" )
    parser.add_argument( "-s", "--symmetrise_errors", 
        action = "store_true", 
        dest = "symmetrise_errors",
        help = "Makes the errors symmetric" )
    parser.add_argument( '--visiblePS', 
        dest = "visiblePS", 
        action = "store_true",
        help = "Unfold to visible phase space" )
    parser.add_argument( "-u", "--unfolding_method", 
        dest = "unfolding_method", 
        default = 'TUnfold',
        help = "Unfolding method:  TUnfold (default)" )
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    '''
    1) read all background subtraction results (group by MET, PDF, other)
    2) calculate the difference to central measurement
    3) 
    '''
    args = parse_arguments()
    measurement_config = XSectionConfig( args.CoM )
    # caching of variables for shorter access
    method                      = args.unfolding_method
    symmetrise_errors           = args.symmetrise_errors
    variable                    = args.variable
    visiblePS                   = args.visiblePS
    met_specific_systematics    = measurement_config.met_specific_systematics
    variables_no_met            = measurement_config.variables_no_met
    topMasses                   = measurement_config.topMasses
    topMassUncertainty          = measurement_config.topMassUncertainty

    phase_space = 'VisiblePS'
    if not visiblePS:
        phase_space = 'FullPS'

    path_to_DF = '{path}/{com}TeV/{variable}/{phase_space}'
    path_to_DF = path_to_DF.format(
        path = args.path, 
        com = args.CoM,
        variable = variable,
        phase_space = phase_space,
    )

    number_of_bins=len(bin_edges_vis[variable])-1

    # List of args to pass to systematic functions
    args={
        'met_specific_systematics' : met_specific_systematics,
        'variables_no_met' : variables_no_met,
        'symmetrise_errors' : symmetrise_errors,
        'path_to_DF' : path_to_DF,
        'method' : method,
        'variable' : variable,
        'number_of_bins' : number_of_bins,
        'topMasses' : topMasses,
        'topMassUncertainty' : topMassUncertainty,
        'phase_space' : phase_space
    }

    # Get list of all systematics
    all_systematics = measurement_config.list_of_systematics
    # Add in the PDF weights
    all_systematics = append_PDF_uncertainties(all_systematics, measurement_config.pdfWeightMin, measurement_config.pdfWeightMax)

    list_of_systematics = all_systematics
    # If you want different lists of systematics can just do some manipulation here

    print(list_of_systematics)

    channel = [
        'electron', 
        'muon', 
        'combined', 
        # 'combinedBeforeUnfolding',
    ]
    for ch in channel:
        print("Calculating {0} channel systematic uncertainties : ".format(ch))

        # Add channel specific args to list of args
        args['channel'] = ch

        # Retreive the normalised cross sections, for all groups in list_of_systematics.
        systematic_normalised_uncertainty, unfolded_systematic_normalised_uncertainty = get_normalised_cross_sections(
            args, 
            list_of_systematics
        )
        # print_dictionary("Normalised cross sections of the systematics in use", systematic_normalised_uncertainty)
        # print_dictionary("Unfolded normalised cross sections of the systematics in use", unfolded_systematic_normalised_uncertainty)

        # Get and symmetrise the uncertainties
        x_sec_with_symmetrised_systematics = get_symmetrised_systematic_uncertainty(
            args, 
            systematic_normalised_uncertainty, 
        )
        unfolded_x_sec_with_symmetrised_systematics = get_symmetrised_systematic_uncertainty(
            args, 
            unfolded_systematic_normalised_uncertainty 
        )
        # print_dictionary("Normalised cross sections of the systematics with symmetrised uncertainties", x_sec_with_symmetrised_systematics)
        # print_dictionary("Unfolded normalised cross sections of the systematics  with symmetrised uncertainties", unfolded_x_sec_with_symmetrised_systematics)

        # Create covariance matrices
        generate_covariance_matrices(
            args, 
            x_sec_with_symmetrised_systematics
        )
        generate_covariance_matrices(
            args, 
            unfolded_x_sec_with_symmetrised_systematics
        )

        # Combine all systematic uncertainties for each of the groups of systematics
        # Currently returns (Value, SysUp, SysDown) - Need to include stat?
        full_measurement = get_measurement_with_total_systematic_uncertainty(
            args, 
            x_sec_with_symmetrised_systematics
        )
        full_unfolded_measurement = get_measurement_with_total_systematic_uncertainty(
            args, 
            unfolded_x_sec_with_symmetrised_systematics
        )
        # print_dictionary("Measurement with total systematic error for each systematic group", full_measurement)
        # print_dictionary("Unfolded measurement with total systematic error for each systematic group", full_unfolded_measurement)

        # Write central +- error to JSON. Group of systematics in question is included in outputfile name.
        # Summary if you want to specify specific list. e.g. GeneratorOnly etc
        write_normalised_xsection_measurement(
            args, 
            full_measurement, 
            full_unfolded_measurement, 
            summary = '' 
        )
        write_systematic_xsection_measurement(
            args, 
            unfolded_x_sec_with_symmetrised_systematics, 
            full_unfolded_measurement, 
            summary = '' 
        )

