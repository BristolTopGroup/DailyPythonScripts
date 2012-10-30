from ROOT import gSystem, gROOT, cout, TH1F
gROOT.SetBatch(True)
gSystem.Load('/software/RooUnfold-1.1.1/libRooUnfold.so')
from ROOT import RooUnfoldResponse, RooUnfold, RooUnfoldBayes, RooUnfoldSvd
from ROOT import RooUnfoldBinByBin, RooUnfoldInvert, RooUnfoldTUnfold
from rootpy.io import File
from rootpy.plotting import Hist
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from rootpy.utils import asrootpy
from array import array

bins = array('d', [0, 25, 45, 70, 100, 1000])
nbins = len(bins) - 1
lumiweight = 164.5 * 5050 / 7543741.0
inputFile = File('../data/unfolding_merged.root', 'read')
h_truth = asrootpy(inputFile.unfoldingAnalyserElectronChannel.truth.Rebin(nbins, 'truth', bins))
h_measured = asrootpy(inputFile.unfoldingAnalyserElectronChannel.measured.Rebin(nbins, 'measured', bins))
h_response = inputFile.unfoldingAnalyserElectronChannel.response_AsymBins
h_truth.Scale(lumiweight)
h_measured.Scale(lumiweight)
h_response.Scale(lumiweight)
# h_truth.Rebin(10)
# h_measured.Rebin(10)
# h_response.Rebin(10)
#test values
h_data = Hist([0, 25, 45, 70, 100, 1000])
h_data.SetBinContent(1, 2146)
h_data.SetBinError(1, 145)
h_data.SetBinContent(2, 3399)
h_data.SetBinError(2, 254)
h_data.SetBinContent(3, 3723)
h_data.SetBinError(3, 69)
h_data.SetBinContent(4, 2256)
h_data.SetBinError(4, 53)
h_data.SetBinContent(5, 1722)
h_data.SetBinError(5, 91)


response = RooUnfoldResponse (h_measured, h_truth, h_response)
# unfold= RooUnfoldBayes     (response, h_data, 4)
unfold= RooUnfoldBinByBin     (response, h_data)
#unfold = RooUnfoldSvd(response, h_data, 6, 1000)
hReco = unfold.Hreco();
unfold.PrintTable (cout, h_truth);
h_unfolded = asrootpy(hReco)
h_unfolded.SetMarkerStyle(20)
h_unfolded.SetLineColor('black')
h_truth.SetLineColor('red')
h_measured.SetLineColor('blue')
h_data.SetLineColor('blue')

h_unfolded.SetFillStyle(0)
h_truth.SetFillStyle(0)
h_data.SetFillStyle(0)

plt.figure(figsize=(16, 10), dpi=100)
rplt.hist(h_truth, label=r'SM $\mathrm{t}\bar{\mathrm{t}}$ truth', stacked=False)
rplt.hist(h_data, label=r'$\mathrm{t}\bar{\mathrm{t}}$ from fit', stacked=False)
rplt.errorbar(h_unfolded, label='unfolded')
plt.xlabel('$E_{\mathrm{T}}^{miss}$')
plt.axis([0, 1000, 0, 60000])
plt.ylabel('Events')
plt.title('Unfolding')
plt.legend()
plt.savefig('Unfolding.png')

#plt.figure(figsize=(16, 10), dpi=100)
#rplt.hist(h_response, label='response matrix')
#h_response.Draw()
#plt.xlabel('reconstructed $E_{\mathrm{T}}^{miss}$')
#plt.ylabel('Generated $E_{\mathrm{T}}^{miss}$')
#plt.title('Response Matrix')
#plt.savefig('ResponseMatrix.png')
print 'Done'
