#!/bin/sh

export BYU_PROJECT_DIR=/groups/dusk
export BYU_TOOLS_DIR=/groups/dusk/byu-pipeline-tools

# PyQt4
export PYTHONPATH=${PYTHONPATH}:/usr/lib64/python2.7/site-packages

# houdini python
export PYTHONPATH=${PYTHONPATH}:/opt/hfs.current/houdini/python2.7libs

# byu tools
export MAYA_SHELF_DIR=${BYU_TOOLS_DIR}/maya-tools/shelf

export PYTHONPATH=${PYTHONPATH}:${BYU_TOOLS_DIR}
export PATH=${PATH}:${BYU_TOOLS_DIR}/bin

# Nuke
export NUKE_LOCATION=/usr/local/Nuke10.0v2
export NUKE_TOOLS_DIR=${BYU_TOOLS_DIR}/nuke-tools
export NUKE_PATH=${NUKE_TOOLS_DIR}
