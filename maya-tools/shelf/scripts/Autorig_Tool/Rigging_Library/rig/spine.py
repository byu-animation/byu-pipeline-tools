"""
spine @ rig
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
          root_target,
          lower_belly_target,
          middle_belly_target,
          upper_belly_target,
          lower_ribcage_target,
          prefix = 'spine',
          rig_scale = 1.0,
          base_rig = None
          ):
    
    """
    @param name: str, base name of rig
    @param root_target: str, root target cc
    @param lower_belly_target: str, lower belly target cc
    @param middle_belly_target: str, middle belly target cc
    @param upper_belly_target: str, upper belly target cc
    @param lower_ribcage_target: str, lower_ribcage target cc
    @param prefix: str, prefix to name new spine objects
    @param rig_scale: float, scale of new controls
    @param base_rig: instance of base.module.Base class
    @return: dictionary with rig module objects
    """

    print("building spine...")

    """
    create settings control and add custom attributes
    """

    spine_settings_control = control.Control(
                                  prefix = name + '_spine_settings',
                                  scale = .4,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = middle_belly_target,
                                  rotate_to = '',
                                  parent = '',
                                  shape = 'gear',
                                  locked_channels = ['visibility']
                                  )


    # add custom FK attributes to control
    mc.addAttr( spine_settings_control.C, shortName='secondaries_visibility_parameter', longName='Secondaries_Visibility', attributeType='enum', enumName='Off:On:', defaultValue=1, keyable=True)
    mc.addAttr( spine_settings_control.C, shortName='stretch_volume_parameter', longName='Stretch_Volume', attributeType='float', defaultValue=1.0, keyable=True)

    # make two offset groups
    transform.make_offset_group(name + '_spine_settings_cc_01', name + '_spine_settings_constrain')
    transform.make_offset_group(name + '_spine_settings_cc_01', name + '_spine_settings_curve_offset')

    # position settings control
    mc.move(-1.4,0.0,0.0, name + '_spine_settings_curve_offset_os_grp_01', relative=True)
    mc.rotate(90.0,0.0,0.0, name + '_spine_settings_curve_offset_os_grp_01', relative=True)

    # parent control offset group and freeze transforms
    mc.parent(name + '_spine_settings_cc_os_grp_01', name + '_secondary_global_cc_01')
    mc.makeIdentity (apply=True, translate=True, rotate=True, scale=False)

    # align settings control and groups
    mc.rotate(0.0,-90.0,0.0, name + '_spine_settings_cc_os_grp_01', relative=True)

    # lock and hide all rotate, scale, and visibility
    mc.setAttr( name + "_spine_settings_cc_01.rotateX", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_spine_settings_cc_01.rotateY", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_spine_settings_cc_01.rotateZ", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_spine_settings_cc_01.scaleX", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_spine_settings_cc_01.scaleY", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_spine_settings_cc_01.scaleZ", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_spine_settings_cc_01.visibility", lock=True, keyable=False, channelBox=False)



    """
    spine setup
    """

    #organization
    mc.group(name=name + '_spine_no_transform_GRP_01', empty=True)
    mc.parent(name + '_spine_no_transform_GRP_01', name + '_no_transform_GRP_01')
    mc.group(name=name + '_spine_extras_GRP_01', empty=True)
    mc.parent(name + '_spine_extras_GRP_01', name + '_extras_GRP_01')


    ################ create spine joints #####################

    # create root JNT
    mc.select(clear=True)
    root_JNT=mc.joint(name=name + "_root_JNT_01", position = mc.xform(root_target, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=.05)
    mc.parent(root_JNT, name + '_secondary_global_cc_01')

    # create lower belly BN
    mc.select(clear=True)
    lower_belly_BN=mc.joint(name=name + "_LOW_belly_BN_01", position = mc.xform(lower_belly_target, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=.05)

    # create middle belly BN
    middle_belly_BN=mc.joint(name=name + "_MID_belly_BN_01", position = mc.xform(middle_belly_target, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=.05)

    # create upper belly BN
    upper_belly_BN=mc.joint(name=name + "_UPP_belly_BN_01", position = mc.xform(upper_belly_target, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=.05)

    # create chest JNT
    chest_JNT=mc.joint(name=name + "_chest_JNT_01", position = mc.xform(lower_ribcage_target, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=.05)

    # create chest BN
    chest_BN=mc.joint(name=name + "_chest_BN_01", position = mc.xform(lower_ribcage_target, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=.05)

    # create hip BN
    mc.select(root_JNT)
    hips_BN=mc.joint(name=name + "_hips_BN_01", position = mc.xform(root_target, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=.05)

    #orient three inner joints
    mc.joint( name + '_LOW_belly_BN_01', edit=True, children=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient = 'yup' )

    # make sure inner joint rotations match
    mc.parent(middle_belly_BN, world=True)
    mc.parent(upper_belly_BN, world=True)
    mc.setAttr( name + "_LOW_belly_BN_01.jointOrientX", -90.0)
    mc.setAttr( name + "_MID_belly_BN_01.jointOrientX", -90.0)
    mc.setAttr( name + "_UPP_belly_BN_01.jointOrientX", -90.0)
    mc.parent(middle_belly_BN, lower_belly_BN)
    mc.parent(upper_belly_BN, middle_belly_BN)

    #skip this step to for decidedly un-neutralized dragon - no way to align him to world
    if name == 'Dragon':
        mc.delete(mc.aimConstraint(name + "_LOW_belly_BN_01", name + "_root_JNT_01", maintainOffset=False ))

        #connect whole spine together
        mc.parent(lower_belly_BN, root_JNT)

    else:
        #unparent chest JNT and zero out rotations
        mc.parent(chest_JNT, world=True)
        mc.rotate(0,0,0, chest_JNT)

        #orient root/hips and chest to world, but with offset so almost matches inner joint orientations
        mc.setAttr( name + "_root_JNT_01.jointOrientX", -90.0)
        mc.setAttr( name + "_root_JNT_01.jointOrientY", 0.0)
        mc.setAttr( name + "_root_JNT_01.jointOrientZ", 90.0)
        mc.setAttr( name + "_chest_JNT_01.jointOrientX", -90.0)
        mc.setAttr( name + "_chest_JNT_01.jointOrientY", 0.0)
        mc.setAttr( name + "_chest_JNT_01.jointOrientZ", 90.0)

        #connect whole spine together
        mc.parent(chest_JNT, upper_belly_BN)
        mc.parent(lower_belly_BN, root_JNT)

    #parenting
    mc.parent(root_JNT, name + '_skeleton_GRP_01')
    mc.makeIdentity (root_JNT, apply=True, translate=False, rotate=True, scale=False)






    ################ make spline IK ########################

    #make spline IK
    splineIK = mc.ikHandle(name=name + '_spine_splineIK_01', startJoint=root_JNT, endEffector=chest_JNT, solver='ikSplineSolver', numSpans=4)[0]

    #rename spline curve
    mc.rename('curve1', name + '_spine_splineIK_curve_01')

    #create locators for spline twist up matrices
    upploc=mc.spaceLocator(name=name + '_spine_upper_twist_loc_01')[0]
    lowloc=mc.spaceLocator(name=name + '_spine_lower_twist_loc_01')[0]

    #align locators to controls with offset
    mc.delete(mc.parentConstraint(chest_JNT, upploc, maintainOffset=False))
    mc.delete(mc.parentConstraint(hips_BN, lowloc, maintainOffset=False))
    mc.move(0,10,0, upploc, objectSpace=True, relative=True)
    mc.move(0,10,0, lowloc, objectSpace=True, relative=True)


    #parenting
    mc.parent(name + '_spine_splineIK_01', name + '_spine_splineIK_curve_01', upploc, lowloc, name + '_spine_extras_GRP_01')


    #set spline IK advanced twist attributes
    mc.setAttr(splineIK + '.dTwistControlEnable', True)
    mc.setAttr(splineIK + '.dWorldUpType', 4)
    mc.setAttr(splineIK + '.dTwistValueType', 0)
    mc.connectAttr(lowloc + '.worldMatrix', splineIK + '.dWorldUpMatrix', force=True)
    mc.connectAttr(upploc + '.worldMatrix', splineIK + '.dWorldUpMatrixEnd', force=True)


    #make curveInfo node to track length of splineIK curve
    curveInfoNode = mc.arclen(name + '_spine_splineIK_curve_01', constructionHistory=True)
    curveInfoNode = mc.rename(curveInfoNode, name + '_spine_splineIK_curve_length_info_01')
    splineIK_start_curve_length = mc.getAttr(curveInfoNode + '.arcLength')

    #setup to get joints to scale with splineIK curve
    #find splineIK curve scale length
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + '_spine_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + '_spine_splineIK_curve_scale_length_MD_01')
    mc.setAttr( name + '_spine_splineIK_curve_scale_length_MD_01.operation', 2)

    mc.setAttr( name + '_spine_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01.input1X', splineIK_start_curve_length)
    mc.connectAttr( name + '_secret_total_scale_MD_01.outputX', name + '_spine_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01.input2X')

    mc.connectAttr( curveInfoNode + '.arcLength', name + '_spine_splineIK_curve_scale_length_MD_01.input1X' )
    mc.connectAttr( name + '_spine_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01.outputX', name + '_spine_splineIK_curve_scale_length_MD_01.input2X')

    #connect to joints' scale X
    mc.connectAttr( name + '_spine_splineIK_curve_scale_length_MD_01.outputX', root_JNT + '.scaleX')
    mc.connectAttr( name + '_spine_splineIK_curve_scale_length_MD_01.outputX', lower_belly_BN + '.scaleX')
    mc.connectAttr( name + '_spine_splineIK_curve_scale_length_MD_01.outputX', middle_belly_BN + '.scaleX')
    mc.connectAttr( name + '_spine_splineIK_curve_scale_length_MD_01.outputX', upper_belly_BN + '.scaleX')



    ################ volume preservation ################
    for part in ['LOW', 'MID', 'UPP']:
        #create and initialize nodes
        mc.shadingNode('plusMinusAverage', asUtility=True, name = name + '_spine_' + part + '_length_minus_one_PMA_01')
        mc.setAttr(name + '_spine_' + part + '_length_minus_one_PMA_01.operation', 2)
        mc.setAttr(name + '_spine_' + part + '_length_minus_one_PMA_01.input3D[1].input3Dy', 1.0 )
        mc.setAttr(name + '_spine_' + part + '_length_minus_one_PMA_01.input3D[1].input3Dz', 1.0 )

        mc.shadingNode('multiplyDivide', asUtility=True, name= name + '_spine_' + part + '_input_multiplied_by_stretch_volume_attr_MD_01')

        mc.shadingNode('multiplyDivide', asUtility=True, name= name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01')
        #set scaling factor for each individual piece
        if name == 'Viking':
            if part=='LOW':
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Y', 1.25)
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Z', 1.25)
            elif part == 'MID':
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Y', 1.25)
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Z', 1.25)
            elif part =='UPP':
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Y', 1.0)
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Z', 1.0)
        elif name == 'Beowulf':
            if part=='LOW':
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Y', 2.0)
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Z', 2.0)
            elif part == 'MID':
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Y', 1.0)
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Z', 1.0)
            elif part =='UPP':
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Y', 1.0)
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Z', 1.0)
        elif name == 'Grendel':
            if part=='LOW':
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Y', 1.0)
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Z', 1.0)
            elif part == 'MID':
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Y', 1.0)
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Z', 1.0)
            elif part =='UPP':
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Y', 0.75)
                mc.setAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Z', 0.75)

        mc.shadingNode('plusMinusAverage', asUtility=True, name= name + '_spine_' + part + '_input_plus_one_PMA_01')
        mc.setAttr(name + '_spine_' + part + '_input_plus_one_PMA_01.input3D[1].input3Dy', 1.0 )
        mc.setAttr(name + '_spine_' + part + '_input_plus_one_PMA_01.input3D[1].input3Dz', 1.0 )

        mc.shadingNode('multiplyDivide', asUtility=True, name= name + '_spine_' + part + '_one_divided_by_input_MD_01')
        mc.setAttr(name + '_spine_' + part + '_one_divided_by_input_MD_01.operation', 2)
        mc.setAttr(name + '_spine_' + part + '_one_divided_by_input_MD_01.input1Y', 1.0 )
        mc.setAttr(name + '_spine_' + part + '_one_divided_by_input_MD_01.input1Z', 1.0 )


        #connections
        mc.connectAttr(name + '_spine_splineIK_curve_scale_length_MD_01.outputX', name + '_spine_' + part + '_length_minus_one_PMA_01.input3D[0].input3Dy', force=True)
        mc.connectAttr(name + '_spine_splineIK_curve_scale_length_MD_01.outputX', name + '_spine_' + part + '_length_minus_one_PMA_01.input3D[0].input3Dz', force=True)

        mc.connectAttr(name + '_spine_' + part + '_length_minus_one_PMA_01.output3Dy', name + '_spine_' + part + '_input_multiplied_by_stretch_volume_attr_MD_01.input1Y', force=True)
        mc.connectAttr(name + '_spine_' + part + '_length_minus_one_PMA_01.output3Dz', name + '_spine_' + part + '_input_multiplied_by_stretch_volume_attr_MD_01.input1Z', force=True)
        mc.connectAttr(spine_settings_control.C + '.stretch_volume_parameter', name + '_spine_' + part + '_input_multiplied_by_stretch_volume_attr_MD_01.input2Y', force=True)
        mc.connectAttr(spine_settings_control.C + '.stretch_volume_parameter', name + '_spine_' + part + '_input_multiplied_by_stretch_volume_attr_MD_01.input2Z', force=True)

        mc.connectAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_attr_MD_01.outputY', name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input1Y', force=True)
        mc.connectAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_attr_MD_01.outputZ', name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input1Z', force=True)

        mc.connectAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.outputY', name + '_spine_' + part + '_input_plus_one_PMA_01.input3D[0].input3Dy', force=True)
        mc.connectAttr(name + '_spine_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.outputZ', name + '_spine_' + part + '_input_plus_one_PMA_01.input3D[0].input3Dz', force=True)

        mc.connectAttr(name + '_spine_' + part + '_input_plus_one_PMA_01.output3Dy', name + '_spine_' + part + '_one_divided_by_input_MD_01.input2Y', force=True)
        mc.connectAttr(name + '_spine_' + part + '_input_plus_one_PMA_01.output3Dz', name + '_spine_' + part + '_one_divided_by_input_MD_01.input2Z', force=True)

        mc.connectAttr(name + '_spine_' + part + '_one_divided_by_input_MD_01.outputY', name + '_' + part + '_belly_BN_01.scaleY', force=True)
        mc.connectAttr(name + '_spine_' + part + '_one_divided_by_input_MD_01.outputZ', name + '_' + part + '_belly_BN_01.scaleZ', force=True)



    ################ cluster setup ######################

    # make locators to act as the weighted node for each cluster
    mc.spaceLocator(name=name + '_root_CLU_01')
    mc.spaceLocator(name=name + '_LOW_belly_CLU_01')
    mc.spaceLocator(name=name + '_MID_belly_CLU_01')
    mc.spaceLocator(name=name + '_UPP_belly_CLU_01')
    mc.spaceLocator(name=name + '_chest_CLU_01')

    # position locators via offset groups
    mc.group(name=name + '_root_CLU_os_grp_01', empty=True)
    mc.group(name=name + '_LOW_belly_CLU_os_grp_01', empty=True)
    mc.group(name=name + '_MID_belly_CLU_os_grp_01', empty=True)
    mc.group(name=name + '_UPP_belly_CLU_os_grp_01', empty=True)
    mc.group(name=name + '_chest_CLU_os_grp_01', empty=True)

    mc.parent(name + '_root_CLU_01', name + '_root_CLU_os_grp_01')
    mc.parent(name + '_LOW_belly_CLU_01', name + '_LOW_belly_CLU_os_grp_01')
    mc.parent(name + '_MID_belly_CLU_01', name + '_MID_belly_CLU_os_grp_01')
    mc.parent(name + '_UPP_belly_CLU_01', name + '_UPP_belly_CLU_os_grp_01')
    mc.parent(name + '_chest_CLU_01', name + '_chest_CLU_os_grp_01')

    mc.delete(mc.parentConstraint(root_JNT, name + '_root_CLU_os_grp_01', maintainOffset=False))
    mc.delete(mc.parentConstraint(lower_belly_BN, name + '_LOW_belly_CLU_os_grp_01', maintainOffset=False))
    mc.delete(mc.parentConstraint(middle_belly_BN, name + '_MID_belly_CLU_os_grp_01', maintainOffset=False))
    mc.delete(mc.parentConstraint(upper_belly_BN, name + '_UPP_belly_CLU_os_grp_01', maintainOffset=False))
    mc.delete(mc.parentConstraint(chest_JNT, name + '_chest_CLU_os_grp_01', maintainOffset=False))

    #make FK-ish hierarchy
    mc.parent(name + '_LOW_belly_CLU_os_grp_01', name + '_root_CLU_01')
    mc.parent(name + '_MID_belly_CLU_os_grp_01', name + '_LOW_belly_CLU_01')
    mc.parent(name + '_UPP_belly_CLU_os_grp_01', name + '_MID_belly_CLU_01')
    mc.parent(name + '_chest_CLU_os_grp_01', name + '_UPP_belly_CLU_01')

    # make a cluster for pretty much every cv on the spline IK curve

    #CANT GET TO WORK WITH CODE, but in viewport all you need to do is change the weighted node entry and hit enter
    #mc.cluster(name + '_spine_splineIK_curve_01.cv[0:1]', name=name + '_root_cluster_01', weightedNode=(name + '_root_CLU_01', name + '_root_CLU_01'))
    """
    #junk code that don't work but might help solve problem later
    # set weighted nodes for clusters to be locators
    mc.setAttr(name + '_root_cluster_01HandleShape.weightedNode', name + '_root_CLU_01')
    mc.setAttr(name + '_LOW_belly_cluster_01HandleShape.weightedNode', name + '_LOW_belly_CLU_01')
    mc.setAttr(name + '_MID_belly_cluster_01HandleShape.weightedNode', name + '_MID_belly_CLU_01')
    mc.setAttr(name + '_UPP_belly_cluster_01HandleShape.weightedNode', name + '_UPP_belly_CLU_01')
    mc.setAttr(name + '_chest_cluster_01HandleShape.weightedNode', name + '_chest_CLU_01')
    """

    mc.cluster(name + '_spine_splineIK_curve_01.cv[0:1]', name=name + '_root_cluster_01', bindState=True, weightedNode=(name + '_root_CLU_01', name + '_root_CLU_01'))
    mc.cluster(name + '_spine_splineIK_curve_01.cv[2]', name=name + '_LOW_belly_cluster_01', bindState=True, weightedNode=(name + '_LOW_belly_CLU_01', name + '_LOW_belly_CLU_01'))
    mc.cluster(name + '_spine_splineIK_curve_01.cv[3]', name=name + '_MID_belly_cluster_01', bindState=True, weightedNode=(name + '_MID_belly_CLU_01', name + '_MID_belly_CLU_01'))
    mc.cluster(name + '_spine_splineIK_curve_01.cv[4]', name=name + '_UPP_belly_cluster_01', bindState=True, weightedNode=(name + '_UPP_belly_CLU_01', name + '_UPP_belly_CLU_01'))
    mc.cluster(name + '_spine_splineIK_curve_01.cv[5:6]', name=name + '_chest_cluster_01', bindState=True, weightedNode=(name + '_chest_CLU_01', name + '_chest_CLU_01'))

    #parent cluster setup under no transform group to avoid... unpleasantness.
    mc.parent(name + '_root_CLU_os_grp_01', name + '_spine_no_transform_GRP_01')


    """
    other spine controls
    """

    COG_control = control.Control(
                                  prefix = name + '_COG',
                                  scale = 2.0,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = root_JNT,
                                  rotate_to = root_JNT,
                                  parent = name + '_secondary_global_cc_01',
                                  shape = 'circle_y',
                                  locked_channels = ['visibility']
                                  )

    #rotate control to more or less orient with world (so y is up)
    mc.rotate(0,90,-90, COG_control.Off, objectSpace=True, relative=True)


    hips_control = control.Control(
                                  prefix = name + '_hips',
                                  scale = 1.6,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = root_JNT,
                                  rotate_to = root_JNT,
                                  parent = COG_control.C,
                                  shape = 'box',
                                  locked_channels = ['visibility']
                                  )

    #rotate control to more or less orient with world (so y is up)
    mc.rotate(0,90,-90, hips_control.Off, objectSpace=True, relative=True)

    #position hips control
    temp1=mc.cluster( hips_control.C, name=name + 'temp_CLU_01' )
    mc.scale(1.0,0.4,1.0, temp1, relative=True)
    mc.delete(hips_control.C, constructionHistory=True)


    LOW_belly_control = control.Control(
                                  prefix = name + '_LOW_belly',
                                  scale = 1.0,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = lower_belly_BN,
                                  rotate_to = lower_belly_BN,
                                  parent = COG_control.C,
                                  shape = 'box',
                                  locked_channels = ['visibility']
                                  )

    #rotate control to more or less orient with world (so y is up)
    mc.rotate(0,90,-90, LOW_belly_control.Off, objectSpace=True, relative=True)

    #position lower_belly control
    mc.scale(1.0,0.2,1.0, LOW_belly_control.C, relative=True)
    mc.makeIdentity (LOW_belly_control.C, apply=True, translate=False, rotate=False, scale=True)


    MID_belly_control = control.Control(
                                  prefix = name + '_MID_belly',
                                  scale = 1.0,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = middle_belly_BN,
                                  rotate_to = middle_belly_BN,
                                  parent = LOW_belly_control.C,
                                  shape = 'box',
                                  locked_channels = ['visibility']
                                  )

    #rotate control to more or less orient with world (so y is up)
    mc.rotate(0,90,-90, MID_belly_control.Off, objectSpace=True, relative=True)

    #position middle_belly control
    mc.scale(1.0,0.2,1.0, MID_belly_control.C, relative=True)
    mc.makeIdentity (MID_belly_control.C, apply=True, translate=False, rotate=False, scale=True)


    UPP_belly_control = control.Control(
                                  prefix = name + '_UPP_belly',
                                  scale = 1.0,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = upper_belly_BN,
                                  rotate_to = upper_belly_BN,
                                  parent = MID_belly_control.C,
                                  shape = 'box',
                                  locked_channels = ['visibility']
                                  )

    #rotate control to more or less orient with world (so y is up)
    mc.rotate(0,90,-90, UPP_belly_control.Off, objectSpace=True, relative=True)

    #position upper_belly control
    mc.scale(1.0,0.2,1.0, UPP_belly_control.C, relative=True)
    mc.makeIdentity (UPP_belly_control.C, apply=True, translate=False, rotate=False, scale=True)


    chest_control = control.Control(
                                  prefix = name + '_chest',
                                  scale = 1.2,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = chest_JNT,
                                  rotate_to = chest_JNT,
                                  parent = UPP_belly_control.C,
                                  shape = 'box',
                                  locked_channels = ['visibility']
                                  )

    #rotate control to more or less orient with world (so y is up)
    mc.rotate(0,90,-90, chest_control.Off, objectSpace=True, relative=True)

    #scale and position chest control
    temp=mc.cluster( chest_control.C, name=name + 'temp_CLU_01' )
    mc.scale(1.0,0.6,1.0, temp, relative=True)
    mc.move(0.0,.35,0.0, temp, relative=True)
    mc.delete(chest_control.C, constructionHistory=True)

    #parenting
    mc.parent(spine_settings_control.Off, COG_control.C)
    mc.parent(name + '_spine_splineIK_curve_01', name + '_spine_no_transform_GRP_01')





    ############### connections ###################
    #point and orient constraints to replace below direct connections and allow controls to be world-oriented
    mc.pointConstraint(COG_control.C, name + '_root_CLU_01', maintainOffset=True)
    mc.pointConstraint(LOW_belly_control.C, name + '_LOW_belly_CLU_01', maintainOffset=True)
    mc.pointConstraint(MID_belly_control.C, name + '_MID_belly_CLU_01', maintainOffset=True)
    mc.pointConstraint(UPP_belly_control.C, name + '_UPP_belly_CLU_01', maintainOffset=True)
    mc.pointConstraint(chest_control.C, name + '_chest_CLU_01', maintainOffset=True)
    mc.orientConstraint(COG_control.C, name + '_root_CLU_01', maintainOffset=True)
    mc.orientConstraint(LOW_belly_control.C, name + '_LOW_belly_CLU_01', maintainOffset=True)
    mc.orientConstraint(MID_belly_control.C, name + '_MID_belly_CLU_01', maintainOffset=True)
    mc.orientConstraint(UPP_belly_control.C, name + '_UPP_belly_CLU_01', maintainOffset=True)
    mc.orientConstraint(chest_control.C, name + '_chest_CLU_01', maintainOffset=True)
    mc.scaleConstraint(COG_control.C, name + '_root_CLU_01', maintainOffset=True)
    mc.scaleConstraint(LOW_belly_control.C, name + '_LOW_belly_CLU_01', maintainOffset=True)
    mc.scaleConstraint(MID_belly_control.C, name + '_MID_belly_CLU_01', maintainOffset=True)
    mc.scaleConstraint(UPP_belly_control.C, name + '_UPP_belly_CLU_01', maintainOffset=True)
    mc.scaleConstraint(chest_control.C, name + '_chest_CLU_01', maintainOffset=True)


    '''
    #direct connect translations and rotations of controls to clusters
    mc.connectAttr(COG_control.C + '.translate', name + '_root_CLU_01.translate', force=True)
    mc.connectAttr(LOW_belly_control.C + '.translate', name + '_LOW_belly_CLU_01.translate', force=True)
    mc.connectAttr(MID_belly_control.C + '.translate', name + '_MID_belly_CLU_01.translate', force=True)
    mc.connectAttr(UPP_belly_control.C + '.translate', name + '_UPP_belly_CLU_01.translate', force=True)
    mc.connectAttr(chest_control.C + '.translate', name + '_chest_CLU_01.translate', force=True)
    mc.connectAttr(COG_control.C + '.rotate', name + '_root_CLU_01.rotate', force=True)
    mc.connectAttr(LOW_belly_control.C + '.rotate', name + '_LOW_belly_CLU_01.rotate', force=True)
    mc.connectAttr(MID_belly_control.C + '.rotate', name + '_MID_belly_CLU_01.rotate', force=True)
    mc.connectAttr(UPP_belly_control.C + '.rotate', name + '_UPP_belly_CLU_01.rotate', force=True)
    mc.connectAttr(chest_control.C + '.rotate', name + '_chest_CLU_01.rotate', force=True)
    '''

    #orient constrain chest control to chest JNT
    mc.orientConstraint(chest_control.C, chest_JNT, maintainOffset=True)

    #orient and point constrain chest and hips BNs to chest and hips controlss
    mc.orientConstraint(hips_control.C, hips_BN, maintainOffset=True)
    mc.orientConstraint(chest_control.C, chest_BN, maintainOffset=True)
    mc.pointConstraint(hips_control.C, hips_BN, maintainOffset=True)
    mc.pointConstraint(chest_control.C, chest_BN, maintainOffset=True)

    #parent constrain twist locators to controls
    mc.parentConstraint(chest_control.C, upploc, maintainOffset=True)
    mc.parentConstraint(hips_control.C, lowloc, maintainOffset=True)

    #connect total spine rotations to twist end and hip control to twist start (values are actually y rotations of controls, x rotations for joints
    upper_spine_total_x_rotations = mc.shadingNode('plusMinusAverage', asUtility=True, name= name + '_COG_plus_LOW_belly_plus_MID_belly_plus_UPP_belly_plus_chest_sum_rotations_X_PMA_01')
    lower_spine_total_x_rotations = mc.shadingNode('plusMinusAverage', asUtility=True, name= name + '_COG_plus_hips_sum_rotations_X_PMA_01')

    mc.connectAttr(COG_control.C + '.rotateY', upper_spine_total_x_rotations + '.input3D[0].input3Dx', force=True)
    mc.connectAttr(LOW_belly_control.C + '.rotateY', upper_spine_total_x_rotations + '.input3D[1].input3Dx', force=True)
    mc.connectAttr(MID_belly_control.C + '.rotateY', upper_spine_total_x_rotations + '.input3D[2].input3Dx', force=True)
    mc.connectAttr(UPP_belly_control.C + '.rotateY', upper_spine_total_x_rotations + '.input3D[3].input3Dx', force=True)
    mc.connectAttr(chest_control.C + '.rotateY', upper_spine_total_x_rotations + '.input3D[4].input3Dx', force=True)

    mc.connectAttr(COG_control.C + '.rotateY', lower_spine_total_x_rotations + '.input3D[0].input3Dx', force=True)
    mc.connectAttr(hips_control.C + '.rotateY', lower_spine_total_x_rotations + '.input3D[1].input3Dx', force=True)

    #####ditched in favor of simpler objectUp(start/end) option - can't twist spine past 180, but more stable in crazy COG orientations/gimbal locks
    #mc.connectAttr(upper_spine_total_x_rotations + '.output3Dx', splineIK + '.dTwistStartEnd.dTwistEnd', force=True)
    #mc.connectAttr(lower_spine_total_x_rotations + '.output3Dx', splineIK + '.dTwistStartEnd.dTwistStart')


    #visibility
    for control_object in [ LOW_belly_control.C, MID_belly_control.C, UPP_belly_control.C ]:
        control_shapes = mc.listRelatives( control_object, shapes=True, type='nurbsCurve' )
        for control_shape in control_shapes:
            if control_shape != None:
                mc.setAttr( control_shape + '.overrideEnabled', True)
                mc.connectAttr(spine_settings_control.C + '.secondaries_visibility_parameter', control_shape + '.visibility', force=True)



    #################cleanup#######################
    mc.setAttr(name + "_spine_no_transform_GRP_01.visibility", 0)
    mc.setAttr(name + "_spine_extras_GRP_01.visibility", 0)



    print('done.')
