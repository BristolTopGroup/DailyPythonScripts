DailyPythonScripts
==================
[![build status](https://travis-ci.org/BristolTopGroup/DailyPythonScripts.png)](https://travis-ci.org/BristolTopGroup/DailyPythonScripts)

Python scripts for the daily tasks in particle physics

Quick installation recipe:
```
# get the code from the repository
git clone https://github.com/BristolTopGroup/DailyPythonScripts
cd DailyPythonScripts
# checkout the last working version
git checkout AN-14-071_2nd_draft

# get submodules:
git submodule init && git submodule update

# setup run:
./setup_standalone.sh

# setup environment (using virtualenv for python):
source environment.sh
```

If working on soolin (or anywhere where dependencies like ROOT/latex/etc are not available), run it within CMSSW:

```
# install CMSSW and setup environment:
cmsenv

# install DailyPythonScripts according to the recipe above, or if done already, setup the vpython environment:
source environment.sh

# make sure matplotlib is up to date (should return 1.3.1 or above):
python -c 'import matplotlib; print matplotlib.__version__'
```

Dependencies
==================
[ROOT](http://root.cern.ch) >=5.30

[freetype](http://www.freetype.org) and other matplotlib dependencies

Disclaimer
==================
All plots/histograms provided by this package are based on either toy MC or simulated events from the CMS experiment.
Real data is not included at any point.

Structure
==================
config/* - files to save presets for available modules

data/* - example ROOT input files

examples/* - generic examples for available modules

src/* - specific use of available modules

test/* - unit tests for available modules

tools/* - available modules

Instructions for ttbar differential cross-section analysis
==================

- Run experimental/BLTUnfold/merge_unfolding_jobs.sh to merge BLT unfolding files CRAB outputs
- Move merged files to e.g.: /hdfs/TopQuarkGroup/mc/<7> or <8> TeV/v11/NoSkimUnfolding/BLT/
- run produceUnfoldingJobs.py with finebinning option turned on on central sample only (run locally on soolin): ```python produceUnfoldingJobs.py -c=7 -f --sample=central```
- Move fine binned unfolding /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_5th_draft/<7> or <8> TeV/unfolding/
- Run the src/cross_section_measurement/00_pick_bins.py script to find new binning.
- Modify config/variable_binning (and TTbar_plus_X_analyser.cpp in AnalysisSoftware) with new binning
- Run python experimental/BLTUnfold/runJobsCrab.py with the last few lines commented out and printing the number of jobs.
- Update 'queue' in experimental/BLTUnfold/submitBLTUnfold.description with the outputted number of jobs
- tar --exclude='external/vpython' --exclude='any other large/unnecessary folders in DailyPythonScripts' -cf dps.tar DailyPythonScripts (tar file should be <=100MB)
- Run experimental/BLTUnfold/produceUnfoldingHistogram.py script on merged files using HTCondor by submitting submitBLTUnfold.description to convert unfolding files to our binning
- Move new files to /hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_5th_draft/<7> or <8> TeV/unfolding/

- Run final measurement scripts in bin/:
x_01_all_vars
x_02_all_vars
x_03_all_vars
x_04_all_vars
x_05_all_vars
x_98_all_vars
x_99_QCD_cross_checks
x_make_binning_plots
x_make_control_plots
x_make_fit_variable_plots
(script AN-14-071 runs all of these scripts automatically if you are confident everything will run smoothly(!))
