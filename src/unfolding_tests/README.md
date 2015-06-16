# Unfolding Tests

## Creating toy MC
First we need to create a set of toy MC. Run
```
python src/unfolding_tests/create_toy_mc.py -n 10
```
For more information about available parameters, execute
```
python src/unfolding_tests/create_toy_mc.py -h
```
This will create a root file in data/toy_mc named toy_mc_MET_N_10_8TeV.root 
(generally toy_mc_<variable>_N_<n>_<centre-of-mass>TeV.root).

## Creating pull distributions
```
python src/unfolding_tests/create_unfolding_pull_data.py -f data/toy_mc/toy_mc_MET_N_10_8TeV.root -c electron -n 10
```
which will create 
```data/pull_data//8TeV/MET/10_input_toy_mc/k_value_3/Pulls_multiple_data_multiple_unfolding_RooUnfoldSvd_electron_toy_MC_1_to_10_MC_1_to_10_data.txt```

## Analysing pull data
table form
```
python src/unfolding_tests/analyze_unfolding_pulls.py -c electron -i data/pull_dat
```

plot form