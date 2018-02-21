export startFrame=$1
export endFrame=$2
export step=$3
export rendernode=$4
export fileName=$5

echo "frame $startFrame"
echo "last frame $endFrame"
echo "step $step"
echo "rendernode $rendernode"
echo "fileName $fileName"

# houdini
# sh /groups/grendel/byu-pipeline-tools/app-launch-scripts/project_houdini.sh
/opt/hfs.current/bin/hscript -c ./hscriptCmd.cmd $fileName

echo 'done'
# read name
# echo name
