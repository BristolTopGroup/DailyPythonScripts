'''
Created on 10 April 2013

@author: kreczko

This module produces several results for the three channels (electron, muon, combined):
1) central measurement with error =  sqrt([combined systematic uncertainties]^2 + [unfolding]^2)
2) all systematics evaluated with respect to central: up & down shifts, MET summary, PDF summary, Total up & down
3) additional result for MET systematics
4) additional result for PDF systematics

1) + existing result can be used for the final plots
2) can be used to compare systematics (both in tables and plots)
3) + 4) for more fine-grained analysis
'''
from optparse import OptionParser
from copy import deepcopy


if __name__ == "__main__":
    '''
    1) read all fit results (group by MET, PDF, other)
    2) calculate the difference to central measurement
    3) 
    '''
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", default='data/',
                  help="set path to JSON files")
    parser.add_option("-v", "--variable", dest="variable", default='MET',
                  help="set variable to plot (MET, HT, ST, MT)")
    parser.add_option("-m", "--metType", dest="metType", default='type1',
                      help="set MET type used in the analysis of MET, ST or MT")
    parser.add_option("-b", "--bjetbin", dest="bjetbin", default='2m',
                  help="set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m")
    parser.add_option("-k", "--k_value", type='int',
                      dest="k_value", default=6,
                      help="k-value for SVD unfolding, used in histogram names")
    parser.add_option("-c", "--centre-of-mass-energy", dest="CoM", default=8, type=int,
                      help="set the centre of mass energy for analysis. Default = 8 [TeV]")
    
    
    (options, args) = parser.parse_args()
    from config.cross_section_measurement_common import analysis_types, met_systematics_suffixes, translate_options
    
    path_to_JSON = options.path
    variable = options.variable
    met_type = translate_options[options.metType]
    k_value = options.k_value
    b_tag_bin = translate_options[options.bjetbin]
    
    if options.CoM == 8:
        from config.variable_binning_8TeV import bin_widths, bin_edges
        import config.cross_section_measurement_8TeV as measurement_config
    elif options.CoM == 7:
        from config.variable_binning_7TeV import bin_widths, bin_edges
        import config.cross_section_measurement_7TeV as measurement_config
    else:
        import sys
        sys.exit('Unknown centre of mass energy')
        

    categories = deepcopy(measurement_config.categories_and_prefixes.keys())
    categories.extend(measurement_config.generator_systematics)
    
    pdf_uncertainties = ['PDFWeights_%d' % index for index in range(1,45)]
    #all MET uncertainties except JES as this is already included
    met_uncertainties = [met_type + suffix for suffix in met_systematics_suffixes if not 'JetEn' in suffix]
    all_measurements = deepcopy(categories)
    all_measurements.extend(pdf_uncertainties)
    all_measurements.extend(met_uncertainties)
    #[ 'central', 'matchingup', 'matchingdown', 'scaleup', 'scaledown', 'BJet_down', 'BJet_up', 'JES_down', 'JES_up', 'LightJet_down', 'LightJet_up', 'PU_down', 'PU_up' ]