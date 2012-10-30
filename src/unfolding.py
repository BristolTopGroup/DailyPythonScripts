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
temp = TH1F('temp', 'temp', len(bins) - 1, bins)
temp.SetBinContent(1, 2146)
temp.SetBinError(1, 145)
temp.SetBinContent(2, 3399)
temp.SetBinError(2, 254)
temp.SetBinContent(3, 3723)
temp.SetBinError(3, 69)
temp.SetBinContent(4, 2256)
temp.SetBinError(4, 53)
temp.SetBinContent(5, 1722)
temp.SetBinError(5, 91)

h_data = asrootpy(temp)



response = RooUnfoldResponse (h_measured, h_truth, h_response)
# unfold= RooUnfoldBayes     (response, h_measured, 4)
# unfold= RooUnfoldBinByBin     (response, h_measured)
unfold = RooUnfoldSvd(response, h_data, 6, 1000)
hReco = unfold.Hreco();
unfold.PrintTable (cout, h_truth);
print 'converting'
h_unfolded = asrootpy(hReco)
print 'converted'
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
plt.savefig('Unfolding_1k.png')
print 'Done'
