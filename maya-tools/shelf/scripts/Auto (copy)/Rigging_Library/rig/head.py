"""
head @ rig 
"""

import maya.cmds as mc
import maya.OpenMaya as om
import math as math
import pymel.core as pm

from ..base import module
from ..base import control
from ..base import pose_space_reader

from ..utilities import joint
from ..utilities import naming
from ..utilities import transform

from Third_Party_Tools import SoftCluster



def build(
          name,
          rig_scale = 1.0,
          base_rig = None 
          ):
    
    """
    @param name: str, base name of rig
    @param rig_scale: float, scale of new controls
    @param base_rig: instance of base.module.Base class
    @return: dictionary with rig module objects
    """
    
    print("building head...")
    
    """ 
    create settings control and add custom attributes
    """
    
    head_settings_control = control.Control(
                                  prefix = name + '_head_settings',
                                  scale = .01,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + '_head_target_cc_01',
                                  rotate_to = name + '_head_target_cc_01',
                                  parent = '',
                                  shape = 'gear',
                                  locked_channels = ['visibility']
                                  )
    
    
    # add custom FK attributes to control
    mc.addAttr( head_settings_control.C, shortName='secondaries_visibility_parameter', longName='Secondaries_Visibility', attributeType='enum', enumName='Off:On:', keyable=True)    
    mc.addAttr( head_settings_control.C, shortName='eye_controls', longName='Eye_Controls', attributeType='enum', enumName='----------', keyable=True)
    mc.setAttr(name + "_head_settings_cc_01.eye_controls", keyable=False, channelBox=True)
    mc.addAttr( head_settings_control.C, shortName='follow_parameter', longName='Follow', attributeType='enum', enumName='None:Head:COG:', keyable=True)
    mc.addAttr( head_settings_control.C, shortName='eyelid_tracking_parameter', longName='Eyelid_Tracking', attributeType='float', defaultValue=0.5, minValue=0.0, maxValue=1.0, keyable=True)

    # make two offset groups
    transform.make_offset_group(name + '_head_settings_cc_01', name + '_head_settings_constrain')
    transform.make_offset_group(name + '_head_settings_cc_01', name + '_head_settings_curve_offset')
  
    # position settings control
    mc.move(-.14,0.0,0.0, name + '_head_settings_curve_offset_os_grp_01', relative=True)
    mc.rotate(90.0,0.0,0.0, name + '_head_settings_curve_offset_os_grp_01', relative=True)
    mc.scale(4.0,4.0,4.0, name + '_head_settings_curve_offset_os_grp_01', relative=True)

    # parent control offset group and freeze transforms
    mc.parent(name + '_head_settings_cc_os_grp_01', name + '_secondary_global_cc_01')
    mc.makeIdentity (apply=True, translate=True, rotate=True, scale=False)
    
    # align settings control and groups
    mc.rotate(0.0,-90.0,0.0, name + '_head_settings_cc_os_grp_01', relative=True)
    
    # lock and hide all rotate, scale, and visibility
    mc.setAttr( name + "_head_settings_cc_01.rotateX", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_head_settings_cc_01.rotateY", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_head_settings_cc_01.rotateZ", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_head_settings_cc_01.scaleX", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_head_settings_cc_01.scaleY", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_head_settings_cc_01.scaleZ", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_head_settings_cc_01.visibility", lock=True, keyable=False, channelBox=False)



    """
    head
    """
    
    # create head extras GRP
    mc.group(name=name + '_head_extras_GRP_01', empty=True, world=True)
    mc.parentConstraint(name + '_head_BN_01', name + '_head_extras_GRP_01', maintainOffset=False)
    mc.parent(name + '_head_extras_GRP_01', name + '_extras_GRP_01')

    
    
    """
    jaw
    """
    
    # create jaw joint
    mc.select(clear=True)
    mc.joint(name=name + "_jaw_BN_01", position = mc.xform(name + '_jaw_target_cc_01', query=True, translation=True, worldSpace=True), absolute=True, radius=.01)
    mc.setAttr(name + "_jaw_BN_01.rotateY", -90.0)
    
    jaw_offset=transform.make_offset_group(name + "_jaw_BN_01")
    mc.parent(jaw_offset, name + '_head_BN_01')
    
    # create jaw control
    jaw_control = control.Control(
                                prefix = name + '_jaw',
                                scale = .04,
                                use_numerical_transforms = False,
                                transform_x = 0.0,
                                transform_y = 0.0,
                                transform_z = 0.0,
                                translate_to = name + '_jaw_BN_01',
                                rotate_to = name + '_jaw_BN_01',
                                parent = name + '_head_cc_01',
                                shape = 'circle',
                                locked_channels = ['visibility']
                                )
    #position control shape
    jaw_control_shapes = mc.listRelatives( jaw_control.C, shapes=True, type = 'nurbsCurve' )
    cluster = mc.cluster( jaw_control_shapes )[1]
    mc.setAttr(cluster + '.scaleY', 0.7)
    mc.setAttr(cluster + '.translateZ', .22)
    mc.setAttr(cluster + '.translateY', -.17)
    mc.delete( jaw_control_shapes, constructionHistory=True)      
    
    # connect control to joint
    mc.connectAttr(jaw_control.C + '.translate', name + "_jaw_BN_01.translate", force=True)
    mc.connectAttr(jaw_control.C + '.rotate', name + "_jaw_BN_01.rotate", force=True)
    mc.connectAttr(jaw_control.C + '.scale', name + "_jaw_BN_01.scale", force=True)


    """
    mouth
    """
    # create UPP teeth joint and offsets
    mc.select(name + "_head_BN_01")
    mc.joint(name=name + "_UPP_teeth_BN_01", position = (0.0,0.0,0.0), absolute=True, radius=.01)
    mc.delete(mc.pointConstraint(name + "_UPP_teeth_target_cc_01", name + "_UPP_teeth_BN_01", maintainOffset=False))
    UPP_teeth_offset=transform.make_offset_group(name + "_UPP_teeth_BN_01")

    # create LOW teeth joint and offsets
    mc.select(name + "_jaw_BN_01")
    mc.joint(name=name + "_LOW_teeth_BN_01", position = (0.0,0.0,0.0), absolute=True, radius=.01)
    mc.delete(mc.pointConstraint(name + "_LOW_teeth_target_cc_01", name + "_LOW_teeth_BN_01", maintainOffset=False))
    LOW_teeth_offset=transform.make_offset_group(name + "_LOW_teeth_BN_01")

    # create root tongue joint
    mc.select(name + "_jaw_BN_01")
    mc.joint(name=name + "_tongue_root_BN_01", position = (0.0,0.0,0.0), absolute=True, radius=.01)
    mc.delete(mc.pointConstraint(name + "_tongue_root_target_cc_01", name + "_tongue_root_BN_01", maintainOffset=False))

    # create middle tongue joint
    mc.select(name + "_tongue_root_BN_01")
    mc.joint(name=name + "_tongue_middle_BN_01", position = (0.0,0.0,0.0), absolute=True, radius=.01)
    mc.delete(mc.pointConstraint(name + "_tongue_middle_target_cc_01", name + "_tongue_middle_BN_01", maintainOffset=False))

    # create tip tongue joint
    mc.select(name + "_tongue_middle_BN_01")
    mc.joint(name=name + "_tongue_tip_BN_01", position = (0.0,0.0,0.0), absolute=True, radius=.01)
    mc.delete(mc.pointConstraint(name + "_tongue_tip_target_cc_01", name + "_tongue_tip_BN_01", maintainOffset=False))

    # orient tongue joints and set tip orients to zero
    mc.joint( name + '_tongue_root_BN_01', edit=True, zeroScaleOrient=True, orientJoint='xyz', children=True, secondaryAxisOrient = 'yup' )
    mc.setAttr(name + "_tongue_tip_BN_01.rotateX", 0.0)
    mc.setAttr(name + "_tongue_tip_BN_01.rotateY", 0.0)
    mc.setAttr(name + "_tongue_tip_BN_01.rotateZ", 0.0)
    
    # make offset groups for joints
    tongue_root_offset=transform.make_offset_group(name + "_tongue_root_BN_01")
    tongue_middle_offset=transform.make_offset_group(name + "_tongue_middle_BN_01")
    tongue_tip_offset=transform.make_offset_group(name + "_tongue_tip_BN_01")

    
    
    
    # create UPP_teeth control
    UPP_teeth_control = control.Control(
                                prefix = name + '_UPP_teeth',
                                scale = .07,
                                use_numerical_transforms = False,
                                transform_x = 0.0,
                                transform_y = 0.0,
                                transform_z = 0.0,
                                translate_to = name + '_UPP_teeth_BN_01',
                                rotate_to = name + '_UPP_teeth_BN_01',
                                parent = name + '_head_cc_01',
                                shape = 'circle_y',
                                locked_channels = ['visibility']
                                )
    #position control shape
    UPP_teeth_control_shapes = mc.listRelatives( UPP_teeth_control.C, shapes=True, type = 'nurbsCurve' )
    cluster = mc.cluster( UPP_teeth_control_shapes )[1]
    mc.setAttr(cluster + '.scaleX', 0.7)
    mc.delete( UPP_teeth_control_shapes, constructionHistory=True)      
    
    # connect control to joint
    mc.connectAttr(UPP_teeth_control.C + '.translate', name + "_UPP_teeth_BN_01.translate", force=True)
    mc.connectAttr(UPP_teeth_control.C + '.rotate', name + "_UPP_teeth_BN_01.rotate", force=True)
    mc.connectAttr(UPP_teeth_control.C + '.scale', name + "_UPP_teeth_BN_01.scale", force=True)

    # create LOW_teeth control
    LOW_teeth_control = control.Control(
                                prefix = name + '_LOW_teeth',
                                scale = .07,
                                use_numerical_transforms = False,
                                transform_x = 0.0,
                                transform_y = 0.0,
                                transform_z = 0.0,
                                translate_to = name + '_LOW_teeth_BN_01',
                                rotate_to = name + '_LOW_teeth_BN_01',
                                parent = jaw_control.C,
                                shape = 'circle_y',
                                locked_channels = ['visibility']
                                )  
    #position control shape
    LOW_teeth_control_shapes = mc.listRelatives( LOW_teeth_control.C, shapes=True, type = 'nurbsCurve' )
    cluster = mc.cluster( LOW_teeth_control_shapes )[1]
    mc.setAttr(cluster + '.scaleX', 0.7)
    mc.delete( LOW_teeth_control_shapes, constructionHistory=True)      
    
    # connect control to joint
    mc.connectAttr(LOW_teeth_control.C + '.translate', name + "_LOW_teeth_BN_01.translate", force=True)
    mc.connectAttr(LOW_teeth_control.C + '.rotate', name + "_LOW_teeth_BN_01.rotate", force=True)
    mc.connectAttr(LOW_teeth_control.C + '.scale', name + "_LOW_teeth_BN_01.scale", force=True)


    # create tongue_root control
    tongue_root_control = control.Control(
                                prefix = name + '_tongue_root',
                                scale = .04,
                                use_numerical_transforms = False,
                                transform_x = 0.0,
                                transform_y = 0.0,
                                transform_z = 0.0,
                                translate_to = name + '_tongue_root_BN_01',
                                rotate_to = name + '_tongue_root_BN_01',
                                parent = jaw_control.C,
                                shape = 'circle',
                                locked_channels = ['visibility']
                                )  

    # create tongue_middle control
    tongue_middle_control = control.Control(
                                prefix = name + '_tongue_middle',
                                scale = .03,
                                use_numerical_transforms = False,
                                transform_x = 0.0,
                                transform_y = 0.0,
                                transform_z = 0.0,
                                translate_to = name + '_tongue_middle_BN_01',
                                rotate_to = name + '_tongue_middle_BN_01',
                                parent = tongue_root_control.C,
                                shape = 'circle',
                                locked_channels = ['visibility']
                                )      
    
    # create tongue_tip control
    tongue_tip_control = control.Control(
                                prefix = name + '_tongue_tip',
                                scale = .02,
                                use_numerical_transforms = False,
                                transform_x = 0.0,
                                transform_y = 0.0,
                                transform_z = 0.0,
                                translate_to = name + '_tongue_tip_BN_01',
                                rotate_to = name + '_tongue_tip_BN_01',
                                parent = tongue_middle_control.C,
                                shape = 'circle',
                                locked_channels = ['visibility']
                                )      
    
    # connect tongue controls to joints
    mc.connectAttr(tongue_root_control.C + '.translate', name + "_tongue_root_BN_01.translate", force=True)
    mc.connectAttr(tongue_root_control.C + '.rotate', name + "_tongue_root_BN_01.rotate", force=True)
    mc.connectAttr(tongue_root_control.C + '.scale', name + "_tongue_root_BN_01.scale", force=True)
    mc.connectAttr(tongue_middle_control.C + '.translate', name + "_tongue_middle_BN_01.translate", force=True)
    mc.connectAttr(tongue_middle_control.C + '.rotate', name + "_tongue_middle_BN_01.rotate", force=True)
    mc.connectAttr(tongue_middle_control.C + '.scale', name + "_tongue_middle_BN_01.scale", force=True)    
    mc.connectAttr(tongue_tip_control.C + '.translate', name + "_tongue_tip_BN_01.translate", force=True)
    mc.connectAttr(tongue_tip_control.C + '.rotate', name + "_tongue_tip_BN_01.rotate", force=True)
    mc.connectAttr(tongue_tip_control.C + '.scale', name + "_tongue_tip_BN_01.scale", force=True)    
    
    
    
    """
    eyes
    """
    
    # create LFT eye joints
    mc.select(clear=True)
    mc.joint(name=name + "_LFT_eye_BN_01", position = mc.xform(name + '_LFT_eye_target_cc_01', query=True, translation=True, worldSpace=True), absolute=True, radius=.01)
    mc.joint(name=name + "_LFT_eye_JNT_END_01", position = (.03,0.0,0.0), relative=True, radius=.01)
    mc.setAttr(name + "_LFT_eye_BN_01.jointOrientY", -90.0)
    
    mc.parent(name + "_LFT_eye_BN_01", name + '_head_BN_01')
    
    # create RGT eye joints
    mc.mirrorJoint(name + '_LFT_eye_BN_01', mirrorBehavior=False, mirrorYZ=True, searchReplace=("LFT","RGT"))
       
            
    both_eyes_aim_control = control.Control(
                                    prefix = name + '_both_eyes_aim',
                                    scale = .03,
                                    use_numerical_transforms = False,
                                    transform_x = 0.0,
                                    transform_y = 0.0,
                                    transform_z = 0.0,
                                    translate_to = name + '_head_BN_01',
                                    rotate_to = name + '_head_BN_01',
                                    parent = name + '_secondary_global_cc_01',
                                    shape = 'oval',
                                    locked_channels = ['visibility']
                                    )

    
    # set up eye base
    for side in ["_LFT_", "_RGT_"]:
        # create nodes
        #groups
        mc.select(clear=True)
        mc.group(name=name + side + 'eye_GRP_01', empty=True, world=True)
        mc.group(name=name + side + 'eye_aim_grp_01', empty=True, parent=name + side + 'eye_GRP_01')
        mc.group(name=name + side + 'eye_anim_grp_01', empty=True, parent=name + side + 'eye_GRP_01')
        mc.group(name=name + side + 'eye_out_grp_01', empty=True, parent=name + side + 'eye_GRP_01')
        mc.addAttr( name + side + 'eye_out_grp_01', shortName='aim_parameter', longName='Aim', attributeType='float', defaultValue=1.0, minValue=0.0, maxValue=1.0, keyable=True)
        mc.addAttr( name + side + 'eye_out_grp_01', shortName='anim_parameter', longName='Anim', attributeType='float', defaultValue=1.0, minValue=0.0, maxValue=1.0, keyable=True)
        #aim locator
        mc.spaceLocator(name=name + side + 'aim_target_loc_01')
        mc.parent(name + side + 'aim_target_loc_01', name + side + 'eye_GRP_01')
        #MD nodes
        mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + 'eye_aim_MD_01')
        mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + 'eye_anim_MD_01')
        #PMA node
        mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + 'eye_rotations_PMA_01')
        #controls
        eye_aim_control = control.Control(
                        prefix = name + side + 'eye_aim',
                        scale = .02,
                        use_numerical_transforms = False,
                        transform_x = 0.0,
                        transform_y = 0.0,
                        transform_z = 0.0,
                        translate_to = name + side + 'eye_BN_01',
                        rotate_to = name + side + 'eye_BN_01',
                        parent = name + '_head_cc_01',
                        shape = 'circle',
                        locked_channels = ['visibility']
                        )
        mc.move(0.0,0.0,.3, eye_aim_control.Off, relative=True, worldSpace=True)             
        eye_rotate_control = control.Control(
                        prefix = name + side + 'eye_rotate',
                        scale = .02,
                        use_numerical_transforms = False,
                        transform_x = 0.0,
                        transform_y = 0.0,
                        transform_z = 0.0,
                        translate_to = name + side + 'eye_BN_01',
                        rotate_to = name + side + 'eye_BN_01',
                        parent = name + '_head_cc_01',
                        shape = 'circle',
                        locked_channels = ['visibility']
                        )   
        eye_rotate_control_shapes = mc.listRelatives( eye_rotate_control.C, shapes=True, type = 'nurbsCurve' )
        cluster = mc.cluster( eye_rotate_control_shapes )[1]
        mc.setAttr(cluster + '.translateZ', .08)
        mc.delete( eye_rotate_control_shapes, constructionHistory=True)          
    
        # create constraints
        #aim constraint
        mc.pointConstraint(eye_aim_control.C, name + side + 'aim_target_loc_01', maintainOffset=False)
        mc.aimConstraint( name + side + 'aim_target_loc_01', name + side + 'eye_aim_grp_01', worldUpType="none")
        
        # establish connections
        mc.connectAttr(name + side + 'eye_rotate_cc_01.rotate', name + side + 'eye_anim_grp_01.rotate',  force=True)
        
        mc.connectAttr(name + side + 'eye_aim_grp_01.rotate', name + side + 'eye_aim_MD_01.input1',  force=True)
        mc.connectAttr(name + side + 'eye_out_grp_01.aim_parameter', name + side + 'eye_aim_MD_01.input2X',  force=True)
        mc.connectAttr(name + side + 'eye_out_grp_01.aim_parameter', name + side + 'eye_aim_MD_01.input2Y',  force=True)
        mc.connectAttr(name + side + 'eye_out_grp_01.aim_parameter', name + side + 'eye_aim_MD_01.input2Z',  force=True)
    
        mc.connectAttr(name + side + 'eye_anim_grp_01.rotate', name + side + 'eye_anim_MD_01.input1',  force=True)
        mc.connectAttr(name + side + 'eye_out_grp_01.anim_parameter', name + side + 'eye_anim_MD_01.input2X',  force=True)
        mc.connectAttr(name + side + 'eye_out_grp_01.anim_parameter', name + side + 'eye_anim_MD_01.input2Y',  force=True)
        mc.connectAttr(name + side + 'eye_out_grp_01.anim_parameter', name + side + 'eye_anim_MD_01.input2Z',  force=True)
        
        mc.connectAttr(name + side + 'eye_aim_MD_01.output', name + side + 'eye_rotations_PMA_01.input3D[0]', force=True)
        mc.connectAttr(name + side + 'eye_anim_MD_01.output', name + side + 'eye_rotations_PMA_01.input3D[1]', force=True)
    
        mc.connectAttr(name + side + 'eye_rotations_PMA_01.output3D', name + side + 'eye_out_grp_01.rotate', force=True)
        
        mc.connectAttr(name + side + 'eye_out_grp_01.rotate', name + side + 'eye_BN_01.rotate', force=True)
        
        #move assembly to appropriate location
        #orient group properly
        mc.rotate(0.0,-90.0,0.0, name + side + 'eye_GRP_01')
        #moving and parenting
        mc.delete(mc.pointConstraint(name + side + 'eye_BN_01', name + side + 'eye_GRP_01'))
        mc.parent(name + side + 'eye_GRP_01', name + '_head_extras_GRP_01')
        
    #move and parent both eyes control
    mc.delete(mc.parentConstraint(eye_aim_control.C, both_eyes_aim_control.Off, maintainOffset=False))
    mc.setAttr(both_eyes_aim_control.Off + '.translateX', 0.0)
    mc.parent(name + '_LFT_eye_aim_cc_os_grp_01', name + '_RGT_eye_aim_cc_os_grp_01', both_eyes_aim_control.C)  
    
    
    """
    eyelids
    """
    # create eyelid joints
    mc.duplicate(name + "_LFT_eye_BN_01", renameChildren=True)
    mc.rename(name + "_LFT_eye_BN_02", name + "_LFT_UPP_eyelid_BN_01")
    mc.rename(name + "_LFT_eye_JNT_END_02", name + "_LFT_UPP_eyelid_JNT_END_01")
    mc.duplicate(name + "_LFT_eye_BN_01", renameChildren=True)
    mc.rename(name + "_LFT_eye_BN_02", name + "_LFT_LOW_eyelid_BN_01")
    mc.rename(name + "_LFT_eye_JNT_END_02", name + "_LFT_LOW_eyelid_JNT_END_01")    
    
    mc.duplicate(name + "_RGT_eye_BN_01", renameChildren=True)
    mc.rename(name + "_RGT_eye_BN_02", name + "_RGT_UPP_eyelid_BN_01")
    mc.rename(name + "_RGT_eye_JNT_END_02", name + "_RGT_UPP_eyelid_JNT_END_01")
    mc.duplicate(name + "_RGT_eye_BN_01", renameChildren=True)
    mc.rename(name + "_RGT_eye_BN_02", name + "_RGT_LOW_eyelid_BN_01")
    mc.rename(name + "_RGT_eye_JNT_END_02", name + "_RGT_LOW_eyelid_JNT_END_01")
    
    #shift lower eyelid bone down slightly and upper eyelid up slightly to avoid skinning problems
    mc.move(0.0, 0.001*rig_scale, 0.0, name + "_RGT_UPP_eyelid_BN_01", relative=True, worldSpace=True)
    mc.move(0.0, -0.001*rig_scale, 0.0, name + "_RGT_LOW_eyelid_BN_01", relative=True, worldSpace=True)
    mc.move(0.0, 0.001*rig_scale, 0.0, name + "_LFT_UPP_eyelid_BN_01", relative=True, worldSpace=True)
    mc.move(0.0, -0.001*rig_scale, 0.0, name + "_LFT_LOW_eyelid_BN_01", relative=True, worldSpace=True)
    
    # begin node network setup for soft follow eyelids
    # props to Jason Osipa and his Stop Staring book for the basic functionality of the following setup:
    for side in ["_LFT", "_RGT"]:
    
        # add attributes for upper and lower eyelid animation to eye out group
        mc.addAttr( name + side + '_eye_out_grp_01', shortName='UPP_eyelid_parameter', longName='UPP_Eyelid', attributeType='float', defaultValue=0.0, minValue=-10.0, maxValue=10.0, keyable=True)
        mc.addAttr( name + side + '_eye_out_grp_01', shortName='LOW_eyelid_parameter', longName='LOW_Eyelid', attributeType='float', defaultValue=0.0, minValue=-10.0, maxValue=10.0, keyable=True)
    
    
        #create nulls
        mc.group(name=name + side + '_eyelid_rig_grp_01', empty=True)
        mc.group(name=name + side + '_eyelid_LOW_tracker_grp_01', empty=True)
        mc.group(name=name + side + '_eyelid_LOW_eyelid_grp_01', empty=True)
        mc.group(name=name + side + '_eyelid_UPP_eyelid_grp_01', empty=True)
        mc.group(name=name + side + '_eyelid_UPP_tracker_grp_01', empty=True)
        mc.group(name=name + side + '_eyelid_UPP_eyelid_reference_grp_01', empty=True)


        #parent nulls
        mc.parent(name + side + '_eyelid_UPP_eyelid_grp_01', name + side + '_eyelid_LOW_eyelid_grp_01')
        mc.parent(name + side + '_eyelid_LOW_eyelid_grp_01', name + side + '_eyelid_LOW_tracker_grp_01')
        mc.parent(name + side + '_eyelid_LOW_tracker_grp_01', name + side + '_eyelid_rig_grp_01')
        mc.parent(name + side + '_eyelid_UPP_eyelid_reference_grp_01', name + side + '_eyelid_UPP_tracker_grp_01')
        mc.parent(name + side + '_eyelid_UPP_tracker_grp_01', name + side + '_eyelid_rig_grp_01')
        
        
        #position to eye and parent eyelid rig to head extras
        mc.delete(mc.parentConstraint(name + side + '_eye_out_grp_01', name + side + '_eyelid_rig_grp_01', maintainOffset=False))
        mc.parent(name + side + '_eyelid_rig_grp_01', name + '_head_extras_GRP_01')
        
        
        #orient constrain upper lid to upper lid reference and lower lid
        mc.orientConstraint(name + side + '_eyelid_UPP_eyelid_reference_grp_01', name + side + '_eyelid_LOW_eyelid_grp_01', name + side + '_eyelid_UPP_eyelid_grp_01', maintainOffset=False)
        
        
        #create nodes
        mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_eyelid_tracking_MD_01')
        mc.setAttr( name + side + '_eyelid_tracking_MD_01.input2Y', 0.9)
        mc.setAttr( name + side + '_eyelid_tracking_MD_01.input2Z', 0.3)
    
        mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_UPP_eyelid_control_translate_MD_01')
        mc.setAttr( name + side + '_UPP_eyelid_control_translate_MD_01.input2X', -300.0)
    
        mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_LOW_eyelid_control_translate_MD_01')
        mc.setAttr( name + side + '_LOW_eyelid_control_translate_MD_01.input2X', 300.0)    
    
        mc.shadingNode('remapValue', asUtility=True, name= name + side + '_eyelid_diminish_tracking_with_distance_RMV_01')
        mc.setAttr( name + side + '_eyelid_diminish_tracking_with_distance_RMV_01.value[0].value_Interp', 2)
        mc.setAttr( name + side + '_eyelid_diminish_tracking_with_distance_RMV_01.inputMin', -30.0)
        mc.setAttr( name + side + '_eyelid_diminish_tracking_with_distance_RMV_01.inputMax', 0.0)
        mc.setAttr( name + side + '_eyelid_diminish_tracking_with_distance_RMV_01.value[0].value_FloatValue', 0.5)
        mc.setAttr( name + side + '_eyelid_diminish_tracking_with_distance_RMV_01.value[1].value_FloatValue', 0.9)
        
        mc.shadingNode('remapValue', asUtility=True, name= name + side + '_UPP_eyelid_reference_x_rotation_RMV_01')
        mc.setAttr( name + side + '_UPP_eyelid_reference_x_rotation_RMV_01.value[0].value_Interp', 1)
        mc.setAttr( name + side + '_UPP_eyelid_reference_x_rotation_RMV_01.value[0].value_FloatValue', 1.0)        
        mc.setAttr( name + side + '_UPP_eyelid_reference_x_rotation_RMV_01.value[1].value_FloatValue', 0.0)        
        
        mc.setAttr( name + side + '_UPP_eyelid_reference_x_rotation_RMV_01.inputMin', -10)
        mc.setAttr( name + side + '_UPP_eyelid_reference_x_rotation_RMV_01.inputMax', 10.0)        
        mc.setAttr( name + side + '_UPP_eyelid_reference_x_rotation_RMV_01.outputMin', -60.0)
        mc.setAttr( name + side + '_UPP_eyelid_reference_x_rotation_RMV_01.outputMax', 60.0)

        mc.shadingNode('remapValue', asUtility=True, name= name + side + '_LOW_eyelid_x_rotation_RMV_01')
        mc.setAttr( name + side + '_LOW_eyelid_x_rotation_RMV_01.value[0].value_Interp', 1)
        mc.setAttr( name + side + '_LOW_eyelid_x_rotation_RMV_01.inputMin', -10)
        mc.setAttr( name + side + '_LOW_eyelid_x_rotation_RMV_01.inputMax', 10.0)        
        mc.setAttr( name + side + '_LOW_eyelid_x_rotation_RMV_01.outputMin', -60.0)
        mc.setAttr( name + side + '_LOW_eyelid_x_rotation_RMV_01.outputMax', 60.0)
     
        mc.shadingNode('remapValue', asUtility=True, name= name + side + '_UPP_eyelid_orient_constraint_upper_eyelid_reference_weight_RMV_01')
        mc.setAttr( name + side + '_UPP_eyelid_orient_constraint_upper_eyelid_reference_weight_RMV_01.value[0].value_Interp', 2)
        mc.setAttr( name + side + '_UPP_eyelid_orient_constraint_upper_eyelid_reference_weight_RMV_01.inputMin', 7.0)
        mc.setAttr( name + side + '_UPP_eyelid_orient_constraint_upper_eyelid_reference_weight_RMV_01.inputMax', 10.0)        
        mc.setAttr( name + side + '_UPP_eyelid_orient_constraint_upper_eyelid_reference_weight_RMV_01.value[0].value_FloatValue', 1.0)
        mc.setAttr( name + side + '_UPP_eyelid_orient_constraint_upper_eyelid_reference_weight_RMV_01.value[1].value_FloatValue', 0.0)        
        
        mc.shadingNode('remapValue', asUtility=True, name= name + side + '_UPP_eyelid_orient_constraint_lower_eyelid_weight_RMV_01')
        mc.setAttr( name + side + '_UPP_eyelid_orient_constraint_lower_eyelid_weight_RMV_01.value[0].value_Interp', 2)
        mc.setAttr( name + side + '_UPP_eyelid_orient_constraint_lower_eyelid_weight_RMV_01.inputMin', 7.0)
        mc.setAttr( name + side + '_UPP_eyelid_orient_constraint_lower_eyelid_weight_RMV_01.inputMax', 10.0)        
        mc.setAttr( name + side + '_UPP_eyelid_orient_constraint_lower_eyelid_weight_RMV_01.value[0].value_FloatValue', 0.0)
        mc.setAttr( name + side + '_UPP_eyelid_orient_constraint_lower_eyelid_weight_RMV_01.value[1].value_FloatValue', 1.0)         
        
        #connect eyelid joints to eyelid rig
        mc.orientConstraint(name + side + '_eyelid_UPP_eyelid_grp_01', name + side + '_UPP_eyelid_BN_01', maintainOffset=False)
        mc.orientConstraint(name + side + '_eyelid_LOW_eyelid_grp_01', name + side + '_LOW_eyelid_BN_01', maintainOffset=False)
        
        
        #Controls
        UPP_eyelid_control = control.Control(
                        prefix = name + side + '_UPP_eyelid',
                        scale = 0.005,
                        use_numerical_transforms = False,
                        transform_x = 0.0,
                        transform_y = 0.0,
                        transform_z = 0.0,
                        translate_to = name + side + '_eye_BN_01',
                        rotate_to = name + side + '_eye_BN_01',
                        parent = name + side + '_eye_rotate_cc_01',
                        shape = 'circle',
                        locked_channels = ['visibility']
                        )           
        UPP_eyelid_control_shapes = mc.listRelatives( UPP_eyelid_control.C, shapes=True, type = 'nurbsCurve' )
        cluster = mc.cluster( UPP_eyelid_control_shapes )[1]
        mc.setAttr(cluster + '.translateZ', .08)
        mc.setAttr(cluster + '.translateY', .01)
        mc.delete( UPP_eyelid_control_shapes, constructionHistory=True)    
                
        LOW_eyelid_control = control.Control(
                        prefix = name + side + '_LOW_eyelid',
                        scale = 0.005,
                        use_numerical_transforms = False,
                        transform_x = 0.0,
                        transform_y = 0.0,
                        transform_z = 0.0,
                        translate_to = name + side + '_eye_BN_01',
                        rotate_to = name + side + '_eye_BN_01',
                        parent = name + side + '_eye_rotate_cc_01',
                        shape = 'circle',
                        locked_channels = ['visibility']
                        )           
        LOW_eyelid_control_shapes = mc.listRelatives( LOW_eyelid_control.C, shapes=True, type = 'nurbsCurve' )
        cluster = mc.cluster( LOW_eyelid_control_shapes )[1]
        mc.setAttr(cluster + '.translateZ', .08)
        mc.setAttr(cluster + '.translateY', -.01)
        mc.delete( LOW_eyelid_control_shapes, constructionHistory=True)  
                
        
        #connections
        mc.connectAttr(name + side + '_eye_out_grp_01.rotateZ', name + side + '_eyelid_tracking_MD_01.input1X', force=True)
        mc.connectAttr(name + side + '_eye_out_grp_01.rotateZ', name + side + '_eyelid_tracking_MD_01.input1Y', force=True)
        mc.connectAttr(name + side + '_eye_out_grp_01.rotateY', name + side + '_eyelid_tracking_MD_01.input1Z', force=True)
        
        mc.connectAttr(name + side + '_eye_out_grp_01.rotateZ', name + side + '_eyelid_diminish_tracking_with_distance_RMV_01.inputValue', force=True)
        mc.connectAttr(name + side + '_eyelid_diminish_tracking_with_distance_RMV_01.outValue', name + side + '_eyelid_tracking_MD_01.input2X', force=True)
    
        mc.connectAttr(name + side + '_eyelid_tracking_MD_01.outputX', name + side + '_eyelid_LOW_tracker_grp_01.rotateZ', force=True)
        mc.connectAttr(name + side + '_eyelid_tracking_MD_01.outputZ', name + side + '_eyelid_LOW_tracker_grp_01.rotateY', force=True)
        mc.connectAttr(name + side + '_eyelid_tracking_MD_01.outputY', name + side + '_eyelid_UPP_tracker_grp_01.rotateZ', force=True)    
        mc.connectAttr(name + side + '_eyelid_tracking_MD_01.outputZ', name + side + '_eyelid_UPP_tracker_grp_01.rotateY', force=True)
    
        mc.connectAttr(name + side + '_UPP_eyelid_reference_x_rotation_RMV_01.outValue', name + side + '_eyelid_UPP_eyelid_reference_grp_01.rotateZ', force=True)
        mc.connectAttr(name + side + '_LOW_eyelid_x_rotation_RMV_01.outValue', name + side + '_eyelid_LOW_eyelid_grp_01.rotateZ', force=True)
    
        mc.connectAttr(name + side + '_eye_out_grp_01.UPP_eyelid_parameter', name + side + '_UPP_eyelid_reference_x_rotation_RMV_01.inputValue', force=True)
        mc.connectAttr(name + side + '_eye_out_grp_01.LOW_eyelid_parameter', name + side + '_LOW_eyelid_x_rotation_RMV_01.inputValue', force=True)

        mc.connectAttr(name + side + '_eye_out_grp_01.UPP_eyelid_parameter', name + side + '_UPP_eyelid_orient_constraint_upper_eyelid_reference_weight_RMV_01.inputValue', force=True)
        mc.connectAttr(name + side + '_UPP_eyelid_orient_constraint_upper_eyelid_reference_weight_RMV_01.outValue', name + side + '_eyelid_UPP_eyelid_grp_01_orientConstraint1.' + name + side + '_eyelid_UPP_eyelid_reference_grp_01W0', force=True)
    
        mc.connectAttr(name + side + '_eye_out_grp_01.UPP_eyelid_parameter', name + side + '_UPP_eyelid_orient_constraint_lower_eyelid_weight_RMV_01.inputValue', force=True)
        mc.connectAttr(name + side + '_UPP_eyelid_orient_constraint_lower_eyelid_weight_RMV_01.outValue', name + side + '_eyelid_UPP_eyelid_grp_01_orientConstraint1.' + name + side + '_eyelid_LOW_eyelid_grp_01W1', force=True)
        
        mc.connectAttr(name + side + '_UPP_eyelid_cc_01.translateY', name + side + '_UPP_eyelid_control_translate_MD_01.input1X', force=True)
        mc.connectAttr(name + side + '_UPP_eyelid_control_translate_MD_01.outputX', name + side + '_eye_out_grp_01.UPP_eyelid_parameter', force=True)
       
        mc.connectAttr(name + side + '_LOW_eyelid_cc_01.translateY', name + side + '_LOW_eyelid_control_translate_MD_01.input1X', force=True)
        mc.connectAttr(name + side + '_LOW_eyelid_control_translate_MD_01.outputX', name + side + '_eye_out_grp_01.LOW_eyelid_parameter', force=True)        
        
        #set rotate limit to upper lid to prevent crashing through lower lid
        mc.transformLimits(name + side + '_eyelid_UPP_eyelid_grp_01', rotationZ=(0,0), enableRotationZ=(True,False))
        


    """
    eyebrows
    """
    
    #turn off symmetry
    mc.symmetricModelling(symmetry=0)

    for side in ["_LFT", "_RGT"]:
        for part in ["INN", "MID", "OUT"]:
            # create INN MID and OUT clusters for eyebrows based on mesh proximity to targets
            # create closest point on mesh nodes
            mc.createNode("closestPointOnMesh", name=name + side + '_' + part + '_eyebrow_CPM_01')   
        
            #create decompose matrix nodes to find transforms of eyebrow targets
            mc.shadingNode('decomposeMatrix', asUtility=True, name= name + side + '_' + part + '_eyebrow_DM_01')
                
            #make connections
            mc.connectAttr(name + side + '_' + part + '_eyebrow_target_cc_01.worldMatrix', name + side + '_' + part + '_eyebrow_DM_01.inputMatrix', force=True)
            mc.connectAttr(name + side + '_' + part + '_eyebrow_DM_01.outputTranslate', name + side + '_' + part + '_eyebrow_CPM_01.inPosition', force=True)
            if mc.objExists(name + '_body_GEO_01Shape.outMesh'):
                mc.connectAttr(name + '_body_GEO_01Shape.outMesh', name + side + '_' + part + '_eyebrow_CPM_01.inMesh', force=True)
            if mc.objExists(name + '_body_GEO_0Shape1.outMesh'):
                mc.connectAttr(name + '_body_GEO_0Shape1.outMesh', name + side + '_' + part + '_eyebrow_CPM_01.inMesh', force=True)
    
            #store vertex index closest to target
            closest_vertex=mc.getAttr(name + side + '_' + part + '_eyebrow_CPM_01.closestVertexIndex')
            
            #expand selection by one increment and convert to soft selection
            mc.select( name + '_body_GEO_01.vtx[' + str(closest_vertex) + ']' )
            mc.polySelectConstraint( pp=1 )
            mc.softSelect(softSelectEnabled=True,softSelectDistance=0.05*rig_scale,softSelectFalloff=1)
    
            #call third party softcluster script to do some magic
            SoftCluster.createSoftCluster(name + side + '_' + part + '_eyebrow_CLU_01')
            #mc.select('blah')

            #create eyebrow controls
            control.Control(
                        prefix = name + side + '_' + part + '_eyebrow',
                        scale = 0.005,
                        use_numerical_transforms = False,
                        transform_x = 0.0,
                        transform_y = 0.0,
                        transform_z = 0.0,
                        translate_to = name + side + '_' + part + '_eyebrow_target_cc_01',
                        rotate_to = name + side + '_' + part + '_eyebrow_target_cc_01',
                        parent = name + '_head_cc_01',
                        shape = 'oval_z',
                        locked_channels = ['visibility']
                        )       
            
            mc.delete(mc.pointConstraint(name + side + '_' + part + '_eyebrow_target_cc_01', name + side + '_' + part + '_eyebrow_cc_os_grp_01', maintainOffset=False))
            

            #connect translate, scale, and rotate values from control to cluster
            mc.connectAttr(name + side + '_' + part + '_eyebrow_cc_01.translate', name + side + '_' + part +  '_eyebrow_CLU_01Handle.translate', force=True)
            mc.connectAttr(name + side + '_' + part + '_eyebrow_cc_01.rotate', name + side + '_' + part + '_eyebrow_CLU_01Handle.rotate', force=True)
            mc.connectAttr(name + side + '_' + part + '_eyebrow_cc_01.scale', name + side + '_' + part + '_eyebrow_CLU_01Handle.scale', force=True)


        #store inside vertex index closest to target
        closest_inside_vertex=mc.getAttr(name + side + '_INN_eyebrow_CPM_01.closestVertexIndex')
        
        #store outside vertex index closest to target
        closest_outside_vertex=mc.getAttr(name + side + '_OUT_eyebrow_CPM_01.closestVertexIndex')
                
        #select all verts between        
        pm.select(pm.polySelectSp( name + '_body_GEO_01.vtx[' + str(closest_inside_vertex) + ']', name + '_body_GEO_01.vtx[' + str(closest_outside_vertex) + ']', q=True, loop=True ))  
        #between_verts=mc.ls(selection=True)      
      
        #expand selection by one increment and convert to soft selection
        mc.polySelectConstraint( pp=1 )
        mc.softSelect(softSelectEnabled=True,softSelectDistance=0.05*rig_scale,softSelectFalloff=1)

        #call third party softcluster script to do some magic
        SoftCluster.createSoftCluster(name + side + '_MAIN_eyebrow_CLU_01')

        #create eyebrow controls
        control.Control(
                    prefix = name + side + '_MAIN_eyebrow',
                    scale = 0.015,
                    use_numerical_transforms = False,
                    transform_x = 0.0,
                    transform_y = 0.0,
                    transform_z = 0.0,
                    translate_to = name + side + '_MID_eyebrow_target_cc_01',
                    rotate_to = name + side + '_MID_eyebrow_target_cc_01',
                    parent = name + '_head_cc_01',
                    shape = 'oval_z',
                    locked_channels = ['visibility']
                    )       
        
        mc.delete(mc.pointConstraint(name + side + '_MID_eyebrow_target_cc_01', name + side + '_MAIN_eyebrow_cc_os_grp_01', maintainOffset=False))
        
        #connect translate, scale, and rotate values from control to cluster
        mc.connectAttr(name + side + '_MAIN_eyebrow_cc_01.translate', name + side + '_MAIN_eyebrow_CLU_01Handle.translate', force=True)
        mc.connectAttr(name + side + '_MAIN_eyebrow_cc_01.rotate', name + side + '_MAIN_eyebrow_CLU_01Handle.rotate', force=True)
        mc.connectAttr(name + side + '_MAIN_eyebrow_cc_01.scale', name + side + '_MAIN_eyebrow_CLU_01Handle.scale', force=True)

        #parent things
        mc.parent(name + side + '_INN_eyebrow_cc_os_grp_01',name + side + '_MID_eyebrow_cc_os_grp_01',name + side + '_OUT_eyebrow_cc_os_grp_01', name + side + '_MAIN_eyebrow_cc_01')
        
        mc.group(name=name + side + '_eyebrow_clusters_GRP_01', empty=True)
        mc.parent(name + side + '_INN_eyebrow_CLU_01Handle', name + side + '_MID_eyebrow_CLU_01Handle', name + side + '_OUT_eyebrow_CLU_01Handle', name + side + '_MAIN_eyebrow_CLU_01Handle', name + side + '_eyebrow_clusters_GRP_01')
        mc.parent(name + side + '_eyebrow_clusters_GRP_01', name + '_head_extras_GRP_01')









    
    #cleanup
    #parenting
    mc.group(name=name + '_head_controls_GRP_01', empty=True)
    mc.group(name=name + '_head_joints_GRP_01', empty=True)
    mc.parent(name + '_head_BN_01', name + '_head_joints_GRP_01')
    mc.parent(name + '_head_joints_GRP_01', name + '_skeleton_GRP_01')
    mc.parent(name + '_head_cc_os_grp_01', name + '_head_settings_cc_os_grp_01', name + '_head_controls_GRP_01')
    mc.parentConstraint(name + '_head_cc_01', name + '_head_settings_constrain_os_grp_01', maintainOffset=True)
    mc.parent(name + '_head_controls_GRP_01', name + '_secondary_global_cc_01')
    
    #visibility
    mc.setAttr( name + "_head_extras_GRP_01.visibility", 0)


    ######################connect to rest of rig##############################
    '''
    #controls
    mc.parent(name + '_head_controls_GRP_01', name + '_chest_cc_01')
    
    #joints
    mc.parent(name + '_head_joints_GRP_01', name + '_skeleton_GRP_01')
    '''



    print('done.')
    
    

        

    