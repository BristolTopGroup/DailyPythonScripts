#!/bin/bash
# This script is meant to be called by the "install" step defined in
# .travis.yml. See http://docs.travis-ci.com/ for more details.
# The behavior of the script is controlled by environment variabled defined
# in the .travis.yml in the top level folder of the project.

#set -e

# Check if we are running Python 2 or 3. This is needed for the apt-get package names
if [[ $TRAVIS_PYTHON_VERSION == '3.2' ]]; then 
	export PYTHON_SUFFIX="3"; 
fi

# add repositories for gcc 4.8 and clang $CLANG_VERSION (set in .travis.yml)
sudo add-apt-repository --yes ppa:ubuntu-toolchain-r/test
sudo add-apt-repository --yes 'deb http://llvm.org/apt/precise/ llvm-toolchain-precise main'
wget -O - http://llvm.org/apt/llvm-snapshot.gpg.key | sudo apt-key add -
# Needed because sometimes travis' repositories get out of date
time sudo apt-get update -qq

# Install the dependencies we need
time sudo apt-get -qq install clang-${CLANG_VERSION} libclang-${CLANG_VERSION}-dev gcc-4.8 g++-4.8
time sudo apt-get install -qq python${PYTHON_SUFFIX}-numpy python${PYTHON_SUFFIX}-sphinx python${PYTHON_SUFFIX}-nose python${PYTHON_SUFFIX}-pip cython${PYTHON_SUFFIX}
# matplotlib and PyTables are not available for Python 3 as packages from the main repo yet.
if [[ $TRAVIS_PYTHON_VERSION == '2.7' ]]; then 
	time sudo apt-get install -qq python-matplotlib python-tables; 
fi

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

# setup newer compilers for ROOT 6
if [[ $ROOT == '6-00-00' ]]; then 
	sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.8 50;
	sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-4.8 50; 
	sudo update-alternatives --set gcc /usr/bin/gcc-4.8; sudo update-alternatives --set g++ /usr/bin/g++-4.8; 
fi

# setup vpython with all packages
# being standalone.sh
#DailyPythonTools location
export base=`pwd`

# package list from FinalStateAnalysis 
# (https://github.com/uwcms/FinalStateAnalysis/blob/master/recipe/install_python.sh)
echo "Installing yolk"
time sudo pip install -U yolk
echo "Installing ipython"
time sudo pip install -U ipython
echo "Installing termcolor"
time sudo pip install -U termcolor
echo "Installing uncertainties <-- awesome error propagation"
time sudo pip install -U uncertainties
echo "Install progressbar"
time sudo pip install -U progressbar
echo "Installing argparse"
time sudo pip install -U argparse
echo "Installing pudb <-- interactive debugging"
time sudo pip install -U pudb
echo "Installing dateutil"
time sudo pip install python-dateutil
echo "Installing PrettyTable"
time sudo pip install PrettyTable

echo "Installing rootpy"
time pip install --user -e $base/external/rootpy

echo "Installing root_numpy"
git clone https://github.com/rootpy/root_numpy.git && (cd root_numpy && python setup.py install --user)
cd $base

if [ ! -d "$base/external/lib" ]; then
	mkdir $base/external/lib
	echo "Building RooUnfold"
	cd $base/external/RooUnfold/
	make -j4
	#remove tmp folder
	rm -fr $base/external/RooUnfold/tmp
	mv $base/external/RooUnfold/libRooUnfold.so $base/external/lib/.
	echo "Updating RooUnfold config"
	cat $base/config/RooUnfold_template.py > $base/config/RooUnfold.py
	echo "library = '$base/external/lib/libRooUnfold.so'" >> $base/config/RooUnfold.py

	echo "Building TopAnalysis"
	cd $base/external/TopAnalysis/
	make -j4
	# remove tmp folder
	rm -fr $base/external/TopAnalysis/tmp
	mv $base/external/TopAnalysis/libTopSVDUnfold.so $base/external/lib/.
	echo "Updating TopSVDUnfold config"
	echo "library = '$base/external/lib/libTopSVDUnfold.so'" > $base/config/TopSVDUnfold.py
fi

cd $base
export PATH=$PATH:$base/bin
# end standalone.sh
# add base path from setup_standalone to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$base
