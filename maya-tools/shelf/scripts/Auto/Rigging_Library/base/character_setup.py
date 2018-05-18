"""
Module for running a character rig's main setup
"""

import maya.cmds as mc
from . import control
from . import module
from . import character_deform
from . import proxy

from Rigging_Library.rig import spine
from Rigging_Library.rig import neck
from Rigging_Library.rig import leg
from Rigging_Library.rig import arm
from Rigging_Library.rig import head
from Rigging_Library.rig import tail




"""
FUNCTIONS
"""   
    

   
def build_rig( character_name, scene_scale, main_project_path, geometry_filepath, builder_scene_filepath, primary_targets_filepath, secondary_targets_filepath, skin_weights_directory, skin_weights_extension, controls_directory ):
    
    """
    use initialized data to build character rig
    """
    
    name=character_name
    
    # clear scene of objects
    mc.select(all=True)
    mc.delete() 
    
    # import geometry
    geometry_file = geometry_filepath % ( main_project_path, str.lower(character_name), str.lower(character_name) )
    mc.file( geometry_file , i=True )  
    
    # import builder scene from build_prep
    builder_file = builder_scene_filepath % ( main_project_path, str.lower(character_name), str.lower(character_name) )
    mc.file( builder_file , i=True )

    # make base of rig
    base_rig = module.Base( character_name=character_name, scale=1.0 )     
    
    # use builder scene's targets to build rig's skeleton
    mc.select(character_name + '_root_target_cc_01')  
    root_target = mc.ls(selection=True)[0]
    mc.select(character_name + '_lower_belly_secondary_target_cc_01') 
    lower_belly_target = mc.ls(selection=True)[0]
    mc.select(character_name + '_belly_target_cc_01') 
    middle_belly_target = mc.ls(selection=True)[0]
    mc.select(character_name + '_upper_belly_secondary_target_cc_01') 
    upper_belly_target = mc.ls(selection=True)[0]
    mc.select(character_name + '_lower_ribcage_target_cc_01') 
    lower_ribcage_target = mc.ls(selection=True)[0]
    
    spine.build( name=character_name,
                 root_target=root_target,
                 lower_belly_target=lower_belly_target,
                 middle_belly_target=middle_belly_target,
                 upper_belly_target=upper_belly_target,
                 lower_ribcage_target=lower_ribcage_target,
                 prefix = 'spine',
                 rig_scale = 1.0,
                 base_rig = None 
                 )
    
    mc.select(character_name + '_neck_base_target_cc_01')  
    neck_base_target = mc.ls(selection=True)[0]
    mc.select(character_name + '_lower_neck_secondary_target_cc_01') 
    lower_neck_target = mc.ls(selection=True)[0]
    mc.select(character_name + '_neck_MID_target_cc_01') 
    middle_neck_target = mc.ls(selection=True)[0]
    mc.select(character_name + '_upper_neck_secondary_target_cc_01') 
    upper_neck_target = mc.ls(selection=True)[0]
    mc.select(character_name + '_head_target_cc_01') 
    head_target = mc.ls(selection=True)[0]
    
    neck.build( name=character_name,           
                neck_base_target=neck_base_target,
                lower_neck_target=lower_neck_target,
                middle_neck_target=middle_neck_target,
                upper_neck_target=upper_neck_target,
                head_target=head_target,
                prefix = 'neck',
                rig_scale = 1.0,
                base_rig = None 
                )
    
    if mc.objExists('*tail_base_target_cc_01'):
        mc.select(character_name + '_tail_base_target_cc_01')  
        tail_base_target = mc.ls(selection=True)[0]
        mc.select(character_name + '_lower_tail_secondary_target_cc_01') 
        lower_tail_target = mc.ls(selection=True)[0]
        mc.select(character_name + '_tail_MID_target_cc_01') 
        middle_tail_target = mc.ls(selection=True)[0]
        mc.select(character_name + '_upper_tail_secondary_target_cc_01') 
        upper_tail_target = mc.ls(selection=True)[0]
        mc.select(character_name + '_tail_tip_target_cc_01') 
        tail_tip_target = mc.ls(selection=True)[0]
        
        tail.build( name=character_name,           
                    tail_base_target=tail_base_target,
                    lower_tail_target=lower_tail_target,
                    middle_tail_target=middle_tail_target,
                    upper_tail_target=upper_tail_target,
                    tail_tip_target=tail_tip_target,
                    prefix = 'tail',
                    rig_scale = 1.0,
                    base_rig = None 
                    )    
    
    
    head.build( name=character_name,           
                rig_scale = 1.0,
                base_rig = None 
                )    
    
    for side in ["_LFT" , "_RGT"]:  
        mc.select('*' + side + '*arm*')  
        arm_joint_targets = mc.ls(selection=True)
        mc.select(character_name + side + '_scapula_target_cc_01')        
        scapula_joint = mc.ls(selection=True)[0]
        mc.select(character_name + side + '_upper_arm_target_cc_01')  
        shoulder_joint = mc.ls(selection=True)[0]
        mc.select(character_name + side + '_lower_arm_target_cc_01') 
        elbow_joint = mc.ls(selection=True)[0]
        mc.select(character_name + side + '_hand_target_cc_01') 
        wrist_joint = mc.ls(selection=True)[0]
        arm.build(             
                 name=character_name,
                 scapula_joint=scapula_joint,
                 shoulder_joint=shoulder_joint,
                 elbow_joint=elbow_joint,
                 wrist_joint=wrist_joint,
                 side=side,
                 prefix = side + '_arm',
                 rig_scale = 1.0,
                 base_rig = None
                 )
        
        mc.select('*' + side + '*leg*')
        leg_joint_targets = mc.ls(selection=True)
        mc.select(character_name + side + '_upper_leg_target_cc_01')  
        hip_joint = mc.ls(selection=True)[0]
        mc.select(character_name + side + '_lower_leg_target_cc_01') 
        knee_joint = mc.ls(selection=True)[0]
        mc.select(character_name + side + '_foot_target_cc_01') 
        ankle_joint = mc.ls(selection=True)[0]
        leg.build( 
                name=character_name,
                hip_joint=hip_joint,
                knee_joint=knee_joint,
                ankle_joint=ankle_joint,
                side=side,
                prefix = side + '_leg',
                rig_scale = 1.0,
                base_rig = None
                 )
        
    
    # delete targets
    mc.delete("*target_cc_01")
    mc.delete("*stretchy_target*")
    
    # parent geo to appropriate group in base
    mc.parent( character_name + '_GEO_GRP_01', base_rig.geo_GRP )
    
    # scale entire rig to scene scale
    mc.scale(scene_scale,scene_scale,scene_scale, character_name + '_secret_scale_os_grp_01')

    # add proxy geometry and parent and scale constrain to appropriate joints
    proxy.build_proxy_rig(character_name, scene_scale, main_project_path, geometry_filepath, builder_scene_filepath, primary_targets_filepath, secondary_targets_filepath, skin_weights_directory, skin_weights_extension )
    
    # Camera settings
    mc.setAttr('perspShape.nearClipPlane', 0.001)
    
    # control setup
    #make_control_setup(character_name, base_rig, root_JNT, head_JNT)
    
    #final cleanup
    mc.setAttr(name + "_extras_GRP_01.visibility", 0)
    
    # deform setup
    character_deform.skin( character_name, scene_scale, main_project_path, geometry_filepath, builder_scene_filepath, primary_targets_filepath, secondary_targets_filepath, skin_weights_directory, skin_weights_extension, controls_directory )
    
    
    



    
    