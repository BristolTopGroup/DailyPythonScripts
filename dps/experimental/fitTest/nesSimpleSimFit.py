'''
Created on 29 July 2014

@author: clement
'''
import unittest
from dps.utils.Fitting import Minuit, FitData, FitDataCollection
from rootpy.plotting import Hist, Canvas, Legend
from math import sqrt
from ROOT import TH1, gStyle, TVirtualPad, gROOT
from templates_electron import *
# from initial_values_electron_eta_afterSimFit  import *
from initial_values_electron_eta  import *
import pickle

# gROOT.SetBatch(1)

gStyle.SetOptStat(0)

class result():
    def __init__(self, variables, whichBin, dataTemplates, fitResults ):
        self.variables = variables
        self.whichBin = whichBin
        self.dataTemplates = dataTemplates
        self.fitResults = fitResults
        pass
    
    def producePickle(self):
        pickle = {
                  'variables' : self.variables,
                  'whichBin' : self.whichBin,
                  'dataTemplates' : self.dataTemplates,
                  }
        for result in self.fitResults:
            pickle[result] = round( self.fitResults[result][0], 5)
            pickle[result+'Error'] = round( self.fitResults[result][1], 5)
        return pickle
    pass

def getTemplatesFromFile( variable, whichBinFromFile ):
    t1Template = inputTemplates[variable][t1Name][whichBinFromFile]
    t2Template = inputTemplates[variable][t2Name][whichBinFromFile]
    t3Template = inputTemplates[variable][t3Name][whichBinFromFile]
    t4Template = inputTemplates[variable][t4Name][whichBinFromFile]
    return t1Template, t2Template, t3Template, t4Template

def getDataFromFile( variable, whichBinFromFile ):
    dataTemplate = inputTemplates[variable]['data'][whichBinFromFile]
    nBins = len( inputTemplates[variable]['data'][whichBinFromFile] )
    h_data = Hist(nBins,0,nBins, title = 'data' )
    for bin in range( 1, nBins+1 ):
        h_data.SetBinContent( bin, dataTemplate[bin-1])
        pass
    h_data.Scale(absolute_eta_initialValues['data'][whichBinFromFile][0])
    h_data.Sumw2()
    for bin in range( 1, nBins+1 ):
        h_data.SetBinError( bin, sqrt( h_data.GetBinContent( bin ) ) )
        pass
    return h_data

def getInitialValues(variable, whichBinFromFile):
    initialValues = {}
    initialValues[t1Name] = absolute_eta_initialValues[t1Name][whichBinFromFile][0]
    initialValues[t2Name] = absolute_eta_initialValues[t2Name][whichBinFromFile][0]
    initialValues[t3Name] = absolute_eta_initialValues[t3Name][whichBinFromFile][0]
    initialValues[t4Name] = absolute_eta_initialValues[t4Name][whichBinFromFile][0]

    for value in initialValues:
        if initialValues[value] <10.0:
            initialValues[value] == 10.0
            pass
        pass
    
    return initialValues

def getInitialValueErrors(variable, whichBinFromFile):
    initialValues = {}
    initialValues[t1Name] = absolute_eta_initialValues[t1Name][whichBinFromFile][1]
    initialValues[t2Name] = absolute_eta_initialValues[t2Name][whichBinFromFile][1]
    initialValues[t3Name] = absolute_eta_initialValues[t3Name][whichBinFromFile][1]
    initialValues[t4Name] = absolute_eta_initialValues[t4Name][whichBinFromFile][1]
    
    return initialValues

def plotResults( variable, data, templates, results ):
    
    resCan = Canvas()
    leg = Legend(nTemplates+2)
 
    data.Draw('PE')
    leg.AddEntry( data, style='LEP')
    nBins = len( inputTemplates[variable]['data'][whichBinFromFile] )
    h_tSumAfter=Hist(nBins,0,nBins, title ='after_'+variable )
    
    if useT1:
        plotTemplateAfter( templates[tNames['t1']], results[tNames['t1']][0], resCan, leg, h_tSumAfter )
        pass
    if useT2:
        plotTemplateAfter( templates[tNames['t2']], results[tNames['t2']][0], resCan, leg, h_tSumAfter )
        pass  
    if useT3:
        plotTemplateAfter( templates[tNames['t3']], results[tNames['t3']][0], resCan, leg, h_tSumAfter )
        pass  
    if useT4:
        plotTemplateAfter( templates[tNames['t4']], results[tNames['t4']][0], resCan, leg, h_tSumAfter )
        pass
    leg.Draw()
    
    h_tSumAfter.SetLineColor(2)
    h_tSumAfter.SetLineStyle(7)
    h_tSumAfter.SetMarkerSize(0)
    h_tSumAfter.Draw('SAME HIST')
    resCan.Update()
    
    return resCan, h_tSumAfter

def plotTemplateAfter( hBefore, fitResult, canvas, legend, h_tSumAfter ):
    hAfter = hBefore.Clone()
    hAfter.Scale( fitResult / hBefore.Integral() )
    canvas.cd()
    hAfter.Draw('SAME')
    legend.AddEntry( hAfter, style='L')
    h_tSumAfter += hAfter
    pass

def calculateChi2( data, fit ):
    chis = 0
    for bin in range(1, data.nbins()+1):
        chis += ( data.GetBinContent(bin) -  fit.GetBinContent(bin) ) **2
        pass
    return chis

def printResults( results, templates, data ):
    
    norm = 1.
    for t in templates:
        h = templates[t]
        norm +=  h.Integral() * scales[t]
    for t in templates:
        h = templates[t]
        tExp = h.Integral() * scales[t] * data.Integral() / norm
        print '%s : %.3g \t\t %.3g +/- %.3g' % (t, tExp, results[t][0], results[t][1])
        pass
    pass

useT1 = 1
useT2 = 1
useT3 = 1
useT4 = 1

nTemplates = useT1 + useT2 + useT3 + useT4

t1Scale = 1
t2Scale = 1
t3Scale = 1
t4Scale = 1

scales = {
  'TTJet' : t1Scale,
  'SingleTop' : t2Scale,
  'V+Jets' : t3Scale,
  'QCD' : t4Scale
}

t1Name = 'TTJet'
t2Name = 'SingleTop'
t3Name = 'V+Jets'
t4Name = 'QCD'
            
tNames = {
          't1' : t1Name,
          't2' : t2Name,
          't3' : t3Name,
          't4' : t4Name
          }
            
variableCombination = [
                        [
                        'absolute_eta',
                        ],
#                         [
#                         'M3',
#                         ],
#                         [
#                         'angle_bl',
#                         ],
#                         [
#                         'absolute_eta',
#                         'M3',
#                         ],
#                        [
#                         'absolute_eta',
#                         'angle_bl',
#                         ],
#                        [
#                         'angle_bl',
#                         'M3',
#                         ],
                        [
                        'absolute_eta',
                        'M3',
                        'angle_bl',
                        ],
                       ]
dataTemplates = {
                't1t2t3t4' :   {
                't1' : True,
                't2' : True,
                't3' : True,
                't4' : True,
                },
#                 't1' :    {
#                  't1' : True,
#                  't2' : False,
#                  't3' : False,
#                  't4' : False,
#                  },
#                  't2' :   {
#                 't1' : False,
#                 't2' : True,
#                 't3' : False,
#                 't4' : False,
#                 },
#                  't3' :   {
#                 't1' : False,
#                 't2' : True,
#                 't3' : False,
#                 't4' : False,
#                 },
#                 't4' :   {
#                 't1' : False,
#                 't2' : False,
#                 't3' : False,
#                 't4' : True,
#                 },
                 }
fillDataRandom = False
useRealData = True

if useRealData:
    dataTemplates = { 'data' :{}}

allResults = []

chi2ForVariableCombination = {}
for variables in variableCombination:
    chi2ForVariableCombination[str.join('_',variables)] = []
    chi2ForTemplateCombination = {}
    for useTemplateForData in dataTemplates:
        chi2ForTemplateCombination[useTemplateForData] = []
        chi2ForTemplate = []
        for whichBinFromFile in range(0,1):
            
            nVariables = len(variables)
            
            nBins = {}
            for variable in variables:
                nBins[variable] = len( inputTemplates[variable]['data'][whichBinFromFile] )
                pass
                
            h_t1 = {}
            h_t2 = {}
            h_t3 = {}
            h_t4 = {}
            h_data = {}
            
            templates = {}
            fitData = {}
            
            # Fill templates
            for variable in variables:
                h_t1[variable] = Hist(nBins[variable],0,nBins[variable], title =t1Name+'_'+variable )
                h_t2[variable] = Hist(nBins[variable],0,nBins[variable], title =t2Name+'_'+variable )
                h_t3[variable] = Hist(nBins[variable],0,nBins[variable], title =t3Name+'_'+variable )
                h_t4[variable] = Hist(nBins[variable],0,nBins[variable], title =t4Name+'_'+variable )
                h_data[variable] = Hist(nBins[variable],0,nBins[variable], title ='data_'+variable )
            
                templatesFromFile = getTemplatesFromFile(variable, whichBinFromFile)
                for bin in range( 1, nBins[variable]+1 ):
                    h_t1[variable].SetBinContent( bin, templatesFromFile[0][bin-1] )
                    h_t2[variable].SetBinContent( bin, templatesFromFile[1][bin-1] )
                    h_t3[variable].SetBinContent( bin, templatesFromFile[2][bin-1] )
                    h_t4[variable].SetBinContent( bin, templatesFromFile[3][bin-1] )
                    pass
                
                initialValues = getInitialValues( variable, whichBinFromFile )
                h_t1[variable].Scale( initialValues[t1Name] )
                h_t2[variable].Scale( initialValues[t2Name] )
                h_t3[variable].Scale( initialValues[t3Name] )
                h_t4[variable].Scale( initialValues[t4Name] )

                print '---> Initial Values'
                for t in tNames:
                    print tNames[t],initialValues[tNames[t]]
                    pass
                print '---'
                
                h_t1[variable].SetLineColor(4)
                h_t2[variable].SetLineColor(8)
                h_t3[variable].SetLineColor(6)
                h_t4[variable].SetLineColor(7)
                
                templates[variable] = {}
                if useT1: templates[variable][tNames['t1']] = h_t1[variable]
                if useT2: templates[variable][tNames['t2']] = h_t2[variable]
                if useT3: templates[variable][tNames['t3']] = h_t3[variable]
                if useT4: templates[variable][tNames['t4']] = h_t4[variable]
            
                # Fill data
                dataFillingHistogram=0
                if useRealData:
                    h_data[variable]= getDataFromFile( variable, whichBinFromFile )
                    pass
                else:
                    if dataTemplates[useTemplateForData]['t1']: dataFillingHistogram += h_t1[variable].Clone() * t1Scale
                    if dataTemplates[useTemplateForData]['t2']: dataFillingHistogram += h_t2[variable].Clone() * t2Scale
                    if dataTemplates[useTemplateForData]['t3']: dataFillingHistogram += h_t3[variable].Clone() * t3Scale
                    if dataTemplates[useTemplateForData]['t4']: dataFillingHistogram += h_t4[variable].Clone() * t4Scale
                
                    if fillDataRandom:
                        h_data[variable].FillRandom( dataFillingHistogram, int( absolute_eta_initialValues['data'][whichBinFromFile][0] ))
                    else:
                        h_data[variable] = dataFillingHistogram
                        
#                         if useT1: templates[variable]['t1'].Scale(1)
#                         if useT2: templates[variable]['t2'].Scale(1)
#                         if useT3: templates[variable]['t3'].Scale(1)
#                         if useT4: templates[variable]['t4'].Scale(10/templates[variable]['t4'].Integral())
#                         h_data[variable] = h_t1[variable] * 1.3
                #     h_data[variable].Scale(absolute_eta_initialValues['data'][whichBinFromFile][0] / h_data[variable].Integral() )


                blah = getInitialValueErrors( variable, whichBinFromFile )
#                 fitData[variable] = FitData( h_data[variable], templates[variable], fit_boundaries = ( 0, h_data[variable].nbins() ), normalisation_limits = blah )
                fitData[variable] = FitData( h_data[variable], templates[variable], fit_boundaries = ( 0, h_data[variable].nbins() ) )

                pass
            
            # Prepare fit
            fit_collection = FitDataCollection()
            for variable in variables:
                fit_collection.add( fitData[variable], variable)
            
            # Perform fit
            minuit_fitter = Minuit( fit_collection, method = 'logLikelihood', verbose = False )
            minuit_fitter.fit()
            
            
            # Do stuff after fit
            results = minuit_fitter.readResults()
            canvas={}
            chi2Total = 0
            for variable in variables:
                canvas[variable], fittedTemplate = plotResults( variable, h_data[variable], templates[variable], results )
                chi2 = calculateChi2( h_data[variable], fittedTemplate )
                print 'Chi2 :',chi2
                chi2Total += chi2
                pass
            
            printResults( results, templates[variables[0]], h_data[variables[0]] )
            
            allResults.append( result(variables, whichBinFromFile, dataTemplates[useTemplateForData], results ))
            # results['t1'][2].SetMarkerStyle(20)
            # results['t1'][2].Draw('AP')
#             raw_input()
            chi2ForTemplate.append(chi2Total)
            
            if chi2Total > 0.:
                print '---> PAUSING TO SHOW THE FIT'
                print str.join('_',variables)
                print useTemplateForData
                print whichBinFromFile
                if len(useTemplateForData) == 2:
                    print tNames[useTemplateForData]
                raw_input()
                pass
            pass
        chi2ForTemplateCombination[useTemplateForData] = chi2ForTemplate
        chi2ForVariableCombination[str.join('_',variables)] = chi2ForTemplateCombination
        pass
    pass


# outputList = {}
# index = 1
# for results in allResults:
#     outputList['%i' % index] = results.producePickle()
#     index+=1
#     
#     for template in results.fitResults:
#         print '%s %s : %.3g +/- %.3g' % ( template, tNames[template], results.fitResults[template][0], results.fitResults[template][1] )
#         pass
#     print '\n'

output = open('fitResults.pkl', 'wb')
pickle.dump( chi2ForVariableCombination, output)
output.close()