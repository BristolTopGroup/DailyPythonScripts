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
export conda_env=dps
export PATH=/software/miniconda/bin:$PATH

if [ ! -z "$CMSSW_BASE" ]; then
    echo "CMSSW has been set up..."
    echo "...giving priority to conda."
    export PYTHONPATH=/software/miniconda/envs/${conda_env}/lib/python2.7/site-packages:$PYTHONPATH
    echo $PYTHONPATH
fi

echo "Activating conda environment ${conda_env}"
source activate ${conda_env}
echo "setting up BOOST_INCLUDEDIR"
export BOOST_INCLUDEDIR=/software/miniconda/envs/${conda_env}/include
# the following should only be done on soolin
# otherwise DICE jobs might interfere with each other
echo "I am running on machine ${HOSTNAME}"

if [ ! -d "$base/external/lib" ]; then
	mkdir $base/external/lib
	echo "Building RooUnfold"
	cd $base/external/RooUnfold/
	cmake CMakeLists.txt
	make RooUnfold -j4
	success $? RooUnfold
	#remove tmp folder
	rm -fr $base/external/RooUnfold/tmp
	mv $base/external/RooUnfold/libRooUnfold.so $base/external/lib/.
	echo "Updating RooUnfold config"
	cat $base/config/RooUnfold_template.py > $base/config/RooUnfold.py
	echo "library = '$base/external/lib/libRooUnfold.so'" >> $base/config/RooUnfold.py
	cp $base/external/RooUnfold/RooUnfoldDict_rdict.pcm $base/.
fi

cd $base
echo "Adding ${base}/bin to path"
export PATH=$PATH:$base/bin
