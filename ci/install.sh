#!/bin/bash
# This script is meant to be called by the "install" step defined in
# .travis.yml. See http://docs.travis-ci.com/ for more details.
# The behavior of the script is controlled by environment variabled defined
# in the .travis.yml in the top level folder of the project.

set -e

# Install a ROOT binary that we custom-built in a 64-bit Ubuntu VM
# for the correct python / ROOT version
time wget --no-check-certificate https://copy.com/s3BcYu1drmZa/ci/root_builds/root_v${ROOT}_python_${TRAVIS_PYTHON_VERSION}.tar.gz
time tar zxf root_v${ROOT}_python_${TRAVIS_PYTHON_VERSION}.tar.gz
mv root_v${ROOT}_python_${TRAVIS_PYTHON_VERSION} root
source root/bin/thisroot.sh

# test ROOT install 
# Check if ROOT and PyROOT work
root -l -q
python -c "import ROOT; ROOT.TBrowser()"

#DailyPythonTools location
export base=`pwd`

# setup vpython with all packages
# package list from FinalStateAnalysis 
# (https://github.com/uwcms/FinalStateAnalysis/blob/master/recipe/install_python.sh)
echo "Installing uncertainties <-- awesome error propagation"
time pip install -U uncertainties
echo "Installing tabulate (latex table printing, etc)"
pip install tabulate

echo "Installing rootpy"
time pip install --user -e $base/external/rootpy

echo "Installing root_numpy"
git clone https://github.com/rootpy/root_numpy.git && (cd root_numpy && python setup.py install --user)
cd $base
major_root_version=`echo $ROOT | cut -d- -f1`

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
