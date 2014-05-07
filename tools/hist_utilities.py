'''
Created on 20 Nov 2012

@author: kreczko
'''
from __future__ import division
from rootpy.plotting import Hist, Graph
from rootpy import asrootpy
from ROOT import TGraphAsymmErrors
from array import array
from itertools import izip
from rootpy.plotting.hist import Hist2D
import random
import string
from cmath import sqrt

def hist_to_value_error_tuplelist( hist ):
    values = list( hist.y() )
    errors = []
    add_error = errors.append
    get_bin_error = hist.GetBinError
    for bin_i in range( len( values ) ):
        add_error( get_bin_error( bin_i + 1 ) )
    return zip( values, errors )

def values_and_errors_to_hist( values, errors, bins ):
    assert( len( values ) == len( bins ) )
    if len( errors ) == 0:
        errors = [0.] * len( values )
    value_error_tuplelist = zip( values, errors )
    return value_error_tuplelist_to_hist( value_error_tuplelist, bins )

def value_errors_tuplelist_to_graph( value_errors_tuplelist, bin_edges ):
    value_error_tuplelist = [( value, 0 ) for value, lower_error, upper_error in value_errors_tuplelist]
    hist = value_error_tuplelist_to_hist( value_error_tuplelist, bin_edges )
    rootpy_graph = asrootpy( TGraphAsymmErrors( hist ) ) 
#    rootpy_graph = Graph(hist = hist)
    set_lower_error = rootpy_graph.SetPointEYlow
    set_upper_error = rootpy_graph.SetPointEYhigh
    
    for point_i, ( value, lower_error, upper_error ) in enumerate( value_errors_tuplelist ):
        set_lower_error( point_i, lower_error )
        set_upper_error( point_i, upper_error )
        
    return rootpy_graph

def graph_to_value_errors_tuplelist( graph ):
    values = list( graph.y() )
    errors_high = list( graph.yerrh() )
    errors_low = list( graph.yerrl() )
    value_error_tuplelist = zip( values, errors_low, errors_high )
    return value_error_tuplelist

def value_error_tuplelist_to_hist( value_error_tuplelist, bin_edges ):
    assert( len( bin_edges ) == len( value_error_tuplelist ) + 1 )
    rootpy_hist = Hist( bin_edges, type = 'D' )
    set_bin_value = rootpy_hist.SetBinContent
    set_bin_error = rootpy_hist.SetBinError
    for bin_i, ( value, error ) in enumerate( value_error_tuplelist ):
        set_bin_value( bin_i + 1, value )
        set_bin_error( bin_i + 1, error )
    return rootpy_hist

def value_tuplelist_to_hist( value_tuplelist, bin_edges ):
    assert( len( bin_edges ) == len( value_tuplelist ) + 1 )
    rootpy_hist = Hist( bin_edges, type = 'D' )
    set_bin_value = rootpy_hist.SetBinContent
    for bin_i, value in enumerate( value_tuplelist ):
        set_bin_value( bin_i + 1, value )
    return rootpy_hist

def sum_histograms( histogram_dict, sample_list ):
    # histogram_dict = {sample:{histogram_name:histogram}
    summary = {}
    preparation = {}
    for sample in sample_list:
        sample_hists = histogram_dict[sample]
        for histogram_name, histogram in sample_hists.iteritems():
            if not preparation.has_key( histogram_name ):
                preparation[histogram_name] = []
            preparation[histogram_name].append( histogram )
    for histogram_name, histogram_list in preparation.iteritems():
        summary[histogram_name] = sum( histogram_list )
    return summary

def scale_histogram_errors( histogram, total_error ):
    bins_number = histogram.GetNbinsX()
    current_total_error = sum( histogram.yerravg() )
    scale_factor = total_error / current_total_error
    
    for bin_i in range( bins_number ):
        histogram.SetBinError( bin_i + 1, scale_factor * histogram.GetBinError( bin_i + 1 ) )

def prepare_histograms( histograms, rebin = 1, scale_factor = 1., normalisation = {}, exclude_from_scaling = ['data'] ):
    for sample, histogram_dict in histograms.iteritems():
        for _, histogram in histogram_dict.iteritems():
            histogram.Rebin( rebin )
            if not sample in exclude_from_scaling:
                histogram.Scale( scale_factor )
            if normalisation != {} and histogram.Integral() != 0:
                if sample == 'TTJet':
                    histogram.Scale( normalisation['TTJet'][0] / histogram.Integral() )
                    scale_histogram_errors( histogram, normalisation['TTJet'][1] )
                if sample == 'SingleTop':
                    histogram.Scale( normalisation['SingleTop'][0] / histogram.Integral() )
                    scale_histogram_errors( histogram, normalisation['SingleTop'][1] )
                if sample == 'V+Jets':
                    histogram.Scale( normalisation['V+Jets'][0] / histogram.Integral() )
                    scale_histogram_errors( histogram, normalisation['V+Jets'][1] )
                if sample == 'QCD':
                    histogram.Scale( normalisation['QCD'][0] / histogram.Integral() )
                    scale_histogram_errors( histogram, normalisation['QCD'][1] )

def rebin_asymmetric( histogram, bins ):
    bin_array = array( 'd', bins )
    nbins = len( bin_array ) - 1
    new_histogram = histogram.Rebin( nbins, histogram.GetName() + 'new', bin_array )
    return asrootpy( new_histogram )

def spread_x( histograms, bin_edges ):
    """
        Usually when plotting multiple histograms with same x-values and 
        similar y-values their markers will overlap. This function spreads
        the data points across a bin. It creates a set of graphs with the
        same y-values but different x.
        
        @param histograms: list of histograms with same binning
        @param bin_edges: the bin edges of the histograms 
    """
    # construct bins from the bin edges
    bins = [( bin_lower, bin_upper ) for bin_lower, bin_upper in izip( bin_edges[:-1], bin_edges[1:] )]
    # now get the bin widths
    bin_widths = [abs( bin_i[1] - bin_i[0] ) for bin_i in bins]
    # number of histograms
    number_of_hists = len( histograms )
    # and divide the bins into equidistant bits leaving some space to the bin edges
    x_locations = []
    add_locations = x_locations.append
    for bin_lower, width in izip( bin_edges, bin_widths ):
        x_step = width / ( 1.0 * number_of_hists + 1 )  # +1 due to spacing to bin edge
        add_locations( [bin_lower + n * x_step for n in range( 1, number_of_hists + 1 )] )
    
    # transpose
    x_locations = map( list, zip( *x_locations ) )
    
    graphs = []
    for histogram, x_coordinates in zip( histograms, x_locations ):
        g = Graph( histogram )
        for i, ( x, y ) in enumerate( zip( x_coordinates, histogram.y() ) ):
            g.SetPoint( i, x, y )
        
        graphs.append( g )
        
    return graphs

def limit_range_y( histogram ):
    """
        Calculates the minimum and maximum values of the histogram y values
        Can be useful for setting limits of log plots
    """
    tuple_list = hist_to_value_error_tuplelist( histogram )
    min_value = map( min, zip( *tuple_list ) )[0]
    max_value = map( max, zip( *tuple_list ) )[0]
    return min_value, max_value

def fix_overflow( hist ):
    ''' Moves entries from the overflow bin into the last bin as we treat the last bin as everything > last_bin.lower_edge.
    This is to fix a bug in the unfolding workflow where we neglect this treatment.'''
    
    if 'TH1' in hist.class_name():
        last_bin = hist.nbins()
        overflow_bin = last_bin + 1
        overflow = hist.GetBinContent( overflow_bin )
        overflow_error= hist.GetBinError( overflow_bin )
        
        new_last_bin_content = hist.GetBinContent( last_bin ) + overflow
        new_last_bin_error = hist.GetBinError( last_bin ) + overflow_error
        
        hist.SetBinContent( last_bin, new_last_bin_content )
        hist.SetBinError( last_bin, new_last_bin_error )
        hist.SetBinContent( overflow_bin, 0. )
    elif 'TH2' in hist.class_name():
        last_bin_x = hist.nbins()
        last_bin_y = hist.nbins( axis = 1 )
        overflow_bin_x = last_bin_x + 1
        overflow_bin_y = last_bin_y + 1
        # first all y-overflow
        for x in range( 1, overflow_bin_x +1):
            overflow_y = hist.GetBinContent( x, overflow_bin_y )
            overflow_error_y = hist.GetBinError( x, overflow_bin_y )
            
            last_bin_content_y = hist.GetBinContent( x, last_bin_y )
            last_bin_error_y = hist.GetBinError( x, last_bin_y )
            
            hist.SetBinContent( x, overflow_bin_y, 0. )
            hist.SetBinContent( x, last_bin_y, overflow_y + last_bin_content_y )
            hist.SetBinError( x, last_bin_y, overflow_error_y + last_bin_error_y )
        # now all x-overflow
        for y in range( 1, overflow_bin_y +1):
            overflow_x = hist.GetBinContent( overflow_bin_x, y )
            overflow_error_x = hist.GetBinError( overflow_bin_x, y )
            
            last_bin_content_x = hist.GetBinContent( last_bin_x, y )
            last_bin_error_x = hist.GetBinError( last_bin_x, y )
            
            hist.SetBinContent( overflow_bin_x, y, 0. )
            hist.SetBinContent( last_bin_x, y, overflow_x + last_bin_content_x )
            hist.SetBinError( last_bin_x, y, overflow_error_x + last_bin_error_x )
        # and now the final bin (both x and y overflow)
        overflow_x_y = hist.GetBinContent( overflow_bin_x, overflow_bin_y )
        last_bin_content_x_y = hist.GetBinContent( last_bin_x, last_bin_y )
        hist.SetBinContent( overflow_bin_x, overflow_bin_y, 0. )
        hist.SetBinContent( last_bin_x, last_bin_y, overflow_x_y + last_bin_content_x_y )
    else:
        raise Exception("Unknown type of histogram in fix_overflow")

    hist = transfer_values_without_overflow(hist)
    return hist

def transfer_values_without_overflow( histogram ):
    if histogram == None:
        return histogram
    
    histogram_new = None
    if 'TH1' in histogram.class_name():
        histogram_new = Hist( list( histogram.xedges() ), type = 'D' ) 
        n_bins = histogram_new.nbins()
        for i in range(1, n_bins + 1):
            histogram_new.SetBinContent(i, histogram.GetBinContent(i))
            histogram_new.SetBinError(i, histogram.GetBinError(i))
    elif 'TH2' in histogram.class_name():
        histogram_new = Hist2D( list( histogram.xedges() ), list( histogram.yedges() ), type = 'D' )
        n_bins_x = histogram_new.nbins()
        n_bins_y = histogram_new.nbins(axis=1)
        for i in range(1, n_bins_x + 1):
            for j in range(1, n_bins_y + 1):
                histogram_new.SetBinContent(i,j, histogram.GetBinContent(i, j))
                histogram_new.SetBinError(i,j, histogram.GetBinError(i, j))
    else:
        raise Exception("Unknown type of histogram in transfer_values_without_overflow")
    
    return histogram_new
    
def rebin_2d( hist_2D, bin_edges_x, bin_edges_y ):
    # since there is no easy way to rebin a 2D histogram, lets make it from 
    # scratch
    random_string = ''.join( random.choice( string.ascii_uppercase + string.digits ) for _ in range( 6 ) )
    hist = Hist2D( bin_edges_x, bin_edges_y, name = hist_2D.GetName() + '_rebinned_' + random_string )  
    n_bins_x = hist_2D.nbins()
    n_bins_y = hist_2D.nbins( axis = 1 )
    
    fill = hist.Fill
    get = hist_2D.GetBinContent
    x_axis_centre = hist_2D.GetXaxis().GetBinCenter
    y_axis_centre = hist_2D.GetYaxis().GetBinCenter
    for i in range( 1, n_bins_x + 1 ):
        for j in range( 1, n_bins_y + 1 ):
            fill( x_axis_centre( i ), y_axis_centre( j ), get( i, j ) )
    
    return hist

if __name__ == '__main__':
    value_error_tuplelist = [( 0.006480446927374301, 0.0004647547547401945 ),
                             ( 0.012830288388947605, 0.0010071677178938234 ),
                             ( 0.011242639287332025, 0.000341258792551077 ),
                             ( 0.005677185565453722, 0.00019082371879446718 ),
                             ( 0.0008666767325985203, 5.0315979327182054e-05 )]
    hist = value_error_tuplelist_to_hist( value_error_tuplelist, bin_edges = [0, 25, 45, 70, 100, 300] )
    import rootpy.plotting.root2matplotlib as rplt
    import matplotlib.pyplot as plt
    plt.figure( figsize = ( 16, 10 ), dpi = 100 )
    plt.figure( 1 )
    rplt.errorbar( hist, label = 'test' )
    plt.xlabel( 'x' )
    plt.ylabel( 'y' )
    plt.title( 'Testing' )
    plt.legend( numpoints = 1 )
    plt.savefig( 'Array2Hist.png' )
    plt.close()
      
    value_errors_tuplelist = [( 0.006480446927374301, 0.0004647547547401945, 0.0004647547547401945 * 2 ),
                             ( 0.012830288388947605, 0.0010071677178938234, 0.0010071677178938234 * 2 ),
                             ( 0.011242639287332025, 0.000341258792551077 * 2, 0.000341258792551077 ),
                             ( 0.005677185565453722, 0.00019082371879446718 * 2, 0.00019082371879446718 ),
                             ( 0.0008666767325985203, 5.0315979327182054e-05, 5.0315979327182054e-05 )]
    hist = value_errors_tuplelist_to_graph( value_errors_tuplelist, bin_edges = [0, 25, 45, 70, 100, 300] )
    tuplelist = graph_to_value_errors_tuplelist( hist )
    assert tuplelist == value_errors_tuplelist
  
    plt.figure( figsize = ( 16, 10 ), dpi = 100 )
    plt.figure( 1 )
    rplt.errorbar( hist, label = 'test2' )
    plt.xlabel( 'x' )
    plt.ylabel( 'y' )
    plt.title( 'Testing' )
    plt.legend( numpoints = 1 )
    plt.savefig( 'Array2Graph.png' )
