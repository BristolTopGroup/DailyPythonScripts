export base=`pwd`
export conda_base=/software/miniconda/envs/dps
export vpython=$base/external/vpython
export PATH=/software/miniconda/bin:$PATH

source activate dps

export PYTHONPATH=$PYTHONPATH:`pwd`

if [ ! -z "$CMSSW_BASE" ]; then
	echo "CMSSW has been set up..."
	echo "...giving priority to conda dps."
    export PYTHONPATH=$conda_base/lib/python2.7/site-packages:$PYTHONPATH
fi

export PATH=$PATH:$base/bin
