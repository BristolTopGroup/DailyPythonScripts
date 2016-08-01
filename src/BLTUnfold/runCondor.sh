#!/bin/bash
git_branch=master

echo "Setting up DailyPythonScripts from tar file ..."
echo "... getting ${git_branch} branch"
>&2 echo "... getting ${git_branch} branch"
time git clone https://github.com/BristolTopGroup/DailyPythonScripts.git
cd DailyPythonScripts/
git checkout ${git_branch}
echo "... extracting ${_CONDOR_JOB_IWD}/dps.tar on top"
tar -xf ${_CONDOR_JOB_IWD}/dps.tar --overwrite
echo "... enforcing conda python environment"
source bin/env.sh
export PYTHONPATH=$PYTHONPATH:`pwd`

echo "DailyPythonScripts are set up"

ls -l ${DPSROOT}/src/BLTUnfold/runJobsCrab.py
chmod a+x ${DPSROOT}/src/BLTUnfold/runJobsCrab.py
jobArguments=`${DPSROOT}/src/BLTUnfold/runJobsCrab.py --return_job_options -j $1`
echo "Job arguments "$jobArguments
if [[ $jobArguments == *"generatorWeight"* ]]
then
	echo "Will copy input file locally"
	hadoop fs -copyToLocal /TopQuarkGroup/run2/atOutput/13TeV/25ns/TTJets_PowhegPythia8_tree.root ${DPSROOT}/localInputFile.root
fi

echo "Running payload"
>&2 echo "Running payload"
mkdir -p unfolding/13TeV
echo "Running script"
time python ${DPSROOT}/src/BLTUnfold/runJobsCrab.py -j $1

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
	ls -l ${DPSROOT}/
	rm ${DPSROOT}/localInputFile.root
	echo "After removing input file:"
	ls -l ${DPSROOT}/
fi