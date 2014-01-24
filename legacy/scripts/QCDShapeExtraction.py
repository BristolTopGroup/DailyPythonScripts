'''
Created on Nov 23, 2011

@author: Lukasz Kreczko

Email: Lukasz.Kreczko@cern.ch
'''

import ROOTFileReader as reader

def getQCDShape(file, histname, histnameForSystematics, rebin=1, suffix=''):
    errors = None
    if not suffix == '':
        histogramForShape = histname + '_' + suffix
        histogramForComparison = histnameForSystematics + '_' + suffix
    histogramForShape = reader.getHistogramFromFile(histogramForShape, file)
    histogramForComparison = reader.getHistogramFromFile(histogramForComparison, file)
    #sum weights for correct error calculation
    histogramForShape.Sumw2()
    histogramForComparison.Sumw2()
    #rebin
    histogramForShape.Rebin(rebin)
    histogramForComparison.Rebin(rebin)
    #get normalisation
    nShape = histogramForShape.Integral()
    nCompare = histogramForComparison.Integral()
    
    
def getShapeErrorHistogram(files,
                           histogramForShape='topReconstruction/backgroundShape/mttbar_conversions_withMETAndAsymJets',
                           histogramForComparison='topReconstruction/backgroundShape/mttbar_antiIsolated_withMETAndAsymJets',
                           rebin=1,
                           suffix=''):

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
