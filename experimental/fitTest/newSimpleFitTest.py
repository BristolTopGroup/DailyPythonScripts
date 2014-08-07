'''
Created on 20 July 2014

@author: clement
'''
import unittest
from tools.Fitting import Minuit, FitData, FitDataCollection
from rootpy.plotting import Hist, Canvas, Legend
from math import sqrt
from ROOT import TH1, gStyle, TVirtualPad
from templates_electron import *
from initial_values_electron_eta  import *

gStyle.SetOptStat(0)

useT1 = 1
useT2 = 1
useT3 = 1
useT4 = 1

useTemplatesFromFile = True
useDataFromFile = False
variable = 'absolute_eta'
whichBinFromFile = 1
t1Name = 'TTJet'
t2Name = 'SingleTop'
t3Name = 'V+Jets'
t4Name = 'QCD'

nBins = len( inputTemplates[variable]['data'][whichBinFromFile] )

drawScancan = False

nTemplates = useT1 + useT2 + useT3 + useT4

nData = 20000
nTemplate = 1000000
t1Scale = 1
t2Scale = 1
t3Scale = 1
t4Scale = 1

# import numpy as np

def getMax(histograms):
    maximum = 0
    for hist in histograms:
        current_max = hist.GetMaximum()
        if current_max > maximum:
            maximum = current_max
    return maximum


def checkFitResults( target, fitResult ):
    if not (abs( target - fitResult[0] ) < fitResult[1]):
        if (abs( target - fitResult[0] ) < 2*fitResult[1]):
            print 'Almost ok FIT'
        else:
            print 'BAD FIT'
            print target, fitResult[0]
        pass
    return

def getTemplatesFromFile():
    t1Template = inputTemplates[variable][t1Name][whichBinFromFile]
    t2Template = inputTemplates[variable][t2Name][whichBinFromFile]
    t3Template = inputTemplates[variable][t3Name][whichBinFromFile]
    t4Template = inputTemplates[variable][t4Name][whichBinFromFile]
    return t1Template, t2Template, t3Template, t4Template

def getDataFromFile():
    dataTemplate = inputTemplates[variable]['data'][whichBinFromFile]
    h_data = Hist(nBins,0,nBins, title = 'data' )
    for bin in range( 1, nBins+1 ):
        h_data.SetBinContent( bin, dataTemplate[bin-1])
        pass
    h_data.Scale(absolute_eta_initialValues['data'][whichBinFromFile][0])
    return h_data
    
# Define the templates
h_t1Shape = Hist(nBins,0,nBins, title ='t1Shape' )
h_t2Shape = Hist(nBins,0,nBins, title ='t2Shape' )
h_t3Shape = Hist(nBins,0,nBins, title ='t3Shape' )
h_t4Shape = Hist(nBins,0,nBins, title ='t4Shape' )

h_t1 = Hist(nBins,0,nBins, title =t1Name )
h_t2 = Hist(nBins,0,nBins, title =t2Name )
h_t3 = Hist(nBins,0,nBins, title =t3Name )
h_t4 = Hist(nBins,0,nBins, title =t4Name )
h_data = Hist(nBins,0,nBins, title = 'data' )


if useTemplatesFromFile:
    templates = getTemplatesFromFile()
    
    for bin in range( 1, nBins+1 ):
        h_t1.SetBinContent( bin, templates[0][bin-1] )
        h_t2.SetBinContent( bin, templates[1][bin-1] )
        h_t3.SetBinContent( bin, templates[2][bin-1] )
        h_t4.SetBinContent( bin, templates[3][bin-1] )
        pass

    h_t1.Scale( absolute_eta_initialValues[t1Name][whichBinFromFile][0])
    h_t2.Scale( absolute_eta_initialValues[t2Name][whichBinFromFile][0])
    h_t3.Scale( absolute_eta_initialValues[t3Name][whichBinFromFile][0])
    h_t4.Scale( absolute_eta_initialValues[t4Name][whichBinFromFile][0])
else :
    # Fill the histograms
    h_t1Shape.SetBinContent(1,20)
    h_t1Shape.SetBinContent(2,20)
    h_t1Shape.SetBinContent(3,20)
    h_t1Shape.SetBinContent(4,50)
    h_t1Shape.SetBinContent(5,50)
    h_t1Shape.SetBinContent(6,100)
    h_t1Shape.SetBinContent(7,100)
    h_t1Shape.SetBinContent(8,50)
    h_t1Shape.SetBinContent(9,50)
    h_t1Shape.SetBinContent(10,40)
      
    h_t2Shape.SetBinContent(1,0)
    h_t2Shape.SetBinContent(2,90)
    h_t2Shape.SetBinContent(3,0)
    h_t2Shape.SetBinContent(4,30)
    h_t2Shape.SetBinContent(5,30)
    h_t2Shape.SetBinContent(6,20)
    h_t2Shape.SetBinContent(7,20)
    h_t2Shape.SetBinContent(8,20)
    h_t2Shape.SetBinContent(9,10)
    h_t2Shape.SetBinContent(10,10)
     
    h_t3Shape.SetBinContent(1,20)
    h_t3Shape.SetBinContent(2,20)
    h_t3Shape.SetBinContent(3,20)
    h_t3Shape.SetBinContent(4,50)
    h_t3Shape.SetBinContent(5,50)
    h_t3Shape.SetBinContent(6,100)
    h_t3Shape.SetBinContent(7,100)
    h_t3Shape.SetBinContent(8,50)
    h_t3Shape.SetBinContent(9,50)
    h_t3Shape.SetBinContent(10,40)
    if useT1: h_t1.FillRandom( h_t1Shape, nTemplate )
    if useT2: h_t2.FillRandom( h_t2Shape, nTemplate )
    if useT3: h_t3.FillRandom( h_t3Shape, nTemplate )
    if useT4: h_t4.FillRandom( h_t4Shape, nTemplate )   
    pass

# h_data.Scale(nData)
# h_data.FillRandom(  t1Scale * h_t1Shape + t2Scale * h_t2Shape + t3Scale * h_t3Shape, nData )
fillingHistogram = 0
if useT1: fillingHistogram += t1Scale * h_t1Shape
if useT2: fillingHistogram += t2Scale * h_t2Shape
if useT3: fillingHistogram += t3Scale * h_t3Shape
if useT4: fillingHistogram += t4Scale * h_t4Shape


if useDataFromFile:
    h_data = getDataFromFile()
else:
#     h_data.FillRandom(  ( h_t1 * t1Scale + h_t2 * t2Scale + h_t3 * t3Scale ), nData )
    # print 'Integral :',h_data.Integral()
    # h_data = h_t1 * t1Scale + h_t2 * t2Scale + h_t3 * t3Scale
#     h_data.FillRandom( h_t3, nData )
    dataFillingHistogram=0
    if useT1: dataFillingHistogram += h_t1.Clone()
    if useT2: dataFillingHistogram += h_t2.Clone()
    if useT3: dataFillingHistogram += h_t3.Clone()
    if useT4: dataFillingHistogram += h_t4.Clone()
#     h_data = dataFillingHistogram
    h_data = h_t1 * 1.3
#     h_data.Scale(absolute_eta_initialValues['data'][whichBinFromFile][0] / h_data.Integral() )
#     h_data.FillRandom( dataFillingHistogram, int(absolute_eta_initialValues['data'][whichBinFromFile][0]) )
#     h_data.FillRandom( dataFillingHistogram, int(absolute_eta_initialValues['data'][whichBinFromFile][0]) )
    pass

# for bin in range (0,nBins+1):
# #     h_data.SetBinContent( bin, t1Scale * h_t1.GetBinContent( bin ) + t2Scale*h_t2.GetBinContent( bin ) + t3Scale*h_t3.GetBinContent( bin ) )
#     h_data.SetBinError(bin, sqrt(h_data.GetBinContent(bin)))
#     h_t1.SetBinError( bin, sqrt(h_t1.GetBinContent(bin)))
#     h_t2.SetBinError( bin, sqrt(h_t2.GetBinContent(bin)))
#     h_t3.SetBinError( bin, sqrt(h_t3.GetBinContent(bin)))
#     h_t4.SetBinError( bin, sqrt(h_t4.GetBinContent(bin)))
#     pass


# Make pretty
h_t1.SetLineColor(4)
h_t2.SetLineColor(8)
h_t3.SetLineColor(6)
h_t4.SetLineColor(7)
h_data.SetLineColor(1)
h_data.SetMarkerColor(1)

ymax = getMax( [h_data, h_t1, h_t2, h_t3] )
ymax = ymax*1.1
h_data.GetYaxis().SetRangeUser(0,ymax)
h_t1.GetYaxis().SetRangeUser(0,ymax)
h_t2.GetYaxis().SetRangeUser(0,ymax)
h_t3.GetYaxis().SetRangeUser(0,ymax)
h_t4.GetYaxis().SetRangeUser(0,ymax)

c = Canvas()
c.Divide(2)
c.cd(1)
h_data.Draw('PE')
h_t1.Draw('SAME HIST')
h_t2.Draw('SAME HIST')
h_t3.Draw('SAME HIST')
h_t4.Draw('SAME HIST')

templates = {
             }
if useT1: templates['t1'] = h_t1
if useT2: templates['t2'] = h_t2
if useT3: templates['t3'] = h_t3
if useT4: templates['t4'] = h_t4

fit_data = FitData( h_data, templates, fit_boundaries = ( 0, h_data.nbins() ) )

fit_collection = FitDataCollection()
fit_collection.add( fit_data )

minuit_fitter = Minuit( fit_collection, method = 'logLikelihood', verbose = True )
minuit_fitter.fit()

results = minuit_fitter.readResults()

c.cd(2)
ymax = h_data.GetBinContent( h_data.GetMaximumBin() ) * 1.1
h_data.GetYaxis().SetRangeUser(0,ymax)
h_data.Draw('PE')
leg = Legend(nTemplates+2)
leg.AddEntry( h_data, style='LEP')
h_tSumAfter=0

print '----> Target \t Fit Result'
if useT1:
    h_t1After = h_t1.Clone()
    h_t1After.Scale( results['t1'][0] / h_t1.Integral() )
    h_t1After.Draw('SAME HIST')
    h_tSumAfter += h_t1After
    leg.AddEntry( h_t1After, style='L')
    t1AfterCont = h_t1.Integral() * t1Scale * h_data.Integral() / ( h_t1.Integral() * t1Scale + h_t2.Integral() * t2Scale + h_t3.Integral() * t3Scale )
    print '%s : \t %.3g \t %.3g +/- %.3g' % ( t1Name, t1AfterCont,results['t1'][0],results['t1'][1] )
    scan1 = results['t1'][2]
    pass
if useT2:
    h_t2After = h_t2.Clone()
    h_t2After.Scale( results['t2'][0] / h_t2.Integral() )
    h_t2After.Draw('SAME HIST')
    h_tSumAfter += h_t2After
    leg.AddEntry( h_t2After, style='L')
    t2AfterCont = h_t2.Integral() * t2Scale * h_data.Integral() / ( h_t1.Integral() * t1Scale + h_t2.Integral() * t2Scale + h_t3.Integral() * t3Scale )
    print '%s : \t %.3g \t %.3g +/- %.3g' % ( t2Name, t2AfterCont,results['t2'][0],results['t2'][1] )

    scan2 = results['t2'][2]
    pass
if useT3:
    h_t3After = h_t3.Clone()
    h_t3After.Scale( results['t3'][0] / h_t3.Integral() )
    h_t3After.Draw('SAME HIST')
    h_tSumAfter += h_t3After
    leg.AddEntry( h_t3After, style='L')
    t3AfterCont = h_t3.Integral() * t3Scale * h_data.Integral() / ( h_t1.Integral() * t1Scale + h_t2.Integral() * t2Scale + h_t3.Integral() * t3Scale )
    print '%s : \t %.3g \t %.3g +/- %.3g' % ( t3Name, t3AfterCont, results['t3'][0],results['t3'][1] )
    scan3 = results['t3'][2]
    pass   
if useT4:
    h_t4After = h_t4.Clone()
    h_t4After.Scale( results['t4'][0] / h_t4.Integral() )
    h_t4After.Draw('SAME HIST')
    h_tSumAfter += h_t4After
    leg.AddEntry( h_t4After, style='L')
    t4AfterCont = h_t4.Integral() * t4Scale * h_data.Integral() / ( h_t1.Integral() * t1Scale + h_t2.Integral() * t2Scale + h_t4.Integral() * t4Scale )
    print '%s : \t %.3g \t %.3g +/- %.3g' % ( t4Name, t4AfterCont, results['t4'][0],results['t4'][1] )
    scan4 = results['t4'][2]
    pass   
h_tSumAfter.SetLineColor(2)
h_tSumAfter.SetLineStyle(7)
h_tSumAfter.SetMarkerSize(0)
h_tSumAfter.Draw('SAME HIST')

chis = 0
for bin in range(1, h_data.nbins()+1):
#     print ( h_data.GetBinContent(bin) - h_tSumAfter.GetBinContent(bin) )**2
    chis += ( h_data.GetBinContent(bin) - h_tSumAfter.GetBinContent(bin) )**2
    pass
print 'CHI 2 :',chis

# ymax = getMax( [h_data, h_t1After, h_t2After, h_t3After] )
# h_data.GetYaxis().SetRangeUser(0,ymax)
# h_t1After.GetYaxis().SetRangeUser(0,ymax)
# h_t2After.GetYaxis().SetRangeUser(0,ymax)
# h_t3After.GetYaxis().SetRangeUser(0,ymax)

leg.AddEntry( h_tSumAfter, style='L', label='Sum')
leg.Draw()

c.Update()

if drawScancan:
    scancan = Canvas()
    scancan.Divide(nTemplates)
    scancan.SetLogy()
    nCan = 1
    if useT1:
        scancan.cd(nCan)
    #     scan1.SetMaximum(scan1.GetMaximum()/100)
        scan1.SetMarkerStyle(20)
    #     scan1.SetMarkerSize(1)
        scan1.Draw('AP')
        nCan = nCan+1
        pass
    if useT2:
        scancan.cd(nCan)
        scan2.SetMaximum(1000)
        scan2.SetMarkerStyle(20)
    #     scan2.SetMarkerSize(20)
        scan2.Draw('AP')
        nCan = nCan+1
        pass
    if useT3:
        scancan.cd(nCan)
        scan3.SetMaximum(1000)
        scan3.SetMarkerStyle(20)
    #     scan3.SetMarkerSize(20)
        scan3.Draw('AP')
        nCan = nCan+1
        pass
    if useT4:
        scancan.cd(nCan)
        scan4.SetMaximum(1000)
        scan4.SetMarkerStyle(20)
    #     scan3.SetMarkerSize(20)
        scan4.Draw('AP')
        nCan = nCan+1
        pass
    scancan.Update()
    pass

# contour1 = results['contour'][0]
# contour2 = results['contour'][1]
# concan = Canvas()
# contour2.SetFillColor(42)
# contour2.Draw('ALF')
# contour1.SetFillColor(38)
# contour1.Draw('LF')
# concan.Update()


# checkFitResults( t1AfterCont, results['t1'] )
# checkFitResults( t2AfterCont, results['t2'] )
# checkFitResults( t3AfterCont, results['t3'] )

raw_input()
