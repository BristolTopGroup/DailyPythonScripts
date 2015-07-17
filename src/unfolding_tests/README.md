# Unfolding Tests

## Creating toy MC
First we need to create a set of toy MC. Run
```shell
python src/unfolding_tests/create_toy_mc.py -n 10
```
For more information about available parameters, execute
```shell
python src/unfolding_tests/create_toy_mc.py -h
```
This will create a root file in data/toy_mc named toy_mc_MET_N_from_1_to_10_8TeV.root 
(generally toy_mc_<variable>_N_from_1_to_<n>_<centre-of-mass>TeV.root).
This file can be used in the next step.

## Creating pull distributions
```shell
python src/unfolding_tests/create_unfolding_pull_data.py -f data/toy_mc/toy_mc_MET_N_10_8TeV.root -c electron -n 10
```
which will create 
```
data/pull_data/8TeV/MET/10_input_toy_mc/10_input_toy_data/k_value_3/Pulls_multiple_data_multiple_unfolding_RooUnfoldSvd_electron_toy_MC_1_to_10_MC_1_to_10_data.txt
```
Again, please use
```shell
python src/unfolding_tests/create_unfolding_pull_data.py -h
```
for usage instructions. You can also use the DICE cluster for this step (all variables for a given centre-of-mass energy):
```shell
create_unfolding_pulls_on_DICE -c 8
```
This script can only be executed on submission nodes (like soolin).

## Analysing pull data
Making the plots:
```shell
python src/unfolding_tests/make_unfolding_pull_plots.py -s 8 -c electron data/pull_data/8TeV/MET/10_input_toy_mc/10_input_toy_data/k_value_3/*.txt
```
for more information on which plots are going to be produce please consult
```shell
python src/unfolding_tests/make_unfolding_pull_plots.py -h
```