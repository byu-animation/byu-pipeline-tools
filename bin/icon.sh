#!/bin/bash

nickname=""

while getopts n: option
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
	echo "Error: Invalid input."
    echo "Usage: icon.sh project_name project_dir script_name script_icon script"
	exit 1
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
FILENAME=${PROJECT_PATH}"byu-${NOSPACES,,}"

echo "#!/usr/bin/env xdg-open" > ${FILENAME}.desktop
echo "[Desktop Entry]" >> ${FILENAME}.desktop
echo "Version=x.y" >> ${FILENAME}.desktop
echo "Name=${PROGRAM_NAME}" >> ${FILENAME}.desktop
echo "Name[en_US]=${PROGRAM_NAME}" >> ${FILENAME}.desktop
echo "Comment=BYU Pipeline Tools ${PROJECT_NAME} ${SOFTWARE_NAME}" >> ${FILENAME}.desktop
echo "Exec=${PROJECT_PATH}byu-pipeline-tools/app-launch-scripts/${SCRIPT}" >> ${FILENAME}.desktop
echo "Icon=${PROJECT_PATH}byu-pipeline-tools/assets/images/icons/${ICON}" >> ${FILENAME}.desktop
echo "Terminal=false" >> ${FILENAME}.desktop
echo "Type=Application" >> ${FILENAME}.desktop
echo "Categories=Utility;Application;" >> ${FILENAME}.desktop

chmod 770 ${FILENAME}.desktop
