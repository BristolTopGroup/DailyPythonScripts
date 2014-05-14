'''
Created on Nov 22, 2011

@author: Lukasz Kreczko

Email: Lukasz.Kreczko@cern.ch

important features:

- read MC and data histograms and combine them
- set styles and colors
- allow switches for log-scale, cumulitative histograms, underflow/overflow bins, error sources

'''

import tools.PlottingUtilities as plotting
import FILES
import ROOTFileReader as reader
import QCDRateEstimation

def plot(histpath, qcdShapeFrom, qcdShapeForSystematics, qcdRateEstimate, rebin=1, suffixes=[]):
    inputFiles = FILES.files
    #get histograms
    if len(suffixes) > 0:
        for suffix in suffixes:
            hist = histpath + '_' + suffix
            histograms = reader.getHistogramDictionary(histpath, inputFiles)
    else:
        histograms = reader.getHistogramDictionary(histpath, inputFiles)


if __name__ == "__main__":
    inputFiles = FILES.files
    estimateQCD = QCDRateEstimation.estimateQCDWithRelIso
    plot(histpath='TTbarEplusJetsPlusMetAnalysis/Ref selection/MET/patMETsPFlow/Angle_lepton_MET',
         qcdShapeFrom ='TTbarEplusJetsPlusMetAnalysis/Ref selection/QCDConversions/MET/patMETsPFlow/Angle_lepton_MET',
         qcdShapeForSystematics = 'TTbarEplusJetsPlusMetAnalysis/Ref selection/QCD non iso e+jets/MET/patMETsPFlow/Angle_lepton_MET',
         qcdRateEstimate=estimateQCD,
         rebin=1,
         suffixes=['0btag', '1btag', '2orMoreBtags'])
    
