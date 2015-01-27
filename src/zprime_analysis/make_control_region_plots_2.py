from config import CMS
from tools.ROOT_utils import get_histograms_from_files

from tools.ROOT_utils import set_root_defaults

from make_control_region_plots import make_control_region_comparison
from make_control_region_plots import make_control_region_data_mc_comparision
from make_control_region_plots import prepare_histograms

if __name__ == '__main__':
    set_root_defaults()
    CMS.title['fontsize'] = 40
    CMS.x_axis_title['fontsize'] = 50
    CMS.y_axis_title['fontsize'] = 50
    CMS.axis_label_major['labelsize'] = 40
    CMS.axis_label_minor['labelsize'] = 40
    CMS.legend_properties['size'] = 40
    
    # for mttbar
    rebin = 50  
    path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-11-265_V2/'
    lumi = 5028
    data = 'ElectronHad'
    pfmuon = 'PFMuon_'
    histogram_files = {
                       'TTJet': path_to_files + 'TTJet_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'data' : path_to_files + '%s_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (data, str(lumi), pfmuon),
            'WJets': path_to_files + 'WJetsToLNu_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'ZJets': path_to_files + 'DYJetsToLL_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'QCD': '/storage/TopQuarkGroup/results/histogramfiles/AN-11-265_V2/QCD_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(1959.75), ''),
            'SingleTop': path_to_files + 'SingleTop_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
                       }

    control_region_1 = 'topReconstruction/backgroundShape/mttbar_3jets_conversions_withMETAndAsymJets_0btag'
    control_region_2 = 'topReconstruction/backgroundShape/mttbar_3jets_antiIsolated_withMETAndAsymJets_0btag'
    control_region_3 = 'topReconstruction/backgroundShape/mttbar_conversions_withMETAndAsymJets_0btag'
    control_region_4 = 'topReconstruction/backgroundShape/mttbar_antiIsolated_withMETAndAsymJets_0btag'
    
    histograms_to_read = [control_region_1, control_region_2, control_region_3, control_region_4]
    histograms = get_histograms_from_files(histograms_to_read, histogram_files)
    prepare_histograms(histograms, rebin=rebin)
    for _,histogram in histograms['QCD'].iteritems():
        histogram.Scale(5028./1959.75)
    
    make_control_region_data_mc_comparision(histograms, control_region_1, 'mttbar_3jets_conversions_withMETAndAsymJets_0btag')
    make_control_region_data_mc_comparision(histograms, control_region_2, 'mttbar_3jets_antiIsolated_withMETAndAsymJets_0btag')
    make_control_region_data_mc_comparision(histograms, control_region_3, 'mttbar_conversions_withMETAndAsymJets_0btag')
    make_control_region_data_mc_comparision(histograms, control_region_4, 'mttbar_antiIsolated_withMETAndAsymJets_0btag')

    make_control_region_comparison(histograms['data'][control_region_1],
                                   histograms['data'][control_region_2],
                                   'conversions',
                                   'non-isolated electrons',
                                   'mttbar_3jets_withMETAndAsymJets_0btag')
    make_control_region_comparison(histograms['data'][control_region_3],
                                   histograms['data'][control_region_4],
                                   'conversions',
                                   'non-isolated electrons',
                                   'mttbar_withMETAndAsymJets_0btag')

