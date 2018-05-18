"""
arm @ rig
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
          scapula_joint,
          shoulder_joint,
          elbow_joint,
          wrist_joint,
          side = '_LFT',
          prefix = 'LFT_arm',
          rig_scale = 1.0,
          base_rig = None
          ):

    """
    @param name: str, base name of rig
    @param scapula_joint: str, scapula target cc
    @param shoulder_joint: str, shoulder (upper arm) target cc
    @param elbow_joint: str, elbow target cc
    @param wrist_joint: str, wrist target cc
    @param side: side of the character, LFT or RGT
    @param prefix: str, prefix to name new arm objects
    @param rig_scale: float, scale of new controls
    @param base_rig: instance of base.module.Base class
    @return: dictionary with rig module objects
    """

    print("building " + side + " arm...")


    """
    create settings control and add custom attributes
    """

    arm_settings_control = control.Control(
                                  prefix = name + side + '_arm_settings',
                                  scale = .3,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = wrist_joint,
                                  rotate_to = wrist_joint,
                                  parent = '',
                                  shape = 'gear',
                                  locked_channels = ['visibility']
                                  )


    # add custom FK attributes to control
    mc.addAttr( arm_settings_control.C, shortName='fk_ik_parameter', longName='FK_IK', attributeType='float', defaultValue=0.0, minValue=0.0, maxValue=1.0, keyable=True)
    mc.addAttr( arm_settings_control.C, shortName='bendy_control_visibility_parameter', longName='Bendy_Controls', attributeType='enum', enumName='Off:On:', keyable=True)
    mc.addAttr( arm_settings_control.C, shortName='fk_controls', longName='FK_Controls', attributeType='enum', enumName='----------', keyable=True)
    mc.setAttr(name + side + "_arm_settings_cc_01.fk_controls", keyable=False, channelBox=True)
    mc.addAttr( arm_settings_control.C, shortName='upper_arm_length_parameter', longName='Upper_Arm_Length', attributeType='float', defaultValue=1.0, minValue=0.0, keyable=True)
    mc.addAttr( arm_settings_control.C, shortName='lower_arm_length_parameter', longName='Lower_Arm_Length', attributeType='float', defaultValue=1.0, minValue=0.0, keyable=True)

    # add custom IK attributes to control
    mc.addAttr( arm_settings_control.C, shortName='ik_controls', longName='IK_Controls', attributeType='enum', enumName='----------', keyable=True)
    mc.setAttr( name + side + "_arm_settings_cc_01.ik_controls", keyable=False, channelBox=True)
    mc.addAttr( arm_settings_control.C, shortName='slide_parameter', longName='Slide', attributeType='float', defaultValue=0.0, minValue=-1.0, maxValue=1.0, keyable=True)
    mc.addAttr( arm_settings_control.C, shortName='stretch_parameter', longName='Stretch', attributeType='float', defaultValue=1.0, minValue=0.0, maxValue=1.0, keyable=True)
    mc.addAttr( arm_settings_control.C, shortName='soft_parameter', longName='Soft', attributeType='float', defaultValue=0.0, minValue=0.0, maxValue=1.0, keyable=True)
    mc.addAttr( arm_settings_control.C, shortName='pin_parameter', longName='Pin', attributeType='float', defaultValue=0.0, minValue=0.0, maxValue=1.0, keyable=True)
    mc.addAttr( arm_settings_control.C, shortName='ik_follow_parameter', longName='Follow', attributeType='enum', enumName='Global:COG:Chest:', keyable=True)

    # make an offset group
    transform.make_offset_group(name + side + '_arm_settings_cc_01', name + side + '_arm_settings_curve_offset')


    # position control
    if side=="_LFT":
        mc.rotate(180.0,0.0,0.0, name + side + '_arm_settings_curve_offset_os_grp_01', relative=True)

    mc.move(0.0,-.50,0.0, name + side + '_arm_settings_curve_offset_os_grp_01', relative=True, objectSpace=True)

    mc.rotate(90.0,0.0,0.0, name + side + '_arm_settings_curve_offset_os_grp_01', relative=True)


    # parent control offset group
    mc.parent(name + side + '_arm_settings_cc_os_grp_01', name + '_secondary_global_cc_01')

    # lock and hide all rotate, scale, and visibility
    mc.setAttr( name + side + "_arm_settings_cc_01.rotateX", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_arm_settings_cc_01.rotateY", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_arm_settings_cc_01.rotateZ", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_arm_settings_cc_01.scaleX", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_arm_settings_cc_01.scaleY", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_arm_settings_cc_01.scaleZ", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_arm_settings_cc_01.visibility", lock=True, keyable=False, channelBox=False)



    """
    FK arm setup
    """

    # create left FK joints and mirror for right FK joints
    if side=="_LFT":
        # create upper_arm FK JNT
        mc.joint(name=name + side + "_upper_arm_FK_JNT_01", position = mc.xform(shoulder_joint, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=0.01)
        mc.parent(name + side + "_upper_arm_FK_JNT_01", name + '_secondary_global_cc_01')

        # create lower_arm FK JNT
        mc.joint(name=name + side + "_lower_arm_FK_JNT_01", position = mc.xform(elbow_joint, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=0.01)
        mc.joint( name + side + '_upper_arm_FK_JNT_01', edit=True, zeroScaleOrient=True, orientJoint='xzy', secondaryAxisOrient = 'yup' )

        # create wrist FK JNT
        mc.joint(name=name + side + "_wrist_FK_JNT_01", position = mc.xform(wrist_joint, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=0.01)
        mc.joint( name + side + '_lower_arm_FK_JNT_01', edit=True, zeroScaleOrient=True, orientJoint='xzy', secondaryAxisOrient = 'yup' )

        # reset orientations on upper arm joint
        mc.joint( name + side + '_upper_arm_FK_JNT_01', edit=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient = 'yup' )
    else:
        mc.mirrorJoint(name + '_LFT_upper_arm_FK_JNT_01', mirrorBehavior=True, mirrorYZ=True, searchReplace=("LFT","RGT"))

    #set wrist orientation
    mc.setAttr( name + side + "_wrist_FK_JNT_01.jointOrientX", 90.0)
    mc.setAttr( name + side + "_wrist_FK_JNT_01.jointOrientY", 0.0)
    mc.setAttr( name + side + "_wrist_FK_JNT_01.jointOrientZ", 0.0)

    # create offset grp
    FK_joints_offset_group = mc.group( name=name + side + '_upper_arm_FK_JNT_os_grp_01', empty=True)

    #match offset group's transforms to object transforms
    mc.delete( mc.parentConstraint( name + side + "_upper_arm_FK_JNT_01", FK_joints_offset_group ))
    mc.delete( mc.scaleConstraint( name + side + "_upper_arm_FK_JNT_01", FK_joints_offset_group ))

    ############## WHAT THE HECK IS GOING ON WITH THE PARENT COMMAND HERE???????????? KEEPS COMBINING MIRRORED JOINTS - HENCE NO TRANSFORM.MAKE_OFFSET_GROUP AND THE SNIPPET BELOW.
    mc.parent(FK_joints_offset_group, name + '_secondary_global_cc_01')
    mc.parent(name + side + "_upper_arm_FK_JNT_01", FK_joints_offset_group, absolute=True)
    if side=="_RGT":
        reversed_x_position = mc.getAttr(FK_joints_offset_group + '.translateX')
        fixed_x_position = reversed_x_position*-1.0
        mc.setAttr(FK_joints_offset_group + '.translateX', fixed_x_position)




    # create FK control curves
    FK_upper_arm_control = control.Control(
                                  prefix = name + side + '_FK_upper_arm',
                                  scale = .40,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_upper_arm_FK_JNT_01',
                                  rotate_to = name + side + '_upper_arm_FK_JNT_01',
                                  parent = name + '_secondary_global_cc_01',
                                  shape = 'circle',
                                  locked_channels = ['scale', 'visibility']
                                  )

    FK_lower_arm_control = control.Control(
                                  prefix = name + side + '_FK_lower_arm',
                                  scale = .375,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_lower_arm_FK_JNT_01',
                                  rotate_to = name + side + '_lower_arm_FK_JNT_01',
                                  parent = FK_upper_arm_control.C,
                                  shape = 'circle',
                                  locked_channels = ['scale', 'visibility']
                                  )

    FK_wrist_control = control.Control(
                                  prefix = name + side + '_FK_wrist',
                                  scale = .35,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_wrist_FK_JNT_01',
                                  rotate_to = name + side + '_wrist_FK_JNT_01',
                                  parent = FK_lower_arm_control.C,
                                  shape = 'circle',
                                  locked_channels = ['scale', 'visibility']
                                  )


    # lock and hide translate, scale, and visibility
    for part in ['upper_arm', 'lower_arm', 'wrist']:
        mc.setAttr( name + side + "_FK_" + part + "_cc_01.translateX", lock=True, keyable=False, channelBox=False)
        mc.setAttr( name + side + "_FK_" + part + "_cc_01.translateY", lock=True, keyable=False, channelBox=False)
        mc.setAttr( name + side + "_FK_" + part + "_cc_01.translateZ", lock=True, keyable=False, channelBox=False)
        mc.setAttr( name + side + "_FK_" + part + "_cc_01.scaleX", lock=True, keyable=False, channelBox=False)
        mc.setAttr( name + side + "_FK_" + part + "_cc_01.scaleY", lock=True, keyable=False, channelBox=False)
        mc.setAttr( name + side + "_FK_" + part + "_cc_01.scaleZ", lock=True, keyable=False, channelBox=False)
        mc.setAttr( name + side + "_FK_" + part + "_cc_01.visibility", lock=True, keyable=False, channelBox=False)

    # Create offset groups to move controls according to FK stretch parameters
    transform.make_offset_group(FK_upper_arm_control.Off, name + side + '_FK_upper_arm_cc_stretch')
    transform.make_offset_group(FK_lower_arm_control.Off, name + side + '_FK_lower_arm_cc_stretch')
    transform.make_offset_group(FK_wrist_control.Off, name + side + '_FK_wrist_cc_stretch')

    # Point constrain control stretchy offset groups to FK joints
    mc.pointConstraint(name + side + '_lower_arm_FK_JNT_01', name + side + '_FK_lower_arm_cc_stretch_os_grp_01')
    mc.pointConstraint(name + side + '_wrist_FK_JNT_01', name + side + '_FK_wrist_cc_stretch_os_grp_01')

    # Connect joints to controls
    mc.connectAttr( FK_upper_arm_control.C + '.rotate', name + side + '_upper_arm_FK_JNT_01.rotate', force=True)
    mc.connectAttr( FK_lower_arm_control.C + '.rotate', name + side + '_lower_arm_FK_JNT_01.rotate', force=True)
    mc.connectAttr( FK_wrist_control.C + '.rotate', name + side + '_wrist_FK_JNT_01.rotate', force=True)
    mc.connectAttr( name + side + '_arm_settings_cc_01.upper_arm_length_parameter', name + side + '_upper_arm_FK_JNT_01.scaleX', force=True)
    mc.connectAttr( name + side + '_arm_settings_cc_01.lower_arm_length_parameter', name + side + '_lower_arm_FK_JNT_01.scaleX', force=True)





    """
    IK arm setup
    """

    # create IK joints by duplicating FK chain
    mc.duplicate(name + side + '_upper_arm_FK_JNT_01', renameChildren=True)
    mc.rename(name + side + '_upper_arm_FK_JNT_02', name + side + '_upper_arm_IK_JNT_01')
    mc.rename(name + side + '_lower_arm_FK_JNT_02', name + side + '_lower_arm_IK_JNT_01')
    mc.rename(name + side + '_wrist_FK_JNT_02', name + side + '_wrist_IK_point_JNT_01')

    # create offset group
    IK_joints_offset_group = transform.make_offset_group(name + side + "_upper_arm_IK_JNT_01")

    # duplicate wrist IK JNT and point constrain to wrist IK point JNT
    mc.duplicate(name + side + "_wrist_IK_point_JNT_01", name=name + side + "_wrist_IK_JNT_01")
    mc.parent(name + side + "_wrist_IK_JNT_01", name + side + '_upper_arm_IK_os_grp_01')
    mc.pointConstraint(name + side + "_wrist_IK_point_JNT_01", name + side + "_wrist_IK_JNT_01")

    # create locators for IK arm rig
    mc.spaceLocator(name=name + side + "_upper_arm_loc_01")
    mc.delete(mc.pointConstraint(shoulder_joint, name + side + "_upper_arm_loc_01"))
    mc.spaceLocator(name=name + side + "_lower_arm_loc_01")
    mc.delete(mc.pointConstraint(elbow_joint, name + side + "_lower_arm_loc_01"))
    mc.spaceLocator(name=name + side + "_wrist_IK_loc_01")
    mc.delete(mc.pointConstraint(wrist_joint, name + side + "_wrist_IK_loc_01"))
    mc.spaceLocator(name=name + side + "_arm_soft_blend_IK_loc_01")
    mc.delete(mc.pointConstraint(wrist_joint, name + side + "_arm_soft_blend_IK_loc_01"))
    mc.spaceLocator(name=name + side + "_IK_arm_cc_distance_loc_01")
    mc.delete(mc.pointConstraint(wrist_joint, name + side + "_IK_arm_cc_distance_loc_01"))


    # create IK control curve
    IK_arm_control = control.Control(
                                  prefix = name + side + '_IK_arm',
                                  scale = .55,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_wrist_IK_JNT_01',
                                  rotate_to = name + side + '_wrist_IK_JNT_01',
                                  parent = '',
                                  shape = 'box',
                                  locked_channels = ['scale', 'visibility']
                                  )


    # constrain wrist joint's rotations to IK control's rotations
    mc.orientConstraint( name + side + '_IK_arm_cc_01', name + side + '_wrist_IK_JNT_01', maintainOffset=True)

    # lock and hide attributes
    mc.setAttr( name + side + "_IK_arm_cc_01.scaleX", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_IK_arm_cc_01.scaleY", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_IK_arm_cc_01.scaleZ", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_IK_arm_cc_01.visibility", lock=True, keyable=False, channelBox=False)

    # add rpIK handle
    rpIK_handle = mc.ikHandle( name=name + side + "_arm_rpIK_01", startJoint=name + side + "_upper_arm_IK_JNT_01", endEffector=name + side + "_wrist_IK_point_JNT_01", solver='ikRPsolver' )
    mc.setAttr( 'ikRPsolver.tolerance', 1e-007)

    # add pole vector constraint
    mc.poleVectorConstraint( name + side + "_lower_arm_loc_01", name + side + "_arm_rpIK_01" )

    # aim constrain upper arm loc to rpIK control curve
    mc.aimConstraint( IK_arm_control.C, name + side + "_upper_arm_loc_01", worldUpType="objectRotation", worldUpObject=name + '_secondary_global_cc_01')

    # parenting
    mc.pointConstraint( name + side + "_upper_arm_loc_01", name + side + "_upper_arm_IK_JNT_01" )
    mc.parent(name + side + "_wrist_IK_loc_01", name + side + "_upper_arm_loc_01")
    mc.pointConstraint( IK_arm_control.C, name + side + "_IK_arm_cc_distance_loc_01" )
    mc.setAttr(name + side + "_IK_arm_cc_distance_loc_01.rotateY", 0.0) # not sure why the parenting is causing this rotation, perhaps because of locked channels?
    mc.parent(name + side + "_upper_arm_loc_01", name + '_secondary_global_cc_01')
    mc.parent(name + side + "_lower_arm_loc_01", name + '_secondary_global_cc_01')
    mc.parent(name + side + "_arm_soft_blend_IK_loc_01", name + '_secondary_global_cc_01')
    mc.makeIdentity (apply=True, translate=True, rotate=False, scale=False)
    mc.parent( name + side + "_arm_rpIK_01", name + side + "_arm_soft_blend_IK_loc_01",)

    # for attaching to rest of rig
    mc.group(name=name + side + '_upper_arm_loc_connect_grp_01', empty=True)
    mc.delete(mc.pointConstraint(name + side + '_upper_arm_loc_01', name + side + '_upper_arm_loc_connect_grp_01', maintainOffset=False))
    mc.parent(name + side + '_upper_arm_loc_01', name + side + '_upper_arm_loc_connect_grp_01')
    mc.parent(name + side + '_upper_arm_loc_connect_grp_01', name + '_secondary_global_cc_01')


    # create measure distance nodes
    IK_control_distance_shape = mc.distanceDimension( startPoint=[1.0,0.0,0.0], endPoint=[10.0,0.0,0.0] )
    soft_distance_shape = mc.distanceDimension( startPoint=[1.0,0.0,0.0], endPoint=[10.0,0.0,0.0] )
    upper_arm_distance_shape = mc.distanceDimension( startPoint=[1.0,0.0,0.0], endPoint=[10.0,0.0,0.0] )
    lower_arm_distance_shape = mc.distanceDimension( startPoint=[1.0,0.0,0.0], endPoint=[10.0,0.0,0.0] )
    stretch_distance_shape = mc.distanceDimension( startPoint=[1.0,0.0,0.0], endPoint=[10.0,0.0,0.0] )


    # attach measure distance node to appropriate locators
    mc.connectAttr(name + side + '_upper_arm_loc_01.worldPosition[0]', IK_control_distance_shape + '.startPoint', force=True)
    mc.connectAttr(name + side + '_IK_arm_cc_distance_loc_01.worldPosition[0]', IK_control_distance_shape + '.endPoint', force=True)

    mc.connectAttr(name + side + '_wrist_IK_loc_01.worldPosition[0]', soft_distance_shape + '.startPoint', force=True)
    mc.connectAttr(name + side + '_arm_soft_blend_IK_loc_01.worldPosition[0]', soft_distance_shape + '.endPoint', force=True)

    mc.connectAttr(name + side + '_upper_arm_loc_01.worldPosition[0]', upper_arm_distance_shape + '.startPoint', force=True)
    mc.connectAttr(name + side + '_lower_arm_loc_01.worldPosition[0]', upper_arm_distance_shape + '.endPoint', force=True)

    mc.connectAttr(name + side + '_lower_arm_loc_01.worldPosition[0]', lower_arm_distance_shape + '.startPoint', force=True)
    mc.connectAttr(name + side + '_arm_soft_blend_IK_loc_01.worldPosition[0]', lower_arm_distance_shape + '.endPoint', force=True)

    mc.connectAttr(name + side + '_upper_arm_loc_01.worldPosition[0]', stretch_distance_shape + '.startPoint', force=True)
    mc.connectAttr(name + side + '_arm_soft_blend_IK_loc_01.worldPosition[0]', stretch_distance_shape + '.endPoint', force=True)


    # rename measure distance nodes
    mc.rename(mc.listRelatives(IK_control_distance_shape, parent=True), name + side + '_arm_IK_control_distance_01')
    mc.rename(mc.listRelatives(soft_distance_shape, parent=True), name + side + '_arm_soft_distance_01')
    mc.rename(mc.listRelatives(upper_arm_distance_shape, parent=True), name + side + '_upper_arm_distance_01')
    mc.rename(mc.listRelatives(lower_arm_distance_shape, parent=True), name + side + '_lower_arm_distance_01')
    mc.rename(mc.listRelatives(stretch_distance_shape, parent=True), name + side + '_arm_stretch_distance_01')

    # get rid of spare locators
    mc.delete('locator*')


    """
    Basic "soft" setup
    """

    # create condition nodes
    mc.shadingNode('condition', asUtility=True, name= name + side + '_arm_ik_control_distance_greater_than_chain_length_minus_soft_parameter_COND_01')
    mc.setAttr( name + side + '_arm_ik_control_distance_greater_than_chain_length_minus_soft_parameter_COND_01.operation', 2)
    mc.shadingNode('condition', asUtility=True, name= name + side + '_arm_soft_parameter_greater_than_zero_COND_01')
    mc.setAttr( name + side + '_arm_soft_parameter_greater_than_zero_COND_01.operation', 2)

    # create plus minus average nodes
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_arm_chain_length_minus_soft_parameter_PMA_01')
    mc.setAttr( name + side + '_arm_chain_length_minus_soft_parameter_PMA_01.operation', 2)
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_arm_chain_length_CONS_01')
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_arm_control_distance_minus_chain_length_minus_soft_parameter_PMA_01')
    mc.setAttr( name + side + '_arm_control_distance_minus_chain_length_minus_soft_parameter_PMA_01.operation', 2)
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_arm_chain_length_minus_input_PMA_01')
    mc.setAttr( name + side + '_arm_chain_length_minus_input_PMA_01.operation', 2)

    # create multiply divide nodes
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_arm_input_divide_by_soft_parameter_MD_01')
    mc.setAttr( name + side + '_arm_input_divide_by_soft_parameter_MD_01.operation', 2)
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_arm_input_multiply_by_negative_one_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_arm_e_to_the_input_power_MD_01')
    mc.setAttr( name + side + '_arm_e_to_the_input_power_MD_01.operation', 3)
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_arm_input_multiply_by_soft_parameter_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_arm_divide_one_by_total_scale_MD_01')
    mc.setAttr( name + side + '_arm_divide_one_by_total_scale_MD_01.operation', 2)
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_arm_input_multiply_by_control_distance_MD_01')
    mc.setAttr( name + side + '_arm_input_multiply_by_control_distance_MD_01.operation', 1)
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_arm_diminish_soft_parameter_MD_01')
    mc.setAttr( name + side + '_arm_diminish_soft_parameter_MD_01.operation', 1)
    mc.setAttr( name + side + '_arm_diminish_soft_parameter_MD_01.input2X', 0.01)


    # make connections and initialize values
    mc.connectAttr( name + side + '_upper_arm_distance_0Shape1.distance', name + side + '_arm_chain_length_CONS_01.input3D[0].input3Dx', force=True)
    mc.connectAttr( name + side + '_lower_arm_distance_0Shape1.distance', name + side + '_arm_chain_length_CONS_01.input3D[1].input3Dx', force=True)
    mc.connectAttr( name + side + '_arm_chain_length_CONS_01.output3Dx', name + side + '_arm_chain_length_minus_soft_parameter_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_arm_settings_cc_01.soft_parameter', name + side + '_arm_diminish_soft_parameter_MD_01.input1X', force=True)
    mc.connectAttr( name + side + '_arm_diminish_soft_parameter_MD_01.outputX', name + side + '_arm_chain_length_minus_soft_parameter_PMA_01.input3D[1].input3Dx', force=True)
    mc.connectAttr( name + side + '_arm_input_multiply_by_control_distance_MD_01.outputX', name + side + '_arm_ik_control_distance_greater_than_chain_length_minus_soft_parameter_COND_01.firstTerm', force=True)
    mc.connectAttr( name + side + '_arm_chain_length_minus_soft_parameter_PMA_01.output3Dx', name + side + '_arm_ik_control_distance_greater_than_chain_length_minus_soft_parameter_COND_01.secondTerm', force=True)
    mc.connectAttr( name + side + '_arm_diminish_soft_parameter_MD_01.outputX', name + side + '_arm_soft_parameter_greater_than_zero_COND_01.firstTerm', force=True)
    mc.connectAttr( name + side + '_arm_chain_length_CONS_01.output3Dx', name + side + '_arm_soft_parameter_greater_than_zero_COND_01.colorIfFalse.colorIfFalseR', force=True)
    mc.connectAttr( name + side + '_arm_input_multiply_by_control_distance_MD_01.outputX', name + side + '_arm_control_distance_minus_chain_length_minus_soft_parameter_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr( name + side + '_arm_chain_length_minus_soft_parameter_PMA_01.output3Dx', name + side + '_arm_control_distance_minus_chain_length_minus_soft_parameter_PMA_01.input3D[1].input3Dx', force=True)
    mc.connectAttr( name + side + '_arm_control_distance_minus_chain_length_minus_soft_parameter_PMA_01.output3Dx', name + side + '_arm_input_divide_by_soft_parameter_MD_01.input1X', force=True)
    mc.connectAttr( name + side + '_arm_diminish_soft_parameter_MD_01.outputX', name + side + '_arm_input_divide_by_soft_parameter_MD_01.input2X', force=True)
    mc.connectAttr( name + side + '_arm_input_divide_by_soft_parameter_MD_01.outputX', name + side + '_arm_input_multiply_by_negative_one_MD_01.input1X', force=True)
    mc.setAttr( name + side + '_arm_input_multiply_by_negative_one_MD_01.input2X', -1.0)
    mc.setAttr( name + side + '_arm_e_to_the_input_power_MD_01.input1X', 2.718282)
    mc.connectAttr( name + side + '_arm_input_multiply_by_negative_one_MD_01.outputX', name + side + '_arm_e_to_the_input_power_MD_01.input2X', force=True)
    mc.connectAttr( name + side + '_arm_e_to_the_input_power_MD_01.outputX', name + side + '_arm_input_multiply_by_soft_parameter_MD_01.input1X', force=True)
    mc.connectAttr( name + side + '_arm_diminish_soft_parameter_MD_01.outputX', name + side + '_arm_input_multiply_by_soft_parameter_MD_01.input2X', force=True)
    mc.connectAttr( name + side + '_arm_chain_length_CONS_01.output3Dx', name + side + '_arm_chain_length_minus_input_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr( name + side + '_arm_input_multiply_by_soft_parameter_MD_01.outputX', name + side + '_arm_chain_length_minus_input_PMA_01.input3D[1].input3Dx', force=True)
    mc.connectAttr( name + side + '_arm_chain_length_minus_input_PMA_01.output3Dx', name + side + '_arm_soft_parameter_greater_than_zero_COND_01.colorIfTrue.colorIfTrueR', force=True)
    mc.connectAttr( name + side + '_arm_soft_parameter_greater_than_zero_COND_01.outColor.outColorR', name + side + '_arm_ik_control_distance_greater_than_chain_length_minus_soft_parameter_COND_01.colorIfTrue.colorIfTrueR', force=True)
    mc.connectAttr( name + side + '_arm_input_multiply_by_control_distance_MD_01.outputX', name + side + '_arm_ik_control_distance_greater_than_chain_length_minus_soft_parameter_COND_01.colorIfFalse.colorIfFalseR', force=True)
    mc.connectAttr( name + side + '_arm_ik_control_distance_greater_than_chain_length_minus_soft_parameter_COND_01.outColor.outColorR', name + side + '_wrist_IK_loc_01.translateX', force=True)
    mc.connectAttr( name + '_secret_total_scale_MD_01.outputX', name + side + '_arm_divide_one_by_total_scale_MD_01.input2X', force=True)
    mc.setAttr( name + side + '_arm_divide_one_by_total_scale_MD_01.input1X', 1.0)
    mc.connectAttr( name + side + '_arm_divide_one_by_total_scale_MD_01.outputX', name + side + '_arm_input_multiply_by_control_distance_MD_01.input1X', force=True)
    mc.connectAttr( name + side + '_arm_IK_control_distance_0Shape1.distance', name + side + '_arm_input_multiply_by_control_distance_MD_01.input2X', force=True)


    # convert PMA to CONS (made by disconnecting PMA inputs to convert a plus minus average node into a constant node)
    mc.disconnectAttr( name + side + '_lower_arm_distance_0Shape1.distance', name + side + '_arm_chain_length_CONS_01.input3D[1].input3Dx')
    mc.disconnectAttr( name + side + '_upper_arm_distance_0Shape1.distance', name + side + '_arm_chain_length_CONS_01.input3D[0].input3Dx')


    # point constrain soft blend locator to wrist locator and IK control
    mc.pointConstraint(name + side + "_wrist_IK_loc_01", name + side + '_IK_arm_cc_01', name + side + "_arm_soft_blend_IK_loc_01" )

    # create remap value node and inverse to assign weights to point constraint
    mc.shadingNode('remapValue', asUtility=True, name= name + side + '_arm_IK_stretch_weight_RMV_01')
    mc.setAttr( name + side + '_arm_IK_stretch_weight_RMV_01.value[0].value_Interp', 2)
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_arm_invert_IK_stretch_weight_RMV_01')
    mc.setAttr( name + side + '_arm_invert_IK_stretch_weight_RMV_01.operation', 2)
    mc.setAttr(name + side + '_arm_invert_IK_stretch_weight_RMV_01.input3D[0].input3Dx', 1.0)
    mc.connectAttr(name + side + '_arm_IK_stretch_weight_RMV_01.outValue', name + side + '_arm_invert_IK_stretch_weight_RMV_01.input3D[1].input3Dx', force=True)
    mc.connectAttr(name + side + '_arm_settings_cc_01.stretch_parameter', name + side + '_arm_IK_stretch_weight_RMV_01.inputValue', force=True)
    mc.connectAttr(name + side + '_arm_IK_stretch_weight_RMV_01.outValue', name + side + '_arm_soft_blend_IK_loc_01_pointConstraint1.' + name + side + '_IK_arm_cc_01W1', force=True)
    mc.connectAttr(name + side + '_arm_invert_IK_stretch_weight_RMV_01.output3Dx', name + side + '_arm_soft_blend_IK_loc_01_pointConstraint1.' + name + side + '_wrist_IK_loc_01W0', force=True)


    """
    Upper arm stretch setup
    """

    # create plus minus average nodes
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_upper_arm_bone_length_CONS_01')
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_upper_arm_bone_length_plus_input_PMA_01')

    # create multiply divide nodes
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_upper_arm_bone_length_divide_by_chain_length_MD_01')
    mc.setAttr( name + side + '_upper_arm_bone_length_divide_by_chain_length_MD_01.operation', 2)
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_upper_arm_input_multiply_by_inverse_total_scale_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_upper_arm_input_multiply_by_soft_length_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_upper_arm_input_multiply_by_stretch_parameter_MD_01')

    # make connections and initialize values
    mc.connectAttr(name + side + '_lower_arm_IK_JNT_01.translateX', name + side + '_upper_arm_bone_length_CONS_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_upper_arm_bone_length_CONS_01.output3Dx', name + side + '_upper_arm_bone_length_divide_by_chain_length_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_arm_chain_length_CONS_01.output3Dx', name + side + '_upper_arm_bone_length_divide_by_chain_length_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_arm_divide_one_by_total_scale_MD_01.outputX', name + side + '_upper_arm_input_multiply_by_inverse_total_scale_MD_01.input1X',  force=True)
    mc.connectAttr(name + side + '_arm_soft_distance_01.distance', name + side + '_upper_arm_input_multiply_by_inverse_total_scale_MD_01.input2X',  force=True)
    mc.connectAttr(name + side + '_upper_arm_input_multiply_by_inverse_total_scale_MD_01.outputX', name + side + '_upper_arm_input_multiply_by_soft_length_MD_01.input1X',  force=True)
    mc.connectAttr(name + side + '_upper_arm_bone_length_divide_by_chain_length_MD_01.outputX', name + side + '_upper_arm_input_multiply_by_soft_length_MD_01.input2X',  force=True)
    mc.connectAttr(name + side + '_upper_arm_input_multiply_by_soft_length_MD_01.outputX', name + side + '_upper_arm_input_multiply_by_stretch_parameter_MD_01.input1X',  force=True)
    mc.connectAttr(name + side + '_arm_settings_cc_01.stretch_parameter', name + side + '_upper_arm_input_multiply_by_stretch_parameter_MD_01.input2X',  force=True)
    mc.connectAttr(name + side + '_upper_arm_input_multiply_by_stretch_parameter_MD_01.outputX', name + side + '_upper_arm_bone_length_plus_input_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_upper_arm_bone_length_CONS_01.output3Dx', name + side + '_upper_arm_bone_length_plus_input_PMA_01.input3D[1].input3Dx', force=True)

    # convert PMA to CONS (made by disconnecting PMA inputs to convert a plus minus average node into a constant node)
    mc.disconnectAttr( name + side + '_lower_arm_IK_JNT_01.translateX', name + side + '_upper_arm_bone_length_CONS_01.input3D[0].input3Dx')
    if side=="_RGT":
        true_length=mc.getAttr(name + side + '_upper_arm_bone_length_CONS_01.input3D[0].input3Dx')*-1.0
        mc.setAttr(name + side + '_upper_arm_bone_length_CONS_01.input3D[0].input3Dx', true_length)

    """
    Lower arm stretch setup
    """

    # create plus minus average nodes
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_lower_arm_bone_length_CONS_01')
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_lower_arm_bone_length_plus_input_PMA_01')

    # create multiply divide nodes
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_lower_arm_bone_length_divide_by_chain_length_MD_01')
    mc.setAttr( name + side + '_lower_arm_bone_length_divide_by_chain_length_MD_01.operation', 2)
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_lower_arm_input_multiply_by_inverse_total_scale_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_lower_arm_input_multiply_by_soft_length_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_lower_arm_input_multiply_by_stretch_parameter_MD_01')

    # make connections and initialize values
    mc.connectAttr(name + side + '_wrist_IK_point_JNT_01.translateX', name + side + '_lower_arm_bone_length_CONS_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_lower_arm_bone_length_CONS_01.output3Dx', name + side + '_lower_arm_bone_length_divide_by_chain_length_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_arm_chain_length_CONS_01.output3Dx', name + side + '_lower_arm_bone_length_divide_by_chain_length_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_arm_divide_one_by_total_scale_MD_01.outputX', name + side + '_lower_arm_input_multiply_by_inverse_total_scale_MD_01.input1X',  force=True)
    mc.connectAttr(name + side + '_arm_soft_distance_01.distance', name + side + '_lower_arm_input_multiply_by_inverse_total_scale_MD_01.input2X',  force=True)
    mc.connectAttr(name + side + '_lower_arm_input_multiply_by_inverse_total_scale_MD_01.outputX', name + side + '_lower_arm_input_multiply_by_soft_length_MD_01.input1X',  force=True)
    mc.connectAttr(name + side + '_lower_arm_bone_length_divide_by_chain_length_MD_01.outputX', name + side + '_lower_arm_input_multiply_by_soft_length_MD_01.input2X',  force=True)
    mc.connectAttr(name + side + '_lower_arm_input_multiply_by_soft_length_MD_01.outputX', name + side + '_lower_arm_input_multiply_by_stretch_parameter_MD_01.input1X',  force=True)
    mc.connectAttr(name + side + '_arm_settings_cc_01.stretch_parameter', name + side + '_lower_arm_input_multiply_by_stretch_parameter_MD_01.input2X',  force=True)
    mc.connectAttr(name + side + '_lower_arm_input_multiply_by_stretch_parameter_MD_01.outputX', name + side + '_lower_arm_bone_length_plus_input_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_lower_arm_bone_length_CONS_01.output3Dx', name + side + '_lower_arm_bone_length_plus_input_PMA_01.input3D[1].input3Dx', force=True)

    # convert PMA to CONS (made by disconnecting PMA inputs to convert a plus minus average node into a constant node)
    mc.disconnectAttr( name + side + '_wrist_IK_point_JNT_01.translateX', name + side + '_lower_arm_bone_length_CONS_01.input3D[0].input3Dx')
    if side=="_RGT":
        true_length=mc.getAttr(name + side + '_lower_arm_bone_length_CONS_01.input3D[0].input3Dx')*-1.0
        mc.setAttr(name + side + '_lower_arm_bone_length_CONS_01.input3D[0].input3Dx', true_length)


    """
    Upper arm pin setup
    """

    # create condition nodes
    mc.shadingNode('condition', asUtility=True, name= name + side + '_upper_arm_pin_length_greater_than_bone_length_COND_01')
    mc.setAttr( name + side + '_upper_arm_pin_length_greater_than_bone_length_COND_01.operation', 1)

    # create blend two attr nodes
    mc.shadingNode('blendTwoAttr', asUtility=True, name= name + side + '_upper_arm_pin_BLEND_01')

    # create multiply divide nodes
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_upper_arm_distance_multiply_by_inverse_scale_MD_01')
    if side=="_RGT":
        mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_upper_arm_length_reinvert_MD_01')
        mc.setAttr(name + side + '_upper_arm_length_reinvert_MD_01.input2X', -1.0)


    # make connections and initialize values
    mc.connectAttr(name + side + '_upper_arm_distance_01.distance', name + side + '_upper_arm_distance_multiply_by_inverse_scale_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_arm_divide_one_by_total_scale_MD_01.outputX', name + side + '_upper_arm_distance_multiply_by_inverse_scale_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_upper_arm_distance_multiply_by_inverse_scale_MD_01.outputX', name + side + '_upper_arm_pin_length_greater_than_bone_length_COND_01.firstTerm', force=True)
    mc.connectAttr(name + side + '_upper_arm_distance_multiply_by_inverse_scale_MD_01.outputX', name + side + '_upper_arm_pin_length_greater_than_bone_length_COND_01.colorIfTrue.colorIfTrueR', force=True)
    mc.connectAttr(name + side + '_upper_arm_bone_length_plus_input_PMA_01.output3Dx', name + side + '_upper_arm_pin_BLEND_01.input[0]', force=True)
    mc.connectAttr(name + side + '_upper_arm_pin_length_greater_than_bone_length_COND_01.outColorR', name + side + '_upper_arm_pin_BLEND_01.input[1]', force=True)
    mc.connectAttr(name + side + '_arm_settings_cc_01.pin_parameter', name + side + '_upper_arm_pin_BLEND_01.attributesBlender', force=True)
    mc.connectAttr(name + side + '_upper_arm_pin_BLEND_01.output', name + side + '_lower_arm_IK_JNT_01.translateX', force=True)
    if side=="_RGT":
        mc.connectAttr(name + side + '_upper_arm_pin_BLEND_01.output', name + side + '_upper_arm_length_reinvert_MD_01.input1X',force=True)
        mc.connectAttr(name + side + '_upper_arm_length_reinvert_MD_01.outputX', name + side + '_lower_arm_IK_JNT_01.translateX', force=True)


    """
    Lower arm pin setup
    """

    # create condition nodes
    mc.shadingNode('condition', asUtility=True, name= name + side + '_lower_arm_pin_length_greater_than_bone_length_COND_01')
    mc.setAttr( name + side + '_lower_arm_pin_length_greater_than_bone_length_COND_01.operation', 1)

    # create blend two attr nodes
    mc.shadingNode('blendTwoAttr', asUtility=True, name= name + side + '_lower_arm_pin_BLEND_01')

    # create multiply divide nodes
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_lower_arm_distance_multiply_by_inverse_scale_MD_01')
    if side=="_RGT":
        mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_lower_arm_length_reinvert_MD_01')
        mc.setAttr(name + side + '_lower_arm_length_reinvert_MD_01.input2X', -1.0)

    # make connections and initialize values
    mc.connectAttr(name + side + '_lower_arm_distance_01.distance', name + side + '_lower_arm_distance_multiply_by_inverse_scale_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_arm_divide_one_by_total_scale_MD_01.outputX', name + side + '_lower_arm_distance_multiply_by_inverse_scale_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_lower_arm_distance_multiply_by_inverse_scale_MD_01.outputX', name + side + '_lower_arm_pin_length_greater_than_bone_length_COND_01.firstTerm', force=True)
    mc.connectAttr(name + side + '_lower_arm_distance_multiply_by_inverse_scale_MD_01.outputX', name + side + '_lower_arm_pin_length_greater_than_bone_length_COND_01.colorIfTrue.colorIfTrueR', force=True)
    mc.connectAttr(name + side + '_lower_arm_pin_length_greater_than_bone_length_COND_01.outColorR', name + side + '_lower_arm_pin_BLEND_01.input[1]', force=True)
    mc.connectAttr(name + side + '_arm_settings_cc_01.pin_parameter', name + side + '_lower_arm_pin_BLEND_01.attributesBlender', force=True)
    mc.connectAttr(name + side + '_lower_arm_pin_BLEND_01.output', name + side + '_wrist_IK_point_JNT_01.translateX', force=True)
    if side=="_RGT":
        mc.connectAttr(name + side + '_lower_arm_pin_BLEND_01.output', name + side + '_lower_arm_length_reinvert_MD_01.input1X',force=True)
        mc.connectAttr(name + side + '_lower_arm_length_reinvert_MD_01.outputX', name + side + '_wrist_IK_point_JNT_01.translateX', force=True)


    """
    Arm slide setup
    """

    # create condition nodes
    mc.shadingNode('condition', asUtility=True, name= name + side + '_arm_slide_parameter_less_than_zero_COND_01')
    mc.setAttr( name + side + '_arm_slide_parameter_less_than_zero_COND_01.operation', 4)
    mc.shadingNode('condition', asUtility=True, name= name + side + '_stretched_arm_chain_distance_greater_than_chain_distance_COND_01')
    mc.setAttr( name + side + '_stretched_arm_chain_distance_greater_than_chain_distance_COND_01.operation', 2)

    # create plus minus average nodes
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_upper_arm_slide_input_minus_condition_PMA_01')
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_lower_arm_slide_input_minus_condition_PMA_01')
    mc.setAttr( name + side + '_lower_arm_slide_input_minus_condition_PMA_01.operation', 2)

    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_upper_arm_length_constant_plus_slide_condition_output_PMA_01')
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_lower_arm_length_constant_plus_slide_condition_output_PMA_01')



    # create multiply divide nodes
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_upper_arm_input_multiply_by_slide_parameter_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_lower_arm_input_multiply_by_slide_parameter_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_arm_stretch_distance_multiply_by_inverse_total_scale_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_stretchy_arm_chain_length_divided_by_constant_chain_length_MD_01')
    mc.setAttr( name + side + '_stretchy_arm_chain_length_divided_by_constant_chain_length_MD_01.operation', 2)
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_input_multiply_by_upper_arm_constant_length_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_input_multiply_by_lower_arm_constant_length_MD_01')

    # make connections and initialize values
    mc.connectAttr(name + side + '_arm_settings_cc_01.slide_parameter', name + side + '_arm_slide_parameter_less_than_zero_COND_01.firstTerm', force=True)
    mc.connectAttr(name + side + '_upper_arm_bone_length_CONS_01.output3Dx', name + side + '_input_multiply_by_upper_arm_constant_length_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_lower_arm_bone_length_CONS_01.output3Dx', name + side + '_input_multiply_by_lower_arm_constant_length_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_arm_settings_cc_01.slide_parameter', name + side + '_upper_arm_input_multiply_by_slide_parameter_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_arm_settings_cc_01.slide_parameter', name + side + '_lower_arm_input_multiply_by_slide_parameter_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_stretched_arm_chain_distance_greater_than_chain_distance_COND_01.outColor.outColorR', name + side + '_stretchy_arm_chain_length_divided_by_constant_chain_length_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_arm_chain_length_CONS_01.output3Dx', name + side + '_stretchy_arm_chain_length_divided_by_constant_chain_length_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_stretchy_arm_chain_length_divided_by_constant_chain_length_MD_01.outputX', name + side + '_input_multiply_by_upper_arm_constant_length_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_stretchy_arm_chain_length_divided_by_constant_chain_length_MD_01.outputX', name + side + '_input_multiply_by_lower_arm_constant_length_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_input_multiply_by_upper_arm_constant_length_MD_01.outputX', name + side + '_upper_arm_input_multiply_by_slide_parameter_MD_01.input1X',force=True)
    mc.connectAttr(name + side + '_input_multiply_by_lower_arm_constant_length_MD_01.outputX', name + side + '_lower_arm_input_multiply_by_slide_parameter_MD_01.input1X',force=True)
    mc.connectAttr(name + side + '_upper_arm_input_multiply_by_slide_parameter_MD_01.outputX', name + side + '_arm_slide_parameter_less_than_zero_COND_01.colorIfTrue.colorIfTrueR', force=True)
    mc.connectAttr(name + side + '_lower_arm_input_multiply_by_slide_parameter_MD_01.outputX', name + side + '_arm_slide_parameter_less_than_zero_COND_01.colorIfFalse.colorIfFalseR', force=True)
    mc.connectAttr(name + side + '_upper_arm_bone_length_plus_input_PMA_01.output3Dx', name + side + '_upper_arm_slide_input_minus_condition_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_arm_slide_parameter_less_than_zero_COND_01.outColorR', name + side + '_upper_arm_slide_input_minus_condition_PMA_01.input3D[1].input3Dx', force=True)
    mc.connectAttr(name + side + '_lower_arm_bone_length_plus_input_PMA_01.output3Dx', name + side + '_lower_arm_slide_input_minus_condition_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_arm_slide_parameter_less_than_zero_COND_01.outColorR', name + side + '_lower_arm_slide_input_minus_condition_PMA_01.input3D[1].input3Dx', force=True)
    mc.connectAttr(name + side + '_upper_arm_slide_input_minus_condition_PMA_01.output3Dx', name + side + '_upper_arm_pin_BLEND_01.input[0]', force=True)
    mc.connectAttr(name + side + '_lower_arm_slide_input_minus_condition_PMA_01.output3Dx', name + side + '_lower_arm_pin_BLEND_01.input[0]', force=True)
    mc.connectAttr(name + side + '_arm_stretch_distance_01.distance', name + side + '_arm_stretch_distance_multiply_by_inverse_total_scale_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_arm_divide_one_by_total_scale_MD_01.outputX', name + side + '_arm_stretch_distance_multiply_by_inverse_total_scale_MD_01.input2X', force=True)
    mc.connectAttr(name + side + '_arm_stretch_distance_multiply_by_inverse_total_scale_MD_01.outputX', name + side + '_stretched_arm_chain_distance_greater_than_chain_distance_COND_01.firstTerm', force=True)
    mc.connectAttr(name + side + '_arm_chain_length_CONS_01.output3Dx', name + side + '_stretched_arm_chain_distance_greater_than_chain_distance_COND_01.secondTerm', force=True)
    mc.connectAttr(name + side + '_arm_stretch_distance_multiply_by_inverse_total_scale_MD_01.outputX', name + side + '_stretched_arm_chain_distance_greater_than_chain_distance_COND_01.colorIfTrue.colorIfTrueR', force=True)
    mc.connectAttr(name + side + '_arm_chain_length_CONS_01.output3Dx', name + side + '_stretched_arm_chain_distance_greater_than_chain_distance_COND_01.colorIfFalse.colorIfFalseR', force=True)
    mc.connectAttr(name + side + '_upper_arm_bone_length_CONS_01.output3Dx', name + side + '_upper_arm_length_constant_plus_slide_condition_output_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_arm_slide_parameter_less_than_zero_COND_01.outColor.outColorR', name + side + '_upper_arm_length_constant_plus_slide_condition_output_PMA_01.input3D[1].input3Dx', force=True)
    mc.connectAttr(name + side + '_lower_arm_bone_length_CONS_01.output3Dx', name + side + '_lower_arm_length_constant_plus_slide_condition_output_PMA_01.input3D[0].input3Dx', force=True)
    mc.connectAttr(name + side + '_arm_slide_parameter_less_than_zero_COND_01.outColor.outColorR', name + side + '_lower_arm_length_constant_plus_slide_condition_output_PMA_01.input3D[1].input3Dx', force=True)
    mc.connectAttr(name + side + '_upper_arm_length_constant_plus_slide_condition_output_PMA_01.output3Dx', name + side + '_upper_arm_pin_length_greater_than_bone_length_COND_01.secondTerm', force=True)
    mc.connectAttr(name + side + '_upper_arm_length_constant_plus_slide_condition_output_PMA_01.output3Dx', name + side + '_upper_arm_pin_length_greater_than_bone_length_COND_01.colorIfFalse.colorIfFalseR', force=True)
    mc.connectAttr(name + side + '_lower_arm_length_constant_plus_slide_condition_output_PMA_01.output3Dx', name + side + '_lower_arm_pin_length_greater_than_bone_length_COND_01.secondTerm', force=True)
    mc.connectAttr(name + side + '_lower_arm_length_constant_plus_slide_condition_output_PMA_01.output3Dx', name + side + '_lower_arm_pin_length_greater_than_bone_length_COND_01.colorIfFalse.colorIfFalseR', force=True)



    """
    Settings control parent constraining
    """

    # constrain offset group to FK and IK chains
    mc.parentConstraint(name + side + "_wrist_FK_JNT_01", name + side + "_wrist_IK_JNT_01", name + side + "_arm_settings_cc_os_grp_01", maintainOffset=False)

    # create remap value node and inverse to assign weights to parent constraint
    mc.shadingNode('remapValue', asUtility=True, name= name + side + '_arm_settings_cc_parent_constraint_weight_RMV_01')
    mc.setAttr( name + side + '_arm_settings_cc_parent_constraint_weight_RMV_01.value[0].value_Interp', 2)
    mc.shadingNode('plusMinusAverage', asUtility=True, name= name + side + '_arm_settings_cc_parent_constraint_inverse_weight_RMV_01')
    mc.setAttr( name + side + '_arm_settings_cc_parent_constraint_inverse_weight_RMV_01.operation', 2)
    mc.setAttr(name + side + '_arm_settings_cc_parent_constraint_inverse_weight_RMV_01.input3D[0].input3Dx', 1.0)
    mc.connectAttr(name + side + '_arm_settings_cc_parent_constraint_weight_RMV_01.outValue', name + side + '_arm_settings_cc_parent_constraint_inverse_weight_RMV_01.input3D[1].input3Dx', force=True)
    mc.connectAttr(name + side + '_arm_settings_cc_01.fk_ik_parameter', name + side + '_arm_settings_cc_parent_constraint_weight_RMV_01.inputValue', force=True)
    mc.connectAttr(name + side + '_arm_settings_cc_parent_constraint_weight_RMV_01.outValue', name + side + '_arm_settings_cc_os_grp_01_parentConstraint1.' + name + side + '_wrist_IK_JNT_01W1', force=True)
    mc.connectAttr(name + side + '_arm_settings_cc_parent_constraint_inverse_weight_RMV_01.output3Dx', name + side + '_arm_settings_cc_os_grp_01_parentConstraint1.' + name + side + '_wrist_FK_JNT_01W0', force=True)



    """
    Base arm setup
    """

    # create Base joints by duplicating FK chain
    mc.duplicate(name + side + '_upper_arm_FK_JNT_01', renameChildren=True)
    mc.rename(name + side + '_upper_arm_FK_JNT_02', name + side + '_upper_arm_JNT_01')
    mc.rename(name + side + '_lower_arm_FK_JNT_02', name + side + '_lower_arm_JNT_01')
    mc.rename(name + side + '_wrist_FK_JNT_02', name + side + '_wrist_JNT_01')

    # constrain joints to FK and IK chains
    mc.parentConstraint(name + side + "_upper_arm_FK_JNT_01", name + side + "_upper_arm_IK_JNT_01", name + side + "_upper_arm_JNT_01")
    mc.parentConstraint(name + side + "_lower_arm_FK_JNT_01", name + side + "_lower_arm_IK_JNT_01", name + side + "_lower_arm_JNT_01")
    mc.parentConstraint(name + side + "_wrist_FK_JNT_01", name + side + "_wrist_IK_JNT_01", name + side + "_wrist_JNT_01")

    # set constraint weights driven by settings control
    mc.connectAttr(name + side + '_arm_settings_cc_parent_constraint_weight_RMV_01.outValue', name + side + '_wrist_JNT_01_parentConstraint1.' + name + side + '_wrist_IK_JNT_01W1', force=True)
    mc.connectAttr(name + side + '_arm_settings_cc_parent_constraint_inverse_weight_RMV_01.output3Dx', name + side + '_wrist_JNT_01_parentConstraint1.' + name + side + '_wrist_FK_JNT_01W0', force=True)
    mc.connectAttr(name + side + '_arm_settings_cc_parent_constraint_weight_RMV_01.outValue', name + side + '_lower_arm_JNT_01_parentConstraint1.' + name + side + '_lower_arm_IK_JNT_01W1', force=True)
    mc.connectAttr(name + side + '_arm_settings_cc_parent_constraint_inverse_weight_RMV_01.output3Dx', name + side + '_lower_arm_JNT_01_parentConstraint1.' + name + side + '_lower_arm_FK_JNT_01W0', force=True)
    mc.connectAttr(name + side + '_arm_settings_cc_parent_constraint_weight_RMV_01.outValue', name + side + '_upper_arm_JNT_01_parentConstraint1.' + name + side + '_upper_arm_IK_JNT_01W1', force=True)
    mc.connectAttr(name + side + '_arm_settings_cc_parent_constraint_inverse_weight_RMV_01.output3Dx', name + side + '_upper_arm_JNT_01_parentConstraint1.' + name + side + '_upper_arm_FK_JNT_01W0', force=True)




    """
    create pole vector control
    """

    arm_pole_vector_control = control.Control(
                                  prefix = name + side + '_arm_pole_vector',
                                  scale = .20,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = elbow_joint,
                                  rotate_to = '',
                                  parent = '',
                                  shape = 'box',
                                  locked_channels = ['visibility']
                                  )

    # add attribute for determining what the pole vector follows
    mc.addAttr( arm_pole_vector_control.C, shortName='ik_pole_vector_follow_parameter', longName='Follow', attributeType='enum', enumName='Wrist:Shoulder:COG:Global:', keyable=True)

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
    mc.select(name + side + '_upper_arm_IK_JNT_01', replace=True)
    mc.select(name + side + '_lower_arm_IK_JNT_01', add=True)
    mc.select(name + side + '_wrist_IK_point_JNT_01', add=True)
    selList = mc.ls(sl=1)
    pole_vector_position = get_pole_vector_position(selList[0],selList[1],selList[2]);
    mc.move(pole_vector_position.x, pole_vector_position.y, pole_vector_position.z, arm_pole_vector_control.Off, absolute=True)
    mc.select(clear=True)

    # point constrain pole vector locator to pole vector control
    mc.pointConstraint(arm_pole_vector_control.C, name + side + '_lower_arm_loc_01')

    # make pole vector connection line
    pole_vector_line_start = mc.xform( name + side + '_lower_arm_IK_JNT_01', q=True, translation=True, worldSpace=True)
    pole_vector_line_end = mc.xform( arm_pole_vector_control.C, q=True, translation=True, worldSpace=True)
    pole_vector_line = mc.curve( name = name + side + '_arm_pole_vector_line_cc_01', degree=1, point=[pole_vector_line_start, pole_vector_line_end] )
    mc.cluster( pole_vector_line + '.cv[0]', name= name + side + 'pole_vector_CLU_A_01', weightedNode=[ name + side + '_lower_arm_IK_JNT_01', name + side + '_lower_arm_IK_JNT_01' ], bindState=True)
    mc.cluster( pole_vector_line + '.cv[1]', name= name + side + 'pole_vector_CLU_B_01', weightedNode=[ arm_pole_vector_control.C, arm_pole_vector_control.C ], bindState=True)
    mc.parent( pole_vector_line, name + '_no_transform_GRP_01')
    mc.setAttr(pole_vector_line + '.template', True)
    mc.select(clear=True)



    """
    hands
    """
    # create GRP for hand controls
    mc.group(name = name + side + '_hand_controls_GRP_01', empty=True)
    mc.delete(mc.parentConstraint( name + side + '_wrist_JNT_01', name + side + '_hand_controls_GRP_01'))

    # make cupping/splaying control
    hand_cupping_control = control.Control(
                                  prefix = name + side + '_hand_cupping_splaying',
                                  scale = .10,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = wrist_joint,
                                  rotate_to = wrist_joint,
                                  parent = name + side + '_hand_controls_GRP_01',
                                  shape = 'box',
                                  locked_channels = ['visibility', 'translate', 'scale', 'rotateZ']
                                  )

    mc.move(0.0,0.0,-.50, hand_cupping_control.Off, relative=True)
    mc.move(0.0,0.0,.50, hand_cupping_control.C + '.rotatePivot', relative=True)
    mc.move(0.0,0.0,.50, hand_cupping_control.C + '.scalePivot', relative=True)



    # thumb
    if(mc.objExists(name + side + '_thumb_PRO_target_cc_01')):
        mc.select(name + side + '_wrist_JNT_01', replace=True)
        mc.joint(name=name + side + "_thumb_PRO_BN_01", radius=.05)
        mc.delete(mc.parentConstraint(name + side + '_thumb_PRO_target_cc_01', name + side + "_thumb_PRO_BN_01", maintainOffset=False))
        parent_offset_group = transform.make_offset_group(name + side + '_thumb_PRO_BN_01')
        transform.make_offset_group(name + side + '_thumb_PRO_BN_01', prefix = name + side + '_thumb_PRO_JNT_cupping_control')
        transform.make_offset_group(name + side + '_thumb_PRO_BN_01', prefix = name + side + '_thumb_PRO_JNT_primary_control_transforms')

        # make primary control
        thumb_primary_control = control.Control(
                                              prefix = name + side + '_thumb_primary',
                                              scale = 0.05,
                                              use_numerical_transforms = False,
                                              transform_x = 0.0,
                                              transform_y = 0.0,
                                              transform_z = 0.0,
                                              translate_to = name + side + '_thumb_PRO_BN_01',
                                              rotate_to = name + side + '_thumb_PRO_BN_01',
                                              parent = name + side + '_hand_controls_GRP_01',
                                              shape = 'square',
                                              locked_channels = ['visibility']
                                              )
        #add secondaries visibility attribute
        mc.addAttr( thumb_primary_control.C, shortName='bendy_control_visibility_parameter', longName='Secondaries_Visibility', attributeType='enum', enumName='Off:On:', keyable=True)

        # reposition thumb control
        if side == "_LFT":
            mc.select( name + side + '_thumb_primary_cc_01Shape.cv[0:4]' )
            mc.rotate(90.0,0.0,0.0, relative=True)
            mc.scale(5.0,1.0,0.7, relative=True)
            mc.move(.15,.10,0.0, relative=True)
        else:
            mc.select( name + side + '_thumb_primary_cc_01Shape.cv[0:4]' )
            mc.rotate(90.0,0.0,0.0, relative=True)
            mc.scale(5.0,1.0,0.7, relative=True)
            mc.move(-.15,.10,0.0, relative=True)


        # make offset group for control
        transform.make_offset_group(name + side + '_thumb_primary_cc_01', prefix = name + side + '_thumb_primary_cc_cupping_control')

        # make offset group and MD node to counter scaling of primary control
        transform.make_offset_group(name + side + '_thumb_primary_cc_01', prefix = name + side + '_thumb_MED_secondary_cc_primary_scale_reverse')
        mc.parent(name + side + '_thumb_primary_cc_01', world=True)
        mc.parent(name + side + '_thumb_MED_secondary_cc_primary_scale_reverse_os_grp_01', world=True)
        mc.parent(name + side + '_thumb_MED_secondary_cc_primary_scale_reverse_os_grp_01',name + side + '_thumb_primary_cc_01')
        mc.parent(name + side + '_thumb_primary_cc_01', name + side + '_thumb_primary_cc_cupping_control_os_grp_01')
        mc.shadingNode('multiplyDivide', asUtility=True, name=name + side + '_thumb_primary_scale_inverse_MD_01')
        mc.setAttr( name + side + '_thumb_primary_scale_inverse_MD_01.operation', 2)
        mc.setAttr( name + side + '_thumb_primary_scale_inverse_MD_01.input1X', 1.0)
        mc.connectAttr(name + side + '_thumb_primary_cc_01.scaleX', name + side + '_thumb_primary_scale_inverse_MD_01.input2X')
        mc.connectAttr(name + side + '_thumb_primary_scale_inverse_MD_01.outputX', name + side + '_thumb_MED_secondary_cc_primary_scale_reverse_os_grp_01.scaleX')

        # create RMV node for converting primary control's scale X to rotations for further finger joints
        mc.shadingNode('remapValue', asUtility=True, name=name + side + '_thumb_primary_rotate_RMV_01')
        mc.setAttr( name + side + '_thumb_primary_rotate_RMV_01.value[0].value_Interp', 2)
        mc.setAttr( name + side + '_thumb_primary_rotate_RMV_01.inputMin', 0.0)
        mc.setAttr( name + side + '_thumb_primary_rotate_RMV_01.inputMax', 2.0)
        mc.setAttr( name + side + '_thumb_primary_rotate_RMV_01.outputMin', -180.0)
        mc.setAttr( name + side + '_thumb_primary_rotate_RMV_01.outputMax', 180.0)
        mc.connectAttr(thumb_primary_control.C + '.scaleX', name + side + '_thumb_primary_rotate_RMV_01.inputValue', force=True)

        # direct connect translates, scales and rotates of secondary cc to joint
        mc.connectAttr(name + side + '_thumb_primary_cc_01.translate', name + side + '_thumb_PRO_BN_01.translate')
        mc.connectAttr(name + side + '_thumb_primary_cc_01.rotate', name + side + '_thumb_PRO_BN_01.rotate')
        mc.connectAttr(name + side + '_thumb_primary_cc_01.scaleY', name + side + '_thumb_PRO_BN_01.scaleY')
        mc.connectAttr(name + side + '_thumb_primary_cc_01.scaleZ', name + side + '_thumb_PRO_BN_01.scaleZ')
        # select joint for next iteration
        mc.select(name + side + '_thumb_PRO_BN_01')

        # test if has at least two segments
        if(mc.objExists(name + side + '_thumb_MED_target_cc_01')):
            mc.joint(name=name + side + '_thumb_MED_BN_01', radius=.05)
            mc.delete(mc.parentConstraint(name + side + '_thumb_MED_target_cc_01', name + side + '_thumb_MED_BN_01', maintainOffset=False))
            transform.make_offset_group(name + side + '_thumb_MED_BN_01')
            transform.make_offset_group(name + side + '_thumb_MED_BN_01', prefix = name + side + '_thumb_MED_JNT_cupping_control')
            transform.make_offset_group(name + side + '_thumb_MED_BN_01', prefix = name + side + '_thumb_MED_JNT_primary_control_transforms')
            transform.make_offset_group(name + side + '_thumb_MED_BN_01', prefix = name + side + '_thumb_MED_JNT_primary_control')
            # make secondary control
            thumb_MED_secondary_control = control.Control(
                                                         prefix = name + side + '_thumb_MED_secondary',
                                                         scale = 0.05,
                                                         use_numerical_transforms = False,
                                                         transform_x = 0.0,
                                                         transform_y = 0.0,
                                                         transform_z = 0.0,
                                                         translate_to = name + side + '_thumb_MED_BN_01',
                                                         rotate_to = name + side + '_thumb_MED_BN_01',
                                                         parent = name + side + '_thumb_MED_secondary_cc_primary_scale_reverse_os_grp_01',
                                                         shape = 'pin',
                                                         locked_channels = []
                                                         )
            mc.connectAttr(thumb_primary_control.C + '.bendy_control_visibility_parameter', thumb_MED_secondary_control.C + '.visibility', force=True)
            # make offset groups for control
            transform.make_offset_group(name + side + '_thumb_MED_secondary_cc_01', prefix = name + side + '_thumb_MED_secondary_cc_cupping_control')
            transform.make_offset_group(name + side + '_thumb_MED_secondary_cc_01', prefix = name + side + '_thumb_MED_secondary_cc_primary_control_transforms')
            transform.make_offset_group(name + side + '_thumb_MED_secondary_cc_01', prefix = name + side + '_thumb_MED_secondary_cc_primary_control')
            # connect primary control os grp to primary scale RMV node
            mc.connectAttr(name + side + '_thumb_primary_rotate_RMV_01.outValue', name + side + '_thumb_MED_JNT_primary_control_os_grp_01.rotateZ', force=True)
            mc.connectAttr(name + side + '_thumb_primary_rotate_RMV_01.outValue', name + side + '_thumb_MED_secondary_cc_primary_control_os_grp_01.rotateZ', force=True)
            # direct connect translates, scales and rotates of secondary cc to joint
            mc.connectAttr(name + side + '_thumb_MED_secondary_cc_01.translate', name + side + '_thumb_MED_BN_01.translate')
            mc.connectAttr(name + side + '_thumb_MED_secondary_cc_01.rotate', name + side + '_thumb_MED_BN_01.rotate')
            mc.connectAttr(name + side + '_thumb_MED_secondary_cc_01.scale', name + side + '_thumb_MED_BN_01.scale')
            # select joint for next iteration
            mc.select(name + side + '_thumb_MED_BN_01')


        # test if has at least three segments
        if(mc.objExists(name + side + '_thumb_DIS_target_cc_01')):
            mc.joint(name=name + side + '_thumb_DIS_BN_01', radius=.05)
            mc.delete(mc.parentConstraint(name + side + '_thumb_DIS_target_cc_01', name + side + '_thumb_DIS_BN_01', maintainOffset=False))
            transform.make_offset_group(name + side + '_thumb_DIS_BN_01')
            transform.make_offset_group(name + side + '_thumb_DIS_BN_01', prefix = name + side + '_thumb_DIS_JNT_cupping_control')
            transform.make_offset_group(name + side + '_thumb_DIS_BN_01', prefix = name + side + '_thumb_DIS_JNT_primary_control_transforms')
            transform.make_offset_group(name + side + '_thumb_DIS_BN_01', prefix = name + side + '_thumb_DIS_JNT_primary_control')
            # make secondary control
            if(mc.objExists(name + side + '_thumb_MED_target_cc_01')):
                parent_control=name + side + '_thumb_MED_secondary_cc_primary_scale_reverse_os_grp_01'
            else:
                parent_control=name + side + '_thumb_primary_cc_01'
            thumb_DIS_secondary_control = control.Control(
                                                         prefix = name + side + '_thumb_DIS_secondary',
                                                         scale = 0.05,
                                                         use_numerical_transforms = False,
                                                         transform_x = 0.0,
                                                         transform_y = 0.0,
                                                         transform_z = 0.0,
                                                         translate_to = name + side + '_thumb_DIS_BN_01',
                                                         rotate_to = name + side + '_thumb_DIS_BN_01',
                                                         parent = parent_control,
                                                         shape = 'pin',
                                                         locked_channels = []
                                                         )
            mc.connectAttr(thumb_primary_control.C + '.bendy_control_visibility_parameter', thumb_DIS_secondary_control.C + '.visibility', force=True)
            # make offset groups for control
            transform.make_offset_group(name + side + '_thumb_DIS_secondary_cc_01', prefix = name + side + '_thumb_DIS_secondary_cc_cupping_control')
            transform.make_offset_group(name + side + '_thumb_DIS_secondary_cc_01', prefix = name + side + '_thumb_DIS_secondary_cc_primary_control_transforms')
            transform.make_offset_group(name + side + '_thumb_DIS_secondary_cc_01', prefix = name + side + '_thumb_DIS_secondary_cc_primary_control')
            # connect primary control os grp to primary scale RMV node
            mc.connectAttr(name + side + '_thumb_primary_rotate_RMV_01.outValue', name + side + '_thumb_DIS_JNT_primary_control_os_grp_01.rotateZ', force=True)
            mc.connectAttr(name + side + '_thumb_primary_rotate_RMV_01.outValue', name + side + '_thumb_DIS_secondary_cc_primary_control_os_grp_01.rotateZ', force=True)
            # direct connect translates, scales and rotates of secondary cc to joint
            mc.connectAttr(name + side + '_thumb_DIS_secondary_cc_01.translate', name + side + '_thumb_DIS_BN_01.translate')
            mc.connectAttr(name + side + '_thumb_DIS_secondary_cc_01.rotate', name + side + '_thumb_DIS_BN_01.rotate')
            mc.connectAttr(name + side + '_thumb_DIS_secondary_cc_01.scale', name + side + '_thumb_DIS_BN_01.scale')
            # select joint for next iteration
            mc.select(name + side + '_thumb_DIS_BN_01')

        # test if has at least four segments
        if(mc.objExists(name + side + '_thumb_DIS_2_target_cc_01')):
            mc.joint(name=name + side + '_thumb_DIS_2_BN_01', radius=.05)
            mc.delete(mc.parentConstraint(name + side + '_thumb_DIS_2_target_cc_01',name + side + '_thumb_DIS_2_BN_01', maintainOffset=False))
            transform.make_offset_group(name + side + '_thumb_DIS_2_BN_01')
            transform.make_offset_group(name + side + '_thumb_DIS_2_BN_01', prefix = name + side + '_thumb_DIS_2_JNT_cupping_control')
            transform.make_offset_group(name + side + '_thumb_DIS_2_BN_01', prefix = name + side + '_thumb_DIS_2_JNT_primary_control_transforms')
            transform.make_offset_group(name + side + '_thumb_DIS_2_BN_01', prefix = name + side + '_thumb_DIS_2_JNT_primary_control')
            # make secondary control
            thumb_DIS_2_secondary_control = control.Control(
                                                                 prefix = name + side + '_thumb_DIS_2_secondary',
                                                                 scale = 0.05,
                                                                 use_numerical_transforms = False,
                                                                 transform_x = 0.0,
                                                                 transform_y = 0.0,
                                                                 transform_z = 0.0,
                                                                 translate_to = name + side + '_thumb_DIS_2_BN_01',
                                                                 rotate_to = name + side + '_thumb_DIS_2_BN_01',
                                                                 parent = thumb_DIS_secondary_control.C,
                                                                 shape = 'pin',
                                                                 locked_channels = []
                                                                 )
            mc.connectAttr(thumb_primary_control.C + '.bendy_control_visibility_parameter', thumb_DIS_2_secondary_control.C + '.visibility', force=True)
            # make offset groups for control
            transform.make_offset_group(name + side + '_thumb_DIS_2_secondary_cc_01', prefix = name + side + '_thumb_DIS_2_secondary_cc_cupping_control')
            transform.make_offset_group(name + side + '_thumb_DIS_2_secondary_cc_01', prefix = name + side + '_thumb_DIS_2_secondary_cc_primary_control_transforms')
            transform.make_offset_group(name + side + '_thumb_DIS_2_secondary_cc_01', prefix = name + side + '_thumb_DIS_2_secondary_cc_primary_control')
            # connect primary control os grp to primary scale RMV node
            mc.connectAttr(name + side + '_thumb_primary_rotate_RMV_01.outValue', name + side + '_thumb_DIS_2_JNT_primary_control_os_grp_01.rotateZ', force=True)
            mc.connectAttr(name + side + '_thumb_primary_rotate_RMV_01.outValue', name + side + '_thumb_DIS_2_secondary_cc_primary_control_os_grp_01.rotateZ', force=True)
            # direct connect translates, scales and rotates of secondary cc to joint
            mc.connectAttr(name + side + '_thumb_DIS_2_secondary_cc_01.translate', name + side + '_thumb_DIS_2_BN_01.translate')
            mc.connectAttr(name + side + '_thumb_DIS_2_secondary_cc_01.rotate', name + side + '_thumb_DIS_2_BN_01.rotate')
            mc.connectAttr(name + side + '_thumb_DIS_2_secondary_cc_01.scale', name + side + '_thumb_DIS_2_BN_01.scale')
            # select joint for next iteration
            mc.select(name + side + '_thumb_DIS_2_BN_01')

        # test if has at least five segments
        if(mc.objExists(name + side + '_thumb_DIS_3_target_cc_01')):
            mc.joint(name=name + side + '_thumb_DIS_3_BN_01', radius=.05)
            mc.delete(mc.parentConstraint(name + side + '_thumb_DIS_3_target_cc_01', name + side + '_thumb_DIS_3_BN_01', maintainOffset=False))
            transform.make_offset_group(name + side + '_thumb_DIS_3_BN_01')
            transform.make_offset_group(name + side + '_thumb_DIS_3_BN_01', prefix = name + side + '_thumb_DIS_3_JNT_cupping_control')
            transform.make_offset_group(name + side + '_thumb_DIS_3_BN_01', prefix = name + side + '_thumb_DIS_3_JNT_primary_control_transforms')
            transform.make_offset_group(name + side + '_thumb_DIS_3_BN_01', prefix = name + side + '_thumb_DIS_3_JNT_primary_control')
            # make secondary control
            thumb_DIS_3_secondary_control = control.Control(
                                                                 prefix = name + side + '_thumb_DIS_3_secondary',
                                                                 scale = 0.05,
                                                                 use_numerical_transforms = False,
                                                                 transform_x = 0.0,
                                                                 transform_y = 0.0,
                                                                 transform_z = 0.0,
                                                                 translate_to = name + side + '_thumb_DIS_3_BN_01',
                                                                 rotate_to = name + side + '_thumb_DIS_3_BN_01',
                                                                 parent = thumb_DIS_2_secondary_control.C,
                                                                 shape = 'pin',
                                                                 locked_channels = []
                                                                 )
            #visibility
            mc.connectAttr(thumb_primary_control.C + '.bendy_control_visibility_parameter', thumb_DIS_3_secondary_control.C + '.visibility', force=True)
            # make offset groups for control
            transform.make_offset_group(name + side + '_thumb_DIS_3_secondary_cc_01', prefix = name + side + '_thumb_DIS_3_secondary_cc_cupping_control')
            transform.make_offset_group(name + side + '_thumb_DIS_3_secondary_cc_01', prefix = name + side + '_thumb_DIS_3_secondary_cc_primary_control_transforms')
            transform.make_offset_group(name + side + '_thumb_DIS_3_secondary_cc_01', prefix = name + side + '_thumb_DIS_3_secondary_cc_primary_control')
            # connect primary control os grp to primary scale RMV node
            mc.connectAttr(name + side + '_thumb_primary_rotate_RMV_01.outValue', name + side + '_thumb_DIS_3_JNT_primary_control_os_grp_01.rotateZ', force=True)
            mc.connectAttr(name + side + '_thumb_primary_rotate_RMV_01.outValue', name + side + '_thumb_DIS_3_secondary_cc_primary_control_os_grp_01.rotateZ', force=True)
            # direct connect translates, scales and rotates of secondary cc to joint
            mc.connectAttr(name + side + '_thumb_DIS_3_secondary_cc_01.translate', name + side + '_thumb_DIS_3_BN_01.translate')
            mc.connectAttr(name + side + '_thumb_DIS_3_secondary_cc_01.rotate', name + side + '_thumb_DIS_3_BN_01.rotate')
            mc.connectAttr(name + side + '_thumb_DIS_3_secondary_cc_01.scale', name + side + '_thumb_DIS_3_BN_01.scale')
            # select joint for next iteration
            mc.select(name + side + '_thumb_DIS_3_BN_01')

        mc.joint(name=name + side + '_thumb_JNT_END_01', radius=.05)
        mc.delete(mc.parentConstraint(name + side + '_thumb_END_target_cc_01',name + side + '_thumb_JNT_END_01', maintainOffset=False))
        mc.setAttr( name + side + "_thumb_JNT_END_01.jointOrientX", 0)



    # other fingers
    for finger in ['index', 'middle', 'ring', 'pinky', 'second_pinky', 'third_pinky']:

        # base of any finger
        if(mc.objExists(name + side + '_' + finger + '_finger_PRO_target_cc_01')):
            # metacarpal joint
            mc.select(name + side + '_wrist_JNT_01', replace=True)
            mc.joint(name=name + side + '_' + finger + '_metacarpal_BN_01', radius=.05)
            mc.delete(mc.parentConstraint(name + side + '_' + finger + '_finger_metacarpal_target_cc_01', name + side + '_' + finger + '_metacarpal_BN_01', maintainOffset=False))
            parent_offset_group = transform.make_offset_group(name + side + '_' + finger + '_metacarpal_BN_01')
            transform.make_offset_group(name + side + '_' + finger + '_metacarpal_BN_01', prefix = name + side + '_' + finger + '_metacarpal_JNT_cupping_control')
            #metacarpal control
            current_finger_metacarpal_secondary_control = control.Control(
                                                                  prefix = name + side + '_' + finger + '_metacarpal_secondary',
                                                                  scale = 0.05,
                                                                  use_numerical_transforms = False,
                                                                  transform_x = 0.0,
                                                                  transform_y = 0.0,
                                                                  transform_z = 0.0,
                                                                  translate_to = name + side + '_' + finger + '_metacarpal_BN_01',
                                                                  rotate_to = name + side + '_' + finger + '_metacarpal_BN_01',
                                                                  parent = name + side + '_hand_controls_GRP_01',
                                                                  shape = 'pin',
                                                                  locked_channels = []
                                                                  )
            transform.make_offset_group(name + side + '_' + finger + '_metacarpal_secondary_cc_01', prefix = name + side + '_' + finger + '_metacarpal_secondary_cc_cupping_control')
            # direct connect translates, scales and rotates of secondary cc to joint
            mc.connectAttr(name + side + '_' + finger + '_metacarpal_secondary_cc_01.translate', name + side + '_' + finger + '_metacarpal_BN_01.translate')
            mc.connectAttr(name + side + '_' + finger + '_metacarpal_secondary_cc_01.rotate', name + side + '_' + finger + '_metacarpal_BN_01.rotate')
            mc.connectAttr(name + side + '_' + finger + '_metacarpal_secondary_cc_01.scale', name + side + '_' + finger + '_metacarpal_BN_01.scale')
            # select joint for next iteration
            mc.select(name + side + '_' + finger + '_metacarpal_BN_01', replace=True)
            # proximal phalange
            mc.joint(name=name + side + '_' + finger + '_finger_PRO_BN_01', radius=.05)
            mc.delete(mc.parentConstraint(name + side + '_' + finger + '_finger_PRO_target_cc_01', name + side + '_' + finger + '_finger_PRO_BN_01', maintainOffset=False))
            parent_offset_group = transform.make_offset_group(name + side + '_' + finger + '_finger_PRO_BN_01')
            transform.make_offset_group(name + side + '_' + finger + '_finger_PRO_BN_01', prefix = name + side + '_' + finger + '_finger_PRO_JNT_cupping_control')
            transform.make_offset_group(name + side + '_' + finger + '_finger_PRO_BN_01', prefix = name + side + '_' + finger + '_finger_PRO_JNT_primary_control_transforms')

            # make primary control
            current_finger_primary_control = control.Control(
                                                          prefix = name + side + '_' + finger + '_finger_primary',
                                                          scale = 0.05,
                                                          use_numerical_transforms = False,
                                                          transform_x = 0.0,
                                                          transform_y = 0.0,
                                                          transform_z = 0.0,
                                                          translate_to = name + side + '_' + finger + '_finger_PRO_BN_01',
                                                          rotate_to = name + side + '_' + finger + '_finger_PRO_BN_01',
                                                          parent = current_finger_metacarpal_secondary_control.C,
                                                          shape = 'square',
                                                          locked_channels = ['visibility']
                                                          )
            #add secondaries visibility attribute
            mc.addAttr( current_finger_primary_control.C, shortName='bendy_control_visibility_parameter', longName='Secondaries_Visibility', attributeType='enum', enumName='Off:On:', keyable=True)
            #take care of metacarpal visibility now that primary control is made
            metacarpal_shapes = mc.listRelatives(current_finger_metacarpal_secondary_control.C, children=True, type='nurbsCurve')
            for metacarpal_shape in metacarpal_shapes:
                mc.connectAttr(current_finger_primary_control.C + '.bendy_control_visibility_parameter', metacarpal_shape + '.visibility', force=True)


            # position primary control
            if side == "_LFT":
                mc.select( name + side + '_' + finger + '_finger_primary_cc_01Shape.cv[0:4]' )
                mc.rotate(90.0,0.0,0.0, relative=True)
                mc.scale(5.0,1.0,0.7, relative=True)
                mc.move(.15,0.07,0.0, relative=True)

            else:
                mc.select( name + side + '_' + finger + '_finger_primary_cc_01Shape.cv[0:4]' )
                mc.rotate(90.0,0.0,0.0, relative=True)
                mc.scale(5.0,1.0,0.7, relative=True)
                mc.move(-.15,0.07,0.0, relative=True)


            # make offset group for control
            transform.make_offset_group(name + side + '_' + finger + '_finger_primary_cc_01', prefix = name + side + '_' + finger + '_finger_primary_cc_cupping_control')
            # make offset group and MD node to counter scaling of primary control
            transform.make_offset_group(name + side + '_' + finger + '_finger_primary_cc_01', prefix = name + side + '_' + finger + '_finger_MED_secondary_cc_primary_scale_reverse')
            mc.parent(name + side + '_' + finger + '_finger_primary_cc_01', world=True)
            mc.parent(name + side + '_' + finger + '_finger_MED_secondary_cc_primary_scale_reverse_os_grp_01', world=True)
            mc.parent(name + side + '_' + finger + '_finger_MED_secondary_cc_primary_scale_reverse_os_grp_01',name + side + '_' + finger + '_finger_primary_cc_01')
            mc.parent(name + side + '_' + finger + '_finger_primary_cc_01', name + side + '_' + finger + '_finger_primary_cc_cupping_control_os_grp_01')
            mc.shadingNode('multiplyDivide', asUtility=True, name=name + side + '_' + finger + '_finger_primary_scale_inverse_MD_01')
            mc.setAttr( name + side + '_' + finger + '_finger_primary_scale_inverse_MD_01.operation', 2)
            mc.setAttr( name + side + '_' + finger + '_finger_primary_scale_inverse_MD_01.input1X', 1.0)
            mc.connectAttr(name + side + '_' + finger + '_finger_primary_cc_01.scaleX', name + side + '_' + finger + '_finger_primary_scale_inverse_MD_01.input2X')
            mc.connectAttr(name + side + '_' + finger + '_finger_primary_scale_inverse_MD_01.outputX', name + side + '_' + finger + '_finger_MED_secondary_cc_primary_scale_reverse_os_grp_01.scaleX')
            # create RMV node for converting primary control's scale X to rotations for further finger joints
            mc.shadingNode('remapValue', asUtility=True, name=name + side + '_' + finger + '_finger_primary_rotate_RMV_01')
            mc.setAttr( name + side + '_' + finger + '_finger_primary_rotate_RMV_01.value[0].value_Interp', 2)
            mc.setAttr( name + side + '_' + finger + '_finger_primary_rotate_RMV_01.inputMin', 0.0)
            mc.setAttr( name + side + '_' + finger + '_finger_primary_rotate_RMV_01.inputMax', 2.0)
            mc.setAttr( name + side + '_' + finger + '_finger_primary_rotate_RMV_01.outputMin', -180.0)
            mc.setAttr( name + side + '_' + finger + '_finger_primary_rotate_RMV_01.outputMax', 180.0)
            mc.connectAttr(current_finger_primary_control.C + '.scaleX', name + side + '_' + finger + '_finger_primary_rotate_RMV_01.inputValue', force=True)
            # direct connect translates, scales and rotates of secondary cc to joint
            mc.connectAttr(name + side + '_' + finger + '_finger_primary_cc_01.translate', name + side + '_' + finger + '_finger_PRO_BN_01.translate')
            mc.connectAttr(name + side + '_' + finger + '_finger_primary_cc_01.rotate', name + side + '_' + finger + '_finger_PRO_BN_01.rotate')
            mc.connectAttr(name + side + '_' + finger + '_finger_primary_cc_01.scaleY', name + side + '_' + finger + '_finger_PRO_BN_01.scaleY')
            mc.connectAttr(name + side + '_' + finger + '_finger_primary_cc_01.scaleZ', name + side + '_' + finger + '_finger_PRO_BN_01.scaleZ')
            # select joint for next iteration
            mc.select(name + side + '_' + finger + '_finger_PRO_BN_01')

            # test if has at least two segments
            if(mc.objExists(name + side + '_' + finger + '_finger_MED_target_cc_01')):
                mc.joint(name=name + side + '_' + finger + '_finger_MED_BN_01', radius=.05)
                mc.delete(mc.parentConstraint(name + side + '_' + finger + '_finger_MED_target_cc_01', name + side + '_' + finger + '_finger_MED_BN_01', maintainOffset=False))
                transform.make_offset_group(name + side + '_' + finger + '_finger_MED_BN_01')
                transform.make_offset_group(name + side + '_' + finger + '_finger_MED_BN_01', prefix = name + side + '_' + finger + '_finger_MED_JNT_cupping_control')
                transform.make_offset_group(name + side + '_' + finger + '_finger_MED_BN_01', prefix = name + side + '_' + finger + '_finger_MED_JNT_primary_control_transforms')
                transform.make_offset_group(name + side + '_' + finger + '_finger_MED_BN_01', prefix = name + side + '_' + finger + '_finger_MED_JNT_primary_control')
                # make secondary control
                current_finger_MED_secondary_control = control.Control(
                                                                      prefix = name + side + '_' + finger + '_finger_MED_secondary',
                                                                      scale = 0.05,
                                                                      use_numerical_transforms = False,
                                                                      transform_x = 0.0,
                                                                      transform_y = 0.0,
                                                                      transform_z = 0.0,
                                                                      translate_to = name + side + '_' + finger + '_finger_MED_BN_01',
                                                                      rotate_to = name + side + '_' + finger + '_finger_MED_BN_01',
                                                                      parent = name + side + '_' + finger + '_finger_MED_secondary_cc_primary_scale_reverse_os_grp_01',
                                                                      shape = 'pin',
                                                                      locked_channels = []
                                                                      )
                #visibility
                mc.connectAttr(current_finger_primary_control.C + '.bendy_control_visibility_parameter', current_finger_MED_secondary_control.C + '.visibility', force=True)

                # make offset groups for control
                transform.make_offset_group(name + side + '_' + finger + '_finger_MED_secondary_cc_01', prefix = name + side + '_' + finger + '_finger_MED_secondary_cc_cupping_control')
                transform.make_offset_group(name + side + '_' + finger + '_finger_MED_secondary_cc_01', prefix = name + side + '_' + finger + '_finger_MED_secondary_cc_primary_control_transforms')
                transform.make_offset_group(name + side + '_' + finger + '_finger_MED_secondary_cc_01', prefix = name + side + '_' + finger + '_finger_MED_secondary_cc_primary_control')
                # connect primary control os grp to primary scale RMV node
                mc.connectAttr(name + side + '_' + finger + '_finger_primary_rotate_RMV_01.outValue', name + side + '_' + finger + '_finger_MED_JNT_primary_control_os_grp_01.rotateZ', force=True)
                mc.connectAttr(name + side + '_' + finger + '_finger_primary_rotate_RMV_01.outValue', name + side + '_' + finger + '_finger_MED_secondary_cc_primary_control_os_grp_01.rotateZ', force=True)
                # direct connect translates, scales and rotates of secondary cc to joint
                mc.connectAttr(name + side + '_' + finger + '_finger_MED_secondary_cc_01.translate', name + side + '_' + finger + '_finger_MED_BN_01.translate')
                mc.connectAttr(name + side + '_' + finger + '_finger_MED_secondary_cc_01.rotate', name + side + '_' + finger + '_finger_MED_BN_01.rotate')
                mc.connectAttr(name + side + '_' + finger + '_finger_MED_secondary_cc_01.scale', name + side + '_' + finger + '_finger_MED_BN_01.scale')
                # select joint for next iteration
                mc.select(name + side + '_' + finger + '_finger_MED_BN_01')


            # test if has at least three segments
            if(mc.objExists(name + side + '_' + finger + '_finger_DIS_target_cc_01')):
                mc.joint(name=name + side + '_' + finger + '_finger_DIS_BN_01', radius=.05)
                mc.delete(mc.parentConstraint(name + side + '_' + finger + '_finger_DIS_target_cc_01', name + side + '_' + finger + '_finger_DIS_BN_01', maintainOffset=False))
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_BN_01')
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_BN_01', prefix = name + side + '_' + finger + '_finger_DIS_JNT_cupping_control')
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_BN_01', prefix = name + side + '_' + finger + '_finger_DIS_JNT_primary_control_transforms')
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_BN_01', prefix = name + side + '_' + finger + '_finger_DIS_JNT_primary_control')
                # make secondary control
                if(mc.objExists(name + side + '_' + finger + '_finger_MED_target_cc_01')):
                    parent_control=name + side + '_' + finger + '_finger_MED_secondary_cc_01'
                else:
                    parent_control=name + side + '_' + finger + '_finger_MED_secondary_cc_primary_scale_reverse_os_grp_01'
                current_finger_DIS_secondary_control = control.Control(
                                                                      prefix = name + side + '_' + finger + '_finger_DIS_secondary',
                                                                      scale = 0.05,
                                                                      use_numerical_transforms = False,
                                                                      transform_x = 0.0,
                                                                      transform_y = 0.0,
                                                                      transform_z = 0.0,
                                                                      translate_to = name + side + '_' + finger + '_finger_DIS_BN_01',
                                                                      rotate_to = name + side + '_' + finger + '_finger_DIS_BN_01',
                                                                      parent = parent_control,
                                                                      shape = 'pin',
                                                                      locked_channels = []
                                                                      )
                #visibility
                mc.connectAttr(current_finger_primary_control.C + '.bendy_control_visibility_parameter', current_finger_DIS_secondary_control.C + '.visibility', force=True)

                # make offset groups for control
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_secondary_cc_01', prefix = name + side + '_' + finger + '_finger_DIS_secondary_cc_cupping_control')
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_secondary_cc_01', prefix = name + side + '_' + finger + '_finger_DIS_secondary_cc_primary_control_transforms')
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_secondary_cc_01', prefix = name + side + '_' + finger + '_finger_DIS_secondary_cc_primary_control')
                # connect primary control os grp to primary scale RMV node
                mc.connectAttr(name + side + '_' + finger + '_finger_primary_rotate_RMV_01.outValue', name + side + '_' + finger + '_finger_DIS_JNT_primary_control_os_grp_01.rotateZ', force=True)
                mc.connectAttr(name + side + '_' + finger + '_finger_primary_rotate_RMV_01.outValue', name + side + '_' + finger + '_finger_DIS_secondary_cc_primary_control_os_grp_01.rotateZ', force=True)
                # direct connect translates, scales and rotates of secondary cc to joint
                mc.connectAttr(name + side + '_' + finger + '_finger_DIS_secondary_cc_01.translate', name + side + '_' + finger + '_finger_DIS_BN_01.translate')
                mc.connectAttr(name + side + '_' + finger + '_finger_DIS_secondary_cc_01.rotate', name + side + '_' + finger + '_finger_DIS_BN_01.rotate')
                mc.connectAttr(name + side + '_' + finger + '_finger_DIS_secondary_cc_01.scale', name + side + '_' + finger + '_finger_DIS_BN_01.scale')
                # select joint for next iteration
                mc.select(name + side + '_' + finger + '_finger_DIS_BN_01')

            # test if has at least four segments
            if(mc.objExists(name + side + '_' + finger + '_finger_DIS_2_target_cc_01')):
                mc.joint(name=name + side + '_' + finger + '_finger_DIS_2_BN_01', radius=.05)
                mc.delete(mc.parentConstraint(name + side + '_' + finger + '_finger_DIS_2_target_cc_01', name + side + '_' + finger + '_finger_DIS_2_BN_01', maintainOffset=False))
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_2_BN_01')
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_2_BN_01', prefix = name + side + '_' + finger + '_finger_DIS_2_JNT_cupping_control')
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_2_BN_01', prefix = name + side + '_' + finger + '_finger_DIS_2_JNT_primary_control_transforms')
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_2_BN_01', prefix = name + side + '_' + finger + '_finger_DIS_2_JNT_primary_control')
                # make secondary control
                current_finger_DIS_2_secondary_control = control.Control(
                                                                      prefix = name + side + '_' + finger + '_finger_DIS_2_secondary',
                                                                      scale = 0.05,
                                                                      use_numerical_transforms = False,
                                                                      transform_x = 0.0,
                                                                      transform_y = 0.0,
                                                                      transform_z = 0.0,
                                                                      translate_to = name + side + '_' + finger + '_finger_DIS_2_BN_01',
                                                                      rotate_to = name + side + '_' + finger + '_finger_DIS_2_BN_01',
                                                                      parent = current_finger_DIS_secondary_control.C,
                                                                      shape = 'pin',
                                                                      locked_channels = []
                                                                      )
                #visibility
                mc.connectAttr(current_finger_primary_control.C + '.bendy_control_visibility_parameter', current_finger_DIS_2_secondary_control.C + '.visibility', force=True)

                # make offset groups for control
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_2_secondary_cc_01', prefix = name + side + '_' + finger + '_finger_DIS_2_secondary_cc_cupping_control')
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_2_secondary_cc_01', prefix = name + side + '_' + finger + '_finger_DIS_2_secondary_cc_primary_control_transforms')
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_2_secondary_cc_01', prefix = name + side + '_' + finger + '_finger_DIS_2_secondary_cc_primary_control')
                # connect primary control os grp to primary scale RMV node
                mc.connectAttr(name + side + '_' + finger + '_finger_primary_rotate_RMV_01.outValue', name + side + '_' + finger + '_finger_DIS_2_JNT_primary_control_os_grp_01.rotateZ', force=True)
                mc.connectAttr(name + side + '_' + finger + '_finger_primary_rotate_RMV_01.outValue', name + side + '_' + finger + '_finger_DIS_2_secondary_cc_primary_control_os_grp_01.rotateZ', force=True)
                # direct connect translates, scales and rotates of secondary cc to joint
                mc.connectAttr(name + side + '_' + finger + '_finger_DIS_2_secondary_cc_01.translate', name + side + '_' + finger + '_finger_DIS_2_BN_01.translate')
                mc.connectAttr(name + side + '_' + finger + '_finger_DIS_2_secondary_cc_01.rotate', name + side + '_' + finger + '_finger_DIS_2_BN_01.rotate')
                mc.connectAttr(name + side + '_' + finger + '_finger_DIS_2_secondary_cc_01.scale', name + side + '_' + finger + '_finger_DIS_2_BN_01.scale')
                # select joint for next iteration
                mc.select(name + side + '_' + finger + '_finger_DIS_2_BN_01')

            # test if has at least five segments
            if(mc.objExists(name + side + '_' + finger + '_finger_DIS_3_target_cc_01')):
                mc.joint(name=name + side + '_' + finger + '_finger_DIS_3_BN_01', radius=.05)
                mc.delete(mc.parentConstraint(name + side + '_' + finger + '_finger_DIS_3_target_cc_01', name + side + '_' + finger + '_finger_DIS_3_BN_01', maintainOffset=False))
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_3_BN_01')
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_3_BN_01', prefix = name + side + '_' + finger + '_finger_DIS_3_JNT_cupping_control')
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_3_BN_01', prefix = name + side + '_' + finger + '_finger_DIS_3_JNT_primary_control_transforms')
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_3_BN_01', prefix = name + side + '_' + finger + '_finger_DIS_3_JNT_primary_control')
                # make secondary control
                current_finger_DIS_3_secondary_control = control.Control(
                                                                      prefix = name + side + '_' + finger + '_finger_DIS_3_secondary',
                                                                      scale = 0.05,
                                                                      use_numerical_transforms = False,
                                                                      transform_x = 0.0,
                                                                      transform_y = 0.0,
                                                                      transform_z = 0.0,
                                                                      translate_to = name + side + '_' + finger + '_finger_DIS_3_BN_01',
                                                                      rotate_to = name + side + '_' + finger + '_finger_DIS_3_BN_01',
                                                                      parent = current_finger_DIS_2_secondary_control.C,
                                                                      shape = 'pin',
                                                                      locked_channels = []
                                                                      )
                #visibility
                mc.connectAttr(current_finger_primary_control.C + '.bendy_control_visibility_parameter', current_finger_DIS_3_secondary_control.C + '.visibility', force=True)

                # make offset groups for control
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_3_secondary_cc_01', prefix = name + side + '_' + finger + '_finger_DIS_3_secondary_cc_cupping_control')
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_3_secondary_cc_01', prefix = name + side + '_' + finger + '_finger_DIS_3_secondary_cc_primary_control_transforms')
                transform.make_offset_group(name + side + '_' + finger + '_finger_DIS_3_secondary_cc_01', prefix = name + side + '_' + finger + '_finger_DIS_3_secondary_cc_primary_control')
                # connect primary control os grp to primary scale RMV node
                mc.connectAttr(name + side + '_' + finger + '_finger_primary_rotate_RMV_01.outValue', name + side + '_' + finger + '_finger_DIS_3_JNT_primary_control_os_grp_01.rotateZ', force=True)
                mc.connectAttr(name + side + '_' + finger + '_finger_primary_rotate_RMV_01.outValue', name + side + '_' + finger + '_finger_DIS_3_secondary_cc_primary_control_os_grp_01.rotateZ', force=True)
                # direct connect translates, scales and rotates of secondary cc to joint
                mc.connectAttr(name + side + '_' + finger + '_finger_DIS_3_secondary_cc_01.translate', name + side + '_' + finger + '_finger_DIS_3_BN_01.translate')
                mc.connectAttr(name + side + '_' + finger + '_finger_DIS_3_secondary_cc_01.rotate', name + side + '_' + finger + '_finger_DIS_3_BN_01.rotate')
                mc.connectAttr(name + side + '_' + finger + '_finger_DIS_3_secondary_cc_01.scale', name + side + '_' + finger + '_finger_DIS_3_BN_01.scale')
                # select joint for next iteration
                mc.select(name + side + '_' + finger + '_finger_DIS_3_BN_01')

            mc.joint(name=name + side + '_' + finger + '_finger_JNT_END_01', radius=.05)
            mc.delete(mc.parentConstraint(name + side + '_' + finger + '_finger_END_target_cc_01', name + side + '_' + finger + '_finger_JNT_END_01', maintainOffset=False))
            mc.setAttr( name + side + '_' + finger + '_finger_JNT_END_01.jointOrientX', 0)







    """
    make shoulder PSR
    """

    shoulder_PSR = pose_space_reader.PoseSpaceReader(
                                                       prefix = name + side,
                                                       scale = 1.0,
                                                       base_object = name + side + "_upper_arm_JNT_01",
                                                       tracker_object = name + side + "_lower_arm_JNT_01",
                                                       base_name = 'shoulder',
                                                       tracker_name = 'elbow',
                                                       target_names = ['up', 'down', 'forward', 'back'],
                                                       parent = '',
                                                    )

    """
    make clavicle/scapula
    """

    # create left shoulder joint and mirror for right shoulder joint
    if side=="_LFT":
        # create scapula JNT
        mc.select(clear=True)
        mc.joint(name=name + side + "_scapula_BN_01", position = mc.xform(scapula_joint, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=0.01)

        # create shoulder JNT
        mc.joint(name=name + side + "_shoulder_JNT_01", position = mc.xform(shoulder_joint, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=0.01)

        # set orientations on upper arm joint
        mc.joint( name + side + '_scapula_BN_01', edit=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient = 'yup' )
    else:
        mc.mirrorJoint(name + '_LFT_scapula_BN_01', mirrorBehavior=True, mirrorYZ=True, searchReplace=("LFT","RGT"))

    #parenting
    shoulder_joints_offset_group = mc.group(name=name + side + '_scapula_BN_os_grp_01', empty=True)
    mc.delete(mc.parentConstraint(name + side + "_scapula_BN_01", name + side + '_scapula_BN_os_grp_01', maintainOffset=False))
    shoulder_joints_control_group = mc.group(name=name + side + '_scapula_BN_control_grp_01', empty=True)
    mc.delete(mc.parentConstraint(name + side + "_scapula_BN_01", name + side + '_scapula_BN_control_grp_01', maintainOffset=False))
    mc.parent(name + side + "_scapula_BN_01", name + side + "_scapula_BN_control_grp_01")
    mc.parent(name + side + "_scapula_BN_control_grp_01", name + side + "_scapula_BN_os_grp_01")
    mc.parent(name + side + "_scapula_BN_os_grp_01", name + '_secondary_global_cc_01')

    #set shoulder orientation
    mc.setAttr( name + side + "_shoulder_JNT_01.jointOrientX", 0.0)
    mc.setAttr( name + side + "_shoulder_JNT_01.jointOrientY", 0.0)
    mc.setAttr( name + side + "_shoulder_JNT_01.jointOrientZ", 0.0)



    ############## WHAT THE HECK IS GOING ON WITH THE PARENT COMMAND HERE???????????? KEEPS COMBINING MIRRORED JOINTS/CREATING MULTIPLE CHAINS - HENCE NO TRANSFORM.MAKE_OFFSET_GROUP AND THE SNIPPET BELOW.
    if(mc.listRelatives(shoulder_joints_offset_group, parent=True)[0] != name + '_secondary_global_cc_01'):
        mc.parent(shoulder_joints_offset_group, name + '_secondary_global_cc_01')
    if side=="_RGT":
        reversed_x_position = mc.getAttr(shoulder_joints_offset_group + '.translateX')
        fixed_x_position = reversed_x_position*-1.0
        mc.setAttr(shoulder_joints_offset_group + '.translateX', fixed_x_position)
        mc.delete('*_LFT_upper_arm_os_grp_02')

    # create FK control curves
    clavicle_control = control.Control(
                                  prefix = name + side + '_clavicle',
                                  scale = .40,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_scapula_BN_01',
                                  rotate_to = name + side + '_scapula_BN_01',
                                  parent = name + '_secondary_global_cc_01',
                                  shape = 'circle',
                                  locked_channels = ['scale', 'visibility']
                                  )

    # lock and hide translate, scale, and visibility
    for part in ['clavicle']:
        mc.setAttr( name + side + "_" + part + "_cc_01.scaleX", lock=True, keyable=False, channelBox=False)
        mc.setAttr( name + side + "_" + part + "_cc_01.scaleY", lock=True, keyable=False, channelBox=False)
        mc.setAttr( name + side + "_" + part + "_cc_01.scaleZ", lock=True, keyable=False, channelBox=False)
        mc.setAttr( name + side + "_" + part + "_cc_01.visibility", lock=True, keyable=False, channelBox=False)


    # Connect joints to controls
    mc.connectAttr( clavicle_control.C + '.rotate', name + side + '_scapula_BN_control_grp_01.rotate', force=True)
    mc.connectAttr( clavicle_control.C + '.translate', name + side + '_scapula_BN_control_grp_01.translate', force=True)





    """
    bendy arm setup
    """


    #
    # read in variables
    number_of_upper_arm_joints = mc.intField( "number_of_upper_arm_spans", query = True, value=True )
    number_of_lower_arm_joints = mc.intField( "number_of_lower_arm_spans", query = True, value=True )

    upp_arm_length=mc.getAttr(name + side + '_lower_arm_JNT_01.translateX')
    low_arm_length=mc.getAttr(name + side + '_wrist_JNT_01.translateX')


    print(upp_arm_length)
    #
    # create bendy_JNT control joints
    bendy_control_joints_offset_group=mc.group(empty=True, name=name + side + '_arm_bendy_control_JNT_GRP_01')

    mc.duplicate(name + side + '_upper_arm_JNT_01', parentOnly=True, name=name + side + '_shoulder_bendy_JNT_01')
    transform.make_offset_group(name + side + '_shoulder_bendy_JNT_01', prefix=name + side + '_shoulder_bendy_JNT')
    mc.parent(name + side + '_shoulder_bendy_JNT_os_grp_01', name + side + '_arm_bendy_control_JNT_GRP_01')

    mc.duplicate(name + side + '_upper_arm_JNT_01', parentOnly=True, name=name + side + '_upper_arm_bendy_JNT_01')
    mc.move(upp_arm_length/2.0,0,0, name + side + '_upper_arm_bendy_JNT_01', objectSpace=True, relative=True)
    transform.make_offset_group(name + side + '_upper_arm_bendy_JNT_01', prefix=name + side + '_upper_arm_bendy_JNT')
    mc.parent(name + side + '_upper_arm_bendy_JNT_os_grp_01', name + side + '_arm_bendy_control_JNT_GRP_01')

    mc.duplicate(name + side + '_lower_arm_JNT_01', parentOnly=True, name=name + side + '_elbow_bendy_JNT_01')
    transform.make_offset_group(name + side + '_elbow_bendy_JNT_01', prefix=name + side + '_elbow_bendy_JNT')
    mc.parent(name + side + '_elbow_bendy_JNT_os_grp_01', name + side + '_arm_bendy_control_JNT_GRP_01')

    mc.duplicate(name + side + '_lower_arm_JNT_01', parentOnly=True, name=name + side + '_lower_arm_bendy_JNT_01')
    mc.move(low_arm_length/2.0,0,0, name + side + '_lower_arm_bendy_JNT_01', objectSpace=True, relative=True)
    transform.make_offset_group(name + side + '_lower_arm_bendy_JNT_01', prefix=name + side + '_lower_arm_bendy_JNT')
    mc.parent(name + side + '_lower_arm_bendy_JNT_os_grp_01', name + side + '_arm_bendy_control_JNT_GRP_01')

    mc.duplicate(name + side + '_wrist_JNT_01', parentOnly=True, name=name + side + '_wrist_bendy_JNT_01')
    transform.make_offset_group(name + side + '_wrist_bendy_JNT_01', prefix=name + side + '_wrist_bendy_JNT')
    mc.parent(name + side + '_wrist_bendy_JNT_os_grp_01', name + side + '_arm_bendy_control_JNT_GRP_01')


    #create tangent bendy_JNT control joints
    mc.duplicate(name + side + '_shoulder_bendy_JNT_01', parentOnly=True, name=name + side + '_shoulder_bendy_low_tangent_JNT_01')
    transform.make_offset_group(name + side + '_shoulder_bendy_low_tangent_JNT_01', prefix=name + side + '_shoulder_bendy_low_tangent_JNT')
    mc.parent(name + side + '_shoulder_bendy_low_tangent_JNT_os_grp_01', name + side + '_shoulder_bendy_JNT_01')

    mc.duplicate(name + side + '_upper_arm_bendy_JNT_01', parentOnly=True, name=name + side + '_upper_arm_bendy_upp_tangent_JNT_01')
    transform.make_offset_group(name + side + '_upper_arm_bendy_upp_tangent_JNT_01', prefix=name + side + '_upper_arm_bendy_upp_tangent_JNT')
    mc.parent(name + side + '_upper_arm_bendy_upp_tangent_JNT_os_grp_01', name + side + '_upper_arm_bendy_JNT_01')
    mc.duplicate(name + side + '_upper_arm_bendy_JNT_01', parentOnly=True, name=name + side + '_upper_arm_bendy_low_tangent_JNT_01')
    transform.make_offset_group(name + side + '_upper_arm_bendy_low_tangent_JNT_01', prefix=name + side + '_upper_arm_bendy_low_tangent_JNT')
    mc.parent(name + side + '_upper_arm_bendy_low_tangent_JNT_os_grp_01', name + side + '_upper_arm_bendy_JNT_01')

    mc.duplicate(name + side + '_elbow_bendy_JNT_01', parentOnly=True, name=name + side + '_elbow_bendy_upp_tangent_JNT_01')
    transform.make_offset_group(name + side + '_elbow_bendy_upp_tangent_JNT_01', prefix=name + side + '_elbow_bendy_upp_tangent_JNT')
    mc.parent(name + side + '_elbow_bendy_upp_tangent_JNT_os_grp_01', name + side + '_elbow_bendy_JNT_01')
    mc.duplicate(name + side + '_elbow_bendy_JNT_01', parentOnly=True, name=name + side + '_elbow_bendy_low_tangent_JNT_01')
    transform.make_offset_group(name + side + '_elbow_bendy_low_tangent_JNT_01', prefix=name + side + '_elbow_bendy_low_tangent_JNT')
    mc.parent(name + side + '_elbow_bendy_low_tangent_JNT_os_grp_01', name + side + '_elbow_bendy_JNT_01')

    mc.duplicate(name + side + '_lower_arm_bendy_JNT_01', parentOnly=True, name=name + side + '_lower_arm_bendy_upp_tangent_JNT_01')
    transform.make_offset_group(name + side + '_lower_arm_bendy_upp_tangent_JNT_01', prefix=name + side + '_lower_arm_bendy_upp_tangent_JNT')
    mc.parent(name + side + '_lower_arm_bendy_upp_tangent_JNT_os_grp_01', name + side + '_lower_arm_bendy_JNT_01')
    mc.duplicate(name + side + '_lower_arm_bendy_JNT_01', parentOnly=True, name=name + side + '_lower_arm_bendy_low_tangent_JNT_01')
    transform.make_offset_group(name + side + '_lower_arm_bendy_low_tangent_JNT_01', prefix=name + side + '_lower_arm_bendy_low_tangent_JNT')
    mc.parent(name + side + '_lower_arm_bendy_low_tangent_JNT_os_grp_01', name + side + '_lower_arm_bendy_JNT_01')

    mc.duplicate(name + side + '_wrist_bendy_JNT_01', parentOnly=True, name=name + side + '_wrist_bendy_upp_tangent_JNT_01')
    transform.make_offset_group(name + side + '_wrist_bendy_upp_tangent_JNT_01', prefix=name + side + '_wrist_bendy_upp_tangent_JNT')
    mc.parent(name + side + '_wrist_bendy_upp_tangent_JNT_os_grp_01', name + side + '_wrist_bendy_JNT_01')





    #
    # create Bendy control curves

    #Primaries
    bendy_shoulder_control = control.Control(
                                  prefix = name + side + '_shoulder_bendy',
                                  scale = .60,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_shoulder_bendy_JNT_01',
                                  rotate_to = name + side + '_shoulder_bendy_JNT_01',
                                  parent = name + '_secondary_global_cc_01',
                                  shape = 'circle',
                                  locked_channels = ['scale']
                                  )

    bendy_upper_arm_control = control.Control(
                                  prefix = name + side + '_upper_arm_bendy',
                                  scale = .60,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_upper_arm_bendy_JNT_01',
                                  rotate_to = name + side + '_upper_arm_bendy_JNT_01',
                                  parent = name + '_secondary_global_cc_01',
                                  shape = 'circle',
                                  locked_channels = ['scale']
                                  )

    bendy_elbow_control = control.Control(
                                  prefix = name + side + '_elbow_bendy',
                                  scale = .60,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_elbow_bendy_JNT_01',
                                  rotate_to = name + side + '_elbow_bendy_JNT_01',
                                  parent = name + '_secondary_global_cc_01',
                                  shape = 'circle',
                                  locked_channels = ['scale']
                                  )

    bendy_lower_arm_control = control.Control(
                                  prefix = name + side + '_lower_arm_bendy',
                                  scale = .60,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_lower_arm_bendy_JNT_01',
                                  rotate_to = name + side + '_lower_arm_bendy_JNT_01',
                                  parent = name + '_secondary_global_cc_01',
                                  shape = 'circle',
                                  locked_channels = ['scale']
                                  )

    bendy_wrist_control = control.Control(
                                  prefix = name + side + '_wrist_bendy',
                                  scale = .60,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_wrist_bendy_JNT_01',
                                  rotate_to = name + side + '_wrist_bendy_JNT_01',
                                  parent = name + '_secondary_global_cc_01',
                                  shape = 'circle',
                                  locked_channels = ['scale']
                                  )



    #Tangents
    shoulder_bendy_low_tangent_control = control.Control(
                                  prefix = name + side + '_shoulder_bendy_low_tangent',
                                  scale = .50,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_shoulder_bendy_low_tangent_JNT_01',
                                  rotate_to = name + side + '_shoulder_bendy_low_tangent_JNT_01',
                                  parent = name + side + '_shoulder_bendy_cc_01',
                                  shape = 'diamond',
                                  locked_channels = ['scale']
                                  )

    upper_arm_bendy_upp_tangent_control = control.Control(
                                  prefix = name + side + '_upper_arm_bendy_upp_tangent',
                                  scale = .50,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_upper_arm_bendy_upp_tangent_JNT_01',
                                  rotate_to = name + side + '_upper_arm_bendy_upp_tangent_JNT_01',
                                  parent = name + side + '_upper_arm_bendy_cc_01',
                                  shape = 'diamond',
                                  locked_channels = ['scale']
                                  )

    upper_arm_bendy_low_tangent_control = control.Control(
                                  prefix = name + side + '_upper_arm_bendy_low_tangent',
                                  scale = .50,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_upper_arm_bendy_low_tangent_JNT_01',
                                  rotate_to = name + side + '_upper_arm_bendy_low_tangent_JNT_01',
                                  parent = name + side + '_upper_arm_bendy_cc_01',
                                  shape = 'diamond',
                                  locked_channels = ['scale']
                                  )

    elbow_bendy_upp_tangent_control = control.Control(
                                  prefix = name + side + '_elbow_bendy_upp_tangent',
                                  scale = .50,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_elbow_bendy_upp_tangent_JNT_01',
                                  rotate_to = name + side + '_elbow_bendy_upp_tangent_JNT_01',
                                  parent = name + side + '_elbow_bendy_cc_01',
                                  shape = 'diamond',
                                  locked_channels = ['scale']
                                  )

    elbow_bendy_low_tangent_control = control.Control(
                                  prefix = name + side + '_elbow_bendy_low_tangent',
                                  scale = .50,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_elbow_bendy_low_tangent_JNT_01',
                                  rotate_to = name + side + '_elbow_bendy_low_tangent_JNT_01',
                                  parent = name + side + '_elbow_bendy_cc_01',
                                  shape = 'diamond',
                                  locked_channels = ['scale']
                                  )

    lower_arm_bendy_upp_tangent_control = control.Control(
                                  prefix = name + side + '_lower_arm_bendy_upp_tangent',
                                  scale = .50,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_lower_arm_bendy_upp_tangent_JNT_01',
                                  rotate_to = name + side + '_lower_arm_bendy_upp_tangent_JNT_01',
                                  parent = name + side + '_lower_arm_bendy_cc_01',
                                  shape = 'diamond',
                                  locked_channels = ['scale']
                                  )

    lower_arm_bendy_low_tangent_control = control.Control(
                                  prefix = name + side + '_lower_arm_bendy_low_tangent',
                                  scale = .50,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_lower_arm_bendy_low_tangent_JNT_01',
                                  rotate_to = name + side + '_lower_arm_bendy_low_tangent_JNT_01',
                                  parent = name + side + '_lower_arm_bendy_cc_01',
                                  shape = 'diamond',
                                  locked_channels = ['scale']
                                  )

    wrist_bendy_upp_tangent_control = control.Control(
                                  prefix = name + side + '_wrist_bendy_upp_tangent',
                                  scale = .50,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + side + '_wrist_bendy_upp_tangent_JNT_01',
                                  rotate_to = name + side + '_wrist_bendy_upp_tangent_JNT_01',
                                  parent = name + side + '_wrist_bendy_cc_01',
                                  shape = 'diamond',
                                  locked_channels = ['scale']
                                  )


    #Group bendy_curve control_joints
    bendy_curve_control_joint_os_grps = [name + side + '_shoulder_bendy_cc_os_grp_01',
                              name + side + '_upper_arm_bendy_cc_os_grp_01',
                              name + side + '_elbow_bendy_cc_os_grp_01',
                              name + side + '_lower_arm_bendy_cc_os_grp_01',
                              name + side + '_wrist_bendy_cc_os_grp_01']
    mc.group(name=name + side + '_arm_bendy_controls_GRP_01', empty=True)
    mc.parent(bendy_curve_control_joint_os_grps, name + side + '_arm_bendy_controls_GRP_01')





    #
    # connect tangent offset distances to custom noodle attr on primary bendy controls

    # determine good default value for noodle attr
    noodle_default=abs(upp_arm_length+low_arm_length)/30

    # create custom noodle attribute and its utility inverse
    for part in ['_shoulder_bendy_cc', '_upper_arm_bendy_cc', '_elbow_bendy_cc', '_lower_arm_bendy_cc', '_wrist_bendy_cc']:
        mc.addAttr(name + side + part + '_01', shortName='noodle_parameter', longName='Noodle', attributeType='float', defaultValue=noodle_default, minValue=0.0, maxValue=1.0, keyable=True)
        mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + part + '_noodle_parameter_inverse_01')
        mc.connectAttr( name + side + part + '_01.noodle_parameter', name + side + part + '_noodle_parameter_inverse_01.input1X', force=True)
        mc.setAttr( name + side + part + '_noodle_parameter_inverse_01.input2X', -1.0)

    #connections
    if side == '_LFT':

        mc.connectAttr(name + side + '_shoulder_bendy_cc_01.noodle_parameter', name + side + '_shoulder_bendy_low_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_upper_arm_bendy_cc_01.noodle_parameter', name + side + '_upper_arm_bendy_low_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_elbow_bendy_cc_01.noodle_parameter', name + side + '_elbow_bendy_low_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_lower_arm_bendy_cc_01.noodle_parameter', name + side + '_lower_arm_bendy_low_tangent_JNT_os_grp_01.translateX', force=True)

        mc.connectAttr(name + side + '_shoulder_bendy_cc_01.noodle_parameter', name + side + '_shoulder_bendy_low_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_upper_arm_bendy_cc_01.noodle_parameter', name + side + '_upper_arm_bendy_low_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_elbow_bendy_cc_01.noodle_parameter', name + side + '_elbow_bendy_low_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_lower_arm_bendy_cc_01.noodle_parameter', name + side + '_lower_arm_bendy_low_tangent_cc_os_grp_01.translateX', force=True)

        mc.connectAttr(name + side + '_upper_arm_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_upper_arm_bendy_upp_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_elbow_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_elbow_bendy_upp_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_lower_arm_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_lower_arm_bendy_upp_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_wrist_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_wrist_bendy_upp_tangent_JNT_os_grp_01.translateX', force=True)

        mc.connectAttr(name + side + '_upper_arm_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_upper_arm_bendy_upp_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_elbow_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_elbow_bendy_upp_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_lower_arm_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_lower_arm_bendy_upp_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_wrist_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_wrist_bendy_upp_tangent_cc_os_grp_01.translateX', force=True)

    else:

        mc.connectAttr(name + side + '_shoulder_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_shoulder_bendy_low_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_upper_arm_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_upper_arm_bendy_low_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_elbow_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_elbow_bendy_low_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_lower_arm_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_lower_arm_bendy_low_tangent_JNT_os_grp_01.translateX', force=True)

        mc.connectAttr(name + side + '_shoulder_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_shoulder_bendy_low_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_upper_arm_bendy_cc_01.noodle_parameter', name + side + '_upper_arm_bendy_low_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_elbow_bendy_cc_01.noodle_parameter', name + side + '_elbow_bendy_low_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_lower_arm_bendy_cc_01.noodle_parameter', name + side + '_lower_arm_bendy_low_tangent_cc_os_grp_01.translateX', force=True)

        mc.connectAttr(name + side + '_upper_arm_bendy_cc_01.noodle_parameter', name + side + '_upper_arm_bendy_upp_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_elbow_bendy_cc_01.noodle_parameter', name + side + '_elbow_bendy_upp_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_lower_arm_bendy_cc_01.noodle_parameter', name + side + '_lower_arm_bendy_upp_tangent_JNT_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_wrist_bendy_cc_01.noodle_parameter', name + side + '_wrist_bendy_upp_tangent_JNT_os_grp_01.translateX', force=True)

        mc.connectAttr(name + side + '_upper_arm_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_upper_arm_bendy_upp_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_elbow_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_elbow_bendy_upp_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_lower_arm_bendy_cc_noodle_parameter_inverse_01.outputX', name + side + '_lower_arm_bendy_upp_tangent_cc_os_grp_01.translateX', force=True)
        mc.connectAttr(name + side + '_wrist_bendy_cc_01.noodle_parameter', name + side + '_wrist_bendy_upp_tangent_cc_os_grp_01.translateX', force=True)


    #
    # connect bendy control curve

    # List of joints that will be used to create CVs for ikSpline curve and then be bound to said CVs
    curve_cv_control_joints = [name + side + '_shoulder_bendy_JNT_01',
                              name + side + '_shoulder_bendy_low_tangent_JNT_01',
                              name + side + '_upper_arm_bendy_upp_tangent_JNT_01',
                              name + side + '_upper_arm_bendy_JNT_01',
                              name + side + '_upper_arm_bendy_low_tangent_JNT_01',
                              name + side + '_elbow_bendy_upp_tangent_JNT_01',
                              name + side + '_elbow_bendy_JNT_01',
                              name + side + '_elbow_bendy_low_tangent_JNT_01',
                              name + side + '_lower_arm_bendy_upp_tangent_JNT_01',
                              name + side + '_lower_arm_bendy_JNT_01',
                              name + side + '_lower_arm_bendy_low_tangent_JNT_01',
                              name + side + '_wrist_bendy_upp_tangent_JNT_01',
                              name + side + '_wrist_bendy_JNT_01']

    # List of joints that will be used to create CVs for pointer ikSpline curve and then be bound to said CVs
    curve_cv_primary_control_joints = [name + side + '_shoulder_bendy_JNT_01',
                                      name + side + '_upper_arm_bendy_JNT_01',
                                      name + side + '_elbow_bendy_JNT_01',
                                      name + side + '_lower_arm_bendy_JNT_01',
                                      name + side + '_wrist_bendy_JNT_01']

    # List of controls that will drive the curve_cv_control_joints
    curve_cv_control_ccs = [name + side + '_shoulder_bendy_cc_01',
                          name + side + '_shoulder_bendy_low_tangent_cc_01',
                          name + side + '_upper_arm_bendy_upp_tangent_cc_01',
                          name + side + '_upper_arm_bendy_cc_01',
                          name + side + '_upper_arm_bendy_low_tangent_cc_01',
                          name + side + '_elbow_bendy_upp_tangent_cc_01',
                          name + side + '_elbow_bendy_cc_01',
                          name + side + '_elbow_bendy_low_tangent_cc_01',
                          name + side + '_lower_arm_bendy_upp_tangent_cc_01',
                          name + side + '_lower_arm_bendy_cc_01',
                          name + side + '_lower_arm_bendy_low_tangent_cc_01',
                          name + side + '_wrist_bendy_upp_tangent_cc_01',
                          name + side + '_wrist_bendy_cc_01']

    # List of controls that will be used to create CVs for pointer ikSpline curve and then be bound to said CVs
    curve_cv_primary_control_controls = [name + side + '_shoulder_bendy_cc_01',
                                      name + side + '_upper_arm_bendy_cc_01',
                                      name + side + '_elbow_bendy_cc_01',
                                      name + side + '_lower_arm_bendy_cc_01',
                                      name + side + '_wrist_bendy_cc_01']


    #Add os_grp for rotations to all primary bendy controls and joints
    transform.make_offset_group(name + side + '_shoulder_bendy_JNT_01', prefix=name + side + "_shoulder_bendy_JNT_rotation")
    transform.make_offset_group(name + side + '_upper_arm_bendy_JNT_01', prefix=name + side + "_upper_arm_bendy_JNT_rotation")
    transform.make_offset_group(name + side + '_elbow_bendy_JNT_01', prefix=name + side + "_elbow_bendy_JNT_rotation")
    transform.make_offset_group(name + side + '_lower_arm_bendy_JNT_01', prefix=name + side + "_lower_arm_bendy_JNT_rotation")
    transform.make_offset_group(name + side + '_wrist_bendy_JNT_01', prefix=name + side + "_wrist_bendy_JNT_rotation")

    transform.make_offset_group(name + side + '_shoulder_bendy_cc_01', prefix=name + side + "_shoulder_bendy_cc_rotation")
    transform.make_offset_group(name + side + '_upper_arm_bendy_cc_01', prefix=name + side + "_upper_arm_bendy_cc_rotation")
    transform.make_offset_group(name + side + '_elbow_bendy_cc_01', prefix=name + side + "_elbow_bendy_cc_rotation")
    transform.make_offset_group(name + side + '_lower_arm_bendy_cc_01', prefix=name + side + "_lower_arm_bendy_cc_rotation")
    transform.make_offset_group(name + side + '_wrist_bendy_cc_01', prefix=name + side + "_wrist_bendy_cc_rotation")




    #
    # Connect cc's to joints
    for cc, jnt in zip(curve_cv_control_ccs, curve_cv_control_joints):
        for attr in ['.tx','.ty','.tz','.rx','.ry','.rz','.sx','.sy','.sz']:
            mc.connectAttr(cc + attr, jnt + attr, force=True)



    #
    # create bendy joints (these will serve as a base for the bones that actually bind to the mesh)

    bendy_joints_offset_group=mc.group(empty=True, name=name + side + '_arm_bendy_JNT_GRP_01')

    mc.select(name + side + '_arm_bendy_JNT_GRP_01')
    for num in range(1, number_of_upper_arm_joints+number_of_lower_arm_joints+1):
        # create upper_arm bendy JNTs
        if num <= number_of_upper_arm_joints:
            mc.joint(name=name + side + '_arm_bendy_'+str(num)+'_JNT_01', position = mc.xform(name + side + '_upper_arm_stretchy_target_'+str(num)+'_cc_01', query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=0.05)
        else:
            mc.joint(name=name + side + '_arm_bendy_'+str(num)+'_JNT_01', position = mc.xform(name + side + '_lower_arm_stretchy_target_'+str(num-number_of_upper_arm_joints)+'_cc_01', query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=0.05)
    #reorient chain
    mc.joint(name + side + '_arm_bendy_1_JNT_01', edit=True, zeroScaleOrient=True, orientJoint='xzy', secondaryAxisOrient = 'yup', children=True )
    #align last joint
    for attr in ['jointOrientX','jointOrientY','jointOrientZ']:
        mc.setAttr(name + side + '_arm_bendy_'+str(number_of_upper_arm_joints+number_of_lower_arm_joints)+'_JNT_01.'+attr, 0)


    #
    # create bendy pointer joints (these will control the x rotations of the bendy bones)

    bendy_pointer_joints_offset_group=mc.group(empty=True, name=name + side + '_arm_bendy_pointer_JNT_GRP_01')

    mc.select(name + side + '_arm_bendy_pointer_JNT_GRP_01')
    for num in range(1, number_of_upper_arm_joints+number_of_lower_arm_joints+1):
        # create upper_arm bendy JNTs
        if num <= number_of_upper_arm_joints:
            mc.joint(name=name + side + '_arm_bendy_pointer_'+str(num)+'_JNT_01', position = mc.xform(name + side + '_upper_arm_stretchy_target_'+str(num)+'_cc_01', query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=0.05)
        else:
            mc.joint(name=name + side + '_arm_bendy_pointer_'+str(num)+'_JNT_01', position = mc.xform(name + side + '_lower_arm_stretchy_target_'+str(num-number_of_upper_arm_joints)+'_cc_01', query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=0.05)
    #reorient chain
    mc.joint(name + side + '_arm_bendy_pointer_1_JNT_01', edit=True, zeroScaleOrient=True, orientJoint='xzy', secondaryAxisOrient = 'yup', children=True )
    #align last joint
    for attr in ['jointOrientX','jointOrientY','jointOrientZ']:
        mc.setAttr(name + side + '_arm_bendy_pointer_'+str(number_of_upper_arm_joints+number_of_lower_arm_joints)+'_JNT_01.'+attr, 0)


    #
    # create bendy bones (these will be the bones that actually bind to the mesh)
    bendy_bones_offset_group=mc.group(empty=True, name=name + side + '_arm_bendy_BN_GRP_01')

    mc.select(name + side + '_arm_bendy_BN_GRP_01')
    for num in range(1, number_of_upper_arm_joints+number_of_lower_arm_joints+1):
        mc.select(name + side + '_arm_bendy_BN_GRP_01')
        # create upper_arm bendy BNs
        if num <= number_of_upper_arm_joints:
            mc.joint(name=name + side + '_arm_bendy_'+str(num)+'_BN_01', position = mc.xform(name + side + '_upper_arm_stretchy_target_'+str(num)+'_cc_01', query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=0.05)
        else:
            mc.joint(name=name + side + '_arm_bendy_'+str(num)+'_BN_01', position = mc.xform(name + side + '_lower_arm_stretchy_target_'+str(num-number_of_upper_arm_joints)+'_cc_01', query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=0.05)
    #reorient chain
    mc.joint(name + side + '_arm_bendy_1_BN_01', edit=True, zeroScaleOrient=True, orientJoint='xzy', secondaryAxisOrient = 'yup', children=True )
    #align last joint
    for attr in ['jointOrientX','jointOrientY','jointOrientZ']:
        mc.setAttr(name + side + '_arm_bendy_'+str(number_of_upper_arm_joints+number_of_lower_arm_joints)+'_BN_01.'+attr, 0)



    #
    # Create IK spline for bendy arm joints

    # will contain positions in space of all joints
    cv_world_positions=[]
    for joint in curve_cv_control_joints:
        cur_cv_position = mc.pointPosition( joint + '.rotatePivot' )
        cv_world_positions.append( cur_cv_position )

    #Create curve with CVs at proper positions to generate curve
    temp_name = mc.curve( d=3, p=cv_world_positions)
    mc.rename(temp_name, name + side + '_arm_splineIK_curve_01')

    #Bind bendy_JNT joints to curve and adjust weights
    mc.skinCluster(curve_cv_control_joints, name + side + '_arm_splineIK_curve_01', name=name + side + '_arm_splineIK_curve_scls_01')
    for joint in curve_cv_control_joints:
        mc.skinPercent(name + side + '_arm_splineIK_curve_scls_01', name + side + '_arm_splineIK_curve_01.cv['+str(curve_cv_control_joints.index(joint))+']', transformValue=[(joint, 1.0)])

    mc.ikHandle(name=name + side + '_arm_splineIK_handle_01', solver="ikSplineSolver", createCurve=False, startJoint=(name + side + '_arm_bendy_1_JNT_01'), endEffector=(name + side + '_arm_bendy_'+str(number_of_upper_arm_joints+number_of_lower_arm_joints)+'_JNT_01'), curve=name + side + '_arm_splineIK_curve_01')

    #make curveInfo node to track length of splineIK curve
    curveInfoNode = mc.arclen(name + side + '_arm_splineIK_curve_01', constructionHistory=True)
    curveInfoNode = mc.rename(curveInfoNode, name + side + '_arm_splineIK_curve_length_info_01')
    splineIK_start_curve_length = mc.getAttr(curveInfoNode + '.arcLength')

    #setup to get joints to scale with splineIK curve
    #find splineIK curve scale length
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_arm_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_arm_splineIK_curve_scale_length_MD_01')
    mc.setAttr( name + side + '_arm_splineIK_curve_scale_length_MD_01.operation', 2)

    mc.setAttr( name + side + '_arm_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01.input1X', splineIK_start_curve_length)
    mc.connectAttr( name + '_secret_total_scale_MD_01.outputX', name + side + '_arm_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01.input2X')

    mc.connectAttr( curveInfoNode + '.arcLength', name + side + '_arm_splineIK_curve_scale_length_MD_01.input1X' )
    mc.connectAttr( name + side + '_arm_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01.outputX', name + side + '_arm_splineIK_curve_scale_length_MD_01.input2X')

    #connect to joints' scale X
    for num in range(1, number_of_upper_arm_joints+number_of_lower_arm_joints+1):
        mc.connectAttr( name + side + '_arm_splineIK_curve_scale_length_MD_01.outputX', name + side + '_arm_bendy_'+str(num)+'_JNT_01.scaleX')




    #
    # Create IK spline for bendy leg bone pointers

    # will contain positions in space of all joints
    cv_world_positions=[]
    for joint in curve_cv_primary_control_joints:
        cur_cv_position = mc.pointPosition( joint + '.rotatePivot' )
        cv_world_positions.append( cur_cv_position )

    # create curve with CVs at proper positions to generate curve
    temp_name = mc.curve( d=3, p=cv_world_positions)
    mc.rename(temp_name, name + side + '_arm_splineIK_pointer_curve_01')

    # move pointer curve backward in Z (so crimps without overlapping)
    mc.move(0,0,abs(upp_arm_length+low_arm_length)/6, name + side + '_arm_splineIK_pointer_curve_01', worldSpace=True, relative=True )



    #For DANG BENT ARMS only:
    if name=='Grendel' or name=='Dragon':
        elbow_pos=mc.xform(elbow_joint, query=True, rotatePivot=True, worldSpace=True)
        mc.scale(0.8,0.8,0.8, name + side + '_arm_splineIK_pointer_curve_01', relative=True, pivot=(elbow_pos[0]-0.051, elbow_pos[1]+0.060, elbow_pos[2]-0.379) )


    #Bind bendy_JNT joints to curve and adjust weights
    mc.skinCluster(curve_cv_control_joints, name + side + '_arm_splineIK_pointer_curve_01', name=name + side + '_arm_splineIK_pointer_curve_scls_01')
    for joint in curve_cv_primary_control_joints:
        mc.skinPercent(name + side + '_arm_splineIK_pointer_curve_scls_01', name + side + '_arm_splineIK_pointer_curve_01.cv['+str(curve_cv_primary_control_joints.index(joint))+']', transformValue=[(joint, 1.0)])
    mc.ikHandle(name=name + side + '_arm_splineIK_pointer_handle_01', solver="ikSplineSolver", createCurve=False, startJoint=(name + side + '_arm_bendy_pointer_1_JNT_01'), endEffector=(name + side + '_arm_bendy_pointer_'+str(number_of_upper_arm_joints+number_of_lower_arm_joints)+'_JNT_01'), curve=name + side + '_arm_splineIK_pointer_curve_01')

    #make curveInfo node to track length of splineIK curve
    curveInfoNode = mc.arclen(name + side + '_arm_splineIK_pointer_curve_01', constructionHistory=True)
    curveInfoNode = mc.rename(curveInfoNode, name + side + '_arm_splineIK_pointer_curve_length_info_01')
    splineIK_start_pointer_curve_length = mc.getAttr(curveInfoNode + '.arcLength')

    #setup to get joints to scale with splineIK curve
    #find splineIK curve scale length
    mc.shadingNode('multiplyDivide', asUtility=True, name=name + side + '_arm_splineIK_pointer_curve_simplify_compensate_MD_01')
    mc.setAttr( name + side + '_arm_splineIK_pointer_curve_simplify_compensate_MD_01.operation', 2)

    mc.shadingNode('multiplyDivide', asUtility=True, name=name + side + '_arm_splineIK_compensated_pointer_curve_length_multiplied_by_rig_scale_MD_01')

    mc.shadingNode('multiplyDivide', asUtility=True, name=name + side + '_arm_splineIK_pointer_curve_scale_length_MD_01')
    mc.setAttr( name + side + '_arm_splineIK_pointer_curve_scale_length_MD_01.operation', 2)

    mc.shadingNode('multiplyDivide', asUtility=True, name=name + side + '_arm_splineIK_pointer_curve_joint_scale_MD_01')
    mc.setAttr( name + side + '_arm_splineIK_pointer_curve_joint_scale_MD_01.operation', 2)


    mc.setAttr(name + side + '_arm_splineIK_pointer_curve_simplify_compensate_MD_01.input2X', mc.getAttr(name + side + '_arm_splineIK_pointer_curve_length_info_01.arcLength'))
    mc.setAttr(name + side + '_arm_splineIK_pointer_curve_simplify_compensate_MD_01.input1X', mc.getAttr(name + side + '_arm_splineIK_curve_length_info_01.arcLength'))

    mc.connectAttr(name + side + '_arm_splineIK_pointer_curve_simplify_compensate_MD_01.outputX', name + side + '_arm_splineIK_compensated_pointer_curve_length_multiplied_by_rig_scale_MD_01.input1X', force=True)
    mc.connectAttr(name + '_secret_total_scale_MD_01.outputX', name + side + '_arm_splineIK_compensated_pointer_curve_length_multiplied_by_rig_scale_MD_01.input2X', force=True)

    mc.connectAttr(name + side + '_arm_splineIK_pointer_curve_length_info_01.arcLength', name + side + '_arm_splineIK_pointer_curve_scale_length_MD_01.input1X', force=True)
    mc.setAttr(name + side + '_arm_splineIK_pointer_curve_scale_length_MD_01.input2X', splineIK_start_pointer_curve_length)

    mc.connectAttr(name + side + '_arm_splineIK_pointer_curve_scale_length_MD_01.outputX', name + side + '_arm_splineIK_pointer_curve_joint_scale_MD_01.input1X', force=True)
    mc.connectAttr(name + side + '_arm_splineIK_compensated_pointer_curve_length_multiplied_by_rig_scale_MD_01.outputX', name + side + '_arm_splineIK_pointer_curve_joint_scale_MD_01.input2X', force=True)


    #connect to joints' scale X
    for num in range(1, number_of_upper_arm_joints+number_of_lower_arm_joints+1):
        mc.connectAttr( name + side + '_arm_splineIK_pointer_curve_joint_scale_MD_01.outputX', name + side + '_arm_bendy_pointer_'+str(num)+'_JNT_01.scaleX', force=True)




    #
    # Aim bendy bones to bendy joints
    # all but last
    for num in range(1, number_of_upper_arm_joints+number_of_lower_arm_joints):
        mc.pointConstraint(name + side + '_arm_bendy_'+str(num)+'_JNT_01', name + side + '_arm_bendy_'+str(num)+'_BN_01', maintainOffset=False)
        mc.aimConstraint(name + side + '_arm_bendy_'+str(num+1)+'_BN_01', name + side + '_arm_bendy_'+str(num)+'_BN_01', maintainOffset=True, worldUpType="object", worldUpObject=name + side + '_arm_bendy_pointer_' + str(num) + '_JNT_01', upVector=(0,-1,0) )
    #last
    mc.parentConstraint(name + side + '_wrist_JNT_01', name + side + '_arm_bendy_'+str(number_of_upper_arm_joints+number_of_lower_arm_joints)+'_BN_01', maintainOffset=True)




    #
    # connect bendy rig to normal rig

    # constrain bendy joint control offsets to normal joint chain

    transform.make_offset_group(name + side + '_shoulder_bendy_cc_os_grp_01', prefix=name + side + '_shoulder_bendy_cc_shoulder')
    mc.parentConstraint(name + side + '_scapula_BN_01', name + side + '_shoulder_bendy_cc_shoulder_os_grp_01', maintainOffset=True)
    #mc.pointConstraint(name + side + '_upper_arm_JNT_01', name + side + '_shoulder_bendy_cc_os_grp_01', maintainOffset=True)
    mc.orientConstraint(name + side + '_upper_arm_JNT_01', name + side + '_shoulder_bendy_cc_os_grp_01', maintainOffset=True, skip=['x'])

    mc.parentConstraint(name + side + '_upper_arm_JNT_01', name + side + '_upper_arm_bendy_cc_os_grp_01', maintainOffset=True)

    mc.parentConstraint(name + side + '_lower_arm_JNT_01', name + side + '_elbow_bendy_cc_os_grp_01', maintainOffset=True)

    mc.parentConstraint(name + side + '_lower_arm_JNT_01', name + side + '_lower_arm_bendy_cc_os_grp_01', maintainOffset=True)

    mc.parentConstraint(name + side + '_wrist_JNT_01', name + side + '_wrist_bendy_cc_os_grp_01', maintainOffset=True)


    # constrain bendy joint control offsets to normal joint chain

    transform.make_offset_group(name + side + '_shoulder_bendy_JNT_os_grp_01', prefix=name + side + '_shoulder_bendy_JNT_shoulder')
    mc.parentConstraint(name + side + '_scapula_BN_01', name + side + '_shoulder_bendy_JNT_shoulder_os_grp_01', maintainOffset=True)
    #mc.pointConstraint(name + side + '_upper_arm_JNT_01', name + side + '_shoulder_bendy_JNT_os_grp_01', maintainOffset=True)
    mc.orientConstraint(name + side + '_upper_arm_JNT_01', name + side + '_shoulder_bendy_JNT_os_grp_01', maintainOffset=True, skip=['x'])

    mc.parentConstraint(name + side + '_upper_arm_JNT_01', name + side + '_upper_arm_bendy_JNT_os_grp_01', maintainOffset=True)

    mc.parentConstraint(name + side + '_lower_arm_JNT_01', name + side + '_elbow_bendy_JNT_os_grp_01', maintainOffset=True)

    mc.parentConstraint(name + side + '_lower_arm_JNT_01', name + side + '_lower_arm_bendy_JNT_os_grp_01', maintainOffset=True)

    mc.parentConstraint(name + side + '_wrist_JNT_01', name + side + '_wrist_bendy_JNT_os_grp_01', maintainOffset=True)



    #
    # Twists

    # rotate bendy elbow halfway in z, so that it makes a nice bend instead of a kink
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_arm_bendy_elbow_follow_MD_01')
    mc.connectAttr(name + side + '_lower_arm_JNT_01.rotateZ', name + side + '_arm_bendy_elbow_follow_MD_01.input1X', force=True)
    mc.setAttr(name + side + '_arm_bendy_elbow_follow_MD_01.input2X', -0.5)
    mc.connectAttr(name + side + '_arm_bendy_elbow_follow_MD_01.outputX', name + side + '_elbow_bendy_cc_rotation_os_grp_01.rotateZ', force=True)
    mc.connectAttr(name + side + '_arm_bendy_elbow_follow_MD_01.outputX', name + side + '_elbow_bendy_JNT_rotation_os_grp_01.rotateZ', force=True)

    # rotate bendy upper_arm halfway in z, so that whole arm twists nicely
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_arm_bendy_upper_arm_follow_MD_01')
    mc.connectAttr(name + side + '_upper_arm_JNT_01.rotateX', name + side + '_arm_bendy_upper_arm_follow_MD_01.input1X', force=True)
    mc.setAttr(name + side + '_arm_bendy_upper_arm_follow_MD_01.input2X', -0.5)
    mc.connectAttr(name + side + '_arm_bendy_upper_arm_follow_MD_01.outputX', name + side + '_upper_arm_bendy_cc_rotation_os_grp_01.rotateX', force=True)
    mc.connectAttr(name + side + '_arm_bendy_upper_arm_follow_MD_01.outputX', name + side + '_upper_arm_bendy_JNT_rotation_os_grp_01.rotateX', force=True)

    # rotate bendy lower_arm halfway in z, so that whole arm twists nicely
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + side + '_arm_bendy_lower_arm_follow_MD_01')
    mc.connectAttr(name + side + '_wrist_JNT_01.rotateX', name + side + '_arm_bendy_lower_arm_follow_MD_01.input1X', force=True)
    mc.setAttr(name + side + '_arm_bendy_lower_arm_follow_MD_01.input2X', 0.5)
    mc.connectAttr(name + side + '_arm_bendy_lower_arm_follow_MD_01.outputX', name + side + '_lower_arm_bendy_cc_rotation_os_grp_01.rotateX', force=True)
    mc.connectAttr(name + side + '_arm_bendy_lower_arm_follow_MD_01.outputX', name + side + '_lower_arm_bendy_JNT_rotation_os_grp_01.rotateX', force=True)




    # constrain bendy bones to shoulder
    mc.parentConstraint(name + side + '_FK_upper_arm_cc_01', name + side + '_arm_bendy_BN_GRP_01', maintainOffset=True)



    # connect vis attrs
    primary_curve_cv_control_ccs = [name + side + '_shoulder_bendy_cc_01',
                                  name + side + '_upper_arm_bendy_cc_01',
                                  name + side + '_elbow_bendy_cc_01',
                                  name + side + '_lower_arm_bendy_cc_01',
                                  name + side + '_wrist_bendy_cc_01']

    for primary_cc in primary_curve_cv_control_ccs:
        mc.connectAttr(name + side + '_arm_settings_cc_01.bendy_control_visibility_parameter', primary_cc + '.visibility', force=True)
        mc.addAttr(primary_cc, shortName='noodle_tangents_parameter', longName='Tangents', attributeType='enum', enumName='Off:On:', keyable=True)
        children=mc.listRelatives(primary_cc, children=True, type="transform")
        for child in children:
            mc.connectAttr(primary_cc + '.noodle_tangents_parameter', child + '.visibility', force=True)







    """
    scene cleanup
    """

    # parent constrain pole vector control to IK ankle control, hips, COG, and global controls
    mc.parentConstraint(name + side + '_IK_arm_cc_01', name + side + '_clavicle_cc_01', name + '_COG_cc_01', name + '_secondary_global_cc_01', arm_pole_vector_control.Off, maintainOffset=True)

    # parenting
    base_joints_offset_group = transform.make_offset_group(name + side + "_upper_arm_JNT_01")
    mc.group(name = name + side + '_IK_arm_controls_shoulder_constraint_grp_01', empty=True)
    mc.group(name = name + side + '_IK_arm_controls_GRP_01')
    mc.parent(name + side + "_IK_arm_cc_os_grp_01", name + side + '_IK_arm_controls_shoulder_constraint_grp_01')
    mc.connectAttr(name + side + '_IK_arm_controls_GRP_01.visibility', pole_vector_line + '.visibility')
    mc.parent(arm_pole_vector_control.Off, name + side + '_IK_arm_controls_GRP_01' )
    mc.group(name = name + side + '_FK_arm_controls_GRP_01', empty=True)
    mc.parent(name + side + "_FK_upper_arm_cc_stretch_os_grp_01", name + side + '_FK_arm_controls_GRP_01')
    mc.group(name = name + side + '_shoulder_controls_GRP_01', empty=True)
    mc.parent(name + side + "_clavicle_cc_os_grp_01", name + side + '_shoulder_controls_GRP_01')

    # Arm distance nodes GRP
    mc.group(name = name + side + '_arm_distance_nodes_GRP_01', empty=True)
    mc.parent(name + side + '_arm_IK_control_distance_01',
              name + side + '_arm_soft_distance_01',
              name + side + '_upper_arm_distance_01',
              name + side + '_lower_arm_distance_01',
              name + side + '_arm_stretch_distance_01',
              name + side + '_arm_distance_nodes_GRP_01')
    mc.parent(name + side + '_arm_distance_nodes_GRP_01', name + '_secondary_global_cc_01')

    # Arm controls GRP
    mc.group(name = name + side + '_arm_controls_GRP_01', empty=True)
    mc.parent(name + side + '_arm_settings_cc_os_grp_01',
              name + side + '_FK_arm_controls_GRP_01',
              name + side + '_IK_arm_controls_GRP_01',
              name + side + '_hand_controls_GRP_01',
              name + side + '_shoulder_controls_GRP_01',
              name + side + '_arm_bendy_controls_GRP_01',
              name + side + '_arm_controls_GRP_01')

    # Arm extras GRP
    mc.group(name = name + side + '_arm_extras_GRP_01', empty=True)
    mc.parent(name + side + '_upper_arm_loc_connect_grp_01',
              name + side + '_lower_arm_loc_01',
              name + side + '_arm_soft_blend_IK_loc_01',
              name + side + '_arm_distance_nodes_GRP_01',
              name + side + '_IK_arm_cc_distance_loc_01',
              name + side + '_shoulder_PSR_GRP_01',
              name + side + '_arm_splineIK_handle_01',
              name + side + '_arm_splineIK_pointer_handle_01',
              name + side + '_arm_extras_GRP_01')

    # more parenting
    mc.parent(name + side + '_arm_controls_GRP_01', name + '_secondary_global_cc_01')
    mc.parent(name + side + '_arm_extras_GRP_01', name + '_extras_GRP_01')
    mc.group(name = name + side + '_arm_joints_GRP_01', empty=True)
    mc.parent(FK_joints_offset_group,
              IK_joints_offset_group,
              base_joints_offset_group,
              shoulder_joints_offset_group,
              bendy_control_joints_offset_group,
              bendy_joints_offset_group,
              bendy_pointer_joints_offset_group,
              bendy_bones_offset_group,
              name + side + '_arm_joints_GRP_01')
    mc.parent(name + side + '_arm_joints_GRP_01', name + '_skeleton_GRP_01')
    mc.group(name = name + side + '_arm_no_transform_GRP_01', empty=True)
    mc.parent(name + side + '_arm_no_transform_GRP_01', name + '_no_transform_GRP_01')
    mc.parent(pole_vector_line,
              name + side + '_arm_splineIK_curve_01',
              name + side + '_arm_splineIK_pointer_curve_01',
              name + side + '_arm_no_transform_GRP_01')




    #
    # visibility

    #groups
    mc.setAttr( name + side + "_arm_extras_GRP_01.visibility", 0)
    mc.setAttr( name + side + "_arm_no_transform_GRP_01.visibility", 0)

    #IK/FK

    mc.connectAttr( name + side + '_arm_settings_cc_parent_constraint_weight_RMV_01.outValue', name + side + "_IK_arm_controls_GRP_01.visibility", force = True)
    mc.connectAttr( name + side + '_arm_settings_cc_parent_constraint_inverse_weight_RMV_01.output3Dx', name + side + "_FK_arm_controls_GRP_01.visibility", force = True)

    #Hide SplineIK bendy Curve
    #mc.setAttr(name + side + '_arm_splineIK_curve_01.visibility', 0)




    #
    # lock attrs

    # lock translate on arm settings control after reparenting
    mc.setAttr( name + side + "_arm_settings_cc_01.translateX", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_arm_settings_cc_01.translateY", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + side + "_arm_settings_cc_01.translateZ", lock=True, keyable=False, channelBox=False)


    # direct connect hand GRP's transforms to settings os grp's transforms
    mc.connectAttr( name + side + '_arm_settings_cc_os_grp_01.translate', name + side + '_hand_controls_GRP_01.translate', force=True)
    mc.connectAttr( name + side + '_arm_settings_cc_os_grp_01.rotate', name + side + '_hand_controls_GRP_01.rotate', force=True)






    ######################connect to rest of rig##############################
    #controls
    mc.parentConstraint(name + '_chest_cc_01', name + side + '_shoulder_controls_GRP_01', maintainOffset=True)
    mc.parentConstraint(name + side + '_clavicle_cc_01', name + side + '_FK_arm_controls_GRP_01', maintainOffset=True)
    mc.parentConstraint(name + '_secondary_global_cc_01', name + '_COG_cc_01', name + '_chest_cc_01', name + side + '_IK_arm_controls_GRP_01', maintainOffset=True)

    #IK space switching
    mc.shadingNode('condition', asUtility=True, name= name + side + '_arm_ik_cc_chest_follow_COND_01')
    mc.setAttr( name + side + '_arm_ik_cc_chest_follow_COND_01.operation', 1)
    mc.setAttr( name + side + '_arm_ik_cc_chest_follow_COND_01.secondTerm', 2)

    mc.shadingNode('condition', asUtility=True, name= name + side + '_arm_ik_cc_COG_follow_COND_01')
    mc.setAttr( name + side + '_arm_ik_cc_COG_follow_COND_01.operation', 1)
    mc.setAttr( name + side + '_arm_ik_cc_COG_follow_COND_01.secondTerm', 1)

    mc.shadingNode('condition', asUtility=True, name= name + side + '_arm_ik_cc_global_follow_COND_01')
    mc.setAttr( name + side + '_arm_ik_cc_global_follow_COND_01.operation', 1)
    mc.setAttr( name + side + '_arm_ik_cc_global_follow_COND_01.secondTerm', 0)

    mc.connectAttr(name + side + '_arm_settings_cc_01.ik_follow_parameter', name + side + '_arm_ik_cc_global_follow_COND_01.firstTerm')
    mc.connectAttr(name + side + '_arm_settings_cc_01.ik_follow_parameter', name + side + '_arm_ik_cc_COG_follow_COND_01.firstTerm')
    mc.connectAttr(name + side + '_arm_settings_cc_01.ik_follow_parameter', name + side + '_arm_ik_cc_chest_follow_COND_01.firstTerm')

    mc.connectAttr(name + side + '_arm_ik_cc_global_follow_COND_01.outColor.outColorR', name + side + '_IK_arm_controls_GRP_01_parentConstraint1.' + name + '_secondary_global_cc_01W0')
    mc.connectAttr(name + side + '_arm_ik_cc_COG_follow_COND_01.outColor.outColorR', name + side + '_IK_arm_controls_GRP_01_parentConstraint1.' + name + '_COG_cc_01W1')
    mc.connectAttr(name + side + '_arm_ik_cc_chest_follow_COND_01.outColor.outColorR', name + side + '_IK_arm_controls_GRP_01_parentConstraint1.' + name + '_chest_cc_01W2')

    # Connections to shoulder
    #joints
    mc.parentConstraint(name + '_chest_cc_01', name + side + '_scapula_BN_os_grp_01', maintainOffset=True)
    mc.parentConstraint(name + side + '_scapula_BN_01', name + side + '_upper_arm_FK_JNT_os_grp_01', maintainOffset=True)
    #extras
    mc.pointConstraint(name + side + '_shoulder_JNT_01', name + side + '_upper_arm_loc_connect_grp_01', maintainOffset=False)
    mc.parentConstraint(name + '_chest_cc_01', name + side + '_shoulder_PSR_GRP_01', maintainOffset=True)
    #mc.orientConstraint(name + '_shoulder_JNT_01', name + side + '_upper_arm_loc_connect_grp_01', maintainOffset=True)
    #mc.setAttr(name + side + '_IK_arm_controls_GRP_01_parentConstraint1.' + name + '_clavicle_cc_01W3', 0.0)
    #parenting (to avoid constraint flipping in bendy control joints)
    mc.parent(name + side + '_upper_arm_os_grp_01', name + side + '_shoulder_JNT_01')


    #ik pole vector connections
    mc.shadingNode('condition', asUtility=True, name= name + side + '_arm_ik_pole_vector_cc_wrist_follow_COND_01')
    mc.setAttr( name + side + '_arm_ik_pole_vector_cc_wrist_follow_COND_01.operation', 1)
    mc.setAttr( name + side + '_arm_ik_pole_vector_cc_wrist_follow_COND_01.secondTerm', 0)

    mc.shadingNode('condition', asUtility=True, name= name + side + '_arm_ik_pole_vector_cc_shoulder_follow_COND_01')
    mc.setAttr( name + side + '_arm_ik_pole_vector_cc_shoulder_follow_COND_01.operation', 1)
    mc.setAttr( name + side + '_arm_ik_pole_vector_cc_shoulder_follow_COND_01.secondTerm', 1)

    mc.shadingNode('condition', asUtility=True, name= name + side + '_arm_ik_pole_vector_cc_COG_follow_COND_01')
    mc.setAttr( name + side + '_arm_ik_pole_vector_cc_COG_follow_COND_01.operation', 1)
    mc.setAttr( name + side + '_arm_ik_pole_vector_cc_COG_follow_COND_01.secondTerm', 2)

    mc.shadingNode('condition', asUtility=True, name= name + side + '_arm_ik_pole_vector_cc_global_follow_COND_01')
    mc.setAttr( name + side + '_arm_ik_pole_vector_cc_global_follow_COND_01.operation', 1)
    mc.setAttr( name + side + '_arm_ik_pole_vector_cc_global_follow_COND_01.secondTerm', 3)

    mc.connectAttr(name + side + '_arm_pole_vector_cc_01.ik_pole_vector_follow_parameter', name + side + '_arm_ik_pole_vector_cc_global_follow_COND_01.firstTerm')
    mc.connectAttr(name + side + '_arm_pole_vector_cc_01.ik_pole_vector_follow_parameter', name + side + '_arm_ik_pole_vector_cc_COG_follow_COND_01.firstTerm')
    mc.connectAttr(name + side + '_arm_ pole_vector_cc_01.ik_pole_vector_follow_parameter', name + side + '_arm_ik_pole_vector_cc_shoulder_follow_COND_01.firstTerm')
    mc.connectAttr(name + side + '_arm_ pole_vector_cc_01.ik_pole_vector_follow_parameter', name + side + '_arm_ik_pole_vector_cc_wrist_follow_COND_01.firstTerm')

    mc.connectAttr(name + side + '_arm_ik_pole_vector_cc_global_follow_COND_01.outColor.outColorR', name + side + '_arm_pole_vector_cc_os_grp_01_parentConstraint1.' + name + '_secondary_global_cc_01W3')
    mc.connectAttr(name + side + '_arm_ik_pole_vector_cc_COG_follow_COND_01.outColor.outColorR', name + side + '_arm_pole_vector_cc_os_grp_01_parentConstraint1.' + name + '_COG_cc_01W2')
    mc.connectAttr(name + side + '_arm_ik_pole_vector_cc_shoulder_follow_COND_01.outColor.outColorR', name + side + '_arm_pole_vector_cc_os_grp_01_parentConstraint1.' + name + side + '_clavicle_cc_01W1')
    mc.connectAttr(name + side + '_arm_ik_pole_vector_cc_wrist_follow_COND_01.outColor.outColorR', name + side + '_arm_pole_vector_cc_os_grp_01_parentConstraint1.' + name + side + '_IK_arm_cc_01W0')


    '''
    ############################### temporary, remove once gotten stretchies set up
    # create temp bones by duplicating JNT chain
    mc.duplicate(name + side + '_upper_arm_JNT_01', renameChildren=True)
    mc.rename(name + side + '_upper_arm_JNT_02', name + side + '_upper_arm_BN_01')
    mc.rename(name + side + '_lower_arm_JNT_02', name + side + '_lower_arm_BN_01')
    mc.rename(name + side + '_wrist_JNT_02', name + side + '_wrist_BN_01')

    # constrain joints to FK and IK chains
    mc.parentConstraint(name + side + "_upper_arm_JNT_01", name + side + "_upper_arm_BN_01")
    mc.parentConstraint(name + side + "_lower_arm_JNT_01", name + side + "_lower_arm_BN_01")
    mc.parentConstraint(name + side + "_wrist_JNT_01", name + side + "_wrist_BN_01")
    '''


    if name == 'Dragon':
        mc.setAttr( name + side + '_arm_settings_cc_01.FK_IK', 1)


    print('done.')

    """

    make rig module
    rig_module = module.Module( prefix = prefix, base_object=base_rig)


    return{ 'module':rig_module }
    """
