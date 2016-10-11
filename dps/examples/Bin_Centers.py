'''
Created on 12 Nov 2012

@author: kreczko
'''

from dps.utils.datapoint_position import get_bin_centers, barycenters, calculate_correct_x_coordinates
from rootpy.io import File
from rootpy.plotting import Hist, Graph
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from array import array
from rootpy import asrootpy
import numpy as np
if __name__ == '__main__':
    bins = array('d', [0, 25, 45, 70, 100, 1000])
    nbins = len(bins) - 1
    
    inputFile = File('/storage/TopQuarkGroup/unfolding/unfolding_merged_sub1.root', 'read')
    h_truth_finebinned = inputFile.unfoldingAnalyserElectronChannel.truth
    h_truth = asrootpy(inputFile.unfoldingAnalyserElectronChannel.truth.Rebin(nbins, 'truth_new', bins))
    print 'old:', get_bin_centers(bins)
    new_centers = barycenters(h_truth_finebinned, h_truth)
    print 'centre of mass:', new_centers
    new_centers = calculate_correct_x_coordinates(h_truth_finebinned, bins)
    print 'correct:', new_centers
    data = list(h_truth.y())
    h_truth_new = Hist(new_centers)
    bin_widths = [25,20,25,30,1000]
    g_truth_new = Graph(len(new_centers))
    for i, (x,y, width) in enumerate(zip(new_centers, data, bin_widths)):
        g_truth_new.SetPoint(i, x, y/width)
        error = h_truth.GetBinError(i+1)
        g_truth_new.SetPointError(i, 0, 0, error, error)
    
    for bin_i in range(len(data)):
        h_truth_new.SetBinContent(bin_i + 1, data[bin_i]/bin_widths[bin_i])
        h_truth.SetBinContent(bin_i + 1, data[bin_i]/bin_widths[bin_i])
    
    h_truth_finebinned.SetFillStyle(0)
    h_truth_finebinned.Smooth(500)
    x,y = list(h_truth_finebinned.x()), list(h_truth_finebinned.y())
    bin_edges = np.array(list(h_truth_finebinned.xedges()))
    bincenters = 0.5*(bin_edges[1:]+bin_edges[:-1])
    g_truth = Graph(h_truth)
#    g_truth_new = Graph(len(h_truth), h_truth_new)
    g_truth_new.SetLineColor('red')
    g_truth_new.SetMarkerColor('red')
    h_truth_finebinned.axis().SetRange(0, 1000)
    h_truth_finebinned.linecolor = 'orange'
    plt.figure(figsize=(16, 10), dpi=100)
    axes = plt.axes()
    rplt.errorbar(g_truth_new, label=r'corrected', emptybins=False)
    rplt.errorbar(g_truth, label=r'bin centre', emptybins=False)
    # rplt.hist(h_truth_finebinned, label=r'MC', stacked=False)
    plt.plot(bincenters, y, '-')
    axes.set_xlim([0,300])
    plt.xlabel('$E_{\mathrm{T}}^{miss}$')
    plt.ylabel('Events')
    plt.title('Unfolding')
    plt.legend()
    plt.savefig('plots/Bin_Centers.png')