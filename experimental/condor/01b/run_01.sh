#!/bin/bash
scramv1 project CMSSW CMSSW_7_4_7_patch2
cd CMSSW_7_4_7_patch2/src
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
python experimental/condor/01b/run01_forAllOptions.py -n $1
echo "Done"
ls
echo "Tarring"
tar -cf output_$1.tar data
ls
echo "Moving"
mv output_$1.tar ../../../
ls ../../../