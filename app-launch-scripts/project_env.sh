#!/bin/sh

dir=`dirname $0`

pwd=$(pwd)

#Get the location of project_env.sh so we can set the environment variables accordingly.
scriptLocation="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${scriptLocation}
projectDir="$( cd ../../ && pwd )"

#Check ouptions for specifying a project directory
while getopts p: option
do
	case "${option}"
	in
		p) projectDir=${OPTARG};;
	esac
done

#If the specified project directory is not a directory then quit.
if [ ! -d ${projectDir} ] ;
then
	echo ${projectDir}" is not a directory."
	echo "Usage: sh test.sh -p directory/path"
	exit 1
fi

export BYU_PROJECT_DIR=${projectDir}
export BYU_TOOLS_DIR=${projectDir}/byu-pipeline-tools

# PyQt4
export PYTHONPATH=${PYTHONPATH}:/usr/lib64/python2.7/site-packages

# houdini python
export PYTHONPATH=${PYTHONPATH}:/opt/hfs.current/houdini/python2.7libs

# byu tools
export MAYA_SHELF_DIR=${BYU_TOOLS_DIR}/maya-tools/shelf

export PYTHONPATH=${PYTHONPATH}:${BYU_TOOLS_DIR}
export PATH=${PATH}:${BYU_TOOLS_DIR}/bin

# Nuke
export NUKE_LOCATION=/usr/local/Nuke10.0v5
export NUKE_TOOLS_DIR=${BYU_TOOLS_DIR}/nuke-tools
export NUKE_PATH=${NUKE_TOOLS_DIR}

cd ${pwd}
