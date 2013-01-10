'''
Created on 11 Dec 2012

@author: kreczko
1) get template
2) generate N events with gaussian distribution
'''
from optparse import OptionParser
from tools.toy_mc import generate_toy_MC_from_distribution
from rootpy.io import File
from rootpy.utils import asrootpy
from array import array
import ROOT

def get_new_set_of_histograms(h_truth, h_measured, h_fakes, h_response_AsymBins, h_reco_truth, h_truth_selected):
    h_truth_new = generate_toy_MC_from_distribution(h_truth)
    h_measured_new = generate_toy_MC_from_distribution(h_measured)
    h_fakes_new = generate_toy_MC_from_distribution(h_fakes)
    h_reco_truth_new = h_measured_new - h_fakes_new
    
    h_truth_new.SetName('truth')
    h_measured_new.SetName('measured')
    h_fakes_new.SetName('fake')
    h_reco_truth_new.SetName('reco_truth')
    # get acceptance scale factor
    acceptance = h_truth_selected / h_truth
    # assume identical acceptance (no reason this should change)
    h_truth_selected_new = h_truth_new.Clone('truth_selected')
    h_truth_selected_new *= acceptance
    h_truth_selected_new.SetName('truth_selected')
    
    scaling_truth_selected = h_truth_selected_new / h_truth_selected
    scaling_reco_truth = h_reco_truth_new / h_reco_truth
    h_response_AsymBins_new = h_response_AsymBins.Clone('response_AsymBins_new')
    h_response_AsymBins_new.SetName('response_withoutFakes_AsymBins')
    for y in range(1, 6):
        for x in range(1, 6):
            entry = h_response_AsymBins.GetBinContent(x, y)
            # this weight is only approximate due to the correlation of both results!
            weight = scaling_truth_selected.GetBinContent(y) * scaling_reco_truth.GetBinContent(x)
            h_response_AsymBins_new.SetBinContent(x, y, entry * weight)
    return h_truth_new, h_measured_new, h_fakes_new, h_response_AsymBins_new, h_reco_truth_new, h_truth_selected_new


def read_and_scale_histograms(channel):
    global bins, nbins, options
    input_file = File(options.input_file, 'read')
    h_truth, h_measured, h_fakes, h_response_AsymBins, h_reco_truth, h_truth_selected = None, None, None, None, None, None
    
    if channel == 'electron':
        h_truth = asrootpy(input_file.unfoldingAnalyserElectronChannel.truth.Rebin(nbins, 'truth', bins))
        h_measured = asrootpy(input_file.unfoldingAnalyserElectronChannel.measured.Rebin(nbins, 'measured', bins))
        h_fakes = asrootpy(input_file.unfoldingAnalyserElectronChannel.fake.Rebin(nbins, 'truth', bins))
        h_response = input_file.unfoldingAnalyserElectronChannel.response_withoutFakes  # response_AsymBins
        h_response_AsymBins = input_file.unfoldingAnalyserElectronChannel.response_withoutFakes_AsymBins  # for rescaling
    elif channel == 'muon':
        h_truth = asrootpy(input_file.unfoldingAnalyserMuonChannel.truth.Rebin(nbins, 'truth', bins))
        h_measured = asrootpy(input_file.unfoldingAnalyserMuonChannel.measured.Rebin(nbins, 'measured', bins))
        h_fakes = asrootpy(input_file.unfoldingAnalyserMuonChannel.fake.Rebin(nbins, 'truth', bins))
        h_response = input_file.unfoldingAnalyserMuonChannel.response_withoutFakes  # response_AsymBins
        h_response_AsymBins = input_file.unfoldingAnalyserMuonChannel.response_withoutFakes_AsymBins  # for rescaling
    else:
        print 'Unknown channel', channel
        print 'Expecting electron or muon'
        return
    nEvents = input_file.EventFilter.EventCounter.GetBinContent(1)
    lumiweight = 164.5 * 5050 / nEvents
    h_truth.Scale(lumiweight)
    h_measured.Scale(lumiweight)
    h_fakes.Scale(lumiweight)
    h_response.Scale(lumiweight)
    h_response_AsymBins.Scale(lumiweight)
    h_reco_truth = asrootpy(h_response.ProjectionX().Rebin(nbins, 'reco_truth', bins))
    h_truth_selected = asrootpy(h_response.ProjectionY().Rebin(nbins, 'truth_selected', bins))
    
    return h_truth, h_measured, h_fakes, h_response_AsymBins, h_reco_truth, h_truth_selected


if __name__ == '__main__':
    #prevent directory ownership of ROOT histograms (python does the garbage collection)
    ROOT.TH1F.AddDirectory(False)
    #define bins
    bins = array('d', [0, 25, 45, 70, 100, 1000])
    nbins = len(bins) - 1
    parser = OptionParser()
    parser.add_option("-n", "--n_toy_mc",
                      dest="n_toy_mc", default=100,
                      help="number of toy MC to create")
    parser.add_option("-i", "--input",
                      dest="input_file", default='/storage/TopQuarkGroup/unfolding/unfolding_merged_sub1.root',
                      help="input file for templates")
    parser.add_option("-f", "--file",
                      dest="output_file", default='../data/unfolding_toy_mc.root',
                      help="output file for toy MC")
    
    (options, args) = parser.parse_args()
    #define output file
    output = File(options.output_file, 'recreate')
    for channel in ['electron', 'muon']:
        # get histograms
        h_truth, h_measured, h_fakes, h_response_AsymBins, h_reco_truth, h_truth_selected = read_and_scale_histograms(channel)
        directory = output.mkdir(channel)
        directory.cd()
        mkdir = directory.mkdir
        cd = directory.cd
        #generate toy MC
        for i in range(1,10001):
            mkdir('toy_%d' % i)
            cd('toy_%d' % i)#should the numbering be transferred to the histograms?
            if i % 100 == 0:
                print 'Done %d toy MC' % i
            new_histograms = get_new_set_of_histograms(h_truth, h_measured, h_fakes, h_response_AsymBins, h_reco_truth, h_truth_selected)
            for hist in new_histograms:
                hist.Write()
    output.Write()
    output.Close()
