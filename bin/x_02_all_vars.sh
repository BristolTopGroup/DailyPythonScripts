#!/bin/bash
python 02_unfold_and_measure.py &> logs/met_unfold.log &
python 02_unfold_and_measure.py -v HT &> logs/ht_unfold.log &
python 02_unfold_and_measure.py -v ST &> logs/st_unfold.log &
python 02_unfold_and_measure.py -v MT &> logs/mt_unfold.log &
python 02_unfold_and_measure.py -v WPT &> logs/wpt_unfold.log &
