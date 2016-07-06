#!/bin/bash
export CONDAINSTALL=/software
export PATH="$CONDAINSTALL/miniconda/bin:$PATH"
export ENVNAME=dps-new
export CONDA_ENV_PATH=$CONDAINSTALL/miniconda/envs/$ENVNAME

source activate dps-new # This version comes with ROOT 6.04
git clone https://github.com/BristolTopGroup/DailyPythonScripts
cd DailyPythonScripts
export PYTHONPATH=$PYTHONPATH:`pwd`
export PATH=$PATH:$base/bin

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

echo "Running payload"
>&2 echo "Running payload"
time env PATH=$PATH PYTHONPATH=$PYTHONPATH ./condor/run_job $@

echo "Cleaning up files"
rm ${_CONDOR_JOB_IWD}/dps.tar
