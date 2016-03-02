# Some checks
ls
cd src
ls
hostname
which git
echo $PATH
ls /hdfs/

# CMSSW stuff
echo $SCRAM_ARCH
echo $VO_CMS_SW_DIR
. $VO_CMS_SW_DIR/cmsset_default.sh
cmsenv

which root
which python

# Checkout and setup DailyPythonScripts
rm -r DailyPythonScripts
git clone https://github.com/EmyrClement/DailyPythonScripts.git -b BLT_Unfold
cd DailyPythonScripts
git submodule init && git submodule update

ls -trlh
echo $PYTHONPATH
./setup_standalone.sh
echo $PYTHONPATH
which python
ls -trlh environment.sh
source environment.sh
mkdir unfolding # For output file

python src/BLTUnfold/runJobsCrab.py -j $1
#python src/BLTUnfold/produceUnfoldingHistograms.py

pwd
ls -trlh
ls -trlh unfolding
ls -trlh ../../

# Tar output file to generic name that can be found by crab
tar -cvf ../../output.tar unfolding/*.root
ls -trlh ../../