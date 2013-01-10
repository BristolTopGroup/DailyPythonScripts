DailyPythonScripts
==================
Python scripts for the daily tasks in particle physics

To setup run
./setup_standalone.sh

To setup environment (using virtualenv for python):
source environment.sh

Dependencies
==================
ROOT >=5.30 - http://root.cern.ch

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
