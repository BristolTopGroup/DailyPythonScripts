'''
Approval conditions for TOP-15-013
'''
from __future__ import division
from tools.plotting import Histogram_properties, compare_histograms, Plot
from tools.file_utilities import read_data_from_JSON
from tools.hist_utilities import value_error_tuplelist_to_hist, value_tuplelist_to_hist
from config.variable_binning import bin_edges
from config.latex_labels import variables_latex
from math import sqrt
def getHistograms( fileName, variable, label, plotErrors=False ):

    data = read_data_from_JSON(fileName)[label]
    for bin in data:
        while len(bin) > 2 :
            del bin[-1]

    # Interested in errors, rather than central value
    if plotErrors:
        for bin in data:
            binContent = bin[0]
            del bin[0]
            bin.append(0)
            bin[0] /= binContent
            bin[0] *= 100
    #     h = value_tuplelist_to_hist( data, bin_edges[variable] )
    # else:
    h=value_error_tuplelist_to_hist( data, bin_edges[variable] )
    return h

def useOnlyNormalisationErrors(h, fileName, variable, label):
    bkgHists = {}

    bkgErr = {
    'QCD' : 1.,
    'SingleTop' : 0.3,
    'V+Jets' : 0.3
    }

    print list(h.y())
    var = None
    firstBkg = True
    for bkg in ['QCD', 'SingleTop', 'V+Jets']:
        bkgHist = getHistograms(fileName, variable, bkg)

        if firstBkg:
            var = ( bkgHist * ( bkgErr[bkg] ) / h ) ** 2
            firstBkg = False
        else :
            var += ( bkgHist * ( bkgErr[bkg] ) / h ) ** 2

    # Add luminosity
    var += 0.022**2

    for bin in range(0,h.GetNbinsX()):
        newBinError2 = var.GetBinContent(bin)
        var.SetBinContent(bin, sqrt(newBinError2))
        h.SetBinError(bin, sqrt(newBinError2))




def compare_yield_methods(  measurement='fit_results',
                            com=8,
                            channel='electron',
                            compareErrors=False,
                            statOnly=False):

    file_template = None
    label = None
    fileSuffix = ''
    if compareErrors and not statOnly:
        fileSuffix = '_with_errors'
    if measurement == 'fit_results':
        file_template = 'data/{method}/{com}TeV/{variable}/central/normalisation_{channel}_patType1CorrectedPFMet{suffix}.txt'
        label = 'TTJet'
    elif measurement == 'normalised_xsection':
        file_template = 'data/{method}/{com}TeV/{variable}/xsection_measurement_results/{channel}/central/normalised_xsection_patType1CorrectedPFMet{suffix}.txt'
        label = 'TTJet_unfolded'

    variables = ['MET', 'HT', 'ST','WPT']
    # variables = ['HT']

    for variable in variables:
        fit = file_template.format(
            method='absolute_eta_M3_angle_bl',
            com=com,
            variable=variable,
            channel=channel,
            suffix=fileSuffix
            )
        background = file_template.format(
            method='normalisation/background_subtraction',
            com=com,
            variable=variable,
            channel=channel,
            suffix=fileSuffix
            )
        
        h_fit = getHistograms( fit, variable, label, compareErrors )
        h_bkg = getHistograms( background, variable, label, compareErrors )

        # if measurement is 'fit_results':
        #     useOnlyNormalisationErrors(h_bkg, background, variable, label)
        #     for bin in range(0,h_fit.GetNbinsX()):
        #         h_fit.SetBinError(bin,0)



        properties = Histogram_properties()
        properties.name = '{0}_compare_yield_methods_{1}_{2}_{3}'.format(measurement, variable, com, channel)
        if compareErrors:
            if statOnly:
                properties.name = properties.name.replace('yield','StatErrors')
            else:
                properties.name = properties.name.replace('yield','StatPlusSysErrors')                
        properties.title = 'Comparison of ttbar yield methods'
        properties.path = 'plots/compareFitBackground/{0}TeV/{1}/'.format(com,variable)
        properties.has_ratio = True
        properties.xerr = True
        properties.x_limits = (
            bin_edges[variable][0], bin_edges[variable][-1])
        properties.x_axis_title = variables_latex[variable]
        
        if measurement == 'normalised_xsection':
            if compareErrors:
                if statOnly:
                    properties.y_axis_title = r'Statistical error in $\frac{1}{\sigma}  \frac{d\sigma}{d' + \
                        variables_latex[variable] + '}$'
                    properties.ratio_y_limits = [0.5,1.5]
                else:
                    properties.y_axis_title = r'Total error in $\frac{1}{\sigma}  \frac{d\sigma}{d' + \
                        variables_latex[variable] + '}$'
                    properties.ratio_y_limits = [0.5,1.5]
            else :
                properties.y_axis_title = r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + \
                    variables_latex[variable] + '}$'
                properties.ratio_y_limits = [0.9,1.1]
        else :
            properties.y_axis_title = r'$t\bar{t}$ normalisation'
            properties.ratio_y_limits = [0.7,1.3]

        histograms = {'Fit': h_fit, 'Background subtraction': h_bkg}
        plot = Plot(histograms, properties)
        plot.draw_method = 'errorbar'
        compare_histograms(plot)

if __name__ == '__main__':
    import sys
    if '-d' in sys.argv:
        from tools.logger import log
        log.setLevel(log.DEBUG)

    # compare_yield_methods( measurement='fit_results', com=7, channel='electron')
    # compare_yield_methods( measurement='fit_results', com=7, channel='muon')
    # compare_yield_methods( measurement='fit_results', com=8, channel='electron')
    # compare_yield_methods( measurement='fit_results', com=8, channel='muon')

    # compare_yield_methods( measurement='normalised_xsection', com=8, channel='combined')
    # compare_yield_methods( measurement='normalised_xsection', com=7, channel='combined')

    compare_yield_methods( measurement='normalised_xsection', com=8, channel='combined', compareErrors=True)
    compare_yield_methods( measurement='normalised_xsection', com=7, channel='combined', compareErrors=True)

    compare_yield_methods( measurement='normalised_xsection', com=8, channel='combined', compareErrors=True, statOnly=True)
    compare_yield_methods( measurement='normalised_xsection', com=7, channel='combined', compareErrors=True, statOnly=True)