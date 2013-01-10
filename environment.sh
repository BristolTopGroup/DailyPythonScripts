export base=`pwd`
export vpython=$base/external/vpython

if [ -d "$vpython" ]; then
	echo "Activating virtual python environment"
	export VIRTUAL_ENV_DISABLE_PROMPT=1
	source $vpython/bin/activate
fi

cd $base
export PYTHONPATH=$PYTHONPATH:`pwd`