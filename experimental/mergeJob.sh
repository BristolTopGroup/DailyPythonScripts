#!/bin/bash
scramv1 project CMSSW CMSSW_6_2_12
cd CMSSW_6_2_12/src
eval `scramv1 runtime -sh`
tar -xf ../../dps.tar
cd DailyPythonScripts/
cd external/
rm -r vpython/
cd ../
git submodule init && git submodule update
./setup_standalone.sh
eval `scramv1 runtime -sh`
. environment.sh
python experimental/merge_samples_onDICE.py -n $1 -c $2