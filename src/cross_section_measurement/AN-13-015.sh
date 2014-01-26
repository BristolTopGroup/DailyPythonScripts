mkdir plots
mkdir plots/fitchecks

python 01_get_fit_results.py >& plots/fitchecks/correlation_MET.txt &
python 01_get_fit_results.py -v HT >& plots/fitchecks/correlation_HT.txt &
python 01_get_fit_results.py -v ST >& plots/fitchecks/correlation_ST.txt &
python 01_get_fit_results.py -v MT >& plots/fitchecks/correlation_MT.txt &
python 01_get_fit_results.py -v WPT >& plots/fitchecks/correlation_WPT.txt &
wait

python 02_unfold_and_measure.py &
python 02_unfold_and_measure.py -v HT &
python 02_unfold_and_measure.py -v ST &
python 02_unfold_and_measure.py -v MT &
python 02_unfold_and_measure.py -v WPT &
wait

python 03_calculate_systematics.py &
python 03_calculate_systematics.py -v HT &
python 03_calculate_systematics.py -v ST &
python 03_calculate_systematics.py -v MT &
python 03_calculate_systematics.py -v WPT &
wait

python 04_make_plots_matplotlib.py &
python 04_make_plots_matplotlib.py -v HT &
python 04_make_plots_matplotlib.py -v ST &
python 04_make_plots_matplotlib.py -v MT &
python 04_make_plots_matplotlib.py -v WPT &
wait

python 05_make_tables.py &
python 05_make_tables.py -v HT &
python 05_make_tables.py -v ST &
python 05_make_tables.py -v MT &
python 05_make_tables.py -v WPT &
wait

python 99_QCD_cross_checks.py &

python 98_fit_cross_checks.py &
python 98_fit_cross_checks.py -v HT &
python 98_fit_cross_checks.py -v ST &
python 98_fit_cross_checks.py -v MT &
python 98_fit_cross_checks.py -v WPT &
wait
