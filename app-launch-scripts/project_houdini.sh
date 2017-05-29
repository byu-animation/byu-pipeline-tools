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

export HOUDINI_MENU_PATH=${HOUDINI_TOOLS}/houdini-menus

echo "Starting Houdini..."
houdinifx "$@"
