#!/bin/bash
git_branch=master

echo "Setting up DailyPythonScripts from tar file ..."
echo "... getting ${git_branch} branch"
>&2 echo "... getting ${git_branch} branch"
time git clone https://github.com/BristolTopGroup/DailyPythonScripts.git
cd DailyPythonScripts/
git checkout ${git_branch}
cd ../
echo "... extracting ${_CONDOR_JOB_IWD}/dps.tar on top"
cd DailyPythonScripts/
tar -xf ${_CONDOR_JOB_IWD}/dps.tar
echo "... enforcing conda python environment"
source bin/env.sh
echo "DailyPythonScripts are set up"


echo "Running payload"
>&2 echo "Running payload"
time env PATH=$PATH PYTHONPATH=$PYTHONPATH ./dps/condor/run_job $@

echo "Cleaning up files"
rm ${_CONDOR_JOB_IWD}/dps.tar
