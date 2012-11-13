'''
Created on 12 Nov 2012

@author: kreczko
'''
from rootpy.io import File
from rootpy.plotting import Hist, Canvas, Graph
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from rootpy.utils import asrootpy
from array import array

def get_bin_centers(bin_edges):
    centers = []
    add_center = centers.append
    for lowerEdge, upperEdge in zip(bin_edges[:-1], bin_edges[1:]):
        center = (upperEdge - lowerEdge)/2 + lowerEdge
        add_center(center)
    return centers

#def get_bin_edges(bin_centers):
#    edges = []
#    add_edge

def barycenters(finedbinnedhist, coarsebinnedhist):
    distribution = list(finedbinnedhist)
    data = list(coarsebinnedhist)
    distribution_binEdges = list(finedbinnedhist.xedges())
    data_binEdges = list(coarsebinnedhist.xedges())
    centers = []
    old_centers = []
    print data_binEdges[:-2]
    print data_binEdges[1:]
    for lowerEdge, upperEdge in zip(data_binEdges[:-1], data_binEdges[1:]):
        data_position = 0
        mass = 0
        for x,y in zip(distribution_binEdges[1:], distribution):
            if x < upperEdge and x>= lowerEdge:
                data_position += x*y
                mass +=y
        data_position /= mass
        old_center = (upperEdge - lowerEdge)/2 + lowerEdge
        print 'Bin:',lowerEdge, '-', upperEdge
        print 'old center:', old_center, 'new center:', data_position
        centers.append(data_position)
        old_centers.append(object)
        
            
    
    
    return centers

def calculateBinCenters(hist, bins):
    pass

if __name__ == '__main__':
    bins = array('d', [0, 25, 45, 70, 100, 1000])
    nbins = len(bins) - 1
    
    
    inputFile = File('../data/unfolding_merged_sub1.root', 'read')
    h_truth_finebinned = inputFile.unfoldingAnalyserElectronChannel.truth
    h_truth = asrootpy(inputFile.unfoldingAnalyserElectronChannel.truth.Rebin(nbins, 'truth_new', bins))
    new_centers = barycenters(h_truth_finebinned, h_truth)
    print new_centers
    data = list(h_truth)
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
    g_truth = Graph(len(h_truth), h_truth)
#    g_truth_new = Graph(len(h_truth), h_truth_new)
    g_truth_new.SetLineColor('red')
    g_truth_new.SetMarkerColor('red')
    h_truth_finebinned.axis().SetRange(0, 1000)
    plt.figure(figsize=(16, 10), dpi=100)
    axes = plt.axes()
    rplt.errorbar(g_truth_new, label=r'centre of mass', emptybins=False)
    rplt.errorbar(g_truth, label=r'bin centre', emptybins=False)
    rplt.hist(h_truth_finebinned, label=r'MC', stacked=False)
    axes.set_xlim([0,200])
    plt.xlabel('$E_{\mathrm{T}}^{miss}$')
    plt.ylabel('Events')
    plt.title('Unfolding')
    plt.legend()
    plt.savefig('CenterOfMass.png')