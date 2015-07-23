#!/bin/bash
# This script is meant to be called by the "before_install" step defined in
# .travis.yml. See http://docs.travis-ci.com/ for more details.
# The behaviour of the script is controlled by environment variabled defined
# in the .travis.yml in the top level folder of the project.

#set -e

# Check if we are running Python 2 or 3. This is needed for the apt-get package names
if [[ $TRAVIS_PYTHON_VERSION == '3.2' ]]; then 
	export PYTHON_SUFFIX="3"; 
fi

sudo add-apt-repository --yes ppa:kalakris/cmake
# add repositories for gcc ${GCC_VERSION} and clang $CLANG_VERSION (set in .travis.yml)
sudo add-apt-repository --yes ppa:ubuntu-toolchain-r/test
sudo add-apt-repository --yes 'deb http://llvm.org/apt/precise/ llvm-toolchain-precise main'
sudo add-apt-repository --yes 'deb http://ppa.launchpad.net/boost-latest/ppa/ubuntu precise main'
wget -O - http://llvm.org/apt/llvm-snapshot.gpg.key | sudo apt-key add -
# Needed because sometimes travis' repositories get out of date
sudo apt-get update -q
# Install the dependencies we need
time sudo apt-get -q install cmake clang-${CLANG_VERSION} libclang-${CLANG_VERSION}-dev gcc-${GCC_VERSION} g++-${GCC_VERSION} boost${BOOST_VERSION} libboost${BOOST_VERSION}-dev libboost-test${BOOST_VERSION}-dev \
python${PYTHON_SUFFIX}-numpy python${PYTHON_SUFFIX}-sphinx python${PYTHON_SUFFIX}-pip cython${PYTHON_SUFFIX}
if [[ $TRAVIS_PYTHON_VERSION == '2.7' ]]; then 
	time sudo apt-get install -qq python-matplotlib python-tables; 
fi

pip install --upgrade pip
pip install nose2 --upgrade

# setup newer compilers ( we need gcc >= 4.7 for c++11
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-${GCC_VERSION} 50;
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-${GCC_VERSION} 50;
sudo update-alternatives --set gcc /usr/bin/gcc-${GCC_VERSION}; 
sudo update-alternatives --set g++ /usr/bin/g++-${GCC_VERSION};

sudo update-alternatives --install /usr/bin/clang clang /usr/bin/clang-${CLANG_VERSION} 50;
sudo update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-${CLANG_VERSION} 50;
sudo update-alternatives --set clang /usr/bin/clang-${CLANG_VERSION};
sudo update-alternatives --set clang++ /usr/bin/clang++-${CLANG_VERSION};
