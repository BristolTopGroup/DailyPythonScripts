'''
Created on Mar 12, 2014

@author: Luke Kreczko

github: kreczko

This script is meant to pick bins used for the measurement for both electron 
and muon channel.
It is maximising the number of bins while keeping *purity*, *stability* and
statistical error above/below a certain limit.
The lower limits for all can be specified and the variable for maximisation can
be picked.
It accepts multiple inputs (channels, files for differenc centre of mass 
energies) and will synchronise binning between them


*purity* is defined as the number reconstructed & generated events in one bin 
divided by the number of reconstructed events:
p_i = \frac{N^{\text{rec\&gen}}}{N^{\text{rec}}}

*stability* is defined as the number reconstructed & generated events in one bin
divided by the number of generated events: 
s_i = \frac{N^{\text{rec\&gen}}}{N^{\text{rec}}}

On the response matrix (gen vs reco) this looks like this:
N^{\text{rec\&gen}}_0
 _ | _ | _
 _ | _ | _
 X | _ | _
 
 N^{\text{rec}}_0 is the sum of X
 X | _ | _
 X | _ | _
 X | _ | _
 
 N^{\text{gen}}_0 is the sum of X
 _ | _ | _
 _ | _ | _
 X | X | X
'''

from rootpy import asrootpy
from rootpy.io import File
from tools.Calculation import calculate_purities, calculate_stabilities
from tools.hist_utilities import rebin_2d
from config import XSectionConfig
from optparse import OptionParser
from config.variable_binning import bin_edges

def main():
    '''
    Step 1: Get the 2D histogram for every sample (channel and/or centre of mass energy)
    Step 2: Change the size of the first bin until it fulfils the minimal criteria
    Step 3: Check if it is true for all other histograms. If not back to step 2
    Step 4: Repeat step 2 & 3 until no mo bins can be created
    '''

    parser = OptionParser()
    parser.add_option( '-v', dest = "visiblePhaseSpace", action = "store_true",
                      help = "Consider visible phase space or not" )
    ( options, args ) = parser.parse_args()

    p_min = 0.5
    s_min = 0.5
    # we also want the statistical error to be larger than 5%
    # this translates (error -= 1/sqrt(N)) to (1/0.05)^2 = 400
    n_min = 100
#     n_min = 200 # N = 200 -> 7.1 % stat error
     
    bin_choices = {}

    for variable in bin_edges.keys():
        print '--- Doing variable',variable
        variableToUse = variable
        if 'Rap' in variable:
            variableToUse = 'abs_%s' % variable
        histogram_information = get_histograms( variableToUse, options )
        print 'Got histograms'
        best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min )
        print 'Got best binning'
        if 'Rap' in variable:
            for bin in list(best_binning):
                print bin
                if bin != 0.0:
                    best_binning.append(-1.0*bin)
            best_binning.sort()

        bin_choices[variable] = best_binning
        print 'The best binning for', variable, 'is:'
        print 'bin edges =', best_binning
        print 'N_bins    =', len( best_binning ) - 1
        print '-' * 120
        print 'The corresponding purities and stabilities are:'
        for info in histogram_information:
            print_latex_table(info, variable, best_binning)
        print '=' * 120  

    print '=' * 120
    print 'For config/variable_binning.py'
    print '=' * 120
    for variable in bin_choices:
        print '\''+variable+'\' : '+str(bin_choices[variable])+','

def get_histograms( variable, options ):
    config = XSectionConfig( 13 )

    path_electron = ''
    path_muon = ''
    histogram_name = ''
    if options.visiblePhaseSpace:
        histogram_name = 'responseVis_without_fakes'
    else :
        histogram_name = 'response_without_fakes'


    if variable == 'HT':
        path_electron = 'unfolding_HT_analyser_electron_channel/%s' % histogram_name
        path_muon = 'unfolding_HT_analyser_muon_channel/%s' % histogram_name
    else :
        path_electron = 'unfolding_%s_analyser_electron_channel_patType1CorrectedPFMet/%s' % ( variable, histogram_name )
        path_muon = 'unfolding_%s_analyser_muon_channel_patType1CorrectedPFMet/%s' % ( variable, histogram_name )

    histogram_information = [
                {'file': config.unfolding_madgraph_raw,
                 'CoM': 13,
                 'path':path_electron,
                 'channel':'electron'},
                {'file':config.unfolding_madgraph_raw,
                 'CoM': 13,
                 'path':path_muon,
                 'channel':'muon'},
                 ]
    

    for histogram in histogram_information:
        f = File( histogram['file'] )
        # scale to lumi
        # nEvents = f.EventFilter.EventCounter.GetBinContent( 1 )  # number of processed events 
        # config = XSectionConfig( histogram['CoM'] )
        # lumiweight = config.ttbar_xsection * config.new_luminosity / nEvents

        lumiweight = 1

        histogram['hist'] = f.Get( histogram['path'] ).Clone()
        histogram['hist'].Scale( lumiweight )
        # change scope from file to memory
        histogram['hist'].SetDirectory( 0 )
        f.close()
    return histogram_information
    

def get_best_binning( histogram_information, p_min, s_min, n_min ):
    '''
    Step 1: Change the size of the first bin until it fulfils the minimal criteria
    Step 3: Check if it is true for all other histograms. If not back to step 2
    Step 4: Repeat step 2 & 3 until no mo bins can be created
    '''
    histograms = [info['hist'] for info in histogram_information]
    bin_edges = []
    purities = {}
    stabilities = {}
    
    current_bin_start = 0
    current_bin_end = 0

    first_hist = histograms[0]
    n_bins = first_hist.GetNbinsX()
    
    while current_bin_end < n_bins:
        current_bin_end, _, _, _ = get_next_end( histograms, current_bin_start, current_bin_end, p_min, s_min, n_min )
        if not bin_edges:
            # if empty
            bin_edges.append( first_hist.GetXaxis().GetBinLowEdge( current_bin_start + 1 ) )
        bin_edges.append( first_hist.GetXaxis().GetBinLowEdge( current_bin_end ) + first_hist.GetXaxis().GetBinWidth( current_bin_end ) )
        current_bin_start = current_bin_end
    
    # add the purity and stability values for the final binning
    for info in histogram_information:
        new_hist = rebin_2d( info['hist'], bin_edges, bin_edges ).Clone( info['channel'] + '_' + str( info['CoM'] ) )  
        get_bin_content = new_hist.GetBinContent
        purities = calculate_purities( new_hist.Clone() )
        stabilities = calculate_stabilities( new_hist.Clone() )
        n_events = [int( get_bin_content( i, i ) ) for i in range( 1, len( bin_edges ) )]
        # Now check if the last bin also fulfils the requirements
        if purities[-1] < p_min or stabilities[-1] < s_min or n_events[-1] < n_min:
            # if not, merge last two bins 
            bin_edges[-2] = bin_edges[-1]
            bin_edges = bin_edges[:-1]
            new_hist = rebin_2d( info['hist'], bin_edges, bin_edges ).Clone()
            get_bin_content = new_hist.GetBinContent
            purities = calculate_purities( new_hist.Clone() )
            stabilities = calculate_stabilities( new_hist.Clone() )
            n_events = [int( get_bin_content( i, i ) ) for i in range( 1, len( bin_edges ) )]
            
        info['p_i'] = purities
        info['s_i'] = stabilities
        info['N'] = n_events
        
    return bin_edges, histogram_information

 
def get_next_end( histograms, bin_start, bin_end, p_min, s_min, n_min ): 
    current_bin_start = bin_start
    current_bin_end = bin_end 

    for gen_vs_reco_histogram in histograms:
        reco = asrootpy( gen_vs_reco_histogram.ProjectionX() )
        gen = asrootpy( gen_vs_reco_histogram.ProjectionY() )
        reco_i = list( reco.y() )
        gen_i = list( gen.y() )
        # keep the start bin the same but roll the end bin
        for bin_i in range ( current_bin_end, len( reco_i ) + 1 ):
            n_reco = sum( reco_i[current_bin_start:bin_i] )
            n_gen = sum( gen_i[current_bin_start:bin_i] )
            n_gen_and_reco = 0
            if bin_i < current_bin_start + 1:
                n_gen_and_reco = gen_vs_reco_histogram.Integral( current_bin_start + 1, bin_i + 1, current_bin_start + 1, bin_i + 1 )
            else:
                # this is necessary to synchronise the integral with the rebin method
                # only if the bin before is taken is is equivalent to rebinning
                # the histogram and taking the diagonal elements (which is what we want)
                n_gen_and_reco = gen_vs_reco_histogram.Integral( current_bin_start + 1, bin_i , current_bin_start + 1, bin_i )

            p, s = 0, 0
            if n_reco > 0:            
                p = round( n_gen_and_reco / n_reco, 3 )
            if n_gen > 0:
                s = round( n_gen_and_reco / n_gen, 3 )
            # find the bin range that matches
            if p >= p_min and s >= s_min and n_gen_and_reco >= n_min:
                current_bin_end = bin_i
                break
            # if it gets to the end, this is the best we can do
            current_bin_end = bin_i
    return current_bin_end, p, s, n_gen_and_reco

def print_console(info, old_purities, old_stabilities, print_old = False):
    print 'CoM =', info['CoM'], 'channel =', info['channel']
    print 'p_i =', info['p_i']
    if print_old:
        print 'p_i (old) =', old_purities
    print 's_i =', info['s_i']
    if print_old:
        print 's_i (old) =', old_stabilities
    print 'N   =', info['N']
    print '*' * 120
    
def print_latex_table( info, variable, best_binning ):
    print 'CoM =', info['CoM'], 'channel =', info['channel']
    header = """\%s bin (\GeV) &  purity & stability & number of events\\\\
    \hline""" % variable.lower()
    print header
    firstBin = 0
    lastBin = len( best_binning ) - 1
    if 'Rap' in variable :
        lastBin = len( best_binning )/2

    for i in range( firstBin, lastBin ):
        bin_range = ""
        if i == len( best_binning ) - 2:
            bin_range = '$\geq %d$' % best_binning[i]
        else:
            bin_range = '%d - %d' % ( best_binning[i], best_binning[i + 1] )
        print '%s & %.3f & %.3f & %d\\\\' % (bin_range, info['p_i'][i], info['s_i'][i], info['N'][i])
    print '\hline'
    
if __name__ == '__main__':
    main()
