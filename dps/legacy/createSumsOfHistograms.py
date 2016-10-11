#0. Open histogram files 
#1. Create inclusive b-tag and jet- multiplicity bins if not present
#2. Write file to current files
#3. add files up (hadd) to create the sum of samples (QCD, singleTop, W+Jets, allMC)
import FILES
from ROOT import TFile
from rootpy.io import File
import dps.utils.ROOTFileReader as fileReader
from optparse import OptionParser

btag_bins_available = ['0btag', '1btag', '2btags', '3btags', '4orMoreBtags'
                       ]
btag_bins_inclusive = ['0orMoreBtag', '1orMoreBtag', '2orMoreBtags', '3orMoreBtags']

def sumExclusiveHistogramsInFile(filename):
    testfile = File(filename, 'read')
    newHistograms = {}
    histExists = newHistograms.has_key
    
    nTimes = 1000000000
    nthTime = 0
    nHistograms = 0
    listOfAllHistograms = []
    addToList = listOfAllHistograms.append
    for folder, emptyThing, histograms in testfile:
        for histogram in histograms:
            nHistograms += 1
            currentPath = folder + '/' + histogram
            addToList(currentPath)
    print 'Loading', nHistograms, 'histograms'
    allHistograms = fileReader.getHistogramsFromFiles(listOfAllHistograms, {'Test':filename}, True)['Test']
    print 'Loaded', nHistograms, 'histograms'
    
    nHistograms = 0
    for histogramName, histogram in allHistograms.iteritems():
        nthTime += 1
        if nthTime >= nTimes:
            continue
        nHistograms += 1
        isBtagBinnedHist = False
        if nHistograms % 5000 == 0:
            print 'Done', nHistograms, 'histograms'
        currentHist = histogramName
        
        for btag_bin in btag_bins_available:
            if btag_bin in histogramName:
                isBtagBinnedHist = True
                currentHist = histogramName.replace(btag_bin, '')
        if not isBtagBinnedHist:
            continue 
        
        currentPath = currentHist
        if histExists(currentHist):#already have it
            continue
        inclBinHistograms = {}
        for exclBin in range(len(btag_bins_inclusive)):
    #        print 'Starting with', currentPath + btag_bins_available[exclBin]
            newhist = allHistograms[currentPath + btag_bins_available[exclBin]]
            for availBin in range(exclBin + 1, len(btag_bins_available)):
    #            print '>>>>> Adding:', currentPath + btag_bins_available[availBin]
                addThis = allHistograms[currentPath + btag_bins_available[availBin]] 
                newhist.Add(addThis)
            inclBinHistograms[currentPath + btag_bins_inclusive[exclBin]] = newhist
        newHistograms[currentPath] = inclBinHistograms
    testfile.Close()
    print 'Done', nHistograms, 'histograms'
    
    
    rootFile = TFile.Open(filename, 'UPDATE')
    cd = rootFile.Cd
    rootFile.cd()
    for histFullPath, histogramDict in newHistograms.iteritems():
        currentHist = histFullPath.split('/')[-1]
        path = histFullPath.replace(currentHist, '')
        cd('/' + path)
        for histname, histogram in histogramDict.iteritems():
            currentHist = histname.split('/')[-1]
            histogram.Write(currentHist)
    rootFile.Write()
    rootFile.Close()  
    del allHistograms 
    del rootFile
    del testfile
    del newHistograms
    
def cleanFile(filename):
    testfile = File(filename, 'update')
    nHistograms = 0
    print "Deleting inclusive bin histograms histograms"
    for folder, emptyThing, histograms in testfile:
        for histogram in histograms:
            currentPath = folder + '/' + histogram
            for btag in btag_bins_inclusive:
                if btag in histogram:
                    nHistograms += 1
#                    print 'Deleting:', currentPath
                    testfile.Delete(currentPath + ';*')
    print 'Deleted', nHistograms, 'histograms'
    print 'Closing file', filename
    testfile.Close()
    print 'Closed file'
                
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-s", "--sample", dest="sample", default='ElectronHad',
                  help="set sample to be combined. Available samples: " + ','.join(FILES.files.keys()))
    parser.add_option("-f", "--fileset", dest="fileset", default='central',
                  help="set of files to be combined")
    (options, args) = parser.parse_args()
    fileset = FILES.files
    if options.fileset == 'PU_down':
        fileset = FILES.files_PU_down
    elif options.fileset == 'PU_up':
        fileset = FILES.files_PU_up
    elif options.fileset == 'PDF':
        fileset = FILES.files_PDF_weights
    elif options.fileset == 'JES_down':
        fileset = FILES.files_JES_down
    elif options.fileset == 'JES_up':
        fileset = FILES.files_JES_up
    elif options.fileset == 'BJet_down':
        fileset = FILES.files_BJet_down
    elif options.fileset == 'BJet_up':
        fileset = FILES.files_BJet_up
    elif options.fileset == 'LightJet_down':
        fileset = FILES.files_LightJet_down
    elif options.fileset == 'LightJet_up':
        fileset = FILES.files_LightJet_up
    elif options.fileset == 'central':
        fileset = FILES.files
    else:
        print 'Do not recognise fileset'
        import sys
        sys.exit
    print 'Doing file set', options.fileset
    
    for sample in fileset.keys():
        print 'Doing sample', sample
        filename = fileset[sample]
        print 'Doing file:', filename
        cleanFile(filename)
#        sumExclusiveHistogramsInFile(filename)
