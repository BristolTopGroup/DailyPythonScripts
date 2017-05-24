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

from argparse import ArgumentParser

from rootpy import asrootpy
from rootpy.io import File

import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt

import numpy as np

from dps.config.xsection import XSectionConfig
from dps.config import CMS
from dps.config.variable_binning import bin_edges_vis, minimum_bin_width, nice_bin_width
from dps.config.latex_labels import b_tag_bins_latex, variables_latex
from dps.utils.Calculation import calculate_purities, calculate_stabilities
from dps.utils.ROOT_utils import get_histogram_from_file
from dps.utils.file_utilities import make_folder_if_not_exists
from dps.utils.hist_utilities import rebin_2d, value_tuplelist_to_hist
from dps.utils.pandas_utilities import dict_to_df, df_to_file
import sys
import gc

from matplotlib import rc
rc( 'font', **CMS.font )
rc( 'text', usetex = True )

channels_latex = { 'electron':'e+jets', 'muon':'$\mu$+jets', 'combined':'e+$\mu$+jets combined' }

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
    parser.add_argument( '-C', 
        dest    = "com",
        default = 13, 
        type    = int,
        help    = "Centre of mass" 
    )
    parser.add_argument( '-V', "--variable",
        dest    = "variable_to_run",
        default =  None, 
        help    = "Variable to run" 
    )
    parser.add_argument( '-b', 
        dest    = "from_previous_binning", 
        action  = "store_true",
        help    = "Find parameters from current binning scheme" 
    )
    parser.add_argument( '-p', 
        dest    = "plotting", 
        action  = "store_true",
        help    = "Plot purity, stability and resolution" 
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
        if args.variable_to_run and variable not in args.variable_to_run: continue
        global var

        var=variable
        print('--- Doing variable',variable)
        variableToUse = variable
        if 'Rap' in variable:
            variableToUse = 'abs_%s' % variable
        histogram_information = get_histograms( measurement_config, variableToUse, args )

        # Calculate binning criteria from previous binning scheme 
        if args.from_previous_binning and args.combined:
            p, s = calculate_purity_stability(histogram_information, bin_edges_vis[variable])
            r = calculate_resolutions( variable, bin_edges = bin_edges_vis[variable], channel='combined', res_to_plot = args.plotting )

            bin_criteria = {
                'p_i' : p,
                's_i' : s,
                'res' : r,
            }
            if args.plotting:
                plotting_purity_stability(var, 'combined', bin_criteria, bin_edges_vis[var])
            f_out = 'unfolding/13TeV/binning_combined_{}.txt'.format(variable)
            df_bin = dict_to_df(bin_criteria)
            df_to_file( f_out, df_bin )
            continue

        # Claculate the best binning
        if variable == 'HT':
            best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min, minimum_bin_width[variable], nice_bin_width[variable], plot_resolution=args.plotting, x_min=120. )
        elif variable == 'ST':
            best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min, minimum_bin_width[variable], nice_bin_width[variable], plot_resolution=args.plotting, x_min=146. )
        elif variable == 'MET':
            best_binning, histogram_information = get_best_binning( histogram_information , 0.5, 0.5, n_min, minimum_bin_width[variable], nice_bin_width[variable], plot_resolution=args.plotting )
        elif variable == 'NJets':
            best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min, minimum_bin_width[variable], nice_bin_width[variable], plot_resolution=args.plotting, x_min=3.5 )
        elif variable == 'lepton_pt':
            best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min_lepton, minimum_bin_width[variable], nice_bin_width[variable], plot_resolution=args.plotting, x_min=26. )
        elif variable == 'abs_lepton_eta':
            best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min_lepton, minimum_bin_width[variable], nice_bin_width[variable], plot_resolution=args.plotting )
        elif variable == 'NJets':
            best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min, minimum_bin_width[variable], nice_bin_width[variable], plot_resolution=args.plotting, is_NJet=True)
        else:
            best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min, minimum_bin_width[variable], nice_bin_width[variable], plot_resolution=args.plotting )

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
            output_file = 'unfolding/13TeV/binningInfo_%s_%s_FullPS.txt' % ( variable, info['channel'] )
            if args.visiblePhaseSpace:
                output_file = 'unfolding/13TeV/binningInfo_%s_%s_VisiblePS.txt' % ( variable, info['channel'] )
            if args.plotting:
                plotting_purity_stability(variable, info['channel'], outputInfo, bin_choices[variable])

            df_out = dict_to_df(outputInfo)
            df_to_file( output_file, df_out )

        print('-' * 120)
        
    # # # # # # # # # # # # # # # # 
    # Plots?
    # # # # # # # # # # # # # # # # 

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


def get_best_binning( histogram_information, p_min, s_min, n_min, min_width, nice_width, x_min = None, is_NJet=False, plot_resolution=False ):
    '''
    Step 1: Change the size of the first bin until it fulfils the minimal criteria
    Step 3: Check if it is true for other channel histograms. If not back to step 2
    Step 4: Repeat step 2 & 3 until no more bins can be created
    '''
    histograms  = [info['hist'] for info in histogram_information]
    bin_edges   = []

    purities    = {}
    stabilities = {}
    resolutions = []

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
        current_bin_end, _, _, _, _ = get_next_end( histogram_information, current_bin_start, current_bin_end, p_min, s_min, n_min, min_width, nice_width, is_NJet=is_NJet)

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
        resolutions         = calculate_resolutions(  var, bin_edges=bin_edges, channel = hist_info['channel'], res_to_plot = plot_resolution )

        n_events            = [int( get_bin_content( i ) ) for i in range( 1, len( bin_edges ) )]

        # Now check if the last bin also fulfils the requirements
        if ( purities[-1] < p_min or stabilities[-1] < s_min or n_events[-1] < n_min ) and len(purities) > 3:
            # Merge last two bins 
            bin_edges[-2]   = bin_edges[-1]
            bin_edges       = bin_edges[:-1]

            # Recalculate purities and stabilites
            new_hist        = rebin_2d( hist_info['hist'], bin_edges, bin_edges ).Clone()
            purities        = calculate_purities( new_hist.Clone() )
            stabilities     = calculate_stabilities( new_hist.Clone() )
            resolutions     = calculate_resolutions(  var, bin_edges=bin_edges, channel = hist_info['channel'], res_to_plot = plot_resolution )
            n_events        = [int( get_bin_content( i ) ) for i in range( 1, len( bin_edges ) )]

        # Make sure last bin edge is also a nice rounded number
        if bin_edges[-1] % nice_width != 0:
            bin_edges[-1] = nice_width * round(bin_edges[-1]/nice_width)
            # print (bin_edges[-1], nice_width * round(bin_edges[-1]/nice_width))

        # Add purites, stabilities, n_events and resolutions to the hstogram information
        hist_info['p_i'] = purities
        hist_info['s_i'] = stabilities
        hist_info['N']   = n_events
        hist_info['res'] = resolutions

    return bin_edges, histogram_information

def get_next_end( histogram_information, bin_start, bin_end, p_min, s_min, n_min, min_width, nice_width, is_NJet=False ): 
    '''
    Getting the next bin end
    '''
    current_bin_start = bin_start
    current_bin_end = bin_end

    histograms  = [info['hist'] for info in histogram_information]
    channels  = [info['channel'] for info in histogram_information]

    for gen_vs_reco_histogram, ch in zip (histograms, channels):
        reco = asrootpy( gen_vs_reco_histogram.ProjectionX() )
        gen  = asrootpy( gen_vs_reco_histogram.ProjectionY( 'py', 1 ) )
        reco_i = list( reco.y() )
        gen_i  = list( gen.y() )

        # keep the start bin the same but roll the end bin
        for bin_i in range ( current_bin_end, len( reco_i ) + 1 ):
            x_high = reco.GetXaxis().GetBinLowEdge(bin_i)
            x_low  = reco.GetXaxis().GetBinUpEdge(current_bin_start)
            binWidth = x_high - x_low

            if binWidth < min_width:
                current_bin_end = bin_i
                continue

            # Does Not work for abs_lepton_eta with current unfolding matrices. fix in produce_unfolding_histograms should fix this.
            if reco.GetXaxis().GetBinLowEdge(bin_i+1) % nice_width > 1e-8:
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
                # Dont use resolution information on NJets 
                if is_NJet:
                    current_bin_end = bin_i
                    break

                # Now that purity and stability are statisfied... What about the resolution?
                res = calculate_resolutions( var, bin_edges=[x_low, x_high], channel = ch )
                # In the case of two bin edges being past there will only be one resolution returned
                if 2*res[0] < binWidth:
                    current_bin_end = bin_i
                    break

            # if it gets to the end, this is the best we can do
            current_bin_end = bin_i
            # And now for the next channel starting with current_bin_end.
        return current_bin_end, p, s, n_reco, res


def calculate_purity_stability(hist_infos, bin_edges):
    '''
    Rebin finebinned histograms to current binning standards
    '''
    hists = []
    for hist_info in hist_infos:
        hist = hist_info['hist']
        binned_hist = rebin_2d( hist, bin_edges, bin_edges ).Clone()
        p = calculate_purities(binned_hist)
        s = calculate_stabilities(binned_hist)
        hists.append(binned_hist)
    return p, s


def calculate_resolutions(variable, bin_edges = [], channel = 'combined', res_to_plot=False ):
    '''
    Calculate the resolutions in the bins using the residual method
    '''
    f = File( 'unfolding/13TeV/unfolding_TTJets_13TeV.root' )
    fineBinEdges_path = '{}_{}/responseVis_without_fakes'.format( variable, channel )
    fineBinEdges_hist2d = f.Get( fineBinEdges_path ).Clone()
    fineBinEdges_hist1d = asrootpy( fineBinEdges_hist2d.ProjectionX() )
    fineBinEdges = list(fineBinEdges_hist1d.xedges())
    nFineBins = len(fineBinEdges)-1

    tmp_residual_path = '{}_{}/residuals/Residuals_Bin_'.format( variable, channel )
    # Absolute lepton eta can have multiple fine bins at the same precision as wide bins. Only taking first.
    if variable == 'abs_lepton_eta': fineBinEdges = [round(entry, 2) for entry in fineBinEdges]
    
    # For N Bin edges find resolutions of bins
    resolutions = []
    for i in range(len(bin_edges)-1):  
        list_of_fine_bins = []
        # Find fine bin edges in wide bins
        for j, fine_bin_edge in enumerate(fineBinEdges):
            if fine_bin_edge >= bin_edges[i] and fine_bin_edge < bin_edges[i+1] and j < nFineBins:
                list_of_fine_bins.append(j+1)

        # Sum the residuals of the fine bins
        for fine_bin in list_of_fine_bins:
            if fine_bin == list_of_fine_bins[0]:
                fineBin_histRes = f.Get( tmp_residual_path+str(fine_bin) ).Clone()
            else:
                fineBin_histRes_tmp = f.Get( tmp_residual_path+str(fine_bin) ).Clone()
                fineBin_histRes.Add(fineBin_histRes, fineBin_histRes_tmp, 1.0, 1.0)
     
        # Get the quantile at 68% = 1 sigma = Resolution
        interval = np.array([0.])
        quantile = np.array([0.68])
        fineBin_histRes.GetQuantiles( 1, interval, quantile)
        resolutions.append(round(interval[0], 2))

        if res_to_plot:
            plotting_resolution( variable, channel, fineBin_histRes, round(interval[0], 2), bin_edges[i], bin_edges[i+1] )

    return resolutions


def plotting_purity_stability(variable, channel, binning_criteria, bin_edges ):
    '''
    Purity, stability and resolution plots.
    '''
    p = binning_criteria['p_i']
    s = binning_criteria['s_i']

    hist_stability = value_tuplelist_to_hist(s, bin_edges)
    hist_purity = value_tuplelist_to_hist(p, bin_edges)

    hist_purity.color = 'red'
    hist_stability.color = 'blue'

    hist_stability.linewidth = 4
    hist_purity.linewidth = 4

    fig = plt.figure( figsize = ( 20, 16 ), dpi = 200, facecolor = 'white' )
    axes = plt.axes()
    axes.minorticks_on()
    axes.set_xlim( [bin_edges[0], bin_edges[-1]] )
    axes.set_ylim( [0,1] )

    axes.xaxis.labelpad = 12
    axes.yaxis.labelpad = 12

    rplt.hist( hist_stability , stacked=False, axes = axes, label = 'Stability' )
    rplt.hist( hist_purity, stacked=False, axes = axes, label = 'Purity' )


    plt.tick_params( **CMS.axis_label_major )
    plt.tick_params( **CMS.axis_label_minor )

    x_title = '$' + variables_latex[variable] + '$ [GeV]'
    plt.xlabel( x_title, CMS.x_axis_title )

    leg = plt.legend(loc=4,prop={'size':40})

    plt.tight_layout()

    plot_filepath = 'plots/binning/purity_stability/'
    make_folder_if_not_exists(plot_filepath)
    plot_filename = channel + '_' + variable+'_purityStability.pdf'
    fig.savefig(plot_filepath+plot_filename, bbox_inches='tight')


def plotting_resolution(variable, channel, residual, resolution, bin_low, bin_high ):
    '''
    Resolution plots.
    '''
    bin_width = bin_high - bin_low
    title = "channel = {}, variable = ${}$, {}-{}".format(channel, variable, bin_low, bin_high)

    fig = plt.figure()
    axes = plt.axes()
    rplt.hist(residual, axes = axes, label = 'Residuals')
    plt.axvline(x=resolution, linewidth=1, color='r', label = 'Resolution')
    plt.axvline(x=bin_width/2, linewidth=1, color='blue', label = 'Bin Width')

    axes.set_ylim(ymin = 0)
    # axes.set_yscale("log", nonposy='clip')
    axes.set_xlabel('Residual')
    axes.set_ylabel('N')
    fig.suptitle('Residual Distribution', fontsize=14, fontweight='bold')
    plt.title(title, loc='right')

    leg = plt.legend(loc='best')
    leg.draw_frame(False)   

    plt.tight_layout()

    plot_filepath = 'plots/binning/residuals/'
    make_folder_if_not_exists(plot_filepath)
    plot_filename = '{}_{}_{}-{}_Residual.pdf'.format(channel, variable, str(bin_low), str(bin_high))
    fig.savefig(plot_filepath+plot_filename, bbox_inches='tight')
    fig.clf()
    plt.close()
    gc.collect()
    return


if __name__ == '__main__':
    main()
