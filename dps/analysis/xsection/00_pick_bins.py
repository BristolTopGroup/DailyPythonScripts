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
from __future__ import print_function
from rootpy import asrootpy
from rootpy.io import File
from dps.utils.Calculation import calculate_purities, calculate_stabilities
from dps.utils.hist_utilities import rebin_2d
from dps.config.xsection import XSectionConfig
from argparse import ArgumentParser
from dps.config.variable_binning import bin_edges_full, minimum_bin_width
from dps.utils.file_utilities import write_data_to_JSON
from ROOT import TH1, TCanvas, TLine, gDirectory, TObjArray, TColor, TLegend

import dps.utils.resolution as rs

def main():
    '''
    Step 1: Get the 2D histogram for every sample (channel and/or centre of mass energy)
    Step 2: Change the size of the first bin until it fulfils the minimal criteria
    Step 3: Check if it is true for all other histograms. If not back to step 2
    Step 4: Repeat step 2 & 3 until no mo bins can be created
    '''
    parser = ArgumentParser()
    parser.add_argument( '-v', 
        dest    = "visiblePhaseSpace", 
        action  = "store_true",
        help    = "Consider visible phase space or not" 
    )
    parser.add_argument( '-c', 
        dest    = "combined", 
        action  = "store_true",
        help    = "Combine channels" 
    )
    parser.add_argument( '-r', 
        dest    = "redo_resolution", 
        action  = "store_true",
        help    = "Recalculate the resolution plots" 
    )
    args = parser.parse_args()

    measurement_config = XSectionConfig(13)

    # Initialise binning parameters
    bin_choices = {}

    # Min Purity and Stability
    p_min = 0.6
    s_min = 0.6
    # 0.5 for MET

    # Min events in bin for appropriate stat unc
    # error = 1/sqrt(N) [ unc=5% : (1/0.05)^2 = 400]
    n_min = 500
    n_min_lepton = 500
     
    variables = measurement_config.variables
    for variable in variables:
        global var
        var=variable
        print('--- Doing variable',variable)
        variableToUse = variable
        if 'Rap' in variable:
            variableToUse = 'abs_%s' % variable
        histogram_information = get_histograms( measurement_config, variableToUse, args )

        # Remake the resolution plots from the fine binned unfolding matrix
        if args.redo_resolution:
            rs.generate_resolution_plots(histogram_information, variable)

        # Claculate the best binning
        if variable == 'HT':
            best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min, minimum_bin_width[variable], x_min=100. )
        elif variable == 'ST':
            best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min, minimum_bin_width[variable], x_min=123. )
        elif variable == 'MET':
            best_binning, histogram_information = get_best_binning( histogram_information , 0.5, 0.5, n_min, minimum_bin_width[variable] )
        elif variable == 'NJets':
            best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min, minimum_bin_width[variable], x_min=3.5 )
        elif variable == 'lepton_pt':
            best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min_lepton, minimum_bin_width[variable], x_min=23. )
        elif variable == 'abs_lepton_eta':
            best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min_lepton, minimum_bin_width[variable] )
        elif variable == 'NJets':
            best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min, minimum_bin_width[variable], is_NJet=True)
        else:
            best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min, minimum_bin_width[variable] )

        # Symmetric binning for lepton_eta
        if 'Rap' in variable:
            for b in list(best_binning):
                if b != 0.0:
                    best_binning.append(-1.0*b)
            best_binning.sort()

        # Make last bin smaller if huge
        # Won't change final results
        if len(best_binning) >= 4:
            lastBinWidth = best_binning[-1] - best_binning[-2]
            penultimateBinWidth = best_binning[-2] - best_binning[-3]
            if lastBinWidth / penultimateBinWidth > 5:
                newLastBinWidth = penultimateBinWidth * 5
                best_binning[-1] = best_binning[-2] + newLastBinWidth

        # Smooth bin edges
        if variable == 'abs_lepton_eta':
            best_binning = [ round(i,2) for i in best_binning ]
        elif variable != 'NJets' :
            best_binning = [ round(i) for i in best_binning ]

        bin_choices[variable] = best_binning

        # Print the best binning to screen and JSON
        print('The best binning for', variable, 'is:')
        print('bin edges =', best_binning)
        print('N_bins    =', len( best_binning ) - 1)
        print('The corresponding purities and stabilities are:')
        for info in histogram_information:
            outputInfo = {}
            outputInfo['p_i'] = info['p_i']
            outputInfo['s_i'] = info['s_i']
            outputInfo['N']   = info['N']
            outputInfo['res'] = info['res']
            outputJsonFile = 'unfolding/13TeV/binningInfo_%s_%s_FullPS.txt' % ( variable, info['channel'] )
            if args.visiblePhaseSpace:
                outputJsonFile = 'unfolding/13TeV/binningInfo_%s_%s_VisiblePS.txt' % ( variable, info['channel'] )
            write_data_to_JSON( outputInfo, outputJsonFile )
            print_latex_table(info, variable, best_binning)
        for key in outputInfo:
            print (key,outputInfo[key])
        print('-' * 120)

    # Final print of all binnings to screen
    print('=' * 120)
    print('For config/variable_binning.py')
    print('=' * 120)
    for variable in bin_choices:
        print('\''+variable+'\' : '+str(bin_choices[variable])+',')

def get_histograms( config, variable, args ):
    '''
    Return a dictionary of the unfolding histogram informations (inc. hist)
    '''
    path_electron   = ''
    path_muon       = ''
    path_combined   = ''    
    histogram_name  = 'response_without_fakes'
    if args.visiblePhaseSpace:
        histogram_name = 'responseVis_without_fakes'

    path_electron = '%s_electron/%s' % ( variable, histogram_name )
    path_muon     = '%s_muon/%s'     % ( variable, histogram_name )
    path_combined = '%s_combined/%s' % ( variable, histogram_name )

    histogram_information = [
        {
            'file'    : config.unfolding_central_raw,
            'CoM'     : 13,
            'path'    : path_electron,
            'channel' :'electron'
        },
        {
            'file'    : config.unfolding_central_raw,
            'CoM'     : 13,
            'path'    : path_muon,
            'channel' :'muon'
        },
    ]
    
    if args.combined:
        histogram_information = [
            {
                'file'    : config.unfolding_central_raw,
                'CoM'     : 13,
                'path'    : path_combined,
                'channel' : 'combined'
            },
        ]

    for histogram in histogram_information:
        lumiweight = 1
        f = File( histogram['file'] )
        histogram['hist'] = f.Get( histogram['path'] ).Clone()

        # scale to current lumi
        lumiweight = config.luminosity_scale
        if round(lumiweight, 1) != 1.0:
            print( "Scaling to {}".format(lumiweight) )
        histogram['hist'].Scale( lumiweight )

        # change scope from file to memory
        histogram['hist'].SetDirectory( 0 )
        f.close()

    return histogram_information


def get_best_binning( histogram_information, p_min, s_min, n_min, min_width, x_min = None, is_NJet=False ):
    '''
    Step 1: Change the size of the first bin until it fulfils the minimal criteria
    Step 3: Check if it is true for other channel histograms. If not back to step 2
    Step 4: Repeat step 2 & 3 until no more bins can be created
    '''
    histograms  = [info['hist'] for info in histogram_information]
    bin_edges   = []
    resolutions = []
    purities    = {}
    stabilities = {}
    
    current_bin_start = 0
    current_bin_end = 0
        
    first_hist = histograms[0]
    n_bins     = first_hist.GetNbinsX()

    # Start at minimum x instead of 0
    if x_min:
        current_bin_start = first_hist.ProjectionX().FindBin(x_min) - 1
        current_bin_end = current_bin_start
    
    # Calculate the bin edges until no more bins can be iterated over
    while current_bin_end < n_bins:
        # Return the next bin end + (p, s, N_reco, res)
        current_bin_end, _, _, _, r = get_next_end( histograms, current_bin_start, current_bin_end, p_min, s_min, n_min, min_width, is_NJet=is_NJet )
        resolutions.append(r)

        # Attach first bin low edge
        if not bin_edges:
            bin_edges.append( first_hist.GetXaxis().GetBinLowEdge( current_bin_start + 1 ) )
        # Attachs the current bin end edge
        bin_edges.append( first_hist.GetXaxis().GetBinLowEdge( current_bin_end ) + first_hist.GetXaxis().GetBinWidth( current_bin_end ) )
        current_bin_start = current_bin_end

    # add the purity and stability values for the final binning
    for hist_info in histogram_information:
        new_hist            = rebin_2d( hist_info['hist'], bin_edges, bin_edges ).Clone( hist_info['channel'] + '_' + str( hist_info['CoM'] ) )
        get_bin_content     = new_hist.ProjectionX().GetBinContent
        purities            = calculate_purities( new_hist.Clone() )
        stabilities         = calculate_stabilities( new_hist.Clone() )
        n_events            = [int( get_bin_content( i ) ) for i in range( 1, len( bin_edges ) )]

        # Now check if the last bin also fulfils the requirements
        if ( purities[-1] < p_min or stabilities[-1] < s_min or n_events[-1] < n_min ) and len(purities) > 3:
            # Merge last two bins 
            bin_edges[-2]   = bin_edges[-1]
            bin_edges       = bin_edges[:-1]
            # Merge the resolutions in the last bins
            resolutions[-2] = (resolutions[-2]+resolutions[-1]) / 2
            resolutions     = resolutions[:-1]
            # Recalculate purities and stabilites
            new_hist        = rebin_2d( hist_info['hist'], bin_edges, bin_edges ).Clone()
            purities        = calculate_purities( new_hist.Clone() )
            stabilities     = calculate_stabilities( new_hist.Clone() )
            n_events        = [int( get_bin_content( i ) ) for i in range( 1, len( bin_edges ) )]

        # Add purites, stabilities, n_events and resolutions to the hstogram information
        hist_info['p_i'] = purities
        hist_info['s_i'] = stabilities
        hist_info['N'] = n_events
        hist_info['res'] = resolutions

    return bin_edges, histogram_information

def get_next_end( histograms, bin_start, bin_end, p_min, s_min, n_min, min_width, is_NJet=False ): 
    '''
    Getting the next bin end
    '''
    current_bin_start = bin_start
    current_bin_end = bin_end

    for gen_vs_reco_histogram in histograms:
        reco = asrootpy( gen_vs_reco_histogram.ProjectionX() )
        gen  = asrootpy( gen_vs_reco_histogram.ProjectionY( 'py', 1 ) )
        reco_i = list( reco.y() )
        gen_i  = list( gen.y() )

        # keep the start bin the same but roll the end bin
        for bin_i in range ( current_bin_end, len( reco_i ) + 1 ):
            x_high = reco.GetXaxis().GetBinLowEdge(bin_i)
            x_mid  = reco.GetXaxis().GetBinCenter(int( (current_bin_start+current_bin_end)/2 ) )
            x_low  = reco.GetXaxis().GetBinUpEdge(current_bin_start)
            binWidth = x_high - x_low

            if binWidth < min_width:
                current_bin_end = bin_i
                continue

            n_reco = sum( reco_i[current_bin_start:bin_i] )
            n_gen  = sum( gen_i[current_bin_start:bin_i] )
            n_gen_and_reco = 0

            if bin_i < current_bin_start + 1:
                n_gen_and_reco = gen_vs_reco_histogram.Integral( current_bin_start + 1, bin_i + 1, current_bin_start + 1, bin_i + 1 )
            else:
                # this is necessary to synchronise the integral with the rebin method
                # only if the bin before is taken is is equivalent to rebinning
                # the histogram and taking the diagonal elements (which is what we want)
                n_gen_and_reco = gen_vs_reco_histogram.Integral( current_bin_start + 1, bin_i , current_bin_start + 1, bin_i )

            p, s, res = 0, 0, 99
            if n_reco > 0:            
                p = round( n_gen_and_reco / n_reco, 3 )
            if n_gen > 0:
                s = round( n_gen_and_reco / n_gen, 3 )

            # find the bin range that matches
            if p >= p_min and s >= s_min and n_reco >= n_min:
                # Now that purity and stability are statisfied... What about the resolution?

                # Dont use resolution information on NJets 
                if is_NJet:
                    current_bin_end = bin_i
                    break

                # Choose the middle fine bin of the total bin width as the resolution
                res = rs.get_merged_bin_resolution('plots/resolutionStudies/resolution.root', var, x_low, x_high)
                res = round( res, 3 )
                if ( x_high - x_mid > res and x_mid - x_low > res ):
                    current_bin_end = bin_i
                    break

            # if it gets to the end, this is the best we can do
            current_bin_end = bin_i
            # And now for the next channel starting with current_bin_end.
    return current_bin_end, p, s, n_reco, res

def print_console(info, old_purities, old_stabilities, print_old = False):
    print('CoM =', info['CoM'], 'channel =', info['channel'])
    print('p_i =', info['p_i'])
    if print_old:
        print('p_i (old) =', old_purities)
    print('s_i =', info['s_i'])
    if print_old:
        print('s_i (old) =', old_stabilities)
    print('N   =', info['N'])
    print('*' * 120)
    
def print_latex_table( info, variable, best_binning ):
    print('CoM =', info['CoM'], 'channel =', info['channel'])
    header = """\{var} bin (\GeV) &  purity & stability & resolution & number of events\\\\
    \hline""".format(var=variable)
    print(header)
    firstBin = 0
    lastBin = len( best_binning ) - 1
    if 'Rap' in variable :
        lastBin = len( best_binning )/2

    for i in range( firstBin, lastBin ):
        bin_range = ""
        if i == len( best_binning ) - 2:
            bin_range = '$\geq %d$' % best_binning[i]
        else:
            bin_range = '{start} - {end}'.format(start=best_binning[i],end=best_binning[i + 1] )
            if 'abs_lepton_eta' in variable:
                bin_range = '{start} - {end}'.format(start=best_binning[i],end=best_binning[i + 1] )
        print('%s & %.3f & %.3f & %.3f & %d\\\\' % (bin_range, info['p_i'][i], info['s_i'][i], info['res'][i], info['N'][i]))
    print('\hline')
    
if __name__ == '__main__':
    main()
