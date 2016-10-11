# Unfolding Tests

## Creating toy MC
First we need to create a set of toy MC. Run
```shell
python src/unfolding_tests/create_toy_mc.py -n 10 -c 8
```
For more information about available parameters, execute
```shell
python src/unfolding_tests/create_toy_mc.py -h
```
This will create a root file in data/toy_mc named toy_mc_N_10_from_1_to_11_8TeV.root 
(generally toy_mc_N_<N>_from_1_to_<N+1>_<centre-of-mass>TeV.root).
This file can be used in the next step.

## Creating pull distributions
```shell
python src/unfolding_tests/create_unfolding_pull_data.py -f data/toy_mc/toy_mc_N_10_from_1_to_11_8TeV.root -c electron -n 10 -v MET
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
create_unfolding_pulls_on_DICE -c 8 -v MET,HT,ST,WPT,MT -i data/toy_mc/toy_mc_N_300_from_1_to_301_8TeV.root 
```
This script can only be executed on submission nodes (like soolin).
If you actually somehow manage to successfully run ```create_unfolding_pulls_on_DICE```, then you will first need to untar the output files:
```shell
for f in *.tar.gz; do tar zxvf "$f"; done
```
This will put the output files in a ```<CofM>TeV/<variable>/<N>_toy_mc/<N>_toy_data/k_value_<k>/*.txt```
Now move the output files to /data/pull_data:
```shell
mkdir data/pull_data
mv 8TeV data/pull_data/
```

## Analysing pull data
Making the plots:
```shell
python src/unfolding_tests/make_unfolding_pull_plots.py -v MET -s 8 -c electron -k 3 data/pull_data/8TeV/MET/10_input_toy_mc/10_input_toy_data/k_value_3/*.txt
```
for more information on which plots are going to be produce please consult
```shell
python src/unfolding_tests/make_unfolding_pull_plots.py -h
```