#DailyPythonTools location
export base=`pwd`
export vpython=$base/external/vpython
cd $base/external/virtualenv

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
pip install -U yolk
echo "Installing ipython"
pip install -U ipython
echo "Installing termcolor"
pip install -U termcolor
echo "Installing uncertainties <-- awesome error propagation"
pip install -U uncertainties
echo "Install progressbar"
pip install -U progressbar
echo "Install cython"
pip install -U cython
echo "Installing argparse"
pip install -U argparse
echo "Installing pudb <-- interactive debugging"
pip install -U pudb
echo "Installing pypm"
pip install -U pypm
echo "Installing numpy"
pip install -U numpy

echo "Installing rootpy"
pip install -e $base/external/rootpy

echo "Installing matplotlib"
#Adding freetype and libpng library and include paths from CMSSW, specific to the version but should be ok for now.
export LDFLAGS="$LDFLAGS -L$VO_CMS_SW_DIR/$SCRAM_ARCH/external/freetype/2.4.7/lib -L$VO_CMS_SW_DIR/$SCRAM_ARCH/external/libpng/1.2.46/lib"
export CFLAGS="$CFLAGS -I$VO_CMS_SW_DIR/$SCRAM_ARCH/external/freetype/2.4.7/include -I$VO_CMS_SW_DIR/$SCRAM_ARCH/external/freetype/2.4.7/include/freetype2 -I$VO_CMS_SW_DIR/$SCRAM_ARCH/external/libpng/1.2.46/include"
pip install -e $base/external/matplotlib

if [ ! -d "$base/external/lib" ]; then
	mkdir $base/external/lib
	echo "Building RooUnfold"
	cd $base/external/RooUnfold/
	make -j4
	#remove tmp folder
	rm -fr $base/external/RooUnfold/tmp
	mv $base/external/RooUnfold/libRooUnfold.rootmap $base/external/lib/.
	mv $base/external/RooUnfold/libRooUnfold.so $base/external/lib/.
	echo "Updating RooUnfold config"
	cat $base/config/RooUnfold_template.py > $base/config/RooUnfold.py
	echo "library = '$base/external/lib/libRooUnfold.so'" >> $base/config/RooUnfold.py
fi

cd $base
