
'''
Created on 15 Jan 2013

@author: kreczko
This module will provide estimates for the number of QCD events after event selection.
It will be able to do the closure test (option --do-closure-test) 
as well get the calibration curve for the estimates (option --make-calibration-curves).
In addition to above it should provide an easy way to present the binned estimates (MET, b-tag, other bins)

'''
from dps.utils.QCD_rate_estimation import estimate_with_fit_to_relative_isolation
from rootpy.io import File

path_to_files = '/storage/TopQuarkGroup/results/histogramfiles/AN-12-241_V4/'
electron_data_file = path_to_files + 'central/ElectronHad_5050pb_PFElectron_PFMuon_PF2PATJets_PFMET.root'

input_file = File(electron_data_file)
histogram_for_estimation = 'TTbarPlusMetAnalysis/EPlusJets/QCD e+jets PFRelIso/BinnedMETAnalysis/Electron_patType1CorrectedPFMet_bin_0-25/electron_pfIsolation_03_0btag'

input_histogram = input_file.Get(histogram_for_estimation)

result = estimate_with_fit_to_relative_isolation(input_histogram)
print result
