"""
tail @ rig
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
          tail_base_target,
          lower_tail_target,
          middle_tail_target,
          upper_tail_target,
          tail_tip_target,
          prefix = 'tail',
          rig_scale = 1.0,
          base_rig = None
          ):

    """
    @param name: str, base name of rig
    @param tail_base_target: str, tail_base target cc
    @param lower_tail_target: str, lower tail target cc
    @param middle_tail_target: str, middle tail target cc
    @param upper_tail_target: str, upper tail target cc
    @param tail_tip_target: str, tail_tip target cc
    @param prefix: str, prefix to name new tail objects
    @param rig_scale: float, scale of new controls
    @param base_rig: instance of base.module.Base class
    @return: dictionary with rig module objects
    """

    print("building tail...")

    """
    create settings control and add custom attributes
    """

    tail_settings_control = control.Control(
                                  prefix = name + '_tail_settings',
                                  scale = 1.0,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = middle_tail_target,
                                  rotate_to = '',
                                  parent = '',
                                  shape = 'gear',
                                  locked_channels = ['visibility']
                                  )


    # add custom FK attributes to control
    mc.addAttr( tail_settings_control.C, shortName='secondaries_visibility_parameter', longName='Secondaries_Visibility', attributeType='enum', enumName='Off:On:', defaultValue=1, keyable=True)
    mc.addAttr( tail_settings_control.C, shortName='stretch_volume_parameter', longName='Stretch_Volume', attributeType='float', defaultValue=1.0, keyable=True)


    # make two offset groups
    transform.make_offset_group(name + '_tail_settings_cc_01', name + '_tail_settings_constrain')
    transform.make_offset_group(name + '_tail_settings_cc_01', name + '_tail_settings_curve_offset')

    # position settings control
    mc.move(-14.0,0.0,0.0, name + '_tail_settings_curve_offset_os_grp_01', relative=True)
    mc.rotate(90.0,0.0,0.0, name + '_tail_settings_curve_offset_os_grp_01', relative=True)
    mc.scale(4.0,4.0,4.0, name + '_tail_settings_curve_offset_os_grp_01', relative=True)

    # parent control offset group and freeze transforms
    mc.parent(name + '_tail_settings_cc_os_grp_01', name + '_secondary_global_cc_01')
    mc.makeIdentity (apply=True, translate=True, rotate=True, scale=False)

    # align settings control and groups
    mc.rotate(0.0,-90.0,0.0, name + '_tail_settings_cc_os_grp_01', relative=True)

    # lock and hide all rotate, scale, and visibility
    mc.setAttr( name + "_tail_settings_cc_01.rotateX", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_tail_settings_cc_01.rotateY", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_tail_settings_cc_01.rotateZ", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_tail_settings_cc_01.scaleX", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_tail_settings_cc_01.scaleY", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_tail_settings_cc_01.scaleZ", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_tail_settings_cc_01.visibility", lock=True, keyable=False, channelBox=False)



    """
    tail setup
    """

    #organization
    mc.group(name=name + '_tail_no_transform_GRP_01', empty=True)
    mc.parent(name + '_tail_no_transform_GRP_01', name + '_no_transform_GRP_01')
    mc.group(name=name + '_tail_extras_GRP_01', empty=True)
    mc.parent(name + '_tail_extras_GRP_01', name + '_extras_GRP_01')

    ################ create tail joints #####################

    # create tail_base BN
    mc.select(clear=True)
    tail_base_BN=mc.joint(name=name + "_tail_base_BN_01", position = mc.xform(tail_base_target, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=.05)
    mc.parent(tail_base_BN, name + '_secondary_global_cc_01')

    # create upper tail BN
    upper_tail_BN=mc.joint(name=name + "_UPP_tail_BN_01", position = mc.xform(upper_tail_target, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=.05)

    # create middle tail BN
    middle_tail_BN=mc.joint(name=name + "_MID_tail_BN_01", position = mc.xform(middle_tail_target, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=.05)

    # create lower tail BN
    lower_tail_BN=mc.joint(name=name + "_LOW_tail_BN_01", position = mc.xform(lower_tail_target, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=.05)

    # create tail_tip JNT
    tail_tip_JNT=mc.joint(name=name + "_tail_tip_JNT_01", position = mc.xform(tail_tip_target, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=.05)

    # create tail_tip BN
    tail_tip_BN=mc.joint(name=name + "_tail_tip_BN_01", position = mc.xform(tail_tip_target, query=True, rotatePivot=True, worldSpace=True), absolute=True, radius=.05)

    #orient tail joints
    mc.joint( name + '_tail_base_BN_01', edit=True, children=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient = 'yup' )


    #unparent tail_tip JNT and tail_base BN from chain and zero out rotations
    mc.parent(tail_tip_JNT, world=True)
    mc.parent(upper_tail_BN, world=True)
    mc.rotate(0,0,0, tail_tip_BN, absolute=True)
    mc.rotate(0,0,0, tail_base_BN, absolute=True)

    #orient tail_base and tail_tip to world, but with offset so almost matches inner joint orientations
    mc.setAttr( name + "_tail_base_BN_01.jointOrientX", 0.0)
    mc.setAttr( name + "_tail_base_BN_01.jointOrientY", 90.0)
    mc.setAttr( name + "_tail_base_BN_01.jointOrientZ", 0.0)
    mc.setAttr( name + "_tail_tip_JNT_01.jointOrientX", 0.0)
    mc.setAttr( name + "_tail_tip_JNT_01.jointOrientY", 90.0)
    mc.setAttr( name + "_tail_tip_JNT_01.jointOrientZ", 0.0)

    #reconnect whole tail together
    mc.parent(tail_tip_JNT, lower_tail_BN)
    mc.parent(upper_tail_BN, tail_base_BN)

    #parenting
    mc.parent(tail_base_BN, name + '_skeleton_GRP_01')


    ################ make spline IK ########################
    #make exceptions for Dragon's crazy crooked tail
    if name != 'Dragon':
        #make spline IK
        splineIK = mc.ikHandle(name=name + '_tail_splineIK_01', startJoint=tail_base_BN, endEffector=tail_tip_JNT, solver='ikSplineSolver', numSpans=4)[0]

        #rename spline curve
        mc.rename('curve1', name + '_tail_splineIK_curve_01')

        #parenting
        mc.parent(name + '_tail_splineIK_01', name + '_tail_splineIK_curve_01', name + '_tail_extras_GRP_01')


        #set spline IK advanced twist attributes
        mc.setAttr(splineIK + '.dTwistControlEnable', True)
        mc.setAttr(splineIK + '.dWorldUpType', 7)
        mc.setAttr(splineIK + '.dTwistValueType', 1)

        #make curveInfo node to track length of splineIK curve
        curveInfoNode = mc.arclen(name + '_tail_splineIK_curve_01', constructionHistory=True)
        curveInfoNode = mc.rename(curveInfoNode, name + '_tail_splineIK_curve_length_info_01')
        splineIK_start_curve_length = mc.getAttr(curveInfoNode + '.arcLength')

        #setup to get joints to scale with splineIK curve
        #find splineIK curve scale length
        mc.shadingNode('multiplyDivide', asUtility=True, name= name + '_tail_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01')
        mc.shadingNode('multiplyDivide', asUtility=True, name= name + '_tail_splineIK_curve_scale_length_MD_01')
        mc.setAttr( name + '_tail_splineIK_curve_scale_length_MD_01.operation', 2)

        mc.setAttr( name + '_tail_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01.input1X', splineIK_start_curve_length)
        mc.connectAttr( name + '_secret_total_scale_MD_01.outputX', name + '_tail_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01.input2X')

        mc.connectAttr( curveInfoNode + '.arcLength', name + '_tail_splineIK_curve_scale_length_MD_01.input1X' )
        mc.connectAttr( name + '_tail_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01.outputX', name + '_tail_splineIK_curve_scale_length_MD_01.input2X')

        #connect to joints' scale X
        mc.connectAttr( name + '_tail_splineIK_curve_scale_length_MD_01.outputX', tail_base_BN + '.scaleX')
        mc.connectAttr( name + '_tail_splineIK_curve_scale_length_MD_01.outputX', lower_tail_BN + '.scaleX')
        mc.connectAttr( name + '_tail_splineIK_curve_scale_length_MD_01.outputX', middle_tail_BN + '.scaleX')
        mc.connectAttr( name + '_tail_splineIK_curve_scale_length_MD_01.outputX', upper_tail_BN + '.scaleX')




        ################ volume preservation ################
        for part in ['LOW', 'MID', 'UPP']:
            #create and initialize nodes
            mc.shadingNode('plusMinusAverage', asUtility=True, name = name + '_tail_' + part + '_length_minus_one_PMA_01')
            mc.setAttr(name + '_tail_' + part + '_length_minus_one_PMA_01.operation', 2)
            mc.setAttr(name + '_tail_' + part + '_length_minus_one_PMA_01.input3D[1].input3Dy', 1.0 )
            mc.setAttr(name + '_tail_' + part + '_length_minus_one_PMA_01.input3D[1].input3Dz', 1.0 )

            mc.shadingNode('multiplyDivide', asUtility=True, name= name + '_tail_' + part + '_input_multiplied_by_stretch_volume_attr_MD_01')

            mc.shadingNode('multiplyDivide', asUtility=True, name= name + '_tail_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01')
            if part=='LOW':
                mc.setAttr(name + '_tail_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Y', 1.0)
            elif part == 'MID':
                mc.setAttr(name + '_tail_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Y', 1.0)
            elif part =='UPP':
                mc.setAttr(name + '_tail_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input2Y', 1.0)


            mc.shadingNode('plusMinusAverage', asUtility=True, name= name + '_tail_' + part + '_input_plus_one_PMA_01')
            mc.setAttr(name + '_tail_' + part + '_input_plus_one_PMA_01.input3D[1].input3Dy', 1.0 )
            mc.setAttr(name + '_tail_' + part + '_input_plus_one_PMA_01.input3D[1].input3Dz', 1.0 )

            mc.shadingNode('multiplyDivide', asUtility=True, name= name + '_tail_' + part + '_one_divided_by_input_MD_01')
            mc.setAttr(name + '_tail_' + part + '_one_divided_by_input_MD_01.operation', 2)
            mc.setAttr(name + '_tail_' + part + '_one_divided_by_input_MD_01.input1Y', 1.0 )
            mc.setAttr(name + '_tail_' + part + '_one_divided_by_input_MD_01.input1Z', 1.0 )


            #connections
            mc.connectAttr(name + '_tail_splineIK_curve_scale_length_MD_01.outputX', name + '_tail_' + part + '_length_minus_one_PMA_01.input3D[0].input3Dy', force=True)
            mc.connectAttr(name + '_tail_splineIK_curve_scale_length_MD_01.outputX', name + '_tail_' + part + '_length_minus_one_PMA_01.input3D[0].input3Dz', force=True)

            mc.connectAttr(name + '_tail_' + part + '_length_minus_one_PMA_01.output3Dy', name + '_tail_' + part + '_input_multiplied_by_stretch_volume_attr_MD_01.input1Y', force=True)
            mc.connectAttr(name + '_tail_' + part + '_length_minus_one_PMA_01.output3Dz', name + '_tail_' + part + '_input_multiplied_by_stretch_volume_attr_MD_01.input1Z', force=True)
            mc.connectAttr(tail_settings_control.C + '.stretch_volume_parameter', name + '_tail_' + part + '_input_multiplied_by_stretch_volume_attr_MD_01.input2Y', force=True)
            mc.connectAttr(tail_settings_control.C + '.stretch_volume_parameter', name + '_tail_' + part + '_input_multiplied_by_stretch_volume_attr_MD_01.input2Z', force=True)

            mc.connectAttr(name + '_tail_' + part + '_input_multiplied_by_stretch_volume_attr_MD_01.outputY', name + '_tail_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input1Y', force=True)
            mc.connectAttr(name + '_tail_' + part + '_input_multiplied_by_stretch_volume_attr_MD_01.outputZ', name + '_tail_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.input1Z', force=True)

            mc.connectAttr(name + '_tail_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.outputY', name + '_tail_' + part + '_input_plus_one_PMA_01.input3D[0].input3Dy', force=True)
            mc.connectAttr(name + '_tail_' + part + '_input_multiplied_by_stretch_volume_individual_adjustment_MD_01.outputZ', name + '_tail_' + part + '_input_plus_one_PMA_01.input3D[0].input3Dz', force=True)

            mc.connectAttr(name + '_tail_' + part + '_input_plus_one_PMA_01.output3Dy', name + '_tail_' + part + '_one_divided_by_input_MD_01.input2Y', force=True)
            mc.connectAttr(name + '_tail_' + part + '_input_plus_one_PMA_01.output3Dz', name + '_tail_' + part + '_one_divided_by_input_MD_01.input2Z', force=True)

            mc.connectAttr(name + '_tail_' + part + '_one_divided_by_input_MD_01.outputY', name + '_' + part + '_tail_BN_01.scaleY', force=True)
            mc.connectAttr(name + '_tail_' + part + '_one_divided_by_input_MD_01.outputZ', name + '_' + part + '_tail_BN_01.scaleZ', force=True)



        ################ cluster setup ######################

        # make locators to act as the weighted node for each cluster
        mc.spaceLocator(name=name + '_tail_base_CLU_01')
        mc.spaceLocator(name=name + '_LOW_tail_CLU_01')
        mc.spaceLocator(name=name + '_MID_tail_CLU_01')
        mc.spaceLocator(name=name + '_UPP_tail_CLU_01')
        mc.spaceLocator(name=name + '_tail_tip_CLU_01')

        # position locators via offset groups
        mc.group(name=name + '_tail_base_CLU_os_grp_01', empty=True)
        mc.group(name=name + '_LOW_tail_CLU_os_grp_01', empty=True)
        mc.group(name=name + '_MID_tail_CLU_os_grp_01', empty=True)
        mc.group(name=name + '_UPP_tail_CLU_os_grp_01', empty=True)
        mc.group(name=name + '_tail_tip_CLU_os_grp_01', empty=True)

        mc.parent(name + '_tail_base_CLU_01', name + '_tail_base_CLU_os_grp_01')
        mc.parent(name + '_LOW_tail_CLU_01', name + '_LOW_tail_CLU_os_grp_01')
        mc.parent(name + '_MID_tail_CLU_01', name + '_MID_tail_CLU_os_grp_01')
        mc.parent(name + '_UPP_tail_CLU_01', name + '_UPP_tail_CLU_os_grp_01')
        mc.parent(name + '_tail_tip_CLU_01', name + '_tail_tip_CLU_os_grp_01')

        mc.delete(mc.parentConstraint(tail_base_BN, name + '_tail_base_CLU_os_grp_01', maintainOffset=False))
        mc.delete(mc.parentConstraint(lower_tail_BN, name + '_LOW_tail_CLU_os_grp_01', maintainOffset=False))
        mc.delete(mc.parentConstraint(middle_tail_BN, name + '_MID_tail_CLU_os_grp_01', maintainOffset=False))
        mc.delete(mc.parentConstraint(upper_tail_BN, name + '_UPP_tail_CLU_os_grp_01', maintainOffset=False))
        mc.delete(mc.parentConstraint(tail_tip_JNT, name + '_tail_tip_CLU_os_grp_01', maintainOffset=False))

        #make FK-ish hierarchy
        mc.parent(name + '_UPP_tail_CLU_os_grp_01', name + '_tail_base_CLU_01')
        mc.parent(name + '_MID_tail_CLU_os_grp_01', name + '_UPP_tail_CLU_01')
        mc.parent(name + '_LOW_tail_CLU_os_grp_01', name + '_MID_tail_CLU_01')
        mc.parent(name + '_tail_tip_CLU_os_grp_01', name + '_LOW_tail_CLU_01')

        # make a cluster for pretty much every cv on the spline IK curve

        #CANT GET TO WORK WITH CODE, but in viewport all you need to do is change the weighted node entry and hit enter
        #mc.cluster(name + '_tail_splineIK_curve_01.cv[0:1]', name=name + '_tail_base_cluster_01', weightedNode=(name + '_tail_base_CLU_01', name + '_tail_base_CLU_01'))
        """
        #junk code that don't work but might help solve problem later
        # set weighted nodes for clusters to be locators
        mc.setAttr(name + '_tail_base_cluster_01HandleShape.weightedNode', name + '_tail_base_CLU_01')
        mc.setAttr(name + '_LOW_tail_cluster_01HandleShape.weightedNode', name + '_LOW_tail_CLU_01')
        mc.setAttr(name + '_MID_tail_cluster_01HandleShape.weightedNode', name + '_MID_tail_CLU_01')
        mc.setAttr(name + '_UPP_tail_cluster_01HandleShape.weightedNode', name + '_UPP_tail_CLU_01')
        mc.setAttr(name + '_tail_tip_cluster_01HandleShape.weightedNode', name + '_tail_tip_CLU_01')
        """

        mc.cluster(name + '_tail_splineIK_curve_01.cv[0:1]', name=name + '_tail_base_cluster_01', bindState=True, weightedNode=(name + '_tail_base_CLU_01', name + '_tail_base_CLU_01'))
        mc.cluster(name + '_tail_splineIK_curve_01.cv[2]', name=name + '_UPP_tail_cluster_01', bindState=True, weightedNode=(name + '_UPP_tail_CLU_01', name + '_UPP_tail_CLU_01'))
        mc.cluster(name + '_tail_splineIK_curve_01.cv[3]', name=name + '_MID_tail_cluster_01', bindState=True, weightedNode=(name + '_MID_tail_CLU_01', name + '_MID_tail_CLU_01'))
        mc.cluster(name + '_tail_splineIK_curve_01.cv[4]', name=name + '_LOW_tail_cluster_01', bindState=True, weightedNode=(name + '_LOW_tail_CLU_01', name + '_LOW_tail_CLU_01'))
        mc.cluster(name + '_tail_splineIK_curve_01.cv[5:6]', name=name + '_tail_tip_cluster_01', bindState=True, weightedNode=(name + '_tail_tip_CLU_01', name + '_tail_tip_CLU_01'))

        #parent cluster setup under no transform group to avoid... unpleasantness.
        mc.parent(name + '_tail_base_CLU_os_grp_01', name + '_tail_no_transform_GRP_01')




    """
    other tail controls
    """

    tail_base_control = control.Control(
                                  prefix = name + '_tail_base',
                                  scale = 14.0,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = tail_base_BN,
                                  rotate_to = tail_base_BN,
                                  parent = name + '_secondary_global_cc_01',
                                  shape = 'box',
                                  locked_channels = []
                                  )




    #position tail_base control
    temp1=mc.cluster( tail_base_control.C, name=name + 'temp_CLU_01' )
    mc.scale(1.0,1.0,0.2, temp1, relative=True, objectSpace=True)
    mc.delete(tail_base_control.C, constructionHistory=True)


    UPP_tail_control = control.Control(
                                  prefix = name + '_UPP_tail',
                                  scale = 10.0,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = upper_tail_BN,
                                  rotate_to = upper_tail_BN,
                                  parent = tail_base_control.C,
                                  shape = 'box',
                                  locked_channels = []
                                  )

    #position upper_tail control
    mc.scale(0.2,1.0,1.0, UPP_tail_control.C)
    mc.makeIdentity (UPP_tail_control.C, apply=True, translate=False, rotate=False, scale=True)


    MID_tail_control = control.Control(
                                  prefix = name + '_MID_tail',
                                  scale = 8.0,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = middle_tail_BN,
                                  rotate_to = middle_tail_BN,
                                  parent = UPP_tail_control.C,
                                  shape = 'box',
                                  locked_channels = []
                                  )

    #position middle_belly control
    mc.scale(0.2,1.0,1.0, MID_tail_control.C)
    mc.makeIdentity (MID_tail_control.C, apply=True, translate=False, rotate=False, scale=True)


    LOW_tail_control = control.Control(
                                  prefix = name + '_LOW_tail',
                                  scale = 6.0,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = lower_tail_BN,
                                  rotate_to = lower_tail_BN,
                                  parent = MID_tail_control.C,
                                  shape = 'box',
                                  locked_channels = []
                                  )

    #position lower_tail control
    mc.scale(0.2,1.0,1.0, LOW_tail_control.C)
    mc.makeIdentity (LOW_tail_control.C, apply=True, translate=False, rotate=False, scale=True)



    tail_tip_control = control.Control(
                                  prefix = name + '_tail_tip',
                                  scale = 4.0,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = tail_tip_JNT,
                                  rotate_to = tail_tip_JNT,
                                  parent = LOW_tail_control.C,
                                  shape = 'box',
                                  locked_channels = []
                                  )

    #scale and position chest control
    temp=mc.cluster( tail_tip_control.C, name=name + 'temp_CLU_01' )
    mc.scale(1.0,1.0,0.2, temp, relative=True, objectSpace=True)
    mc.delete(tail_tip_control.C, constructionHistory=True)

    #parenting
    mc.parent(tail_settings_control.Off, tail_base_control.C)
    #mc.parent(name + '_tail_splineIK_curve_01', name + '_tail_no_transform_GRP_01')


    ############### connections ###################
    if name != 'Dragon':
        #direct connect translations and rotations of controls to clusters
        mc.connectAttr(tail_base_control.C + '.translate', name + '_tail_base_CLU_01.translate', force=True)
        mc.connectAttr(LOW_tail_control.C + '.translate', name + '_LOW_tail_CLU_01.translate', force=True)
        mc.connectAttr(MID_tail_control.C + '.translate', name + '_MID_tail_CLU_01.translate', force=True)
        mc.connectAttr(UPP_tail_control.C + '.translate', name + '_UPP_tail_CLU_01.translate', force=True)
        mc.connectAttr(tail_tip_control.C + '.translate', name + '_tail_tip_CLU_01.translate', force=True)
        mc.connectAttr(tail_base_control.C + '.rotate', name + '_tail_base_CLU_01.rotate', force=True)
        mc.connectAttr(LOW_tail_control.C + '.rotate', name + '_LOW_tail_CLU_01.rotate', force=True)
        mc.connectAttr(MID_tail_control.C + '.rotate', name + '_MID_tail_CLU_01.rotate', force=True)
        mc.connectAttr(UPP_tail_control.C + '.rotate', name + '_UPP_tail_CLU_01.rotate', force=True)
        mc.connectAttr(tail_tip_control.C + '.rotate', name + '_tail_tip_CLU_01.rotate', force=True)

        #orient and point constrain tail_tip BN to tail_tip control
        mc.orientConstraint(tail_tip_control.C, tail_tip_BN, maintainOffset=False)
        #mc.pointConstraint(tail_tip_control.C, tail_tip_BN, maintainOffset=False)

    elif name == 'Dragon':
        #direct connect translations and rotations of controls to BNs
        mc.parentConstraint(tail_base_control.C, name + '_tail_base_BN_01', maintainOffset=True)
        mc.parentConstraint(LOW_tail_control.C, name + '_LOW_tail_BN_01', maintainOffset=True)
        mc.parentConstraint(MID_tail_control.C, name + '_MID_tail_BN_01', maintainOffset=True)
        mc.parentConstraint(UPP_tail_control.C, name + '_UPP_tail_BN_01', maintainOffset=True)
        mc.parentConstraint(tail_tip_control.C, name + '_tail_tip_BN_01', maintainOffset=True)

    #orient constrain tail_tip JNT to tail_tip control
    mc.orientConstraint(tail_tip_control.C, tail_tip_JNT, maintainOffset=False)



    if name != 'Dragon':
        #connect total tail rotations to twist end and hip control to twist start
        upper_tail_total_x_rotations = mc.shadingNode('plusMinusAverage', asUtility=True, name= name + '_tail_base_plus_LOW_belly_plus_MID_belly_plus_UPP_belly_plus_chest_sum_rotations_X_PMA_01')
        lower_tail_total_x_rotations = mc.shadingNode('plusMinusAverage', asUtility=True, name= name + '_tail_base_plus_hips_sum_rotations_X_PMA_01')

        mc.connectAttr(tail_base_control.C + '.rotateX', upper_tail_total_x_rotations + '.input3D[0].input3Dx', force=True)
        mc.connectAttr(LOW_tail_control.C + '.rotateX', upper_tail_total_x_rotations + '.input3D[1].input3Dx', force=True)
        mc.connectAttr(MID_tail_control.C + '.rotateX', upper_tail_total_x_rotations + '.input3D[2].input3Dx', force=True)
        mc.connectAttr(UPP_tail_control.C + '.rotateX', upper_tail_total_x_rotations + '.input3D[3].input3Dx', force=True)
        mc.connectAttr(tail_tip_control.C + '.rotateX', upper_tail_total_x_rotations + '.input3D[4].input3Dx', force=True)

        mc.connectAttr(tail_base_control.C + '.rotateX', lower_tail_total_x_rotations + '.input3D[0].input3Dx', force=True)

        mc.connectAttr(upper_tail_total_x_rotations + '.output3Dx', splineIK + '.dTwistStartEnd.dTwistEnd', force=True)
        mc.connectAttr(lower_tail_total_x_rotations + '.output3Dx', splineIK + '.dTwistStartEnd.dTwistStart')


    #visibility
    for control_object in [ LOW_tail_control.C, MID_tail_control.C, UPP_tail_control.C ]:
        control_shapes = mc.listRelatives( control_object, shapes=True, type='nurbsCurve' )
        for control_shape in control_shapes:
            if control_shape != None:
                mc.setAttr( control_shape + '.overrideEnabled', True)
                mc.connectAttr(tail_settings_control.C + '.secondaries_visibility_parameter', control_shape + '.visibility', force=True)

    if name == 'Dragon':
        mc.setAttr(name + '_tail_settings_cc_01.Secondaries_Visibility', 1.0)

    #################cleanup#######################
    mc.setAttr(name + "_tail_no_transform_GRP_01.visibility", 0)
    mc.setAttr(name + "_tail_extras_GRP_01.visibility", 0)

    ######################connect to rest of rig##############################
    #controls
    mc.parentConstraint(name + '_hips_cc_01', name + '_tail_base_cc_os_grp_01', maintainOffset=True)
    #extras
    mc.parentConstraint(name + '_hips_cc_01', name + '_tail_extras_GRP_01', maintainOffset=True)

    #raise RuntimeError('Something bad happened')


    print('done.')
