#!/bin/bash

#source project environment
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source ${DIR}/project_env.sh

export CURRENT_PROG='Mari'
export JOB=${BYU_PROJECT_DIR}
export BYU_TOOLS_DIR=${JOB}/byu-pipeline-tools
export MARI_TOOLS=${BYU_TOOLS_DIR}/mari-tools
export MARI_SCRIPT_PATH=${MARI_TOOLS}
export MARI_DEFAULT_GEOMETRY_PATH=${JOB}/production/assets
# What do these last two do? Neither of them are valid paths anymore...
export ICONS=/usr/local/Mari2.6v4/Media/Icons/
export PATH=/opt/hfs14.0.201.13/bin:$PATH

###################################################

wacomTabSetUp()
{
	local DEVICE="Wacom Cintiq 22HD"
	local STYLUS="${DEVICE} Pen stylus"
	local ERASER="${DEVICE} Pen eraser"
	local PAD="${DEVICE} Pad pad"
    ## This Preset is set up specifically for Mari 2.0
    ## Stylus
    xsetwacom set "${STYLUS}" MapToOutput HEAD-1
    ## Eraser
    xsetwacom set "${ERASER}" MapToOutput HEAD-1
    ## Pad
    xsetwacom set "${PAD}" MapToOutput HEAD-1
    ## Central button (Full Screen)
    ##xsetwacom set "Wacom Cintiq 22HD pad" Button 1 "key f11"
    ## Button Mapping Left
    xsetwacom set "${PAD}" StripLeftDown "key minus"      # Brush radius
    xsetwacom set "${PAD}" StripLeftUp "key plus"      # Brush radius
    xsetwacom set "${PAD}" Button 1 "key +shift"      # Shift
    xsetwacom set "${PAD}" Button 2 "key +c"     # EyeDropper
    xsetwacom set "${PAD}" Button 3 "key +k"      # Brushes
    xsetwacom set "${PAD}" Button 8 "key +alt"      # Alt
    xsetwacom set "${PAD}" Button 9 "key ctrl z"      # Undo
    xsetwacom set "${PAD}" Button 10 "key b"      # Bake Paint Layer
    xsetwacom set "${PAD}" Button 11 "key super F9"      # Pie Selector
    xsetwacom set "${PAD}" Button 12 "key +x"      # Guestures
    ##xsetwacom set "Wacom Cintiq 22HD pad" Button 13 "key home"      # Hide All Pallates
    ## Button Mapping Right
    xsetwacom set "${PAD}" StripRightUp "key super pgup"      # brush radius (must be mapped in GIMP)
    xsetwacom set "${PAD}" StripRightDown "key super pgdn"   # +ctrl = faster
    xsetwacom set "${PAD}" Button 15 "key t"      # Hide Selection
    xsetwacom set "${PAD}" Button 16 "key t"      # Show Entire Object
    xsetwacom set "${PAD}" Button 17 "key super F2"      # F2
    xsetwacom set "${PAD}" Button 18 "key super F3"      # F3
    xsetwacom set "${PAD}" Button 19 "key n"      # Hard Brush
    xsetwacom set "${PAD}" Button 20 "key n"      # Open BYU Houdini
    xsetwacom set "${PAD}" Button 21 "key n"      # Open BYU Maya
    xsetwacom set "${PAD}" Button 22 "key n"      # Open Terminal

    # Here is the layout for custom mapping:
    #
    #   Left              Right
    # +-----------+     +-----------+
    # | Button 2  |     | Button 15 |
    # +-----------+     +-----------+
    # | Button 3  |     | Button 16 |
    # +-----------+     +-----------+
    # | Button 8  |     | Button 17 |
    # +-----------+     +-----------+
    # | Button 9  |     | Button 18 |
    # +-----------+     +-----------+
    # +-----------+     +-----------+
    # | Button 1  |     | Button 14 |
    # +-----------+     +-----------+
    # +-----------+     +-----------+
    # | Button 10 |     | Button 19 |
    # +-----------+     +-----------+
    # | Button 11 |     | Button 20 |
    # +-----------+     +-----------+
    # | Button 12 |     | Button 21 |
    # +-----------+     +-----------+
    # | Button 13 |     | Button 22 |
    # +-----------+     +-----------+
    #

	echo "Pen Tablet Settings Calibrated";
}
wacomTabSetUp

# Starting Mari
echo "Starting Mari...";
# /usr/local/Mari2.6v4/mari
${MARI_LOCATION}/mari
