#!/bin/bash
python src/cross_section_measurement/03_calculate_systematics.py -s &> logs/met_calculate.log &
python src/cross_section_measurement/03_calculate_systematics.py -s -v HT &> logs/ht_calculate.log &
python src/cross_section_measurement/03_calculate_systematics.py -s -v ST &> logs/st_calculate.log &
python src/cross_section_measurement/03_calculate_systematics.py -s -v MT &> logs/mt_calculate.log &
python src/cross_section_measurement/03_calculate_systematics.py -s -v WPT &> logs/wpt_calculate.log &
# 7 TeV
python src/cross_section_measurement/03_calculate_systematics.py -c 7 -s &> logs/met_calculate.log &
python src/cross_section_measurement/03_calculate_systematics.py -c 7 -s -v HT &> logs/ht_calculate.log &
python src/cross_section_measurement/03_calculate_systematics.py -c 7 -s -v ST &> logs/st_calculate.log &
python src/cross_section_measurement/03_calculate_systematics.py -c 7 -s -v MT &> logs/mt_calculate.log &
python src/cross_section_measurement/03_calculate_systematics.py -c 7 -s -v WPT &> logs/wpt_calculate.log &