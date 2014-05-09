'''
Created on Nov 23, 2011

@author: Lukasz Kreczko

Email: Lukasz.Kreczko@cern.ch

Different methods are available:
- ABCD method (takes 2D histogram)
- Matrix method (takes 1D histogram)
- RelISo method (takes 1D histogram)

Output consists of an estimated number of events and error
'''
from __future__ import division
from math import sqrt
import tools.ROOTFileReader as FileReader
import tools.PlottingUtilities as plotting
import FILES
try:
    from uncertainties import ufloat
    from uncertainties import umath
except:
    print "Could not find uncertainties package, please install for full functionality"
    print 'http://packages.python.org/uncertainties/'
    ufloatEnabled = False
from ROOT import Double
DEBUG = False
allMC = ['TTJet', 'DYJetsToLL', 'QCD_Pt-20to30_BCtoE', 'QCD_Pt-30to80_BCtoE',
                 'QCD_Pt-80to170_BCtoE', 'QCD_Pt-20to30_EMEnriched', 'QCD_Pt-30to80_EMEnriched',
                 'QCD_Pt-80to170_EMEnriched', 'GJets_HT-40To100', 'GJets_HT-100To200',
                 'GJets_HT-200', 'WWtoAnything', 'WZtoAnything', 'ZZtoAnything', 'T_tW-channel',
                 'T_t-channel', 'T_s-channel', 'Tbar_tW-channel', 'Tbar_t-channel',
                 'Tbar_s-channel', 'W1Jet', 'W2Jets', 'W3Jets', 'W4Jets'
                 ]
qcd = ['QCD_Pt-20to30_BCtoE', 'QCD_Pt-30to80_BCtoE',
                 'QCD_Pt-80to170_BCtoE', 'QCD_Pt-20to30_EMEnriched', 'QCD_Pt-30to80_EMEnriched',
                 'QCD_Pt-80to170_EMEnriched', 'GJets_HT-40To100', 'GJets_HT-100To200',
                 'GJets_HT-200']
btag_latex = {
                  '0orMoreBtag':'$ \geq 0$ b-tags',
                '0btag':'0 b-tag',
                '1btag':'1 b-tag',
                '2orMoreBtags':'$\geq 2$ b-tags'
                  }
#relIso method is overestimating by 45%
defaultHistogram = 'TTbarEplusJetsPlusMetAnalysis/Ref selection/QCD e+jets PFRelIso/Electron/electron_pfIsolation_03_0orMoreBtag'
relIsoBias = 0.0

def estimateQCDWithRelIso(inputFiles, histogramForEstimation=defaultHistogram, function='expo',
                   fitRange=(0.3, 1.6), fitRangesForSystematics=[(0.2, 1.6), (0.4, 1.6)]):
    inputFile = inputFiles['SingleElectron']
    if DEBUG:
        print '*' * 120
        print "Estimating QCD using a fit to RelIso"
        print 'Input file = ', inputFile
        print 'Histogram = ', histogramForEstimation
        print 'Fit function = ', function
        print 'Fit range = ', fitRange
        print 'Fit ranges for systematics = ', fitRangesForSystematics
        print '*' * 120
    histogramForEstimation = FileReader.getHistogramFromFile(histogramForEstimation, inputFile)
    result = relIsoMethodWithSystematics(histogramForEstimation, function, fitRange=fitRange, fitRangesForSystematics=fitRangesForSystematics,
                                         applyBiasCorrection=True)
    
    return result

def relIsoMethodWithSystematics(histogramForEstimation=defaultHistogram, function='expo',
                   fitRange=(0.3, 1.6), fitRangesForSystematics=[(0.2, 1.6), (0.4, 1.6)], applyBiasCorrection=True):
     
    centralResult = relIsoMethod(histogramForEstimation, function, fitRange=fitRange)
    centralEstimate, centralAbsoluteError = centralResult['estimate'], centralResult['absoluteError']
    absoluteStatisticError = centralAbsoluteError
    centralRelativeError = 0
    if not centralEstimate == 0:
        centralRelativeError = centralAbsoluteError / centralEstimate
    centralRelativeErrorSquared = centralRelativeError ** 2
    
    #systematic errors
    systematicErrorFromOtherFitRangesSquared = 0
    for currentRange in fitRangesForSystematics:
        currentResult = relIsoMethod(histogramForEstimation, function, fitRange=currentRange)
        currentEstimate, err = currentResult['estimate'], currentResult['absoluteError']
        deviation = currentEstimate - centralEstimate
        if not centralEstimate == 0:
            systematicErrorFromOtherFitRangesSquared += (deviation / centralEstimate) ** 2
            
    centralRelativeErrorSquared += systematicErrorFromOtherFitRangesSquared
    relativeSytematicErrorSquared = systematicErrorFromOtherFitRangesSquared
    
    relativeErrorFromBiasCorrection = 0
    if applyBiasCorrection:
        reductionFromBias = 1 - relIsoBias
        centralEstimate = centralEstimate * reductionFromBias
        relativeErrorFromBiasCorrection = relIsoBias
    
    centralRelativeErrorSquared += relativeErrorFromBiasCorrection ** 2
    relativeSytematicErrorSquared += relativeErrorFromBiasCorrection ** 2
    
    absoluteSystematicError = sqrt(relativeSytematicErrorSquared) * centralEstimate
    centralAbsoluteError = sqrt(absoluteSystematicError ** 2 + absoluteStatisticError ** 2)
#    absoluteStatisticError = centralRelativeError * centralEstimate
    result = {
              'estimate':centralEstimate,
              'absoluteError': centralAbsoluteError,
              'absoluteSystematicError': absoluteSystematicError,
              'absoluteStatisticError': absoluteStatisticError,
              'fit':centralResult['fit']}
    return result

def relIsoMethod(histogramForEstimation, function='expo',
                   fitRange=(0.3, 1.6), signalRegion=(0., 0.1)):
    
    histogramForEstimation = histogramForEstimation.Clone('tmp')
    
    #investigate them
    binWidthOfOriginalHistoram = 0.01
    rebinOfOriginalHistogram = 10

    estimate = 0
    relativeErrorSquared = 0
    histogramForEstimation.Rebin(rebinOfOriginalHistogram)

    fit = None
    fit = performFit(histogramForEstimation, function, fitRange)
    if fit:
        estimate = fit.Integral(signalRegion[0], signalRegion[1]) / (binWidthOfOriginalHistoram * rebinOfOriginalHistogram)
        for parErr in range(0, fit.GetNumberFreeParameters()):
            par = fit.GetParameter(parErr)
            err = fit.GetParError(parErr)
            if not par == 0:
                relativeErrorSquared += (err / par) ** 2
                
    result = {'estimate': estimate,
              'absoluteError':sqrt(relativeErrorSquared) * estimate,
              'relativeError':sqrt(relativeErrorSquared),
              'fit':fit}
    return result
    
def performFit(histogram, function, fitRange):
    histogram = histogram.Clone('fitting')
    numberOfFreeParameters = -1
    fit = None
    
    histogram.Fit(function, "Q0", "ah", fitRange[0], fitRange[1])
    fit = histogram.GetFunction(function)
    if fit:
        return fit.Clone()
    else:
        return None
    
#Estimate the bias on MC only
def getRelIsoCalibrationCurve(inputFiles, histogramForEstimation=defaultHistogram, function='expo',
                   fitRanges=[(0.2, 1.6), (0.3, 1.6), (0.4, 1.6)]):
    if DEBUG:
        print '*' * 120
        print "Estimating QCD using a fit to RelIso"
        print 'Input files = ', inputFiles
        print 'Histogram = ', histogramForEstimation
        print 'Fit function = ', function
        print 'Fit ranges = ', fitRanges
        print '*' * 120
    #get histograms
    #instead of data use sum MC
    
def doPerformanceStudyOnMCOnly(inputFiles,
                               histogramForEstimation=defaultHistogram,
                               function='expo',
                   fitRanges=[(0.2, 1.6), (0.3, 1.6), (0.4, 1.6)]):
    if DEBUG:
        print '*' * 120
        print "Estimating QCD using a fit to RelIso"
        print 'Histogram = ', histogramForEstimation
        print 'Fit functions = ', function
        print 'Fit ranges = ', fitRanges
        print '*' * 120
    #get histograms
    histograms = FileReader.getHistogramDictionary(histogramForEstimation, inputFiles)
    global allMC, qcd
    
    histograms['SumMC'] = plotting.sumSamples(histograms, allMC)
    
    histograms['QCD'] = plotting.sumSamples(histograms, qcd)
    
#    qcdInSignalRegion = histograms['QCD'].Integral()
#    qcdError = 0
#    if not qcdInSignalRegion == 0:
#        qcdError = qcdInSignalRegion / sqrt(qcdInSignalRegion) 
    import copy
    results = {}
    qcdInSignalRegion, qcdError = getIntegral(histograms['QCD'], (0, 0.1))
#        getRelIsoCalibrationCurve(inputFiles, histogramForEstimation, function, fitRanges)
    for fitRange in fitRanges:
        #take all other fit ranges as systematics
        fitRangesForSystematics = copy.deepcopy(fitRanges)
        fitRangesForSystematics.remove(fitRange)
        #instead of data use sum MC
        resultFromMethod = relIsoMethodWithSystematics(histograms['SumMC'], function, fitRange, fitRangesForSystematics, False)
        estimate, absoluteError = resultFromMethod['estimate'], resultFromMethod['absoluteError']
        N_est = ufloat((estimate, absoluteError))
        N_qcd = ufloat((qcdInSignalRegion, qcdError))
        relativeDeviation = N_est / N_qcd

        result = {}
        result['performance'] = (relativeDeviation.nominal_value, relativeDeviation.std_dev())
        result['estimate'] = (estimate, absoluteError)
        result['qcdInSignalRegion'] = (qcdInSignalRegion, qcdError)
        result['fitfunction'] = function
        result['fitRange'] = fitRange
        result['fitRangesForSystematics'] = fitRangesForSystematics
        result['fit'] = resultFromMethod['fit']
        results[str(fitRange)] = result
    return results
        
def printPerformanceResults(btag_results, btagBins):
    print 'function, range & $N_{est,\,QCD}^{data}$ & $N_{true,\,QCD}^{MC}$ & $f_{est./true}$ \\\\'
    for btag in btagBins:
        print '\hline'
        results = btag_results[btag]
        print '%s & & & \\\\' % btag_latex[btag]
        print '\hline'       
        for fitrange, result in results.iteritems():
            N_qcd, N_qcd_error = result['qcdInSignalRegion']
            est, err = result['estimate']
            performance, performanceError = result['performance']
            format = (result['fitfunction'], str(result['fitRange']), N_qcd, N_qcd_error, est, err, performance, performanceError)
            print '%s, %s &  $%.0f \pm %.0f$ &  $%.0f \pm %.0f$ & $ %.3f \pm %.3f$ \\\\' % format
        
def getIntegral(histogram, integralRange=(0, 0.1)):
    firstBin = histogram.GetXaxis().FindBin(integralRange[0])
    lastBin = histogram.GetXaxis().FindBin(integralRange[1])
    
    integral = 0
    absoluteError = Double(0)
    integral = histogram.IntegralAndError(firstBin, lastBin, absoluteError)
    
    return integral, absoluteError        

def printResults(results, btagBins):
    header = "region & $N_{est,\,QCD}^{MC}$ & $N_{est,\,QCD}^{data}$ &"
    header += "$\\frac{(data - MC(QCD^{MC}))}{data}$ &"
    header += "$\\frac{(data -MC(QCD^{data}))}{data}$ \\\\"
    print header
    print '\hline'
    rowTemplate = "%s & $%.0f \pm %.0f$ & "
    rowTemplate += "$%.0f \pm %.0f$ (stat.) $\pm %.0f$ (syst.) &"
    rowTemplate += "%s & %s \\\\"
    global btag_latex
    for btag in btagBins:
        result = results[btag]
        ndata = result['N_data']
        nQCD = result['N_QCD']
        nSumMC = result['N_SumMC']
        nSumMC_QCDFromData = nSumMC - nQCD + result['estimate']
        data_MC_diff = (ndata - nSumMC) / ndata * 100
        data_MC_diff_QCDFromData = (ndata - nSumMC_QCDFromData) / ndata * 100
        result['data-MC(QCDFromMC)'] = data_MC_diff
        result['data-MC(QCDFromData)'] = data_MC_diff_QCDFromData
        formatting = (btag_latex[btag], result['N_QCD'], result['N_QCD_Error'], result['estimate'],
                      result['absoluteStatisticError'], result['absoluteSystematicError'],
                      ('%.2f' % data_MC_diff) + '\%', ('%.2f' % data_MC_diff_QCDFromData) + '\%')
        print rowTemplate % formatting
        
def plotFits(results):
    pass        

def getStuff(histogramForEstimation, inputFiles):
    histograms = FileReader.getHistogramDictionary(histogramForEstimation, inputFiles)
    global allMC, qcd
    
    histograms['SumMC'] = plotting.sumSamples(histograms, allMC)
    
    histograms['QCD'] = plotting.sumSamples(histograms, qcd)
    qcdInSignalRegion, qcdError = getIntegral(histograms['QCD'], (0, 0.1))
    data, dataError = getIntegral(histograms['SingleElectron'], (0, 0.1))
    sumMC, sumMCError = getIntegral(histograms['SumMC'], (0, 0.1))
    result = {
              'N_data': data,
              'N_QCD': qcdInSignalRegion,
              'N_QCD_Error': qcdError,
              'N_SumMC': sumMC
              }
    return result
    
if __name__ == '__main__':
    btagBins = [
                '0orMoreBtag',
                '0btag',
                '1btag',
                '2orMoreBtags'
                ]
    
    
    histBase = 'TTbar_plus_X_analysis/EPlusJets/QCD e+jets PFRelIso/Electron/electron_pfIsolation_03_%s'
    results = {}
    mcresults = {}
    for btag in btagBins:
        hist = histBase % btag
        results[btag] = estimateQCDWithRelIso(FILES.files, histogramForEstimation=hist)
        results[btag].update(getStuff(hist, FILES.files))
        mcresults[btag] = doPerformanceStudyOnMCOnly(FILES.files, hist, function='expo')
    print 
    printResults(results, btagBins)
    print 
    printPerformanceResults(mcresults, btagBins)
