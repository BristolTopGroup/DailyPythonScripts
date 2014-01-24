#!/bin/bash
mkdir logs
python 01_get_fit_results.py &> logs/met_fit.log &
python 01_get_fit_results.py -v HT &> logs/ht_fit.log &
python 01_get_fit_results.py -v ST &> logs/st_fit.log &
python 01_get_fit_results.py -v MT &> logs/mt_fit.log &
python 01_get_fit_results.py -v WPT &> logs/wpt_fit.log &

