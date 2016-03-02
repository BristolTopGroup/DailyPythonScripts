#!/bin/bash
# This script is meant to be called by the "install" step defined in
# .travis.yml. See http://docs.travis-ci.com/ for more details.
# The behavior of the script is controlled by environment variabled defined
# in the .travis.yml in the top level folder of the project.

set -e

major_root_version=`echo $ROOT | cut -d- -f1`

#DailyPythonTools location
export base=`pwd`

sudo apt-get update

# install miniconda
if [[ "$TRAVIS_PYTHON_VERSION" == "2.7" ]]; then
	wget https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O miniconda.sh;
else
	wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
fi
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
hash -r
conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda info -a
conda create -q -n dps python=$TRAVIS_PYTHON_VERSION nose pytest flake8 gcc cmake

source activate dps
conda install -c https://conda.anaconda.org/nlesc root=${major_root_version} rootpy
# workaround for https://github.com/remenska/root-conda-recipes/issues/6
source deactivate && source activate dps

# install other dependencies
echo "Installing uncertainties <-- awesome error propagation"
pip install -U uncertainties
echo "Installing tabulate (latex table printing, etc)"
pip install tabulate

# test ROOT install 
# Check if ROOT and PyROOT work
echo "Checking ROOT & PyROOT"
root -l -q
python -c "import ROOT; ROOT.TBrowser()"
# Check that rootpy can be imported
time python -c 'import rootpy'
# What if ROOT has already been initialized?
time python -c 'from ROOT import kTRUE; import rootpy'

cd $base

if [ ! -d "$base/external/lib" ]; then
	mkdir $base/external/lib
	echo "Building RooUnfold"
	cd $base/external/RooUnfold/
	cmake CMakeLists.txt
	make RooUnfold
	#remove tmp folder
	rm -fr $base/external/RooUnfold/tmp
	mv $base/external/RooUnfold/libRooUnfold.so $base/external/lib/.
	echo "Updating RooUnfold config"
	cat $base/config/RooUnfold_template.py > $base/config/RooUnfold.py
	echo "library = '$base/external/lib/libRooUnfold.so'" >> $base/config/RooUnfold.py
	# this file is only created for ROOT 6
	if [ $major_root_version -eq 6 ]; then
	 cp $base/external/RooUnfold/RooUnfoldDict_rdict.pcm $base/.
	fi

fi

cd $base
export PATH=$PATH:$base/bin

# add base path from setup_standalone to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$base
