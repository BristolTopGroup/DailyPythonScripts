'''
Created on 20 Jul 2014

@author: phxlk
'''
import os
from optparse import OptionParser

from config import XSectionConfig, fit_var_inputs, latex_labels
from src.cross_section_measurement.lib import closure_tests, read_fit_templates, \
    read_initial_normalisation
from tools.file_utilities import read_data_from_JSON, write_data_to_JSON
from config.variable_binning import variable_bins_ROOT, fit_variable_bin_edges, bin_edges_vis
from tools.Fitting import FitData, FitDataCollection, Minuit
from tools.hist_utilities import value_tuplelist_to_hist
from tools.plotting import Histogram_properties, compare_measurements
from config import CMS
from matplotlib import rc
rc( 'font', **CMS.font )
rc( 'text', usetex = True )

def main():
    global config, options
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data/fit_checks/no_merging',
                  help = "set path to JSON files" )
    parser.add_option( '--create_fit_data', dest = "create_fit_data", action = "store_true",
                      help = "create the fit data for testing." )
    parser.add_option( '--refit', dest = "refit", action = "store_true",
                      help = "Fit again even if the output already exists" )
    parser.add_option( '--test', dest = "test", action = "store_true",
                      help = "Test only: run just one selected sample" )
    variables = config.histogram_path_templates.keys()
    fit_variables = fit_var_inputs
    mc_samples = ['TTJet', 'SingleTop', 'QCD', 'V+Jets']
    tests = closure_tests
    channels = ['electron', 'muon']
    COMEnergies = ['7', '8']
    
    ( options, _ ) = parser.parse_args()
    print 'Running from path', options.path 
    
    if ( options.create_fit_data ):
        create_fit_data( options.path, variables, fit_variables, mc_samples,
                        COMEnergies = COMEnergies, channels = channels )
     
    output_file = options.path + '/fit_test_output.txt'
    if options.test:
        output_file = options.path + '/fit_test_output_test.txt'
    if options.refit or not os.path.isfile( output_file ) or options.test:
        if os.path.isfile( options.path + '/fit_check_data.txt' ):
            fit_data = read_data_from_JSON( options.path + '/fit_check_data.txt' )
            results = run_tests( fit_data,
                                COMEnergies,
                                variables,
                                fit_variables,
                                mc_samples,
                                channels,
                                tests )
            write_data_to_JSON(results, output_file )
        else:
            print 'Please run bin/prepare_data_for_fit_checks first'
            print 'Then run this script with the option --create_fit_data.'
     
    results = read_data_from_JSON(output_file)
    plot_results( results )
    
def create_fit_data( path, variables, fit_variables, mc_samples, COMEnergies, channels ):
    '''
        Creates the fit data in path + fit_check_data.txt in the JSON format.
        The resulting dictionary is of the form
        {centre-of-mass-energy: {
            channel : {
                variable : {
                    variable_bin : { 
                        fit_variable : {
                            templates : { sample : []},
                            initial_values : { sample : []}
                                }
                            }
                        }
                    }
                }
        }
    '''
    # first step is to read the data
    raw_data = {}
    # the folder structure is
    # path/fit_variable/centre-of-mass-energy/variable/fit_results/central/*
    for fit_variable in fit_variables:
        raw_data[fit_variable] = {}
        for COMEnergy in COMEnergies:
            raw_data[fit_variable][COMEnergy] = {}
            for variable in variables:
                raw_data[fit_variable][COMEnergy][variable] = {}
                for channel in channels:
                    raw_data[fit_variable][COMEnergy][variable][channel] = {}
                    data_path = path + '/' + fit_variable + '/' + str( COMEnergy ) + 'TeV'
                    templates = read_fit_templates( data_path, variable,
                                                   channel = channel )
                    initial_values = read_initial_normalisation( data_path,
                                                    variable,
                                                    channel = channel )
                    raw_data[fit_variable][COMEnergy][variable][channel]['templates'] = templates
                    raw_data[fit_variable][COMEnergy][variable][channel]['initial_values'] = initial_values
    # put it into the new structure
    fit_data = {}
    for COMEnergy in COMEnergies:
        fit_data[COMEnergy] = {}
        for channel in channels:
            fit_data[COMEnergy][channel] = {}
            for variable in variables:
                fit_data[COMEnergy][channel][variable] = {}
                for v_bin in variable_bins_ROOT[variable]:
                    fit_data[COMEnergy][channel][variable][v_bin] = {}
                    for fit_variable in fit_variables:
                        fit_data[COMEnergy][channel][variable][v_bin][fit_variable] = {}
                        fit_data[COMEnergy][channel][variable][v_bin][fit_variable]['templates'] = raw_data[fit_variable][COMEnergy][variable][channel]['templates']
                        fit_data[COMEnergy][channel][variable][v_bin][fit_variable]['initial_values'] = raw_data[fit_variable][COMEnergy][variable][channel]['initial_values']
                    
    write_data_to_JSON( fit_data, path + '/fit_check_data.txt', indent = False )

def run_tests( fit_data, COMEnergies, variables, fit_variables,
               mc_samples, channels, tests ):
    '''
        Runs all specified tests on the fit data (as produced by create_fit_data) 
        and produces results of the form
        {centre-of-mass-energy: {
            channel : {
                variable : {
                    fit_variable : {
                        test: { sample : [chi2]}
                            }
                        }
                    }
                }
        }
        
        where chi2 = \frac{N_{exp} - N_{fit}}{sigma_{fit}} for each bin of the variable
    '''
    global options
    
    results = {}
    # initiate first
    for COMEnergy in COMEnergies:
        results[COMEnergy] = {}
    for COMEnergy in COMEnergies:
        results[COMEnergy] = {}
        for channel in channels:
            results[COMEnergy][channel] = {}
            for variable in variables:
                results[COMEnergy][channel][variable] = {}
                for fit_variable in fit_variables:
                    if options.test and not is_test_only(COMEnergy, channel, variable, fit_variable):
                            continue
                    results[COMEnergy][channel][variable][fit_variable] = {}
                    for test, scales in tests.iteritems():
                        results[COMEnergy][channel][variable][fit_variable][test] = {}
                        for sample in mc_samples:
                                results[COMEnergy][channel][variable][fit_variable][test][sample] = []
    
    for COMEnergy in COMEnergies:
#         results[COMEnergy] = {}
        for channel in channels:
#             results[COMEnergy][channel] = {}
            for variable in variables:
#                 results[COMEnergy][channel][variable] = {}
                for nth_bin, v_bin in enumerate( variable_bins_ROOT[variable] ):
                    for fit_variable in fit_variables:
                        if options.test and not is_test_only(COMEnergy, channel, variable, fit_variable):
                            continue
#                         if not results[COMEnergy][channel][variable].has_key( fit_variable ):
#                             results[COMEnergy][channel][variable][fit_variable] = {}
                        for test, scales in tests.iteritems():
#                             results[COMEnergy][channel][variable][fit_variable][test] = {}
                            data = fit_data[COMEnergy][channel][variable][v_bin][fit_variable]
                            test_data = create_test_data( data, scales, mc_samples, nth_bin )
                            result = run_test( test_data )
#                             print COMEnergy, channel, variable, nth_bin, fit_variable, test
#                             print result
                            for sample in mc_samples:
#                                 if not results[COMEnergy][channel][variable][fit_variable][test].has_key( sample ):
#                                     print 'Oh, no!', sample
#                                     results[COMEnergy][channel][variable][fit_variable][test][sample] = []
                                results[COMEnergy][channel][variable][fit_variable][test][sample].append( result[sample] )
    return results

def create_test_data( data, scales, samples, nth_bin ):
    '''
        Creates a set of data for testing.
        The inputs are
         - data: {templates : {fit_variable: {sample : []}, 
                  initial_values : {fit_variable: { sample : []}}}
         - scales: {sample : scale}
        The output is:
        { fit_variable : {sample : {distribution : [], normalisation : X }}
        where distribution == template * normalisation 
        
    '''
    test_data = {}
    fit_variables = data['templates'].keys()
    for fit_variable in fit_variables:
        test_data[fit_variable] = {}
        for sample in samples:
            test_data[fit_variable][sample] = {}
            template = data['templates'][fit_variable][sample][nth_bin]
            initial_value = data['initial_values'][sample]
            scale = scales[sample]
            # ignore errors
            value, _ = initial_value[nth_bin]
            normalisation = value * scale
            sample_data = [x * normalisation for x in template]
            test_data[fit_variable][sample]['distribution'] = sample_data
            test_data[fit_variable][sample]['normalisation'] = normalisation
    return test_data

def run_test ( test_data ):
    ''' Used the test_data to fit the number of events for each process
    '''
    global config
    data_scale = 1.2
    fit_data_collection = FitDataCollection()
    for fit_variable, fit_input in test_data.iteritems():
        # create the histograms
        mc_histograms = {}
        for sample, h_input in fit_input.iteritems():
            mc_histograms[sample] = value_tuplelist_to_hist( h_input['distribution'],
                                                             fit_variable_bin_edges[fit_variable] )
        real_data = sum( mc_histograms[sample] for sample in mc_histograms.keys() )
        # scale data so that the fit does not start in the minimum
        real_data.Scale( data_scale )
        fit_data = FitData( real_data, mc_histograms, fit_boundaries = config.fit_boundaries[fit_variable] )
        fit_data_collection.add( fit_data, fit_variable )
    # do fit
    fitter = Minuit( fit_data_collection )
    fitter.fit()
    fit_results = fitter.results
    # calculate chi2 for each sample
    chi2_results = {}
    for sample in fit_results.keys():
        true_normalisation = fit_input[sample]['normalisation'] * data_scale
#         fit_result, fit_error = fit_results[sample]
#         chi2 = pow( true_normalisation - fit_result, 2 ) / pow( fit_error, 2 )
        fit_result, _ = fit_results[sample]
        chi2 = pow( true_normalisation - fit_result, 2 )
        chi2_results[sample] = chi2
    
    return chi2_results


def plot_results ( results ):
    '''
    Takes results fo the form:
        {centre-of-mass-energy: {
            channel : {
                variable : {
                    fit_variable : {
                        test : { sample : []},
                        }
                    }
                }
            }
        }
    '''
    global options
    output_base = 'plots/fit_checks/chi2'
    for COMEnergy in results.keys():
        tmp_result_1 = results[COMEnergy]
        for channel in tmp_result_1.keys():
            tmp_result_2 = tmp_result_1[channel]
            for variable in tmp_result_2.keys():
                tmp_result_3 = tmp_result_2[variable]
                for fit_variable in tmp_result_3.keys():
                    tmp_result_4 = tmp_result_3[fit_variable]
                    # histograms should be {sample: {test : histogram}}
                    histograms = {}
                    for test, chi2 in tmp_result_4.iteritems():
                        for sample in chi2.keys():
                            if not histograms.has_key(sample):
                                histograms[sample] = {}
                            # reverse order of test and sample
                            histograms[sample][test] = value_tuplelist_to_hist(chi2[sample], bin_edges_vis[variable])
                    for sample in histograms.keys():
                        hist_properties = Histogram_properties()
                        hist_properties.name = sample.replace('+', '') + '_chi2'
                        hist_properties.title = '$\\chi^2$ distribution for fit output (' + sample + ')'
                        hist_properties.x_axis_title = '$' + latex_labels.variables_latex[variable] + '$ [TeV]'
                        hist_properties.y_axis_title = '$\chi^2 = \\left({N_{fit}} - N_{{exp}}\\right)^2$'
                        hist_properties.set_log_y = True
                        hist_properties.y_limits = (1e-20, 1e20)
                        path = output_base + '/' + COMEnergy + 'TeV/' + channel + '/' + variable + '/' + fit_variable + '/'
                        if options.test:
                            path = output_base + '/test/'
                        
                        measurements = {}
                        for test, histogram in histograms[sample].iteritems():
                            measurements[test.replace('_',' ')] = histogram
                        compare_measurements({}, 
                                             measurements, 
                                             show_measurement_errors = False, 
                                             histogram_properties = hist_properties, 
                                             save_folder = path, 
                                             save_as = ['pdf'])

def is_test_only(COMEnergy, channel, variable, fit_variable):
    never = COMEnergy == '8'
    gonna = channel == 'electron'
    give = variable == 'MET'
    you = fit_variable == 'absolute_eta'
    up = True
    return never and gonna and give and you and up 

if __name__ == '__main__':
    config = XSectionConfig( 8 )  # assume same setup for all
    options = None
    main()
