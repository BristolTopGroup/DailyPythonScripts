from rootpy import asrootpy
import rootpy.plotting.root2matplotlib as rplt
from rootpy.plotting import HistStack

import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt

from config import CMS
from tools.ROOT_utils import get_histograms_from_files, set_root_defaults

from copy import deepcopy

def make_control_region_comparison(control_region_1, control_region_2,
                                   name_region_1, name_region_2, variable='mttbar',
                                   x_label=r'$m(\mathrm{t}\bar{\mathrm{t}})$ [GeV]',
                                   x_min=300, x_max=1800,
                                   y_label='arbitrary units/ 50 GeV', y_min = 0, y_max = 0.15):
    #make copies in order not to mess with existing histograms
    control_region_1 = deepcopy(control_region_1)
    control_region_2 = deepcopy(control_region_2)
    # normalise as we are comparing shapes
    control_region_1.Scale(1 / control_region_1.Integral())
    control_region_2.Scale(1 / control_region_2.Integral())
    
    ratio = control_region_1.Clone('ratio')
    ratio.Divide(control_region_2)
    ratio.SetMarkerSize(3)
    
    control_region_1.fillcolor = 'yellow'
    control_region_2.fillcolor = 'red'
    control_region_1.fillstyle = 'solid'
    control_region_2.fillstyle = 'solid'
    
    # plot with matplotlib
    plt.figure(figsize=(16, 16), dpi=200, facecolor='white')
    gs = gridspec.GridSpec(2, 1, height_ratios=[5, 1]) 
    ax0 = plt.subplot(gs[0])
    ax0.minorticks_on()
    
    rplt.hist(control_region_1, axes=ax0)
    rplt.hist(control_region_2, axes=ax0, alpha=0.5)
    
    plt.ylabel(y_label, CMS.y_axis_title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    plt.title(get_title(variable), CMS.title)
    plt.legend([name_region_1 + ' (1)', name_region_2 + ' (2)'], numpoints=1, loc='upper right', prop=CMS.legend_properties)
    ax0.set_xlim(xmin=x_min, xmax=x_max)
    ax0.set_ylim(ymin=y_min, ymax=y_max)
    plt.setp(ax0.get_xticklabels(), visible=False)
    
    ax1 = plt.subplot(gs[1])
    ax1.minorticks_on()
    ax1.grid(True, 'major', linewidth=1)
    ax1.yaxis.set_major_locator(MultipleLocator(1.0))
    ax1.yaxis.set_minor_locator(MultipleLocator(0.5))
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    plt.xlabel(x_label, CMS.x_axis_title)
    plt.ylabel('(1)/(2)', CMS.y_axis_title)
    rplt.errorbar(ratio, xerr=True, emptybins=False, axes=ax1)
    ax1.set_xlim(xmin=x_min, xmax=x_max)
    ax1.set_ylim(ymin= -0.5, ymax=4)
    plt.tight_layout()
    plt.savefig(variable + '_shape_comparision.png')  
    plt.savefig(variable + '_shape_comparision.pdf')  
    
    

def make_control_region_data_mc_comparision(histograms, histogram_name,
                                            variable, x_label=r'$m(\mathrm{t}\bar{\mathrm{t}})$ [GeV]',
                                            x_min=300, x_max=1800,
                                            y_label='Events/50 GeV'):
    qcd = histograms['QCD'][histogram_name]
    ttjet = histograms['TTJet'][histogram_name]
    wjets = histograms['WJets'][histogram_name]
    zjets = histograms['ZJets'][histogram_name]
    single_top = histograms['SingleTop'][histogram_name]
    other = ttjet + wjets + zjets + single_top
    data = histograms['data'][histogram_name]
    data.SetMarkerSize(3)
    qcd.SetTitle('QCD from data')
    other.SetTitle('Combined other background')
    data.SetTitle('Data')
    
    qcd.fillcolor = 'yellow'
    other.fillcolor = 'red'
    
    qcd.fillstyle = 'solid'
    other.fillstyle = 'solid'
    stack = HistStack()
    stack.Add(other)
    stack.Add(qcd)
    
    # plot with matplotlib
    plt.figure(figsize=(16, 12), dpi=200, facecolor='white')
    axes = plt.axes()
    
    rplt.hist(stack, stacked=True, axes=axes)
    rplt.errorbar(data, xerr=None, emptybins=False, axes=axes)
    
    plt.xlabel(x_label, CMS.x_axis_title)
    plt.ylabel(y_label, CMS.y_axis_title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    plt.title(get_title(variable), CMS.title)
    plt.legend(numpoints=1, loc='upper right', prop=CMS.legend_properties)
    axes.set_xlim(xmin=x_min, xmax=x_max)
    axes.set_ylim(ymin=0)
    plt.tight_layout()
    plt.savefig(variable + '.png')  
    plt.savefig(variable + '.pdf')  

def prepare_histograms(histograms, rebin = 1, scale_factor=1.):
    
    for _, histogram_dict in histograms.iteritems():
        for _, histogram in histogram_dict.iteritems():
            histogram = asrootpy(histogram)
            histogram.Rebin(rebin)
            histogram.Scale(scale_factor)
            
def get_title(variable):
    if '3jets' in variable:
        return 'CMS Preliminary, $\mathcal{L}$ = 5.0 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV \n e+jets, 3 jets'
    else:
        return 'CMS Preliminary, $\mathcal{L}$ = 5.0 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV \n e+jets, $\geq$4 jets'
        
    
if __name__ == '__main__':
    set_root_defaults()
    CMS.title['fontsize'] = 40
    CMS.x_axis_title['fontsize'] = 50
    CMS.y_axis_title['fontsize'] = 50
    CMS.axis_label_major['labelsize'] = 40
    CMS.axis_label_minor['labelsize'] = 40
    CMS.legend_properties['size'] = 40
    
    # for reliso 
    rebin = 10  
    path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-11-265_V1/'
    lumi = 1959.75
    data = 'data'
    pfmuon = ''
    histogram_files = {
            'TTJet': path_to_files + 'TTJet_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'data' : path_to_files + '%s_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (data, str(lumi), pfmuon),
            'WJets': path_to_files + 'WJetsToLNu_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'ZJets': path_to_files + 'DYJetsToLL_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'QCD': path_to_files + 'QCD_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'SingleTop': path_to_files + 'SingleTop_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
                       }

    control_region = 'QCDStudy/PFIsolation_controlRegion_0btag'
    
    histograms = get_histograms_from_files([control_region], histogram_files)
    prepare_histograms(histograms, rebin=rebin)
    

    nonQCDMC = histograms['TTJet'][control_region] + histograms['WJets'][control_region] + histograms['ZJets'][control_region] + histograms['SingleTop'][control_region]
    make_control_region_data_mc_comparision(histograms, control_region, 'PFIsolation_0btag',
                                            x_label='relative isolation', x_min=0, x_max=1.6, y_label='Events/0.1')

    make_control_region_comparison(histograms['data'][control_region],
                                   histograms['QCD'][control_region],
                                   'data',
                                   'QCD MC',
                                   'PFIsolation_0btag',
                                   x_label='relative isolation', x_min=0, x_max=1.6, y_label='Events/0.1', y_max = 0.4)
    make_control_region_comparison(histograms['data'][control_region] - nonQCDMC,
                                   histograms['QCD'][control_region],
                                   'data',
                                   'QCD MC',
                                   'PFIsolation_mc_subtracted_0btag',
                                   x_label='relative isolation', x_min=0, x_max=1.6, y_label='Events/0.1', y_max = 0.25)
    
