#!/bin/bash
# This script is meant to be called by the "script" step defined in
# .travis.yml. See http://docs.travis-ci.com/ for more details.
# The behavior of the script is controlled by environment variabled defined
# in the .travis.yml in the top level folder of the project.

set -e

python --version
python -c "import numpy; print('numpy %s' % numpy.__version__)"

# Check if ROOT and PyROOT work
root -l -q
python -c "import ROOT; ROOT.TBrowser()"

# Check that rootpy can be imported
time python -c 'import rootpy'
# What if ROOT has already been initialized?
time python -c 'from ROOT import kTRUE; import rootpy'

# Give user write access to shared memory to make multiprocessing semaphores work
# https://github.com/rootpy/rootpy/pull/176#issuecomment-13712313
ls -la /dev/shm
sudo rm -rf /dev/shm && sudo ln -s /run/shm /dev/shm
#- sudo chmod a+w /dev/shm
ls -la /dev/shm

time python test/config_XSectionConfig.py
time python test/cross_section_measurement_00_pick_bins.py
time python test/fix_overflow.py
time python test/tools_Calculation.py
time python test/tools_Fitting_FitData.py
time python test/tools_Fitting_Minuit.py
time python test/tools_Fitting_RooFitFit.py
time python test/tools_hist_utilities.py
time python test/tools_Unfolding.py
time python test/Integral_GetBinContent_consistency.py
time python test/tools/calculate_normalised_xsection.py
