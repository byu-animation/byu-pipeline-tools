#!/bin/sh

# project_houdini.sh: opens houdini with the project environment
# @author Brian Kingery & Ben DeMann

echo "Trying to initialize Houdini environment..."

if [ -z "${HFS}" ]
then
	# The default HFS directory if it isn't already defined
	export HFS=/opt/hfs.current
	# If working on the new image, update the houdini directory
	if [ ! -d "${HFS}" ]
	then
		export HFS=/opt/hfs17.0
	fi
fi

# source current houdini setup
cd ${HFS}
source ./houdini_setup
cd -

# source project environment
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source ${DIR}/project_env.sh

export CURRENT_PROG='Houdini'

# We need this line in order for gridmarkets to work.
export HOUDINI_USE_HFS_PYTHON=1

export JOB=${BYU_PROJECT_DIR}
HOUDINI_TOOLS=${BYU_TOOLS_DIR}/houdini-tools
TRACTOR_AUTHOR=/opt/pixar/Tractor-2.2/lib/python2.7/site-packages
export PYTHONPATH=${PYTHONPATH}:${HOUDINI_TOOLS}:${TRACTOR_AUTHOR}
export HOUDINI_PATH=${HOUDINI_PATH}:${HOUDINI_TOOLS}:${BYU_PROJECT_DIR}"/production;&":${BYU_PROJECT_DIR}"/production/hda;&"
export HOUDINI_DSO_PATH=${HOUDINI_DSO_PATH}:${BYU_PROJECT_DIR}"/production/dso;&"
export HOUDINI_DEFAULT_RIB_TARGET="prman21.0.byu"

export HOUDINI_MENU_PATH=${HOUDINI_TOOLS}"/houdini-menus;&"
export HOUDINI_TOOLBAR_PATH=${BYU_PROJECT_DIR}"/production/tabs;&"

export HOUDINI_UI_ICON_PATH=${BYU_TOOLS_DIR}"/assets/images/icons/tool-icons;&"
