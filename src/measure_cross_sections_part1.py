'''
Created on 9 Dec 2012

@author: kreczko

Episode 0 - Histogram preparation:
- get all interesting histograms from the analysis output files
- make sure the bins are correct (rebin etc)
- write output to a single file! Folder:
    - electron, muon
        - TTJet, QCD (from data), V+Jets, single top
            - met 
                - types
            - HT
            - ST
                -types
            - other differential variables
            - lepton eta
                - met bins
                - HT bins
                - etc
result output files have the format
TTbar_plus_X_analysis_<lumi>pbinv_<nbtag>.root
'''
