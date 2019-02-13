export startFrame=$1
export endFrame=$2
export step=$3
export rendernode=$4
export fileName=$5

echo "----START RENDER TASK---- startFrame: $startFrame | endFrame: $endFrame | step: $step | rendernode $rendernode | fileName $fileName"
if [ $startFrame -le $endFrame ]
	then
		/opt/hfs.current/bin/hscript -c ./hscriptCmd.cmd $fileName
fi
echo "----END  RENDER  TASK---- startFrame: $startFrame | endFrame: $endFrame | step: $step | rendernode $rendernode | fileName $fileName"
