#!/bin/sh

# project_houdini.sh: opens houdini with the project environment
# @author Brian Kingery

if [ -z "${HFS}" ]
then
    # The default HFS directory if it isn't already defined
    export HFS=/opt/hfs.current
    # If working on the new image, update the houdini directory
    if [ ! -d "${HFS}" ]
    then
        export HFS=/opt/hfs15.5.480
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

export JOB=$BYU_PROJECT_DIR
HOUDINI_TOOLS=${BYU_TOOLS_DIR}/houdini-tools
export PYTHONPATH=${PYTHONPATH}:${HOUDINI_TOOLS}
export HOUDINI_PATH=${HOUDINI_PATH}:${HOUDINI_TOOLS}:${BYU_PROJECT_DIR}"/production;&"

export HOUDINI_MENU_PATH=${HOUDINI_TOOLS}"/houdini-menus;&"

echo "Starting Houdini..."
# so I tried to set the $HIP variable but that didn't work. I don't really want people accientally saving their files in the tools directory and I would imagine that they would want to have their home directory as the default $HIP location anyways so we are going to cd into the users home directory, start houdini and then cd back to where ever we were.
currLocation="$( pwd )"
cd ~/
houdinifx "$@"
# after playing around with this it looks like we might still end up in the same directory we started in. Maybe sh puts you back by itself. I'll just leave it here. It's not hurting anybody.
cd $currLocation
