"""
neck @ rig 
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
          neck_base_target,
          lower_neck_target,
          middle_neck_target,
          upper_neck_target,
          head_target,
          prefix = 'neck',
          rig_scale = 1.0,
          base_rig = None 
          ):
    
    """
    @param name: str, base name of rig
    @param neck_base_target: str, neck_base target cc
    @param lower_neck_target: str, lower neck target cc
    @param middle_neck_target: str, middle neck target cc
    @param upper_neck_target: str, upper neck target cc
    @param head_target: str, head target cc
    @param prefix: str, prefix to name new neck objects
    @param rig_scale: float, scale of new controls
    @param base_rig: instance of base.module.Base class
    @return: dictionary with rig module objects
    """
    
    print("building neck...")
    
    """ 
    create settings control and add custom attributes
    """
    
    neck_settings_control = control.Control(
                                  prefix = name + '_neck_settings',
                                  scale = .04,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = middle_neck_target,
                                  rotate_to = '',
                                  parent = '',
                                  shape = 'gear',
                                  locked_channels = ['visibility']
                                  )
    
    
    # add custom attributes to control
    mc.addAttr( neck_settings_control.C, shortName='secondaries_visibility_parameter', longName='Secondaries_Visibility', attributeType='enum', enumName='Off:On:', defaultValue=0, keyable=True)    
    mc.addAttr( neck_settings_control.C, shortName='chicken_neck_parameter', longName='Chicken_Neck', attributeType='enum', enumName='On:Off:', keyable=True)    

    # make two offset groups
    transform.make_offset_group(name + '_neck_settings_cc_01', name + '_neck_settings_constrain')
    transform.make_offset_group(name + '_neck_settings_cc_01', name + '_neck_settings_curve_offset')
  
    # position settings control
    mc.move(-.14,0.0,0.0, name + '_neck_settings_curve_offset_os_grp_01', relative=True)
    mc.rotate(90.0,0.0,0.0, name + '_neck_settings_curve_offset_os_grp_01', relative=True)

    # parent control offset group and freeze transforms
    mc.parent(name + '_neck_settings_cc_os_grp_01', name + '_secondary_global_cc_01')
    mc.makeIdentity (apply=True, translate=True, rotate=True, scale=False)
    
    # align settings control and groups
    mc.rotate(0.0,-90.0,0.0, name + '_neck_settings_cc_os_grp_01', relative=True)
    
    # lock and hide all rotate, scale, and visibility
    mc.setAttr( name + "_neck_settings_cc_01.rotateX", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_neck_settings_cc_01.rotateY", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_neck_settings_cc_01.rotateZ", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_neck_settings_cc_01.scaleX", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_neck_settings_cc_01.scaleY", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_neck_settings_cc_01.scaleZ", lock=True, keyable=False, channelBox=False)
    mc.setAttr( name + "_neck_settings_cc_01.visibility", lock=True, keyable=False, channelBox=False)

    

    """
    neck setup
    """
    
    ################ create neck joints #####################

    # create neck_base BN
    mc.select(clear=True)
    neck_base_BN=mc.joint(name=name + "_neck_base_BN_01", position = mc.xform(neck_base_target, query=True, translation=True, worldSpace=True), absolute=True, radius=.01)
    mc.parent(neck_base_BN, name + '_secondary_global_cc_01')
    
    # create lower neck BN
    mc.select(clear=True)
    lower_neck_BN=mc.joint(name=name + "_LOW_neck_BN_01", position = mc.xform(lower_neck_target, query=True, translation=True, worldSpace=True), absolute=True, radius=.01)
    
    # create middle neck BN
    middle_neck_BN=mc.joint(name=name + "_MID_neck_BN_01", position = mc.xform(middle_neck_target, query=True, translation=True, worldSpace=True), absolute=True, radius=.01)
    
    # create upper neck BN
    upper_neck_BN=mc.joint(name=name + "_UPP_neck_BN_01", position = mc.xform(upper_neck_target, query=True, translation=True, worldSpace=True), absolute=True, radius=.01)
    
    # create head JNT
    head_JNT=mc.joint(name=name + "_head_JNT_01", position = mc.xform(head_target, query=True, translation=True, worldSpace=True), absolute=True, radius=.01)
    
    #orient three inner joints
    mc.joint( name + '_LOW_neck_BN_01', edit=True, children=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient = 'yup' )
    
    # make sure inner joint rotations match
    mc.parent(middle_neck_BN, world=True)
    mc.parent(upper_neck_BN, world=True)
    mc.setAttr( name + "_LOW_neck_BN_01.jointOrientX", -90.0)
    mc.setAttr( name + "_MID_neck_BN_01.jointOrientX", -90.0)
    mc.setAttr( name + "_UPP_neck_BN_01.jointOrientX", -90.0)  
    mc.parent(middle_neck_BN, lower_neck_BN)
    mc.parent(upper_neck_BN, middle_neck_BN)       
    
    #unparent head JNT and zero out rotations
    mc.parent(head_JNT, world=True)
    mc.rotate(0,0,0, head_JNT)  
        
    #orient neck_base and head to world, but with offset so almost matches inner joint orientations
    mc.setAttr( name + "_neck_base_BN_01.jointOrientX", -90.0)
    mc.setAttr( name + "_neck_base_BN_01.jointOrientY", 0.0)
    mc.setAttr( name + "_neck_base_BN_01.jointOrientZ", 90.0)
    mc.setAttr( name + "_head_JNT_01.jointOrientX", -90.0)
    mc.setAttr( name + "_head_JNT_01.jointOrientY", 0.0)
    mc.setAttr( name + "_head_JNT_01.jointOrientZ", 90.0)

    
    # create head BN
    head_BN=mc.duplicate(name + "_head_JNT_01", name=name + "_head_BN_01")
    mc.pointConstraint(head_JNT, head_BN)    
    
    #connect whole neck together
    mc.parent(head_JNT, upper_neck_BN)
    mc.parent(lower_neck_BN, neck_base_BN)

    #parenting
    mc.parent(neck_base_BN, name + '_skeleton_GRP_01')
    
    
    
    
    ################ make spline IK ########################
    
    #make spline IK
    splineIK = mc.ikHandle(name=name + '_neck_splineIK_01', startJoint=neck_base_BN, endEffector=head_JNT, solver='ikSplineSolver', numSpans=4)[0]
    
    #rename spline curve
    mc.rename('curve1', name + '_neck_splineIK_curve_01')
    
    #parenting
    mc.group(name=name + '_neck_extras_GRP_01', empty=True)
    mc.parent(name + '_neck_splineIK_01', name + '_neck_splineIK_curve_01', name + '_neck_extras_GRP_01')
    mc.parent(name + '_neck_extras_GRP_01', name + '_extras_GRP_01')

    #set spline IK advanced twist attributes
    mc.setAttr(splineIK + '.dTwistControlEnable', True)
    mc.setAttr(splineIK + '.dWorldUpType', 7)
    mc.setAttr(splineIK + '.dTwistValueType', 1)
    mc.setAttr(splineIK + '.rootTwistMode', 1)

    #make curveInfo node to track length of splineIK curve
    curveInfoNode = mc.arclen(name + '_neck_splineIK_curve_01', constructionHistory=True)
    curveInfoNode = mc.rename(curveInfoNode, name + '_neck_splineIK_curve_length_info_01')
    splineIK_start_curve_length = mc.getAttr(curveInfoNode + '.arcLength')
    
    #setup to get joints to scale with splineIK curve
    #find splineIK curve scale length
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + '_neck_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01')
    mc.shadingNode('multiplyDivide', asUtility=True, name= name + '_neck_splineIK_curve_scale_length_MD_01')
    mc.setAttr( name + '_neck_splineIK_curve_scale_length_MD_01.operation', 2)
    
    mc.setAttr( name + '_neck_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01.input1X', splineIK_start_curve_length)
    mc.connectAttr( name + '_secret_total_scale_MD_01.outputX', name + '_neck_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01.input2X')

    mc.connectAttr( curveInfoNode + '.arcLength', name + '_neck_splineIK_curve_scale_length_MD_01.input1X' )
    mc.connectAttr( name + '_neck_splineIK_initial_curve_length_multiplied_by_rig_scale_MD_01.outputX', name + '_neck_splineIK_curve_scale_length_MD_01.input2X')
    
    #connect to joints' scale X
    mc.connectAttr( name + '_neck_splineIK_curve_scale_length_MD_01.outputX', neck_base_BN + '.scaleX')
    mc.connectAttr( name + '_neck_splineIK_curve_scale_length_MD_01.outputX', lower_neck_BN + '.scaleX')
    mc.connectAttr( name + '_neck_splineIK_curve_scale_length_MD_01.outputX', middle_neck_BN + '.scaleX')
    mc.connectAttr( name + '_neck_splineIK_curve_scale_length_MD_01.outputX', upper_neck_BN + '.scaleX')
    
    
        
    
    ################ cluster setup ######################
    
    # make locators to act as the weighted node for each cluster
    mc.spaceLocator(name=name + '_neck_base_CLU_01')
    mc.spaceLocator(name=name + '_LOW_neck_CLU_01')
    mc.spaceLocator(name=name + '_MID_neck_CLU_01')
    mc.spaceLocator(name=name + '_UPP_neck_CLU_01')
    mc.spaceLocator(name=name + '_head_CLU_01')
    
    # position locators via offset groups
    mc.group(name=name + '_neck_base_CLU_os_grp_01', empty=True)
    mc.group(name=name + '_LOW_neck_CLU_os_grp_01', empty=True)
    mc.group(name=name + '_MID_neck_CLU_os_grp_01', empty=True)
    mc.group(name=name + '_UPP_neck_CLU_os_grp_01', empty=True)
    mc.group(name=name + '_head_CLU_os_grp_01', empty=True)
    
    mc.parent(name + '_neck_base_CLU_01', name + '_neck_base_CLU_os_grp_01')
    mc.parent(name + '_LOW_neck_CLU_01', name + '_LOW_neck_CLU_os_grp_01')
    mc.parent(name + '_MID_neck_CLU_01', name + '_MID_neck_CLU_os_grp_01')
    mc.parent(name + '_UPP_neck_CLU_01', name + '_UPP_neck_CLU_os_grp_01')
    mc.parent(name + '_head_CLU_01', name + '_head_CLU_os_grp_01')
    
    mc.delete(mc.parentConstraint(neck_base_BN, name + '_neck_base_CLU_os_grp_01', maintainOffset=False))
    mc.delete(mc.parentConstraint(lower_neck_BN, name + '_LOW_neck_CLU_os_grp_01', maintainOffset=False))
    mc.delete(mc.parentConstraint(middle_neck_BN, name + '_MID_neck_CLU_os_grp_01', maintainOffset=False))
    mc.delete(mc.parentConstraint(upper_neck_BN, name + '_UPP_neck_CLU_os_grp_01', maintainOffset=False))
    mc.delete(mc.parentConstraint(head_JNT, name + '_head_CLU_os_grp_01', maintainOffset=False))

    #make FK-ish hierarchy
    mc.parent(name + '_LOW_neck_CLU_os_grp_01', name + '_neck_base_CLU_01')
    mc.parent(name + '_MID_neck_CLU_os_grp_01', name + '_LOW_neck_CLU_01')
    mc.parent(name + '_UPP_neck_CLU_os_grp_01', name + '_MID_neck_CLU_01')
    mc.parent(name + '_head_CLU_os_grp_01', name + '_UPP_neck_CLU_01')

    # make a cluster for pretty much every cv on the spline IK curve
    
    #CANT GET TO WORK WITH CODE, but in viewport all you need to do is change the weighted node entry and hit enter
    #mc.cluster(name + '_neck_splineIK_curve_01.cv[0:1]', name=name + '_neck_base_cluster_01', weightedNode=(name + '_neck_base_CLU_01', name + '_neck_base_CLU_01'))
    """ 
    #junk code that don't work but might help solve problem later
    # set weighted nodes for clusters to be locators 
    mc.setAttr(name + '_neck_base_cluster_01HandleShape.weightedNode', name + '_neck_base_CLU_01')
    mc.setAttr(name + '_LOW_neck_cluster_01HandleShape.weightedNode', name + '_LOW_neck_CLU_01')
    mc.setAttr(name + '_MID_neck_cluster_01HandleShape.weightedNode', name + '_MID_neck_CLU_01')
    mc.setAttr(name + '_UPP_neck_cluster_01HandleShape.weightedNode', name + '_UPP_neck_CLU_01')
    mc.setAttr(name + '_head_cluster_01HandleShape.weightedNode', name + '_head_CLU_01')
    """
    
    mc.cluster(name + '_neck_splineIK_curve_01.cv[0:1]', name=name + '_neck_base_cluster_01', bindState=True, weightedNode=(name + '_neck_base_CLU_01', name + '_neck_base_CLU_01'))
    mc.cluster(name + '_neck_splineIK_curve_01.cv[2]', name=name + '_LOW_neck_cluster_01', bindState=True, weightedNode=(name + '_LOW_neck_CLU_01', name + '_LOW_neck_CLU_01'))
    mc.cluster(name + '_neck_splineIK_curve_01.cv[3]', name=name + '_MID_neck_cluster_01', bindState=True, weightedNode=(name + '_MID_neck_CLU_01', name + '_MID_neck_CLU_01'))
    mc.cluster(name + '_neck_splineIK_curve_01.cv[4]', name=name + '_UPP_neck_cluster_01', bindState=True, weightedNode=(name + '_UPP_neck_CLU_01', name + '_UPP_neck_CLU_01'))
    mc.cluster(name + '_neck_splineIK_curve_01.cv[5:6]', name=name + '_head_cluster_01', bindState=True, weightedNode=(name + '_head_CLU_01', name + '_head_CLU_01'))
    
    #parent cluster setup under no transform group to avoid... unpleasantness.
    mc.group(name=name + '_neck_no_transform_GRP_01', empty=True)
    mc.parent(name + '_neck_base_CLU_os_grp_01', name + '_neck_no_transform_GRP_01')
    mc.parent(name + '_neck_no_transform_GRP_01', name + '_no_transform_GRP_01')



    """
    other neck controls
    """

    neck_base_control = control.Control(
                                  prefix = name + '_neck_base',
                                  scale = .12,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = neck_base_BN,
                                  rotate_to = neck_base_BN,
                                  parent = name + '_secondary_global_cc_01',
                                  shape = 'box',
                                  locked_channels = ['visibility']
                                  )


    #rotate control to more or less orient with world (so y is up)
    mc.rotate(0,90,-90, neck_base_control.Off, objectSpace=True, relative=True)
    
    #position neck_base control
    temp1=mc.cluster( neck_base_control.C, name=name + 'temp_CLU_01' )
    mc.scale(1.0,0.4,1.0, temp1, relative=True)
    mc.delete(neck_base_control.C, constructionHistory=True)        
         
         
    LOW_neck_control = control.Control(
                                  prefix = name + '_LOW_neck',
                                  scale = .1,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = lower_neck_BN,
                                  rotate_to = lower_neck_BN,
                                  parent = neck_base_control.C,
                                  shape = 'box',
                                  locked_channels = []
                                  )
    
    #rotate control to more or less orient with world (so y is up)
    mc.rotate(0,90,-90, LOW_neck_control.Off, objectSpace=True, relative=True)
    
    #position lower_neck control
    mc.scale(1.0,0.2,1.0, LOW_neck_control.C, relative=True)
    mc.makeIdentity (LOW_neck_control.C, apply=True, translate=False, rotate=False, scale=True)
      
         
    MID_neck_control = control.Control(
                                  prefix = name + '_MID_neck',
                                  scale = .1,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = middle_neck_BN,
                                  rotate_to = middle_neck_BN,
                                  parent = LOW_neck_control.C,
                                  shape = 'box',
                                  locked_channels = []
                                  )
    
    #rotate control to more or less orient with world (so y is up)
    mc.rotate(0,90,-90, MID_neck_control.Off, objectSpace=True, relative=True)
        
    #position middle_belly control
    mc.scale(1.0,0.2,1.0, MID_neck_control.C, relative=True)
    mc.makeIdentity (MID_neck_control.C, apply=True, translate=False, rotate=False, scale=True)
    
    
    UPP_neck_control = control.Control(
                                  prefix = name + '_UPP_neck',
                                  scale = .1,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = upper_neck_BN,
                                  rotate_to = upper_neck_BN,
                                  parent = MID_neck_control.C,
                                  shape = 'box',
                                  locked_channels = []
                                  )
    
    #rotate control to more or less orient with world (so y is up)
    mc.rotate(0,90,-90, UPP_neck_control.Off, objectSpace=True, relative=True)    
    
    #position upper_belly control
    mc.scale(1.0,0.2,1.0, UPP_neck_control.C, relative=True)
    mc.makeIdentity (UPP_neck_control.C, apply=True, translate=False, rotate=False, scale=True) 
            
            
    head_control = control.Control(
                                  prefix = name + '_head',
                                  scale = .12,
                                  use_numerical_transforms = False,
                                  transform_x = 0.0,
                                  transform_y = 0.0,
                                  transform_z = 0.0,
                                  translate_to = name + '_head_BN_01',
                                  rotate_to = name + '_head_BN_01',
                                  parent = UPP_neck_control.C,
                                  shape = 'box',
                                  locked_channels = ['visibility']
                                  )
    
    #rotate control to more or less orient with world (so y is up)
    mc.rotate(0,90,-90, head_control.Off, objectSpace=True, relative=True)    
    
    #scale and position chest control
    temp=mc.cluster( head_control.C, name=name + 'temp_CLU_01' )
    mc.scale(1.0,0.6,1.0, temp, relative=True)
    mc.move(0.0,.035,0.0, temp, relative=True)
    mc.delete(head_control.C, constructionHistory=True)        
        
    #parenting
    mc.parent(neck_settings_control.Off, neck_base_control.C)

    chicken=mc.spaceLocator(name=name + '_neck_chicken_translate_loc_01')
    mc.delete(mc.parentConstraint(head_control.C, chicken))
    mc.parent(chicken, UPP_neck_control.C)
    mc.parent(head_control.Off, name + '_secondary_global_cc_01')
    mc.pointConstraint(chicken, head_control.Off)
    mc.orientConstraint(chicken, head_control.Off)

    #connect chicken neck parameter to orient constraint weight
    mc.connectAttr(name + '_neck_settings_cc_01.chicken_neck_parameter', head_control.Off + '_orientConstraint1.' + name + '_neck_chicken_translate_loc_01W0', force=True)



    ############### connections ###################
    #point and orient constraints to replace below direct connections and allow controls to be world-oriented 
    mc.pointConstraint(neck_base_control.C, name + '_neck_base_CLU_01', maintainOffset=True)
    mc.pointConstraint(LOW_neck_control.C, name + '_LOW_neck_CLU_01', maintainOffset=True)
    mc.pointConstraint(MID_neck_control.C, name + '_MID_neck_CLU_01', maintainOffset=True)
    mc.pointConstraint(UPP_neck_control.C, name + '_UPP_neck_CLU_01', maintainOffset=True)
    mc.pointConstraint(head_control.C, name + '_head_CLU_01', maintainOffset=True)
    mc.orientConstraint(neck_base_control.C, name + '_neck_base_CLU_01', maintainOffset=True)
    mc.orientConstraint(LOW_neck_control.C, name + '_LOW_neck_CLU_01', maintainOffset=True)
    mc.orientConstraint(MID_neck_control.C, name + '_MID_neck_CLU_01', maintainOffset=True)
    mc.orientConstraint(UPP_neck_control.C, name + '_UPP_neck_CLU_01', maintainOffset=True)
    mc.orientConstraint(head_control.C, name + '_head_CLU_01', maintainOffset=True)    
    
    '''
    #direct connect translations and rotations of controls to clusters
    mc.connectAttr(neck_base_control.C + '.translate', name + '_neck_base_CLU_01.translate', force=True)
    mc.connectAttr(LOW_neck_control.C + '.translate', name + '_LOW_neck_CLU_01.translate', force=True)
    mc.connectAttr(MID_neck_control.C + '.translate', name + '_MID_neck_CLU_01.translate', force=True)
    mc.connectAttr(UPP_neck_control.C + '.translate', name + '_UPP_neck_CLU_01.translate', force=True)
    mc.connectAttr(head_control.C + '.translate', name + '_head_CLU_01.translate', force=True)
    mc.connectAttr(neck_base_control.C + '.rotate', name + '_neck_base_CLU_01.rotate', force=True)
    mc.connectAttr(LOW_neck_control.C + '.rotate', name + '_LOW_neck_CLU_01.rotate', force=True)
    mc.connectAttr(MID_neck_control.C + '.rotate', name + '_MID_neck_CLU_01.rotate', force=True)
    mc.connectAttr(UPP_neck_control.C + '.rotate', name + '_UPP_neck_CLU_01.rotate', force=True)
    mc.connectAttr(head_control.C + '.rotate', name + '_head_CLU_01.rotate', force=True)
    '''
    
    #orient constrain head JNT to head control
    mc.orientConstraint(head_control.C, head_JNT, maintainOffset=True)
    #delete head BN's point constraint to head_JNT
    mc.delete(name + '_head_BN_01_pointConstraint1')
        
    #orient and point constrain head BN to head control 
    mc.orientConstraint(head_control.C, head_BN, maintainOffset=True)
    mc.pointConstraint(head_control.C, head_BN, maintainOffset=True)

    #make locator to track rotations of neck's root in rig
    mc.spaceLocator(name=name + '_neck_base_tracker_loc_01')
    mc.group(name + '_neck_base_tracker_loc_01', name=name + '_neck_base_tracker_loc_os_grp_01')
    mc.delete(mc.parentConstraint(neck_base_BN, name + '_neck_base_tracker_loc_os_grp_01', maintainOffset=False))
    mc.parent(name + '_neck_base_tracker_loc_os_grp_01', name + '_neck_extras_GRP_01')
    
    #make locator to track rotations of head in rig
    head_tracker = mc.spaceLocator(name=name + '_head_tracker_loc_01')[0]
    mc.group(name + '_head_tracker_loc_01', name=name + '_head_tracker_loc_os_grp_01')
    mc.delete(mc.parentConstraint(head_BN, name + '_head_tracker_loc_os_grp_01', maintainOffset=False))
    mc.parent(name + '_head_tracker_loc_os_grp_01', name + '_neck_extras_GRP_01')
    mc.parentConstraint(head_control.C, name + '_head_tracker_loc_os_grp_01', maintainOffset=False)
    
    #connect total neck rotations to twist end and hip control to twist start
    upper_neck_total_x_rotations = mc.shadingNode('plusMinusAverage', asUtility=True, name= name + '_neck_base_plus_LOW_belly_plus_MID_belly_plus_UPP_belly_plus_chest_sum_rotations_X_PMA_01')
    lower_neck_total_x_rotations = mc.shadingNode('plusMinusAverage', asUtility=True, name= name + '_neck_base_plus_hips_sum_rotations_X_PMA_01')

    mc.connectAttr(neck_base_control.C + '.rotateY', upper_neck_total_x_rotations + '.input3D[0].input3Dx', force=True) 
    mc.connectAttr(LOW_neck_control.C + '.rotateY', upper_neck_total_x_rotations + '.input3D[1].input3Dx', force=True) 
    mc.connectAttr(MID_neck_control.C + '.rotateY', upper_neck_total_x_rotations + '.input3D[2].input3Dx', force=True) 
    mc.connectAttr(UPP_neck_control.C + '.rotateY', upper_neck_total_x_rotations + '.input3D[3].input3Dx', force=True) 
    mc.connectAttr(head_tracker + '.rotateY', upper_neck_total_x_rotations + '.input3D[4].input3Dx', force=True) 
    
    mc.connectAttr(name + '_neck_base_tracker_loc_01.rotateX', lower_neck_total_x_rotations + '.input3D[0].input3Dx', force=True)

    mc.connectAttr(upper_neck_total_x_rotations + '.output3Dx', splineIK + '.dTwistStartEnd.dTwistEnd', force=True)                
    mc.connectAttr(lower_neck_total_x_rotations + '.output3Dx', splineIK + '.dTwistStartEnd.dTwistStart') 


    #visibility
    for control_object in [ LOW_neck_control.C, MID_neck_control.C, UPP_neck_control.C ]:
        control_shapes = mc.listRelatives( control_object, shapes=True, type='nurbsCurve' )
        for control_shape in control_shapes:
            if control_shape != None:
                mc.setAttr( control_shape + '.overrideEnabled', True)
                mc.connectAttr(neck_settings_control.C + '.secondaries_visibility_parameter', control_shape + '.visibility', force=True)                
    
    #################cleanup#######################
    mc.setAttr(name + "_neck_no_transform_GRP_01.visibility", 0)
    mc.setAttr(name + "_neck_extras_GRP_01.visibility", 0)
    mc.setAttr(name + '_neck_chicken_translate_loc_01.visibility', 0)

    ######################connect to rest of rig##############################
    #controls
    mc.parentConstraint(name + '_chest_cc_01', name + '_neck_base_cc_os_grp_01', maintainOffset=True)
    #extras
    #mc.parentConstraint(name + '_chest_cc_01', name + '_neck_splineIK_curve_01', maintainOffset=True)
    mc.parentConstraint(name + '_chest_cc_01', name + '_neck_base_tracker_loc_01', maintainOffset=True)
    

    #############TEMP##############
    

    
    
    print('done.')
    
    

    