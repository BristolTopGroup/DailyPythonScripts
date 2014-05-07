mkdir logs
mkdir plots
mkdir plots/fitchecks

nohup python src/cross_section_measurement/01_get_fit_results.py >& plots/fitchecks/correlation_MET.txt &
nohup python src/cross_section_measurement/01_get_fit_results.py -v HT >& plots/fitchecks/correlation_HT.txt &
nohup python src/cross_section_measurement/01_get_fit_results.py -v ST >& plots/fitchecks/correlation_ST.txt &
nohup python src/cross_section_measurement/01_get_fit_results.py -v MT >& plots/fitchecks/correlation_MT.txt &
nohup python src/cross_section_measurement/01_get_fit_results.py -v WPT >& plots/fitchecks/correlation_WPT.txt &
wait

nohup python src/cross_section_measurement/02_unfold_and_measure.py >& logs/02_unfold_and_measure_MET.log &
nohup python src/cross_section_measurement/02_unfold_and_measure.py -v HT >& logs/02_unfold_and_measure_HT.log &
nohup python src/cross_section_measurement/02_unfold_and_measure.py -v ST >& logs/02_unfold_and_measure_ST.log &
nohup python src/cross_section_measurement/02_unfold_and_measure.py -v MT >& logs/02_unfold_and_measure_MT.log &
nohup python src/cross_section_measurement/02_unfold_and_measure.py -v WPT >& logs/02_unfold_and_measure_WPT.log &
wait

nohup python src/cross_section_measurement/03_calculate_systematics.py >& logs/03_calculate_systematics_MET.log &
nohup python src/cross_section_measurement/03_calculate_systematics.py -v HT >& logs/03_calculate_systematics_HT.log &
nohup python src/cross_section_measurement/03_calculate_systematics.py -v ST >& logs/03_calculate_systematics_ST.log &
nohup python src/cross_section_measurement/03_calculate_systematics.py -v MT >& logs/03_calculate_systematics_MT.log &
nohup python src/cross_section_measurement/03_calculate_systematics.py -v WPT >& logs/03_calculate_systematics_WPT.log &
wait

nohup python src/cross_section_measurement/04_make_plots_matplotlib.py >& logs/04_make_plots_matpotlib_MET.log &
nohup python src/cross_section_measurement/04_make_plots_matplotlib.py -v HT >& logs/04_make_plots_matpotlib_HT.log &
nohup python src/cross_section_measurement/04_make_plots_matplotlib.py -v ST >& logs/04_make_plots_matpotlib_ST.log &
nohup python src/cross_section_measurement/04_make_plots_matplotlib.py -v MT >& logs/04_make_plots_matpotlib_MT.log &
nohup python src/cross_section_measurement/04_make_plots_matplotlib.py -v WPT >& logs/04_make_plots_matpotlib_WPT.log &
wait

nohup python src/cross_section_measurement/05_make_tables.py >& logs/05_make_tables_MET.log &
nohup python src/cross_section_measurement/05_make_tables.py -v HT >& logs/05_make_tables_HT.log &
nohup python src/cross_section_measurement/05_make_tables.py -v ST >& logs/05_make_tables_ST.log &
nohup python src/cross_section_measurement/05_make_tables.py -v MT >& logs/05_make_tables_MT.log &
nohup python src/cross_section_measurement/05_make_tables.py -v WPT >& logs/05_make_tables_WPT.log &
wait

nohup python src/cross_section_measurement/99_QCD_cross_checks.py >& logs/99_QCD_cross_checks.log &

nohup python src/cross_section_measurement/98_fit_cross_checks.py >& logs/98_fit_cross_checks_MET.log &
nohup python src/cross_section_measurement/98_fit_cross_checks.py -v HT >& logs/98_fit_cross_checks_HT.log &
nohup python src/cross_section_measurement/98_fit_cross_checks.py -v ST >& logs/98_fit_cross_checks_ST.log &
nohup python src/cross_section_measurement/98_fit_cross_checks.py -v MT >& logs/98_fit_cross_checks_MT.log &
nohup python src/cross_section_measurement/98_fit_cross_checks.py -v WPT >& logs/98_fit_cross_checks_WPT.log &
wait
