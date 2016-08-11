#!/bin/bash
drop_from_path()
{
   # Assert that we got enough arguments
   if test $# -ne 2 ; then
      echo "drop_from_path: needs 2 arguments"
      return 1
   fi

   p=$1
   drop=$2

   newpath=`echo $p | sed -e "s;:${drop}:;:;g" \
                          -e "s;:${drop};;g"   \
                          -e "s;${drop}:;;g"   \
                          -e "s;${drop};;g"`
}


if [ -n "${DPSROOT}" ] ; then
   old_dpsbase=${DPSROOT}
fi


if [ "x${BASH_ARGV[0]}" = "x" ]; then
    if [ ! -f bin/env.sh ]; then
        echo ERROR: must "cd where/DailyPythonScripts/is" before calling ". bin/env.sh" for this version of bash!
        DPSROOT=; export DPSROOT
        return 1
    fi
    DPSROOT="$PWD"; export DPSROOT
else
    # get param to "."
    envscript=$(dirname ${BASH_ARGV[0]})
    DPSROOT=$(cd ${envscript}/..;pwd); export DPSROOT
fi

if [ -n "${old_dpsbase}" ] ; then
   if [ -n "${PATH}" ]; then
      drop_from_path "$PATH" ${old_dpsbase}/bin
      PATH=$newpath
   fi
   if [ -n "${PYTHONPATH}" ]; then
      drop_from_path $PYTHONPATH ${old_dpsbase}
      PYTHONPATH=$newpath
   fi
fi


if [ -z "${PATH}" ]; then
   PATH=$DPSROOT/bin; export PATH
else
   PATH=$DPSROOT/bin:$PATH; export PATH
fi

if [ -z "${PYTHONPATH}" ]; then
   PYTHONPATH=$DPSROOT/python; export PYTHONPATH
else
   PYTHONPATH=$DPSROOT/python:$PYTHONPATH; export PYTHONPATH
fi

CONDAINSTALL=/software/miniconda
PATH=$CONDAINSTALL/bin:$PATH; export PATH
export ENV_NAME=dps-new
export CONDA_ENV_PATH=$CONDAINSTALL/envs/${ENV_NAME}
source $CONDAINSTALL/bin/activate ${ENV_NAME}
export PYTHONPATH=$PYTHONPATH:`pwd`
unset old_dpsbase
unset envscript
