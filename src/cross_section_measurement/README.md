# Differential cross section measurement
The top quark pair (ttbar) differential cross section measurement consists of
several steps. The first two are executed in the releated projects
[NTupleProduction](https://github.com/BristolTopGroup/NTupleProduction),
which runs over CMS data, selects events and produces data in ROOT
ntuple format, and [AnalysisSoftware](https://github.com/BristolTopGroup/AnalysisSoftware),
which takes this data, selects events, calculates additional variables and produces
histogram files (ROOT). These are then fed into this project, DailyPythonScripts (DPS).

The first step in DPS is to extract the normalisation of ttbar events in bins
of the measured variables. This can be done in two ways: using fitting (01_get_fit_results)
or using the background subtraction method. 

## Fitting method
TODO

## Background subtraction method
Before the background subtraction script can be run, the current config needs
to be translated into JSON files. This is done using
```shell
python src/cross_section_measurement/create_measurement.py -c <centre of mass energy>
```
where centre of mass energy is equal to 7, 8 or 13.
This will create the config files for each measurement 
(```config/measurements/background_subtraction/<centre of mass energy>TeV```).

Now one can run the normalisation script:
```shell
python src/cross_section_measurement/01_get_ttjet_normalisation.py \
        -c 8 -v MET -i config/measurements/background_subtraction/
```

## Unfolding

## Evaluation of systematics

## Tables

## Plots

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

# Adding a new variable
This example will use the existing variable NJets to describe the steps
necessary to make this new variable available for analysis.

## config/cross_section_config.py
1. add variable path to ```self.variable_path_templates```
2. add k values to ```self.k_values_electron```, ```self.k_values_muon``` and ```self.k_values_combined```
3. add &tau; values to ```self.tau_values_electron``` and ```self.tau_values_muon```

## config/latex_labels.py
Add variable latex definitin to ```variables_latex```

## config/variableBranchNames.py
Add variable to ```branchNames```, ```genBranchNames_particle``` and ```genBranchNames_parton```.
The branch names should be according to what is included in the AnalysisTools output files under TTbar_plus_X_analysis/Unfolding.

## config/variable_binning.py
Add variable bin edges to ```bin_edges_vis``` and ```bin_edges```

## experimental/BLTUnfold/produceUnfoldingHistograms.py
Add
```python
elif '<variable name>' in variable:
    maxVar = 20.5
    minVar = -0.5
    nBins = 21
```
for ```if options.fineBinned:```

## src/cross_section_measurement/00_pick_bins.py
If the variable has a defined minimum (maximum) bigger (smaller) than the
variable range, add entry in the variable loop:
```python
for variable in variables:
    ...
    elif variable == '<variable with xmin>':
            best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min, x_min=<xmin> )
    elif variable == '<variable with xmax>':
            best_binning, histogram_information = get_best_binning( histogram_information , p_min, s_min, n_min, x_max=<xmax> )
```



## src/cross_section_measurement/02_unfold_and_measure.py
If the variable does not need to be evaluated for MET systematics expand
```python
if ( variable == 'HT' or variable == 'NJets' ) and (category in measurement_config.met_systematics_suffixes and not category in ['JES_up', 'JES_down', 'JER_up', 'JER_down']):
```
## src/cross_section_measurement/03_calculate_systematics.py
Same as for 02 script.

## src/cross_section_measurement/05_make_tables.py
Same as for 02 script.

##  src/cross_section_measurement/create_measurement.py
Same as for 02 script.






