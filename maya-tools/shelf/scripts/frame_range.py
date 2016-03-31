import maya.cmds as cmds
import os

from byuam import Project

def go():

    project = Project()
    filepath = cmds.file(q=True, sceneName=True)

    checkout = project.get_checkout(os.path.dirname(filepath))
    if checkout is not None:
        body_name = checkout.get_body_name()
        body = project.get_body(body_name)
        if body.is_shot():
            frame_range = body.get_frame_range()
            if frame_range > 0:
                print "set frame range to " + str(frame_range)
                cmds.playbackOptions(animationStartTime=1.0, animationEndTime=frame_range, minTime=1.0, maxTime=frame_range, framesPerSecond=24)
            else:
                print "shot has invalid frame range"
        else:
            print "not a shot"  
    else:
        print "Unknown Shot, can't set frame range"