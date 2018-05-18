"""
leg @ rig 
"""

import maya.cmds as mc
import maya.OpenMaya as om
import math as math

from ..base import module
from ..base import control
from ..base import pose_space_reader

from ..utilities import joint
from ..utilities import naming
from ..utilities import transform



def build(
          name,
          hip_joint,
          knee_joint,
          ankle_joint,
          side = '_LFT',
          prefix = 'LFT_leg',
          rig_scale = 1.0,
          base_rig = None
          ):
    
    """
    @param name: str, base name of rig
    @param hip_joint: str, hip target cc
    @param knee_joint: str, knee target cc
    @param ankle_joint: str, ankle target cc
    @param side: side of the character, LFT or RGT
    @param prefix: str, prefix to name new leg objects
    @param rig_scale: float, scale of new controls
    @param base_rig: instance of base.module.Base class
    @return: dictionary with rig module objects
    """
    
    print("building " + side + " leg...")


    """ 
    create settings control and add custom attributes
    """
    
    leg_settings_control = control.Control(
                                  prefix = name + side + '_leg_settings',
                                  scale = .03,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = ankle_joint,
                                  rotate_to = ankle_joint,
                                  parent = '',
                                  shape = 'gear',
                                  locked_channels = ['visibility']
                                  )
    
    
    # add custom FK attributes to control
    mc.addAttr( leg_settings_control.C, shortName='fk_ik_parameter', longName='FK_IK', attributeType='float', defaultValue=1.0, minValue=0.0, maxValue=1.0, keyable=True)
    mc.addAttr( leg_settings_control.C, shortName='bendy_control_visibility_parameter', longName='Bendy_Controls', attributeType='enum', enumName='Off:On:', keyable=True)    
    mc.addAttr( leg_settings_control.C, shortName='fk_leg_controls', longName='FK_Leg_Controls', attributeType='enum', enumName='----------', keyable=True)
    mc.setAttr(name + side + "_leg_settings_cc_01.fk_leg_controls", keyable=False, channelBox=True)
    mc.addAttr( leg_settings_control.C, shortName='upper_leg_length_parameter', longName='Upper_leg_Length', attributeType='float', defaultValue=1.0, minValue=0.0, keyable=True)
    mc.addAttr( leg_settings_control.C, shortName='lower_leg_length_parameter', longName='Lower_leg_Length', attributeType='float', defaultValue=1.0, minValue=0.0, keyable=True)

    # add custom IK attributes to control
    mc.addAttr( leg_settings_control.C, shortName='ik_leg_controls', longName='IK_Leg_Controls', attributeType='enum', enumName='----------', keyable=True)
    mc.setAttr( name + side + "_leg_settings_cc_01.ik_leg_controls", keyable=False, channelBox=True)
    mc.addAttr( leg_settings_control.C, shortName='slide_parameter', longName='Slide', attributeType='float', defaultValue=0.0, minValue=-1.0, maxValue=1.0, keyable=True)
    mc.addAttr( leg_settings_control.C, shortName='stretch_parameter', longName='Stretch', attributeType='float', defaultValue=1.0, minValue=0.0, maxValue=1.0, keyable=True)
    mc.addAttr( leg_settings_control.C, shortName='soft_parameter', longName='Soft', attributeType='float', defaultValue=0.0, minValue=0.0, maxValue=1.0, keyable=True)
    mc.addAttr( leg_settings_control.C, shortName='pin_parameter', longName='Pin', attributeType='float', defaultValue=0.0, minValue=0.0, maxValue=1.0, keyable=True)
    mc.addAttr( leg_settings_control.C, shortName='ik_follow_parameter', longName='Follow', attributeType='enum', enumName='Global:COG:Hips:', keyable=True)
    
    # add custom IK foot attributes to control
    mc.addAttr( leg_settings_control.C, shortName='ik_foot_controls', longName='IK_Foot_Controls', attributeType='enum', enumName='----------', keyable=True)
    mc.setAttr( name + side + "_leg_settings_cc_01.ik_foot_controls", keyable=False, channelBox=True)
    
    mc.addAttr( leg_settings_control.C, shortName='twist', longName='twist', attributeType='enum', enumName='#####', keyable=True)
    mc.setAttr( name + side + "_leg_settings_cc_01.twist", keyable=False, channelBox=True)
    mc.addAttr( leg_settings_control.C, shortName='toe_twist_parameter', longName='Toe_Twist', attributeType='float', defaultValue=0.0, minValue=-360.0, maxValue=360.0, keyable=True)
    mc.addAttr( leg_settings_control.C, shortName='ball_twist_parameter', longName='Ball_Twist', attributeType='float', defaultValue=0.0, minValue=-360.0, maxValue=360.0, keyable=True)
    mc.addAttr( leg_settings_control.C, shortName='heel_twist_parameter', longName='Heel_Twist', attributeType='float', defaultValue=0.0, minValue=-360.0, maxValue=360.0, keyable=True)

    mc.addAttr( leg_settings_control.C, shortName='roll', longName='roll', attributeType='enum', enumName='#####', keyable=True)
    mc.setAttr( name + side + "_leg_settings_cc_01.roll", keyable=False, channelBox=True)
    mc.addAttr( leg_settings_control.C, shortName='roll_break_angle_parameter', longName='Roll_Break_Angle', attributeType='float', defaultValue=35.0, minValue=-360.0, maxValue=360.0, keyable=True)
    mc.addAttr( leg_settings_control.C, shortName='forward_back_parameter', longName='Forward_Back', attributeType='float', defaultValue=0.0, minValue=-360.0, maxValue=360.0, keyable=True)
    mc.addAttr( leg_settings_control.C, shortName='side_to_side_parameter', longName='Side_To_Side', attributeType='float', defaultValue=0.0, minValue=-360.0, maxValue=360.0, keyable=True)


    
    
    # make two offset groups
    transform.make_offset_group(name + side + '_leg_settings_cc_01', name + side + '_leg_settings_constrain')
    transform.make_offset_group(name + side + '_leg_settings_cc_01', name + side + '_leg_settings_curve_offset')

    # position settings control
    if side=="_LFT":
        mc.move(-.040,0.0,0.0, name + side + '_leg_settings_curve_offset_os_grp_01', relative=True)
    else:
        mc.move(.040,0.0,0.0, name + side + '_leg_settings_curve_offset_os_grp_01', relative=True)
    mc.rotate(90.0,0.0,0.0, name + side + '_leg_settings_curve_offset_os_grp_01', relative=True)

    # parent control offset group and freeze transforms
    mc.parent(name + side + '_leg_settings_cc_os_grp_01', name + '_secondary_global_cc_01')
    mc.makeIdentity (apply=True, translate=True, rotate=True, scale=False)
    
    # align settings control and groups
    mc.rotate(0.0,-90.0,0.0, name + side + '_leg_settings_cc_os_grp_01', relative=True)

    # lock and hide all rotate, scale, and visibility
    mc.setAttr( name + side + "_leg_settings_cc_01.rotateX", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_leg_settings_cc_01.rotateY", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_leg_settings_cc_01.rotateZ", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_leg_settings_cc_01.scaleX", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_leg_settings_cc_01.scaleY", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_leg_settings_cc_01.scaleZ", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_leg_settings_cc_01.visibility", lock=True, keyable=False, channelBox=False)



    """
    FK leg setup
    """
    
    # create FK joints and mirror for right FK joints
    if side == "_LFT":
        # create upper_leg FK JNT
        mc.joint(name=name + side + "_upper_leg_FK_JNT_01", position = mc.xform(hip_joint, query=True, translation=True, worldSpace=True), absolute=True, radius=0.01)
        mc.parent(name + side + "_upper_leg_FK_JNT_01", name + '_secondary_global_cc_01')
        
        # create lower_leg FK JNT
        mc.joint(name=name + side + "_lower_leg_FK_JNT_01", position = mc.xform(knee_joint, query=True, translation=True, worldSpace=True), absolute=True, radius=0.01)
        mc.joint( name + side + '_upper_leg_FK_JNT_01', edit=True, zeroScaleOrient=True, orientJoint='xzy', secondaryAxisOrient = 'zup' )
        
        # create ankle FK JNT
        mc.joint(name=name + side + "_ankle_FK_JNT_01", position = mc.xform(ankle_joint, query=True, translation=True, worldSpace=True), absolute=True, radius=0.01)
        mc.joint( name + side + '_lower_leg_FK_JNT_01', edit=True, zeroScaleOrient=True, orientJoint='xzy', secondaryAxisOrient = 'yup' )
        
        # reset orientations on entire leg
        mc.joint( name + side + '_upper_leg_FK_JNT_01', edit=True, zeroScaleOrient=True, children=True, orientJoint='xyz', secondaryAxisOrient = 'yup' )
        
        
        #################TEMP patch for Beowulf##############
        if name == 'Beowulf':
            mc.joint( name + side + '_upper_leg_FK_JNT_01', edit=True, zeroScaleOrient=True, children=True, orientJoint='xyz', secondaryAxisOrient = 'zup' )
    
        # reset orientations on ankle joint
        mc.select( name + side + "_ankle_FK_JNT_01", replace=True)
        mc.rotate(0.0,-90.0,0.0, worldSpace=True, absolute=True)
        mc.makeIdentity (apply=True, translate=False, rotate=True, scale=False)
    else:
        mc.mirrorJoint(name + '_LFT_upper_leg_FK_JNT_01', mirrorBehavior=True, mirrorYZ=True, searchReplace=("LFT","RGT"))
    
    # create offset grp
    FK_joints_offset_group = transform.make_offset_group( name + side + "_upper_leg_FK_JNT_01" )
    '''
    #match offset group's transforms to object transforms
    mc.delete( mc.parentConstraint( name + side + "_upper_leg_FK_JNT_01", FK_joints_offset_group ))
    mc.delete( mc.scaleConstraint( name + side + "_upper_leg_FK_JNT_01", FK_joints_offset_group ))
    '''
    ############## WHAT THE HECK IS GOING ON WITH THE PARENT COMMAND HERE???????????? KEEPS COMBINING MIRRORED JOINTS - HENCE NO TRANSFORM.MAKE_OFFSET_GROUP AND THE SNIPPET BELOW.
    #mc.parent(name + side + "_upper_leg_FK_JNT_01", FK_joints_offset_group, absolute=True)
    
    if side=="_RGT":
        mc.parent(FK_joints_offset_group, name + '_secondary_global_cc_01')
        reversed_x_position = mc.getAttr(FK_joints_offset_group + '.translateX')
        fixed_x_position = reversed_x_position*-1.0
        mc.setAttr(FK_joints_offset_group + '.translateX', fixed_x_position)

    # create FK control curves
    FK_upper_leg_control = control.Control(
                                  prefix = name + side + '_FK_upper_leg',
                                  scale = .050,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_upper_leg_FK_JNT_01',
                                  rotate_to = name + side + '_upper_leg_FK_JNT_01',
                                  parent = name + '_secondary_global_cc_01',
                                  shape = 'circle',
                                  locked_channels = ['scale', 'visibility']
                                  )
    
    FK_lower_leg_control = control.Control(
                                  prefix = name + side + '_FK_lower_leg',
                                  scale = .040,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_lower_leg_FK_JNT_01',
                                  rotate_to = name + side + '_lower_leg_FK_JNT_01',
                                  parent = FK_upper_leg_control.C,
                                  shape = 'circle',
                                  locked_channels = ['scale', 'visibility']
                                  )
    
    FK_ankle_control = control.Control(
                                  prefix = name + side + '_FK_ankle',
                                  scale = .030,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_ankle_FK_JNT_01',
                                  rotate_to = name + side + '_ankle_FK_JNT_01',
                                  parent = FK_lower_leg_control.C,
                                  shape = 'circle_y',
                                  locked_channels = ['scale', 'visibility']
                                  )


    # lock and hide translate, scale, and visibility
    for part in ['upper_leg', 'lower_leg', 'ankle']:
        mc.setAttr( name + side + "_FK_" + part + "_cc_01.translateX", lock=True, keyable=False, channelBox=False)
        mc.setAttr( name + side + "_FK_" + part + "_cc_01.translateY", lock=True, keyable=False, channelBox=False)
        mc.setAttr( name + side + "_FK_" + part + "_cc_01.translateZ", lock=True, keyable=False, channelBox=False)
        mc.setAttr( name + side + "_FK_" + part + "_cc_01.scaleX", lock=True, keyable=False, channelBox=False)
        mc.setAttr( name + side + "_FK_" + part + "_cc_01.scaleY", lock=True, keyable=False, channelBox=False)
        mc.setAttr( name + side + "_FK_" + part + "_cc_01.scaleZ", lock=True, keyable=False, channelBox=False)
        mc.setAttr( name + side + "_FK_" + part + "_cc_01.visibility", lock=True, keyable=False, channelBox=False)
      
    # Create offset groups to move controls according to FK stretch parameters
    transform.make_offset_group(FK_upper_leg_control.Off, name + side + '_FK_upper_leg_cc_stretch')
    transform.make_offset_group(FK_lower_leg_control.Off, name + side + '_FK_lower_leg_cc_stretch')
    transform.make_offset_group(FK_ankle_control.Off, name + side + '_FK_ankle_cc_stretch')
    
    # Point constrain control stretchy offset groups to FK joints
    mc.pointConstraint(name + side + '_lower_leg_FK_JNT_01', name + side + '_FK_lower_leg_cc_stretch_os_grp_01')
    mc.pointConstraint(name + side + '_ankle_FK_JNT_01', name + side + '_FK_ankle_cc_stretch_os_grp_01')
    
    # Connect joints to controls
    mc.connectAttr( FK_upper_leg_control.C + '.rotate', name + side + '_upper_leg_FK_JNT_01.rotate', force=True)
    mc.connectAttr( FK_lower_leg_control.C + '.rotate', name + side + '_lower_leg_FK_JNT_01.rotate', force=True)
    mc.connectAttr( FK_ankle_control.C + '.rotate', name + side + '_ankle_FK_JNT_01.rotate', force=True)
    mc.connectAttr( name + side + '_leg_settings_cc_01.upper_leg_length_parameter', name + side + '_upper_leg_FK_JNT_01.scaleX', force=True)
    mc.connectAttr( name + side + '_leg_settings_cc_01.lower_leg_length_parameter', name + side + '_lower_leg_FK_JNT_01.scaleX', force=True)
    

    
    
    """
    IK leg setup
    """
    
    # create IK joints by duplicating FK chain
    mc.duplicate(name + side + '_upper_leg_FK_JNT_01', renameChildren=True)
    mc.rename(name + side + '_upper_leg_FK_JNT_02', name + side + '_upper_leg_IK_JNT_01')
    mc.rename(name + side + '_lower_leg_FK_JNT_02', name + side + '_lower_leg_IK_JNT_01')
    mc.rename(name + side + '_ankle_FK_JNT_02', name + side + '_ankle_IK_JNT_01')



    # create offset group
    IK_joints_offset_group = transform.make_offset_group(name + side + "_upper_leg_IK_JNT_01")

    #parent correctly
    mc.parent(IK_joints_offset_group, name + '_secondary_global_cc_01')



    # create locators for IK leg rig
    mc.spaceLocator(name=name + side + "_upper_leg_loc_01")
    mc.delete(mc.pointConstraint(hip_joint, name + side + "_upper_leg_loc_01"))
    mc.spaceLocator(name=name + side + "_lower_leg_loc_01")
    mc.delete(mc.pointConstraint(knee_joint, name + side + "_lower_leg_loc_01"))
    mc.spaceLocator(name=name + side + "_ankle_IK_loc_01")
    mc.delete(mc.pointConstraint(ankle_joint, name + side + "_ankle_IK_loc_01"))
    mc.spaceLocator(name=name + side + "_leg_soft_blend_IK_loc_01")
    mc.delete(mc.pointConstraint(ankle_joint, name + side + "_leg_soft_blend_IK_loc_01"))
    mc.spaceLocator(name=name + side + "_IK_leg_cc_distance_loc_01")
    mc.delete(mc.pointConstraint(ankle_joint, name + side + "_IK_leg_cc_distance_loc_01"))

    # rotate upper leg locator to point X axis at ankle
    mc.rotate(180.0,0.0,-90.0, name + side + "_upper_leg_loc_01")
    
    # create IK control curve
    IK_leg_control = control.Control(
                                  prefix = name + side + '_IK_leg',
                                  scale = .040,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_ankle_IK_JNT_01',
                                  rotate_to = '',
                                  parent = '',
                                  shape = 'box',
                                  locked_channels = ['scale', 'visibility']
                                  )
    
    # rotate offset group to align Z to primary axis
    if side == "_LFT":
        mc.rotate(0.0,-90.0,0.0, IK_leg_control.Off)
    else:
        mc.rotate(180.0,90.0,0.0, IK_leg_control.Off)

    
    # constraint ankle joint's rotations to IK control's rotations
    mc.orientConstraint( name + side + '_IK_leg_cc_01', name + side + '_ankle_IK_JNT_01', maintainOffset=False)
    
    # lock and hide attributes
    mc.setAttr( name + side + "_IK_leg_cc_01.scaleX", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_IK_leg_cc_01.scaleY", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_IK_leg_cc_01.scaleZ", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_IK_leg_cc_01.visibility", lock=True, keyable=False, channelBox=False)
    
    # add rpIK handle
    rpIK_handle = mc.ikHandle( name=name + side + "_leg_rpIK_01", startJoint=name + side + "_upper_leg_IK_JNT_01", endEffector=name + side + "_ankle_IK_JNT_01", solver='ikRPsolver' )
    mc.setAttr( 'ikRPsolver.tolerance', 1e-007)

    # add pole vector constraint
    mc.poleVectorConstraint( name + side + "_lower_leg_loc_01", name + side + "_leg_rpIK_01" )


    # aim constrain upper leg loc to rpIK control curve
    mc.aimConstraint( IK_leg_control.C, name + side + "_upper_leg_loc_01", worldUpType="object", worldUpObject=name + '_hips_cc_01')

    # parenting
    mc.pointConstraint( name + side + "_upper_leg_loc_01", name + side + "_upper_leg_IK_JNT_01" )
    mc.parent(name + side + "_ankle_IK_loc_01", name + side + "_upper_leg_loc_01")
    mc.pointConstraint( IK_leg_control.C, name + side + "_IK_leg_cc_distance_loc_01" )
    mc.setAttr(name + side + "_IK_leg_cc_distance_loc_01.rotateY", 0.0) # not sure why the parenting is causing this rotation, perhaps because of locked channels?
    mc.parent(name + side + "_upper_leg_loc_01", name + '_secondary_global_cc_01')
    mc.parent(name + side + "_lower_leg_loc_01", name + '_secondary_global_cc_01')
    mc.parent(name + side + "_leg_soft_blend_IK_loc_01", name + '_secondary_global_cc_01')
    mc.makeIdentity (apply=True, translate=True, rotate=False, scale=False)
    mc.parent( name + side + "_leg_rpIK_01", name + side + "_leg_soft_blend_IK_loc_01",)

    # for attaching to rest of rig
    mc.group(name=name + side + '_upper_leg_loc_connect_grp_01', empty=True)
    mc.delete(mc.pointConstraint(name + side + '_upper_leg_loc_01', name + side + '_upper_leg_loc_connect_grp_01', maintainOffset=False))
    mc.parent(name + side + '_upper_leg_loc_01', name + side + '_upper_leg_loc_connect_grp_01')
    mc.parent(name + side + '_upper_leg_loc_connect_grp_01', name + '_secondary_global_cc_01')


    # os group for handling constraints (like for foot roll) (OUTDATED, should have no function any more but scared to delete it)
    transform.make_offset_group(name + side + '_leg_rpIK_01', prefix = name + side + '_leg_rpIK_constrain')

    # create measure distance nodes   
    IK_control_distance_shape = mc.distanceDimension( startPoint=[1.0,0.0,0.0], endPoint=[10.0,0.0,0.0] )
    soft_distance_shape = mc.distanceDimension( startPoint=[1.0,0.0,0.0], endPoint=[10.0,0.0,0.0] )
    upper_leg_distance_shape = mc.distanceDimension( startPoint=[1.0,0.0,0.0], endPoint=[10.0,0.0,0.0] )
    lower_leg_distance_shape = mc.distanceDimension( startPoint=[1.0,0.0,0.0], endPoint=[10.0,0.0,0.0] )
    stretch_distance_shape = mc.distanceDimension( startPoint=[1.0,0.0,0.0], endPoint=[10.0,0.0,0.0] )

    # attach measure distance node to appropriate locators  
    mc.connectAttr(name + side + '_upper_leg_loc_01.worldPosition[0]', IK_control_distance_shape + '.startPoint', force=True)
    mc.connectAttr(name + side + '_IK_leg_cc_distance_loc_01.worldPosition[0]', IK_control_distance_shape + '.endPoint', force=True)
    
    mc.connectAttr(name + side + '_ankle_IK_loc_01.worldPosition[0]', soft_distance_shape + '.startPoint', force=True)
    mc.connectAttr(name + side + '_leg_soft_blend_IK_loc_01.worldPosition[0]', soft_distance_shape + '.endPoint', force=True)
    
    mc.connectAttr(name + side + '_upper_leg_loc_01.worldPosition[0]', upper_leg_distance_shape + '.startPoint', force=True)
    mc.connectAttr(name + side + '_lower_leg_loc_01.worldPosition[0]', upper_leg_distance_shape + '.endPoint', force=True)
    
    mc.connectAttr(name + side + '_lower_leg_loc_01.worldPosition[0]', lower_leg_distance_shape + '.startPoint', force=True)
    mc.connectAttr(name + side + '_leg_soft_blend_IK_loc_01.worldPosition[0]', lower_leg_distance_shape + '.endPoint', force=True)

    mc.connectAttr(name + side + '_upper_leg_loc_01.worldPosition[0]', stretch_distance_shape + '.startPoint', force=True)
    mc.connectAttr(name + side + '_leg_soft_blend_IK_loc_01.worldPosition[0]', stretch_distance_shape + '.endPoint', force=True)
    
    # rename measure distance nodes
    mc.rename(mc.listRelatives(IK_control_distance_shape, parent=True), name + side + '_leg_IK_control_distance_01')
    mc.rename(mc.listRelatives(soft_distance_shape, parent=True), name + side + '_leg_soft_distance_01')
    mc.rename(mc.listRelatives(upper_leg_distance_shape, parent=True), name + side + '_upper_leg_distance_01')
    mc.rename(mc.listRelatives(lower_leg_distance_shape, parent=True), name + side + '_lower_leg_distance_01')
    mc.rename(mc.listRelatives(stretch_distance_shape, parent=True), name + side + '_leg_stretch_distance_01')
    
    # get rid of spare locators
    mc.delete('locator*')
    
    
    """
    Basic "soft" setup
    """
    
    # create condition nodes
    mc.shadingNode('condition', asUtility=True, name= name + side + '_leg_ik_control_distance_greater_than_chain_length_minus_soft_parameter_COND_01')
    mc.setAttr( name + side + '_leg_ik_control_distance_greater_than_chain_length_minus_soft_parameter_COND_01.operation', 2)
    mc.shadingNode('condition', asUtility=True, name= name + side + '_leg_soft_parameter_greater_than_zero_COND_01')
    mc.setAttr( name + side + '_leg_soft_parameter_greater_than_zero_COND_01.operation', 2)
    
    # create plus minus average nodes
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_leg_chain_length_minus_soft_parameter_PMA_01')
    mc.setAttr( name + side + '_leg_chain_length_minus_soft_parameter_PMA_01.operation', 2)
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_leg_chain_length_CONS_01')
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_leg_control_distance_minus_chain_length_minus_soft_parameter_PMA_01')
    mc.setAttr( name + side + '_leg_control_distance_minus_chain_length_minus_soft_parameter_PMA_01.operation', 2)
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_leg_chain_length_minus_input_PMA_01')
    mc.setAttr( name + side + '_leg_chain_length_minus_input_PMA_01.operation', 2)

    # create multiply divide nodes
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_leg_input_divide_by_soft_parameter_MD_01')
    mc.setAttr( name + side + '_leg_input_divide_by_soft_parameter_MD_01.operation', 2)
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_leg_input_multiply_by_negative_one_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_leg_e_to_the_input_power_MD_01')
    mc.setAttr( name + side + '_leg_e_to_the_input_power_MD_01.operation', 3) 
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_leg_input_multiply_by_soft_parameter_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_leg_divide_one_by_total_scale_MD_01')
    mc.setAttr( name + side + '_leg_divide_one_by_total_scale_MD_01.operation', 2)
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_leg_input_multiply_by_control_distance_MD_01')
    mc.setAttr( name + side + '_leg_input_multiply_by_control_distance_MD_01.operation', 1)        
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_leg_diminish_soft_parameter_MD_01')
    mc.setAttr( name + side + '_leg_diminish_soft_parameter_MD_01.operation', 1)  
    mc.setAttr( name + side + '_leg_diminish_soft_parameter_MD_01.input2X', 0.01)  

        
    # make connections and initialize values
    mc.connectAttr( name + side + '_upper_leg_distance_0Shape1.distance', name + side + '_leg_chain_length_CONS_01.input3D[0].input3Dx', force=True)
    mc.connectAttr( name + side + '_lower_leg_distance_0Shape1.distance', name + side + '_leg_chain_length_CONS_01.input3D[1].input3Dx', force=True)   
    mc.connectAttr( name + side + '_leg_chain_length_CONS_01.output3Dx', name + side + '_leg_chain_length_minus_soft_parameter_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_01.soft_parameter', name + side + '_leg_diminish_soft_parameter_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_leg_diminish_soft_parameter_MD_01.outputX', name + side + '_leg_chain_length_minus_soft_parameter_PMA_01.input3D[1].input3Dx', force=True)
    mc.connectAttr( name + side + '_leg_input_multiply_by_control_distance_MD_01.outputX', name + side + '_leg_ik_control_distance_greater_than_chain_length_minus_soft_parameter_COND_01.firstTerm', force=True)
    mc.connectAttr( name + side + '_leg_chain_length_minus_soft_parameter_PMA_01.output3Dx', name + side + '_leg_ik_control_distance_greater_than_chain_length_minus_soft_parameter_COND_01.secondTerm', force=True)
    mc.connectAttr(name + side + '_leg_diminish_soft_parameter_MD_01.outputX', name + side + '_leg_soft_parameter_greater_than_zero_COND_01.firstTerm', force=True)
    mc.connectAttr(name + side + '_leg_chain_length_CONS_01.output3Dx', name + side + '_leg_soft_parameter_greater_than_zero_COND_01.colorIfFalse.colorIfFalseR', force=True)
    mc.connectAttr( name + side + '_leg_input_multiply_by_control_distance_MD_01.outputX', name + side + '_leg_control_distance_minus_chain_length_minus_soft_parameter_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr( name + side + '_leg_chain_length_minus_soft_parameter_PMA_01.output3Dx', name + side + '_leg_control_distance_minus_chain_length_minus_soft_parameter_PMA_01.input3D[1].input3Dx', force=True)
    mc.connectAttr( name + side + '_leg_control_distance_minus_chain_length_minus_soft_parameter_PMA_01.output3Dx', name + side + '_leg_input_divide_by_soft_parameter_MD_01.input1X', force=True)
    mc.connectAttr( name + side + '_leg_diminish_soft_parameter_MD_01.outputX', name + side + '_leg_input_divide_by_soft_parameter_MD_01.input2X', force=True)
    mc.connectAttr( name + side + '_leg_input_divide_by_soft_parameter_MD_01.outputX', name + side + '_leg_input_multiply_by_negative_one_MD_01.input1X', force=True)
    mc.setAttr( name + side + '_leg_input_multiply_by_negative_one_MD_01.input2X', -1.0)
    mc.setAttr( name + side + '_leg_e_to_the_input_power_MD_01.input1X', 2.718282)
    mc.connectAttr( name + side + '_leg_input_multiply_by_negative_one_MD_01.outputX', name + side + '_leg_e_to_the_input_power_MD_01.input2X', force=True) 
    mc.connectAttr( name + side + '_leg_e_to_the_input_power_MD_01.outputX', name + side + '_leg_input_multiply_by_soft_parameter_MD_01.input1X', force=True)
    mc.connectAttr( name + side + '_leg_diminish_soft_parameter_MD_01.outputX', name + side + '_leg_input_multiply_by_soft_parameter_MD_01.input2X', force=True)
    mc.connectAttr( name + side + '_leg_chain_length_CONS_01.output3Dx', name + side + '_leg_chain_length_minus_input_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr( name + side + '_leg_input_multiply_by_soft_parameter_MD_01.outputX', name + side + '_leg_chain_length_minus_input_PMA_01.input3D[1].input3Dx', force=True)
    mc.connectAttr(name + side + '_leg_chain_length_minus_input_PMA_01.output3Dx', name + side + '_leg_soft_parameter_greater_than_zero_COND_01.colorIfTrue.colorIfTrueR', force=True)
    mc.connectAttr(name + side + '_leg_soft_parameter_greater_than_zero_COND_01.outColor.outColorR', name + side + '_leg_ik_control_distance_greater_than_chain_length_minus_soft_parameter_COND_01.colorIfTrue.colorIfTrueR', force=True)
    mc.connectAttr(name + side + '_leg_input_multiply_by_control_distance_MD_01.outputX', name + side + '_leg_ik_control_distance_greater_than_chain_length_minus_soft_parameter_COND_01.colorIfFalse.colorIfFalseR', force=True)
    mc.connectAttr(name + side + '_leg_ik_control_distance_greater_than_chain_length_minus_soft_parameter_COND_01.outColor.outColorR', name + side + '_ankle_IK_loc_01.translateX', force=True)
    mc.connectAttr(name + '_secret_total_scale_MD_01.outputX', name + side + '_leg_divide_one_by_total_scale_MD_01.input2X', force=True)
    mc.setAttr( name + side + '_leg_divide_one_by_total_scale_MD_01.input1X', 1.0)
    mc.connectAttr(name + side + '_leg_divide_one_by_total_scale_MD_01.outputX', name + side + '_leg_input_multiply_by_control_distance_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_leg_IK_control_distance_0Shape1.distance', name + side + '_leg_input_multiply_by_control_distance_MD_01.input2X', force=True)


    # convert PMA to CONS (made by disconnecting PMA inputs to convert a plus minus average node into a constant node)
    mc.disconnectAttr( name + side + '_lower_leg_distance_0Shape1.distance', name + side + '_leg_chain_length_CONS_01.input3D[1].input3Dx')
    mc.disconnectAttr( name + side + '_upper_leg_distance_0Shape1.distance', name + side + '_leg_chain_length_CONS_01.input3D[0].input3Dx')
 

    # point constrain soft blend locator to ankle locator and IK control
    mc.pointConstraint(name + side + "_ankle_IK_loc_01", name + side + '_IK_leg_cc_01', name + side + "_leg_soft_blend_IK_loc_01" )
    
    # create remap value node and inverse to assign weights to point constraint
    mc.shadingNode('remapValue', asUtility=True, name= name + side + '_leg_IK_stretch_weight_RMV_01')
    mc.setAttr( name + side + '_leg_IK_stretch_weight_RMV_01.value[0].value_Interp', 2)
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_leg_invert_IK_stretch_weight_RMV_01')
    mc.setAttr( name + side + '_leg_invert_IK_stretch_weight_RMV_01.operation', 2)
    mc.setAttr(name + side + '_leg_invert_IK_stretch_weight_RMV_01.input3D[0].input3Dx', 1.0)
    mc.connectAttr(name + side + '_leg_IK_stretch_weight_RMV_01.outValue', name + side + '_leg_invert_IK_stretch_weight_RMV_01.input3D[1].input3Dx', force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_01.stretch_parameter', name + side + '_leg_IK_stretch_weight_RMV_01.inputValue', force=True)
    mc.connectAttr(name + side + '_leg_IK_stretch_weight_RMV_01.outValue', name + side + '_leg_soft_blend_IK_loc_01_pointConstraint1.' + name + side + '_IK_leg_cc_01W1', force=True)
    mc.connectAttr(name + side + '_leg_invert_IK_stretch_weight_RMV_01.output3Dx', name + side + '_leg_soft_blend_IK_loc_01_pointConstraint1.' + name + side + '_ankle_IK_loc_01W0', force=True)


    """
    Upper leg stretch setup
    """
    
    # create plus minus average nodes
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_upper_leg_bone_length_CONS_01')
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_upper_leg_bone_length_plus_input_PMA_01')

    # create multiply divide nodes
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_upper_leg_bone_length_divide_by_chain_length_MD_01')
    mc.setAttr( name + side + '_upper_leg_bone_length_divide_by_chain_length_MD_01.operation', 2)
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_upper_leg_input_multiply_by_inverse_total_scale_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_upper_leg_input_multiply_by_soft_length_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_upper_leg_input_multiply_by_stretch_parameter_MD_01')

    # make connections and initialize values
    mc.connectAttr(name + side + '_lower_leg_IK_JNT_01.translateX', name + side + '_upper_leg_bone_length_CONS_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_upper_leg_bone_length_CONS_01.output3Dx', name + side + '_upper_leg_bone_length_divide_by_chain_length_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_leg_chain_length_CONS_01.output3Dx', name + side + '_upper_leg_bone_length_divide_by_chain_length_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_leg_divide_one_by_total_scale_MD_01.outputX', name + side + '_upper_leg_input_multiply_by_inverse_total_scale_MD_01.input1X',  force=True)
    mc.connectAttr(name + side + '_leg_soft_distance_01.distance', name + side + '_upper_leg_input_multiply_by_inverse_total_scale_MD_01.input2X',  force=True)
    mc.connectAttr(name + side + '_upper_leg_input_multiply_by_inverse_total_scale_MD_01.outputX', name + side + '_upper_leg_input_multiply_by_soft_length_MD_01.input1X',  force=True)
    mc.connectAttr(name + side + '_upper_leg_bone_length_divide_by_chain_length_MD_01.outputX', name + side + '_upper_leg_input_multiply_by_soft_length_MD_01.input2X',  force=True)
    mc.connectAttr(name + side + '_upper_leg_input_multiply_by_soft_length_MD_01.outputX', name + side + '_upper_leg_input_multiply_by_stretch_parameter_MD_01.input1X',  force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_01.stretch_parameter', name + side + '_upper_leg_input_multiply_by_stretch_parameter_MD_01.input2X',  force=True)
    mc.connectAttr(name + side + '_upper_leg_input_multiply_by_stretch_parameter_MD_01.outputX', name + side + '_upper_leg_bone_length_plus_input_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_upper_leg_bone_length_CONS_01.output3Dx', name + side + '_upper_leg_bone_length_plus_input_PMA_01.input3D[1].input3Dx', force=True)

    # convert PMA to CONS (made by disconnecting PMA inputs to convert a plus minus average node into a constant node)
    mc.disconnectAttr( name + side + '_lower_leg_IK_JNT_01.translateX', name + side + '_upper_leg_bone_length_CONS_01.input3D[0].input3Dx')
    if side=="_RGT":
        true_length=mc.getAttr(name + side + '_upper_leg_bone_length_CONS_01.input3D[0].input3Dx')*-1.0
        mc.setAttr(name + side + '_upper_leg_bone_length_CONS_01.input3D[0].input3Dx', true_length)

    
    """
    Lower leg stretch setup
    """
    
    # create plus minus average nodes
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_lower_leg_bone_length_CONS_01')
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_lower_leg_bone_length_plus_input_PMA_01')

    # create multiply divide nodes
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_lower_leg_bone_length_divide_by_chain_length_MD_01')
    mc.setAttr( name + side + '_lower_leg_bone_length_divide_by_chain_length_MD_01.operation', 2)
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_lower_leg_input_multiply_by_inverse_total_scale_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_lower_leg_input_multiply_by_soft_length_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_lower_leg_input_multiply_by_stretch_parameter_MD_01')

    # make connections and initialize values
    mc.connectAttr(name + side + '_ankle_IK_JNT_01.translateX', name + side + '_lower_leg_bone_length_CONS_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_lower_leg_bone_length_CONS_01.output3Dx', name + side + '_lower_leg_bone_length_divide_by_chain_length_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_leg_chain_length_CONS_01.output3Dx', name + side + '_lower_leg_bone_length_divide_by_chain_length_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_leg_divide_one_by_total_scale_MD_01.outputX', name + side + '_lower_leg_input_multiply_by_inverse_total_scale_MD_01.input1X',  force=True)
    mc.connectAttr(name + side + '_leg_soft_distance_01.distance', name + side + '_lower_leg_input_multiply_by_inverse_total_scale_MD_01.input2X',  force=True)
    mc.connectAttr(name + side + '_lower_leg_input_multiply_by_inverse_total_scale_MD_01.outputX', name + side + '_lower_leg_input_multiply_by_soft_length_MD_01.input1X',  force=True)
    mc.connectAttr(name + side + '_lower_leg_bone_length_divide_by_chain_length_MD_01.outputX', name + side + '_lower_leg_input_multiply_by_soft_length_MD_01.input2X',  force=True)
    mc.connectAttr(name + side + '_lower_leg_input_multiply_by_soft_length_MD_01.outputX', name + side + '_lower_leg_input_multiply_by_stretch_parameter_MD_01.input1X',  force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_01.stretch_parameter', name + side + '_lower_leg_input_multiply_by_stretch_parameter_MD_01.input2X',  force=True)
    mc.connectAttr(name + side + '_lower_leg_input_multiply_by_stretch_parameter_MD_01.outputX', name + side + '_lower_leg_bone_length_plus_input_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_lower_leg_bone_length_CONS_01.output3Dx', name + side + '_lower_leg_bone_length_plus_input_PMA_01.input3D[1].input3Dx', force=True)

    # convert PMA to CONS (made by disconnecting PMA inputs to convert a plus minus average node into a constant node)
    mc.disconnectAttr( name + side + '_ankle_IK_JNT_01.translateX', name + side + '_lower_leg_bone_length_CONS_01.input3D[0].input3Dx')
    if side=="_RGT":
        true_length=mc.getAttr(name + side + '_lower_leg_bone_length_CONS_01.input3D[0].input3Dx')*-1.0
        mc.setAttr(name + side + '_lower_leg_bone_length_CONS_01.input3D[0].input3Dx', true_length)


    """
    Upper leg pin setup
    """
    
    # create condition nodes
    mc.shadingNode('condition', asUtility=True, name= name + side + '_upper_leg_pin_length_greater_than_bone_length_COND_01')
    mc.setAttr( name + side + '_upper_leg_pin_length_greater_than_bone_length_COND_01.operation', 1)

    # create blend two attr nodes
    mc.shadingNode('blendTwoAttr', asUtility=True, name= name + side + '_upper_leg_pin_BLEND_01')

    # create multiply divide nodes
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_upper_leg_distance_multiply_by_inverse_scale_MD_01')
    if side=="_RGT":
        mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_upper_leg_length_reinvert_MD_01')
        mc.setAttr(name + side + '_upper_leg_length_reinvert_MD_01.input2X', -1.0)


    # make connections and initialize values
    mc.connectAttr(name + side + '_upper_leg_distance_01.distance', name + side + '_upper_leg_distance_multiply_by_inverse_scale_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_leg_divide_one_by_total_scale_MD_01.outputX', name + side + '_upper_leg_distance_multiply_by_inverse_scale_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_upper_leg_distance_multiply_by_inverse_scale_MD_01.outputX', name + side + '_upper_leg_pin_length_greater_than_bone_length_COND_01.firstTerm', force=True)
    mc.connectAttr(name + side + '_upper_leg_distance_multiply_by_inverse_scale_MD_01.outputX', name + side + '_upper_leg_pin_length_greater_than_bone_length_COND_01.colorIfTrue.colorIfTrueR', force=True)
    mc.connectAttr(name + side + '_upper_leg_bone_length_plus_input_PMA_01.output3Dx', name + side + '_upper_leg_pin_BLEND_01.input[0]', force=True)
    mc.connectAttr(name + side + '_upper_leg_pin_length_greater_than_bone_length_COND_01.outColorR', name + side + '_upper_leg_pin_BLEND_01.input[1]', force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_01.pin_parameter', name + side + '_upper_leg_pin_BLEND_01.attributesBlender', force=True)
    mc.connectAttr(name + side + '_upper_leg_pin_BLEND_01.output', name + side + '_lower_leg_IK_JNT_01.translateX', force=True)
    if side=="_RGT":
        mc.connectAttr(name + side + '_upper_leg_pin_BLEND_01.output', name + side + '_upper_leg_length_reinvert_MD_01.input1X',force=True)
        mc.connectAttr(name + side + '_upper_leg_length_reinvert_MD_01.outputX', name + side + '_lower_leg_IK_JNT_01.translateX', force=True)

    
    
    """
    Lower leg pin setup
    """
    
    # create condition nodes
    mc.shadingNode('condition', asUtility=True, name= name + side + '_lower_leg_pin_length_greater_than_bone_length_COND_01')
    mc.setAttr( name + side + '_lower_leg_pin_length_greater_than_bone_length_COND_01.operation', 1)

    # create blend two attr nodes
    mc.shadingNode('blendTwoAttr', asUtility=True, name= name + side + '_lower_leg_pin_BLEND_01')

    # create multiply divide nodes
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_lower_leg_distance_multiply_by_inverse_scale_MD_01')
    if side=="_RGT":
        mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_lower_leg_length_reinvert_MD_01')
        mc.setAttr(name + side + '_lower_leg_length_reinvert_MD_01.input2X', -1.0)

    # make connections and initialize values
    mc.connectAttr(name + side + '_lower_leg_distance_01.distance', name + side + '_lower_leg_distance_multiply_by_inverse_scale_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_leg_divide_one_by_total_scale_MD_01.outputX', name + side + '_lower_leg_distance_multiply_by_inverse_scale_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_lower_leg_distance_multiply_by_inverse_scale_MD_01.outputX', name + side + '_lower_leg_pin_length_greater_than_bone_length_COND_01.firstTerm', force=True)
    mc.connectAttr(name + side + '_lower_leg_distance_multiply_by_inverse_scale_MD_01.outputX', name + side + '_lower_leg_pin_length_greater_than_bone_length_COND_01.colorIfTrue.colorIfTrueR', force=True)
    mc.connectAttr(name + side + '_lower_leg_pin_length_greater_than_bone_length_COND_01.outColorR', name + side + '_lower_leg_pin_BLEND_01.input[1]', force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_01.pin_parameter', name + side + '_lower_leg_pin_BLEND_01.attributesBlender', force=True)
    mc.connectAttr(name + side + '_lower_leg_pin_BLEND_01.output', name + side + '_ankle_IK_JNT_01.translateX', force=True)
    if side=="_RGT":
        mc.connectAttr(name + side + '_lower_leg_pin_BLEND_01.output', name + side + '_lower_leg_length_reinvert_MD_01.input1X',force=True)
        mc.connectAttr(name + side + '_lower_leg_length_reinvert_MD_01.outputX', name + side + '_ankle_IK_JNT_01.translateX', force=True)

    
    """
    leg slide setup
    """
    
    # create condition nodes   
    mc.shadingNode('condition', asUtility=True, name= name + side + '_leg_slide_parameter_less_than_zero_COND_01')
    mc.setAttr( name + side + '_leg_slide_parameter_less_than_zero_COND_01.operation', 4)
    mc.shadingNode('condition', asUtility=True, name= name + side + '_stretched_leg_chain_distance_greater_than_chain_distance_COND_01')
    mc.setAttr( name + side + '_stretched_leg_chain_distance_greater_than_chain_distance_COND_01.operation', 2)
    
    # create plus minus average nodes
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_upper_leg_slide_input_minus_condition_PMA_01')
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_lower_leg_slide_input_minus_condition_PMA_01')
    mc.setAttr( name + side + '_lower_leg_slide_input_minus_condition_PMA_01.operation', 2)
    
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_upper_leg_length_constant_plus_slide_condition_output_PMA_01')    
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_lower_leg_length_constant_plus_slide_condition_output_PMA_01')    

    

    # create multiply divide nodes
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_upper_leg_input_multiply_by_slide_parameter_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_lower_leg_input_multiply_by_slide_parameter_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_leg_stretch_distance_multiply_by_inverse_total_scale_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_stretchy_leg_chain_length_divided_by_constant_chain_length_MD_01')
    mc.setAttr( name + side + '_stretchy_leg_chain_length_divided_by_constant_chain_length_MD_01.operation', 2)
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_input_multiply_by_upper_leg_constant_length_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_input_multiply_by_lower_leg_constant_length_MD_01')

    # make connections and initialize values
    mc.connectAttr(name + side + '_leg_settings_cc_01.slide_parameter', name + side + '_leg_slide_parameter_less_than_zero_COND_01.firstTerm', force=True)
    mc.connectAttr(name + side + '_upper_leg_bone_length_CONS_01.output3Dx', name + side + '_input_multiply_by_upper_leg_constant_length_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_lower_leg_bone_length_CONS_01.output3Dx', name + side + '_input_multiply_by_lower_leg_constant_length_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_01.slide_parameter', name + side + '_upper_leg_input_multiply_by_slide_parameter_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_01.slide_parameter', name + side + '_lower_leg_input_multiply_by_slide_parameter_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_stretched_leg_chain_distance_greater_than_chain_distance_COND_01.outColor.outColorR', name + side + '_stretchy_leg_chain_length_divided_by_constant_chain_length_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_leg_chain_length_CONS_01.output3Dx', name + side + '_stretchy_leg_chain_length_divided_by_constant_chain_length_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_stretchy_leg_chain_length_divided_by_constant_chain_length_MD_01.outputX', name + side + '_input_multiply_by_upper_leg_constant_length_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_stretchy_leg_chain_length_divided_by_constant_chain_length_MD_01.outputX', name + side + '_input_multiply_by_lower_leg_constant_length_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_input_multiply_by_upper_leg_constant_length_MD_01.outputX', name + side + '_upper_leg_input_multiply_by_slide_parameter_MD_01.input1X',force=True)
    mc.connectAttr(name + side + '_input_multiply_by_lower_leg_constant_length_MD_01.outputX', name + side + '_lower_leg_input_multiply_by_slide_parameter_MD_01.input1X',force=True)
    mc.connectAttr(name + side + '_upper_leg_input_multiply_by_slide_parameter_MD_01.outputX', name + side + '_leg_slide_parameter_less_than_zero_COND_01.colorIfTrue.colorIfTrueR', force=True)
    mc.connectAttr(name + side + '_lower_leg_input_multiply_by_slide_parameter_MD_01.outputX', name + side + '_leg_slide_parameter_less_than_zero_COND_01.colorIfFalse.colorIfFalseR', force=True)
    mc.connectAttr(name + side + '_upper_leg_bone_length_plus_input_PMA_01.output3Dx', name + side + '_upper_leg_slide_input_minus_condition_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_leg_slide_parameter_less_than_zero_COND_01.outColorR', name + side + '_upper_leg_slide_input_minus_condition_PMA_01.input3D[1].input3Dx', force=True)
    mc.connectAttr(name + side + '_lower_leg_bone_length_plus_input_PMA_01.output3Dx', name + side + '_lower_leg_slide_input_minus_condition_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_leg_slide_parameter_less_than_zero_COND_01.outColorR', name + side + '_lower_leg_slide_input_minus_condition_PMA_01.input3D[1].input3Dx', force=True)
    mc.connectAttr(name + side + '_upper_leg_slide_input_minus_condition_PMA_01.output3Dx', name + side + '_upper_leg_pin_BLEND_01.input[0]', force=True)
    mc.connectAttr(name + side + '_lower_leg_slide_input_minus_condition_PMA_01.output3Dx', name + side + '_lower_leg_pin_BLEND_01.input[0]', force=True)
    mc.connectAttr(name + side + '_leg_stretch_distance_01.distance', name + side + '_leg_stretch_distance_multiply_by_inverse_total_scale_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_leg_divide_one_by_total_scale_MD_01.outputX', name + side + '_leg_stretch_distance_multiply_by_inverse_total_scale_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_leg_stretch_distance_multiply_by_inverse_total_scale_MD_01.outputX', name + side + '_stretched_leg_chain_distance_greater_than_chain_distance_COND_01.firstTerm', force=True)
    mc.connectAttr(name + side + '_leg_chain_length_CONS_01.output3Dx', name + side + '_stretched_leg_chain_distance_greater_than_chain_distance_COND_01.secondTerm', force=True)
    mc.connectAttr(name + side + '_leg_stretch_distance_multiply_by_inverse_total_scale_MD_01.outputX', name + side + '_stretched_leg_chain_distance_greater_than_chain_distance_COND_01.colorIfTrue.colorIfTrueR', force=True)
    mc.connectAttr(name + side + '_leg_chain_length_CONS_01.output3Dx', name + side + '_stretched_leg_chain_distance_greater_than_chain_distance_COND_01.colorIfFalse.colorIfFalseR', force=True)
    mc.connectAttr(name + side + '_upper_leg_bone_length_CONS_01.output3Dx', name + side + '_upper_leg_length_constant_plus_slide_condition_output_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_leg_slide_parameter_less_than_zero_COND_01.outColor.outColorR', name + side + '_upper_leg_length_constant_plus_slide_condition_output_PMA_01.input3D[1].input3Dx', force=True)
    mc.connectAttr(name + side + '_lower_leg_bone_length_CONS_01.output3Dx', name + side + '_lower_leg_length_constant_plus_slide_condition_output_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_leg_slide_parameter_less_than_zero_COND_01.outColor.outColorR', name + side + '_lower_leg_length_constant_plus_slide_condition_output_PMA_01.input3D[1].input3Dx', force=True)
    mc.connectAttr(name + side + '_upper_leg_length_constant_plus_slide_condition_output_PMA_01.output3Dx', name + side + '_upper_leg_pin_length_greater_than_bone_length_COND_01.secondTerm', force=True)
    mc.connectAttr(name + side + '_upper_leg_length_constant_plus_slide_condition_output_PMA_01.output3Dx', name + side + '_upper_leg_pin_length_greater_than_bone_length_COND_01.colorIfFalse.colorIfFalseR', force=True)
    mc.connectAttr(name + side + '_lower_leg_length_constant_plus_slide_condition_output_PMA_01.output3Dx', name + side + '_lower_leg_pin_length_greater_than_bone_length_COND_01.secondTerm', force=True)
    mc.connectAttr(name + side + '_lower_leg_length_constant_plus_slide_condition_output_PMA_01.output3Dx', name + side + '_lower_leg_pin_length_greater_than_bone_length_COND_01.colorIfFalse.colorIfFalseR', force=True)


    """
    Settings control parent constraining
    """
    
    # constrain offset group to FK and IK chains
    mc.parentConstraint(name + side + "_IK_leg_cc_01", name + side + "_FK_ankle_cc_01", name + side + "_leg_settings_constrain_os_grp_01", maintainOffset=False)
    
    # create remap value node and inverse to assign weights to parent constraint
    mc.shadingNode('remapValue', asUtility=True, name= name + side + '_leg_settings_cc_parent_constraint_weight_RMV_01')
    mc.setAttr( name + side + '_leg_settings_cc_parent_constraint_weight_RMV_01.value[0].value_Interp', 2)
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_leg_settings_cc_parent_constraint_inverse_weight_RMV_01')
    mc.setAttr( name + side + '_leg_settings_cc_parent_constraint_inverse_weight_RMV_01.operation', 2)
    mc.setAttr(name + side + '_leg_settings_cc_parent_constraint_inverse_weight_RMV_01.input3D[0].input3Dx', 1.0)
    mc.connectAttr(name + side + '_leg_settings_cc_parent_constraint_weight_RMV_01.outValue', name + side + '_leg_settings_cc_parent_constraint_inverse_weight_RMV_01.input3D[1].input3Dx', force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_01.fk_ik_parameter', name + side + '_leg_settings_cc_parent_constraint_weight_RMV_01.inputValue', force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_parent_constraint_weight_RMV_01.outValue', name + side + '_leg_settings_constrain_os_grp_01_parentConstraint1.' + name + side + '_IK_leg_cc_01W0', force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_parent_constraint_inverse_weight_RMV_01.output3Dx', name + side + '_leg_settings_constrain_os_grp_01_parentConstraint1.' + name + side + '_FK_ankle_cc_01W1', force=True)
    
    
    
    """
    Base leg setup
    """
    
    # create Base joints by duplicating FK chain
    mc.duplicate(name + side + '_upper_leg_FK_JNT_01', renameChildren=True)
    mc.rename(name + side + '_upper_leg_FK_JNT_02', name + side + '_upper_leg_JNT_01')
    mc.rename(name + side + '_lower_leg_FK_JNT_02', name + side + '_lower_leg_JNT_01')
    mc.rename(name + side + '_ankle_FK_JNT_02', name + side + '_ankle_JNT_01')


    #create offset group
    base_joints_offset_group = transform.make_offset_group(name + side + "_upper_leg_JNT_01")
    
    #parent correctly
    mc.parent(base_joints_offset_group, name + '_secondary_global_cc_01')

    # constrain joints to FK and IK chains
    mc.parentConstraint(name + side + "_upper_leg_FK_JNT_01", name + side + "_upper_leg_IK_JNT_01", name + side + "_upper_leg_JNT_01")
    mc.parentConstraint(name + side + "_lower_leg_FK_JNT_01", name + side + "_lower_leg_IK_JNT_01", name + side + "_lower_leg_JNT_01")
    mc.parentConstraint(name + side + "_ankle_FK_JNT_01", name + side + "_ankle_IK_JNT_01", name + side + "_ankle_JNT_01")

    # set constraint weights driven by settings control
    mc.connectAttr(name + side + '_leg_settings_cc_parent_constraint_weight_RMV_01.outValue', name + side + '_ankle_JNT_01_parentConstraint1.' + name + side + '_ankle_IK_JNT_01W1', force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_parent_constraint_inverse_weight_RMV_01.output3Dx', name + side + '_ankle_JNT_01_parentConstraint1.' + name + side + '_ankle_FK_JNT_01W0', force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_parent_constraint_weight_RMV_01.outValue', name + side + '_lower_leg_JNT_01_parentConstraint1.' + name + side + '_lower_leg_IK_JNT_01W1', force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_parent_constraint_inverse_weight_RMV_01.output3Dx', name + side + '_lower_leg_JNT_01_parentConstraint1.' + name + side + '_lower_leg_FK_JNT_01W0', force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_parent_constraint_weight_RMV_01.outValue', name + side + '_upper_leg_JNT_01_parentConstraint1.' + name + side + '_upper_leg_IK_JNT_01W1', force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_parent_constraint_inverse_weight_RMV_01.output3Dx', name + side + '_upper_leg_JNT_01_parentConstraint1.' + name + side + '_upper_leg_FK_JNT_01W0', force=True)
    

    
    
    """ 
    create pole vector control
    """
    
    leg_pole_vector_control = control.Control(
                                  prefix = name + side + '_leg_pole_vector',
                                  scale = .020,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = knee_joint,
                                  rotate_to = '',
                                  parent = '',
                                  shape = 'box',
                                  locked_channels = ['visibility']
                                  )
    
    # add attribute for determining what the pole vector follows
    mc.addAttr( leg_pole_vector_control.C, shortName='ik_pole_vector_follow_parameter', longName='Follow', attributeType='enum', enumName='Ankle:Hips:COG:Global:', keyable=True)
        

    """
    pole vector placement by Nico Sanghrajka, based on demo by Marco Giardano
    """

    class MVector( om.MVector ):
        def __init__(self, *args):
            if( issubclass, args, list ) and len(args[0])== 3:
                om.MVector.__init__(self, args[0][0], args[0][1], args[0][2])
            else:
                om.MVector.__init__(self, args)
    
    def get_pole_vector_position( root_object, mid_object, end_object ):
        # based on the joints positions, figure out where the poleVector needs to go
        root_vector = MVector(mc.xform(root_object,query=True,rp=True,ws=True))
        mid_vector  = MVector(mc.xform(mid_object,query=True,rp=True,ws=True))
        end_vector  = MVector(mc.xform(end_object,query=True,rp=True,ws=True))
        distance_between_root_and_end = (end_vector-root_vector).length()
        
        start_to_end_vector = end_vector-root_vector
        start_to_mid_vector = mid_vector-root_vector
        dot_product = start_to_mid_vector * start_to_end_vector
        proj = float(dot_product) / float(start_to_end_vector.length())
        start_end_vector_normal = start_to_end_vector.normal()
        projV = start_end_vector_normal * proj
        arrowV = start_to_mid_vector - projV
        arrowV*= 1
        final_pole_vector = mid_vector + (arrowV.normal() * distance_between_root_and_end)
        return final_pole_vector
    
    # place pole vector control
    mc.select(name + side + '_upper_leg_IK_JNT_01', replace=True)
    mc.select(name + side + '_lower_leg_IK_JNT_01', add=True)
    mc.select(name + side + '_ankle_IK_JNT_01', add=True)
    selList = mc.ls(sl=1)
    pole_vector_position = get_pole_vector_position(selList[0],selList[1],selList[2]);
    mc.move(pole_vector_position.x, pole_vector_position.y, pole_vector_position.z, leg_pole_vector_control.Off, absolute=True)
    mc.select(clear=True)

    # point constrain pole vector locator to pole vector control
    mc.pointConstraint(leg_pole_vector_control.C, name + side + '_lower_leg_loc_01')
    
    # make pole vector connection line 
    pole_vector_line_start = mc.xform( name + side + '_lower_leg_IK_JNT_01', q=True, translation=True, worldSpace=True)
    pole_vector_line_end = mc.xform( leg_pole_vector_control.C, q=True, translation=True, worldSpace=True)
    pole_vector_line = mc.curve( name = name + side + '_leg_pole_vector_line_cc_01', degree=1, point=[pole_vector_line_start, pole_vector_line_end] )
    mc.cluster( pole_vector_line + '.cv[0]', name= name + side + 'pole_vector_CLU_A_01', weightedNode=[ name + side + '_lower_leg_IK_JNT_01', name + side + '_lower_leg_IK_JNT_01' ], bindState=True)
    mc.cluster( pole_vector_line + '.cv[1]', name= name + side + 'pole_vector_CLU_B_01', weightedNode=[ leg_pole_vector_control.C, leg_pole_vector_control.C ], bindState=True)
    mc.parent( pole_vector_line, name + '_no_transform_GRP_01')
    mc.setAttr(pole_vector_line + '.template', True)
    mc.select(clear=True)
    
    # parent constrain pole vector control to IK ankle control, hips, COG, and global controls
    mc.parentConstraint(name + side + '_IK_leg_cc_01', name + '_hips_cc_01', name + '_COG_cc_01', name + '_secondary_global_cc_01', leg_pole_vector_control.Off, maintainOffset=True)
    

    
    
    
    
    
    
    
    """
    feet
    """
    
    # create GRP for foot controls
    mc.group(name = name + side + '_foot_controls_GRP_01', empty=True)
    
    if side == "_LFT":

        #IK
        # select parent joint
        mc.select(name + side + '_ankle_IK_JNT_01', replace=True)
    
        # create IK joints for reverse foot
        mc.joint(name=name + side + '_foot_ball_IK_JNT_01', radius=.01)
        mc.delete(mc.pointConstraint(name + side + '_foot_ball_target_cc_01', name + side + '_foot_ball_IK_JNT_01', maintainOffset=False))
        mc.joint(name=name + side + '_foot_tip_IK_JNT_01', radius=.01)
        mc.delete(mc.pointConstraint(name + side + '_foot_tip_target_cc_01', name + side + '_foot_tip_IK_JNT_01', maintainOffset=False))


    if side=='_RGT':
        #rename foot joints already duplicated in joint chain
        mc.rename(name + side + '_foot_ball_FK_JNT_02', name + side + '_foot_ball_IK_JNT_01')
        mc.rename(name + side + '_foot_tip_FK_JNT_02', name + side + '_foot_tip_IK_JNT_01')
        mc.rename(name + side + '_foot_ball_FK_JNT_03', name + side + '_foot_ball_JNT_01')
        mc.rename(name + side + '_foot_tip_FK_JNT_03', name + side + '_foot_tip_JNT_01')
        





    # add scIK handles
    foot_ball_scIK_handle = mc.ikHandle( name=name + side + "_foot_ball_scIK_01", startJoint=name + side + "_ankle_IK_JNT_01", endEffector=name + side + "_foot_ball_IK_JNT_01", solver='ikSCsolver' )
    foot_ball_scIK_handle = mc.ikHandle( name=name + side + "_foot_tip_scIK_01", startJoint=name + side + "_foot_ball_IK_JNT_01", endEffector=name + side + "_foot_tip_IK_JNT_01", solver='ikSCsolver' )
    mc.setAttr( 'ikSCsolver.tolerance', 1e-007)
    
    # create os group and constrain group to receive transforms from settings constrain grp
    mc.group(name = name + side + '_foot_controls_constrain_grp_01', empty=True)
    mc.delete(mc.parentConstraint( name + side + '_ankle_IK_JNT_01', name + side + '_foot_controls_constrain_grp_01'))
    transform.make_offset_group(name + side + '_foot_controls_constrain_grp_01')
        
    # parent to foot controls group
    mc.parent(name + side + '_foot_controls_constrain_os_grp_01', name + side + '_foot_controls_GRP_01')

    
    
    # Create reverse foot setup
    # locators
    mc.spaceLocator(name=name + side + "_foot_ball_loc_01")
    mc.delete(mc.pointConstraint(name + side + '_foot_ball_target_cc_01', name + side + "_foot_ball_loc_01"))
    mc.spaceLocator(name=name + side + "_foot_tip_loc_01")
    mc.delete(mc.pointConstraint(name + side + '_foot_tip_target_cc_01', name + side + "_foot_tip_loc_01"))
    mc.spaceLocator(name=name + side + "_foot_heel_loc_01")
    mc.delete(mc.pointConstraint(name + side + '_foot_heel_target_cc_01', name + side + "_foot_heel_loc_01"))
    mc.spaceLocator(name=name + side + "_foot_inner_loc_01")
    mc.delete(mc.pointConstraint(name + side + '_foot_inner_target_cc_01', name + side + "_foot_inner_loc_01"))
    mc.spaceLocator(name=name + side + "_foot_outer_loc_01")
    mc.delete(mc.pointConstraint(name + side + '_foot_outer_target_cc_01', name + side + "_foot_outer_loc_01"))
    mc.spaceLocator(name=name + side + "_foot_tip_twist_loc_01")
    mc.delete(mc.pointConstraint(name + side + '_foot_tip_target_cc_01', name + side + "_foot_tip_twist_loc_01")) 
    mc.spaceLocator(name=name + side + "_foot_ball_twist_loc_01")
    mc.delete(mc.pointConstraint(name + side + '_foot_ball_target_cc_01', name + side + "_foot_ball_twist_loc_01"))
    mc.spaceLocator(name=name + side + "_foot_heel_twist_loc_01")
    mc.delete(mc.pointConstraint(name + side + '_foot_heel_target_cc_01', name + side + "_foot_heel_twist_loc_01"))
    mc.spaceLocator(name=name + side + "_foot_ankle_connect_loc_01")
    mc.delete(mc.pointConstraint(name + side + '_foot_target_cc_01', name + side + "_foot_ankle_connect_loc_01"))
            
    # parent locators
    mc.parent(name + side + '_foot_ball_loc_01', name + side + '_foot_tip_loc_01') 
    mc.parent(name + side + '_foot_tip_loc_01', name + side + '_foot_heel_loc_01') 
    mc.parent(name + side + '_foot_heel_loc_01', name + side + '_foot_inner_loc_01') 
    mc.parent(name + side + '_foot_inner_loc_01', name + side + '_foot_outer_loc_01') 
    mc.parent(name + side + '_foot_outer_loc_01', name + side + "_foot_tip_twist_loc_01") 
    mc.parent(name + side + '_foot_tip_twist_loc_01', name + side + "_foot_ball_twist_loc_01") 
    mc.parent(name + side + "_foot_ball_twist_loc_01", name + side + "_foot_heel_twist_loc_01") 
    mc.parent(name + side + "_foot_ankle_connect_loc_01", name + side + "_foot_ball_loc_01") 
    
    #create offset group to avoid gimbal lock when parent constrained to rest of foot
    transform.make_offset_group(name + side + '_foot_heel_twist_loc_01')
    
    # Constrain scIKs to appropriate locators
    #mc.parentConstraint(name + side + '_foot_ball_loc_01', name + side + '_leg_rpIK_constrain_os_grp_01', maintainOffset=True)
    mc.parentConstraint(name + side + '_foot_ball_loc_01', name + side + '_foot_ball_scIK_01', maintainOffset=True)
    mc.parentConstraint(name + side + '_foot_tip_loc_01', name + side + '_foot_tip_scIK_01', maintainOffset=True)
    
        
    #create nodes
    mc.shadingNode('clamp', asUtility=True, name= name + side + '_foot_outer_rotation_CLAMP_01')
    mc.shadingNode('clamp', asUtility=True, name= name + side + '_foot_inner_rotation_CLAMP_01')
    mc.shadingNode('clamp', asUtility=True, name= name + side + '_foot_heel_forward_back_rotation_CLAMP_01')
    mc.shadingNode('clamp', asUtility=True, name= name + side + '_foot_tip_rotation_CLAMP_01')
    mc.shadingNode('clamp', asUtility=True, name= name + side + '_foot_ball_rotation_CLAMP_01')

    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_foot_tip_forward_back_rotation_PMA_01')
    mc.shadingNode('condition', asUtility=True, name= name + side + '_foot_ball_forward_back_rotation_COND_01')

    #set max and min values
    mc.setAttr(name + side + '_foot_outer_rotation_CLAMP_01.minR', -180.0)
    mc.setAttr(name + side + '_foot_outer_rotation_CLAMP_01.maxR', 0.0)
    mc.setAttr(name + side + '_foot_inner_rotation_CLAMP_01.minR', 0.0)
    mc.setAttr(name + side + '_foot_inner_rotation_CLAMP_01.maxR', 180.0) 
    mc.setAttr(name + side + '_foot_heel_forward_back_rotation_CLAMP_01.minR', -180.0)
    mc.setAttr(name + side + '_foot_heel_forward_back_rotation_CLAMP_01.maxR', 0.0)
    
    mc.setAttr(name + side + '_foot_tip_forward_back_rotation_PMA_01.operation', 2)
    mc.setAttr(name + side + '_foot_tip_rotation_CLAMP_01.minR', 0.0)
    mc.setAttr(name + side + '_foot_tip_rotation_CLAMP_01.maxR', 180.0) 
    mc.setAttr(name + side + '_foot_ball_rotation_CLAMP_01.minR', 0.0)
    mc.setAttr(name + side + '_foot_ball_rotation_CLAMP_01.maxR', 180.0)
    mc.setAttr(name + side + '_foot_ball_forward_back_rotation_COND_01.operation', 2)
         
        
    #connections
    mc.connectAttr(name + side + '_leg_settings_cc_01.side_to_side_parameter', name + side + '_foot_outer_rotation_CLAMP_01.input.inputR')
    mc.connectAttr(name + side + '_leg_settings_cc_01.side_to_side_parameter', name + side + '_foot_inner_rotation_CLAMP_01.input.inputR')
    mc.connectAttr(name + side + '_foot_outer_rotation_CLAMP_01.output.outputR', name + side + '_foot_outer_loc_01.rotateZ')
    mc.connectAttr(name + side + '_foot_inner_rotation_CLAMP_01.output.outputR', name + side + '_foot_inner_loc_01.rotateZ')
    mc.connectAttr(name + side + '_leg_settings_cc_01.heel_twist_parameter', name + side + '_foot_heel_twist_loc_01.rotateY')
    mc.connectAttr(name + side + '_leg_settings_cc_01.ball_twist_parameter', name + side + '_foot_ball_twist_loc_01.rotateY')
    mc.connectAttr(name + side + '_leg_settings_cc_01.toe_twist_parameter', name + side + '_foot_tip_twist_loc_01.rotateY')
    mc.connectAttr(name + side + '_leg_settings_cc_01.forward_back_parameter', name + side + '_foot_heel_forward_back_rotation_CLAMP_01.input.inputR')
    mc.connectAttr(name + side + '_foot_heel_forward_back_rotation_CLAMP_01.output.outputR', name + side + '_foot_heel_loc_01.rotateX')
    
    mc.connectAttr(name + side + '_leg_settings_cc_01.forward_back_parameter', name + side + '_foot_tip_forward_back_rotation_PMA_01.input3D[0].input3Dx')
    mc.connectAttr(name + side + '_leg_settings_cc_01.roll_break_angle_parameter', name + side + '_foot_tip_forward_back_rotation_PMA_01.input3D[1].input3Dx')
    mc.connectAttr(name + side + '_foot_tip_forward_back_rotation_PMA_01.output3Dx', name + side + '_foot_tip_rotation_CLAMP_01.inputR')
    mc.connectAttr(name + side + '_foot_tip_rotation_CLAMP_01.outputR', name + side + '_foot_tip_loc_01.rotateX')
    mc.connectAttr(name + side + '_leg_settings_cc_01.forward_back_parameter', name + side + '_foot_ball_forward_back_rotation_COND_01.firstTerm')
    mc.connectAttr(name + side + '_leg_settings_cc_01.roll_break_angle_parameter', name + side + '_foot_ball_forward_back_rotation_COND_01.secondTerm')
    mc.connectAttr(name + side + '_leg_settings_cc_01.forward_back_parameter', name + side + '_foot_ball_forward_back_rotation_COND_01.colorIfFalse.colorIfFalseR')
    mc.connectAttr(name + side + '_leg_settings_cc_01.roll_break_angle_parameter', name + side + '_foot_ball_forward_back_rotation_COND_01.colorIfTrue.colorIfTrueR')
    mc.connectAttr(name + side + '_foot_ball_forward_back_rotation_COND_01.outColor.outColorR', name + side + '_foot_ball_rotation_CLAMP_01.inputR')
    mc.connectAttr(name + side + '_foot_ball_rotation_CLAMP_01.outputR', name + side + '_foot_ball_loc_01.rotateX')
    
    
    
    if side == "_LFT":
        #FK
        
        #duplicate IK joints to make FK chain
        mc.duplicate(name + side + '_foot_ball_IK_JNT_01', renameChildren=True)
        mc.rename(name + side + '_foot_ball_IK_JNT_02', name + side + '_foot_ball_FK_JNT_01')
        mc.rename(name + side + '_foot_tip_IK_JNT_02', name + side + '_foot_tip_FK_JNT_01')
        
        #parent FK chain to appropriate bones
        mc.parent(name + side + '_foot_ball_FK_JNT_01', name + side + '_ankle_FK_JNT_01')
        
        '''
        # select parent joint
        mc.select(clear=True)
        # create FK joints for reverse foot
        mc.joint(name=name + side + '_foot_ball_FK_JNT_01', radius=.01)
    
        mc.delete(mc.parentConstraint(name + side + '_foot_ball_target_cc_01', name + side + '_foot_ball_FK_JNT_01', maintainOffset=False))
        mc.parent(name + side + '_foot_ball_FK_JNT_01', name + side + '_ankle_FK_JNT_01')
        
        
        ########################Utterly unexplainable to me is how and why Maya decides to make four joints here. Oh well. Deleting rampage in 3...2...1...
        #if side == "_RGT":
        #    mc.delete(name + side + '_foot_ball_FK_JNT_02', name + side + '_foot_ball_FK_JNT_03', name + side + '_foot_ball_FK_JNT_04')
        '''
        
    
        #Base
        
        # create base joints for reverse foot by duplicating IK chain
        mc.duplicate(name + side + '_foot_ball_IK_JNT_01', renameChildren=True)
        mc.rename(name + side + '_foot_ball_IK_JNT_02', name + side + '_foot_ball_JNT_01')
        mc.rename(name + side + '_foot_tip_IK_JNT_02', name + side + '_foot_tip_JNT_01')
        
        #parent base chain to appropriate bones
        mc.parent(name + side + '_foot_ball_JNT_01', name + side + '_ankle_JNT_01')

        '''
        # select parent joint
        mc.select(name + side + '_ankle_JNT_01', replace=True)
        # create base joints for reverse foot
        mc.joint(name=name + side + '_foot_ball_JNT_01', position = mc.xform(name + side + '_foot_ball_target_cc_01', query=True, translation=True, worldSpace=True), absolute=True, radius=.01)
        '''
    """    
    else:
        #rename foot joints already duplicated in joint chain
        mc.rename(name + side + '_foot_ball_FK_JNT_02', name + side + '_foot_ball_IK_JNT_01')
        mc.rename(name + side + '_foot_tip_FK_JNT_02', name + side + '_foot_tip_IK_JNT_01')
        mc.rename(name + side + '_foot_ball_FK_JNT_03', name + side + '_foot_ball_JNT_01')
        mc.rename(name + side + '_foot_tip_FK_JNT_03', name + side + '_foot_tip_JNT_01')
    """    

    
    #Rebuild leg connections to work with reverse foot setup (mostly consists of reconstraining stretch locators from IK control to locator on foot

    # delete old aim constraint
    mc.delete(name + side + "_upper_leg_loc_01_aimConstraint1")
    # aim constrain upper leg loc to ankle connect loc
    mc.aimConstraint( name + side + '_foot_ankle_connect_loc_01', name + side + "_upper_leg_loc_01", worldUpType="objectRotation", worldUpObject=name + '_hips_cc_01')
    
    #delete old point constraint
    mc.delete(name + side + "_IK_leg_cc_distance_loc_01_pointConstraint1" )
    #make new parent constraint
    mc.parentConstraint(name + side + '_foot_ankle_connect_loc_01', name + side + "_IK_leg_cc_distance_loc_01", maintainOffset=False )

    
    
    #delete old point constraint
    mc.delete(name + side + "_leg_soft_blend_IK_loc_01_pointConstraint1" )
    # re-point constrain soft blend locator to ankle locator and reverse ankle loc
    mc.pointConstraint(name + side + "_ankle_IK_loc_01", name + side + '_foot_ankle_connect_loc_01', name + side + "_leg_soft_blend_IK_loc_01" )
    

    # reassign connections
    mc.connectAttr(name + side + '_leg_IK_stretch_weight_RMV_01.outValue', name + side + '_leg_soft_blend_IK_loc_01_pointConstraint1.' + name + side + '_foot_ankle_connect_loc_01W1', force=True)
    mc.connectAttr(name + side + '_leg_invert_IK_stretch_weight_RMV_01.output3Dx', name + side + '_leg_soft_blend_IK_loc_01_pointConstraint1.' + name + side + '_ankle_IK_loc_01W0', force=True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # make offset group
    transform.make_offset_group(name + side + '_foot_ball_JNT_01')
    
    foot_ball_control = control.Control(
                                  prefix = name + side + '_foot_ball',
                                  scale = .010,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_foot_ball_JNT_01',
                                  rotate_to = name + side + '_foot_ball_JNT_01',
                                  parent = name + side + '_foot_controls_constrain_grp_01',
                                  shape = 'circle',
                                  locked_channels = ['visibility']
                                  )


        
    # direct connect translates, scales and rotates of foot ball cc to joint
    mc.connectAttr(name + side + '_foot_ball_cc_01.translate', name + side + '_foot_ball_JNT_01.translate')
    mc.connectAttr(name + side + '_foot_ball_cc_01.rotate', name + side + '_foot_ball_JNT_01.rotate')
    mc.connectAttr(name + side + '_foot_ball_cc_01.scale', name + side + '_foot_ball_JNT_01.scale')
    
    # make toe splaying control
    foot_cupping_control = control.Control(
                                  prefix = name + side + '_foot_splaying',
                                  scale = 0.005,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_foot_ball_JNT_01',
                                  rotate_to = name + side + '_foot_ball_JNT_01',
                                  parent = name + side + '_foot_controls_constrain_grp_01',
                                  shape = 'box',
                                  locked_channels = ['visibility','scale','translate','rotateX','rotateZ']
                                  )
    if side=="_LFT":
        x_scale = 1.0
    else:
        x_scale = -1.0
    
    mc.move(.02*x_scale,0.0,0.0, foot_cupping_control.Off, relative=True)
    mc.move(-.02*x_scale,0.0,0.0, foot_cupping_control.C + '.rotatePivot', relative=True)
    mc.move(-.02*x_scale,0.0,0.0, foot_cupping_control.C + '.scalePivot', relative=True)
    
    # constrain os group to FK and IK chains
    mc.parentConstraint(name + side + "_foot_ball_FK_JNT_01", name + side + "_foot_ball_IK_JNT_01", name + side + "_foot_ball_os_grp_01")

    # set constraint weights driven by settings control
    mc.connectAttr(name + side + '_leg_settings_cc_parent_constraint_weight_RMV_01.outValue', name + side + '_foot_ball_os_grp_01_parentConstraint1.' + name + side + '_foot_ball_IK_JNT_01W1', force=True)
    mc.connectAttr(name + side + '_leg_settings_cc_parent_constraint_inverse_weight_RMV_01.output3Dx', name + side + '_foot_ball_os_grp_01_parentConstraint1.' + name + side + '_foot_ball_FK_JNT_01W0', force=True)
    
    # parent constrain foot controls to foot ball joint os grp so it sticks with foot rolls
    mc.parentConstraint(name + side + '_foot_ball_os_grp_01', name + side + '_foot_controls_constrain_os_grp_01', maintainOffset=True)
    

    
    
    # toes
    for toe in ['big', 'index', 'middle', 'fourth', 'pinky', 'second_pinky']:

        # base of any toe
        if(mc.objExists(name + side + '_' + toe + '_toe_PRO_target_cc_01')):

            # select joint for next iteration
            mc.select(name + side + '_foot_ball_JNT_01', replace=True)
            # proximal phalange
            mc.joint(name=name + side + '_' + toe + '_toe_PRO_BN_01', radius=.005)
            mc.delete(mc.parentConstraint(name + side + '_' + toe + '_toe_PRO_target_cc_01', name + side + '_' + toe + '_toe_PRO_BN_01', maintainOffset=False))      
            parent_offset_group = transform.make_offset_group(name + side + '_' + toe + '_toe_PRO_BN_01')
            transform.make_offset_group(name + side + '_' + toe + '_toe_PRO_BN_01', prefix = name + side + '_' + toe + '_toe_PRO_JNT_cupping_control')     
            transform.make_offset_group(name + side + '_' + toe + '_toe_PRO_BN_01', prefix = name + side + '_' + toe + '_toe_PRO_JNT_primary_control_transforms')
            
            
            
            # make primary control
            current_toe_primary_control = control.Control(
                                                          prefix = name + side + '_' + toe + '_toe_primary',
                                                          scale = 0.005,
                                                          use_numerical_transforms = False,
                                                          transform_x = 0.0,
                                                          transform_y = 0.0,
                                                          transform_z = 0.0,
                                                          translate_to = name + side + '_' + toe + '_toe_PRO_BN_01',
                                                          rotate_to = name + side + '_' + toe + '_toe_PRO_BN_01',
                                                          parent = name + side + '_foot_ball_cc_01',
                                                          shape = 'square',
                                                          locked_channels = ['visibility']
                                                          )
            #add secondaries visibility attribute
            mc.addAttr( current_toe_primary_control.C, shortName='bendy_control_visibility_parameter', longName='Secondaries_Visibility', attributeType='enum', enumName='Off:On:', keyable=True) 
                        
            
            # reposition toe control
            
            if side == "_LFT":
                mc.select( name + side + '_' + toe + '_toe_primary_cc_01Shape.cv[0:4]' )
                mc.rotate(0.0,0.0,0.0, relative=True)
                mc.scale(3.0,1.0,0.5, relative=True)
                mc.move(0.0,0.007,.010, relative=True)
            else:
                mc.select( name + side + '_' + toe + '_toe_primary_cc_01Shape.cv[0:4]' )
                mc.rotate(0.0,0.0,0.0, relative=True)
                mc.scale(3.0,1.0,0.5, relative=True)
                mc.move(0.0,0.007,.010, relative=True)
             

            # make offset group for control
            transform.make_offset_group(name + side + '_' + toe + '_toe_primary_cc_01', prefix = name + side + '_' + toe + '_toe_primary_cc_cupping_control')            
            
            # make offset group and MD node to counter scaling of primary control
            transform.make_offset_group(name + side + '_' + toe + '_toe_primary_cc_01', prefix = name + side + '_' + toe + '_toe_MED_secondary_cc_primary_scale_reverse')
            mc.parent(name + side + '_' + toe + '_toe_primary_cc_01', world=True)
            mc.parent(name + side + '_' + toe + '_toe_MED_secondary_cc_primary_scale_reverse_os_grp_01', world=True)
            mc.parent(name + side + '_' + toe + '_toe_MED_secondary_cc_primary_scale_reverse_os_grp_01',name + side + '_' + toe + '_toe_primary_cc_01')
            mc.parent(name + side + '_' + toe + '_toe_primary_cc_01', name + side + '_' + toe + '_toe_primary_cc_cupping_control_os_grp_01')
            mc.shadingNode('multiplyDivide', asUtility=True, name=name + side + '_' + toe + '_toe_primary_scale_inverse_MD_01')
            mc.setAttr( name + side + '_' + toe + '_toe_primary_scale_inverse_MD_01.operation', 2)
            mc.setAttr( name + side + '_' + toe + '_toe_primary_scale_inverse_MD_01.input1X', 1.0)
            mc.connectAttr(name + side + '_' + toe + '_toe_primary_cc_01.scaleX', name + side + '_' + toe + '_toe_primary_scale_inverse_MD_01.input2X')
            mc.connectAttr(name + side + '_' + toe + '_toe_primary_scale_inverse_MD_01.outputX', name + side + '_' + toe + '_toe_MED_secondary_cc_primary_scale_reverse_os_grp_01.scaleX')
            
            # create RMV node for converting primary control's scale X to rotations for further toe joints
            mc.shadingNode('remapValue', asUtility=True, name=name + side + '_' + toe + '_toe_primary_rotate_RMV_01')
            mc.setAttr( name + side + '_' + toe + '_toe_primary_rotate_RMV_01.value[0].value_Interp', 2)
            mc.setAttr( name + side + '_' + toe + '_toe_primary_rotate_RMV_01.inputMin', 0.0)
            mc.setAttr( name + side + '_' + toe + '_toe_primary_rotate_RMV_01.inputMax', 2.0)
            mc.setAttr( name + side + '_' + toe + '_toe_primary_rotate_RMV_01.outputMin', -180.0)
            mc.setAttr( name + side + '_' + toe + '_toe_primary_rotate_RMV_01.outputMax', 180.0)
            mc.connectAttr(current_toe_primary_control.C + '.scaleX', name + side + '_' + toe + '_toe_primary_rotate_RMV_01.inputValue', force=True)
            
            # direct connect translates, scales and rotates of secondary cc to joint
            mc.connectAttr(name + side + '_' + toe + '_toe_primary_cc_01.translate', name + side + '_' + toe + '_toe_PRO_BN_01.translate')
            mc.connectAttr(name + side + '_' + toe + '_toe_primary_cc_01.rotate', name + side + '_' + toe + '_toe_PRO_BN_01.rotate')
            mc.connectAttr(name + side + '_' + toe + '_toe_primary_cc_01.scaleY', name + side + '_' + toe + '_toe_PRO_BN_01.scaleY')
            mc.connectAttr(name + side + '_' + toe + '_toe_primary_cc_01.scaleZ', name + side + '_' + toe + '_toe_PRO_BN_01.scaleZ')
            
            # select joint for next iteration
            mc.select(name + side + '_' + toe + '_toe_PRO_BN_01')

            # test if has at least two segments
            if(mc.objExists(name + side + '_' + toe + '_toe_MED_target_cc_01')):
                mc.joint(name=name + side + '_' + toe + '_toe_MED_BN_01', radius=.005)
                mc.delete(mc.parentConstraint(name + side + '_' + toe + '_toe_MED_target_cc_01', name + side + '_' + toe + '_toe_MED_BN_01', maintainOffset=False))
                transform.make_offset_group(name + side + '_' + toe + '_toe_MED_BN_01')
                transform.make_offset_group(name + side + '_' + toe + '_toe_MED_BN_01', prefix = name + side + '_' + toe + '_toe_MED_JNT_cupping_control')
                transform.make_offset_group(name + side + '_' + toe + '_toe_MED_BN_01', prefix = name + side + '_' + toe + '_toe_MED_JNT_primary_control_transforms')
                transform.make_offset_group(name + side + '_' + toe + '_toe_MED_BN_01', prefix = name + side + '_' + toe + '_toe_MED_JNT_primary_control')                
                # make secondary control 
                current_toe_MED_secondary_control = control.Control(
                                                                      prefix = name + side + '_' + toe + '_toe_MED_secondary',
                                                                      scale = 0.005,
                                                                      use_numerical_transforms = False,
                                                                      transform_x = 0.0,
                                                                      transform_y = 0.0,
                                                                      transform_z = 0.0,
                                                                      translate_to = name + side + '_' + toe + '_toe_MED_BN_01',
                                                                      rotate_to = name + side + '_' + toe + '_toe_MED_BN_01',
                                                                      parent = name + side + '_' + toe + '_toe_MED_secondary_cc_primary_scale_reverse_os_grp_01',
                                                                      shape = 'pin',
                                                                      locked_channels = []
                                                                      )
                #visibility
                mc.connectAttr(current_toe_primary_control.C + '.bendy_control_visibility_parameter', current_toe_MED_secondary_control.C + '.visibility', force=True)                
                
                # make offset groups for control
                transform.make_offset_group(name + side + '_' + toe + '_toe_MED_secondary_cc_01', prefix = name + side + '_' + toe + '_toe_MED_secondary_cc_cupping_control')
                transform.make_offset_group(name + side + '_' + toe + '_toe_MED_secondary_cc_01', prefix = name + side + '_' + toe + '_toe_MED_secondary_cc_primary_control_transforms')
                transform.make_offset_group(name + side + '_' + toe + '_toe_MED_secondary_cc_01', prefix = name + side + '_' + toe + '_toe_MED_secondary_cc_primary_control')                
                # connect primary control os grp to primary scale RMV node
                mc.connectAttr(name + side + '_' + toe + '_toe_primary_rotate_RMV_01.outValue', name + side + '_' + toe + '_toe_MED_JNT_primary_control_os_grp_01.rotateZ', force=True)
                # direct connect translates, scales and rotates of secondary cc to joint
                mc.connectAttr(name + side + '_' + toe + '_toe_MED_secondary_cc_01.translate', name + side + '_' + toe + '_toe_MED_BN_01.translate')
                mc.connectAttr(name + side + '_' + toe + '_toe_MED_secondary_cc_01.rotate', name + side + '_' + toe + '_toe_MED_BN_01.rotate')
                mc.connectAttr(name + side + '_' + toe + '_toe_MED_secondary_cc_01.scale', name + side + '_' + toe + '_toe_MED_BN_01.scale')
                # select joint for next iteration
                mc.select(name + side + '_' + toe + '_toe_MED_BN_01')
                
                
            # test if has at least three segments
            if(mc.objExists(name + side + '_' + toe + '_toe_DIS_target_cc_01')):
                mc.joint(name=name + side + '_' + toe + '_toe_DIS_BN_01', radius=.005)
                mc.delete(mc.parentConstraint(name + side + '_' + toe + '_toe_DIS_target_cc_01', name + side + '_' + toe + '_toe_DIS_BN_01', maintainOffset=False))
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_BN_01')
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_BN_01', prefix = name + side + '_' + toe + '_toe_DIS_JNT_cupping_control')
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_BN_01', prefix = name + side + '_' + toe + '_toe_DIS_JNT_primary_control_transforms')
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_BN_01', prefix = name + side + '_' + toe + '_toe_DIS_JNT_primary_control')
                
                # make secondary control
                if(mc.objExists(name + side + '_' + toe + '_toe_MED_target_cc_01')):
                    parent_control=name + side + '_' + toe + '_toe_MED_secondary_cc_01'
                else:
                    parent_control=name + side + '_' + toe + '_toe_MED_secondary_cc_primary_scale_reverse_os_grp_01'
 
                current_toe_DIS_secondary_control = control.Control(
                                                                      prefix = name + side + '_' + toe + '_toe_DIS_secondary',
                                                                      scale = 0.005,
                                                                      use_numerical_transforms = False,
                                                                      transform_x = 0.0,
                                                                      transform_y = 0.0,
                                                                      transform_z = 0.0,
                                                                      translate_to = name + side + '_' + toe + '_toe_DIS_BN_01',
                                                                      rotate_to = name + side + '_' + toe + '_toe_DIS_BN_01',
                                                                      parent = parent_control,
                                                                      shape = 'pin',
                                                                      locked_channels = []
                                                                      )
                #visibility
                mc.connectAttr(current_toe_primary_control.C + '.bendy_control_visibility_parameter', current_toe_DIS_secondary_control.C + '.visibility', force=True)                
                
                # make offset groups for control
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_secondary_cc_01', prefix = name + side + '_' + toe + '_toe_DIS_secondary_cc_cupping_control')
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_secondary_cc_01', prefix = name + side + '_' + toe + '_toe_DIS_secondary_cc_primary_control_transforms')
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_secondary_cc_01', prefix = name + side + '_' + toe + '_toe_DIS_secondary_cc_primary_control')
                # connect primary control os grp to primary scale RMV node
                mc.connectAttr(name + side + '_' + toe + '_toe_primary_rotate_RMV_01.outValue', name + side + '_' + toe + '_toe_DIS_JNT_primary_control_os_grp_01.rotateZ', force=True)
                mc.connectAttr(name + side + '_' + toe + '_toe_primary_rotate_RMV_01.outValue', name + side + '_' + toe + '_toe_DIS_secondary_cc_primary_control_os_grp_01.rotateZ', force=True)
                # direct connect translates, scales and rotates of secondary cc to joint
                mc.connectAttr(name + side + '_' + toe + '_toe_DIS_secondary_cc_01.translate', name + side + '_' + toe + '_toe_DIS_BN_01.translate')
                mc.connectAttr(name + side + '_' + toe + '_toe_DIS_secondary_cc_01.rotate', name + side + '_' + toe + '_toe_DIS_BN_01.rotate')
                mc.connectAttr(name + side + '_' + toe + '_toe_DIS_secondary_cc_01.scale', name + side + '_' + toe + '_toe_DIS_BN_01.scale')
                # select joint for next iteration
                mc.select(name + side + '_' + toe + '_toe_DIS_BN_01')

            # test if has at least four segments
            if(mc.objExists(name + side + '_' + toe + '_toe_DIS_2_target_cc_01')):
                mc.joint(name=name + side + '_' + toe + '_toe_DIS_2_BN_01', radius=.005)
                mc.delete(mc.parentConstraint(name + side + '_' + toe + '_toe_DIS_2_target_cc_01', name + side + '_' + toe + '_toe_DIS_2_BN_01', maintainOffset=False))
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_2_BN_01')
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_2_BN_01', prefix = name + side + '_' + toe + '_toe_DIS_2_JNT_cupping_control')
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_2_BN_01', prefix = name + side + '_' + toe + '_toe_DIS_2_JNT_primary_control_transforms')
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_2_BN_01', prefix = name + side + '_' + toe + '_toe_DIS_2_JNT_primary_control')
                # make secondary control 
                current_toe_DIS_2_secondary_control = control.Control(
                                                                      prefix = name + side + '_' + toe + '_toe_DIS_2_secondary',
                                                                      scale = 0.005,
                                                                      use_numerical_transforms = False,
                                                                      transform_x = 0.0,
                                                                      transform_y = 0.0,
                                                                      transform_z = 0.0,
                                                                      translate_to = name + side + '_' + toe + '_toe_DIS_2_BN_01',
                                                                      rotate_to = name + side + '_' + toe + '_toe_DIS_2_BN_01',
                                                                      parent = current_toe_DIS_secondary_control.C,
                                                                      shape = 'pin',
                                                                      locked_channels = []
                                                                      )
                #visibility
                mc.connectAttr(current_toe_primary_control.C + '.bendy_control_visibility_parameter', current_toe_DIS_2_secondary_control.C + '.visibility', force=True)                
                                
                # make offset groups for control
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_2_secondary_cc_01', prefix = name + side + '_' + toe + '_toe_DIS_2_secondary_cc_cupping_control')
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_2_secondary_cc_01', prefix = name + side + '_' + toe + '_toe_DIS_2_secondary_cc_primary_control_transforms')
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_2_secondary_cc_01', prefix = name + side + '_' + toe + '_toe_DIS_2_secondary_cc_primary_control')
                # connect primary control os grp to primary scale RMV node
                mc.connectAttr(name + side + '_' + toe + '_toe_primary_rotate_RMV_01.outValue', name + side + '_' + toe + '_toe_DIS_2_JNT_primary_control_os_grp_01.rotateZ', force=True)
                mc.connectAttr(name + side + '_' + toe + '_toe_primary_rotate_RMV_01.outValue', name + side + '_' + toe + '_toe_DIS_2_secondary_cc_primary_control_os_grp_01.rotateZ', force=True)
                # direct connect translates, scales and rotates of secondary cc to joint
                mc.connectAttr(name + side + '_' + toe + '_toe_DIS_2_secondary_cc_01.translate', name + side + '_' + toe + '_toe_DIS_2_BN_01.translate')
                mc.connectAttr(name + side + '_' + toe + '_toe_DIS_2_secondary_cc_01.rotate', name + side + '_' + toe + '_toe_DIS_2_BN_01.rotate')
                mc.connectAttr(name + side + '_' + toe + '_toe_DIS_2_secondary_cc_01.scale', name + side + '_' + toe + '_toe_DIS_2_BN_01.scale')
                # select joint for next iteration
                mc.select(name + side + '_' + toe + '_toe_DIS_2_BN_01')

            # test if has at least five segments
            if(mc.objExists(name + side + '_' + toe + '_toe_DIS_3_target_cc_01')):
                mc.joint(name=name + side + '_' + toe + '_toe_DIS_3_BN_01', radius=.005)
                mc.delete(mc.parentConstraint(name + side + '_' + toe + '_toe_DIS_3_target_cc_01', name + side + '_' + toe + '_toe_DIS_3_BN_01', maintainOffset=False))
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_3_BN_01')
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_3_BN_01', prefix = name + side + '_' + toe + '_toe_DIS_3_JNT_cupping_control')
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_3_BN_01', prefix = name + side + '_' + toe + '_toe_DIS_3_JNT_primary_control_transforms')
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_3_BN_01', prefix = name + side + '_' + toe + '_toe_DIS_3_JNT_primary_control')
                # make secondary control 
                current_toe_DIS_3_secondary_control = control.Control(
                                                                      prefix = name + side + '_' + toe + '_toe_DIS_3_secondary',
                                                                      scale = 0.005,
                                                                      use_numerical_transforms = False,
                                                                      transform_x = 0.0,
                                                                      transform_y = 0.0,
                                                                      transform_z = 0.0,
                                                                      translate_to = name + side + '_' + toe + '_toe_DIS_3_BN_01',
                                                                      rotate_to = name + side + '_' + toe + '_toe_DIS_3_BN_01',
                                                                      parent = current_toe_DIS_2_secondary_control.C,
                                                                      shape = 'pin',
                                                                      locked_channels = []
                                                                      )
                #visibility
                mc.connectAttr(current_toe_primary_control.C + '.bendy_control_visibility_parameter', current_toe_DIS_3_secondary_control.C + '.visibility', force=True)                
                                
                # make offset groups for control
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_3_secondary_cc_01', prefix = name + side + '_' + toe + '_toe_DIS_3_secondary_cc_cupping_control')
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_3_secondary_cc_01', prefix = name + side + '_' + toe + '_toe_DIS_3_secondary_cc_primary_control_transforms')
                transform.make_offset_group(name + side + '_' + toe + '_toe_DIS_3_secondary_cc_01', prefix = name + side + '_' + toe + '_toe_DIS_3_secondary_cc_primary_control') 
                # connect primary control os grp to primary scale RMV node
                mc.connectAttr(name + side + '_' + toe + '_toe_primary_rotate_RMV_01.outValue', name + side + '_' + toe + '_toe_DIS_3_JNT_primary_control_os_grp_01.rotateZ', force=True)
                mc.connectAttr(name + side + '_' + toe + '_toe_primary_rotate_RMV_01.outValue', name + side + '_' + toe + '_toe_DIS_3_secondary_cc_primary_control_os_grp_01.rotateZ', force=True)  
                # direct connect translates, scales and rotates of secondary cc to joint
                mc.connectAttr(name + side + '_' + toe + '_toe_DIS_3_secondary_cc_01.translate', name + side + '_' + toe + '_toe_DIS_3_BN_01.translate')
                mc.connectAttr(name + side + '_' + toe + '_toe_DIS_3_secondary_cc_01.rotate', name + side + '_' + toe + '_toe_DIS_3_BN_01.rotate')
                mc.connectAttr(name + side + '_' + toe + '_toe_DIS_3_secondary_cc_01.scale', name + side + '_' + toe + '_toe_DIS_3_BN_01.scale')
                # select joint for next iteration
                mc.select(name + side + '_' + toe + '_toe_DIS_3_BN_01')
                            
            mc.joint(name=name + side + '_' + toe + '_toe_JNT_END_01', radius=.005)
            mc.delete(mc.pointConstraint(name + side + '_' + toe + '_toe_END_target_cc_01', name + side + '_' + toe + '_toe_JNT_END_01', maintainOffset=False))        
            mc.joint( name + side + '_' + toe + '_toe_PRO_BN_01', edit=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient = 'yup', children=True )
            mc.setAttr( name + side + '_' + toe + '_toe_JNT_END_01.jointOrientX', 0)
            # parent all to foot GRP
            mc.parent(name + side + '_' + toe + '_toe_primary_cc_os_grp_01', world = True)
            mc.parent(name + side + '_' + toe + '_toe_primary_cc_os_grp_01', name + side + '_foot_ball_cc_01')
    
             
    hip_PSR = pose_space_reader.PoseSpaceReader(
                                                   prefix = name + side,
                                                   scale = .010,
                                                   base_object = name + side + "_upper_leg_JNT_01",
                                                   tracker_object = name + side + "_lower_leg_JNT_01",
                                                   base_name = 'hip',
                                                   tracker_name = 'knee',
                                                   target_names = ['up', 'down', 'forward', 'back'],
                                                   parent = '',
                                                )



    
    
    """
    bendy leg setup
    """
    
    #
    # read in variables
    number_of_upper_leg_joints = mc.intField( "number_of_upper_leg_spans", query = True, value=True )
    number_of_lower_leg_joints = mc.intField( "number_of_lower_leg_spans", query = True, value=True )

    upp_leg_length=mc.getAttr(name + side + '_lower_leg_JNT_01.translateX')
    low_leg_length=mc.getAttr(name + side + '_ankle_JNT_01.translateX')
    
    
    
    #
    # create bendy_JNT control joints
    bendy_control_joints_offset_group=mc.group(empty=True, name=name + side + '_leg_bendy_control_JNT_GRP_01')

    mc.duplicate(name + side + '_upper_leg_JNT_01', parentOnly=True, name=name + side + '_hip_bendy_JNT_01')
    transform.make_offset_group(name + side + '_hip_bendy_JNT_01', prefix=name + side + '_hip_bendy_JNT')
    mc.parent(name + side + '_hip_bendy_JNT_os_grp_01', name + side + '_leg_bendy_control_JNT_GRP_01')

    mc.duplicate(name + side + '_upper_leg_JNT_01', parentOnly=True, name=name + side + '_upper_leg_bendy_JNT_01')
    mc.move(upp_leg_length/2.0,0,0, name + side + '_upper_leg_bendy_JNT_01', objectSpace=True, relative=True)
    transform.make_offset_group(name + side + '_upper_leg_bendy_JNT_01', prefix=name + side + '_upper_leg_bendy_JNT')
    mc.parent(name + side + '_upper_leg_bendy_JNT_os_grp_01', name + side + '_leg_bendy_control_JNT_GRP_01')
    
    mc.duplicate(name + side + '_lower_leg_JNT_01', parentOnly=True, name=name + side + '_knee_bendy_JNT_01')
    transform.make_offset_group(name + side + '_knee_bendy_JNT_01', prefix=name + side + '_knee_bendy_JNT')
    mc.parent(name + side + '_knee_bendy_JNT_os_grp_01', name + side + '_leg_bendy_control_JNT_GRP_01')

    mc.duplicate(name + side + '_lower_leg_JNT_01', parentOnly=True, name=name + side + '_lower_leg_bendy_JNT_01')
    mc.move(low_leg_length/2.0,0,0, name + side + '_lower_leg_bendy_JNT_01', objectSpace=True, relative=True)
    transform.make_offset_group(name + side + '_lower_leg_bendy_JNT_01', prefix=name + side + '_lower_leg_bendy_JNT')
    mc.parent(name + side + '_lower_leg_bendy_JNT_os_grp_01', name + side + '_leg_bendy_control_JNT_GRP_01')

    mc.duplicate(name + side + '_ankle_JNT_01', parentOnly=True, name=name + side + '_ankle_bendy_JNT_01')
    #reorient ankle bendy joint
    mc.delete(mc.orientConstraint(name + side + '_lower_leg_JNT_01', name + side + '_ankle_bendy_JNT_01', maintainOffset=False))
    transform.make_offset_group(name + side + '_ankle_bendy_JNT_01', prefix=name + side + '_ankle_bendy_JNT')
    mc.parent(name + side + '_ankle_bendy_JNT_os_grp_01', name + side + '_leg_bendy_control_JNT_GRP_01')

    
    #create tangent bendy_JNT control joints
    mc.duplicate(name + side + '_hip_bendy_JNT_01', parentOnly=True, name=name + side + '_hip_bendy_low_tangent_JNT_01')
    transform.make_offset_group(name + side + '_hip_bendy_low_tangent_JNT_01', prefix=name + side + '_hip_bendy_low_tangent_JNT')
    mc.parent(name + side + '_hip_bendy_low_tangent_JNT_os_grp_01', name + side + '_hip_bendy_JNT_01')
    
    mc.duplicate(name + side + '_upper_leg_bendy_JNT_01', parentOnly=True, name=name + side + '_upper_leg_bendy_upp_tangent_JNT_01')
    transform.make_offset_group(name + side + '_upper_leg_bendy_upp_tangent_JNT_01', prefix=name + side + '_upper_leg_bendy_upp_tangent_JNT')
    mc.parent(name + side + '_upper_leg_bendy_upp_tangent_JNT_os_grp_01', name + side + '_upper_leg_bendy_JNT_01')
    mc.duplicate(name + side + '_upper_leg_bendy_JNT_01', parentOnly=True, name=name + side + '_upper_leg_bendy_low_tangent_JNT_01')
    transform.make_offset_group(name + side + '_upper_leg_bendy_low_tangent_JNT_01', prefix=name + side + '_upper_leg_bendy_low_tangent_JNT')
    mc.parent(name + side + '_upper_leg_bendy_low_tangent_JNT_os_grp_01', name + side + '_upper_leg_bendy_JNT_01')
        
    mc.duplicate(name + side + '_knee_bendy_JNT_01', parentOnly=True, name=name + side + '_knee_bendy_upp_tangent_JNT_01')
    transform.make_offset_group(name + side + '_knee_bendy_upp_tangent_JNT_01', prefix=name + side + '_knee_bendy_upp_tangent_JNT')
    mc.parent(name + side + '_knee_bendy_upp_tangent_JNT_os_grp_01', name + side + '_knee_bendy_JNT_01')
    mc.duplicate(name + side + '_knee_bendy_JNT_01', parentOnly=True, name=name + side + '_knee_bendy_low_tangent_JNT_01')
    transform.make_offset_group(name + side + '_knee_bendy_low_tangent_JNT_01', prefix=name + side + '_knee_bendy_low_tangent_JNT')
    mc.parent(name + side + '_knee_bendy_low_tangent_JNT_os_grp_01', name + side + '_knee_bendy_JNT_01')

    mc.duplicate(name + side + '_lower_leg_bendy_JNT_01', parentOnly=True, name=name + side + '_lower_leg_bendy_upp_tangent_JNT_01')
    transform.make_offset_group(name + side + '_lower_leg_bendy_upp_tangent_JNT_01', prefix=name + side + '_lower_leg_bendy_upp_tangent_JNT')
    mc.parent(name + side + '_lower_leg_bendy_upp_tangent_JNT_os_grp_01', name + side + '_lower_leg_bendy_JNT_01')
    mc.duplicate(name + side + '_lower_leg_bendy_JNT_01', parentOnly=True, name=name + side + '_lower_leg_bendy_low_tangent_JNT_01')
    transform.make_offset_group(name + side + '_lower_leg_bendy_low_tangent_JNT_01', prefix=name + side + '_lower_leg_bendy_low_tangent_JNT')
    mc.parent(name + side + '_lower_leg_bendy_low_tangent_JNT_os_grp_01', name + side + '_lower_leg_bendy_JNT_01')

    mc.duplicate(name + side + '_ankle_bendy_JNT_01', parentOnly=True, name=name + side + '_ankle_bendy_upp_tangent_JNT_01')
    transform.make_offset_group(name + side + '_ankle_bendy_upp_tangent_JNT_01', prefix=name + side + '_ankle_bendy_upp_tangent_JNT')
    mc.parent(name + side + '_ankle_bendy_upp_tangent_JNT_os_grp_01', name + side + '_ankle_bendy_JNT_01')
    
    
    #
    # create Bendy control curves
    
    #Primaries
    bendy_hip_control = control.Control(
                                  prefix = name + side + '_hip_bendy',
                                  scale = .090,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_hip_bendy_JNT_01',
                                  rotate_to = name + side + '_hip_bendy_JNT_01',
                                  parent = name + '_secondary_global_cc_01',
                                  shape = 'circle',
                                  locked_channels = ['scale']
                                  )
    
    bendy_upper_leg_control = control.Control(
                                  prefix = name + side + '_upper_leg_bendy',
                                  scale = .090,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_upper_leg_bendy_JNT_01',
                                  rotate_to = name + side + '_upper_leg_bendy_JNT_01',
                                  parent = name + '_secondary_global_cc_01',
                                  shape = 'circle',
                                  locked_channels = ['scale']
                                  )
    
    bendy_knee_control = control.Control(
                                  prefix = name + side + '_knee_bendy',
                                  scale = .090,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_knee_bendy_JNT_01',
                                  rotate_to = name + side + '_knee_bendy_JNT_01',
                                  parent = name + '_secondary_global_cc_01',
                                  shape = 'circle',
                                  locked_channels = ['scale']
                                  )
        
    bendy_lower_leg_control = control.Control(
                                  prefix = name + side + '_lower_leg_bendy',
                                  scale = .090,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_lower_leg_bendy_JNT_01',
                                  rotate_to = name + side + '_lower_leg_bendy_JNT_01',
                                  parent = name + '_secondary_global_cc_01',
                                  shape = 'circle',
                                  locked_channels = ['scale']
                                  )
    
    bendy_ankle_control = control.Control(
                                  prefix = name + side + '_ankle_bendy',
                                  scale = .090,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_ankle_bendy_JNT_01',
                                  rotate_to = name + side + '_ankle_bendy_JNT_01',
                                  parent = name + '_secondary_global_cc_01',
                                  shape = 'circle',
                                  locked_channels = ['scale']
                                  )

    
    
    #Tangents
    hip_bendy_low_tangent_control = control.Control(
                                  prefix = name + side + '_hip_bendy_low_tangent',
                                  scale = .070,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_hip_bendy_low_tangent_JNT_01',
                                  rotate_to = name + side + '_hip_bendy_low_tangent_JNT_01',
                                  parent = name + side + '_hip_bendy_cc_01',
                                  shape = 'diamond',
                                  locked_channels = ['scale']
                                  )
    
    upper_leg_bendy_upp_tangent_control = control.Control(
                                  prefix = name + side + '_upper_leg_bendy_upp_tangent',
                                  scale = .070,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_upper_leg_bendy_upp_tangent_JNT_01',
                                  rotate_to = name + side + '_upper_leg_bendy_upp_tangent_JNT_01',
                                  parent = name + side + '_upper_leg_bendy_cc_01',
                                  shape = 'diamond',
                                  locked_channels = ['scale']
                                  )
    
    upper_leg_bendy_low_tangent_control = control.Control(
                                  prefix = name + side + '_upper_leg_bendy_low_tangent',
                                  scale = .070,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_upper_leg_bendy_low_tangent_JNT_01',
                                  rotate_to = name + side + '_upper_leg_bendy_low_tangent_JNT_01',
                                  parent = name + side + '_upper_leg_bendy_cc_01',
                                  shape = 'diamond',
                                  locked_channels = ['scale']
                                  )    
    
    knee_bendy_upp_tangent_control = control.Control(
                                  prefix = name + side + '_knee_bendy_upp_tangent',
                                  scale = .070,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_knee_bendy_upp_tangent_JNT_01',
                                  rotate_to = name + side + '_knee_bendy_upp_tangent_JNT_01',
                                  parent = name + side + '_knee_bendy_cc_01',
                                  shape = 'diamond',
                                  locked_channels = ['scale']
                                  )
    
    knee_bendy_low_tangent_control = control.Control(
                                  prefix = name + side + '_knee_bendy_low_tangent',
                                  scale = .070,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_knee_bendy_low_tangent_JNT_01',
                                  rotate_to = name + side + '_knee_bendy_low_tangent_JNT_01',
                                  parent = name + side + '_knee_bendy_cc_01',
                                  shape = 'diamond',
                                  locked_channels = ['scale']
                                  )    
        
    lower_leg_bendy_upp_tangent_control = control.Control(
                                  prefix = name + side + '_lower_leg_bendy_upp_tangent',
                                  scale = .070,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_lower_leg_bendy_upp_tangent_JNT_01',
                                  rotate_to = name + side + '_lower_leg_bendy_upp_tangent_JNT_01',
                                  parent = name + side + '_lower_leg_bendy_cc_01',
                                  shape = 'diamond',
                                  locked_channels = ['scale']
                                  )
    
    lower_leg_bendy_low_tangent_control = control.Control(
                                  prefix = name + side + '_lower_leg_bendy_low_tangent',
                                  scale = .070,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_lower_leg_bendy_low_tangent_JNT_01',
                                  rotate_to = name + side + '_lower_leg_bendy_low_tangent_JNT_01',
                                  parent = name + side + '_lower_leg_bendy_cc_01',
                                  shape = 'diamond',
                                  locked_channels = ['scale']
                                  )    
    
    ankle_bendy_upp_tangent_control = control.Control(
                                  prefix = name + side + '_ankle_bendy_upp_tangent',
                                  scale = .070,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_ankle_bendy_upp_tangent_JNT_01',
                                  rotate_to = name + side + '_ankle_bendy_upp_tangent_JNT_01',
                                  parent = name + side + '_ankle_bendy_cc_01',
                                  shape = 'diamond',
                                  locked_channels = ['scale']
                                  )
    
    #Group bendy_curve control_joints
    bendy_control_ccs_offset_group = [name + side + '_hip_bendy_cc_os_grp_01', 
                              name + side + '_upper_leg_bendy_cc_os_grp_01',
                              name + side + '_knee_bendy_cc_os_grp_01',
                              name + side + '_lower_leg_bendy_cc_os_grp_01',
                              name + side + '_ankle_bendy_cc_os_grp_01']
    mc.group(name=name + side + '_leg_bendy_controls_GRP_01', empty=True)
    mc.parent(bendy_control_ccs_offset_group, name + side + '_leg_bendy_controls_GRP_01')
    
    

    #
    # connect tangent offset distances to custom noodle attr on primary bendy controls 
    
    # determine good default value for noodle attr
    noodle_default=abs(upp_leg_length+low_leg_length)/20
    
    
    
    #################FIX TWITCHING on arms and legs - not on Grendel, could be scale issue? Doesn't scale as is anyways, gotta fix.
    
    
    
    
    
    # create custom noodle attribute and its utility inverse
    for part in ['_hip_bendy_cc', '_upper_leg_bendy_cc', '_knee_bendy_cc', '_lower_leg_bendy_cc', '_ankle_bendy_cc']:
        mc.addAttr(name + side + part + '_01', shortName='noodle_parameter', longName='Noodle', attributeType='float', defaultValue=noodle_default, minValue=0.0, maxValue=1.0, keyable=True)
        mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + part + '_noodle_parameter_inverse_01')
        mc.connectAttr( name + side + part + '_01.noodle_parameter', name + side + part + '_noodle_parameter_inverse_01.input1X', force=True)         
        mc.setAttr( name + side + part + '_noodle_parameter_inverse_01.input2X', -1.0)         

    #connections
    if side == '_LFT':

        mc.connectAttr(name + side + '_hip_bendy_cc_01.noodle_parameter', name + side + '_hip_bendy_low_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_upper_leg_bendy_cc_01.noodle_parameter', name + side + '_upper_leg_bendy_low_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_knee_bendy_cc_01.noodle_parameter', name + side + '_knee_bendy_low_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_lower_leg_bendy_cc_01.noodle_parameter', name + side + '_lower_leg_bendy_low_tangent_JNT_os_grp_01.translateX', force=True)
            
        mc.connectAttr(name + side + '_hip_bendy_cc_01.noodle_parameter', name + side + '_hip_bendy_low_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_upper_leg_bendy_cc_01.noodle_parameter', name + side + '_upper_leg_bendy_low_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_knee_bendy_cc_01.noodle_parameter', name + side + '_knee_bendy_low_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_lower_leg_bendy_cc_01.noodle_parameter', name + side + '_lower_leg_bendy_low_tangent_cc_os_grp_01.translateX', force=True)
        
        mc.connectAttr(name + side + '_upper_leg_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_upper_leg_bendy_upp_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_knee_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_knee_bendy_upp_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_lower_leg_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_lower_leg_bendy_upp_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_ankle_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_ankle_bendy_upp_tangent_JNT_os_grp_01.translateX', force=True)
    
        mc.connectAttr(name + side + '_upper_leg_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_upper_leg_bendy_upp_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_knee_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_knee_bendy_upp_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_lower_leg_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_lower_leg_bendy_upp_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_ankle_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_ankle_bendy_upp_tangent_cc_os_grp_01.translateX', force=True)
    
    else:

        mc.connectAttr(name + side + '_hip_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_hip_bendy_low_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_upper_leg_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_upper_leg_bendy_low_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_knee_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_knee_bendy_low_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_lower_leg_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_lower_leg_bendy_low_tangent_JNT_os_grp_01.translateX', force=True)
            
        mc.connectAttr(name + side + '_hip_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_hip_bendy_low_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_upper_leg_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_upper_leg_bendy_low_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_knee_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_knee_bendy_low_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_lower_leg_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_lower_leg_bendy_low_tangent_cc_os_grp_01.translateX', force=True)
        
        mc.connectAttr(name + side + '_upper_leg_bendy_cc_01.noodle_parameter', name + side + '_upper_leg_bendy_upp_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_knee_bendy_cc_01.noodle_parameter', name + side + '_knee_bendy_upp_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_lower_leg_bendy_cc_01.noodle_parameter', name + side + '_lower_leg_bendy_upp_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_ankle_bendy_cc_01.noodle_parameter', name + side + '_ankle_bendy_upp_tangent_JNT_os_grp_01.translateX', force=True)
    
        mc.connectAttr(name + side + '_upper_leg_bendy_cc_01.noodle_parameter', name + side + '_upper_leg_bendy_upp_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_knee_bendy_cc_01.noodle_parameter', name + side + '_knee_bendy_upp_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_lower_leg_bendy_cc_01.noodle_parameter', name + side + '_lower_leg_bendy_upp_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_ankle_bendy_cc_01.noodle_parameter', name + side + '_ankle_bendy_upp_tangent_cc_os_grp_01.translateX', force=True)
         
    
    #
    # connect bendy control curve
    
    # List of joints that will be used to create CVs for flexi plane and then be bound to said CVs
    curve_cv_control_joints = [name + side + '_hip_bendy_JNT_01', 
                              name + side + '_hip_bendy_low_tangent_JNT_01',
                              name + side + '_upper_leg_bendy_upp_tangent_JNT_01',
                              name + side + '_upper_leg_bendy_JNT_01',
                              name + side + '_upper_leg_bendy_low_tangent_JNT_01',
                              name + side + '_knee_bendy_upp_tangent_JNT_01',
                              name + side + '_knee_bendy_JNT_01',
                              name + side + '_knee_bendy_low_tangent_JNT_01',
                              name + side + '_lower_leg_bendy_upp_tangent_JNT_01',
                              name + side + '_lower_leg_bendy_JNT_01',
                              name + side + '_lower_leg_bendy_low_tangent_JNT_01',
                              name + side + '_ankle_bendy_upp_tangent_JNT_01',
                              name + side + '_ankle_bendy_JNT_01']
    
    # List of joints that will be used to create CVs for pointer ikSpline curve and then be bound to said CVs
    curve_cv_primary_control_joints = [name + side + '_hip_bendy_JNT_01', 
                                      name + side + '_upper_leg_bendy_JNT_01',
                                      name + side + '_knee_bendy_JNT_01',
                                      name + side + '_lower_leg_bendy_JNT_01',
                                      name + side + '_ankle_bendy_JNT_01']
    
    # List of controls that will drive the curve_cv_control_joints  
    curve_cv_control_ccs = [name + side + '_hip_bendy_cc_01', 
                          name + side + '_hip_bendy_low_tangent_cc_01',
                          name + side + '_upper_leg_bendy_upp_tangent_cc_01',
                          name + side + '_upper_leg_bendy_cc_01',
                          name + side + '_upper_leg_bendy_low_tangent_cc_01',
                          name + side + '_knee_bendy_upp_tangent_cc_01',
                          name + side + '_knee_bendy_cc_01',
                          name + side + '_knee_bendy_low_tangent_cc_01',
                          name + side + '_lower_leg_bendy_upp_tangent_cc_01',
                          name + side + '_lower_leg_bendy_cc_01',
                          name + side + '_lower_leg_bendy_low_tangent_cc_01',
                          name + side + '_ankle_bendy_upp_tangent_cc_01',
                          name + side + '_ankle_bendy_cc_01']

    # List of controls that will be drive the curve_cv_primary_control joints
    curve_cv_primary_control_controls = [name + side + '_hip_bendy_cc_01', 
                                      name + side + '_upper_leg_bendy_cc_01',
                                      name + side + '_knee_bendy_cc_01',
                                      name + side + '_lower_leg_bendy_cc_01',
                                      name + side + '_ankle_bendy_cc_01']
    
    
    #Add os_grp for rotations to all primary bendy controls and joints
    transform.make_offset_group(name + side + '_hip_bendy_JNT_01', prefix=name + side + "_hip_bendy_JNT_rotation")
    transform.make_offset_group(name + side + '_upper_leg_bendy_JNT_01', prefix=name + side + "_upper_leg_bendy_JNT_rotation")
    transform.make_offset_group(name + side + '_knee_bendy_JNT_01', prefix=name + side + "_knee_bendy_JNT_rotation")
    transform.make_offset_group(name + side + '_lower_leg_bendy_JNT_01', prefix=name + side + "_lower_leg_bendy_JNT_rotation")
    transform.make_offset_group(name + side + '_ankle_bendy_JNT_01', prefix=name + side + "_ankle_bendy_JNT_rotation")

    transform.make_offset_group(name + side + '_hip_bendy_cc_01', prefix=name + side + "_hip_bendy_cc_rotation")
    transform.make_offset_group(name + side + '_upper_leg_bendy_cc_01', prefix=name + side + "_upper_leg_bendy_cc_rotation")
    transform.make_offset_group(name + side + '_knee_bendy_cc_01', prefix=name + side + "_knee_bendy_cc_rotation")
    transform.make_offset_group(name + side + '_lower_leg_bendy_cc_01', prefix=name + side + "_lower_leg_bendy_cc_rotation")
    transform.make_offset_group(name + side + '_ankle_bendy_cc_01', prefix=name + side + "_ankle_bendy_cc_rotation")
       


    #
    # Connect cc's to joints
    for cc, jnt in zip(curve_cv_control_ccs, curve_cv_control_joints):
        for attr in ['.tx','.ty','.tz','.rx','.ry','.rz','.sx','.sy','.sz']:
            mc.connectAttr(cc + attr, jnt + attr, force=True)



    #
    # create bendy joints (these will serve as a base for the bones that actually bind to the mesh)
    
    bendy_joints_offset_group=mc.group(empty=True, name=name + side + '_leg_bendy_JNT_GRP_01')
        
    mc.select(name + side + '_leg_bendy_JNT_GRP_01')
    for num in range(1, number_of_upper_leg_joints+number_of_lower_leg_joints+1):
        # create upper_leg bendy JNTs
        if num <= number_of_upper_leg_joints:
            mc.joint(name=name + side + '_leg_bendy_'+str(num)+'_JNT_01', position = mc.xform(name + side + '_upper_leg_stretchy_target_'+str(num)+'_cc_01', query=True, translation=True, worldSpace=True), absolute=True, radius=0.005)
        else:
            mc.joint(name=name + side + '_leg_bendy_'+str(num)+'_JNT_01', position = mc.xform(name + side + '_lower_leg_stretchy_target_'+str(num-number_of_upper_leg_joints)+'_cc_01', query=True, translation=True, worldSpace=True), absolute=True, radius=0.005)
    #reorient chain
    mc.joint(name + side + '_leg_bendy_1_JNT_01', edit=True, zeroScaleOrient=True, orientJoint='xzy', secondaryAxisOrient = 'yup', children=True )
    #align last joint
    for attr in ['jointOrientX','jointOrientY','jointOrientZ']:
        mc.setAttr(name + side + '_leg_bendy_'+str(number_of_upper_leg_joints+number_of_lower_leg_joints)+'_JNT_01.'+attr, 0)


    #
    # create bendy pointer joints (these will control the x rotations of the bendy bones)
    
    bendy_pointer_joints_offset_group=mc.group(empty=True, name=name + side + '_leg_bendy_pointer_JNT_GRP_01')
        
    mc.select(name + side + '_leg_bendy_pointer_JNT_GRP_01')
    for num in range(1, number_of_upper_leg_joints+number_of_lower_leg_joints+1):
        # create upper_leg bendy JNTs
        if num <= number_of_upper_leg_joints:
            mc.joint(name=name + side + '_leg_bendy_pointer_'+str(num)+'_JNT_01', position = mc.xform(name + side + '_upper_leg_stretchy_target_'+str(num)+'_cc_01', query=True, translation=True, worldSpace=True), absolute=True, radius=0.005)
        else:
            mc.joint(name=name + side + '_leg_bendy_pointer_'+str(num)+'_JNT_01', position = mc.xform(name + side + '_lower_leg_stretchy_target_'+str(num-number_of_upper_leg_joints)+'_cc_01', query=True, translation=True, worldSpace=True), absolute=True, radius=0.005)
    #reorient chain
    mc.joint(name + side + '_leg_bendy_pointer_1_JNT_01', edit=True, zeroScaleOrient=True, orientJoint='xzy', secondaryAxisOrient = 'yup', children=True )
    #align last joint
    for attr in ['jointOrientX','jointOrientY','jointOrientZ']:
        mc.setAttr(name + side + '_leg_bendy_pointer_'+str(number_of_upper_leg_joints+number_of_lower_leg_joints)+'_JNT_01.'+attr, 0)


    #
    # create bendy bones (these will be the bones that actually bind to the mesh)
    bendy_bones_offset_group=mc.group(empty=True, name=name + side + '_leg_bendy_BN_GRP_01')
        
    mc.select(name + side + '_leg_bendy_BN_GRP_01')
    for num in range(1, number_of_upper_leg_joints+number_of_lower_leg_joints+1):
        mc.select(name + side + '_leg_bendy_BN_GRP_01')
        # create upper_leg bendy BNs
        if num <= number_of_upper_leg_joints:
            mc.joint(name=name + side + '_leg_bendy_'+str(num)+'_BN_01', position = mc.xform(name + side + '_upper_leg_stretchy_target_'+str(num)+'_cc_01', query=True, translation=True, worldSpace=True), absolute=True, radius=0.005)
        else:
            mc.joint(name=name + side + '_leg_bendy_'+str(num)+'_BN_01', position = mc.xform(name + side + '_lower_leg_stretchy_target_'+str(num-number_of_upper_leg_joints)+'_cc_01', query=True, translation=True, worldSpace=True), absolute=True, radius=0.005)
    #reorient chain
    mc.joint(name + side + '_leg_bendy_1_BN_01', edit=True, zeroScaleOrient=True, orientJoint='xzy', secondaryAxisOrient = 'yup', children=True )
    #align last joint
    for attr in ['jointOrientX','jointOrientY','jointOrientZ']:
        mc.setAttr(name + side + '_leg_bendy_'+str(number_of_upper_leg_joints+number_of_lower_leg_joints)+'_BN_01.'+attr, 0)







    #
    # Create IK spline for bendy leg joints
                                                          
    # will contain positions in space of all joints 
    cv_world_positions=[]
    for joint in curve_cv_control_joints:
        cur_cv_position = mc.pointPosition( joint + '.rotatePivot' )
        cv_world_positions.append( cur_cv_position )
    
    #Create curves with CVs at proper positions to generate curve
    temp_name = mc.curve( d=3, p=cv_world_positions) 
    mc.rename(temp_name, name + side + '_leg_splineIK_curve_01') 

    #Bind bendy_JNT joints to curve and adjust weights
    mc.skinCluster(curve_cv_control_joints, name + side + '_leg_splineIK_curve_01', name=name + side + '_leg_splineIK_curve_scls_01')
    for joint in curve_cv_control_joints:
        mc.skinPercent(name + side + '_leg_splineIK_curve_scls_01', name + side + '_leg_splineIK_curve_01.cv['+str(curve_cv_control_joints.index(joint))+']', transformValue=[(joint, 1.0)])
 
    mc.ikHandle(name=name + side + '_leg_splineIK_handle_01', solver="ikSplineSolver", createCurve=False, startJoint=(name + side + '_leg_bendy_1_JNT_01'), endEffector=(name + side + '_leg_bendy_'+str(number_of_upper_leg_joints+number_of_lower_leg_joints)+'_JNT_01'), curve=name + side + '_leg_splineIK_curve_01')

    #make curveInfo node to track length of splineIK curve
    curveInfoNode = mc.arclen(name + side + '_leg_splineIK_curve_01', constructionHistory=True)
    curveInfoNode = mc.rename(curveInfoNode, name + side + '_leg_splineIK_curve_length_info_01')
    splineIK_start_curve_length = mc.getAttr(curveInfoNode + '.arcLength')
    
    #setup to get joints to scale with splineIK curve
    #find splineIK curve scale length
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_leg_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_leg_splineIK_curve_scale_length_MD_01')
    mc.setAttr( name + side + '_leg_splineIK_curve_scale_length_MD_01.operation', 2)
    
    mc.setAttr( name + side + '_leg_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01.input1X', splineIK_start_curve_length)
    mc.connectAttr( name + '_secret_total_scale_MD_01.outputX', name + side + '_leg_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01.input2X')

    mc.connectAttr( curveInfoNode + '.arcLength', name + side + '_leg_splineIK_curve_scale_length_MD_01.input1X' )
    mc.connectAttr( name + side + '_leg_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01.outputX', name + side + '_leg_splineIK_curve_scale_length_MD_01.input2X')
    
    #connect to joints' scale X
    for num in range(1, number_of_upper_leg_joints+number_of_lower_leg_joints+1):
        mc.connectAttr( name + side + '_leg_splineIK_curve_scale_length_MD_01.outputX', name + side + '_leg_bendy_'+str(num)+'_JNT_01.scaleX')



    #
    # Create IK spline for bendy leg bone pointers
                                                          
    # will contain positions in space of all joints 
    cv_world_positions=[]
    for joint in curve_cv_primary_control_joints:
        cur_cv_position = mc.pointPosition( joint + '.rotatePivot' )
        cv_world_positions.append( cur_cv_position )
    
    # create curve with CVs at proper positions to generate curve
    temp_name = mc.curve( d=3, p=cv_world_positions) 
    mc.rename(temp_name, name + side + '_leg_splineIK_pointer_curve_01') 

    # move pointer curve backward in Z (so crimps without overlapping)
    mc.move(0,0,-abs(upp_leg_length+low_leg_length)/6, name + side + '_leg_splineIK_pointer_curve_01', worldSpace=True, relative=True ) 
    #For Grendel and his DANG BENT LEGS only:
    if name=='Grendel':
        knee_pos=mc.xform(knee_joint, query=True, translation=True, worldSpace=True)
        mc.scale(0.8,0.8,0.8, name + side + '_leg_splineIK_pointer_curve_01', relative=True, pivot=(knee_pos[0]-0.051, knee_pos[1]+0.060, knee_pos[2]-0.379) ) 

    #Bind bendy_JNT joints to curve and adjust weights
    mc.skinCluster(curve_cv_control_joints, name + side + '_leg_splineIK_pointer_curve_01', name=name + side + '_leg_splineIK_pointer_curve_scls_01')
    for joint in curve_cv_primary_control_joints:
        mc.skinPercent(name + side + '_leg_splineIK_pointer_curve_scls_01', name + side + '_leg_splineIK_pointer_curve_01.cv['+str(curve_cv_primary_control_joints.index(joint))+']', transformValue=[(joint, 1.0)])
    mc.ikHandle(name=name + side + '_leg_splineIK_pointer_handle_01', solver="ikSplineSolver", createCurve=False, startJoint=(name + side + '_leg_bendy_pointer_1_JNT_01'), endEffector=(name + side + '_leg_bendy_pointer_'+str(number_of_upper_leg_joints+number_of_lower_leg_joints)+'_JNT_01'), curve=name + side + '_leg_splineIK_pointer_curve_01')

    #make curveInfo node to track length of splineIK curve
    curveInfoNode = mc.arclen(name + side + '_leg_splineIK_pointer_curve_01', constructionHistory=True)
    curveInfoNode = mc.rename(curveInfoNode, name + side + '_leg_splineIK_pointer_curve_length_info_01')
    splineIK_start_pointer_curve_length = mc.getAttr(curveInfoNode + '.arcLength')

    #setup to get joints to scale with splineIK curve
    #find splineIK curve scale length
    mc.shadingNode('multiplyDivide', asUtility=True, name=name + side + '_leg_splineIK_pointer_curve_simplify_compensate_MD_01')
    mc.setAttr( name + side + '_leg_splineIK_pointer_curve_simplify_compensate_MD_01.operation', 2)
    
    mc.shadingNode('multiplyDivide', asUtility=True, name=name + side + '_leg_splineIK_compensated_pointer_curve_length_multiplied_by_rig_scale_MD_01')

    mc.shadingNode('multiplyDivide', asUtility=True, name=name + side + '_leg_splineIK_pointer_curve_scale_length_MD_01')
    mc.setAttr( name + side + '_leg_splineIK_pointer_curve_scale_length_MD_01.operation', 2)

    mc.shadingNode('multiplyDivide', asUtility=True, name=name + side + '_leg_splineIK_pointer_curve_joint_scale_MD_01')
    mc.setAttr( name + side + '_leg_splineIK_pointer_curve_joint_scale_MD_01.operation', 2)


    mc.setAttr(name + side + '_leg_splineIK_pointer_curve_simplify_compensate_MD_01.input1X', mc.getAttr(name + side + '_leg_splineIK_pointer_curve_length_info_01.arcLength'))
    mc.setAttr(name + side + '_leg_splineIK_pointer_curve_simplify_compensate_MD_01.input2X', mc.getAttr(name + side + '_leg_splineIK_curve_length_info_01.arcLength'))
    
    mc.connectAttr(name + side + '_leg_splineIK_pointer_curve_simplify_compensate_MD_01.outputX', name + side + '_leg_splineIK_compensated_pointer_curve_length_multiplied_by_rig_scale_MD_01.input1X', force=True)
    mc.connectAttr(name + '_secret_total_scale_MD_01.outputX', name + side + '_leg_splineIK_compensated_pointer_curve_length_multiplied_by_rig_scale_MD_01.input2X', force=True)
    
    mc.connectAttr(name + side + '_leg_splineIK_pointer_curve_length_info_01.arcLength', name + side + '_leg_splineIK_pointer_curve_scale_length_MD_01.input1X', force=True)
    mc.setAttr(name + side + '_leg_splineIK_pointer_curve_scale_length_MD_01.input2X', splineIK_start_pointer_curve_length)

    mc.connectAttr(name + side + '_leg_splineIK_pointer_curve_scale_length_MD_01.outputX', name + side + '_leg_splineIK_pointer_curve_joint_scale_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_leg_splineIK_compensated_pointer_curve_length_multiplied_by_rig_scale_MD_01.outputX', name + side + '_leg_splineIK_pointer_curve_joint_scale_MD_01.input2X', force=True)

    
    #connect to joints' scale X
    #for num in range(1, number_of_upper_leg_joints+number_of_lower_leg_joints+1):
        #mc.connectAttr( name + side + '_leg_splineIK_pointer_curve_joint_scale_MD_01.outputX', name + side + '_leg_bendy_pointer_'+str(num)+'_JNT_01.scaleX', force=True)



    #
    # Aim bendy bones to bendy joints
    # all but last
    for num in range(1, number_of_upper_leg_joints+number_of_lower_leg_joints):
        mc.pointConstraint(name + side + '_leg_bendy_'+str(num)+'_JNT_01', name + side + '_leg_bendy_'+str(num)+'_BN_01', maintainOffset=False)
        mc.aimConstraint(name + side + '_leg_bendy_'+str(num+1)+'_BN_01', name + side + '_leg_bendy_'+str(num)+'_BN_01', maintainOffset=True, worldUpType="object", worldUpObject=name + side + '_leg_bendy_pointer_' + str(num) + '_JNT_01', upVector=(0,-1,0) )
    #last
    mc.parentConstraint(name + side + '_ankle_JNT_01', name + side + '_leg_bendy_'+str(number_of_upper_leg_joints+number_of_lower_leg_joints)+'_BN_01', maintainOffset=True)




    #
    # connect bendy rig to normal rig
    
    # constrain bendy joint control offsets to normal joint chain
    mc.pointConstraint(name + side + '_upper_leg_JNT_01', name + side + '_hip_bendy_cc_os_grp_01', maintainOffset=True)
    mc.orientConstraint(name + side + '_upper_leg_JNT_01', name + side + '_hip_bendy_cc_os_grp_01', maintainOffset=True)

    mc.parentConstraint(name + side + '_upper_leg_JNT_01', name + side + '_upper_leg_bendy_cc_os_grp_01', maintainOffset=True)

    mc.parentConstraint(name + side + '_lower_leg_JNT_01', name + side + '_knee_bendy_cc_os_grp_01', maintainOffset=True)

    mc.parentConstraint(name + side + '_lower_leg_JNT_01', name + side + '_lower_leg_bendy_cc_os_grp_01', maintainOffset=True)

    mc.parentConstraint(name + side + '_ankle_JNT_01', name + side + '_ankle_bendy_cc_os_grp_01', maintainOffset=True)
 
 
    # constrain bendy joint control offsets to normal joint chain
    mc.pointConstraint(name + side + '_upper_leg_JNT_01', name + side + '_hip_bendy_JNT_os_grp_01', maintainOffset=True)
    mc.orientConstraint(name + side + '_upper_leg_JNT_01', name + side + '_hip_bendy_JNT_os_grp_01', maintainOffset=True)
  
    mc.parentConstraint(name + side + '_upper_leg_JNT_01', name + side + '_upper_leg_bendy_JNT_os_grp_01', maintainOffset=True)

    mc.parentConstraint(name + side + '_lower_leg_JNT_01', name + side + '_knee_bendy_JNT_os_grp_01', maintainOffset=True)

    mc.parentConstraint(name + side + '_lower_leg_JNT_01', name + side + '_lower_leg_bendy_JNT_os_grp_01', maintainOffset=True)

    mc.parentConstraint(name + side + '_ankle_JNT_01', name + side + '_ankle_bendy_JNT_os_grp_01', maintainOffset=True)
 
 



    #
    # Twists
    
    # rotate bendy elbow halfway in z, so that it makes a nice bend instead of a kink
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_leg_bendy_knee_follow_MD_01')
    mc.connectAttr(name + side + '_lower_leg_JNT_01.rotateZ', name + side + '_leg_bendy_knee_follow_MD_01.input1X', force=True)
    mc.setAttr(name + side + '_leg_bendy_knee_follow_MD_01.input2X', -0.5)
    mc.connectAttr(name + side + '_leg_bendy_knee_follow_MD_01.outputX', name + side + '_knee_bendy_cc_rotation_os_grp_01.rotateZ', force=True) 
    mc.connectAttr(name + side + '_leg_bendy_knee_follow_MD_01.outputX', name + side + '_knee_bendy_JNT_rotation_os_grp_01.rotateZ', force=True) 

    # rotate bendy upper_leg halfway in z, so that whole leg twists nicely
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_leg_bendy_upper_leg_follow_MD_01')
    mc.connectAttr(name + side + '_upper_leg_JNT_01.rotateX', name + side + '_leg_bendy_upper_leg_follow_MD_01.input1X', force=True)
    mc.setAttr(name + side + '_leg_bendy_upper_leg_follow_MD_01.input2X', -0.5)
    mc.connectAttr(name + side + '_leg_bendy_upper_leg_follow_MD_01.outputX', name + side + '_upper_leg_bendy_cc_rotation_os_grp_01.rotateX', force=True) 
    mc.connectAttr(name + side + '_leg_bendy_upper_leg_follow_MD_01.outputX', name + side + '_upper_leg_bendy_JNT_rotation_os_grp_01.rotateX', force=True) 

    # rotate bendy lower_leg halfway in z, so that whole leg twists nicely
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_leg_bendy_lower_leg_follow_MD_01')
    mc.connectAttr(name + side + '_ankle_JNT_01.rotateX', name + side + '_leg_bendy_lower_leg_follow_MD_01.input1X', force=True)
    mc.setAttr(name + side + '_leg_bendy_lower_leg_follow_MD_01.input2X', 0.5)
    mc.connectAttr(name + side + '_leg_bendy_lower_leg_follow_MD_01.outputX', name + side + '_lower_leg_bendy_cc_rotation_os_grp_01.rotateX', force=True) 
    mc.connectAttr(name + side + '_leg_bendy_lower_leg_follow_MD_01.outputX', name + side + '_lower_leg_bendy_JNT_rotation_os_grp_01.rotateX', force=True) 


    #constrain last joint of bendy bone chain to ankle
    mc.parentConstraint(name + side + '_ankle_JNT_01', name + side + '_leg_bendy_'+str(number_of_upper_leg_joints+number_of_lower_leg_joints)+'_BN_01', maintainOffset=True)












    #
    # connect vis attrs
    primary_curve_cv_control_ccs = [name + side + '_hip_bendy_cc_01', 
                                  name + side + '_upper_leg_bendy_cc_01',
                                  name + side + '_knee_bendy_cc_01',
                                  name + side + '_lower_leg_bendy_cc_01',
                                  name + side + '_ankle_bendy_cc_01']

    for primary_cc in primary_curve_cv_control_ccs:
        mc.connectAttr(name + side + '_leg_settings_cc_01.bendy_control_visibility_parameter', primary_cc + '.visibility', force=True)
        mc.addAttr(primary_cc, shortName='noodle_tangents_parameter', longName='Tangents', attributeType='enum', enumName='Off:On:', keyable=True)  
        children=mc.listRelatives(primary_cc, children=True, type='transform')
        for child in children:
            mc.connectAttr(primary_cc + '.noodle_tangents_parameter', child + '.visibility', force=True)











    """
    scene cleanup
    """
    
    # parenting
    mc.group(name = name + side + '_IK_leg_controls_GRP_01', empty=True)
    mc.parent(name + side + "_IK_leg_cc_os_grp_01", name + side + '_IK_leg_controls_GRP_01')
    mc.connectAttr(name + side + '_IK_leg_controls_GRP_01.visibility', pole_vector_line + '.visibility')
    mc.parent(leg_pole_vector_control.Off, name + side + '_IK_leg_controls_GRP_01' )
    mc.group(name = name + side + '_FK_leg_controls_GRP_01', empty=True)
    mc.parent(name + side + "_FK_upper_leg_cc_stretch_os_grp_01", name + side + '_FK_leg_controls_GRP_01')

    # Leg distance nodes GRP
    mc.group(name = name + side + '_leg_distance_nodes_GRP_01', empty=True)
    mc.parent(name + side + '_leg_IK_control_distance_01', 
             name + side + '_leg_soft_distance_01', 
             name + side + '_upper_leg_distance_01',
             name + side + '_lower_leg_distance_01',
             name + side + '_leg_stretch_distance_01', 
             name + side + '_leg_distance_nodes_GRP_01')
    mc.parent(name + side + '_leg_distance_nodes_GRP_01', name + '_secondary_global_cc_01')

    # leg controls GRP
    mc.group(name = name + side + '_leg_controls_GRP_01', empty=True)
    mc.parent(name + side + '_leg_settings_cc_os_grp_01', 
             name + side + '_FK_leg_controls_GRP_01', 
             name + side + '_IK_leg_controls_GRP_01',
             name + side + '_foot_controls_GRP_01',
             name + side + '_leg_bendy_controls_GRP_01',
             name + side + '_leg_controls_GRP_01')  
    
    # leg extras GRP
    mc.group(name = name + side + '_leg_extras_GRP_01', empty=True)
    mc.parent(name + side + '_upper_leg_loc_connect_grp_01', 
             name + side + '_lower_leg_loc_01', 
             name + side + '_leg_soft_blend_IK_loc_01',
             name + side + '_leg_distance_nodes_GRP_01',
             name + side + '_IK_leg_cc_distance_loc_01',
             name + side + '_hip_PSR_GRP_01',
             name + side + '_leg_splineIK_handle_01',
             name + side + '_leg_splineIK_pointer_handle_01',
             name + side + '_leg_extras_GRP_01')
    
    # foot extras GRP
    mc.group(name = name + side + '_foot_extras_GRP_01', empty=True)
    mc.group(name = name + side + '_foot_extras_os_grp_01', empty=True)
    mc.parent(name + side + '_foot_extras_os_grp_01', name + side + '_foot_extras_GRP_01')
    mc.group(name = name + side + '_foot_scIKs_GRP_01', empty=True)
    mc.delete(mc.parentConstraint(name + side + '_IK_leg_cc_01', name + side + '_foot_scIKs_GRP_01', maintainOffset=False))
    mc.parent(name + side + '_foot_scIKs_GRP_01', name + side + '_foot_extras_os_grp_01')
    mc.group(name = name + side + '_foot_locators_GRP_01', empty=True)
    mc.delete(mc.parentConstraint(name + side + '_IK_leg_cc_01', name + side + '_foot_locators_GRP_01', maintainOffset=False))
    mc.parent(name + side + '_foot_locators_GRP_01', name + side + '_foot_extras_os_grp_01')
    
    # align extras os grp to foot controls
    mc.delete(mc.parentConstraint(name + side + '_IK_leg_cc_01', name + side + '_foot_extras_os_grp_01', maintainOffset=False))
    
    mc.parentConstraint(name + side + '_IK_leg_cc_01', name + side + '_foot_scIKs_GRP_01', maintainOffset=False)
    mc.parentConstraint(name + side + '_IK_leg_cc_01', name + side + '_foot_locators_GRP_01', maintainOffset=False)
    
    # more parenting
    mc.parent(name + side + '_foot_ball_scIK_01', name + side + '_foot_tip_scIK_01', name + side + '_foot_scIKs_GRP_01')
    mc.parent(name + side + '_foot_heel_twist_os_grp_01', name + side + '_foot_locators_GRP_01')
    mc.parent(name + side + '_leg_controls_GRP_01', name + '_secondary_global_cc_01')
    mc.parent(name + side + '_leg_extras_GRP_01', name + '_extras_GRP_01')
    mc.parent(name + side + '_foot_extras_GRP_01', name + '_extras_GRP_01')
    mc.group(name = name + side + '_leg_joints_GRP_01', empty=True)
    mc.parent(FK_joints_offset_group, 
              IK_joints_offset_group, 
              base_joints_offset_group, 
              bendy_control_joints_offset_group,
              bendy_joints_offset_group,
              bendy_pointer_joints_offset_group,
              bendy_bones_offset_group,
              name + side + '_leg_joints_GRP_01')
    mc.parent( name + side + '_leg_joints_GRP_01', name + '_skeleton_GRP_01')
    mc.group(name = name + side + '_leg_no_transform_GRP_01', empty=True)
    mc.parent(name + side + '_leg_no_transform_GRP_01', name + '_no_transform_GRP_01')
    mc.parent(pole_vector_line, 
              name + side + '_leg_splineIK_curve_01',
              name + side + '_leg_splineIK_pointer_curve_01',
              name + side + '_leg_no_transform_GRP_01')

    
    #
    # visibility
    
    #groups  
    mc.setAttr( name + side + "_leg_extras_GRP_01.visibility", 0)
    mc.setAttr( name + side + "_foot_extras_GRP_01.visibility", 0)
    mc.setAttr( name + side + "_leg_no_transform_GRP_01.visibility", 0)

    #IK/FK
    mc.connectAttr( name + side + '_leg_settings_cc_parent_constraint_weight_RMV_01.outValue', name + side + "_IK_leg_controls_GRP_01.visibility", force = True)
    mc.connectAttr( name + side + '_leg_settings_cc_parent_constraint_inverse_weight_RMV_01.output3Dx', name + side + "_FK_leg_controls_GRP_01.visibility", force = True)
    #Hide SplineIK bendy Curve
    #mc.setAttr(name + side + '_leg_splineIK_curve_01.visibility', 0)
    
    
    
    
    #
    # lock attrs
    
    # lock translate on leg settings control after reparenting
    mc.setAttr( name + side + "_leg_settings_cc_01.translateX", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_leg_settings_cc_01.translateY", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_leg_settings_cc_01.translateZ", lock=True, keyable=False, channelBox=False)
    


    ######################connect to rest of rig##############################
    #controls
    mc.parentConstraint(name + '_hips_cc_01', name + side + '_FK_leg_controls_GRP_01', maintainOffset=True)
    mc.parentConstraint(name + '_secondary_global_cc_01', name + '_COG_cc_01', name + '_hips_cc_01', name + side + '_IK_leg_controls_GRP_01', maintainOffset=True)
    
    #space switching
    #ik feet
    mc.shadingNode('condition', asUtility=True, name= name + side + '_leg_ik_cc_hips_follow_COND_01')
    mc.setAttr( name + side + '_leg_ik_cc_hips_follow_COND_01.operation', 1)   
    mc.setAttr( name + side + '_leg_ik_cc_hips_follow_COND_01.secondTerm', 2)    
 
    mc.shadingNode('condition', asUtility=True, name= name + side + '_leg_ik_cc_COG_follow_COND_01')
    mc.setAttr( name + side + '_leg_ik_cc_COG_follow_COND_01.operation', 1)   
    mc.setAttr( name + side + '_leg_ik_cc_COG_follow_COND_01.secondTerm', 1)   

    mc.shadingNode('condition', asUtility=True, name= name + side + '_leg_ik_cc_global_follow_COND_01')
    mc.setAttr( name + side + '_leg_ik_cc_global_follow_COND_01.operation', 1)       
    mc.setAttr( name + side + '_leg_ik_cc_global_follow_COND_01.secondTerm', 0)   

    mc.connectAttr(name + side + '_leg_settings_cc_01.ik_follow_parameter', name + side + '_leg_ik_cc_global_follow_COND_01.firstTerm')
    mc.connectAttr(name + side + '_leg_settings_cc_01.ik_follow_parameter', name + side + '_leg_ik_cc_COG_follow_COND_01.firstTerm')
    mc.connectAttr(name + side + '_leg_settings_cc_01.ik_follow_parameter', name + side + '_leg_ik_cc_hips_follow_COND_01.firstTerm')
            
    mc.connectAttr(name + side + '_leg_ik_cc_global_follow_COND_01.outColor.outColorR', name + side + '_IK_leg_controls_GRP_01_parentConstraint1.' + name + '_secondary_global_cc_01W0')
    mc.connectAttr(name + side + '_leg_ik_cc_COG_follow_COND_01.outColor.outColorR', name + side + '_IK_leg_controls_GRP_01_parentConstraint1.' + name + '_COG_cc_01W1')
    mc.connectAttr(name + side + '_leg_ik_cc_hips_follow_COND_01.outColor.outColorR', name + side + '_IK_leg_controls_GRP_01_parentConstraint1.' + name + '_hips_cc_01W2')
        
    # Connections to hip
    #joints
    mc.parentConstraint(name + '_hips_cc_01', name + side + '_upper_leg_FK_os_grp_01', maintainOffset=True)
    #extras
    mc.parentConstraint(name + '_hips_cc_01', name + side + '_upper_leg_loc_connect_grp_01', maintainOffset=True)
    mc.parentConstraint(name + '_hips_cc_01', name + side + '_hip_PSR_GRP_01', maintainOffset=True)

    #ik pole vector connections
    mc.shadingNode('condition', asUtility=True, name= name + side + '_leg_ik_pole_vector_cc_ankle_follow_COND_01')
    mc.setAttr( name + side + '_leg_ik_pole_vector_cc_ankle_follow_COND_01.operation', 1)   
    mc.setAttr( name + side + '_leg_ik_pole_vector_cc_ankle_follow_COND_01.secondTerm', 0)  
    
    mc.shadingNode('condition', asUtility=True, name= name + side + '_leg_ik_pole_vector_cc_hips_follow_COND_01')
    mc.setAttr( name + side + '_leg_ik_pole_vector_cc_hips_follow_COND_01.operation', 1)   
    mc.setAttr( name + side + '_leg_ik_pole_vector_cc_hips_follow_COND_01.secondTerm', 1)    
 
    mc.shadingNode('condition', asUtility=True, name= name + side + '_leg_ik_pole_vector_cc_COG_follow_COND_01')
    mc.setAttr( name + side + '_leg_ik_pole_vector_cc_COG_follow_COND_01.operation', 1)   
    mc.setAttr( name + side + '_leg_ik_pole_vector_cc_COG_follow_COND_01.secondTerm', 2)   

    mc.shadingNode('condition', asUtility=True, name= name + side + '_leg_ik_pole_vector_cc_global_follow_COND_01')
    mc.setAttr( name + side + '_leg_ik_pole_vector_cc_global_follow_COND_01.operation', 1)       
    mc.setAttr( name + side + '_leg_ik_pole_vector_cc_global_follow_COND_01.secondTerm', 3)   

    mc.connectAttr(name + side + '_leg_pole_vector_cc_01.ik_pole_vector_follow_parameter', name + side + '_leg_ik_pole_vector_cc_global_follow_COND_01.firstTerm')
    mc.connectAttr(name + side + '_leg_pole_vector_cc_01.ik_pole_vector_follow_parameter', name + side + '_leg_ik_pole_vector_cc_COG_follow_COND_01.firstTerm')
    mc.connectAttr(name + side + '_leg_ pole_vector_cc_01.ik_pole_vector_follow_parameter', name + side + '_leg_ik_pole_vector_cc_hips_follow_COND_01.firstTerm')
    mc.connectAttr(name + side + '_leg_ pole_vector_cc_01.ik_pole_vector_follow_parameter', name + side + '_leg_ik_pole_vector_cc_ankle_follow_COND_01.firstTerm')
            
    mc.connectAttr(name + side + '_leg_ik_pole_vector_cc_global_follow_COND_01.outColor.outColorR', name + side + '_leg_pole_vector_cc_os_grp_01_parentConstraint1.' + name + '_secondary_global_cc_01W3')
    mc.connectAttr(name + side + '_leg_ik_pole_vector_cc_COG_follow_COND_01.outColor.outColorR', name + side + '_leg_pole_vector_cc_os_grp_01_parentConstraint1.' + name + '_COG_cc_01W2')
    mc.connectAttr(name + side + '_leg_ik_pole_vector_cc_hips_follow_COND_01.outColor.outColorR', name + side + '_leg_pole_vector_cc_os_grp_01_parentConstraint1.' + name + '_hips_cc_01W1')
    mc.connectAttr(name + side + '_leg_ik_pole_vector_cc_ankle_follow_COND_01.outColor.outColorR', name + side + '_leg_pole_vector_cc_os_grp_01_parentConstraint1.' + name + side + '_IK_leg_cc_01W0')
    
    



    '''
    ############################### temporary, remove once gotten stretchies set up
    # create temp bones by duplicating JNT chain
    mc.duplicate(name + side + '_upper_leg_JNT_01', renameChildren=True)
    mc.rename(name + side + '_upper_leg_JNT_02', name + side + '_upper_leg_BN_01')
    mc.rename(name + side + '_lower_leg_JNT_02', name + side + '_lower_leg_BN_01')
    mc.rename(name + side + '_ankle_JNT_02', name + side + '_ankle_BN_01')
    mc.rename(name + side + '_foot_ball_JNT_02', name + side + '_foot_ball_BN_01')
    mc.rename(name + side + '_foot_tip_JNT_02', name + side + '_foot_tip_ankle_BN_01')

    # constrain joints to FK and IK chains
    mc.parentConstraint(name + side + "_upper_leg_JNT_01", name + side + "_upper_leg_BN_01")
    mc.parentConstraint(name + side + "_lower_leg_JNT_01", name + side + "_lower_leg_BN_01")
    mc.parentConstraint(name + side + "_ankle_JNT_01", name + side + "_ankle_BN_01")
    '''


    
    print('done.')
    
    """
    
    make rig module
    rig_module = module.Module( prefix = prefix, base_object=base_rig)  
    
    
    return{ 'module':rig_module }
    """
    
