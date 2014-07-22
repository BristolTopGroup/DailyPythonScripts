# Some checks
ls
cd src
ls
hostname
which git
echo $PATH
ls /hdfs/

# CMSSW stuff
export SCRAM_ARCH=slc6_amd64_gcc481
echo $SCRAM_ARCH
echo $VO_CMS_SW_DIR
. $VO_CMS_SW_DIR/cmsset_default.sh
cmsenv

# Checkout and setup DailyPythonScripts
rm -r DailyPythonScripts
git clone https://github.com/EmyrClement/DailyPythonScripts.git -b BLT_Unfold
cd DailyPythonScripts
git submodule init && git submodule update

ls -trlh
ls environment.sh
echo $PYTHONPATH
./setup_standalone.sh
echo $PYTHONPATH
source environment.sh
mkdir unfolding # For output file

python experimental/BLTUnfold/runJobsCrab.py -j $1
#python experimental/BLTUnfold/produceUnfoldingHistograms.py

pwd
ls -trlh
ls -trlh unfolding
ls -trlh ../../

# Tar output file to generic name that can be found by crab
tar -cvf ../../output.tar unfolding/*.root
ls -trlh ../../