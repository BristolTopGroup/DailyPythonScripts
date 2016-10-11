from __future__ import division

from optparse import OptionParser
import sys
from ROOT import *
import glob
from legacy.fileInfo import getROOTFiles
from dps.utils.ROOT_utils import get_histogram_from_file

pathToSkimHist = "topPairEPlusJetsSelectionAnalyser/consecutiveCuts_unweighted"

skips = ['TTJets_PowhegHerwigpp']



def getSkimmedEvents(files):

    totalInitialEvents = 0
    for file in files:
        skimHist = get_histogram_from_file( pathToSkimHist, file )
        firstBinContent = list(skimHist.y())[0]
        totalInitialEvents += firstBinContent

    return totalInitialEvents

if __name__ == "__main__":
    args = sys.argv
    if not len(args) == 2:
        print "Please specify a folder with ntuples in."
        sys.exit()
    
    allNtupleDirs = glob.glob(sys.argv[1]+'/*')
    samplesAndNorms = {}
    for path in allNtupleDirs:
        sample = path.split('/')[-1]
        if sample in skips: continue
        files = getROOTFiles(path)
        totalInitialEvents = getSkimmedEvents(files)
        samplesAndNorms[sample] = totalInitialEvents

    for sample in samplesAndNorms:
        print sample, samplesAndNorms[sample]