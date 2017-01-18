from rootpy.io import root_open
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from dps.config import CMS
from dps.utils.hist_utilities import value_error_tuplelist_to_hist, hist_to_value_error_tuplelist

def normalise(histograms):
    for histogram in histograms:
        total = histogram.Integral()
        if not total == 0:
            histogram.Scale(1 / total)

def draw_pair(constructed, real, systematic):
    fig = plt.figure(figsize=CMS.figsize, dpi=CMS.dpi, facecolor=CMS.facecolor)
    axes = plt.axes([0.15, 0.15, 0.8, 0.8])
    axes.xaxis.set_minor_locator(AutoMinorLocator())
    axes.yaxis.set_minor_locator(AutoMinorLocator())
    axes.tick_params(which='major', labelsize=15, length=8)
    axes.tick_params(which='minor', length=4)
    axes.set_xlim(xmin=0, xmax=250)
    
    constructed.markersize=1.2
    constructed.markercolor = 'green'
    constructed.linecolor = 'green'
    real.linecolor = 'red'
    constructed.SetTitle('constructed')
    real.SetTitle('real')
    
    rplt.errorbar(constructed, xerr=None, emptybins=False, axes=axes)
    rplt.hist(real)
    
    plt.xlabel('MET [GeV]', CMS.x_axis_title)
    plt.ylabel('normalised to unit area', CMS.y_axis_title)
    plt.legend(numpoints=1, prop=CMS.legend_properties)
    plt.savefig('validation_' + systematic + '.png')


bin_edges = {
             'MET':[0, 25, 45, 70, 100, 150, 250],
             'HT':[80, 240, 280, 330, 380, 450, 600, 1000],
             'ST':[106, 350, 400, 450, 500, 580, 700, 1000],
             'MT':[0, 30, 50, 80, 100, 200],
             'WPT':[0, 40, 70, 100, 130, 170, 250]
             }

channel = 'electron'
# unfolding
unfolding_file1 = root_open('/storage/TopQuarkGroup/mc/8TeV/NoSkimUnfolding/v10/TTJets_matchingup_TuneZ2star_8TeV-madgraph-tauola/unfolding_v10_Summer12_DR53X-PU_S10_START53_V7A-v1_NoSkim/TTJets-matchingup_nTuple_53X_mc_merged_001.root')
unfolding_file2 = root_open('/storage/TopQuarkGroup/mc/8TeV/NoSkimUnfolding/v10/TTJets_matchingdown_TuneZ2star_8TeV-madgraph-tauola/unfolding_v10_Summer12_DR53X-PU_S10_START53_V7A-v1_NoSkim/TTJets-matchingdown_nTuple_53X_mc_merged_001.root')
unfolding_file3 = root_open('/storage/TopQuarkGroup/mc/8TeV/NoSkimUnfolding/v10/TTJets_scaleup_TuneZ2star_8TeV-madgraph-tauola/unfolding_v10_Summer12_DR53X-PU_S10_START53_V7A-v1_NoSkim/TTJets-scaleup_nTuple_53X_mc_merged_001.root')
unfolding_file4 = root_open('/storage/TopQuarkGroup/mc/8TeV/NoSkimUnfolding/v10/TTJets_scaledown_TuneZ2star_8TeV-madgraph-tauola/unfolding_v10_Summer12_DR53X-PU_S10_START53_V7A-v1_NoSkim/TTJets-scaledown_nTuple_53X_mc_merged_001.root')

test_file = root_open('test_unfolded.root')

test1 = test_file.Get(channel + '_MET__TTJet__TTJetsMatching__plus')
test2 = test_file.Get(channel + '_MET__TTJet__TTJetsMatching__minus')
test3 = test_file.Get(channel + '_MET__TTJet__TTJetsScale__plus')
test4 = test_file.Get(channel + '_MET__TTJet__TTJetsScale__minus')
test1.Sumw2()
test2.Sumw2()
test3.Sumw2()
test4.Sumw2()

folder = 'unfolding_MET_analyser_' + channel + '_channel_patMETsPFlow'
ref1 = hist_to_value_error_tuplelist(unfolding_file1.Get(folder + '/truth_AsymBins'))
ref2 = hist_to_value_error_tuplelist(unfolding_file2.Get(folder + '/truth_AsymBins'))
ref3 = hist_to_value_error_tuplelist(unfolding_file3.Get(folder + '/truth_AsymBins'))
ref4 = hist_to_value_error_tuplelist(unfolding_file4.Get(folder + '/truth_AsymBins'))
ref1 = value_error_tuplelist_to_hist(ref1, bin_edges['MET'])
ref2 = value_error_tuplelist_to_hist(ref2, bin_edges['MET'])
ref3 = value_error_tuplelist_to_hist(ref3, bin_edges['MET'])
ref4 = value_error_tuplelist_to_hist(ref4, bin_edges['MET'])

normalise([test1, test2, test3, test4, ref1, ref2, ref3, ref4])

draw_pair(test1, ref1, 'matching_up')
draw_pair(test2, ref2, 'matching_down')
draw_pair(test3, ref3, 'scale_up')
draw_pair(test4, ref4, 'scale_down')
