#!/bin/bash
tar -xf ${_CONDOR_JOB_IWD}/dps.tar
cd DailyPythonScripts/
source bin/env.sh
python experimental/merge_samples_onDICE.py -n $1 -c $2
