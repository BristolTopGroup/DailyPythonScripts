# # This file is the same as allplots.py, except that it uses multiprocessing
# # to make better use of machines with multiple cores

try:
    # # the normal way to import rootplot
    from rootplot import plot, plotmpl
    from rootplot.core import report_progress
except ImportError:
    # # special import for CMSSW installations of rootplot
    from PhysicsTools.PythonAnalysis.rootplot import plot, plotmpl
    from PhysicsTools.PythonAnalysis.rootplot.core import report_progress
import ROOT
import multiprocessing as multi
from Queue import Empty

import os
os.chdir( '..' )  # return to the directory with the ROOT files

calls = []

calls.append( """
figure, objects = plotmpl('/scratch/results/histogramFiles/data_3934.08pb_PFElectron_PF2PATJets_PFMET.root', '/scratch/results/histogramFiles/NewCode/TTJet_1959.75pb_PFElectron_PF2PATJets_PFMET.root', '/scratch/results/histogramFiles/NewCode/WJetsToLNu_1959.75pb_PFElectron_PF2PATJets_PFMET.root', 'topReconstruction/mttbar_withMETAndAsymJets_0orMoreBtag', 'rootplotmpl_config.py', rebin=50, xmin=1000.0, data=1, stack=True, underflow=True)
figure.savefig('plots/topReconstruction/mttbar_withMETAndAsymJets_0orMoreBtag', transparent=False, dpi=80)
""" )


queue = multi.JoinableQueue()
qglobals = multi.Manager().Namespace()
qglobals.nfinished = 0
qglobals.ntotal = len( calls )
for call in calls:
    queue.put( call )

def qfunc( queue, qglobals ):
    while True:
        try: mycall = queue.get( timeout = 5 )
        except ( Empty, IOError ): break
        exec( mycall )
        ROOT.gROOT.GetListOfCanvases().Clear()
        qglobals.nfinished += 1
        report_progress( qglobals.nfinished, qglobals.ntotal,
                        'plots', 'png' )
        queue.task_done()

for i in range( 8 ):
    p = multi.Process( target = qfunc, args = ( queue, qglobals ) )
    p.daemon = True
    p.start()
queue.join()
report_progress( len( calls ), len( calls ), 'plots', 'png' )
print ''
