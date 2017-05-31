#!/bin/bash

shortProjectName=""

while getopts s: option
do
	case "${option}"
	in
		s) shortProjectName=${OPTARG}
		shift
		shift
		;;
	esac
done

if [ "$1" == "" ]||[ "$2" == "" ]; then
	echo "Error: Invalid input."
    echo "Usage: make-icon.sh project_name project_dir"
	exit 1
fi

PROJECT_NAME="$1"
PROJECT_PATH="$2"

if [ "${shortProjectName}" != "" ]; then
	sh ./icon.sh -n ${shortProjectName}aya ${PROJECT_NAME} ${PROJECT_PATH} Maya byu-maya.png project_maya.sh
	sh ./icon.sh -n ${shortProjectName}ini ${PROJECT_NAME} ${PROJECT_PATH} Houdini byu-houdini.png project_houdini.sh
	sh ./icon.sh -n ${shortProjectName}ari ${PROJECT_NAME} ${PROJECT_PATH} Mari byu-mari.png project_mari.sh
	sh ./icon.sh -n ${shortProjectName}uke ${PROJECT_NAME} ${PROJECT_PATH} Nuke byu-nuke.png project_nuke.sh
	sh ./icon.sh -n ${shortProjectName}ack ${PROJECT_NAME} ${PROJECT_PATH} Slack byu-slack.png project_slack.sh
else
	sh ./icon.sh ${PROJECT_NAME} ${PROJECT_PATH} Maya byu-maya.png project_maya.sh
	sh ./icon.sh ${PROJECT_NAME} ${PROJECT_PATH} Houdini byu-houdini.png project_houdini.sh
	sh ./icon.sh ${PROJECT_NAME} ${PROJECT_PATH} Mari byu-mari.png project_mari.sh
	sh ./icon.sh ${PROJECT_NAME} ${PROJECT_PATH} Nuke byu-nuke.png project_nuke.sh
	sh ./icon.sh ${PROJECT_NAME} ${PROJECT_PATH} Slack byu-slack.png project_slack.sh
fi

sh ./icon.sh -n "Pipeline Instructions" ${PROJECT_NAME} ${PROJECT_PATH} "Pipeline Instructions" byu-how-to.png project_how_to.sh
sh ./icon.sh ${PROJECT_NAME} ${PROJECT_PATH} Browser byu-browser.png project_browser.sh
