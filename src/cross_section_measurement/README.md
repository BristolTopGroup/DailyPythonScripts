# Usage


# Plans for final version

## Episode 0 - Histogram preparation:
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


## Episode 1 - Fitting
- Read histograms from Episode 0
- perform fits (central result and systematics)
- write everything to JSON and ROOT files

* all channels, central + systematic results

## Episode 2 - Unfolding
- Read histograms from Episode 2
- unfold the fit results for central result and systematics
- combine results for unfolded and not unfolded fit results
- write everything* to JSON and ROOT files

* all channels + combination, central + systematic results

## Episode 3 - Calculation of (differential) cross section:
- Read JSON files
- calculate the cross sections (for each systematic)
- write JSON files

## Episode 4 - Calculation of systematics:
- Read JSON files
- calculate the cross sections with systematics
- write JSON files

## Episode 5 - Presenting the results:
- Read JSON files from Episode 4
- create plots (see 04_make_plots.py)
- create tables (see 05_make_tables.py)
- have a good day

