
'''
Created on 15 Jan 2013

@author: kreczko
This module will provide estimates for the number of QCD events after event selection.
It will be able to do the closure test (option --do-closure-test) 
as well get the calibration curve for the estimates (option --make-calibration-curves).
In addition to above it should provide an easy way to present the binned estimates (MET, b-tag, other bins)

'''
from dps.utils.QCD_rate_estimation import estimate_with_fit_to_relative_isolation
import dps.utils.QCD_rate_estimation as QCD_rate_estimation
from rootpy.io import File

if __name__ == "__main__":
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
#            'GJets': path_to_files + 'GJets_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
            'QCD': path_to_files + 'QCD_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(1959.75), ''),
            'SingleTop': path_to_files + 'SingleTop_%spb_PFElectron_%sPF2PATJets_PFMET.root' % (str(lumi), pfmuon),
                       }

    input_file = File(histogram_files['data'])

    histograms_for_estimation = [
#                                 'QCDStudy/PFIsolation_3jets_WithMETCutAndAsymJetCuts_0btag',
                                 'QCDStudy/PFIsolation_3jets_WithMETCutAndAsymJetCuts_1orMoreBtag',
                                 'QCDStudy/PFIsolation_WithMETCutAndAsymJetCuts_DR03_0btag',
                                 'QCDStudy/PFIsolation_WithMETCutAndAsymJetCuts_DR03_1btag',
                                 'QCDStudy/PFIsolation_WithMETCutAndAsymJetCuts_DR03_2orMoreBtags',
                                 ]
    
    qcd_expected = {
                    'QCDStudy/PFIsolation_3jets_WithMETCutAndAsymJetCuts_0btag':1528./0.48,
                    'QCDStudy/PFIsolation_3jets_WithMETCutAndAsymJetCuts_1orMoreBtag': 491./0.67,
                    'QCDStudy/PFIsolation_WithMETCutAndAsymJetCuts_DR03_0btag':1398./0.61,
                    'QCDStudy/PFIsolation_WithMETCutAndAsymJetCuts_DR03_1btag':504./0.79,
                    'QCDStudy/PFIsolation_WithMETCutAndAsymJetCuts_DR03_2orMoreBtags':210/0.73
                    }
    
    QCD_rate_estimation.relative_isolation_bias = 0.0
    results = {}
    for histogram_for_estimation in histograms_for_estimation:
        input_histogram = input_file.Get(histogram_for_estimation)
        result = estimate_with_fit_to_relative_isolation(input_histogram)
        results[histogram_for_estimation] = result
        #QCD normalised to lumi
        input_histogram_qcd = File(histogram_files['QCD']).Get(histogram_for_estimation.replace('_DR03_', '_'))
        input_histogram_qcd.Scale((1.0*lumi)/1959.75)
        input_histogram_qcd.Rebin(10)
        nQCD = input_histogram_qcd.GetBinContent(1)
#        print nQCD
#        nQCD = qcd_expected[histogram_for_estimation]
        fQCD = '---'
        if not nQCD == 0:
            fQCD = (result['value'])/nQCD
        print histogram_for_estimation, ':', result['value'], '+-', result['error'], 'QCD: ', nQCD, ',f_QCD:',  fQCD
    
    print 'Closure test'
    QCD_rate_estimation.relative_isolation_bias = 0.0
    for histogram_for_estimation in histograms_for_estimation:
        input_histogram = File(histogram_files['QCD']).Get(histogram_for_estimation.replace('_DR03_', '_')).Clone()
        input_histogram.Scale((1.0*lumi)/1959.75)
        input_histogram_allMC = input_histogram + File(histogram_files['TTJet']).Get(histogram_for_estimation) + File(histogram_files['WJets']).Get(histogram_for_estimation) + File(histogram_files['ZJets']).Get(histogram_for_estimation) + File(histogram_files['SingleTop']).Get(histogram_for_estimation)
        
        result = estimate_with_fit_to_relative_isolation(input_histogram_allMC)
        results[histogram_for_estimation] = result
        #QCD normalised to lumi
        input_histogram_qcd = File(histogram_files['QCD']).Get(histogram_for_estimation.replace('_DR03_', '_'))
        input_histogram_qcd.Scale((1.0*lumi)/1959.75)
        input_histogram_qcd.Rebin(10)
        nQCD = input_histogram_qcd.GetBinContent(1)
#        print nQCD
#        nQCD = qcd_expected[histogram_for_estimation]
        fQCD = '---'
        if not nQCD == 0:
            fQCD = (result['value'] - nQCD)/nQCD
        print histogram_for_estimation, ':', result['value'], '+-', result['error'], 'QCD: ', nQCD, ',f_QCD:',  fQCD
        
        