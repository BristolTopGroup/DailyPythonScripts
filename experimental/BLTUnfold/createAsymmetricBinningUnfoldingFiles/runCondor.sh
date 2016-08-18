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
rm -r unfolding
mkdir unfolding
time python experimental/BLTUnfold/createAsymmetricBinningUnfoldingFiles/runJobsCrab.py -j $1

echo "bltUnfoldAsymm folder contents:"
ls unfolding
tar -cf bltUnfoldAsymm.$2.$1.tar unfolding
mv bltUnfoldAsymm.$2.$1.tar ../../../
echo "DailyPythonScripts folder contents:"
ls
echo "Base folder contents:"
ls ../../../