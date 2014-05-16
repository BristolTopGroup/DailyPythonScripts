from rootpy.io import File
from rootpy.plotting import Hist, Canvas
import matplotlib
matplotlib.use('agg')
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from rootpy import asrootpy
from array import array
from tools.Unfolding import Unfolding
import config.RooUnfold as unfoldCfg
from config import CMS, RooUnfold
from tools.ROOT_utililities import set_root_defaults

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

def checkOnMC(unfolding, method):
    global bins, nbins
    RooUnfold.SVD_n_toy = 1000
    pulls = []
    for sub in range(1,9):
        inputFile2 = File('../data/unfolding_merged_sub%d.root' % sub, 'read')
        h_data = asrootpy(inputFile2.unfoldingAnalyserElectronChannel.measured.Rebin(nbins, 'measured', bins))
        nEvents = inputFile2.EventFilter.EventCounter.GetBinContent(1)
        lumiweight = 164.5 * 5050 / nEvents
#        print sub, nEvents
        h_data.Scale(lumiweight)
        doUnfoldingSequence(unfolding, h_data, method, '_sub%d' %sub)
        pull = unfolding.pull_inputErrorOnly()
#        unfolding.printTable()
        pulls.append(pull)
        unfolding.Reset()
    allpulls = []

    for pull in pulls:
        allpulls.extend(pull)
    h_allpulls = Hist(100,-30,30)
    filling = h_allpulls.Fill
    for entry in allpulls:
        filling(entry)
    fit = h_allpulls.Fit('gaus', 'WWS')
    h_fit = asrootpy(h_allpulls.GetFunction("gaus").GetHistogram())
    canvas = Canvas(width=1600, height=1000)
    canvas.SetLeftMargin(0.15)
    canvas.SetBottomMargin(0.15)
    canvas.SetTopMargin(0.10)
    canvas.SetRightMargin(0.05)
    h_allpulls.Draw()
    fit.Draw('same')
    canvas.SaveAs('plots/Pull_allBins_withFit.png')
    
    
    
    plt.figure(figsize=(16, 10), dpi=100)
    rplt.errorbar(h_allpulls, label=r'Pull distribution for all bins',  emptybins=False)
    rplt.hist(h_fit, label=r'fit')
    plt.xlabel('(unfolded-true)/error', CMS.x_axis_title)
    plt.ylabel('entries', CMS.y_axis_title)
    plt.title('Pull distribution for all bins', CMS.title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    plt.legend(numpoints=1)
    plt.savefig('plots/Pull_allBins.png')
    
    #individual bins
    for bin_i in range(nbins):
        h_pull = Hist(100,-30,30)
        for pull in pulls:
            h_pull.Fill(pull[bin_i])
        plt.figure(figsize=(16, 10), dpi=100)
        rplt.errorbar(h_pull, label=r'Pull distribution for bin %d' % (bin_i + 1), emptybins=False)
        plt.xlabel('(unfolded-true)/error', CMS.x_axis_title)
        plt.ylabel('entries', CMS.y_axis_title)
        plt.title('Pull distribution for  bin %d' % (bin_i + 1), CMS.title)
        plt.savefig('Pull_bin_%d.png' % (bin_i + 1))
    
    
    
def doUnfoldingSequence(unfolding, h_data, method, outputfile_suffix = '', doClosureTest = False, checkFakes = False):
    unfolding.unfold(h_data)
    saveUnfolding(unfolding, 'plots/Unfolding_' + method + outputfile_suffix + '.png')
    if doClosureTest:
        unfolding.closureTest()
        saveClosureTest(unfolding, 'plots/Unfolding_' + method + outputfile_suffix + '_closure.png')
    
    
    if checkFakes:
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
        plt.savefig('plots/Fakes' + outputfile_suffix + '.png')
    
if __name__ == "__main__":
    set_root_defaults()
    method = 'RooUnfoldSvd' # = 'RooUnfoldBayes | RooUnfoldSvd | RooUnfoldBinByBin | RooUnfoldInvert | RooUnfoldTUnfold
    
    bins = array('d', [0, 25, 45, 70, 100, 1000])
    nbins = len(bins) - 1
    inputFile = File('../data/unfolding_merged_sub1.root', 'read')
    h_truth = asrootpy(inputFile.unfoldingAnalyserElectronChannel.truth.Rebin(nbins, 'truth', bins))
    h_measured = asrootpy(inputFile.unfoldingAnalyserElectronChannel.measured.Rebin(nbins, 'measured', bins))
    h_fakes = asrootpy(inputFile.unfoldingAnalyserElectronChannel.fake.Rebin(nbins, 'fake', bins))
    h_response = inputFile.unfoldingAnalyserElectronChannel.response_withoutFakes_AsymBins #response_AsymBins
    # h_measured_new = h_measured - h_fakes
    
#    h_response = inputFile.unfoldingAnalyserElectronChannel.response_AsymBins #response_AsymBins
    nEvents = inputFile.EventFilter.EventCounter.GetBinContent(1)
    lumiweight = 164.5 * 5050 / nEvents
    h_truth.Scale(lumiweight)
    h_measured.Scale(lumiweight)
    h_fakes.Scale(lumiweight)
    h_response.Scale(lumiweight)
    unfolding = Unfolding(h_truth, h_measured, h_response, method = method)
    #should be identical to
#    unfolding = Unfolding(h_truth, h_measured, h_response, h_fakes, method = method)
    
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
    
    checkOnMC(unfolding, method)
    doUnfoldingSequence(unfolding, h_data, method)
    print 'Done'
