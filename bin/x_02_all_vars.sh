#!/bin/bash
python src/cross_section_measurement/02_unfold_and_measure.py &> logs/met_unfold.log &
python src/cross_section_measurement/02_unfold_and_measure.py -v HT &> logs/ht_unfold.log &
python src/cross_section_measurement/02_unfold_and_measure.py -v ST &> logs/st_unfold.log &
python src/cross_section_measurement/02_unfold_and_measure.py -v MT &> logs/mt_unfold.log &
python src/cross_section_measurement/02_unfold_and_measure.py -v WPT &> logs/wpt_unfold.log &
# 7 TeV
python src/cross_section_measurement/02_unfold_and_measure.py -c 7 &> logs/met_unfold.log &
python src/cross_section_measurement/02_unfold_and_measure.py -c 7 -v HT &> logs/ht_unfold.log &
python src/cross_section_measurement/02_unfold_and_measure.py -c 7 -v ST &> logs/st_unfold.log &
python src/cross_section_measurement/02_unfold_and_measure.py -c 7 -v MT &> logs/mt_unfold.log &
python src/cross_section_measurement/02_unfold_and_measure.py -c 7 -v WPT &> logs/wpt_unfold.log &
