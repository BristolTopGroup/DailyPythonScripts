
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
from optparse import OptionParser
from config import XSectionConfig
from config.variable_binning import bin_edges_vis
from tools.systematic import *

if __name__ == '__main__':
    '''
    1) read all background subtraction results (group by MET, PDF, other)
    2) calculate the difference to central measurement
    3) 
    '''
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data/M3_angle_bl/',
                  help = "set path to JSON files" )
    parser.add_option( "-v", "--variable", dest = "variable", default = 'MET',
                  help = "set variable to plot (MET, HT, ST, MT)" )
    parser.add_option( "-m", "--metType", dest = "metType", default = 'type1',
                      help = "set MET type used in the analysis of MET, ST or MT" )
    parser.add_option( "-b", "--bjetbin", dest = "bjetbin", default = '2m',
                  help = "set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m" )
    parser.add_option( "-c", "--centre-of-mass-energy", dest = "CoM", default = 13, type = int,
                      help = "set the centre of mass energy for analysis. Default = 13 [TeV]" )
    parser.add_option( "-s", "--symmetrise_errors", action = "store_true", dest = "symmetrise_errors",
                      help = "Makes the errors symmetric" )
    parser.add_option( '--visiblePS', dest = "visiblePS", action = "store_true",
                      help = "Unfold to visible phase space" )
    parser.add_option( "-u", "--unfolding_method", dest = "unfolding_method", default = 'TUnfold',
                      help = "Unfolding method:  TUnfold (default)" )

    ( options, args ) = parser.parse_args()
    measurement_config = XSectionConfig( options.CoM )
    # caching of variables for shorter access
    translate_options = measurement_config.translate_options
    met_specific_systematics = measurement_config.met_specific_systematics
    met_type = translate_options[options.metType]
    variables_no_met = measurement_config.variables_no_met
    method = options.unfolding_method
    symmetrise_errors = options.symmetrise_errors
    variable = options.variable
    visiblePS = options.visiblePS
    phase_space = 'VisiblePS'
    if not visiblePS:
        phase_space = 'FullPS'

    path_to_JSON = '{path}/{com}TeV/{variable}/{phase_space}'
    path_to_JSON = path_to_JSON.format(
        path = options.path, 
        com = options.CoM,
        variable = variable,
        phase_space = phase_space,
        )
    number_of_bins=len(bin_edges_vis[variable])-1
    print("Number of bins in {var} is {bin}".format(var=variable, bin=number_of_bins))

    # List of options to pass to systematic functions
    opts={
    'met_specific_systematics' : met_specific_systematics,
    'met_type' : met_type,
    'variables_no_met' : variables_no_met,
    'symmetrise_errors' : symmetrise_errors,
    'path_to_JSON' : path_to_JSON,
    'method' : method,
    'variable' : variable,
    'number_of_bins' : number_of_bins,
    }

    # Get list of all systematics
    all_systematics = measurement_config.list_of_systematics
    all_systematics = append_PDF_uncertainties(all_systematics)

    print(all_systematics)

    list_of_systematics = {}
    list_of_systematics['all'] = all_systematics
    # Get separated lists of systematics e.g. only hadronisation etc...
    # TODO

    # Print the systematics if required
    # TODO

    for channel in ['combinedBeforeUnfolding']:

    # for channel in ['electron', 'muon', 'combined', 'combinedBeforeUnfolding']:
        print("New Channel ___ ", channel)
        # Add channel to list of options
        opts['channel'] = channel

        # print(list_of_systematics)
        systematic_normalised_uncertainty, unfolded_systematic_normalised_uncertainty = \
            get_normalised_cross_sections(opts, list_of_systematics)



        unfolded_x_sec_with_symmetrised_systematics = get_symmetrised_systematic_uncertainty(unfolded_systematic_normalised_uncertainty)
        # Some systematics are identical before unfolding.
        x_sec_with_symmetrised_systematics = get_symmetrised_systematic_uncertainty(systematic_normalised_uncertainty)

        full_measurement = get_measurement_with_total_systematic_uncertainty(opts, x_sec_with_symmetrised_systematics)
        full_unfolded_measurement = get_measurement_with_total_systematic_uncertainty(opts, unfolded_x_sec_with_symmetrised_systematics)

        for keys in list_of_systematics.keys():
            write_normalised_xsection_measurement(opts, full_measurement[keys], full_unfolded_measurement[keys], summary = keys )





    # # Create categories of systematics. e.g. hadronisation, pdf, other...
    # list_systematic_categories = get_systematic_categories(opts, measurement_config)

    # # Print categories of systematics
    # print_systematic_categories(list_systematic_categories)

    # # What channels are systematics to be done for
    # for channel in ['electron', 'muon', 'combined', 'combinedBeforeUnfolding']:



    #     # Read in the normalised measurements from 01 and 02
    #     list_normalised_measurements = get_normalised_measurements(opts, list_systematic_categories)

    #     # Print the normalised measurements
    #     # print_normalised_measurements(list_normalised_measurements)

    #     # Get the upper and lower systematic variations for measured and unfolded
    #     upper_lower_variation_measured, up_down_variation_unfolded = get_upper_lower_variations(opts, list_normalised_measurements)

    #     # Get a list of the normalised measurements with their systematics
    #     list_measurement_with_systematics = get_measurement_with_systematics(opts, upper_lower_variation_measured, up_down_variation_unfolded)

    #     # Write central values and systematics to file
    #     write_normalised_measurements(opts, list_normalised_measurements, list_measurement_with_systematics, upper_lower_variation_measured, up_down_variation_unfolded)


    #     # get_correlation_matrix(opts, stuff_here=No idea yet)

