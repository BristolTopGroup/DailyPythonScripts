# Unfolding Tests

## Get the best value for tau

Make the configs.  These store where the input unfolding files and input data (ttbar normalisation) are.
```shell
python src/unfolding_tests/makeConfig.py 
```
You can get the best regularisation for one variable/phase space/channel (i.e. one config file), example:
```shell
python src/unfolding_tests/get_best_regularisation_TUnfold.py config/unfolding/VisiblePS/abs_lepton_eta_13TeV_combined_channel.json
```
or run on several using wildcards.  To run on all 13TeV variables, combined channel, in the visible phase:
```shell
python src/unfolding_tests/get_best_regularisation_TUnfold.py config/unfolding/VisiblePS/*_13TeV_combined_channel.json
```


## Creating toy MC
First we need to create a set of toy MC. Run
```shell
python src/unfolding_tests/create_toy_mc.py -s powhegPythia
```
This will create 300 toy mc (300 is the default amount, probably need more for a full study) based on the powheg pythia sample.
Other possible options for -s are currently "madgraph" and "amcatnlo"

For more information about available parameters, do
```shell
python src/unfolding_tests/create_toy_mc.py -h
```
This will create a root file in data/toy_mc named toy_mc_powhegPythia_N_300_13TeV.root
(generally toy_mc_<sample>_N_<n>_<centre-of-mass>TeV.root).
This file can be used in the next step.

## Creating pull distributions
```shell
python src/unfolding_tests/create_unfolding_pull_data.py -f data/toy_mc/toy_mc_powhegPythia_N_300_13TeV.root -c combined -n 10 -v HT -s powhegPythia --tau 0.001
```
This will consider the toy mc file, for HT in the combined channel.  It will take the first 10 toy mc in that file, and unfold with a tau value of 0.001.
Output will be placed in:
```shell
data/pull_data/13TeV/HT/powhegPythia/Pull_data_TUnfold_combined_0.001.txt
```
The -s option is used for specifying the output directory (FIXME this could be derived from the input file)

To run on dice, you can do :
```shell
create_unfolding_pulls_on_DICE -c 13 -v MET,HT,ST,WPT,abs_lepton_eta,lepton_pt,NJets -s powhegPythia,madgraph,amcatnlo --scan_tau --doBestTau
```

This will submit a one job per tau value, for each variable (just in combined channel, as that's what we are typically interested in), and for each sample.
Passing --scan_tau will tell the script to submit jobs for a range of tau values (from --tau_min, to --tau_max) equally spaced on a log scale (same number of jobs between 0.1-1, and 1-10 etc.).  The number of tau values to consider between each factor of 10 is set with --spacing.

Passing --doBestTau will run one job for the best tau value, as specified in the main configuration file (config/cross_section_config.py)


## Analysing pull data
Making the plots:
```shell
python src/unfolding_tests/make_unfolding_pull_plots.py -s 8 -c electron data/pull_data/8TeV/MET/10_input_toy_mc/10_input_toy_data/k_value_3/*.txt
```
for more information on which plots are going to be produce please consult
```shell
python src/unfolding_tests/make_unfolding_pull_plots.py -h
```


python src/unfolding_tests/create_unfolding_pull_data.py -f data/toy_mc/toy_mc_madgraph_N_10_13TeV.root -c combined -n 10 -v MET -s test --tau 0.001

create_unfolding_pulls_on_DICE -c 13 -v MET,HT,ST,WPT,abs_lepton_eta,lepton_pt,NJets -s powhegPythia,madgraph,amcatnlo --scan_tau --doBestTau