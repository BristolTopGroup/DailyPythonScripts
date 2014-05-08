mkdir -p pull_logs_MET/kv3
mkdir -p pull_logs_HT/kv3
mkdir -p pull_logs_ST/kv3
mkdir -p pull_logs_WPT/kv4
mkdir -p pull_logs_MT/kv2

echo 'Creating toy MC for all variables, 300x300, combined channel (default)'
python create_toy_mc.py -v MET -n 300
python create_toy_mc.py -v HT -n 300
python create_toy_mc.py -v ST -n 300
python create_toy_mc.py -v WPT -n 300
python create_toy_mc.py -v MT -n 300
wait

echo 'Producing pull data for MET variable, combined channel, kv=3'
python create_unfolding_pull_data.py -v MET -k 3 -f ../data/toy_mc/toy_mc_MET_N_300.root -n 100 --offset_toy_mc=0 --offset_toy_data=0     -c combined &>pull_logs_MET/kv3/1.log &
python create_unfolding_pull_data.py -v MET -k 3 -f ../data/toy_mc/toy_mc_MET_N_300.root -n 100 --offset_toy_mc=100 --offset_toy_data=0   -c combined &>pull_logs_MET/kv3/2.log &
python create_unfolding_pull_data.py -v MET -k 3 -f ../data/toy_mc/toy_mc_MET_N_300.root -n 100 --offset_toy_mc=200 --offset_toy_data=0   -c combined &>pull_logs_MET/kv3/3.log &
python create_unfolding_pull_data.py -v MET -k 3 -f ../data/toy_mc/toy_mc_MET_N_300.root -n 100 --offset_toy_mc=0 --offset_toy_data=100   -c combined &>pull_logs_MET/kv3/4.log &
python create_unfolding_pull_data.py -v MET -k 3 -f ../data/toy_mc/toy_mc_MET_N_300.root -n 100 --offset_toy_mc=0 --offset_toy_data=200   -c combined &>pull_logs_MET/kv3/5.log &
python create_unfolding_pull_data.py -v MET -k 3 -f ../data/toy_mc/toy_mc_MET_N_300.root -n 100 --offset_toy_mc=100 --offset_toy_data=100 -c combined &>pull_logs_MET/kv3/6.log &
python create_unfolding_pull_data.py -v MET -k 3 -f ../data/toy_mc/toy_mc_MET_N_300.root -n 100 --offset_toy_mc=200 --offset_toy_data=200 -c combined &>pull_logs_MET/kv3/7.log &
python create_unfolding_pull_data.py -v MET -k 3 -f ../data/toy_mc/toy_mc_MET_N_300.root -n 100 --offset_toy_mc=100 --offset_toy_data=200 -c combined &>pull_logs_MET/kv3/8.log &
python create_unfolding_pull_data.py -v MET -k 3 -f ../data/toy_mc/toy_mc_MET_N_300.root -n 100 --offset_toy_mc=200 --offset_toy_data=100 -c combined &>pull_logs_MET/kv3/9.log &
wait

echo 'Producing pull plots for MET variable, combined channel, kv=3'
python make_unfolding_pull_plots.py -i ../data/pull_data/MET/100_input_toy_mc/k_value_3 -c combined -v MET -k 3
wait

echo 'Producing pull data for HT variable, combined channel, kv=3'
python create_unfolding_pull_data.py -v HT -k 3 -f  ../data/toy_mc/toy_mc_HT_N_300.root -n 100 --offset_toy_mc=0 --offset_toy_data=0     -c combined &>pull_logs_HT/kv3/1.log &
python create_unfolding_pull_data.py -v HT -k 3 -f  ../data/toy_mc/toy_mc_HT_N_300.root -n 100 --offset_toy_mc=100 --offset_toy_data=0   -c combined &>pull_logs_HT/kv3/2.log &
python create_unfolding_pull_data.py -v HT -k 3 -f  ../data/toy_mc/toy_mc_HT_N_300.root -n 100 --offset_toy_mc=200 --offset_toy_data=0   -c combined &>pull_logs_HT/kv3/3.log &
python create_unfolding_pull_data.py -v HT -k 3 -f  ../data/toy_mc/toy_mc_HT_N_300.root -n 100 --offset_toy_mc=0 --offset_toy_data=100   -c combined &>pull_logs_HT/kv3/4.log &
python create_unfolding_pull_data.py -v HT -k 3 -f  ../data/toy_mc/toy_mc_HT_N_300.root -n 100 --offset_toy_mc=0 --offset_toy_data=200   -c combined &>pull_logs_HT/kv3/5.log &
python create_unfolding_pull_data.py -v HT -k 3 -f  ../data/toy_mc/toy_mc_HT_N_300.root -n 100 --offset_toy_mc=100 --offset_toy_data=100 -c combined &>pull_logs_HT/kv3/6.log &
python create_unfolding_pull_data.py -v HT -k 3 -f  ../data/toy_mc/toy_mc_HT_N_300.root -n 100 --offset_toy_mc=200 --offset_toy_data=200 -c combined &>pull_logs_HT/kv3/7.log &
python create_unfolding_pull_data.py -v HT -k 3 -f  ../data/toy_mc/toy_mc_HT_N_300.root -n 100 --offset_toy_mc=100 --offset_toy_data=200 -c combined &>pull_logs_HT/kv3/8.log &
python create_unfolding_pull_data.py -v HT -k 3 -f  ../data/toy_mc/toy_mc_HT_N_300.root -n 100 --offset_toy_mc=200 --offset_toy_data=100 -c combined &>pull_logs_HT/kv3/9.log &
wait

echo 'Producing pull plots for HT variable, combined channel, kv=3'
python make_unfolding_pull_plots.py -i ../data/pull_data/HT/100_input_toy_mc/k_value_3 -c combined -v HT -k 3
wait

echo 'Producing pull data for ST variable, combined channel, kv=3'
python create_unfolding_pull_data.py -v ST -k 3 -f  ../data/toy_mc/toy_mc_ST_N_300.root -n 100 --offset_toy_mc=0 --offset_toy_data=0     -c combined &>pull_logs_ST/kv3/1.log &
python create_unfolding_pull_data.py -v ST -k 3 -f  ../data/toy_mc/toy_mc_ST_N_300.root -n 100 --offset_toy_mc=100 --offset_toy_data=0   -c combined &>pull_logs_ST/kv3/2.log &
python create_unfolding_pull_data.py -v ST -k 3 -f  ../data/toy_mc/toy_mc_ST_N_300.root -n 100 --offset_toy_mc=200 --offset_toy_data=0   -c combined &>pull_logs_ST/kv3/3.log &
python create_unfolding_pull_data.py -v ST -k 3 -f  ../data/toy_mc/toy_mc_ST_N_300.root -n 100 --offset_toy_mc=0 --offset_toy_data=100   -c combined &>pull_logs_ST/kv3/4.log &
python create_unfolding_pull_data.py -v ST -k 3 -f  ../data/toy_mc/toy_mc_ST_N_300.root -n 100 --offset_toy_mc=0 --offset_toy_data=200   -c combined &>pull_logs_ST/kv3/5.log &
python create_unfolding_pull_data.py -v ST -k 3 -f  ../data/toy_mc/toy_mc_ST_N_300.root -n 100 --offset_toy_mc=100 --offset_toy_data=100 -c combined &>pull_logs_ST/kv3/6.log &
python create_unfolding_pull_data.py -v ST -k 3 -f  ../data/toy_mc/toy_mc_ST_N_300.root -n 100 --offset_toy_mc=200 --offset_toy_data=200 -c combined &>pull_logs_ST/kv3/7.log &
python create_unfolding_pull_data.py -v ST -k 3 -f  ../data/toy_mc/toy_mc_ST_N_300.root -n 100 --offset_toy_mc=100 --offset_toy_data=200 -c combined &>pull_logs_ST/kv3/8.log &
python create_unfolding_pull_data.py -v ST -k 3 -f  ../data/toy_mc/toy_mc_ST_N_300.root -n 100 --offset_toy_mc=200 --offset_toy_data=100 -c combined &>pull_logs_ST/kv3/9.log &
wait

echo 'Producing pull plots for ST variable, combined channel, kv=3'
python make_unfolding_pull_plots.py -i ../data/pull_data/ST/100_input_toy_mc/k_value_3 -c combined -v ST -k 3
wait

echo 'Producing pull data for WPT variable, combined channel, kv=4'
python create_unfolding_pull_data.py -v WPT -k 4 -f ../data/toy_mc/toy_mc_WPT_N_300.root -n 100 --offset_toy_mc=0 --offset_toy_data=0     -c combined &>pull_logs_WPT/kv4/1.log &
python create_unfolding_pull_data.py -v WPT -k 4 -f ../data/toy_mc/toy_mc_WPT_N_300.root -n 100 --offset_toy_mc=100 --offset_toy_data=0   -c combined &>pull_logs_WPT/kv4/2.log &
python create_unfolding_pull_data.py -v WPT -k 4 -f ../data/toy_mc/toy_mc_WPT_N_300.root -n 100 --offset_toy_mc=200 --offset_toy_data=0   -c combined &>pull_logs_WPT/kv4/3.log &
python create_unfolding_pull_data.py -v WPT -k 4 -f ../data/toy_mc/toy_mc_WPT_N_300.root -n 100 --offset_toy_mc=0 --offset_toy_data=100   -c combined &>pull_logs_WPT/kv4/4.log &
python create_unfolding_pull_data.py -v WPT -k 4 -f ../data/toy_mc/toy_mc_WPT_N_300.root -n 100 --offset_toy_mc=0 --offset_toy_data=200   -c combined &>pull_logs_WPT/kv4/5.log &
python create_unfolding_pull_data.py -v WPT -k 4 -f ../data/toy_mc/toy_mc_WPT_N_300.root -n 100 --offset_toy_mc=100 --offset_toy_data=100 -c combined &>pull_logs_WPT/kv4/6.log &
python create_unfolding_pull_data.py -v WPT -k 4 -f ../data/toy_mc/toy_mc_WPT_N_300.root -n 100 --offset_toy_mc=200 --offset_toy_data=200 -c combined &>pull_logs_WPT/kv4/7.log &
python create_unfolding_pull_data.py -v WPT -k 4 -f ../data/toy_mc/toy_mc_WPT_N_300.root -n 100 --offset_toy_mc=100 --offset_toy_data=200 -c combined &>pull_logs_WPT/kv4/8.log &
python create_unfolding_pull_data.py -v WPT -k 4 -f ../data/toy_mc/toy_mc_WPT_N_300.root -n 100 --offset_toy_mc=200 --offset_toy_data=100 -c combined &>pull_logs_WPT/kv4/9.log &
wait

echo 'Producing pull plots for WPT variable, combined channel, kv=4'
python make_unfolding_pull_plots.py -i ../data/pull_data/WPT/100_input_toy_mc/k_value_4 -c combined -v WPT -k 4
wait

echo 'Producing pull data for MT variable, combined channel, kv=2'
python create_unfolding_pull_data.py -v MT -k 2 -f  ../data/toy_mc/toy_mc_MT_N_300.root -n 100 --offset_toy_mc=0 --offset_toy_data=0     -c combined &>pull_logs_MT/kv2/1.log &
python create_unfolding_pull_data.py -v MT -k 2 -f  ../data/toy_mc/toy_mc_MT_N_300.root -n 100 --offset_toy_mc=100 --offset_toy_data=0   -c combined &>pull_logs_MT/kv2/2.log &
python create_unfolding_pull_data.py -v MT -k 2 -f  ../data/toy_mc/toy_mc_MT_N_300.root -n 100 --offset_toy_mc=200 --offset_toy_data=0   -c combined &>pull_logs_MT/kv2/3.log &
python create_unfolding_pull_data.py -v MT -k 2 -f  ../data/toy_mc/toy_mc_MT_N_300.root -n 100 --offset_toy_mc=0 --offset_toy_data=100   -c combined &>pull_logs_MT/kv2/4.log &
python create_unfolding_pull_data.py -v MT -k 2 -f  ../data/toy_mc/toy_mc_MT_N_300.root -n 100 --offset_toy_mc=0 --offset_toy_data=200   -c combined &>pull_logs_MT/kv2/5.log &
python create_unfolding_pull_data.py -v MT -k 2 -f  ../data/toy_mc/toy_mc_MT_N_300.root -n 100 --offset_toy_mc=100 --offset_toy_data=100 -c combined &>pull_logs_MT/kv2/6.log &
python create_unfolding_pull_data.py -v MT -k 2 -f  ../data/toy_mc/toy_mc_MT_N_300.root -n 100 --offset_toy_mc=200 --offset_toy_data=200 -c combined &>pull_logs_MT/kv2/7.log &
python create_unfolding_pull_data.py -v MT -k 2 -f  ../data/toy_mc/toy_mc_MT_N_300.root -n 100 --offset_toy_mc=100 --offset_toy_data=200 -c combined &>pull_logs_MT/kv2/8.log &
python create_unfolding_pull_data.py -v MT -k 2 -f  ../data/toy_mc/toy_mc_MT_N_300.root -n 100 --offset_toy_mc=200 --offset_toy_data=100 -c combined &>pull_logs_MT/kv2/9.log &
wait

echo 'Producing pull plots for MT variable, combined channel, kv=2'
python make_unfolding_pull_plots.py -i ../data/pull_data/MT/100_input_toy_mc/k_value_2 -c combined -v MT -k 2
wait
