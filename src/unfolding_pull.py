'''
Created on 9 Dec 2012

@author: kreczko
'''
from optparse import OptionParser
from ROOT import gSystem, gROOT, cout, TH1F, gStyle
gROOT.SetBatch(True)
from rootpy.io import File
from rootpy.plotting import Hist, Canvas
from rootpy.utils import asrootpy
from array import array
from tools.Unfolding import Unfolding
from config import RooUnfold

from unfolding import saveUnfolding

def check_unfolding_truth(files, method):
    gStyle.SetOptFit(0111)
    #same data different unfolding input
    h_data = get_histograms(files[0])[1]#h_data = measured
    pulls = []
    for n, input_file in enumerate(files[1:]):
        h_truth, h_measured, h_response = get_histograms(input_file)
        unfolding_obj = Unfolding(h_truth, h_measured, h_response, method = method)
        unfolding_obj.unfold(h_data)
        saveTo = 'plots/Unfolding_truth_test_%s_%s_%d.png' %(method, options.channel, n)
        saveUnfolding(unfolding_obj, saveTo)
        pull = unfolding_obj.pull_inputErrorOnly()
        pulls.append(pull)
        unfolding_obj.Reset()
        
    allpulls = []

    for pull in pulls:
        allpulls.extend(pull)
    h_allpulls = Hist(100,-30,30)
    filling = h_allpulls.Fill
    for entry in allpulls:
        filling(entry)
    fit = h_allpulls.Fit('gaus', 'WWS')
    output_file = 'plots/Pull_truth_allBins_withFit_%s_%s.png' %(method, options.channel)
    plot_pull(h_allpulls, fit, output_file)
    
    #individual bins
    for bin_i in range(nbins):
        h_pull = Hist(100,-30,30)
        for pull in pulls:
            h_pull.Fill(pull[bin_i])
        fit = h_pull.Fit('gaus', 'WWS')
        output_file = 'plots/Pull_reco_bin%d_withFit_%s_%s.png' %(bin_i, method, options.channel)
        plot_pull(h_pull, fit, output_file)

def check_unfolding_reco(files, method):
    global nbins
    gStyle.SetOptFit(0111)
    #same unfolding input, different data
    h_truth, h_measured, h_response = get_histograms(files[0])
    unfolding_obj = Unfolding(h_truth, h_measured, h_response, method = method)
    pulls = []
    for n, input_file in enumerate(files[1:]):
        h_data = get_histograms(input_file)[1]#h_data = measured
        unfolding_obj.unfold(h_data)
        saveTo = 'plots/Unfolding_reco_test_%s_%s_%d.png' %(method, options.channel, n)
        saveUnfolding(unfolding_obj, saveTo)
        pull = unfolding_obj.pull_inputErrorOnly()
        pulls.append(pull)
        unfolding_obj.Reset()
        
    allpulls = []

    for pull in pulls:
        allpulls.extend(pull)
    h_allpulls = Hist(100,-30,30)
    filling = h_allpulls.Fill
    for entry in allpulls:
        filling(entry)
    fit = h_allpulls.Fit('gaus', 'WWS')
    output_file = 'plots/Pull_reco_allBins_withFit_%s_%s.png' %(method, options.channel)
    plot_pull(h_allpulls, fit, output_file)
    
    #individual bins
    for bin_i in range(nbins):
        h_pull = Hist(100,-30,30)
        for pull in pulls:
            h_pull.Fill(pull[bin_i])
        fit = h_pull.Fit('gaus', 'WWS')
        output_file = 'plots/Pull_reco_bin%d_withFit_%s_%s.png' % (bin_i, method, options.channel)
        plot_pull(h_pull, fit, output_file)

def get_histograms(input_file):
    h_truth, h_measured, h_response = None, None, None
    inputFile = File(input_file, 'read')
    
    if options.channel == 'electron':
        h_truth = asrootpy(inputFile.unfoldingAnalyserElectronChannel.truth.Rebin(nbins, 'truth', bins))
        h_measured = asrootpy(inputFile.unfoldingAnalyserElectronChannel.measured.Rebin(nbins, 'measured', bins))
        h_response = inputFile.unfoldingAnalyserElectronChannel.response_withoutFakes_AsymBins #response_AsymBins
    if options.channel == 'muon':
        h_truth = asrootpy(inputFile.unfoldingAnalyserMuonChannel.truth.Rebin(nbins, 'truth', bins))
        h_measured = asrootpy(inputFile.unfoldingAnalyserMuonChannel.measured.Rebin(nbins, 'measured', bins))
        h_response = inputFile.unfoldingAnalyserMuonChannel.response_withoutFakes_AsymBins #response_AsymBins
    
    nEvents = inputFile.EventFilter.EventCounter.GetBinContent(1)
    lumiweight = 164.5 * 5050 / nEvents
    h_truth.Scale(lumiweight)
    h_measured.Scale(lumiweight)
    h_response.Scale(lumiweight)
    
    return h_truth, h_measured, h_response

def plot_pull(h_pull, fit, output_file):
    canvas = Canvas(width=1600, height=1000)
    canvas.SetLeftMargin(0.15)
    canvas.SetBottomMargin(0.15)
    canvas.SetTopMargin(0.10)
    canvas.SetRightMargin(0.05)
    h_pull.Draw()
    if fit:
        fit.Draw('same')
    canvas.SaveAs(output_file)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-c", "--channel",
                  action="store_false", dest="channel", default='muon',
                  help="Electron or Muon")
    (options, args) = parser.parse_args()
    
    bins = array('d', [0, 25, 45, 70, 100, 1000])
    nbins = len(bins) - 1
    #set the number of toy MC for error calculation
    RooUnfold.SVD_n_toy = 10000
    
    input_files = ['../data/unfolding_merged_sub%d.root' % sub for sub in range(1,9)]
    
    check_unfolding_truth(input_files, 'RooUnfoldSvd')
    check_unfolding_reco(input_files, 'RooUnfoldSvd')
    
    