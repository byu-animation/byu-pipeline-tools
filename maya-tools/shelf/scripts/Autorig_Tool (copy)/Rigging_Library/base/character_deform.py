"""
Module for saving and loading skin weights and other deformation information
"""

import maya.cmds as mc
import maya.mel as mel
import os
from Rigging_Library.utilities import naming
from Third_Party_Tools import bSkinSaver
from functools import partial
from ..utilities import transform





def close_window_button_press(deformations_GUI_window, character_name, maya_button_trash):
    print('closing_window')

    #set rig defaults, like soft stretchy
    mc.setAttr( character_name + '_LFT_arm_settings_cc_01.soft_parameter', 0.5 )
    mc.setAttr( character_name + '_RGT_arm_settings_cc_01.soft_parameter', 0.5 )
    mc.setAttr( character_name + '_LFT_leg_settings_cc_01.soft_parameter', 0.5 )
    mc.setAttr( character_name + '_RGT_leg_settings_cc_01.soft_parameter', 0.5 )

    # Grendel (short) scale
    mc.setAttr(character_name + '_secret_scale_os_grp_01.scaleX', 0.1)
    mc.setAttr(character_name + '_secret_scale_os_grp_01.scaleY', 0.1)
    mc.setAttr(character_name + '_secret_scale_os_grp_01.scaleZ', 0.1)

    #close window
    mc.deleteUI ( deformations_GUI_window, window=True )

    print('DONE')



def make_deformer_GUI(character_name, scene_scale, main_project_path, geometry_filepath, builder_scene_filepath, primary_targets_filepath, secondary_targets_filepath, skin_weights_directory, skin_weights_extension, geometry_list, controls_directory):

    """
    function to build GUI to assist in deformation setups
    """

    # check to see if the window exists
    if mc.windowPref("deformations_window",exists=True): mc.windowPref("deformations_window",remove=True)
    if mc.window("deformations_window",exists=True): mc.deleteUI("deformations_window",window=True)

    # create the window
    deformations_GUI_window = mc.window("deformations_window",title="Deformations",width=300,height=550,sizeable=True)

    # set overarching form layout
    form_layout = mc.formLayout(numberOfDivisions=100)

    # banner image
    image_path = mc.internalVar(userPrefDir=True) + 'icons/BYU_logo.jpg'
    BYU_icon = mc.image(w=300, h=136, image=image_path)

    # add button to save all control shape information
    save_controls_button = mc.button("save_controls_button", label = "Save Controls", width = 270,
                                          command = partial(save_controls, character_name, main_project_path, controls_directory ))

    # add button to reload all skin weight information
    load_controls_button = mc.button("load_controls_button", label = "Load Controls", width = 270,
                                          command = partial(load_controls, character_name, main_project_path, controls_directory ))

    # add button to save all skin weight information
    save_skin_weights_button = mc.button("save_skin_weights_button", label = "Save Skin Weights", width = 270,
                                          command = partial(save_skin_weights, character_name, main_project_path, skin_weights_directory, skin_weights_extension, geometry_list ))

    # add button to reload all skin weight information
    load_skin_weights_button = mc.button("load_skin_weights_button", label = "Load Skin Weights", width = 270,
                                          command = partial(load_skin_weights, character_name, main_project_path, skin_weights_directory, skin_weights_extension, geometry_list ))

    # add button to close window
    close_window_button = mc.button("close_window_button", label = "Done", width = 270,
                                          command = partial(close_window_button_press, deformations_GUI_window, character_name))


    mc.formLayout(form_layout,
                    edit=True,
                    attachForm =     [(BYU_icon, 'top', 5),
                                      (BYU_icon, 'left', 5),
                                      (BYU_icon, 'right', 5),
                                      (close_window_button, 'left', 5),
                                      (close_window_button, 'right', 5),
                                      (close_window_button, 'bottom', 5),
                                      (save_controls_button, 'left', 10),
                                      (save_controls_button, 'right', 10),
                                      (load_controls_button, 'left', 10),
                                      (load_controls_button, 'right', 10),                                      (save_skin_weights_button, 'left', 10),
                                      (save_skin_weights_button, 'right', 10),
                                      (load_skin_weights_button, 'left', 10),
                                      (load_skin_weights_button, 'right', 10)],
                    attachControl =  [(save_controls_button, 'top', 5, BYU_icon),
                                      (load_controls_button, 'top', 5, save_controls_button),
                                      (save_skin_weights_button, 'top', 5, load_controls_button),
                                      (load_skin_weights_button, 'top', 5, save_skin_weights_button),
                                      (close_window_button, 'top', 5, load_skin_weights_button)]
                 )



    mc.showWindow( deformations_GUI_window )







def skin( character_name, scene_scale, main_project_path, geometry_filepath, builder_scene_filepath, primary_targets_filepath, secondary_targets_filepath, skin_weights_directory, skin_weights_extension, controls_directory ):

    # determine which pieces of geometry need to be skinned
    geometry_list = mc.listRelatives(character_name + '_GEO_GRP_01', children=True, type='transform')

    # load previously existing weight files
    maya_button_trash = ''
    load_skin_weights( character_name, main_project_path, skin_weights_directory, geometry_list, skin_weights_extension, maya_button_trash )

    print(geometry_list)
    for object in geometry_list:
        # skin unskinned meshes with default smooth bind
        if mel.eval('findRelatedSkinCluster ' + object) == '':
            print('Initial skinning performed on: ' + str(object))

            if object == character_name + '_LFT_eye_GEO_01':
                mc.skinCluster( character_name + '_LFT_eye_BN_01', object, toSelectedBones=True)
            if object == character_name + '_RGT_eye_GEO_01':
                mc.skinCluster( character_name + '_RGT_eye_BN_01', object, toSelectedBones=True)
            if object == character_name + '_UPP_teeth_GEO_01':
                mc.skinCluster( character_name + '_UPP_teeth_BN_01', object, toSelectedBones=True)
            if object == character_name + '_LOW_teeth_GEO_01':
                mc.skinCluster( character_name + '_LOW_teeth_BN_01', object, toSelectedBones=True)
            if object == character_name + '_tongue_GEO_01':
                mc.skinCluster( character_name + '_head_BN_01', character_name + '_jaw_BN_01', character_name + '_tongue_root_BN_01', character_name + '_tongue_middle_BN_01', character_name + '_tongue_tip_BN_01', object, toSelectedBones=True)


            if object == character_name + '_body_GEO_01':
                mc.select('*BN_01', replace=True)
                mc.select('*eye_*', '*tongue*', '*teeth*', deselect=True)
                body_bones=mc.ls(selection=True)
                print(body_bones)

                mc.skinCluster( body_bones, object, bindMethod=1, toSelectedBones=True)

    # initialize deformer GUI
    make_deformer_GUI(character_name, scene_scale, main_project_path, geometry_filepath, builder_scene_filepath, primary_targets_filepath, secondary_targets_filepath, skin_weights_directory, skin_weights_extension, geometry_list, controls_directory)



def save_controls( character_name, main_project_path, controls_directory, maya_button_trash ):

    """
    save control shapes for character
    """
    print('Saving controls...')

    # create temporary duplicate_controls_group to contain all duplicated controls
    mc.duplicate(character_name + '_controls_GRP_01', name = character_name + '_temporary_duplicate_controls_GRP_01', renameChildren=True)
    mc.parent(character_name + '_temporary_duplicate_controls_GRP_01', world=True)

    # name controls file
    controls_file = os.path.join( main_project_path, str.lower(character_name), controls_directory, 'controls.mb')

    # save controls file
    mc.select(character_name + '_temporary_duplicate_controls_GRP_01', replace=True)
    mc.file( controls_file, force=True, exportSelected=True, type='mayaBinary' )

    # delete temporary duplicate_controls_group
    mc.delete(character_name + '_temporary_duplicate_controls_GRP_01')

    print('done.')


def load_controls( character_name, main_project_path, controls_directory, maya_button_trash ):

    """
    load control shapes for character
    """
    print('Loading controls...')

    # controls file
    controls_file = os.path.join( main_project_path, str.lower(character_name), controls_directory, 'controls.mb')
    # load controls file
    mc.file(controls_file, i=True, force=True)


    # replace all shapes in any control transform with the shapes from the newly loaded controls file's corresponding transforms
    duplicate_transforms=mc.listRelatives(character_name + '_temporary_duplicate_controls_GRP_01', allDescendents=True, type='transform')
    for duplicate_transform in duplicate_transforms:
        if "cc_0" in duplicate_transform:



            #transform.freeze_locked_transforms( duplicate_transform )



            source_transform=duplicate_transform
            destination_transform = naming.renumber(source_transform)
            print('source_transform: ' + source_transform)
            print('destination_transform: ' + destination_transform)

            new_shape_curves = mc.listRelatives(source_transform, children=True, type='nurbsCurve')
            old_shape_curves = mc.listRelatives(destination_transform, children=True, type='nurbsCurve')
            print('new_shape_curves:')
            print( new_shape_curves)
            print('old_shape_curves:')
            print( old_shape_curves)

            for new_shape_curve in new_shape_curves:
                mc.parent( new_shape_curve, destination_transform, absolute=True, shape=True)
                #will make new intermediate transform - fine, let it. It preserves object space if source and destination transforms don't align.
                new_inserted_transform = mc.listRelatives(new_shape_curve, parent=True)
                #make the intermediate align with world to allow for a relative shape parenting.
                mc.makeIdentity (new_inserted_transform, apply=True, translate=True, rotate=True, scale=True)
                #parent new shape under old transform
                mc.parent( new_shape_curve, destination_transform, relative=True, shape=True)
                #delete intermediate transform that is now empty
                mc.delete(new_inserted_transform)

            for old_shape_curve in old_shape_curves:
                mc.parent( old_shape_curve, removeObject=True, shape=True)


    mc.delete(character_name + '_temporary_duplicate_controls_GRP_01')

    # reconnect visibility connections to shape nodes
    for control_set in ['neck', 'belly', 'tail']:
        if mc.objExists('*' + control_set + '*'):
            for control_object in [ character_name + '_LOW_' + control_set + '_cc_01', character_name + '_MID_' + control_set + '_cc_01', character_name + '_UPP_' + control_set + '_cc_01' ]:
                control_shapes = mc.listRelatives( control_object, shapes=True, type='nurbsCurve' )
                if control_shapes != None:
                    for control_shape in control_shapes:
                        if control_shape != None:
                            mc.setAttr( control_shape + '.overrideEnabled', True)
                            if control_set == 'neck' or control_set == 'tail':
                                mc.connectAttr(character_name + '_' + control_set + '_settings_cc_01.secondaries_visibility_parameter', control_shape + '.visibility', force=True)
                            else:
                                mc.connectAttr(character_name + '_spine_settings_cc_01.secondaries_visibility_parameter', control_shape + '.visibility', force=True)




    print('done.')




def save_skin_weights( character_name, main_project_path, skin_weights_directory, skin_weights_extension, geometry_list, maya_button_trash ):

    """
    save skin weights for character geometry objects
    """
    print('Saving skin weights...')
    for object in geometry_list:

        # name weights file
        weight_file = os.path.join( main_project_path, str.lower(character_name), skin_weights_directory, object + skin_weights_extension)

        # save skin weights file
        mc.select( object )
        bSkinSaver.bSaveSkinValues( weight_file )

    print('done.')


def load_skin_weights( character_name, main_project_path, skin_weights_directory, skin_weights_extension, geometry_list, maya_button_trash ):

    """
    load skin weights for character geometry objects
    """
    print('Loading skin weights...')
    # weights folder
    weight_directory = os.path.join( main_project_path, str.lower(character_name), skin_weights_directory)
    weight_files = os.listdir( weight_directory )

    # load skin weights
    for weight_file in weight_files:

        extension_result = os.path.splitext( weight_file )

        # check extension format
        if not extension_result > 1:
            continue

        # check skin weight file
        if not extension_result[1] == skin_weights_extension:
            continue

        # check user specified geometry list
        if geometry_list and not extension_result[0] in geometry_list:
            continue

        # check if object exists
        if not mc.objExists( extension_result[0]):
            continue

        full_path_weight_file = os.path.join( weight_directory, weight_file )
        bSkinSaver.bLoadSkinValues( loadOnSelection=False, inputFile=full_path_weight_file )

    print('done.')
