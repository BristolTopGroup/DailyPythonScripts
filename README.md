DailyPythonScripts
==================
[![build status](https://travis-ci.org/BristolTopGroup/DailyPythonScripts.png)](https://travis-ci.org/BristolTopGroup/DailyPythonScripts)

Python scripts for the daily tasks in particle physics

Quick installation recipe:
```
# get the code from the repository
git clone https://github.com/BristolTopGroup/DailyPythonScripts
cd DailyPythonScripts

# for Run 1 code, please checkout the run1 branch
 git checkout run1

# get submodules:
git submodule init && git submodule update

# setup environment (using virtualenv for python):
./setup_with_conda.sh

# setup environment (using virtualenv for python):
source environment_conda.sh

# make sure matplotlib is up to date (should return 1.3.1 or above):
python -c 'import matplotlib; print matplotlib.__version__'
```

If working on soolin (or anywhere where dependencies like ROOT/latex/etc are not available), run it within CMSSW:

```
# install CMSSW and setup environment:
scram p -n CMSSW_7_4_7_DPS CMSSW_7_4_7
cd CMSSW_7_4_7_DPS/src/
cmsenv
# This version comes with ROOT 6.02/05

# then install DailyPythonScripts according to the recipe above

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

### Merge CRAB output unfolding files
- Run ```python experimental/BLTUnfold/mergeUnfoldingBLT/merge_unfolding_BLT_files_on_DICE.py -c 7``` or ```8 --listJobs``` to list how many merging jobs are required to run (run locally on soolin).
- Edit the following lines in ```experimental/BLTUnfold/mergeUnfoldingBLT/submitMergeUnfoldingJobs.description```:
```arguments = $(process) $(cluster) com username``` and 
```queue n```
with ```com``` as the centre of mass energy, ```username``` as your grid username and ```n``` as the number of jobs output from the previous step.
- ```cd``` up to the folder containing DailyPythonScripts and ```tar --exclude='external/vpython' --exclude='any other large/unnecessary folders in DailyPythonScripts' -cf dps.tar DailyPythonScripts``` (tar file should be approximately 100MB in size).
- Merge the BLT unfolding files (each sample needs to be merged into one file, cannot be split over several files) using ```condor_submit DailyPythonScripts/experimental/BLTUnfold/mergeUnfoldingBLT/submitMergeUnfoldingJobs.description```.
- Move merged files to e.g.: ```/hdfs/TopQuarkGroup/mc/7TeV``` or ```8TeV/v11/NoSkimUnfolding/BLT/```.

### Calculate binning (if needed)
- run ```experimental/BLTUnfold/createAsymmetricBinningUnfoldingFiles/produceUnfoldingHistograms.py -c 7 -f --sample central``` i.e. finebinning option turned on, on central sample only (run locally on soolin).
- Move fine binned unfolding file to ```/hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV``` or ```8TeV/unfolding/```.
- Run the ```src/cross_section_measurement/00_pick_bins.py``` script to find new binning.
- Modify ```config/variable_binning``` (and TTbar_plus_X_analyser.cpp in AnalysisSoftware) with new binning.

### Create new asymmetric unfolding files 
- Run ```python experimental/BLTUnfold/createAsymmetricBinningUnfoldingFiles/runJobsCrab.py``` after uncommenting the line ```print len(jobs)``` to print the number of jobs and commenting out the lines after that
- Update ```queue``` in ```experimental/BLTUnfold/createAsymmetricBinningUnfoldingFiles/submitBLTUnfold.description``` with the outputted number of jobs
- ```cd``` up to the folder containing DailyPythonScripts and ```tar --exclude='external/vpython' --exclude='any other large/unnecessary folders in DailyPythonScripts' -cf dps.tar DailyPythonScripts``` (tar file should be approximately 100MB in size)
- In ```experimental/BLTUnfold/createAsymmetricBinningUnfoldingFiles/runJobsCrab.py``` comment out the line ```print len(jobs)``` and uncomment the lines after that
- Run ```experimental/BLTUnfold/createAsymmetricBinningUnfoldingFiles/produceUnfoldingHistogram.py``` script on merged files using HTCondor: ```condor_submit DailyPythonScripts/experimental/BLTUnfold/createAsymmetricBinningUnfoldingFiles/submitBLTUnfold.description``` to convert unfolding files to our binning. Check progress using ```condor_q your_username```
- Once all jobs have finished, untar output files: ```for file in *.tar; do tar -xf "$file"; done```.
- Output root files should be in a folder called ```unfolding```. Move these new files to ```/hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_8th_draft/7TeV``` or ```8TeV/unfolding/```

### Prepare BAT output files
- After running the Analysis Software, move the output files to ```/hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_8th_draft/7TeV``` or ```8TeV``` using ```python experimental/mergeBATOutputFilesOnDICE/move_BAT_output_files_to_hdfs.py -c 7(or 8) -p /storage/<username>/path/to/BAT/output/files/```. Use the ```--doNothing``` option if you just want to print out and check which/where files are going to be moved.
- Find out how many merging jobs are needed using ```python experimental/mergeBATOutputFilesOnDICE/merge_samples_onDICE.py -c 7(or 8) -n 1 --listJobs```
- Modify the following lines in ```experimental/submitMerge.description```:
centre of mass energy: ```arguments = $(process) 7``` or ```arguments = $(process) 8```
number of jobs: enter the number of merging jobs for the centre of mass energy in question here e.g. ```queue 65```
- ```cd``` up to the folder containing DailyPythonScripts and ```tar --exclude='external/vpython' --exclude='any other large/unnecessary folders in DailyPythonScripts' -cf dps.tar DailyPythonScripts``` (tar file should be approximately 100MB in size)
- Merge the required BAT output files (e.g. SingleTop, QCD etc.) using ```condor_submit DailyPythonScripts/experimental/mergeBATOutputFilesOnDICE/submitMerge.description```

### Prepare config files for background subtraction
```python src/cross_section_measurement/create_measurement.py -c 8```
```python src/cross_section_measurement/create_measurement.py -c 7```
This puts config files in config/measurements/background_subtraction/ for use by the x_0Nb_all_vars scripts.

### Run final measurement scripts in bin/:
```
x_01_all_vars
x_01b_all_vars
x_02_all_vars
x_02b_all_vars
x_03_all_vars
x_03b_all_vars
x_04_all_vars
x_04b_all_vars
x_05_all_vars
x_05b_all_vars
x_98_all_vars
x_99_QCD_cross_checks
x_make_binning_plots
x_make_control_plots
x_make_fit_variable_plots
```
(script AN-14-071 runs all of these scripts automatically if you are confident everything will run smoothly(!))