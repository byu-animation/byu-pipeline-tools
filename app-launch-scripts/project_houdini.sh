#!/bin/sh

# project_houdini.sh: opens houdini with the project environment
# @author Brian Kingery & Ben DeMann

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
echo $HOUDINI_MENU_PATH
echo "Starting Houdini..."
# so I tried to set the $HIP variable but that didn't work. I don't really want people accientally saving their files in the tools directory and I would imagine that they would want to have their home directory as the default $HIP location anyways so we are going to cd into the users home directory, start houdini and then cd back to where ever we were.
currLocation="$( pwd )"
cd ~/
gnome-terminal -e "houdinifx -foreground $@"
# after playing around with this it looks like we might still end up in the same directory we started in. Maybe sh puts you back by itself. I'll just leave it here. It's not hurting anybody.
cd $currLocation


#TODO: Figure out how to render preview to it program
#export RMANFB="it"
