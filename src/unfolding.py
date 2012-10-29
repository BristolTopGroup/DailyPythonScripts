from ROOT import gSystem, gROOT, cout
gROOT.SetBatch(True)
gSystem.Load('/software/RooUnfold-1.1.1/libRooUnfold.so')
from ROOT import RooUnfoldResponse, RooUnfold, RooUnfoldBayes, RooUnfoldSvd
from ROOT import RooUnfoldBinByBin, RooUnfoldInvert, RooUnfoldTUnfold
from rootpy.io import File
#from rootpy.plotting import Hist
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from rootpy.utils import asrootpy

inputFile = File('../data/unfolding_merged.root', 'read')
h_truth = inputFile.unfoldingAnalyserElectronChannel.truth_AsymBins
h_measured = inputFile.unfoldingAnalyserElectronChannel.measured_AsymBins
h_response = inputFile.unfoldingAnalyserElectronChannel.response_AsymBins
#h_truth.Rebin(10)
#h_measured.Rebin(10)
#h_response.Rebin(10)


response = RooUnfoldResponse (h_measured, h_truth, h_response)
unfold= RooUnfoldBayes     (response, h_measured, 4)
hReco= unfold.Hreco();
unfold.PrintTable (cout, h_truth);
print 'converting'
h_unfolded = asrootpy(hReco)
print 'converted'
h_unfolded.SetMarkerStyle(20)
h_unfolded.SetColor('black')
h_truth.SetColor('red')
h_measured.SetColor('blue')
print list(h_unfolded)
#

plt.figure(figsize=(16, 10), dpi=100)
rplt.hist(h_truth, label='truth', stacked=False)
rplt.hist(h_measured, label='measured', stacked=False)
rplt.errorbar(h_unfolded, label='unfolded')
plt.xlabel('$E_{\mathrm{T}}^{miss}$')
plt.axis([0, 2000, 0, h_truth.GetMaximum()*1.2])
plt.ylabel('Events')
plt.title('Unfolding')
plt.legend()
plt.savefig('Unfolding.png')
print 'Done'
