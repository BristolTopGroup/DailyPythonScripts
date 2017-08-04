from dps.utils.pandas_utilities import read_tuple_from_file
from dps.utils.hist_utilities import value_error_tuplelist_to_hist
from dps.config.variable_binning import reco_bin_edges_vis, bin_edges_vis, control_plot_nbins, control_plots_bins_for01
from dps.config.latex_labels import samples_latex
from dps.config.histogram_colours import histogram_colours as colours
from dps.utils.plotting import make_data_mc_comparison_plot, Histogram_properties
from dps.config.xsection import XSectionConfig
from dps.config.latex_labels import channel_latex, variables_latex
import math

# Move to config
systmematicSourceToPlot = [
'JES',
'JER',
'BJet',
'LightJet',
'Electron',
'Muon',
'PileUp',

'QCD_shape',
'QCD_cross_section',

'ElectronEn',
'MuonEn',
'TauEn',
'UnclusteredEn',

'luminosity',
'V+Jets_cross_section',
'SingleTop_cross_section',
]

def uncertaintyForSystematicSource( name, centralMC, bin_edges, path, channel ):
    variation_up_prefix = '_up'
    variation_down_prefix = '_down'
    if 'En' in name:
        variation_up_prefix = 'Up'
        variation_down_prefix = 'Down'
    elif 'luminosity' in name or 'V+Jets' in name or 'SingleTop' in name:
        variation_up_prefix = '+'
        variation_down_prefix = '-'
    elif 'QCD' in name:
        variation_up_prefix = ''
        variation_down_prefix = ''        


    normalisation_results_up  = read_tuple_from_file( '{path}/{variation}{prefix}/normalisation_{channel}.txt'.format( path = path, variation=name, prefix = variation_up_prefix, channel=channel ) )
    normalisation_results_down  = read_tuple_from_file( '{path}/{variation}{prefix}/normalisation_{channel}.txt'.format( path = path, variation=name, prefix = variation_down_prefix, channel=channel ) )

    histograms_up = getHistogramsFromNormalisationResults(normalisation_results_up, bin_edges)
    histograms_down = getHistogramsFromNormalisationResults(normalisation_results_down, bin_edges)

    total_up = sumMCHistograms( histograms_up )
    total_down = sumMCHistograms( histograms_down )

    total_up.Add( centralMC, -1 )
    total_down.Add( centralMC, -1 )

    relative_uncertainties = []

    for i in range(1,centralMC.GetNbinsX()+1):
        uncertainty = max( abs(total_down.GetBinContent(i)), abs( total_up.GetBinContent(i) ) )
        centralValue = centralMC.GetBinContent(i)
        if centralValue != 0:
            relative_uncertainties.append( uncertainty/centralMC.GetBinContent(i) )
        else:
            relative_uncertainties.append( 0 )

    # print name, relative_uncertainties
    return relative_uncertainties

def getHistogramsFromNormalisationResults( normalisations, bin_edges ) :
    histograms = {
        'Data' : value_error_tuplelist_to_hist( normalisations['data'], bin_edges ),#.Rebin(2),
        'QCD' : value_error_tuplelist_to_hist( normalisations['QCD'], bin_edges ),#.Rebin(2),
        'V+Jets' : value_error_tuplelist_to_hist( normalisations['V+Jets'], bin_edges ),#.Rebin(2),
        'SingleTop' : value_error_tuplelist_to_hist( normalisations['SingleTop'], bin_edges ),#.Rebin(2),
        'TTJet' : value_error_tuplelist_to_hist( normalisations['TTJet_MC'], bin_edges ),#.Rebin(2),
    }
    return histograms

def sumMCHistograms( dictOfHistograms ) :
	return dictOfHistograms['TTJet'] + dictOfHistograms['SingleTop'] + dictOfHistograms['V+Jets'] + dictOfHistograms['QCD']

def setMCUncertaintiesToZero( dictOfHistograms ):
    for label, histogram in dict_histograms.iteritems():
        if 'Data' in label: continue

        for i in range(0,histogram.GetNbinsX()+2):
            histogram.SetBinError(i,0)

def getTotalSystematicUncertainty( systematicUncertainties ):
    totalUncertainty = []

    for source, u in systematicUncertainties.iteritems():
        if len(totalUncertainty) == 0:
            totalUncertainty = u
            continue

        for i in range(0,len(totalUncertainty)):
            currentUncertainty = totalUncertainty[i]
            additionalUncertainty = u[i]

            newUncertainty = math.sqrt( currentUncertainty * currentUncertainty + additionalUncertainty * additionalUncertainty )
            totalUncertainty[i] = newUncertainty
    return totalUncertainty

def drawHistograms( dictionaryOfHistograms, uncertaintyBand, config, channel, variable ) :
    histograms_to_draw = [
        dictionaryOfHistograms['Data'],
        dictionaryOfHistograms['QCD'],
        dictionaryOfHistograms['V+Jets'],
        dictionaryOfHistograms['SingleTop'],
        dictionaryOfHistograms['TTJet'],
    ]

    histogram_lables   = [
        'data',
        'QCD', 
        'V+jets', 
        'single-top', 
        samples_latex['TTJet'],
    ]

    histogram_colors   = [
        colours['data'], 
        colours['QCD'], 
        colours['V+Jets'], 
        colours['Single-Top'], 
        colours['TTJet'],
    ]


    # Find maximum y of samples
    maxData = max( list(histograms_to_draw[0].y()) )
    y_limits = [0, maxData * 1.4]

    # More histogram settings to look semi decent
    histogram_properties = Histogram_properties()
    histogram_properties.name                   = '{channel}_{variable}'.format(channel = channel, variable=variable)
    histogram_properties.title                  = '$%.1f$ fb$^{-1}$ (%d TeV)' % ( config.new_luminosity/1000., config.centre_of_mass_energy )
    histogram_properties.x_axis_title           = variables_latex[variable]
    histogram_properties.y_axis_title           = 'Events'
    if variable in ['HT', 'ST', 'MET', 'WPT', 'lepton_pt']:
        histogram_properties.y_axis_title       = 'Events / {binWidth} GeV'.format( binWidth=binWidth )
        histogram_properties.x_axis_title           = '{variable} (GeV)'.format( variable = variables_latex[variable] )


    histogram_properties.x_limits               = [ reco_bin_edges[0], reco_bin_edges[-1] ]
    histogram_properties.y_limits               = y_limits
    histogram_properties.y_max_scale            = 1.3
    histogram_properties.xerr                   = None
    # workaround for rootpy issue #638
    histogram_properties.emptybins              = True
    histogram_properties.additional_text        = channel_latex[channel.lower()]
    histogram_properties.legend_location        = ( 0.9, 0.73 )
    histogram_properties.cms_logo_location      = 'left'
    histogram_properties.preliminary            = True
    # histogram_properties.preliminary            = False
    histogram_properties.set_log_y              = False
    histogram_properties.legend_color           = False
    histogram_properties.ratio_y_limits     = [0.5, 1.5]

    # Draw histogram with ratio plot
    histogram_properties.name += '_with_ratio'
    loc = histogram_properties.legend_location
    # adjust legend location as it is relative to canvas!
    histogram_properties.legend_location = ( loc[0], loc[1] + 0.05 )

    make_data_mc_comparison_plot( 
        histograms_to_draw, 
        histogram_lables, 
        histogram_colors,
        histogram_properties, 
        save_folder = 'plots/control_plots_with_systematic/',
        show_ratio = True, 
        normalise = False,
        systematics_for_ratio = uncertaintyBand,
        systematics_for_plot = uncertaintyBand,
    )

    histogram_properties.set_log_y = True
    histogram_properties.y_limits = [0.1, y_limits[-1]*100 ]
    histogram_properties.legend_location = ( 0.9, 0.9 )
    histogram_properties.name += '_logY'
    make_data_mc_comparison_plot( 
        histograms_to_draw, 
        histogram_lables, 
        histogram_colors,
        histogram_properties, 
        save_folder = 'plots/control_plots_with_systematic/logY/',
        show_ratio = True, 
        normalise = False,
        systematics_for_ratio = uncertaintyBand,
        systematics_for_plot = uncertaintyBand,
    )    

config = XSectionConfig(13)


for variable in config.variables:
    if not 'Bins' in variable: continue
    print variable

    histogramsForEachChannel = {}
    uncertaintiesForEachChannel = {}

    binEdges = control_plots_bins_for01[variable]
    # bin_low = binEdges[0]
    # bin_high = binEdges[-1]
    # nBins = control_plot_nbins[variable] 
    # binWidth = ( bin_high - bin_low ) / nBins

    # reco_bin_edges = [ bin_low + binWidth * i for i in range(0, nBins + 1) ]
    reco_bin_edges = binEdges
    print reco_bin_edges
    for channel in config.analysis_types.keys():
        if channel == 'combined': continue

        path_to_DF = 'data/normalisation/background_subtraction/13TeV/{variable}/VisiblePS/'.format( variable = variable )
        normalisation_fileName = 'normalisation_{channel}.txt'.format(channel=channel)
        normalisation_results_electron  = read_tuple_from_file( '{path}/central/{filename}'.format(path=path_to_DF,filename=normalisation_fileName)  )

        print normalisation_results_electron
        dict_histograms = getHistogramsFromNormalisationResults(normalisation_results_electron, reco_bin_edges )

        totalMC = sumMCHistograms( dict_histograms )
        statisticalUncertainties = [ totalMC.GetBinError(i) / totalMC.GetBinContent(i) if totalMC.GetBinContent(i) else 0 for i in range(1, totalMC.GetNbinsX()+1)]

        systematicUncertainties = {}
        systematicUncertainties['stat'] = statisticalUncertainties
        for source in systmematicSourceToPlot:
            if channel == 'electron' and source == 'Muon': continue
            elif channel == 'muon' and source == 'Electron': continue

            if variable in config.variables_no_met and 'En' in source : continue
            systematicUncertainties[source] = uncertaintyForSystematicSource( source, totalMC, reco_bin_edges, path_to_DF, channel )

        totalSystematicUncertainty = getTotalSystematicUncertainty( systematicUncertainties )

        setMCUncertaintiesToZero( dict_histograms )

        histogramsForEachChannel[channel] = dict_histograms
        uncertaintiesForEachChannel[channel] = totalSystematicUncertainty

        drawHistograms( dict_histograms, totalSystematicUncertainty, config, channel, variable )

    # Now draw combined plot
    combinedHistograms = None
    for channel, histograms in histogramsForEachChannel.iteritems():
        if combinedHistograms is None:
            combinedHistograms = histograms
        else:
            for label,histogram in histograms.iteritems():
                combinedHistograms[label].Add( histogram )

    combinedUncertainties = None
    for channel, uncertainties in uncertaintiesForEachChannel.iteritems():
        if combinedUncertainties is None:
            combinedUncertainties = uncertainties
        else:
            for i in range(0,len(uncertainties)):
                newUncertainty = math.sqrt( combinedUncertainties[i] ** 2 + uncertainties[i] ** 2 )
                combinedUncertainties[i] = newUncertainty

    print combinedHistograms

    ttbarMC = combinedHistograms['TTJet']
    data = combinedHistograms['Data']
    totalMC = sumMCHistograms( combinedHistograms )

    print 'Total data : ',data.integral(overflow=True)
    print 'Total MC : ',totalMC.integral(overflow=True)
    print 'Fraction of ttbar :',ttbarMC.integral(overflow=True)/totalMC.integral(overflow=True)

    drawHistograms( combinedHistograms, combinedUncertainties, config, 'COMBINED', variable )

