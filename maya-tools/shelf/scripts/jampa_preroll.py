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
"jampa_rig_main_shoulder_r_cc_01", 
"jampa_rig_main_shoulder_l_cc_01",
"jampa_rig_main_knee_l_pole_vector_cc_01",
"jampa_rig_main_knee_r_pole_vector_cc_01",
"jampa_rig_main_elbow_r_pole_vector_cc_01"
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
            cm.currentTime(-10)
            channel = c + "." + attr
        
            #If channel can be keyed, set a keyframe to match the value at frame 0
            if cm.getAttr(channel, keyable=True):
                cm.setAttr(channel, cm.getAttr(channel, time=0))
                cm.setKeyframe(channel)
                cm.keyTangent(ott="step")
            
                #Set key at frame -40 in resting cloth pose
                cm.currentTime(-25)
                cm.setAttr(channel, (0 if "scale" not in attr else 1))
                cm.setKeyframe(channel)
            
    #Set Arms
    if cm.getAttr("jampa_rig_main_arm_l_extras_cc_01.FK_IK_Switch") == 0:
        leftFK()
    else:
        leftIK()
    if cm.getAttr("jampa_rig_main_arm_r_extras_cc_01.FK_IK_Switch") == 0:
        rightFK()
    else:
        rightIK()

    #Handle cases where controls do not have regular transformation channels
    cm.currentTime(-10)
    cm.setAttr("jampa_rig_main_foot_l_cc_01.Forward_Back", cm.getAttr("jampa_rig_main_foot_l_cc_01.Forward_Back", time=0))
    cm.setKeyframe("jampa_rig_main_foot_l_cc_01.Forward_Back")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_foot_r_cc_01.Forward_Back", cm.getAttr("jampa_rig_main_foot_r_cc_01.Forward_Back", time=0))
    cm.setKeyframe("jampa_rig_main_foot_r_cc_01.Forward_Back")
    cm.keyTangent(ott="step")

    cm.currentTime(-25)
    cm.setAttr("jampa_rig_main_foot_l_cc_01.Forward_Back", 0)
    cm.setKeyframe("jampa_rig_main_foot_l_cc_01.Forward_Back")
    cm.setAttr("jampa_rig_main_foot_r_cc_01.Forward_Back", 0)
    cm.setKeyframe("jampa_rig_main_foot_r_cc_01.Forward_Back")

def leftFK():
    cm.currentTime(-10)
    cm.setAttr("jampa_rig_main_upper_arm_l_FK_cc_01.rotateX", cm.getAttr("jampa_rig_main_upper_arm_l_FK_cc_01.rotateX", time=0))
    cm.setKeyframe("jampa_rig_main_upper_arm_l_FK_cc_01.rotateX")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_upper_arm_l_FK_cc_01.rotateY", cm.getAttr("jampa_rig_main_upper_arm_l_FK_cc_01.rotateY", time=0))
    cm.setKeyframe("jampa_rig_main_upper_arm_l_FK_cc_01.rotateY")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_upper_arm_l_FK_cc_01.rotateZ", cm.getAttr("jampa_rig_main_upper_arm_l_FK_cc_01.rotateZ", time=0))
    cm.setKeyframe("jampa_rig_main_upper_arm_l_FK_cc_01.rotateZ")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_forearm_l_FK_cc_01.rotateX", cm.getAttr("jampa_rig_main_forearm_l_FK_cc_01.rotateX", time=0))
    cm.setKeyframe("jampa_rig_main_forearm_l_FK_cc_01.rotateX")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_forearm_l_FK_cc_01.rotateY", cm.getAttr("jampa_rig_main_forearm_l_FK_cc_01.rotateY", time=0))
    cm.setKeyframe("jampa_rig_main_forearm_l_FK_cc_01.rotateY")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_forearm_l_FK_cc_01.rotateZ", cm.getAttr("jampa_rig_main_forearm_l_FK_cc_01.rotateZ", time=0))
    cm.setKeyframe("jampa_rig_main_forearm_l_FK_cc_01.rotateZ")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_wrist_l_FK_cc_01.rotateX", cm.getAttr("jampa_rig_main_wrist_l_FK_cc_01.rotateX", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_l_FK_cc_01.rotateX")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_wrist_l_FK_cc_01.rotateY", cm.getAttr("jampa_rig_main_wrist_l_FK_cc_01.rotateY", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_l_FK_cc_01.rotateY")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_wrist_l_FK_cc_01.rotateZ", cm.getAttr("jampa_rig_main_wrist_l_FK_cc_01.rotateZ", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_l_FK_cc_01.rotateZ")
    cm.keyTangent(ott="step")

    cm.currentTime(-25)
    cm.setAttr("jampa_rig_main_upper_arm_l_FK_cc_01.rotateX", 82.324)
    cm.setKeyframe("jampa_rig_main_upper_arm_l_FK_cc_01.rotateX")
    cm.setAttr("jampa_rig_main_upper_arm_l_FK_cc_01.rotateY", -34.129)
    cm.setKeyframe("jampa_rig_main_upper_arm_l_FK_cc_01.rotateY")
    cm.setAttr("jampa_rig_main_upper_arm_l_FK_cc_01.rotateZ", -80.925)
    cm.setKeyframe("jampa_rig_main_upper_arm_l_FK_cc_01.rotateZ")
    cm.setAttr("jampa_rig_main_forearm_l_FK_cc_01.rotateX", 0)
    cm.setKeyframe("jampa_rig_main_forearm_l_FK_cc_01.rotateX")
    cm.setAttr("jampa_rig_main_forearm_l_FK_cc_01.rotateY", 0)
    cm.setKeyframe("jampa_rig_main_forearm_l_FK_cc_01.rotateY")
    cm.setAttr("jampa_rig_main_forearm_l_FK_cc_01.rotateZ", -93.43)
    cm.setKeyframe("jampa_rig_main_forearm_l_FK_cc_01.rotateZ")
    cm.setAttr("jampa_rig_main_wrist_l_FK_cc_01.rotateX", 0)
    cm.setKeyframe("jampa_rig_main_wrist_l_FK_cc_01.rotateX")
    cm.setAttr("jampa_rig_main_wrist_l_FK_cc_01.rotateY", 0)
    cm.setKeyframe("jampa_rig_main_wrist_l_FK_cc_01.rotateY")
    cm.setAttr("jampa_rig_main_wrist_l_FK_cc_01.rotateZ", -6.526)
    cm.setKeyframe("jampa_rig_main_wrist_l_FK_cc_01.rotateZ")

def leftIK():
    cm.currentTime(-10)
    cm.setAttr("jampa_rig_main_wrist_l_IK_cc_01.translateX", cm.getAttr("jampa_rig_main_wrist_l_IK_cc_01.translateX", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_l_IK_cc_01.translateX")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_wrist_l_IK_cc_01.translateY", cm.getAttr("jampa_rig_main_wrist_l_IK_cc_01.translateY", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_l_IK_cc_01.translateY")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_wrist_l_IK_cc_01.translateZ", cm.getAttr("jampa_rig_main_wrist_l_IK_cc_01.translateZ", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_l_IK_cc_01.translateZ")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_wrist_l_IK_cc_01.rotateX", cm.getAttr("jampa_rig_main_wrist_l_IK_cc_01.rotateX", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_l_IK_cc_01.rotateX")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_wrist_l_IK_cc_01.rotateY", cm.getAttr("jampa_rig_main_wrist_l_IK_cc_01.rotateY", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_l_IK_cc_01.rotateY")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_wrist_l_IK_cc_01.rotateZ", cm.getAttr("jampa_rig_main_wrist_l_IK_cc_01.rotateZ", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_l_IK_cc_01.rotateZ")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_elbow_l_pole_vector_cc_01.translateX", cm.getAttr("jampa_rig_main_elbow_l_pole_vector_cc_01.translateX", time=0))
    cm.setKeyframe("jampa_rig_main_elbow_l_pole_vector_cc_01.translateX")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_elbow_l_pole_vector_cc_01.translateY", cm.getAttr("jampa_rig_main_elbow_l_pole_vector_cc_01.translateY", time=0))
    cm.setKeyframe("jampa_rig_main_elbow_l_pole_vector_cc_01.translateY")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_elbow_l_pole_vector_cc_01.translateZ", cm.getAttr("jampa_rig_main_elbow_l_pole_vector_cc_01.translateZ", time=0))
    cm.setKeyframe("jampa_rig_main_elbow_l_pole_vector_cc_01.translateZ")
    cm.keyTangent(ott="step")

    cm.currentTime(-25)
    cm.setAttr("jampa_rig_main_wrist_l_IK_cc_01.translateX", -8.775)
    cm.setKeyframe("jampa_rig_main_wrist_l_IK_cc_01.translateX")
    cm.setAttr("jampa_rig_main_wrist_l_IK_cc_01.translateY", -2.526)
    cm.setKeyframe("jampa_rig_main_wrist_l_IK_cc_01.translateY")
    cm.setAttr("jampa_rig_main_wrist_l_IK_cc_01.translateZ", 2.053)
    cm.setKeyframe("jampa_rig_main_wrist_l_IK_cc_01.translateZ")
    cm.setAttr("jampa_rig_main_wrist_l_IK_cc_01.rotateX", -55.53)
    cm.setKeyframe("jampa_rig_main_wrist_l_IK_cc_01.rotateX")
    cm.setAttr("jampa_rig_main_wrist_l_IK_cc_01.rotateY", 179.55)
    cm.setKeyframe("jampa_rig_main_wrist_l_IK_cc_01.rotateY")
    cm.setAttr("jampa_rig_main_wrist_l_IK_cc_01.rotateZ", 0)
    cm.setKeyframe("jampa_rig_main_wrist_l_IK_cc_01.rotateZ")
    cm.setAttr("jampa_rig_main_elbow_l_pole_vector_cc_01.translateX", -3.362)
    cm.setKeyframe("jampa_rig_main_elbow_l_pole_vector_cc_01.translateX")
    cm.setAttr("jampa_rig_main_elbow_l_pole_vector_cc_01.translateY", 0)
    cm.setKeyframe("jampa_rig_main_elbow_l_pole_vector_cc_01.translateY")
    cm.setAttr("jampa_rig_main_elbow_l_pole_vector_cc_01.translateZ", 6.486)
    cm.setKeyframe("jampa_rig_main_elbow_l_pole_vector_cc_01.translateZ")

def rightFK():
    cm.currentTime(-10)
    cm.setAttr("jampa_rig_main_upper_arm_r_FK_cc_01.rotateX", cm.getAttr("jampa_rig_main_upper_arm_r_FK_cc_01.rotateX", time=0))
    cm.setKeyframe("jampa_rig_main_upper_arm_r_FK_cc_01.rotateX")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_upper_arm_r_FK_cc_01.rotateY", cm.getAttr("jampa_rig_main_upper_arm_r_FK_cc_01.rotateY", time=0))
    cm.setKeyframe("jampa_rig_main_upper_arm_r_FK_cc_01.rotateY")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_upper_arm_r_FK_cc_01.rotateZ", cm.getAttr("jampa_rig_main_upper_arm_r_FK_cc_01.rotateZ", time=0))
    cm.setKeyframe("jampa_rig_main_upper_arm_r_FK_cc_01.rotateZ")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_forearm_r_FK_cc_01.rotateX", cm.getAttr("jampa_rig_main_forearm_r_FK_cc_01.rotateX", time=0))
    cm.setKeyframe("jampa_rig_main_forearm_r_FK_cc_01.rotateX")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_forearm_r_FK_cc_01.rotateY", cm.getAttr("jampa_rig_main_forearm_r_FK_cc_01.rotateY", time=0))
    cm.setKeyframe("jampa_rig_main_forearm_r_FK_cc_01.rotateY")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_forearm_r_FK_cc_01.rotateZ", cm.getAttr("jampa_rig_main_forearm_r_FK_cc_01.rotateZ", time=0))
    cm.setKeyframe("jampa_rig_main_forearm_r_FK_cc_01.rotateZ")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_wrist_r_FK_cc_01.rotateX", cm.getAttr("jampa_rig_main_wrist_r_FK_cc_01.rotateX", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_r_FK_cc_01.rotateX")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_wrist_r_FK_cc_01.rotateY", cm.getAttr("jampa_rig_main_wrist_r_FK_cc_01.rotateY", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_r_FK_cc_01.rotateY")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_wrist_r_FK_cc_01.rotateZ", cm.getAttr("jampa_rig_main_wrist_r_FK_cc_01.rotateZ", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_r_FK_cc_01.rotateZ")
    cm.keyTangent(ott="step")

    cm.currentTime(-25)
    cm.setAttr("jampa_rig_main_upper_arm_r_FK_cc_01.rotateX", 0)
    cm.setKeyframe("jampa_rig_main_upper_arm_r_FK_cc_01.rotateX")
    cm.setAttr("jampa_rig_main_upper_arm_r_FK_cc_01.rotateY", 0)
    cm.setKeyframe("jampa_rig_main_upper_arm_r_FK_cc_01.rotateY")
    cm.setAttr("jampa_rig_main_upper_arm_r_FK_cc_01.rotateZ", -45)
    cm.setKeyframe("jampa_rig_main_upper_arm_r_FK_cc_01.rotateZ")
    cm.setAttr("jampa_rig_main_forearm_r_FK_cc_01.rotateX", 0)
    cm.setKeyframe("jampa_rig_main_forearm_r_FK_cc_01.rotateX")
    cm.setAttr("jampa_rig_main_forearm_r_FK_cc_01.rotateY", 0)
    cm.setKeyframe("jampa_rig_main_forearm_r_FK_cc_01.rotateY")
    cm.setAttr("jampa_rig_main_forearm_r_FK_cc_01.rotateZ", 0)
    cm.setKeyframe("jampa_rig_main_forearm_r_FK_cc_01.rotateZ")
    cm.setAttr("jampa_rig_main_wrist_r_FK_cc_01.rotateX", 0)
    cm.setKeyframe("jampa_rig_main_wrist_r_FK_cc_01.rotateX")
    cm.setAttr("jampa_rig_main_wrist_r_FK_cc_01.rotateY", 0)
    cm.setKeyframe("jampa_rig_main_wrist_r_FK_cc_01.rotateY")
    cm.setAttr("jampa_rig_main_wrist_r_FK_cc_01.rotateZ", 0)
    cm.setKeyframe("jampa_rig_main_wrist_r_FK_cc_01.rotateZ")

def rightIK():
    cm.currentTime(-10)
    cm.setAttr("jampa_rig_main_wrist_r_IK_cc_01.translateX", cm.getAttr("jampa_rig_main_wrist_r_IK_cc_01.translateX", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_r_IK_cc_01.translateX")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_wrist_r_IK_cc_01.translateY", cm.getAttr("jampa_rig_main_wrist_r_IK_cc_01.translateY", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_r_IK_cc_01.translateY")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_wrist_r_IK_cc_01.translateZ", cm.getAttr("jampa_rig_main_wrist_r_IK_cc_01.translateZ", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_r_IK_cc_01.translateZ")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_wrist_r_IK_cc_01.rotateX", cm.getAttr("jampa_rig_main_wrist_r_IK_cc_01.rotateX", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_r_IK_cc_01.rotateX")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_wrist_r_IK_cc_01.rotateY", cm.getAttr("jampa_rig_main_wrist_r_IK_cc_01.rotateY", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_r_IK_cc_01.rotateY")
    cm.keyTangent(ott="step")
    cm.setAttr("jampa_rig_main_wrist_r_IK_cc_01.rotateZ", cm.getAttr("jampa_rig_main_wrist_r_IK_cc_01.rotateZ", time=0))
    cm.setKeyframe("jampa_rig_main_wrist_r_IK_cc_01.rotateZ")
    cm.keyTangent(ott="step")

    cm.currentTime(-25)
    cm.setAttr("jampa_rig_main_wrist_r_IK_cc_01.translateX", 2.047)
    cm.setKeyframe("jampa_rig_main_wrist_r_IK_cc_01.translateX")
    cm.setAttr("jampa_rig_main_wrist_r_IK_cc_01.translateY", -4.417)
    cm.setKeyframe("jampa_rig_main_wrist_r_IK_cc_01.translateY")
    cm.setAttr("jampa_rig_main_wrist_r_IK_cc_01.translateZ", 0.017)
    cm.setKeyframe("jampa_rig_main_wrist_r_IK_cc_01.translateZ")
    cm.setAttr("jampa_rig_main_wrist_r_IK_cc_01.rotateX", 0)
    cm.setKeyframe("jampa_rig_main_wrist_r_IK_cc_01.rotateX")
    cm.setAttr("jampa_rig_main_wrist_r_IK_cc_01.rotateY", 0)
    cm.setKeyframe("jampa_rig_main_wrist_r_IK_cc_01.rotateY")
    cm.setAttr("jampa_rig_main_wrist_r_IK_cc_01.rotateZ", 47.345)
    cm.setKeyframe("jampa_rig_main_wrist_r_IK_cc_01.rotateZ")
    
