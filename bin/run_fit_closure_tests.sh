nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'absolute_eta' --closure_test &> fit_absolute_eta.log &
nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'M_bl' --closure_test &> fit_M_bl.log &
nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'M3' --closure_test &> fit_M3.log &
nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'angle_bl' --closure_test &> fit_angle_bl.log &

nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'absolute_eta,M_bl' --closure_test &> fit_absolute_eta_M_bl.log &
nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'absolute_eta,M3' --closure_test &> fit_absolute_eta_M3.log &
nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'absolute_eta,angle_bl' --closure_test &> fit_absolute_eta_angle_bl.log &
wait
nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'absolute_eta,M_bl,M3' --closure_test &> fit_absolute_eta_M_bl_M3.log &
nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'absolute_eta,M3,angle_bl' --closure_test &> fit_absolute_eta_M3_angle_bl.log &
nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'absolute_eta,M_bl,angle_bl' --closure_test &> fit_absolute_eta_angle_bl_M_bl.log &

nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'absolute_eta,M_bl,M3,angle_bl' --closure_test &> fit_absolute_eta_angle_bl_M_bl_M3.log &


nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'absolute_eta' --closure_test --no_combined_signal -p data/no_merging &> fit_absolute_eta.log &
nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'M_bl' --closure_test --no_combined_signal -p data/no_merging &> fit_M_bl.log &
nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'M3' --closure_test --no_combined_signal -p data/no_merging &> fit_M3.log &
nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'angle_bl' --closure_test --no_combined_signal -p data/no_merging  &> fit_angle_bl.log &

nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'absolute_eta,M_bl' --closure_test --no_combined_signal -p data/no_merging &> fit_absolute_eta_M_bl.log &
nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'absolute_eta,M3' --closure_test --no_combined_signal -p data/no_merging &> fit_absolute_eta_M3.log &
nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'absolute_eta,angle_bl' --closure_test --no_combined_signal -p data/no_merging &> fit_absolute_eta_angle_bl.log &
wait
nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'absolute_eta,M_bl,M3' --closure_test --no_combined_signal -p data/no_merging &> fit_absolute_eta_M_bl_M3.log &
nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'absolute_eta,M3,angle_bl' --closure_test --no_combined_signal -p data/no_merging &> fit_absolute_eta_M3_angle_bl.log &
nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'absolute_eta,M_bl,angle_bl' --closure_test --no_combined_signal -p data/no_merging &> fit_absolute_eta_angle_bl_M_bl.log &

nohup time python src/cross_section_measurement/01_get_fit_results.py --fit-variables 'absolute_eta,M_bl,M3,angle_bl' --closure_test --no_combined_signal -p data/no_merging &> fit_absolute_eta_angle_bl_M_bl_M3.log &
