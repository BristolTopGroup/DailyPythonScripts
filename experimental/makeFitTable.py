from src.cross_section_measurement.lib import read_normalisation, read_fit_templates, read_initial_normalisation, closure_tests
from config.variable_binning import bin_edges
from config.latex_labels import samples_latex


# All possible options
# variables = [ 'MET', 'HT', 'ST', 'WPT', 'MT' ]
# channels = ['electron', 'muon']
# com = '8TeV'
# processes = [ 'TTJet', 'SingleTop', 'V+Jets', 'QCD' ]
# fitVariableCombinations = ['absolute_eta', 'M3', 'angle_bl', 'absolute_eta_M3_angle_bl']
# closureTest = True


variables = [ 'MET' ]
channels = ['electron' ]
com = '8TeV'
processes = [ 'TTJet', 'SingleTop', 'V+Jets', 'QCD' ]
fitVariableCombinations = ['absolute_eta', 'M3', 'angle_bl', 'absolute_eta_M3_angle_bl']
closureTest = True


def makeClosureErrorTable():
    for channel in channels:
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
                        fit_results_ = read_normalisation( dir,
                                                    variable,
                                                    'central',
                                                    channel,
                                                    'patType1CorrectedPFMet' )
                        fitResults[process].append( fit_results_[process][whichBin] )
                        pass
                    pass
                
                for process in processes:
                    line = samples_latex[process] + ' '
                
                    for fit in fitResults[process]:
                        line += '& %.0f \pm %.1f ' % ( fit[0],fit[1] )
                        pass
                    line +=' \\\\'
                    print line
                    pass
                print '\n'
                pass
            print '\n'
            pass
        pass
    pass

def makeClosureTestTable():
    fitVariable='absolute_eta_M3_angle_bl'
    for channel in channels:
        print 'CHANNEL :',channel
        for variable in variables:
            print '--->',variable
            # Read fit results
            dir = 'data/'+fitVariable+'/'+com+'/'
            if closureTest : dir = 'data/closure_test/simple/'+fitVariable+'/'+com+'/'
            fit_results = read_normalisation( dir,
                                        variable,
                                        'central',
                                        channel,
                                        'patType1CorrectedPFMet' )
            # Read initial values
            initial_values = read_initial_normalisation( dir,
                                        variable,
                                        'central',
                                        channel,
                                        'patType1CorrectedPFMet' )
            
#             for whichBin in range (0,len(bin_edges[variable])-1):
            for whichBin in range (0,1):
                for process in processes:
                    scale = closure_tests['simple'][process]
                    
                    line = '%s ' % (samples_latex[process])
                    line += '& %.0f ' % initial_values[process][whichBin][0]
                    line += '& %.0f ' % (initial_values[process][whichBin][0]*scale)
                    line += '& %.0f \pm %.0f ' % (fit_results[process][whichBin][0],fit_results[process][whichBin][1])
                    line += '\\\\'
                    print line
#                     print process
#                     print scale
#                     print initial_values[process][whichBin][0]
#                     print initial_values[process][whichBin][0]*scale
#                     print fit_results[process][whichBin][0],'+/-',fit_results[process][whichBin][1]
                    
                    pass
                pass
            print '\n'
            pass
        pass
    pass

if __name__ == '__main__':
    makeClosureTestTable()
    makeClosureErrorTable()
    pass
