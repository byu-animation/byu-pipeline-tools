startFrame=$1
endFrame=$2
renderNode=$3
hipFile=$4

numCores=$(grep -c ^processor /proc/cpuinfo)
numFrames=$(($endFrame - $startFrame))
framesPerCore=$(($numFrames / $numCores))
leftoverFrames=$(($numFrames % $numCores))
declare -a tasks

echo "Start rib creation"
cd /users/animation/bdemann/Documents/grendel-dev/byu-pipeline-tools/houdini-tools/parallelRibs
ls
pwd

for (( i=0; i<$numCores; i++))
	do
		firstFrame=$(($startFrame + $i))
		lastFrame=$(($endFrame))
		step=$numCores
		echo "rendering from ${firstFrame} to ${lastFrame} with a step of ${step}"
		./renderTask.sh ${firstFrame} ${lastFrame} ${step} ${renderNode} ${hipFile} &
		tasks[$i]=$!
		echo $!
	done

for (( i=0; i<$numCores; i++))
	do
		wait ${tasks[$i]}
		echo "finshed task $i wtih PID ${tasks[$i]}"
	done

echo "Finish rib creation"
