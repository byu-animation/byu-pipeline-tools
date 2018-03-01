export startFrame=$1
export endFrame=$2
export step=$3
export rendernode=$4
export fileName=$5

echo "----START RENDER TASK---- startFrame: $startFrame | endFrame: $endFrame | step: $step | rendernode $rendernode | fileName $fileName"

# houdini
# sh /groups/grendel/byu-pipeline-tools/app-launch-scripts/project_houdini.sh
if [ $endFrame -gt $startFrame ]
	then
		/opt/hfs.current/bin/hscript -c ./hscriptCmd.cmd $fileName
fi
echo "----END  RENDER  TASK---- startFrame: $startFrame | endFrame: $endFrame | step: $step | rendernode $rendernode | fileName $fileName"
