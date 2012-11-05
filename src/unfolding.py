from ROOT import gSystem, gROOT, cout, TH1F
gROOT.SetBatch(True)
#gSystem.Load('/software/RooUnfold-1.1.1/libRooUnfold.so')
#from ROOT import RooUnfoldResponse, RooUnfold, RooUnfoldBayes, RooUnfoldSvd
#from ROOT import RooUnfoldBinByBin, RooUnfoldInvert, RooUnfoldTUnfold
from rootpy.io import File
from rootpy.plotting import Hist
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from rootpy.utils import asrootpy
from array import array
from tools.Unfolding import Unfolding
import config.RooUnfold as unfoldCfg

def saveClosureTest(unfolding, outputfile, **kwargs):
    
    if not unfolding.unfolded_closure:
        print 'Run closureTest function first'
        return
    setDrawStyles(unfolding)
    # TODO: change this to be more generic
    plt.figure(figsize=(16, 10), dpi=100)
    rplt.hist(unfolding.truth, label=r'truth', stacked=False)
    rplt.hist(unfolding.measured, label=r'measured', stacked=False)
    rplt.errorbar(unfolding.unfolded_closure, label='unfolded')
    plt.xlabel('$E_{\mathrm{T}}^{miss}$')
    plt.ylabel('Events')
    plt.title('Unfolding closure test')
    plt.legend()
    plt.savefig('Unfolding_' + unfolding.method + '_closureTest.png')
    
def saveUnfolding(unfolding, outputfile, **kwargs):
    if not unfolding.unfolded_data:
        print 'Run unfold function first'
        return
    setDrawStyles(unfolding)
    # TODO: change this to be more generic
    plt.figure(figsize=(16, 10), dpi=100)
    rplt.hist(unfolding.truth, label=r'SM $\mathrm{t}\bar{\mathrm{t}}$ truth', stacked=False)
    rplt.hist(unfolding.data, label=r'$\mathrm{t}\bar{\mathrm{t}}$ from fit', stacked=False)
    rplt.errorbar(unfolding.unfolded_data, label='unfolded')
    plt.xlabel('$E_{\mathrm{T}}^{miss}$')
    plt.ylabel('Events')
    plt.title('Unfolding')
    plt.legend()
    plt.savefig(outputfile)

def setDrawStyles(unfolding):
    if unfolding.unfolded_data:
        unfolding.unfolded_data.SetFillStyle(unfoldCfg.unfolded_fillStyle)
        unfolding.unfolded_data.SetColor(unfoldCfg.unfolded_color)
        unfolding.unfolded_data.SetMarkerStyle(unfoldCfg.unfolded_markerStyle)
    
    if unfolding.unfolded_closure:
        unfolding.unfolded_closure.SetFillStyle(unfoldCfg.unfolded_fillStyle)
        unfolding.unfolded_closure.SetColor(unfoldCfg.unfolded_color)
        unfolding.unfolded_closure.SetMarkerStyle(unfoldCfg.unfolded_markerStyle)
    
    unfolding.truth.SetFillStyle(unfoldCfg.truth_fillStyle)
    unfolding.truth.SetColor(unfoldCfg.truth_color)
    
    unfolding.measured.SetFillStyle(unfoldCfg.measured_fillStyle)
    unfolding.measured.SetColor(unfoldCfg.measured_color)
    
    if(unfolding.data):
        unfolding.data.SetFillStyle(unfoldCfg.measured_fillStyle)
        unfolding.data.SetColor(unfoldCfg.measured_color)


if __name__ == "__main__":

    method = 'RooUnfoldTUnfold' # = 'RooUnfoldBayes | RooUnfoldSvd | RooUnfoldBinByBin | RooUnfoldInvert | RooUnfoldTUnfold
    
    bins = array('d', [0, 25, 45, 70, 100, 1000])
    nbins = len(bins) - 1
    lumiweight = 164.5 * 5050 / 7543741.0
    inputFile = File('../data/unfolding_merged.root', 'read')
    h_truth = asrootpy(inputFile.unfoldingAnalyserElectronChannel.truth.Rebin(nbins, 'truth', bins))
    h_measured = asrootpy(inputFile.unfoldingAnalyserElectronChannel.measured.Rebin(nbins, 'measured', bins))
    h_fakes = asrootpy(inputFile.unfoldingAnalyserElectronChannel.fake.Rebin(nbins, 'truth', bins))
    h_response = inputFile.unfoldingAnalyserElectronChannel.response_withoutFakes_AsymBins #response_AsymBins
    h_truth.Scale(lumiweight)
    h_measured.Scale(lumiweight)
    h_fakes.Scale(lumiweight)
    h_response.Scale(lumiweight)
    #test values for real data input
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
    
    unfolding = Unfolding(h_truth, h_measured, h_response, method = method)
    #should be identical to
    #unfolding = Unfolding(h_truth, h_measured, h_response, h_fakes, method)
    unfolding.unfold(h_data)
    saveUnfolding(unfolding, 'Unfolding_' + method + '.png')
    unfolding.closureTest()
    saveClosureTest(unfolding, 'Unfolding_' + method + '_closure.png')
    
    fakes = asrootpy(unfolding.unfoldResponse.Hfakes())
    fakes.SetColor('red')
    h_fakes.SetColor('blue')
    fakes.SetFillStyle('\\')
    h_fakes.SetFillStyle('/')
    
    #cross check: are the fakes the same?
    plt.figure(figsize=(16, 10), dpi=100)
    rplt.hist(fakes, label=r'fakes from unfolding', stacked=False)
    rplt.hist(h_fakes, label=r'fakes from MC', stacked=False, alpha = 0.5)
    plt.xlabel('$E_{\mathrm{T}}^{miss}$')
    plt.ylabel('Events')
    plt.title('Unfolding')
    plt.legend()
    plt.savefig('Fakes.png')
    
    print 'Done'
