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
from tools.Unfolding import Unfolding

method = 'RooUnfoldSvd' # = 'RooUnfoldBayes | RooUnfoldSvd | RooUnfoldBinByBin | RooUnfoldInvert | RooUnfoldTUnfold

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
#test values
h_data = Hist(bins.tolist())
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

unfolding = Unfolding(h_truth, h_measured, h_response, method)
unfolding.unfold(h_data)
unfolding.saveUnfolding('Unfolding_' + method + '.png')

fakes = asrootpy(unfolding.unfoldResponse.Hfakes())
h_fakes = asrootpy(inputFile.unfoldingAnalyserElectronChannel.fake.Rebin(nbins, 'truth', bins))
h_fakes.Scale(lumiweight)
fakes.Scale(1000000)
fakes.SetColor('red')
h_fakes.SetColor('blue')
fakes.SetFillStyle(0)
h_fakes.SetFillStyle(0)

plt.figure(figsize=(16, 10), dpi=100)
rplt.hist(fakes, label=r'fakes from RM', stacked=False)
rplt.hist(h_fakes, label=r'fakes from MC', stacked=False)
plt.xlabel('$E_{\mathrm{T}}^{miss}$')
#plt.axis([0, 1000, 0, 5000])
plt.ylabel('Events')
plt.title('Unfolding')
plt.legend()
plt.savefig('Fakes.png')

print 'Done'
