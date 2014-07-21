# Some checks
cd src
hostname
which git
echo $PATH

# CMSSW stuff
echo $VO_CMS_SW_DIR
. $VO_CMS_SW_DIR/cmsset_default.sh
cd ..
cmsenv
cd DailyPythonScripts

# Checkout and setup DailyPythonScripts
rm -r DailyPythonScripts
git clone https://github.com/EmyrClement/DailyPythonScripts.git -b BLT_Unfold
cd DailyPythonScripts
git submodule init && git submodule update

./setup_standalone.sh
source environment.sh
mkdir unfolding #ÊFor output file

python experimental/BLTUnfold/runJobsCrab.py -j $1
#python experimental/BLTUnfold/produceUnfoldingHistograms.py

pwd
ls -trlh
ls -trlh unfolding
ls -trlh ../../

# Tar output file to generic name that can be found by crab
tar -cvf ../../output.tar unfolding/*.root
ls -trlh ../../