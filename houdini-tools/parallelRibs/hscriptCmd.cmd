echo 'We are rendering frame '$frame
echo 'We are rendering this node' $rendernode
echo $HIPFILE
render -Vaf $startFrame $endFrame -i $step $rendernode
quit
