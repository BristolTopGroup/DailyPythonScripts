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
tar -xf ${_CONDOR_JOB_IWD}/dps.tar --overwrite
cd DailyPythonScripts/
echo "... enforcing conda python environment"
source bin/env.sh
echo "DailyPythonScripts are set up"

echo "Running payload"
>&2 echo "Running payload"
time python dps/experimental/condor/01b/run01_forAllOptions.py -n $1

echo "Done"
ls
echo "Tarring"
tar -cf output_$1.tar data
ls
echo "Moving"
mv output_$1.tar ${_CONDOR_JOB_IWD}/.
ls ${_CONDOR_JOB_IWD}/
