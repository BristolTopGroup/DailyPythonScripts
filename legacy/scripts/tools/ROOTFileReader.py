from ROOT import TFile, gROOT
import tools.Log as Log
from config.sampleSummations import btag_bins_inclusive, btag_sums

openRootFile = TFile.Open
gcd = gROOT.cd
#Reads a single histogram from a single file
def getHistogramFromFile(histname, filename):
    rootFile = TFile.Open(filename)
    getHist = rootFile.Get
    testIfFalidFile(rootFile, filename)
    
    btag_found = ''
    for btag in btag_bins_inclusive:
        if btag in histname:
            btag_found = btag
            break
    rootHist = None
#    sumEvents = 0
    if btag_found == '':
        rootHist = getHist(histname)
        if not isValidHist(rootHist, histname, filename):
            return
    else:
        listOfExclusiveBins = btag_sums[btag_found]
        exclhists = []
        
        for excbin in listOfExclusiveBins:
            hist = getHist(histname.replace(btag_found, excbin))
            if not isValidHist(hist, histname.replace(btag_found, excbin), filename):
                return
            exclhists.append(hist)
        rootHist = exclhists[0].Clone()
        
        for hist in exclhists[1:]:
            rootHist.Add(hist)
    
    gcd()
    histogram = rootHist.Clone()
    rootFile.Close()
    
    return histogram 
def testIfFalidFile(rootFile, filename):
    if not rootFile:
        Log.logErrorMessage('Could not find rootFile: ' + filename)
        
def isValidHist(rootHist, histname, filename):
    if not rootHist:
        Log.logErrorMessage('Histogram \n"%s" \ncould not be found in rootFile:\n%s' % (histname, filename))
        return False
    return True
        
#Reads a single histogram from each given rootFile
#and returns a dictionary with the same naming as 'files'
def getHistogramDictionary(histname, files={}):
    hists = {}
    for sample, filename in files.iteritems():
        hists[sample] = getHistogramFromFile(histname, filename)
    return hists

#Reads a list of histograms from each given file
def getHistogramsFromFiles(histnames=[], files={}, verbose = False):
    histograms = {}
    nHistograms = 0
    for sample, filename in files.iteritems():
        rootFile = openRootFile(filename)
        getHist = rootFile.Get
        histograms[sample] = {}
        for histname in histnames:
            btag_found = ''
            for btag in btag_bins_inclusive:
                if btag in histname:
                    btag_found = btag
                    break
            rootHist = None
            if btag_found == '':
                rootHist = getHist(histname)
                if not isValidHist(rootHist, histname, filename):
                    continue
            else:
                listOfExclusiveBins = btag_sums[btag_found]
                exclhists = []
                for excbin in listOfExclusiveBins:
                    hist = getHist(histname.replace(btag_found, excbin))
                    if not isValidHist(hist, histname.replace(btag_found, excbin), filename):
                        continue
                    exclhists.append(hist)
                rootHist = exclhists[0].Clone()
                for hist in exclhists[1:]:
                    rootHist.Add(hist)
            gcd()
            nHistograms += 1
            histograms[sample][histname] = rootHist.Clone()
            if verbose and nHistograms % 5000 == 0:
                print 'Read', nHistograms, 'histograms'
        rootFile.Close()
    return histograms


