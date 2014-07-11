#!/bin/bash
# This script is meant to be called by the "install" step defined in
# .travis.yml. See http://docs.travis-ci.com/ for more details.
# The behavior of the script is controlled by environment variabled defined
# in the .travis.yml in the top level folder of the project.

set -e

# Helper functions
success() {
	if [ $1 -eq 0 ];then
		echo "Successfully installed $2"
	else
		echo "Failed to install $2"
	fi
}

# Check if we are running Python 2 or 3. This is needed for the apt-get package names
if [[ $TRAVIS_PYTHON_VERSION == '3.2' ]]; then 
	export PYTHON_SUFFIX="3"; 
fi

# add repositories for gcc 4.8 and clang 3.5
sudo add-apt-repository --yes ppa:ubuntu-toolchain-r/test
sudo add-apt-repository --yes 'deb http://llvm.org/apt/precise/ llvm-toolchain-precise main'
wget -O - http://llvm.org/apt/llvm-snapshot.gpg.key | sudo apt-key add -
# Needed because sometimes travis' repositories get out of date
time sudo apt-get update -qq

# Install the dependencies we need
time sudo apt-get -qq install clang-3.5 libclang-3.5-dev gcc-4.8 g++-4.8
time sudo apt-get install -qq python${PYTHON_SUFFIX}-numpy python${PYTHON_SUFFIX}-sphinx python${PYTHON_SUFFIX}-nose
# matplotlib and PyTables are not available for Python 3 as packages from the main repo yet.
if [[ $TRAVIS_PYTHON_VERSION == '2.7' ]]; then time sudo apt-get install -qq python${PYTHON_SUFFIX}-matplotlib python${PYTHON_SUFFIX}-tables; fi

# This is needed for the docs
git submodule init
git submodule update

# Use system python, not virtualenv, because building the dependencies from source takes too long
deactivate # the virtualenv


# Install the dependencies we need
time sudo apt-get -qq install clang-3.5 libclang-3.5-dev gcc-4.8 g++-4.8
time sudo apt-get install -qq python${PYTHON_SUFFIX}-numpy python${PYTHON_SUFFIX}-sphinx python${PYTHON_SUFFIX}-nose
# matplotlib and PyTables are not available for Python 3 as packages from the main repo yet.
if [[ $TRAVIS_PYTHON_VERSION == '2.7' ]]; then time sudo apt-get install -qq python${PYTHON_SUFFIX}-matplotlib python${PYTHON_SUFFIX}-tables; fi

# Install a ROOT binary that we custom-built in a 64-bit Ubuntu VM
# for the correct python / ROOT version
time wget --no-check-certificate https://copy.com/s3BcYu1drmZa/ci/root_builds/root_v${ROOT}_python_${TRAVIS_PYTHON_VERSION}.tar.gz
time tar zxf root_v${ROOT}_python_${TRAVIS_PYTHON_VERSION}.tar.gz
mv root_v${ROOT}_python_${TRAVIS_PYTHON_VERSION} root
source root/bin/thisroot.sh
# setup newer compilers for ROOT 6
if [[ $ROOT == '6-00-00' ]]; then 
	sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.8 50;
	sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-4.8 50; 
	sudo update-alternatives --set gcc /usr/bin/gcc-4.8; sudo update-alternatives --set g++ /usr/bin/g++-4.8; 
fi

# setup vpython with all packages
export base=`pwd`
echo "Installing rootpy"
pip install -e $base/external/rootpy &> /dev/null
success $? rootpy

echo "Installing root_numpy"
pip install root_numpy &> /dev/null
success $? root_numpy

if [ ! -d "$base/external/lib" ]; then
	mkdir $base/external/lib
	echo "Building RooUnfold"
	cd $base/external/RooUnfold/
	make -j4
	success $? RooUnfold
	#remove tmp folder
	rm -fr $base/external/RooUnfold/tmp
	mv $base/external/RooUnfold/libRooUnfold.so $base/external/lib/.
	echo "Updating RooUnfold config"
	cat $base/config/RooUnfold_template.py > $base/config/RooUnfold.py
	echo "library = '$base/external/lib/libRooUnfold.so'" >> $base/config/RooUnfold.py

	echo "Building TopAnalysis"
	cd $base/external/TopAnalysis/
	make -j4 &> /dev/null
	success $? TopAnalysis
	# remove tmp folder
	rm -fr $base/external/TopAnalysis/tmp
	mv $base/external/TopAnalysis/libTopSVDUnfold.so $base/external/lib/.
	echo "Updating TopSVDUnfold config"
	echo "library = '$base/external/lib/libTopSVDUnfold.so'" > $base/config/TopSVDUnfold.py
fi

cd $base
export PATH=$PATH:$base/bin
# add base path from setup_standalone to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$base
