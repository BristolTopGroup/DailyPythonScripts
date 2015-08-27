#!/bin/bash
echo "Setting up DailyPythonScripts from tar file ..."
echo "... getting master branch"
git clone https://github.com/BristolTopGroup/DailyPythonScripts.git
cd DailyPythonScripts/
echo "... setting up git submodules"
git submodule init && git submodule update
echo "... running setup routine"
./setup.sh
echo "... enforcing virtual python environment"
source environment.sh
echo "... extracting ${_CONDOR_JOB_IWD}/dps.tar on top"
tar -xf ${_CONDOR_JOB_IWD}/dps.tar --overwrite
echo "DailyPythonScripts are set up"
