#!/bin/bash
echo "Setting up DailyPythonScripts from tar file ..."
echo "... getting ${git_branch} branch"
>&2 echo "... getting ${git_branch} branch"
time git clone https://github.com/BristolTopGroup/DailyPythonScripts.git
cd DailyPythonScripts/
git checkout ${git_branch}
echo "... copying dps.tar from hdfs"
hadoop fs -copyToLocal $5/dps.tar ${_CONDOR_JOB_IWD}/dps.tar
echo "... extracting ${_CONDOR_JOB_IWD}/dps.tar on top"
tar -xf ${_CONDOR_JOB_IWD}/dps.tar --overwrite
echo "DailyPythonScripts are set up"
