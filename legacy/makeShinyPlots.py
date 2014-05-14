#!/usr/bin/env python

# 0. Set ROOT into batch mode
# 1. set TDR style
# 2. read histograms from list (list including paths in file)


import ROOT
import HistPlotter


def plotFromFiles(files, plots):
    pass

def plotFromFolders(file, folders, plots):
    pass

def plotFromTargets(file, targets, plots):
    pass


if '__main__' in __name__:
    ROOT.gROOT.SetBatch(1)
    HistPlotter.setStyle()