#!/bin/bash
scramv1 project CMSSW CMSSW_7_4_0_pre7
cd CMSSW_7_4_0_pre7/src
eval `scramv1 runtime -sh`
tar -xf ../../dps.tar
cd DailyPythonScripts/
cd external/
rm -r vpython/
cd ../
git submodule init && git submodule update
echo "Running setup.sh"
./setup.sh
eval `scramv1 runtime -sh`
. environment.sh
rm -r unfolding
mkdir unfolding
mkdir unfolding/13TeV
echo "Running script"
time python experimental/BLTUnfold/runJobsCrab.py -j $1

echo "Unfolding folder contents:"
ls unfolding
tar -cf unfolding.$2.$1.tar unfolding
mv unfolding.$2.$1.tar ../../../
echo "DailyPythonScripts folder contents:"
ls
echo "Base folder contents:"
ls ../../../