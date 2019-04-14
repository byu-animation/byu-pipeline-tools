DIR=`dirname $0`
source ../../app-launch-scripts/project_env.sh



export CURRENT_PROG='Maya'

# Set Maya file path variables. For more information, check out https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2015/ENU/Maya/files/GUID-228CCA33-4AFE-4380-8C3D-18D23F7EAC72-htm.html
export MAYA_PRESET_PATH=${BYU_TOOLS_DIR}/maya-tools/presets
export MAYA_PLUG_IN_PATH=${BYU_TOOLS_DIR}/maya-tools/plug-ins
export MAYA_SHELF_PATH=${BYU_TOOLS_DIR}/maya-tools/shelf
export MAYA_CUSTOM_TEMPLATE_WRITE_PATH=${BYU_TOOLS_DIR}/maya-tools/viewTemplates
export XBMLANGPATH=${BYU_TOOLS_DIR}/maya-tools/shelf/icons/%B


# Change directories so current directory is not in the tools folder
#cd ${USER_DIR}
if [ $# -eq 0 ]; then echo 'Specify Python Script to run as first argument'; exit
else '/usr/autodesk/maya2018/bin/mayapy' $1
fi
