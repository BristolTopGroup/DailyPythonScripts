from __future__ import division

from optparse import OptionParser
import sys
from fileInfo import *
from ROOT import *
from mergeROOTFilesWithCompression import getProcess

pathToSkimHist = "EventFilter/EventCounter"
pathToEventTree = "rootTupleTree/tree"

def getSkimmedEvents(files):
    skimInfo = getSkimInfo(files)
    skimHist = skimInfo[0]
    
    #TODO: do this part dynamic in case the skim changes. The skim has the names set for the bins!
    numberOfTotalEvents = skimHist.GetBinContent(1)
    numberOfEventsPassingHBHENoiseFilter = skimHist.GetBinContent(2)
    numberOfEventsPassingScrapingVeto = skimHist.GetBinContent(3)
    numberOfEventsHavingGoodPrimaryVertex = skimHist.GetBinContent(4)
    numberOfEventsPassingElectronCuts = skimHist.GetBinContent(5)
    numberOfEventsPassingJetCuts = skimHist.GetBinContent(6)
    
    numberOfEventsAfterAllFilters = skimInfo[1]
    electronSkimEfficiency = numberOfEventsPassingHBHENoiseFilter / numberOfTotalEvents
    TotalSkimEfficiency = numberOfEventsAfterAllFilters / numberOfTotalEvents
    
    
    dataSetDescription, totals, lastStep = {}, {}, {}
    dataSetDescription['numberOfEvents'] = numberOfTotalEvents
    dataSetDescription['numberOfEventsAfterSkim'] = numberOfEventsAfterAllFilters
    dataSetDescription['totalSkimEfficiency'] = dataSetDescription['numberOfEventsAfterSkim'] / dataSetDescription['numberOfEvents']
    dataSetDescription['HBHENoiseFilter'] = int(numberOfEventsPassingHBHENoiseFilter)
    dataSetDescription['ScrapingVeto'] = int(numberOfEventsPassingScrapingVeto)
    dataSetDescription['GoodPrimaryVertex'] = int(numberOfEventsHavingGoodPrimaryVertex)
    dataSetDescription['ElectronCuts'] = int(numberOfEventsPassingElectronCuts)
    dataSetDescription['JetCuts'] = int(numberOfEventsPassingJetCuts)
    
    
    totals['HBHENoiseFilter'] = numberOfEventsPassingHBHENoiseFilter / numberOfTotalEvents
    totals['ScrapingVeto'] = numberOfEventsPassingScrapingVeto / numberOfTotalEvents
    totals['GoodPrimaryVertex'] = numberOfEventsHavingGoodPrimaryVertex / numberOfTotalEvents
    totals['ElectronCuts'] = numberOfEventsPassingElectronCuts / numberOfTotalEvents
    totals['JetCuts'] = numberOfEventsPassingJetCuts / numberOfTotalEvents
    
    lastStep['HBHENoiseFilter'] = numberOfEventsPassingHBHENoiseFilter / numberOfTotalEvents
    lastStep['ScrapingVeto'] = numberOfEventsPassingScrapingVeto / numberOfEventsPassingHBHENoiseFilter
    lastStep['GoodPrimaryVertex'] = numberOfEventsHavingGoodPrimaryVertex / numberOfEventsPassingScrapingVeto
    lastStep['ElectronCuts'] = numberOfEventsPassingElectronCuts / numberOfEventsHavingGoodPrimaryVertex
    lastStep['JetCuts'] = numberOfEventsPassingJetCuts / numberOfEventsPassingElectronCuts
    
    return dataSetDescription, totals, lastStep

#    return {'total': numberOfTotalEvents,
#            'skimmed':numberOfEventsAfterAllFilters,
#            'electronSkimEfficiency':electronSkimEfficiency,
#            'afterSkimAndNoiseFilter':numberOfEventsAfterAllFilters,
#            'totalSkimEfficiency':TotalSkimEfficiency}
            
def getSkimInfo(files):
    skimHist = None
    eventBranch = None
    eventTree = None
    n_skim = 0
    TfOpen = TFile.Open
    gcd = gROOT.cd
    
    for file in files:
        f = TfOpen(file)
        gcd()
        eventTree = f.Get(pathToEventTree)
        if eventTree is None:
            print 'Could not find tree', pathToEventTree, 'in file', file
        else:
            eventBranch = eventTree.GetBranch('Event.Number')
            
        if eventBranch is None:
            print 'Could not find branch', pathToEventTree + '/Event.Number', 'in file', file
        else:
            n_skim += eventBranch.GetEntries()
        
        if skimHist is None:
            skimHist = f.Get(pathToSkimHist)
            if skimHist is None:
                print 'Could not find histogram', pathToSkimHist, 'in file', file
                continue
        else:
            hist = f.Get(pathToSkimHist)
            if hist is None:
                print 'Could not find histogram', pathToSkimHist, 'in file', file
                continue
            skimHist.Add(hist)
    return (skimHist, n_skim)


def formatSkimEfficiencies(dataSetDescription, totals, lastStep):
    print 'Local merged files:', dataSetDescription['path']
    print
    print 'Total number of files:', int(dataSetDescription['numberOfFiles'])
    print
    print 'Process recognised:', dataSetDescription['process']
    print
    print 'Total number of events:', int(dataSetDescription['numberOfEvents'])
    print
    print
    print '| *Filter Name* | *# passing* | *efficiency(total) in %* | *efficiency(last step) in %* |'
    print '| HBHENoiseFilter  | ', dataSetDescription['HBHENoiseFilter'], '| ', totals['HBHENoiseFilter'], '| ', lastStep['HBHENoiseFilter'], '|'
    print '| ScrapingVeto  | ', dataSetDescription['ScrapingVeto'], '| ', totals['ScrapingVeto'], '| ', lastStep['ScrapingVeto'], '|'
    print '| GoodPrimaryVertex  | ', dataSetDescription['GoodPrimaryVertex'], '| ', totals['GoodPrimaryVertex'], '| ', lastStep['GoodPrimaryVertex'], '|'
    print '| ElectronCuts  | ', dataSetDescription['ElectronCuts'], '| ', totals['ElectronCuts'], '| ', lastStep['ElectronCuts'], '|'
    print '| JetCuts  | ', dataSetDescription['JetCuts'], '| ', totals['JetCuts'], '| ', lastStep['JetCuts'], '|'    
    print '| total | ', int(dataSetDescription['numberOfEventsAfterSkim']), '| ',
    print dataSetDescription['totalSkimEfficiency'], '|  --- |'

            

if __name__ == "__main__":
    args = sys.argv
    if not len(args) == 2:
        print "Please specify a folder to merge files in."
        sys.exit()
        
    path = sys.argv[1]
    files = getROOTFiles(path)
    dataSetDescription, totals, lastStep = getSkimmedEvents(files)
    dataSetDescription['numberOfFiles'] = len(files)
    dataSetDescription['process'] = getProcess(files[0])
    dataSetDescription['path'] = path
    formatSkimEfficiencies(dataSetDescription, totals, lastStep)
    
#    print '=' * 100
#    print '{0:70} : {1:15d}'.format('Total number of files', len(files))
#    print '{0:70} : {1:15s}'.format('Process recognised', getProcess(files[0]))
#    print '{0:70} : {1:15d}'.format('Total number of events', int(events['total']))
#    print '{0:70} : {1:15d}'.format('Number of events after electron skim', int(events['skimmed']))
#    print '{0:70} : {1:15d}'.format('Number of events after electron skim and HBHE noise filter', events['afterSkimAndNoiseFilter'])
#    print
#    print '{0:70} : {1:15f}'.format('Electron skim efficiency', events['electronSkimEfficiency'])
#    print '{0:70} : {1:15f}'.format('Total skim efficiency', events['totalSkimEfficiency'])
#    print '=' * 100
