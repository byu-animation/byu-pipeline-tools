startFrame=$1
endFrame=$2
renderNode=$3
hipFile=$4
numCores=$5

echo "--------BEGIN TASK DISTRIBUTION------------"
cd $JOB/byu-pipeline-tools/houdini-tools/parallelRibs

availableCores=$(grep -c ^processor /proc/cpuinfo)
if [ $numCores -gt $availableCores ]
	then
		numCores=$(($availableCores - 1))
fi

numFrames=$(($endFrame - ($startFrame - 1)))

# Make sure we aren't using more cores than we are rendering frames
if [ $numCores -gt $numFrames ]
	then
		numCores=$numFrames
fi

echo "we are working with $numCores cores"

declare -a tasks

echo "Start rib creation"

for (( i=0; i<$numCores; i++))
	do
		firstFrame=$(($startFrame + $i))
		lastFrame=$(($endFrame))
		step=$numCores
		echo "Rendering from ${firstFrame} to ${lastFrame} with a step of ${step}"
		./renderTask.sh ${firstFrame} ${lastFrame} ${step} ${renderNode} ${hipFile} &
		tasks[$i]=$!
		echo "Started rendering on proccss PID $!"
	done

for (( i=0; i<$numCores; i++))
	do
		wait ${tasks[$i]}
		echo "Finshed task $i with PID ${tasks[$i]}"
	done

echo "Finish rib creation"
echo "--------END TASK DISTRIBUTION------------"
