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
echo "... extracting ${_CONDOR_JOB_IWD}/dps.tar on top"
tar -xf ${_CONDOR_JOB_IWD}/dps.tar --overwrite
echo "... enforcing conda python environment"
source environment_conda.sh
echo "DailyPythonScripts are set up"

ls -l src/BLTUnfold/runJobsCrab.py
chmod a+x src/BLTUnfold/runJobsCrab.py
jobArguments=`src/BLTUnfold/runJobsCrab.py --return_job_options -j $1`
echo "Job arguments "$jobArguments
if [[ $jobArguments == *"generatorWeight"* ]]
then
	echo "Will copy input file locally"
	hadoop fs -copyToLocal /TopQuarkGroup/run2/atOutput/13TeV/25ns/TTJets_PowhegPythia8_tree.root ${_CONDOR_JOB_IWD}/CMSSW_7_4_7/src/DailyPythonScripts/localInputFile.root
fi

echo "Running payload"
>&2 echo "Running payload"
mkdir -p unfolding/13TeV
echo "Running script"
time python src/BLTUnfold/runJobsCrab.py -j $1

echo "Unfolding folder contents:"
ls -l unfolding
tar -cf unfolding.$2.$1.tar unfolding
cp unfolding.$2.$1.tar ${_CONDOR_JOB_IWD}/.
echo "DailyPythonScripts folder contents:"
ls -l
echo "Base folder contents:"
ls -l ${_CONDOR_JOB_IWD}/

if [[ $jobArguments == *"generatorWeight"* ]]
then
	echo "Before removing input file:"
	ls -l ${_CONDOR_JOB_IWD}/CMSSW_7_4_7/src/DailyPythonScripts/
	rm ${_CONDOR_JOB_IWD}/CMSSW_7_4_7/src/DailyPythonScripts/localInputFile.root
	echo "After removing input file:"
	ls -l ${_CONDOR_JOB_IWD}/CMSSW_7_4_7/src/DailyPythonScripts/
fi
