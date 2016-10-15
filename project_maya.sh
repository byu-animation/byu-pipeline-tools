#!/bin/sh

# project_maya.sh: opens maya with the project environment
# @author Brian Kingery

# source project environment
DIR=`dirname $0`
source ${DIR}/project_env.sh

export CURRENT_PROG='Maya'
export MAYA_PRESET_PATH=${BYU_TOOLS_DIR}/maya-tools/presets

# Change directories so current directory is not in the tools folder
cd ${USER_DIR}

echo "Starting Maya..."
maya -script ${MAYA_SHELF_DIR}/byu_shelf.mel &

