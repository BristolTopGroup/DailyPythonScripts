## This file contains all the necessary calls to the rootplot API to produce
## the same set of plots that were created from the command-line.

## You can use this file to intercept the objects and manipulate them before
## the figure is saved, making any custom changes that are not possible from
## the command-line.

## 'objects' is a python dictionary containing all the elements used in the
## plot, including 'hists', 'legend', etc.
##   ex: objects['hists'] returns a list of histograms

try:
  ## the normal way to import rootplot
  from rootplot import plot, plotmpl
except ImportError:
  ## special import for CMSSW installations of rootplot
  from PhysicsTools.PythonAnalysis.rootplot import plot, plotmpl

import os
os.chdir('..')  # return to the directory with the ROOT files

figure, objects = plotmpl('/scratch/results/histogramFiles/data_3934.08pb_PFElectron_PF2PATJets_PFMET.root', '/scratch/results/histogramFiles/NewCode/TTJet_1959.75pb_PFElectron_PF2PATJets_PFMET.root', '/scratch/results/histogramFiles/NewCode/WJetsToLNu_1959.75pb_PFElectron_PF2PATJets_PFMET.root', 'topReconstruction/mttbar_withMETAndAsymJets_0orMoreBtag', 'rootplotmpl_config.py', rebin=50, xmin=1000.0, data=1, stack=True, underflow=True)
figure.savefig('plots/topReconstruction/mttbar_withMETAndAsymJets_0orMoreBtag', transparent=False, dpi=80)
