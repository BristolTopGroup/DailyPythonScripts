from __future__ import division
from ROOT import *
from math import fsum

from HistPlotter import inclusiveBjetBins, exclusiveBjetBins, allBjetBins, rebin
from HistGetter import getHistsFromFiles, addSampleSum
import inputFiles

ufloatEnabled = True
try:
    from uncertainties import ufloat
    from uncertainties import umath
except:
    print "Could not find uncertainties package, please install for full functionality"
    print 'http://packages.python.org/uncertainties/'
    ufloatEnabled = False
    

fitRangesClosureTest = [ (0.1, 0.9), (0.1, 1.0), (0.1, 1.1),
                  (0.2, 0.9), (0.2, 1.0), (0.2, 1.1),
                  (0.3, 0.9), (0.3, 1.0), (0.3, 1.1)]

rebinRelIso = 10


def doFit(histogram, function, fitRange):#, constrainFit = False):
    histogram = histogram.Clone('fitting')
    numberOfFreeParameters = -1
    fit = None
    
    histogram.Fit(function, "Q0", "ah", fitRange[0], fitRange[1])
    fit = histogram.GetFunction(function)
    if fit:
        return fit.Clone()
    else:
        return None

def estimateQCDFrom(histogramForEstimation, function='expo',
                   fitRanges=[(0.2, 1.6), (0.3, 1.6), (0.4, 1.6)]):
    
    histogramForEstimation = histogramForEstimation.Clone('tmp')
    
    binWidthOfOriginalHIstoram = 0.01
    rebinOfOriginalHistogram = rebinRelIso
    signalRegion = (0., 0.1)
    estimate = 0
    estimate2 = 0
    relFitError = 0
    histogramForEstimation.Rebin(rebinOfOriginalHistogram)
    for fitrange in fitRanges:
        fit = None
        fit = doFit(histogramForEstimation, function, fitrange)
        if fit:
            est = fit.Integral(signalRegion[0], signalRegion[1]) / (binWidthOfOriginalHIstoram * rebinOfOriginalHistogram)
            for parErr in range(0, fit.GetNumberFreeParameters()):
                par = fit.GetParameter(parErr)
                err = fit.GetParError(parErr)
                if not par == 0:
                    relFitError += (err / par) ** 2
#            print par, err
            estimate += est
            estimate2 += est * est
    

    mean = estimate / len(fitRanges)
    mean2 = estimate2 / len(fitRanges)
    error = 0
    if not (mean2 - mean * mean) == 0:
        error = sqrt((mean2 - mean * mean) / 2)
    if not mean == 0:
        return (mean, sqrt(relFitError + (error / mean) ** 2) * mean)
    else:
        return (0, 0) 
 
def getQCDEstimateFor(histogramForEstimation='QCDStudy/PFIsolation_WithMETCutAndAsymJetCuts_DR03_0orMoreBtag', function='expo',
                   fitRange=(0.3, 1.6), additionFitRanges=[(0.2, 1.6), (0.4, 1.6)]):
    estimate, absoluteError = estimateQCDFrom(histogramForEstimation, function, fitRanges=[fitRange])
    
    relativeError = 0
    if not estimate == 0:
        relativeError = absoluteError / estimate
    relativeErrorSquared = relativeError ** 2
    
    systematicErrorFromOtherFitRanges = 0
    for currentRange in additionFitRanges:
        est, err = estimateQCDFrom(histogramForEstimation, function, fitRanges=[currentRange])
        deviation = est - estimate
        if not estimate == 0:
            relativeErrorSquared += (deviation / estimate) ** 2
            
#    statisticalErrorSquared = 0
#    if not estimate == 0:
#        statisticalErrorSquared = 1 / estimate
#    relativeErrorSquared += statisticalErrorSquared
    
    relativeError = sqrt(relativeErrorSquared)
    absoluteError = relativeError * estimate
    
    return estimate, absoluteError

def getQCDEstimate(datafile, 
                   histogramForEstimation='QCDStudy/PFIsolation_WithMETCutAndAsymJetCuts_DR03', 
                   bjetBin='', function='expo',
                   fitRange=(0.3, 1.6), additionFitRanges=[(0.2, 1.6), (0.4, 1.6)]): 
    bias = 0.45
    bias = 0
    reductionFromBias = 1 - bias 
    if bjetBin:
        histogramForEstimation = histogramForEstimation + '_' + bjetBin
    files = {'data': datafile}
    hists = [histogramForEstimation]
    hists = getHistsFromFiles(hists, files)
    histogramForEstimation = hists['data'][histogramForEstimation]  
    estimate, absoluteError = getQCDEstimateFor(histogramForEstimation, function, fitRange=fitRange, additionFitRanges=additionFitRanges)
    estimate = estimate * reductionFromBias
    absoluteError = absoluteError * reductionFromBias
    absoluteError = sqrt(absoluteError ** 2 + (estimate * bias) ** 2)
    return estimate, absoluteError

    
def getIntegral(histogram, integralRange=(0, 0.1)):
    firstBin = histogram.GetXaxis().FindBin(integralRange[0])
    lastBin = histogram.GetXaxis().FindBin(integralRange[1])
    
    integral = 0
    absoluteError = Double(0)
    integral = histogram.IntegralAndError(firstBin, lastBin, absoluteError)
    
    return integral, absoluteError
    
    
def getPerformanceOnMC(files, histogramForEstimation='QCDStudy/PFIsolation_WithMETCutAndAsymJetCuts_DR03', bjetBin='', function='expo',
                   fitRange=(0.3, 1.6), additionFitRanges=[(0.2, 1.6), (0.4, 1.6)]):  
    if bjetBin:
        histogramForEstimation = histogramForEstimation + '_' + bjetBin
        
    hists = [histogramForEstimation]
    hists = getHistsFromFiles(hists, files)
    hists = addSampleSum(hists)
    
    histogramForComparison = hists['qcd'][histogramForEstimation]
    histogramForEstimation = hists['allMC'][histogramForEstimation]  
    
    
    estimate, absoluteError = getQCDEstimateFor(histogramForEstimation, function, fitRange=fitRange, additionFitRanges=additionFitRanges)
    
    qcdInSignalRegion, qcdError = getIntegral(histogramForComparison, (0, 0.1))
    
    N_est = ufloat((estimate, absoluteError))
    N_qcd = ufloat((qcdInSignalRegion, qcdError))
    
    relativeDeviation = N_est/ N_qcd
    
    result = {}
    result['performance'] = (relativeDeviation.nominal_value, relativeDeviation.std_dev())
    result['estimate'] = (estimate, absoluteError)
    result['qcdInSignalRegion'] = (qcdInSignalRegion, qcdError)
    
    return result
    
    
def getShapeErrorHistogram(files, 
                           histogramForShape = 'topReconstruction/backgroundShape/mttbar_conversions_withMETAndAsymJets', 
                           histogramForComparison = 'topReconstruction/backgroundShape/mttbar_antiIsolated_withMETAndAsymJets',
                           rebin = 1, 
                           suffix = ''):
    files = {'data': files['data']}
#    histogramForShape = 'topReconstruction/backgroundShape/mttbar_conversions_withMETAndAsymJets'
#    histogramForComparison = 'topReconstruction/backgroundShape/mttbar_antiIsolated_withMETAndAsymJets'
#    suffixes = allBjetBins
#    rebin = 50

    errors = None
        
#    for suffix in suffixes:
#        if suffix in histname:
    if not suffix == '':
        histogramForShape = histogramForShape + '_' + suffix
        histogramForComparison = histogramForComparison + '_' + suffix
        
    hists = [histogramForShape, histogramForComparison]
    hists = getHistsFromFiles(hists, files)
    histogramForShape = hists['data'][histogramForShape]
    histogramForComparison = hists['data'][histogramForComparison]
    histogramForShape.Sumw2()
    histogramForComparison.Sumw2()
            
    histogramForShape.Rebin(rebin)
    histogramForComparison.Rebin(rebin)
            
    nShape = histogramForShape.Integral()
    nCompare = histogramForComparison.Integral()
            
    if nShape > 0 and nCompare > 0:
        histogramForShape.Scale(1 / nShape)
        histogramForComparison.Scale(1 / nCompare)
            
    errors = histogramForShape.Clone('ShapeErrors')
    errors.Add(histogramForComparison, -1)#subtraction
    for bin in range(1, errors.GetNbinsX()):
        errors.SetBinContent(bin, fabs(errors.GetBinContent(bin)))
    errors.Divide(histogramForShape)
            
    return errors   
    
#def combineErrorsFromHistogramList():
#    pass

def createErrorHistogram(mcHistograms, qcdHistogram, relativeQCDEstimationError, shapeErrorHistogram):
    errorHist = qcdHistogram.Clone("ErrorHist")
    
    for bin in range(1, errorHist.GetNbinsX()):
        nQCD = qcdHistogram.GetBinContent(bin)
        nMC = 0
        for hist in mcHistograms:
            nMC += hist.GetBinContent(bin)
        err = relativeQCDEstimationError
        if shapeErrorHistogram:
            shapeErr = shapeErrorHistogram.GetBinContent(bin)
            shapeErrStat = shapeErrorHistogram.GetBinError(bin)
            shapeErr = fabs(shapeErr) + shapeErrStat
            err = sqrt(err * err + shapeErr * shapeErr)
        errorHist.SetBinContent(bin, nMC)
        errorHist.SetBinError(bin, err * nQCD)
    return errorHist


def compareFitFunctions(datafile, histogramForEstimation, functions, fitRange=(0.3, 1.6)):   
    files = {'data': datafile}
    hists = [histogramForEstimation]
    hists = getHistsFromFiles(hists, files)
    histogramForEstimation = hists['data'][histogramForEstimation]  
    
    result = {}
    for function in functions:
        fit = doFit(histogramForEstimation, function, fitRange)
        ndof = fit.GetNDF()
        chi2 = fit.GetChisquare()
        result[function] = {'NDOF': ndof, 'Chi2':chi2}
    return result

def doComparisonFitFunctions(files):
    functions = ['expo', 'gaus', 'pol1']
    print 'Comparison between fit functions'
    fitRanges = [(0.2, 1.6), (0.3, 1.6), (0.4, 1.6)]
    
    averageChi2 = {}
    averageNDOF = {}
    btags = ['0btag', '1btag', '2orMoreBtags']
    for function in functions:
        averageChi2[function] = 0
        averageNDOF[function] = 0
        
    for fitRange in fitRanges:
        result = compareFitFunctions(files['data'], histogramForEstimation='QCDStudy/QCDest_PFIsolation_1btag_WithMETCutAndAsymJetCuts_3jets', functions=functions,
                   fitRange=fitRange)
    
        print '| * 3jets, 1 btag* | *fit range (%.1f, %1.f)*|||' % fitRange
        print '| *fit function* | *Chi^2* | *NDoF* | *Chi^2/NDoF* |'
        for function, values in result.iteritems():
            chi2 = values['Chi2']
            ndof = values['NDOF']
            averageChi2[function] += chi2
            averageNDOF[function] += ndof
            print '| %s | %.3f | %d | %.3f |' % (function, chi2, ndof, chi2 / ndof)
        
        for btag in btags:
            result = compareFitFunctions(files['data'], histogramForEstimation='QCDStudy/PFIsolation_WithMETCutAndAsymJetCuts_DR03_%s' % btag, functions=functions,
                   fitRange=fitRange)
            print '| * 4jets, %s* | *fit range (%.1f, %1.f)*|||' % (btag, fitRange[0], fitRange[1])
            print '| *fit function* | *Chi^2* | *NDoF* | *Chi^2/NDoF* |'
            for function, values in result.iteritems():
                chi2 = values['Chi2']
                ndof = values['NDOF']
                averageChi2[function] += chi2
                averageNDOF[function] += ndof
                print '| %s | %.3f | %d | %.3f |' % (function, chi2, ndof, chi2 / ndof)
            
    print '| *average over all regions and fit ranges* ||||'
    print '| *fit function* | *Chi^2* | *NDoF* | *Chi^2/NDoF* |'
    N_measurements = len(fitRanges) * (len(btags) + 1)
    for function, values in result.iteritems():
            chi2 = averageChi2[function] / N_measurements
            ndof = averageNDOF[function] / N_measurements
            print '| %s | %.3f | %d | %.3f |' % (function, chi2, ndof, chi2 / ndof)
            
    
    
def doEstimation(files, function, hist):
#    print 'QCD estimation in relative isolation using', function, 'function'
#    est, err = getQCDEstimate(files['data'], histogramForEstimation='QCDStudy/QCDest_PFIsolation_1btag_WithMETCutAndAsymJetCuts_3jets', function=function,
#                   fitRange=(0.3, 1.6), additionFitRanges=[(0.2, 1.6), (0.4, 1.6)])
#    print '| *region* | *N<sub>QCD, exp</sub>* | *N<sub>est</sub>* | *scale factor* |'
#    print '| 3j1t | --- |  %.1f &pm; %.1f | --- |' % (est, err)
#    print 'Final QCD estimate (==3jet, %s): %.1f +- %.1f' % ('1 b-tag', est, err)
    
    for btag in ['0btag', '1btag', '2orMoreBtags']:
        tag = 0
        if '0' in btag:
            tag= 0
        elif '1' in btag:
            tag = 1
        elif '2' in btag:
            tag = 2
        
        est, err = getQCDEstimate(files['data'], histogramForEstimation= hist + '_%s' % btag, function=function,
                   fitRange=(0.3, 1.6), additionFitRanges=[(0.2, 1.6), (0.4, 1.6)])
#        print 'Final QCD estimate (>=4jet, %s): %.1f +- %.1f' % (btag, est, err)
        print '| 4j%dt | --- |  %.1f +- %.1f | --- |' % (tag, est, err)
        
def doMCPerformance(files, function, hist):
#    print 'Performance on MC using', function, 'function'
#    result = getPerformanceOnMC(files, 
#                                histogramForEstimation='QCDStudy/QCDest_PFIsolation_1btag_WithMETCutAndAsymJetCuts_3jets', 
#                                function=function,
#                   fitRange=(0.3, 1.6), additionFitRanges=[(0.2, 1.6), (0.4, 1.6)])
#    est, err = result['estimate']
#    N_qcd, N_qcd_error = result['qcdInSignalRegion']
#    performance, performanceError = result['performance']
    print '| *region* | *N<sub>QCD, true</sub>* | *N<sub>est</sub>* | *(N<sub>est</sub> - N<sub>QCD, true</sub>)/N<sub>QCD, true</sub>* |'
#    print '| (==3jet, %s) |  %.1f +- %.1f |  %.1f +- %.1f |  %.3f +- %.3f |' % ('1 b-tag', N_qcd, N_qcd_error, est, err, performance, performanceError)
#    hist = 'TTbarEplusJetsPlusMetAnalysis/Ref + AsymJets selection/QCD e+jets PFRelIso/Electron/electron_pfIsolation_03'
    for btag in ['0btag', '1btag', '2orMoreBtags']:
        result = getPerformanceOnMC(files, 
                                    histogramForEstimation=hist + '_%s' % btag, function=function,
                   fitRange=(0.3, 1.6), additionFitRanges=[(0.2, 1.6), (0.4, 1.6)])
        est, err = result['estimate']
        N_qcd, N_qcd_error = result['qcdInSignalRegion']
        performance, performanceError = result['performance']
        print '| (>=4jet, %s) |  %.1f +- %.1f |  %.1f +- %.1f |  %.3f +- %.3f |' % (btag, N_qcd, N_qcd_error, est, err, performance, performanceError)
        
if __name__ == '__main__':
    gROOT.SetBatch(True)
    gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    
    files = inputFiles.files
    function = 'expo'
    hist = 'TTbarEplusJetsPlusMetAnalysis/Ref + AsymJets selection/QCD e+jets PFRelIso/Electron/electron_pfIsolation_03'
    
#    doEstimation(files, function, hist)
#    print "MC performance"
#    doMCPerformance(files, function, hist)
    
#    doComparisonFitFunctions(files)
    
    
        
        
        
    
