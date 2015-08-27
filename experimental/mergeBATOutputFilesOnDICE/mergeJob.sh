#!/bin/bash
scramv1 project CMSSW CMSSW_7_4_7
cd CMSSW_7_4_7/src
eval `scramv1 runtime -sh`
tar -xf ../../dps.tar
cd DailyPythonScripts/
cd external/
rm -r vpython/
cd ../
git submodule init && git submodule update
./setup.sh
eval `scramv1 runtime -sh`
. environment.sh
python experimental/mergeBATOutputFilesOnDICE/merge_samples_onDICE.py -n $1 -c $2