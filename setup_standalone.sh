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

echo "Building RooUnfold"
cd $base/external/RooUnfold/
make -j4
#remove tmp folder
rm -fr $base/external/RooUnfold/tmp

if [ ! -d "$base/external/lib" ]; then
	mkdir $base/external/lib
fi
mv $base/external/RooUnfold/libRooUnfold.rootmap $base/external/lib/.
mv $base/external/RooUnfold/libRooUnfold.so $base/external/lib/.

echo "Updating RooUnfold config"
cat $base/config/RooUnfold_template.py > $base/config/RooUnfold.py
echo "library = '$base/external/lib/libRooUnfold.so'" >> $base/config/RooUnfold.py
