#!/bin/bash
# remove Analysis.tar in case it exists. We want to ship the latest code!
# also useful for syncing between machines!
echo "Preparing DailyPythonScripts for condor submission"
if [ -f "dps.tar" ]; then
	echo "... deleting old dps.tar"
	rm -f dps.tar
fi
echo "... creating tar file (dps.tar)"
mkdir -p jobs
tar -zcf dps.tar bin condor config jobs src tools setup.sh environment.sh \
setup_with_conda.sh environment_conda.sh experimental data/toy_mc \
--exclude="*.pyc" --exclude="jobs/*/logs" \
--exclude "*.tar" --exclude="config/unfolding" --exclude="experimental/topReco"

hadoop fs -mkdir -p $1
hadoop fs -copyFromLocal dps.tar $1
