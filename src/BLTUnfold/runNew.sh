export ORIGDIR=`pwd`
cd ../
git clone https://github.com/EmyrClement/DailyPythonScripts.git -b BLT_Unfold
cd DailyPythonScripts
source bin/env.sh

mkdir unfolding
python experimental/BLTUnfold/runJobsCrab.py -j $1
ls unfolding

echo "Tar output"
tar -cvf $ORIGDIR/output.tar unfolding/*.root
ls -trlh $ORIGDIR