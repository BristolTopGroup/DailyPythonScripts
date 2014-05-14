mkdir -p logs
mkdir -p plots/fitchecks

x_01_all_vars
wait

x_02_all_vars
wait

x_03_all_vars
wait

x_04_all_vars
wait

nohup python src/cross_section_measurement/05_make_tables.py >& logs/MET_make_tables_8TeV.log &
nohup python src/cross_section_measurement/05_make_tables.py -v HT >& logs/HT_tables_8TeV.log &
nohup python src/cross_section_measurement/05_make_tables.py -v ST >& logs/ST_tables_8TeV.log &
nohup python src/cross_section_measurement/05_make_tables.py -v MT >& logs/MT_tables_8TeV.log &
nohup python src/cross_section_measurement/05_make_tables.py -v WPT >& logs/WPT_tables_8TeV.log &
wait

nohup python src/cross_section_measurement/05_make_tables.py -c 7 >& logs/MET_tables_7TeV.log &
nohup python src/cross_section_measurement/05_make_tables.py -c 7 -v HT >& logs/HT_tables_7TeV.log &
nohup python src/cross_section_measurement/05_make_tables.py -c 7 -v ST >& logs/ST_tables_7TeV.log &
nohup python src/cross_section_measurement/05_make_tables.py -c 7 -v MT >& logs/MT_tables_7TeV.log &
nohup python src/cross_section_measurement/05_make_tables.py -c 7 -v WPT >& logs/WPT_tables_7TeV.log &
wait

nohup python src/cross_section_measurement/99_QCD_cross_checks.py >& logs/99_QCD_cross_checks.log &

nohup python src/cross_section_measurement/98_fit_cross_checks.py >& logs/MET_fit_cross_checks_8TeV.log &
nohup python src/cross_section_measurement/98_fit_cross_checks.py -v HT >& logs/HT_fit_cross_checks_8TeV.log &
nohup python src/cross_section_measurement/98_fit_cross_checks.py -v ST >& logs/ST_fit_cross_checks_8TeV.log &
nohup python src/cross_section_measurement/98_fit_cross_checks.py -v MT >& logs/MT_fit_cross_checks_8TeV.log &
nohup python src/cross_section_measurement/98_fit_cross_checks.py -v WPT >& logs/WPT_fit_cross_checks_8TeV.log &
wait

nohup python src/cross_section_measurement/98_fit_cross_checks.py -e 7 >& logs/MET_fit_cross_checks_7TeV.log &
nohup python src/cross_section_measurement/98_fit_cross_checks.py -e 7 -v HT >& logs/HT_fit_cross_checks_7TeV.log &
nohup python src/cross_section_measurement/98_fit_cross_checks.py -e 7 -v ST >& logs/ST_fit_cross_checks_7TeV.log &
nohup python src/cross_section_measurement/98_fit_cross_checks.py -e 7 -v MT >& logs/MT_fit_cross_checks_7TeV.log &
nohup python src/cross_section_measurement/98_fit_cross_checks.py -e 7 -v WPT >& logs/WPT_fit_cross_checks_7TeV.log &
wait
