# Some checks
ls
cd src
ls
hostname
which git
echo $PATH
ls /hdfs/



# Checkout and setup DailyPythonScripts
rm -r DailyPythonScripts
git clone https://github.com/EmyrClement/DailyPythonScripts.git -b BLT_Unfold
cd DailyPythonScripts
source bin/env.sh
which root
which python

ls -trlh
echo $PYTHONPATH
mkdir unfolding # For output file

python ${DPSROOT}/src/BLTUnfold/runJobsCrab.py -j $1
#python ${DPSROOT}/src/BLTUnfold/produceUnfoldingHistograms.py

pwd
ls -trlh
ls -trlh unfolding
ls -trlh ${_CONDOR_JOB_IWD}

# Tar output file to generic name that can be found by crab
tar -cvf ${_CONDOR_JOB_IWD}/output.tar unfolding/*.root
ls -trlh ${_CONDOR_JOB_IWD}/