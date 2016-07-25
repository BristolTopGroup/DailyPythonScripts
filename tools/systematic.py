from __future__ import division, print_function
from tools.file_utilities import read_data_from_JSON, write_data_to_JSON
from tools.Calculation import calculate_lower_and_upper_PDFuncertainty, \
calculate_lower_and_upper_systematics, combine_errors_in_quadrature
from copy import deepcopy
from math import sqrt

def read_normalised_xsection_measurement(options, category):
    '''
    Returns the normalised measurement and normalised unfolded measurement for the file associated with the variable under study
    '''
    variables_no_met=options['variables_no_met']
    path_to_JSON=options['path_to_JSON']
    met_systematics_suffixes=options['met_systematics_suffixes']
    method=options['method']
    channel=options['channel']
    variable=options['variable']

    filename = '{path}/{category}/normalised_xsection_{channel}_{method}.txt'
    if category in met_systematics_suffixes and ( variable in variables_no_met ) and not ('JES' in category or 'JER' in category):
        filename = filename.format(
            path = path_to_JSON,
            channel = channel,
            category = 'central',
            method = method,
        )
    else:
        filename = filename.format(
            path = path_to_JSON,
            channel = channel,
            category = category,
            method = method
        )
    normalised_xsection = read_data_from_JSON( filename )
    measurement = normalised_xsection['TTJet_measured']#should this be measured without fakes???
    measurement_unfolded = normalised_xsection['TTJet_unfolded']
    return measurement, measurement_unfolded
  
def read_normalised_xsection_systematics(options, list_of_systematics):
    '''
    Returns the list of normalised measurements and normalised unfolded measurements for each systematic category
    '''
    channel=options['channel']
    systematics = {}
    systematics_unfolded = {}
    
    for systematic_name in list_of_systematics:
        systematic, systematic_unfolded = read_normalised_xsection_measurement(options, systematic_name)
        
        systematics[systematic_name] = systematic
        systematics_unfolded[systematic_name] = systematic_unfolded
        
    return systematics, systematics_unfolded

def write_normalised_xsection_measurement(options, measurement, measurement_unfolded, summary = '' ):
    '''
    Writes the list of normalised measurements and normalised unfolded measurements of the form: 
    [Central Value, Lower Systemtic, Upper Systematic] to a json. Different combinations of 
    systematic uncertainty are stored as different json by appending different 'summary'
    '''
    path_to_JSON=options['path_to_JSON']
    method=options['method']
    channel=options['channel']

    output_file = '{path_to_JSON}/TEST/central/normalised_xsection_{channel}_{method}_with_errors.txt'
    output_file = output_file.format(
                    path_to_JSON = path_to_JSON,
                    channel = channel,
                    method = method,
                    )
    
    if not summary == '':
        output_file = output_file.replace( 'with_errors', summary + '_errors' )
    
    output = {'TTJet_measured':measurement, 'TTJet_unfolded': measurement_unfolded}
    
    write_data_to_JSON( output, output_file )

def get_systematic_categories(options, measurement_config):
    '''
    Returns a list of all the systematic categorys
    Returns of the form:

    [Systematic Category] : [Systemtic 1][Systemtic 2]...[Systemtic N] 
           |                
           |                               
           |
    '''
    ttbar_theory_systematic_prefix=options['ttbar_theory_systematic_prefix']
    vjets_theory_systematic_prefix=options['vjets_theory_systematic_prefix']
    met_systematics_suffixes=options['met_systematics_suffixes']
    # met_type=options['met_type']

    # SET UP SYSTEMATIC UNCERTAINTY LISTS
    # ttbar Generator Systematics
    ttbar_generator_systematics_list = [
        ttbar_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics
    ]
    # Remove hadronisation systematics from this list
    ttbar_generator_systematics_list.remove('TTJets_hadronisation')
    ttbar_generator_systematics_list.remove('TTJets_NLOgenerator')

    # V+Jets Uncertainties - Should probably be reincluded at some point
    # vjets_generator_systematics_list = [
    #     vjets_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics
    # ]

    # ttbar theory systematics: leptonreweighting, hadronisation systematic
    # ttbar_lepton_pt_reweight_systematic_list = [
    #     ttbar_theory_systematic_prefix + 'ptreweight',
    # ]

    # ttbar_lepton_eta_reweight_systematic_list = [
    #     ttbar_theory_systematic_prefix + 'etareweight',
    # ]

    ttbar_hadronisation_systematic_list = [
        ttbar_theory_systematic_prefix + 'hadronisation', 
        ttbar_theory_systematic_prefix + 'NLOgenerator', 
    ]

    ttbar_nlo_systematic_list = [
        ttbar_theory_systematic_prefix + 'NLOgenerator',
    ]

    # 100 PDF uncertainties
    pdf_uncertainties_systematic_list = [
        'PDFWeights_%d' % index for index in range( 0, 100 )
    ]

    # all MET uncertainties except JES and JER as this is already included
    # met_uncertainties_list = [
    #     met_type + suffix for suffix in met_systematics_suffixes if not 'JetEn' in suffix and not 'JetRes' in suffix
    # ]

    # rate changing systematics (luminosity, ttbar/single top cross section uncertainties)
    rate_changing_systematics_list = [
        systematic for systematic in measurement_config.rate_changing_systematics_names
    ]

    # all other uncertainties (including JES and JER)
    experimental_uncertainties_list = deepcopy( measurement_config.categories_and_prefixes.keys() )

    ### other_uncertainties_list.extend( vjets_generator_systematics_list )
    other_uncertainties_list = [ 'QCD_shape' ]
    other_uncertainties_list.extend( rate_changing_systematics_list )

    all_uncertainties = {
    'ttbar_generator'                 : ttbar_generator_systematics_list,
    # 'ttbar_lepton_pt_reweight'  : ttbar_lepton_pt_reweight_systematic_list,
    # 'ttbar_lepton_eta_reweight' : ttbar_lepton_eta_reweight_systematic_list,
    'hadronisation'             : ttbar_hadronisation_systematic_list,
    'ttbar_nlo'                 : ttbar_nlo_systematic_list,
    'ttbar_pdf'                 : pdf_uncertainties_systematic_list,
    # 'met'                       : met_uncertainties_list,
    'experimental'              : experimental_uncertainties_list,
    'other'                     : other_uncertainties_list
    }
    return all_uncertainties

def print_systematic_categories(all_uncertainties):
    '''
    Allows for the contents of each systematic category to be printed to the terminal
    '''
    for key, list_of_uncertainties in all_uncertainties.iteritems():
        print("The {key} uncertainty group contains :\n{list_of_uncertainties}\n".format(
            key=key, 
            list_of_uncertainties=list_of_uncertainties, 
            ) 
        )
    return

def get_normalised_measurements(options, all_uncertainties):
    '''
    Returns a list of all the normalised measurements and unfolded measurements in each bin for each systematic category 
    Returns of the form:

    [Systematic Category] : ['measured'] : [][]...[]
           |                ['unfolded'] : [Bin 1][Bin 2]...[Bin N]
           |                               [Bin N]=[Normalised measurement]
           |
    '''
    central_measurement, central_measurement_unfolded = read_normalised_xsection_measurement(
        options, 
        'central', 
    )
    ttbar_generator_systematics, ttbar_generator_systematics_unfolded = read_normalised_xsection_systematics(
        options, 
        list_of_systematics = all_uncertainties['ttbar_generator'], 
    )
    # ttbar_lepton_pt_reweight_systematics, ttbar_lepton_pt_reweight_systematics_unfolded = read_normalised_xsection_systematics(
        # options, 
        # list_of_systematics = all_uncertainties['ttbar_lepton_pt_reweight'], 
        # )
    # ttbar_lepton_eta_reweight_systematics, ttbar_lepton_eta_reweight_systematics_unfolded = read_normalised_xsection_systematics(
        # options, 
        # list_of_systematics = all_uncertainties['ttbar_lepton_eta_reweight'], 
        # )
    ttbar_hadronisation_systematics, ttbar_hadronisation_systematics_unfolded = read_normalised_xsection_systematics(
        options, 
        list_of_systematics = all_uncertainties['hadronisation'], 
    )
    ttbar_nlo_systematics, ttbar_nlo_systematics_unfolded = read_normalised_xsection_systematics(
        options, 
        list_of_systematics = all_uncertainties['ttbar_nlo'], 
    )
    pdf_systematics, pdf_systematics_unfolded = read_normalised_xsection_systematics(
        options, 
        list_of_systematics = all_uncertainties['ttbar_pdf'], 
    )
    # met_systematics, met_systematics_unfolded = read_normalised_xsection_systematics(
        # options, 
    #     list_of_systematics = all_uncertainties['met'], 
    #     )
    experimental_systematics, experimental_systematics_unfolded = read_normalised_xsection_systematics(
        options, 
        list_of_systematics = all_uncertainties['experimental'], 
    )
    other_systematics, other_systematics_unfolded = read_normalised_xsection_systematics(
        options, 
        list_of_systematics = all_uncertainties['other'], 
    )

    # List of all normalised measurements for the cross section for each systematic category
    all_normalised_measurements = {
    'central'                   : { 'measured' : central_measurement, 
                                    'unfolded' : central_measurement_unfolded
                                },
    'ttbar_generator'           : { 'measured' : ttbar_generator_systematics,
                                    'unfolded' : ttbar_generator_systematics_unfolded
                                },
    # 'ttbar_lepton_pt_reweight'  : { 'measured' : ttbar_lepton_pt_reweight_systematics,
    #                                 'unfolded' : ttbar_lepton_pt_reweight_systematics_unfolded
    #                             },
    # 'ttbar_lepton_eta_reweight' : { 'measured' : ttbar_lepton_eta_reweight_systematics,
    #                                 'unfolded' : ttbar_lepton_eta_reweight_systematics_unfolded
    #                             },
    'ttbar_hadronisation'        : {'measured' : ttbar_hadronisation_systematics,
                                    'unfolded' : ttbar_hadronisation_systematics_unfolded
                                },
    'ttbar_nlo'                  : {'measured' : ttbar_nlo_systematics,
                                    'unfolded' : ttbar_nlo_systematics_unfolded
                                },
    'pdf'                       : { 'measured' : pdf_systematics,
                                    'unfolded' : pdf_systematics_unfolded
                                },
    # 'met'                       : { 'measured' : met_systematics,
    #                                 'unfolded' : met_systematics_unfolded
    #                             },
    'experimental'              : { 'measured' : experimental_systematics,
                                    'unfolded' : experimental_systematics_unfolded
                                },
    'other'                     : { 'measured' : other_systematics,
                                    'unfolded' : other_systematics_unfolded
                                },
    }
    return all_normalised_measurements

def print_normalised_measurements(all_normalised_measurements):
    '''
    Allows for printing of the normalised measurements for the cross section
    '''
    for syst_category, measurements in all_normalised_measurements.iteritems():
        print( "Type of systematics being looked at is '{syst_category}'".format(syst_category=syst_category) )
        for key, list_of_norm_xsec_meas in measurements.iteritems():
            print("\nThe {key} normalised cross section measurements is :\n  {list_of_norm_xsec_meas}\n ".format(
                key=key, 
                list_of_norm_xsec_meas=list_of_norm_xsec_meas)
            ) 
    return

def get_upper_lower_variations(options, all_normalised_measurements):
    '''
    Returns a list of all the up and down variations in each bin for each systematic category 
    as well as the central measurement and statistical uncertainty. Returns of the form:

    [Central]             : [measurement, error]
    [Systematic Category] : ['up']   : [][]...[]
           |                ['down'] : [Bin 1][Bin 2]...[Bin N]
           |                           [Bin N]=[Up/Down Variation]
           |
    '''

    #### ttbar generator systematics (factorisation scale and matching threshold)
    ttbar_generator_min, ttbar_generator_max = summarise_systematics( 
        options,
        all_normalised_measurements['central']['measured'], 
        all_normalised_measurements['ttbar_generator']['measured'], 
    )
    ttbar_generator_min_unfolded, ttbar_generator_max_unfolded = summarise_systematics( 
        options,
        all_normalised_measurements['central']['unfolded'], 
        all_normalised_measurements['ttbar_generator']['unfolded'], 
    )

    #### ttbar theory systematics (lepton reweighting and hadronisation)
    # ttbar_lepton_pt_reweight_min, ttbar_lepton_pt_reweight_max = summarise_systematics( 
        # options,
    #     all_normalised_measurements['central']['measured'], 
    #     all_normalised_measurements['ttbar_lepton_pt_reweight']['measured'], 
    # )
    # ttbar_lepton_pt_reweight_min_unfolded, ttbar_lepton_pt_reweight_max_unfolded = summarise_systematics( 
        # options,
    #     all_normalised_measurements['central']['unfolded'], 
    #     all_normalised_measurements['ttbar_lepton_pt_reweight']['unfolded'], 
    # )

    # ttbar_lepton_eta_reweight_min, ttbar_lepton_eta_reweight_max = summarise_systematics( 
        # options,
    #     all_normalised_measurements['central']['measured'], 
    #     all_normalised_measurements['ttbar_lepton_eta_reweight']['measured'], 
    # )
    # ttbar_lepton_eta_reweight_min_unfolded, ttbar_lepton_eta_reweight_max_unfolded = summarise_systematics( 
        # options,
    #     all_normalised_measurements['central']['unfolded'], 
    #     all_normalised_measurements['ttbar_lepton_eta_reweight']['unfolded'], 
    # )

    ttbar_hadronisation_min, ttbar_hadronisation_max = summarise_systematics( 
        options,
        all_normalised_measurements['central']['measured'], 
        all_normalised_measurements['ttbar_hadronisation']['measured'], 
        hadronisation_systematic = True 
    )
    ttbar_hadronisation_min_unfolded, ttbar_hadronisation_max_unfolded = summarise_systematics( 
        options,
        all_normalised_measurements['central']['unfolded'], 
        all_normalised_measurements['ttbar_hadronisation']['unfolded'], 
        hadronisation_systematic = True 
    )

    ttbar_nlo_min, ttbar_nlo_max = summarise_systematics( 
        options,
        all_normalised_measurements['central']['measured'], 
        all_normalised_measurements['ttbar_nlo']['measured'], 
    )
    ttbar_nlo_min_unfolded, ttbar_nlo_max_unfolded = summarise_systematics( 
        options,
        all_normalised_measurements['central']['unfolded'], 
        all_normalised_measurements['ttbar_nlo']['unfolded'], 
    )

    pdf_min, pdf_max = summarise_systematics( 
        options,
        all_normalised_measurements['central']['measured'], 
        all_normalised_measurements['pdf']['measured'], 
        pdf_calculation = True 
    )
    pdf_min_unfolded, pdf_max_unfolded = summarise_systematics( 
        options,
        all_normalised_measurements['central']['unfolded'], 
        all_normalised_measurements['pdf']['unfolded'], 
        pdf_calculation = True 
    )

    # met_min, met_max = summarise_systematics( 
        # options,
    #     all_normalised_measurements['central']['measured'], 
    #     all_normalised_measurements['met']['measured'], 
    # )
    # met_min_unfolded, met_max_unfolded = summarise_systematics( 
        # options,
    #     all_normalised_measurements['central']['unfolded'], 
    #     all_normalised_measurements['met']['unfolded'], 
    # )

    experimental_min, experimental_max = summarise_systematics( 
        options,        
        all_normalised_measurements['central']['measured'], 
        all_normalised_measurements['experimental']['measured'], 
    )
    experimental_min_unfolded, experimental_max_unfolded = summarise_systematics( 
        options,        
        all_normalised_measurements['central']['unfolded'], 
        all_normalised_measurements['experimental']['unfolded'], 
    )

    # other
    other_min, other_max = summarise_systematics( 
        options,        
        all_normalised_measurements['central']['measured'], 
        all_normalised_measurements['other']['measured'], 
    )
    other_min_unfolded, other_max_unfolded = summarise_systematics( 
        options,        
        all_normalised_measurements['central']['unfolded'], 
        all_normalised_measurements['other']['unfolded'], 
    )

    # Storing all up and down variations for the measurement
    all_up_down_variations_measured = {
    'central'               : all_normalised_measurements['central']['measured'],
    'ttbar_generator'       : { 'up' : ttbar_generator_min,
                                'down' : ttbar_generator_max
                            },
    # 'ttbar_lepton_pt_reweight': { 'up' : ttbar_lepton_pt_reweight_min,
    #                           'down' : ttbar_lepton_pt_reweight_max
    #                         },
    # 'ttbar_lepton_eta_reweight' : { 'up' : ttbar_lepton_eta_reweight_min,
    #                           'down' : ttbar_lepton_eta_reweight_max
    #                         },
    'ttbar_hadronisation'   : { 'up' : ttbar_hadronisation_min,
                                'down' : ttbar_hadronisation_max
                            },
    'ttbar_nlo'             : { 'up' : ttbar_nlo_min,
                                'down' : ttbar_nlo_max
                            },
    'pdf'                   : { 'up' : pdf_min,
                                'down' : pdf_max
                            },
    # 'met'                 : { 'up' : met_min,
                                # 'down' : met_max
                            # },
    'experimental'          : { 'up' : experimental_min,
                                'down' : experimental_max
                            },
    'other'                 : { 'up' : other_min,
                                'down' : other_max
                            },
    }

    # Storing all up and down variations for the unfolded measurement
    all_up_down_variations_unfolded = {
    'central'               : all_normalised_measurements['central']['measured'],
    'ttbar_generator'       : { 'up' : ttbar_generator_min_unfolded,
                                'down' : ttbar_generator_max_unfolded
                            },
    # 'ttbar_lepton_pt_reweight'  : { 'up' : ttbar_lepton_pt_reweight_min_unfolded,
                            #   'down' : ttbar_lepton_pt_reweight_max_unfolded
                            # },
    # 'ttbar_lepton_eta_reweight' : { 'up' : ttbar_lepton_eta_reweight_min_unfolded,
                            #   'down' : ttbar_lepton_eta_reweight_max_unfolded
                            # },
    'ttbar_hadronisation'         : { 'up' : ttbar_hadronisation_min_unfolded,
                                'down' : ttbar_hadronisation_max_unfolded
                            },
    'ttbar_nlo'                   : { 'up' : ttbar_nlo_min_unfolded,
                                'down' : ttbar_nlo_max_unfolded
                            },
    'pdf'                   : { 'up' : pdf_min_unfolded,
                                'down' : pdf_max_unfolded
                            },
    # 'met'                 : { 'up' : met_min_unfolded,
                                # 'down' : met_max_unfolded
                            # },
    'experimental'          : { 'up' : experimental_min_unfolded,
                                'down' : experimental_max_unfolded
                            },
    'other'                 : { 'up' : other_min_unfolded,
                                'down' : other_max_unfolded
                            },
    }
    return all_up_down_variations_measured, all_up_down_variations_unfolded

def summarise_systematics(options, list_of_central_measurements, dictionary_of_systematics, pdf_calculation = False, hadronisation_systematic = False, mass_systematic = False, experimentalUncertainty = False, actualCentralMeasurements = [] ):
    symmetrise_errors = options['symmetrise_errors']
    # number of bins

    # TODO At the moment when retreiving up/down variations it combines all +ve variations and all -ve variations even if from massup/down are both +ve
    # Split into paired syst - up/down
    # And those that are symetric by nature like hadronisation

    # PDF may be interesting - alternative up and down variations.



    number_of_bins = len( list_of_central_measurements )
    down_errors = [0] * number_of_bins
    up_errors = [0] * number_of_bins
    list_of_systematics = {}

    for bin_i in range( number_of_bins ):
        central_value = list_of_central_measurements[bin_i][0]  # 0 = value, 1 = error
        error_down, error_up = 0, 0
        
        if pdf_calculation:
            pdf_uncertainty_values = {systematic:measurement[bin_i][0] for systematic, measurement in dictionary_of_systematics.iteritems()}
            error_down, error_up = calculate_lower_and_upper_PDFuncertainty( central_value, pdf_uncertainty_values )
            if symmetrise_errors:
                error_down = max( error_down, error_up )
                error_up = max( error_down, error_up )
        elif hadronisation_systematic:
            powheg_pythia = central_value
            for idex, systematic in dictionary_of_systematics.iteritems():
                # choose which hadronisation systematic is needed : "TTJets_hadronisation" or "TTJets_NLOgenerator"
                hadr_syst = dictionary_of_systematics[idex][bin_i][0]
                # always symmetric: absolute value of the difference between hadronisation syst and central
                difference = hadr_syst - powheg_pythia
                difference = abs(difference)
                error_down += difference**2
            error_down=sqrt(error_down)
            error_up=error_down
        elif mass_systematic:
            list_of_systematics = [systematic[bin_i][0] for systematic in dictionary_of_systematics.values()]
            error_down, error_up = calculate_lower_and_upper_systematics( central_value, list_of_systematics, False )
            # Scale errors calculated using very different top masses
            error_down, error_up = scaleTopMassSystematicErrors( [error_down], [error_up] )
            error_down = error_down[0]
            error_up = error_up[0]
        elif experimentalUncertainty:
            for systematic, value in dictionary_of_systematics.iteritems():
                variation = get_type_of_variation(systematic)
                # print(systematic)
                # print(variation)

                list_of_systematics[variation] = value[bin_i][0]
            print (list_of_systematics.keys())
            # list_of_systematics = [systematic[bin_i][0] for systematic in dictionary_of_systematics.values()]
            error_down, error_up = calculate_lower_and_upper_systematics( central_value, list_of_systematics, symmetrise_errors )
            actualCentralValue = actualCentralMeasurements[bin_i][0]
            error_down = error_down / central_value * actualCentralValue
            error_up = error_up / central_value * actualCentralValue
        else:
            for systematic, value in dictionary_of_systematics.iteritems():
                variation = get_type_of_variation(systematic)
                list_of_systematics[variation] = value[bin_i][0]
                # print(systematic)
                # print(variation)
            # list_of_systematics = [systematic[bin_i][0] for systematic in dictionary_of_systematics.values()]
            error_down, error_up = calculate_lower_and_upper_systematics( central_value, list_of_systematics, symmetrise_errors )
        down_errors[bin_i] = error_down
        up_errors[bin_i] = error_up

    print(up_errors)
    
    return down_errors, up_errors

def get_measurement_with_systematics(options, measured, unfolded):
    '''
    Returns the collection of measured or unfolded values with total upper and lower systematic uncertainty in the form
    [Bin 1][Bin 2]...[Bin N] where [Bin N]=[Central Value, Lower Systemtic, Upper Systematic]
    '''
    central_measurement_with_systematics = get_measurement_with_lower_and_upper_errors( 
        measured,
        symmetrise_errors = options['symmetrise_errors'],
    )
    central_measurement_with_systematics_but_without_generator = get_measurement_with_lower_and_upper_errors( 
        measured,
        withoutGenerator = True,
        symmetrise_errors = options['symmetrise_errors'],
    )
    central_measurement_with_systematics_only = get_measurement_with_lower_and_upper_errors( 
        measured,
        systematicErrorsOnly = True,
        symmetrise_errors = options['symmetrise_errors'],
    )
    central_measurement_unfolded_with_systematics = get_measurement_with_lower_and_upper_errors( 
        unfolded,
        symmetrise_errors = options['symmetrise_errors'],
    )
    central_measurement_unfolded_with_systematics_but_without_generator = get_measurement_with_lower_and_upper_errors( 
        unfolded,
        withoutGenerator = True, 
        symmetrise_errors = options['symmetrise_errors'],
    )
    central_measurement_unfolded_with_systematics_only = get_measurement_with_lower_and_upper_errors( 
        unfolded,
        systematicErrorsOnly = True,
        symmetrise_errors = options['symmetrise_errors'],
    )

    measurement_and_systematic_list = {
    'meas_with_syst'                        : central_measurement_with_systematics,
    'meas_with_syst_no_generator'           : central_measurement_with_systematics_but_without_generator,
    'meas_with_syst_only'                   : central_measurement_with_systematics_only,
    'meas_unfolded_with_syst'               : central_measurement_unfolded_with_systematics,
    'meas_unfolded_with_syst_no_generator'  : central_measurement_unfolded_with_systematics_but_without_generator,
    'meas_unfolded_with_syst_only'          : central_measurement_unfolded_with_systematics_only,
     }

    return measurement_and_systematic_list

def get_measurement_with_lower_and_upper_errors(list_of_variations, systematicErrorsOnly = False, withoutGenerator = False, symmetrise_errors=False ):
    '''
    Combines a list of systematic errors with the error from the measurement in quadrature.
    @param list_of_central_measurements: A list of measurements - one per bin - of the type (value,error)
    @param lists_of_lower_systematic_errors: Lists of systematic errors - format: [error1, error2, ...] where errorX = [(error), ...] with length = len(list_of_central_measurements)
    '''
    lists_of_upper_systematic_errors, lists_of_lower_systematic_errors = [], []
    # List of errors of the form : [Systematic 1][Systematic 2]...[Systematic N] where [Systematic N]=[Bin 1, Bin 2 ... Bin M]

    # Get lists of up and down variations.
    for syst_group, variation  in list_of_variations.iteritems():
        if withoutGenerator and syst_group=='ttbar_generator' : continue
        if syst_group=='central': 
            list_of_central_measurements=variation
        else:
            for type_of_variation, measurement in variation.iteritems():
                if type_of_variation=='up': lists_of_upper_systematic_errors.append(measurement)
                if type_of_variation=='down': lists_of_lower_systematic_errors.append(measurement)

    # How many bins this variable has
    n_entries = len( list_of_central_measurements )
    complete_measurement = [( 0, 0, 0 )] * n_entries
    
    for index in range( n_entries ):
        # Get the central measurement in each bin and associated error [value,error]
        central_value, central_error = list_of_central_measurements[index]  
        # Get the lower and upper systematic certainties for this particular bin
        lower_errors = [error[index] for error in lists_of_lower_systematic_errors]
        upper_errors = [error[index] for error in lists_of_upper_systematic_errors]
        # Add central error to the list (statistical)
        if not systematicErrorsOnly:
            lower_errors.append( central_error )
            upper_errors.append( central_error )

        # calculate total errors
        total_lower_error = combine_errors_in_quadrature( lower_errors )
        total_upper_error = combine_errors_in_quadrature( upper_errors )
        # If symmetric errors are required
        if symmetrise_errors:
            total_lower_error = max( total_lower_error, total_upper_error )
            total_upper_error = max( total_lower_error, total_upper_error )
        # Store per bin the central measurement with its up and down systematic uncertainty
        complete_measurement[index] = ( central_value, total_lower_error, total_upper_error )

    return complete_measurement

def replace_measurement_with_deviation_from_central(central_measurement, dictionary_of_systematic_measurements ):
    '''
    For each uncertainty replace the measured value with the difference between that value and the central value
    Returns of the form 
    [Systematic Category] : [Bin 1][Bin 2]..[Bin N] where [Bin N]=[Difference to Central]
    '''
    new_dictionary_of_systematic_measurements = {}
    
    for systematic, systematic_measurement in dictionary_of_systematic_measurements.iteritems():
        new_set_of_values = []
        # zip allows iteration over lists in parallel
        for ( value, _ ), ( central, _ ) in zip( systematic_measurement, central_measurement ):
            deviation = abs( value ) - abs( central )    
            new_set_of_values.append( deviation )
        new_dictionary_of_systematic_measurements[systematic] = new_set_of_values
    return new_dictionary_of_systematic_measurements

def write_normalised_measurements(options, all_normalised_measurements, measurement_and_systematic_list, list_of_variations, list_of_variations_unfolded):
    '''
    Write all the normalised measurements and systematics to file
    '''
    write_normalised_xsection_measurement(
        options, 
        measurement_and_systematic_list['meas_with_syst'],
        measurement_and_systematic_list['meas_unfolded_with_syst'],
    )
    write_normalised_xsection_measurement(
        options, 
        measurement_and_systematic_list['meas_with_syst_no_generator'],
        measurement_and_systematic_list['meas_unfolded_with_syst_no_generator'],
        summary = 'with_systematics_but_without_generator' 
    )
    write_normalised_xsection_measurement(
        options, 
        measurement_and_systematic_list['meas_with_syst_only'],
        measurement_and_systematic_list['meas_unfolded_with_syst_only'],
        summary = 'with_systematics_only' 
    )

    # Now to create output files for each individual systematic uncertainty category
    # Replace measurement with deviation from central
    all_normalised_measurements['ttbar_generator']['measured'] = replace_measurement_with_deviation_from_central( 
        all_normalised_measurements['central']['measured'], 
        all_normalised_measurements['ttbar_generator']['measured'] 
    )
    all_normalised_measurements['pdf']['measured'] = replace_measurement_with_deviation_from_central( 
        all_normalised_measurements['central']['measured'], 
        all_normalised_measurements['pdf']['measured'] 
    )
    all_normalised_measurements['ttbar_hadronisation']['measured'] = replace_measurement_with_deviation_from_central( 
        all_normalised_measurements['central']['measured'], 
        all_normalised_measurements['ttbar_hadronisation']['measured'] 
    )
    all_normalised_measurements['other']['measured'] = replace_measurement_with_deviation_from_central( 
        all_normalised_measurements['central']['measured'], 
        all_normalised_measurements['other']['measured'] 
    )
    all_normalised_measurements['experimental']['measured'] = replace_measurement_with_deviation_from_central( 
        all_normalised_measurements['central']['measured'], 
        all_normalised_measurements['experimental']['measured'] 
    )

    all_normalised_measurements['ttbar_generator']['unfolded'] = replace_measurement_with_deviation_from_central( 
        all_normalised_measurements['central']['unfolded'], 
        all_normalised_measurements['ttbar_generator']['unfolded'] 
    )
    all_normalised_measurements['pdf']['unfolded'] = replace_measurement_with_deviation_from_central( 
        all_normalised_measurements['central']['unfolded'], 
        all_normalised_measurements['pdf']['unfolded'] 
    )
    all_normalised_measurements['ttbar_hadronisation']['unfolded'] = replace_measurement_with_deviation_from_central( 
        all_normalised_measurements['central']['unfolded'], 
        all_normalised_measurements['ttbar_hadronisation']['unfolded'] 
    )
    all_normalised_measurements['other']['unfolded'] = replace_measurement_with_deviation_from_central( 
        all_normalised_measurements['central']['unfolded'], 
        all_normalised_measurements['other']['unfolded'] 
    )
    all_normalised_measurements['experimental']['unfolded'] = replace_measurement_with_deviation_from_central( 
        all_normalised_measurements['central']['unfolded'], 
        all_normalised_measurements['experimental']['unfolded'] 
    )

    # Add in the total errors
    #### TODO: these are currently still storing the measurement, but should store the difference to the measurement like total_*
    all_normalised_measurements['ttbar_generator']['measured']['total_lower'] = list_of_variations['ttbar_generator']['down']
    all_normalised_measurements['ttbar_generator']['measured']['total_upper'] = list_of_variations['ttbar_generator']['up']
    all_normalised_measurements['ttbar_generator']['unfolded']['total_lower'] = list_of_variations_unfolded['ttbar_generator']['down']
    all_normalised_measurements['ttbar_generator']['unfolded']['total_upper'] = list_of_variations_unfolded['ttbar_generator']['up']

    all_normalised_measurements['pdf']['measured']['total_lower'] = list_of_variations['pdf']['down']
    all_normalised_measurements['pdf']['measured']['total_upper'] = list_of_variations['pdf']['up']
    all_normalised_measurements['pdf']['unfolded']['total_lower'] = list_of_variations_unfolded['pdf']['down']
    all_normalised_measurements['pdf']['unfolded']['total_upper'] = list_of_variations_unfolded['pdf']['up']

    all_normalised_measurements['ttbar_hadronisation']['measured']['total_lower'] = list_of_variations['ttbar_hadronisation']['down']
    all_normalised_measurements['ttbar_hadronisation']['measured']['total_upper'] = list_of_variations['ttbar_hadronisation']['up']
    all_normalised_measurements['ttbar_hadronisation']['unfolded']['total_lower'] = list_of_variations_unfolded['ttbar_hadronisation']['down']
    all_normalised_measurements['ttbar_hadronisation']['unfolded']['total_upper'] = list_of_variations_unfolded['ttbar_hadronisation']['up']

    all_normalised_measurements['other']['measured']['total_lower'] = list_of_variations['other']['down']
    all_normalised_measurements['other']['measured']['total_upper'] = list_of_variations['other']['up']
    all_normalised_measurements['other']['unfolded']['total_lower'] = list_of_variations_unfolded['other']['down']
    all_normalised_measurements['other']['unfolded']['total_upper'] = list_of_variations_unfolded['other']['up']

    all_normalised_measurements['experimental']['measured']['total_lower'] = list_of_variations['experimental']['down']
    all_normalised_measurements['experimental']['measured']['total_upper'] = list_of_variations['experimental']['up']
    all_normalised_measurements['experimental']['unfolded']['total_lower'] = list_of_variations_unfolded['experimental']['down']
    all_normalised_measurements['experimental']['unfolded']['total_upper'] = list_of_variations_unfolded['experimental']['up']

    write_normalised_xsection_measurement(
        options, 
        all_normalised_measurements['ttbar_generator']['measured'], 
        all_normalised_measurements['ttbar_generator']['unfolded'], 
        summary = 'ttbar_generator' 
    )
    write_normalised_xsection_measurement(
        options, 
        all_normalised_measurements['pdf']['measured'], 
        all_normalised_measurements['pdf']['unfolded'], 
        summary = 'PDF' 
    )
    write_normalised_xsection_measurement(
        options, 
        all_normalised_measurements['ttbar_hadronisation']['measured'], 
        all_normalised_measurements['ttbar_hadronisation']['unfolded'], 
        summary = 'ttbar_hadronisation' 
    )
    write_normalised_xsection_measurement(
        options, 
        all_normalised_measurements['other']['measured'], 
        all_normalised_measurements['other']['unfolded'], 
        summary = 'other' 
    )
    write_normalised_xsection_measurement(
        options, 
        all_normalised_measurements['experimental']['measured'], 
        all_normalised_measurements['experimental']['unfolded'], 
        summary = 'experimental' 
    )
    return

def get_type_of_variation(systematic_name):
    variation=0


    var = systematic_name[-2:-1]
    if (var == "up"): variation=1
    if (var == "Up"): variation=1

    var = systematic_name[-1]
    if (var == "+"): variation=1
    if (var == "-"): variation=-1

    var = systematic_name[-4:-1]
    if (var == "down"): variation=-1
    if (var == "Down"): variation=-1

    return variation



# def scaleTopMassSystematicErrors( error_down, error_up ):
#     error_down_new, error_up_new = [], []
#     for down,up in zip( error_down,error_up ):
#         upMassDifference = measurement_config.topMasses[2] - measurement_config.topMasses[1]
#         downMassDifference = measurement_config.topMasses[1] - measurement_config.topMasses[0]

#         error_down_new.append( down * measurement_config.topMassUncertainty / downMassDifference )
#         error_up_new.append( up * measurement_config.topMassUncertainty / upMassDifference )
#     return error_down_new, error_up_new
