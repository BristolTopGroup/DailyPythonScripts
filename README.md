DailyPythonScripts
==================
[![build status](https://travis-ci.org/BristolTopGroup/DailyPythonScripts.png)](https://travis-ci.org/BristolTopGroup/DailyPythonScripts)

Python scripts for the daily tasks in particle physics

Quick recipe:
```
#get the code from the repository
git clone https://github.com/BristolTopGroup/DailyPythonScripts
cd DailyPythonScripts

# get submodules:
git submodule init && git submodule update

# change matplotlib branch to 1.3.1 (stable version)
cd external/matplotlib
git co 1.3.1
cd -

# setup run:
./setup_standalone.sh

# setup environment (using virtualenv for python):
source environment.sh
```

Dependencies
==================
[ROOT](http://root.cern.ch) >=5.30

[freetype](http://www.freetype.org) and other matplotlib dependencies

Disclaimer
==================
All plots/histograms provided by this package are based on either toy MC or simulated events from the CMS experiment.
Real data is not included at any point.

Structure
==================
config/* - files to save presets for available modules

data/* - example ROOT input files

examples/* - generic examples for available modules

src/* - specific use of available modules

test/* - unit tests for available modules

tools/* - available modules
