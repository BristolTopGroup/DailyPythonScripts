from rootpy import asrootpy
import rootpy.plotting.root2matplotlib as rplt
from rootpy.plotting import HistStack

import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt

from config import CMS
from config import summations
from tools.ROOT_utililities import get_histograms_from_files
from tools.hist_utilities import sum_histograms

from copy import deepcopy

from ROOT import gROOT


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
    if '3jets' in variable:
        plt.title(r'e+jets, 3 jets, CMS Preliminary, $\mathcal{L}$ = 5.0 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV', CMS.title)
    else:
        plt.title(r'e+jets, $\geq$4 jets, CMS Preliminary, $\mathcal{L}$ = 5.0 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV', CMS.title)
    plt.legend([name_region_1 + ' (1)', name_region_2 + ' (2)'], numpoints=1, loc='upper right', prop={'size':32})
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
#    gs = gridspec.GridSpec(2, 1, height_ratios=[5, 1]) 
    axes = plt.axes()
#    axes = plt.axes([0.15, 0.15, 0.8, 0.8])
    
    rplt.hist(stack, stacked=True, axes=axes)
    rplt.errorbar(data, xerr=False, emptybins=False, axes=axes)
    
    plt.xlabel(x_label, CMS.x_axis_title)
    plt.ylabel(y_label, CMS.y_axis_title)
    plt.tick_params(**CMS.axis_label_major)
    plt.tick_params(**CMS.axis_label_minor)
    if '3jets' in variable:
        plt.title(r'e+jets, 3 jets, CMS Preliminary, $\mathcal{L}$ = 5.0 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV', CMS.title)
    else:
        plt.title(r'e+jets, $\geq$4 jets, CMS Preliminary, $\mathcal{L}$ = 5.0 fb$^{-1}$ at $\sqrt{s}$ = 7 TeV', CMS.title)
#    plt.legend(['data', 'QCD from data', 'Combined other background'], numpoints=1, loc='upper right', prop={'size':32})
    plt.legend(numpoints=1, loc='upper right', prop={'size':32})
    axes.set_xlim(xmin=x_min, xmax=x_max)
    axes.set_ylim(ymin=0)
    plt.tight_layout()
    plt.savefig(variable + '.png')  
    plt.savefig(variable + '.pdf')  

def prepare_histograms(histograms, scale_factor=5028. / 1091.45):
    global rebin
    
    for sample, histogram_dict in histograms.iteritems():
        for histogram_name, histogram in histogram_dict.iteritems():
            histogram = asrootpy(histogram)
            histogram.Rebin(rebin)
            
            if 'BCtoE' in histogram_name or 'BCtoE' in histogram_name:
                histogram.Scale(scale_factor)
    histograms['QCD'] = sum_histograms(histograms, summations.electron_qcd_samples)
    histograms['SingleTop'] = sum_histograms(histograms, summations.singleTop_samples)
    
if __name__ == '__main__':
    gROOT.SetBatch(True)
    gROOT.ProcessLine('gErrorIgnoreLevel = 1001;')
    # for mttbar
    rebin = 50  
    path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-11-265_V2/'
    lumi = 5028
    data = 'ElectronHad'
    pfmuon = 'PFMuon_'
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
            'GJets_HT-40To100': path_to_files + 'GJets_TuneD6T_HT-40To100_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'GJets_HT-100To200': path_to_files + 'GJets_TuneD6T_HT-100To200_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'GJets_HT-200': path_to_files + 'GJets_TuneD6T_HT-200_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'QCD_Pt-20to30_BCtoE': path_to_files + 'QCD_Pt-20to30_BCtoE_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'QCD_Pt-30to80_BCtoE': path_to_files + 'QCD_Pt-30to80_BCtoE_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'QCD_Pt-80to170_BCtoE': path_to_files + 'QCD_Pt-80to170_BCtoE_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'QCD_Pt-20to30_EMEnriched': path_to_files + 'QCD_Pt-20to30_EMEnriched_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'QCD_Pt-30to80_EMEnriched': path_to_files + 'QCD_Pt-30to80_EMEnriched_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'QCD_Pt-80to170_EMEnriched': path_to_files + 'QCD_Pt-80to170_EMEnriched_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            
            'Tbar_s-channel': path_to_files + 'Tbar_TuneZ2_s-channel_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'Tbar_t-channel': path_to_files + 'Tbar_TuneZ2_t-channel_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'Tbar_tW-channel': path_to_files + 'Tbar_TuneZ2_tW-channel_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'T_s-channel': path_to_files + 'T_TuneZ2_s-channel_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'T_t-channel': path_to_files + 'T_TuneZ2_t-channel_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'T_tW-channel': path_to_files + 'T_TuneZ2_tW-channel_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
                       }

    control_region_1 = 'topReconstruction/backgroundShape/mttbar_3jets_conversions_withMETAndAsymJets_0btag'
    control_region_2 = 'topReconstruction/backgroundShape/mttbar_3jets_antiIsolated_withMETAndAsymJets_0btag'
    control_region_3 = 'topReconstruction/backgroundShape/mttbar_conversions_withMETAndAsymJets_0btag'
    control_region_4 = 'topReconstruction/backgroundShape/mttbar_antiIsolated_withMETAndAsymJets_0btag'
    control_region_5 = 'QCDStudy/PFIsolation_controlRegion_0btag'
    
    histograms_to_read = [control_region_1, control_region_2, control_region_3, control_region_4]
#    histograms = get_histograms_from_files(histograms_to_read, histogram_files)
    histograms = get_histograms_from_files([control_region_5], histogram_files)
    prepare_histograms(histograms, scale_factor=1.)
    
#    make_control_region_data_mc_comparision(histograms, control_region_1, 'mttbar_3jets_conversions_withMETAndAsymJets_0btag')
#    make_control_region_data_mc_comparision(histograms, control_region_2, 'mttbar_3jets_antiIsolated_withMETAndAsymJets_0btag')
#    make_control_region_data_mc_comparision(histograms, control_region_3, 'mttbar_conversions_withMETAndAsymJets_0btag')
#    make_control_region_data_mc_comparision(histograms, control_region_4, 'mttbar_antiIsolated_withMETAndAsymJets_0btag')

    nonQCDMC = histograms['TTJet'][control_region_5] + histograms['WJets'][control_region_5] + histograms['ZJets'][control_region_5] + histograms['SingleTop'][control_region_5]
    make_control_region_data_mc_comparision(histograms, control_region_5, 'PFIsolation_0btag',
                                            x_label='relative isolation', x_min=0, x_max=1.6, y_label='Events/0.1')

#    make_control_region_comparison(histograms['data'][control_region_1],
#                                   histograms['data'][control_region_2],
#                                   'conversions',
#                                   'non-isolated electrons',
#                                   'mttbar_3jets_withMETAndAsymJets_0btag')
#    make_control_region_comparison(histograms['data'][control_region_3],
#                                   histograms['data'][control_region_4],
#                                   'conversions',
#                                   'non-isolated electrons',
#                                   'mttbar_withMETAndAsymJets_0btag')

    make_control_region_comparison(histograms['data'][control_region_5],
                                   histograms['QCD'][control_region_5],
                                   'data',
                                   'QCD MC',
                                   'PFIsolation_0btag',
                                   x_label='relative isolation', x_min=0, x_max=1.6, y_label='Events/0.1', y_max = 0.4)
    make_control_region_comparison(histograms['data'][control_region_5] - nonQCDMC,
                                   histograms['QCD'][control_region_5],
                                   'data',
                                   'QCD MC',
                                   'PFIsolation_mc_subtracted_0btag',
                                   x_label='relative isolation', x_min=0, x_max=1.6, y_label='Events/0.1', y_max = 0.25)
    
