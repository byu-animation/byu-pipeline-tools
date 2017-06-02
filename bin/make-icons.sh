#!/bin/bash
usage() { echo "make-icon: [-n NICKNAME] projectName projectDir" 1>&2; exit; }

nickname=""

while getopts n: option
do
	case "${option}"
	in
		n) nickname=${OPTARG}
		shift
		shift
		;;
		*)
		usage
	esac
done

if [ "$1" == "" ]||[ "$2" == "" ]; then
	usage
fi

PROJECT_NAME="$1"
PROJECT_PATH="$2"

function icon {
	icon_usage() { echo "icon: [-n NICKNAME] projectName projectDir scriptName scriptIcon script" 1>&2; exit; }
	local nickname=""

	local OPTIND n option
	while getopts ":n:" option
	do
		case "${option}"
		in
			n) nickname=${OPTARG}
			shift
			shift
			;;
		esac
	done

	if [ "$1" == "" ]||[ "$2" == "" ]||[ "$3" == "" ]||[ "$4" == "" ]||[ "$5" == "" ]; then
		icon_usage
	fi

	PROJECT_NAME="$1"
	PROJECT_PATH="$2"
	SOFTWARE_NAME="$3"
	ICON="$4"
	SCRIPT="$5"

	if [ "$nickname" == "" ]; then
		PROGRAM_NAME=${PROJECT_NAME}" "${SOFTWARE_NAME}
	else
		PROGRAM_NAME=$nickname
	fi

	NOSPACES=${SOFTWARE_NAME// /-}
	FILENAME=${PROJECT_PATH}"/${NOSPACES,,}-byu"

	echo "#!/usr/bin/env xdg-open" > ${FILENAME}.desktop
	echo "[Desktop Entry]" >> ${FILENAME}.desktop
	echo "Version=x.y" >> ${FILENAME}.desktop
	echo "Name=${PROGRAM_NAME}" >> ${FILENAME}.desktop
	echo "Name[en_US]=${PROGRAM_NAME}" >> ${FILENAME}.desktop
	echo "Comment=BYU Pipeline Tools ${PROJECT_NAME} ${SOFTWARE_NAME}" >> ${FILENAME}.desktop
	echo "Exec=${PROJECT_PATH}/byu-pipeline-tools/app-launch-scripts/${SCRIPT}" >> ${FILENAME}.desktop
	echo "Icon=${PROJECT_PATH}/byu-pipeline-tools/assets/images/icons/${ICON}" >> ${FILENAME}.desktop
	echo "Terminal=false" >> ${FILENAME}.desktop
	echo "Type=Application" >> ${FILENAME}.desktop
	echo "Categories=Utility;Application;" >> ${FILENAME}.desktop

	chmod 770 ${FILENAME}.desktop
}


if [ "${nickname}" != "" ]; then
	icon -n "${nickname}aya" ${PROJECT_NAME} ${PROJECT_PATH} Maya byu-maya.png project_maya.sh
	icon -n "${nickname}ini" ${PROJECT_NAME} ${PROJECT_PATH} Houdini byu-houdini.png project_houdini.sh
	icon -n "${nickname}ari" ${PROJECT_NAME} ${PROJECT_PATH} Mari byu-mari.png project_mari.sh
	icon -n "${nickname}uke" ${PROJECT_NAME} ${PROJECT_PATH} Nuke byu-nuke.png project_nuke.sh
	icon -n "${nickname}ack" ${PROJECT_NAME} ${PROJECT_PATH} Slack byu-slack.png project_slack.sh
else
	icon ${PROJECT_NAME} ${PROJECT_PATH} Maya byu-maya.png project_maya.sh
	icon ${PROJECT_NAME} ${PROJECT_PATH} Houdini byu-houdini.png project_houdini.sh
	icon ${PROJECT_NAME} ${PROJECT_PATH} Mari byu-mari.png project_mari.sh
	icon ${PROJECT_NAME} ${PROJECT_PATH} Nuke byu-nuke.png project_nuke.sh
	icon ${PROJECT_NAME} ${PROJECT_PATH} Slack byu-slack.png project_slack.sh
fi

icon -n "Pipeline Instructions" ${PROJECT_NAME} ${PROJECT_PATH} "Pipeline Instructions" byu-how-to.png project_how_to.sh
icon ${PROJECT_NAME} ${PROJECT_PATH} Browser byu-browser.png project_browser.sh
