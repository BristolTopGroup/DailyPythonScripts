#!/bin/bash
cmssw_version=CMSSW_7_4_7
git_branch=master
echo "Setting up ${cmssw_version} ..."
echo "... sourcing CMS default environment from CVMFS"
source /cvmfs/cms.cern.ch/cmsset_default.sh
echo "... creating CMSSW project area"
scramv1 project CMSSW ${cmssw_version}
cd ${cmssw_version}/src
eval `scramv1 runtime -sh`
echo "${cmssw_version} has been set up"

echo "Setting up DailyPythonScripts from tar file ..."
echo "... getting ${git_branch} branch"
>&2 echo "... getting ${git_branch} branch"
time git clone https://github.com/BristolTopGroup/DailyPythonScripts.git
cd DailyPythonScripts/
git checkout ${git_branch}
echo "... setting up git submodules"
>&2 echo "... setting up git submodules"
time git submodule init && git submodule update
echo "... copying dps.tar from hdfs"
hadoop fs -copyToLocal $5/dps.tar ${_CONDOR_JOB_IWD}/dps.tar
echo "... extracting ${_CONDOR_JOB_IWD}/dps.tar on top"
tar -xf ${_CONDOR_JOB_IWD}/dps.tar --overwrite
echo "... running setup routine"
>&2 "... running setup routine"
time source setup_with_conda.sh
echo "... enforcing conda python environment"
# this is safe, as the dangerous part is only executed on soolin
source environment_conda.sh
echo "DailyPythonScripts are set up"

echo "Running payload"
>&2 echo "Running payload"
time env PATH=$PATH PYTHONPATH=$PYTHONPATH ./condor/run_job $@

echo "Cleaning up files"
rm ${_CONDOR_JOB_IWD}/dps.tar
