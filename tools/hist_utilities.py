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
from copy import deepcopy
from tools.file_utilities import read_data_from_JSON
from tools.logger import log
hu_log = log["tools/hist_utilities"]

def hist_to_value_error_tuplelist( hist ):
    values = list( hist.y() )
    errors = []
    add_error = errors.append
    get_bin_error = hist.GetBinError
    for bin_i in range( len( values ) ):
        add_error( get_bin_error( bin_i + 1 ) )
    return zip( values, errors )

def values_and_errors_to_hist( values, errors, bins ):
    assert( len( bins ) == len( values ) + 1 )
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

@hu_log.trace()
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

def prepare_histograms( histograms, rebin = 1, scale_factor = 1.,
                        normalisation = {}, exclude_from_scaling = ['data'] ):
    for sample, histogram_dict in histograms.iteritems():
        # check if this is a simple dict
        if histogram_dict.__class__.__name__ == 'Hist':
            h = histogram_dict
            scale = 1.
            norm = None
            if not sample in exclude_from_scaling:
                scale = scale_factor
            if sample in normalisation.keys():
                norm = normalisation[sample]
            scale_and_rebin_histogram( histogram = h, scale_factor = scale,
                                      normalisation = norm, rebin = rebin )
            continue
        # otherwise go a level deeper
        for _, histogram in histogram_dict.iteritems():
            scale = 1.
            norm = None
            if not sample in exclude_from_scaling:
                scale = scale_factor
            if sample in normalisation.keys():
                norm = normalisation[sample]
            scale_and_rebin_histogram( histogram = histogram,
                                       scale_factor = scale,
                                       normalisation = norm, rebin = rebin )

def scale_and_rebin_histogram(histogram, scale_factor,
                              normalisation = None,
                              rebin = 1):
    histogram.Rebin( rebin )
    histogram.Scale( scale_factor )
    if not normalisation is None and histogram.Integral() != 0:
        histogram.Scale( normalisation[0] / histogram.Integral() )
        scale_histogram_errors( histogram, normalisation[1] )

def rebin_asymmetric( histogram, bins ):
    bin_array = array( 'd', bins )
    nbins = len( bin_array ) - 1
    new_histogram = histogram.Rebin( nbins, histogram.GetName() + 'new', bin_array )
    return asrootpy( new_histogram )

@hu_log.trace()
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
    for i in range( 0, n_bins_x + 1 ):
        for j in range( 0, n_bins_y + 1 ):
            fill( x_axis_centre( i ), y_axis_centre( j ), get( i, j ) )

    return hist

def conditional_rebin( histogram, bin_edges ):
    histogram_ = deepcopy(histogram)
    current_nbins = histogram.nbins()
    new_nbins = len( bin_edges ) - 1
    # check if already have the correct number of bins
    if not current_nbins == new_nbins:
        # check if re-binning is possible (simple way)
        if current_nbins > new_nbins:
            histogram_ = histogram_.rebinned( bin_edges, axis = 0 )
            if 'TH2' in histogram_.class_name():
                histogram_ = histogram_.rebinned( bin_edges, axis = 1 )
    return histogram_

def clean_control_region(histograms = {},
                         data_label = 'data',
                         subtract = [],
                         fix_to_zero = True):
    '''This function takes a dictionary of histograms (sample_name:histogram)
     and will subtract all samples given in the parameter "subtract" from the
     data distribution.
     '''
    data_hist = deepcopy(histograms[data_label])
    # first subtract all necessary samples
    for sample, histogram in histograms.iteritems():
        if sample in subtract:
            data_hist -= histogram
    # next make sure there are no negative events
    if fix_to_zero:
        for bin_i, y in enumerate(data_hist.y(overflow=True)):
            if y < 0:
                data_hist.SetBinContent(bin_i, 0)
                # add the difference to 0 to the existing error
                data_hist.SetBinError(bin_i, data_hist.GetBinError(bin_i) + abs(y))
    return data_hist

def adjust_overflow_to_limit(histogram, x_min, x_max):
    ''' Adjust the first and last bin of the histogram such that it becomes
    the new under- and overflow bin'''
    # get the bin before x_min
    histogram_ = deepcopy(histogram)
    underflow_bin = histogram_.FindBin(x_min)
    overflow_bin = histogram_.FindBin(x_max)
    n_bins = histogram_.nbins()
    underflow, underflow_error = 0, 0
    overflow, overflow_error = 0, 0
    if not underflow_bin < 1:
        underflow, underflow_error = histogram_.integral(0, underflow_bin, error=True)
        for i in range(underflow_bin + 1):
            histogram_.SetBinContent(i, 0)
            histogram_.SetBinError(i, 0)

    if not overflow_bin > n_bins:
        overflow, overflow_error = histogram_.integral(overflow_bin, n_bins + 1, error=True)
        for i in range(overflow_bin, n_bins + 2):
            histogram_.SetBinContent(i, 0)
            histogram_.SetBinError(i, 0)

    histogram_.SetBinContent(underflow_bin, underflow)
    histogram_.SetBinError(underflow_bin, underflow_error)
    histogram_.SetBinContent(overflow_bin, overflow)
    histogram_.SetBinError(overflow_bin, overflow_error)

    return histogram_

def get_fitted_normalisation( variable, channel, path_to_JSON, category, met_type ):
    '''
    This function now gets the error on the fit correctly,
    so that it can be applied if the --normalise_to_fit option is used
    '''
    import config.variable_binning
    variable_bins_ROOT = config.variable_binning.variable_bins_ROOT 
    fit_results = read_data_from_JSON( path_to_JSON + variable + '/fit_results/' + category + '/fit_results_' + channel + '_' + met_type + '.txt' )

    N_fit_ttjet = [0, 0]
    N_fit_singletop = [0, 0]
    N_fit_vjets = [0, 0]
    N_fit_qcd = [0, 0]

    bins = variable_bins_ROOT[variable]
    for bin_i, _ in enumerate( bins ):
        # central values
        N_fit_ttjet[0] += fit_results['TTJet'][bin_i][0]
        N_fit_singletop[0] += fit_results['SingleTop'][bin_i][0]
        N_fit_vjets[0] += fit_results['V+Jets'][bin_i][0]
        N_fit_qcd[0] += fit_results['QCD'][bin_i][0]

        # errors
        N_fit_ttjet[1] += fit_results['TTJet'][bin_i][1]
        N_fit_singletop[1] += fit_results['SingleTop'][bin_i][1]
        N_fit_vjets[1] += fit_results['V+Jets'][bin_i][1]
        N_fit_qcd[1] += fit_results['QCD'][bin_i][1]

    fitted_normalisation = {
                'TTJet': N_fit_ttjet,
                'SingleTop': N_fit_singletop,
                'V+Jets': N_fit_vjets,
                'QCD': N_fit_qcd
                }
    return fitted_normalisation

def get_data_derived_qcd( control_hists, qcd_exclusive_hist ):
    '''
    Retrieves the data-driven QCD template and normalises it to MC prediction.
    It uses the inclusive template (across all variable bins) and removes other processes
    before normalising the QCD template.
    '''

    dataDerived_qcd = clean_control_region( control_hists, subtract = ['TTJet', 'V+Jets', 'SingleTop'] )
    normalisation_QCDdata = dataDerived_qcd.integral( overflow = True )
    normalisation_exclusive = qcd_exclusive_hist.integral( overflow = True )

    scale = 1.
    if not normalisation_QCDdata == 0:
        if not normalisation_exclusive == 0:
            scale = 1 / normalisation_QCDdata * normalisation_exclusive
        else:
            scale = 1 / normalisation_QCDdata
    dataDerived_qcd.Scale( scale )
    return dataDerived_qcd

def get_normalisation_error( normalisation ):
    total_normalisation = 0.
    total_error = 0.
    for _, number in normalisation.iteritems():
        total_normalisation += number[0]
        total_error += number[1]
    return total_error / total_normalisation

def get_fit_results_histogram( data_path = 'data/M3_angle_bl',
                               centre_of_mass = 8,
                               channel = 'electron',
                               variable = 'MET',
                               met_type = 'patType1CorrectedPFMet',
                               bin_edges = [] ):
    fit_result_input = data_path + '/%(CoM)dTeV/%(variable)s/fit_results/central/fit_results_%(channel)s_%(met_type)s.txt'
    fit_results = read_data_from_JSON( fit_result_input % {'CoM': centre_of_mass, 'channel': channel, 'variable': variable, 'met_type':met_type} )
    fit_data = fit_results['TTJet']
    h_data = value_error_tuplelist_to_hist( fit_data, bin_edges )
    return h_data

def get_histogram_ratios(nominator, denominators, normalise_ratio_to_errors = False):
    ratios = []
    for denom in denominators:
        ratio =  nominator.Clone()
        if normalise_ratio_to_errors:
            # TODO
            # this is a preliminary feature, use with care
            for bin_i in range( 1, nominator.nbins() ):
                x_i = nominator[bin_i].value
                x_i_error = nominator[bin_i].error
                y_i = denom[bin_i].value
                y_i_error = denom[bin_i].error
                numerator = x_i - y_i
                denominator = pow( pow( x_i_error, 2 ) + pow( y_i_error, 2 ), 0.5 )
                if denominator == 0:
                    ratio.SetBinContent(bin_i, 0.)
                    ratio.SetBinError(bin_i, 0.)
                else:
                    ratio.SetBinContent(bin_i, numerator/denominator)
                    ratio.SetBinError(bin_i, denominator)
        else:
            ratio.Divide( denom )
        if len(denominators) > 1:
            ratio.linecolor = denom.linecolor
            ratio.fillcolor = denom.fillcolor
        ratios.append(ratio)
    return ratios

def copy_style(copy_from, copy_to):
    # colours
    copy_to.linecolor = copy_from.linecolor
    copy_to.markercolor = copy_from.markercolor
    copy_to.fillcolor = copy_from.fillcolor
    # style
    copy_to.markerstyle = copy_from.markerstyle
    copy_to.linestyle = copy_from.linestyle
    copy_to.fillstyle = copy_from.fillstyle
    # size
    copy_to.markersize = copy_from.markersize
    copy_to.linesize = copy_from.markersize
    # legend
    copy_to.legendstyle  = copy_from.legendstyle


def make_line_hist(bin_edges, y_value):
    l = Hist(bin_edges, type = 'D')
    for i in range(1, len(bin_edges)):
        l.SetBinContent(i, y_value)
    return l

def absolute(hist):
    h = deepcopy(hist)
    for bin_i in range(1, h.nbins() + 1):
        value = h.GetBinContent(bin_i)
        error = h.GetBinError(bin_i)
        h.SetBinContent(bin_i, abs(value))
        h.SetBinError(bin_i, abs(error))
    return h

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
