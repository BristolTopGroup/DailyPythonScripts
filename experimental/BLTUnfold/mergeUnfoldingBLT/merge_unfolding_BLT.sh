#!/bin/bash
scramv1 project CMSSW CMSSW_7_4_7
cd CMSSW_7_4_7/src
eval `scramv1 runtime -sh`
tar -xf ../../dps.tar
cd DailyPythonScripts/
cd external/
rm -r vpython/
cd rootpy
make clean
cd ../RooUnfold
make clean
cd ../TopAnalysis
make clean
cd ../../
git submodule init && git submodule update
./setup.sh
eval `scramv1 runtime -sh`
. environment.sh
rm -r mergeBLTUnfold
mkdir mergeBLTUnfold
echo "process " $1
echo "cluster " $2
echo "centre of mass energy " $3
echo "username" $4
time python experimental/BLTUnfold/mergeUnfoldingBLT/merge_unfolding_BLT_files_on_DICE.py -n $1 -c $3 -u $4

mv *.log ../../../
mv *.root ../../../
echo "DailyPythonScripts folder contents:"
ls
echo "Base folder contents:"
ls ../../../