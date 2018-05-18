"""
Module for setting up a proxy rig
"""


import maya.cmds as mc
import os
from Rigging_Library.utilities import naming



# add proxy geometry and parent and scale constrain to appropriate joints
def build_proxy_rig(character_name, scene_scale, main_project_path, geometry_filepath, builder_scene_filepath, primary_targets_filepath, secondary_targets_filepath, skin_weights_directory, skin_weights_extension):
    print('RAN_PROXY')
    
    # import cut up proxy file
    proxy_geometry_file = geometry_filepath % ( main_project_path, str.lower(character_name), str.lower(character_name) + '_proxy' )
    print('proxy_geometry_file: ' + proxy_geometry_file)
    
    mc.file( proxy_geometry_file , i=True )  
    # create nodes to determine "stretchiness" (x length) of every JNT
    mc.select('*JNT*')
    joints = mc.ls(selection=True, type='joint')



    # parent and scale constrain pieces to corresponding joints
    """ 'tongue' """
    if mc.objExists('*tail*') == True:
        centerline_proxy_pieces = ['head', 'jaw', 'hips', 'LOW_belly', 'MID_belly', 'UPP_belly', 'chest', 'neck_base', 'LOW_neck', 'MID_neck', 'UPP_neck', 'UPP_teeth', 'LOW_teeth', 'tail_base', 'UPP_tail', 'MID_tail', 'LOW_tail', 'tail_tip' ]
    else:
        centerline_proxy_pieces = ['head', 'jaw', 'hips', 'LOW_belly', 'MID_belly', 'UPP_belly', 'chest', 'neck_base', 'LOW_neck', 'MID_neck', 'UPP_neck', 'UPP_teeth', 'LOW_teeth' ]


    symmetrical_proxy_pieces = ['shoulder', 'upper_arm', 'lower_arm', 'upper_leg', 'lower_leg', 'ankle', 'foot_ball', 'eye',
                                'thumb_PRO', 'thumb_MED', 'thumb_DIS','thumb_DIS_2','thumb_DIS_3',
                                'index_metacarpal', 'index_finger_PRO', 'index_finger_MED', 'index_finger_DIS', 'index_finger_DIS_2', 'index_finger_DIS_3',
                                'middle_metacarpal', 'middle_finger_PRO', 'middle_finger_MED', 'middle_finger_DIS', 'middle_finger_DIS_2', 'middle_finger_DIS_3',
                                'ring_metacarpal', 'ring_finger_PRO', 'ring_finger_MED', 'ring_finger_DIS', 'ring_finger_DIS_2', 'ring_finger_DIS_3',
                                'pinky_metacarpal', 'pinky_finger_PRO', 'pinky_finger_MED', 'pinky_finger_DIS', 'pinky_finger_DIS_2', 'pinky_finger_DIS_3',
                                'second_pinky_metacarpal', 'second_pinky_finger_PRO', 'second_pinky_finger_MED', 'second_pinky_finger_DIS', 'second_pinky_finger_DIS_2', 'second_pinky_finger_DIS_3' 
                                ]

    #for piece in centerline_proxy_pieces:
    for piece in centerline_proxy_pieces:
        target_translate = mc.xform(character_name + '_' + piece + '_BN_01', query=True, translation=True, worldSpace=True)
        mc.move(target_translate[0], target_translate[1], target_translate[2], character_name + '_' + piece + '_PROXY_01.scalePivot', character_name + '_' + piece + '_PROXY_01.rotatePivot')
        mc.orientConstraint(character_name + '_' + piece + '_BN_01', character_name + '_' + piece + '_PROXY_01', maintainOffset=True)
        mc.pointConstraint(character_name + '_' + piece + '_BN_01', character_name + '_' + piece + '_PROXY_01', maintainOffset=False)
        print('PROXY: ' + character_name + '_' + piece + '_BN_01')
        
    # symmetrical pieces
    for piece in symmetrical_proxy_pieces:
        for side in ['_LFT_', '_RGT_']:
            if(mc.objExists(character_name + side + piece + '_JNT_01')==True):
                mc.parentConstraint(character_name + side + piece + '_JNT_01', character_name + side + piece + '_PROXY_01', maintainOffset=True)
            if(mc.objExists(character_name + side + piece + '_BN_01')==True):
                mc.parentConstraint(character_name + side + piece + '_BN_01', character_name + side + piece + '_PROXY_01', maintainOffset=True)

    # parent all proxy geo to proxy GRP
    mc.parent(character_name + '_hips_PROXY_01', character_name + '_PROXY_GRP_01')
    
    return 
    
    
    
    
    

    