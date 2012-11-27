DailyPythonScripts
==================

Python scripts for the daily tasks in particle physics


Dependencies
==================
ROOT >=5.30 - http://root.cern.ch

rootpy >=0.6 (HEAD version recommended)
http://rootpy.org/
or
https://github.com/rootpy/rootpy

Python uncertainties package
https://github.com/lebigot/uncertainties
or 
http://pypi.python.org/pypi/uncertainties/

For unfolding:
hepunx.rl.ac.uk/~adye/software/unfold/RooUnfold.html (doesn't take fakes in constructor)
or
https://github.com/kreczko/RooUnfold (takes fakes in constructor)

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