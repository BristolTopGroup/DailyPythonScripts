export ORIGDIR=`pwd`
cd ../
. $VO_CMS_SW_DIR/cmsset_default.sh
export SCRAM_ARCH=slc6_amd64_gcc481
cmsrel CMSSW_7_1_3
cd CMSSW_7_1_3/src/
cmsenv
git clone https://github.com/EmyrClement/DailyPythonScripts.git -b BLT_Unfold
cd DailyPythonScripts
git submodule init && git submodule update
./setup_standalone.sh
export base=`pwd`
export vpython=$base/external/vpython

if [ -d "$vpython" ]; then
        echo "Activating virtual python environment"
        export VIRTUAL_ENV_DISABLE_PROMPT=1
        source $vpython/bin/activate
fi

cd $base
export PYTHONPATH=$PYTHONPATH:`pwd`
export PATH=$PATH:$base/bin


mkdir unfolding
python experimental/BLTUnfold/runJobsCrab.py -j $1
ls unfolding

echo "Tar output"
tar -cvf $ORIGDIR/output.tar unfolding/*.root
ls -trlh $ORIGDIR