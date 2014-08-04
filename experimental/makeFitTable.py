from src.cross_section_measurement.lib import read_fit_results, read_fit_templates, read_fit_input, closure_tests
from config.variable_binning import bin_edges

variables = [ 'MET', 'HT', 'ST', 'WPT', 'MT' ]
channel = 'electron'
com = '8TeV'
processes = [ 'TTJet', 'SingleTop', 'V+Jets', 'QCD' ]
fitVariableCombinations = ['absolute_eta', 'M3', 'angle_bl', 'absolute_eta_M3_angle_bl']
closureTest = True

for channel in ['electron', 'muon']:
    print 'CHANNEL :',channel
    for variable in variables:
        print '--->',variable
        for whichBin in range (0,len(bin_edges[variable])-1):
            fitResults = {}
            for process in processes:
                fitResults[process] = []
                for fitVariable in fitVariableCombinations:
                    # Read fit results
                    dir = 'data/'+fitVariable+'/'+com+'/'
                    if closureTest : dir = 'data/closure_test/simple/'+fitVariable+'/'+com+'/'
                    fit_results_ = read_fit_results( dir,
                                                variable,
                                                'central',
                                                channel,
                                                'patType1CorrectedPFMet' )
                    
                    fitResults[process].append( fit_results_[process][whichBin] )
                    pass
                pass
            
            for process in processes:
                line = process + ' :\t'
            
                for fit in fitResults[process]:
                    line += '%.1f +/- %.1f \t' % ( fit[0],fit[1] )
                    pass
                print line
                pass
            print '\n'
            pass
        print '\n'
        pass



