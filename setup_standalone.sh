# Helper functions
success() {
	if [ $1 -eq 0 ];then
		echo "Successfully installed $2"
	else
		echo "Failed to install $2"
	fi
}

#DailyPythonTools location
export base=`pwd`
export vpython=$base/external/vpython
cd $base/external/virtualenv

if [ ! -z "$CMSSW_BASE" ]; then
    echo "CMSSW has been set up..."
    echo "...giving priority to vpython."
    export PYTHONPATH=$vpython/lib/python2.7/site-packages:$PYTHONPATH
    echo $PYTHONPATH
fi

echo "Creating virtual python environment in $vpython"
if [ ! -d "$vpython" ]; then
  python virtualenv.py --distribute $vpython
else
  echo "...virtual environment already setup."
fi

echo "Activating virtual python environment"
cd $vpython
export VIRTUAL_ENV_DISABLE_PROMPT=1
source bin/activate

#package list from FinalStateAnalysis (https://github.com/uwcms/FinalStateAnalysis/blob/master/recipe/install_python.sh)
echo "Installing yolk"
pip install -U yolk &> /dev/null
success $? yolk
echo "Installing ipython"
pip install -U ipython &> /dev/null
success $? ipython
echo "Installing termcolor"
pip install -U termcolor &> /dev/null
success $? termcolor
echo "Installing uncertainties <-- awesome error propagation"
pip install -U uncertainties &> /dev/null
success $? uncertainties
echo "Install progressbar"
pip install -U progressbar &> /dev/null
success $? progressbar
echo "Install cython"
pip install -U cython &> /dev/null
success $? cython
echo "Installing argparse"
pip install -U argparse &> /dev/null
success $? argparse
echo "Installing pudb <-- interactive debugging"
pip install -U pudb &> /dev/null
success $? pudb
echo "Installing numpy"
pip install -U numpy &> /dev/null
success $? numpy
echo "Installing dateutil"
pip install python-dateutil &> /dev/null
success $? dateutil
echo "Installing PrettyTable"
pip install PrettyTable &> /dev/null
success $? PrettyTable

echo "Installing matplotlib"
#Adding freetype and libpng library and include paths from CMSSW, specific to the version but should be ok for now.
export LDFLAGS="$LDFLAGS -L$VO_CMS_SW_DIR/$SCRAM_ARCH/external/freetype/2.4.7/lib -L$VO_CMS_SW_DIR/$SCRAM_ARCH/external/libpng/1.2.46/lib"
export CFLAGS="$CFLAGS -I$VO_CMS_SW_DIR/$SCRAM_ARCH/external/freetype/2.4.7/include -I$VO_CMS_SW_DIR/$SCRAM_ARCH/external/freetype/2.4.7/include/freetype2 -I$VO_CMS_SW_DIR/$SCRAM_ARCH/external/libpng/1.2.46/include"
#pip install -e $base/external/matplotlib
pip install matplotlib==1.3.1 &> /dev/null
success $? matplotlib
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
