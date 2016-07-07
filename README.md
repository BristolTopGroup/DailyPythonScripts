# DailyPythonScripts
[![build status](https://travis-ci.org/BristolTopGroup/DailyPythonScripts.png)](https://travis-ci.org/BristolTopGroup/DailyPythonScripts)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/40f826c689e6445c9a2a416c25817b66/badge.svg)](https://www.quantifiedcode.com/app/project/40f826c689e6445c9a2a416c25817b66)

Python scripts for the daily tasks in particle physics (*Run 2*) - Daily Python Scripts (aka DPS)

If working on soolin (or anywhere where dependencies like ROOT/latex/etc are not available), run it within CMSSW:
```
export PATH="/software/miniconda/bin:$PATH"
export CONDA_ENV_PATH=/software/miniconda/envs/dps-new
source activate dps-new # This version comes with ROOT 6.04
git clone https://github.com/BristolTopGroup/DailyPythonScripts
cd DailyPythonScripts
export PYTHONPATH=$PYTHONPATH:`pwd`
export PATH=$PATH:$base/bin
# make sure matplotlib is up to date (should return 1.5.1 or above):
python -c 'import matplotlib; print matplotlib.__version__'
```

Setting up conda environment on your own machine:
```
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
# follow instructions
export CONDAINSTALL=<path to miniconda install>
export PATH="$CONDAINSTALL/miniconda/bin:$PATH"
export ENVNAME=dps
conda update -q conda
conda install -q psutil
conda config --add channels http://conda.anaconda.org/NLeSC
conda config --set show_channel_urls yes
conda create -q -n $ENVNAME python=2.7 root=6 root-numpy numpy matplotlib nose sphinx pytables rootpy
export CONDA_ENV_PATH=$CONDAINSTALL/miniconda/envs/$ENVNAME
source activate $ENVNAME
pip install -U uncertainties
```

## Dependencies
[ROOT](http://root.cern.ch) &ge; 6.04

[freetype](http://www.freetype.org)

[matplotlib](http://matplotlib.org/) &ge; 1.5

## Disclaimer
All plots/histograms provided by this package are based on either toy MC or simulated events from the CMS experiment.
Real data is not included at any point.

## Structure
config/* - files to save presets for available modules

data/* - for input/output of ROOT & JSON files (will be created by some scripts)

examples/* - generic examples for available modules

plots/* - default output folder for plots (will be created by some scripts)

src/* - specific use of available modules

test/* - unit tests for available modules

tools/* - available modules


## Instructions for ttbar differential cross-section analysis

### Merge CRAB output unfolding files
- Run ```experimental/BLTUnfold/merge_unfolding_jobs.sh``` to merge BLT unfolding CRAB output files (each sample needs to be merged into one file, cannot be split over several files)
- Move merged files to e.g.: ```/hdfs/TopQuarkGroup/mc/7TeV``` or ```8TeV/v11/NoSkimUnfolding/BLT/```

### Calculate binning (if needed)
- run ```produceUnfoldingJobs.py``` with finebinning option turned on, on central sample only (run locally on soolin): ```python produceUnfoldingJobs.py -c=7 -f --sample=central```
- Move fine binned unfolding file to ```/hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV``` or ```8TeV/unfolding/```
- Run the ```src/cross_section_measurement/00_pick_bins.py``` script to find new binning.
- Modify ```config/variable_binning``` (and TTbar_plus_X_analyser.cpp in AnalysisSoftware) with new binning

### Create new asymmetric unfolding files 
- Run ```python experimental/BLTUnfold/runJobsCrab.py``` with the last few lines commented out and uncommenting the line ```print len(jobs)``` to print the number of jobs.
- Update ```queue``` in ```experimental/BLTUnfold/submitBLTUnfold.description``` with the outputted number of jobs
- ```cd``` up to the folder containing DailyPythonScripts and ```tar --exclude='external/vpython' --exclude='any other large/unnecessary folders in DailyPythonScripts' -cf dps.tar DailyPythonScripts``` (tar file should be <= 100MB)
- Run ```experimental/BLTUnfold/produceUnfoldingHistogram.py``` script on merged files using HTCondor: ```condor_submit submitBLTUnfold.description``` to convert unfolding files to our binning. Check progress using ```condor_q your_username```
- Once all jobs have finished, untar output files: ```tar -xf *.tar```
- Output root files should be in a folder called ```unfolding```. Move these new files to ```/hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_6th_draft/7TeV``` or ```8TeV/unfolding/```

### Prepare BAT output files
- After running the Analysis Software, move the output files to ```/hdfs/TopQuarkGroup/results/histogramfiles/AN-14-071_7th_draft/7TeV``` or ```8TeV``` using ```python experimental/move_BAT_output_files_to
- Find out how many merging jobs are needed using ```python experimental/merge_samples_onDICE.py -c 7(or 8) -n 1 --listJobs```
- Modify the following lines in experimental/submitMerge.description:
centre of mass energy: ```arguments = $(process) 7``` or ```arguments = $(process) 8```
number of jobs: enter the number of merging jobs for the centre of mass energy in question here e.g. ```queue 65```
- ```cd``` up to the folder containing DailyPythonScripts and ```tar --exclude='external/vpython' --exclude='any other large/unnecessary folders in DailyPythonScripts' -cf dps.tar DailyPythonScripts``` (tar file should be <= 100MB)
- Merge the required BAT output files (e.g. SingleTop, QCD etc.) using ```condor_submit DailyPythonScripts/experimental/submitMerge.description```

### Run final measurement scripts in bin/:
```
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
```
(script AN-14-071 runs all of these scripts automatically if you are confident everything will run smoothly(!))
