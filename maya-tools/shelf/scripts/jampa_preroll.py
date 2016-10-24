#Author: Trevor Barrus
import maya.cmds as cm

def go():
    rig_controls = {
"jampa_rig_main_ankle_l_IK_cc_01", 
"jampa_rig_main_ankle_r_IK_cc_01", 
"jampa_rig_main_COG_cc_01", 
"jampa_rig_main_Sexy_Hips_cc_01", 
"jampa_rig_main_belly_cc_01", 
"jampa_rig_main_chest_cc_01", 
"jampa_rig_main_neck_base_cc_01", 
"jampa_rig_main_neck_middle_cc_01", 
"jampa_rig_main_upper_arm_l_FK_cc_01", 
"jampa_rig_main_forearm_l_FK_cc_01", 
"jampa_rig_main_forearm_l_FK_cc_01", 
"jampa_rig_main_upper_arm_r_FK_cc_01", 
"jampa_rig_main_forearm_r_FK_cc_01", 
"jampa_rig_main_wrist_r_FK_cc_01", 
"jampa_rig_main_shoulder_r_cc_01", 
"jampa_rig_main_shoulder_l_cc_01"
    }

    attrs = {
"rotateX",
"rotateY",
"rotateZ",
"translateX",
"translateY",
"translateZ",
"scaleX",
"scaleY",
"scaleZ"
    }

    for c in rig_controls:
        for attr in attrs:
            cm.currentTime(-20)
            channel = c + "." + attr
        
            #If channel can be keyed, set a keyframe to match the value at frame 0
            if cm.getAttr(channel, keyable=True):
                cm.setAttr(channel, cm.getAttr(channel, time=0))
                cm.setKeyframe(channel)
                cm.keyTangent(ott="step")
            
                #Set key at frame -40 in resting cloth pose
                cm.currentTime(-40)
                if channel != "jampa_rig_main_upper_arm_r_FK_cc_01.rotateZ":
                    cm.setAttr(channel, (0 if "scale" not in attr else 1))
                else:
                    cm.setAttr(channel, -45)
                
                cm.setKeyframe(channel)
            
    #Handle cases where controls do not have regular transformation channels
    cm.currentTime(-20)
    cm.setAttr("jampa_rig_main_foot_l_cc_01.Forward_Back", cm.getAttr("jampa_rig_main_foot_l_cc_01.Forward_Back", time=0))
    cm.setKeyframe("jampa_rig_main_foot_l_cc_01.Forward_Back")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_foot_r_cc_01.Forward_Back", cm.getAttr("jampa_rig_main_foot_r_cc_01.Forward_Back", time=0))
    cm.setKeyframe("jampa_rig_main_foot_r_cc_01.Forward_Back")
    cm.keyTangent(ott="step")

    cm.currentTime(-40)
    cm.setAttr("jampa_rig_main_foot_l_cc_01.Forward_Back", 0)
    cm.setKeyframe("jampa_rig_main_foot_l_cc_01.Forward_Back")
    cm.setAttr("jampa_rig_main_foot_r_cc_01.Forward_Back", 0)
    cm.setKeyframe("jampa_rig_main_foot_r_cc_01.Forward_Back")
