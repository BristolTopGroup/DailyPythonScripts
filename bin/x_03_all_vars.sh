#!/bin/bash
python 03_calculate_systematics.py -s &> logs/met_calculate.log &
python 03_calculate_systematics.py -s -v HT &> logs/ht_calculate.log &
python 03_calculate_systematics.py -s -v ST &> logs/st_calculate.log &
python 03_calculate_systematics.py -s -v MT &> logs/mt_calculate.log &
python 03_calculate_systematics.py -s -v WPT &> logs/wpt_calculate.log &
