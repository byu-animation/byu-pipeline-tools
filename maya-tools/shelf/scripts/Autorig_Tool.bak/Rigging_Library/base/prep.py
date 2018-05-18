"""
Module for setting up rig prep file (positions of joints, etc.)
"""


import maya.cmds as mc
import os
from . import control
from . import character_setup
from Rigging_Library.utilities import naming
from functools import partial



# function to set up variables for use throughout the entire project
def set_project_variables(selected_project): 

    main_project_path = '/groups/grendel/production/assets/characters'
    geometry_filepath = '%s/%s/model/main/%s_model_main.mb' 
    builder_scene_filepath = '%s/%s/autorig/builder/%s_builder.mb' 
    primary_targets_filepath = '%s/%s/autorig/primary_targets/%s.mb' 
    secondary_targets_filepath = '%s/%s/autorig/secondary_targets/%s.mb' 
    skin_weights_directory = 'autorig/weights/skin_cluster'
    skin_weights_extension = '.swt'
    controls_directory = 'autorig/controls'


    if selected_project == 'Grendel':
        character_name='Grendel'
        scene_scale = 1.0
    elif selected_project == 'Beowulf':
        scene_scale = 1.0
        character_name='Beowulf'
    elif selected_project == 'Viking':
        scene_scale = 1.0
        character_name='Viking'
    else:
        print(selected_project + 'AUTORIG ERROR: Character specified does not have its prerequisite variables set in Rigging_Library.base.prep.set_project_variables')
    
    return character_name, scene_scale, main_project_path, geometry_filepath, builder_scene_filepath, primary_targets_filepath, secondary_targets_filepath, skin_weights_directory, skin_weights_extension, controls_directory


def initialize_rig( character_name ):
    
    """
    Start the rigging process, initialize the scene
    """

    # initialize variables
    character_name, scene_scale, main_project_path, geometry_filepath, builder_scene_filepath, primary_targets_filepath, secondary_targets_filepath, skin_weights_directory, skin_weights_extension, controls_directory = set_project_variables(character_name)
    
    # store camera position
    camera_translate = mc.xform('persp', query=True, translation=True)
    camera_rotate = mc.xform('persp', query=True, rotation=True)

    # new scene
    mc.file( new=True, force=True)
    
    # position camera
    mc.xform('persp', translation=camera_translate, rotation=camera_rotate)
    mc.camera('persp', edit=True, worldCenterOfInterest=[0.0,0.0,0.0], nearClipPlane=0.0001)
    mc.setAttr('persp.rotateZ', 0.0)
    
    # import geometry
    geometry_file = geometry_filepath % ( main_project_path, str.lower(character_name), str.lower(character_name) )
    print('geometry_file: ' + geometry_file)
    mc.file( geometry_file , i=True )
    mc.setAttr( character_name + '_GEO_GRP_01.ove', True)
    mc.setAttr( character_name + '_GEO_GRP_01.ovdt', 1)
    
    # open GUI for user input and to build rig initialize scene 
    make_GUI(character_name, scene_scale, main_project_path, geometry_filepath, builder_scene_filepath, primary_targets_filepath, secondary_targets_filepath, skin_weights_directory, skin_weights_extension)
    


# function to populate projects option menu
def populate_projects(main_project_path):

    #list the contents of the directory
    projects= os.listdir(main_project_path)
    for project in projects:
        print("projects: " + project)
    #add each folder in the projects directory into option menu
    for project in projects :
        mc.menuItem(label=project, parent="project_options_menu")
  
        
# function to call next two functions to initially populate primaries and secondaries textScrollList 
# and provide basic character-dependent variables and import geometry
def change_project(main_project_path, maya_button_trash):
    get_primary_files(main_project_path)
    get_secondary_files(main_project_path)
    
    #change default file save names
    selected_project = str.capitalize(str(mc.optionMenu("project_options_menu", query=True, value=True)))
    mc.textField( "save_primary_targets_filename", edit=True, text=selected_project + '_primaries_01')
    mc.textField( "save_secondary_targets_filename", edit=True, text=selected_project + '_secondaries_01')

    #call function to set basic, character-specific variables
    name, scene_scale, main_project_path, geometry_filepath, builder_scene_filepath, primary_targets_filepath, secondary_targets_filepath, skin_weights_directory, skin_weights_extension, controls_directory = set_project_variables(selected_project)
    
    # clear scene of objects
    mc.select(all=True)
    mc.delete()
    
    # import geometry
    geometry_file = geometry_filepath % ( main_project_path, str.lower(name), str.lower(name) )
    print('geometry_file: ' + geometry_file)
    mc.file( geometry_file , i=True )
    mc.setAttr( name + '_GEO_GRP_01.ove', True)
    mc.setAttr( name + '_GEO_GRP_01.ovdt', 1)


# function to populate primaries textScrollList
def get_primary_files(main_project_path):

    #clean up textScrollList
    menu_items = mc.textScrollList("primary_file_options_menu", edit=True, removeAll = True)

    #query the project selected in option Menu
    print(mc.optionMenu("project_options_menu", query=True, value=True))
    selected_project = str.capitalize(str(mc.optionMenu("project_options_menu", query=True, value=True)))

    #concatenate path to current project scenes folder
    project= str(main_project_path + '/' + str.lower(selected_project) + "/autorig/primary_targets/")
    print(project)
    #list all files in scene directory
    scenefiles = os.listdir(project)

    #append each file to textScrollList if ends with ".mb"
    for file in scenefiles:
        if file.rpartition(".")[2]=="mb" or file.rpartition(".")[2]=="ma":
            mc.textScrollList("primary_file_options_menu", edit=True, append=file )


# function to populate secondaries textScrollList
def get_secondary_files(main_project_path):

    #clean up textScrollList
    menu_items = mc.textScrollList("secondary_file_options_menu", edit=True, removeAll = True)

    #query the project selected in option Menu
    selected_project = str.capitalize(str(mc.optionMenu("project_options_menu", query=True, value=True)))

    #concatenate path to current project scenes folder
    project= str(main_project_path + '/' + str.lower(selected_project) + "/autorig/secondary_targets/")

    #list all files in scene directory
    scenefiles = os.listdir(project)

    #append each file to textScrollList if ends with ".mb"
    for file in scenefiles:
        if file.rpartition(".")[2]=="mb" or file.rpartition(".")[2]=="ma":
            mc.textScrollList("secondary_file_options_menu", edit=True, append=file )


# function to actually open double-clicked primaries files on the list
def primary_load(GUI_window, character_name, primary_targets_filepath, main_project_path):

    #query selected project
    selected_project = str.capitalize(str(mc.optionMenu("project_options_menu", query=True, value=True)))

    #concatenate path to scenes directory
    project= str(main_project_path + '/' + str.lower(selected_project) + "/autorig/primary_targets/")

    #query selected file
    selected_file= mc.textScrollList("primary_file_options_menu", query=True, selectItem= True)[0]

    #concatenate path to file 
    file_to_load= str(project + '/' + selected_file)

    # delete existing targets
    if mc.objExists('*joint_targets_GRP*'):
        mc.delete('*joint_targets_GRP*')
    
    #read file 
    print(file_to_load)
    mc.file(file_to_load, i=True, force=True)

    #deselect file and remove from list
    mc.textScrollList("primary_file_options_menu", edit=True, deselectAll=True)
    
    
# function to actually open double-clicked secondaries files on the list
def secondary_load(GUI_window, character_name, secondary_targets_filepath, main_project_path):

    #query selected project
    selected_project = str.capitalize(str(mc.optionMenu("project_options_menu", query=True, value=True)))

    #concatenate path to scenes directory
    project= str(main_project_path + '/' + str.lower(selected_project) + "/autorig/secondary_targets/")

    #query selected file
    selected_file= mc.textScrollList("secondary_file_options_menu", query=True, selectItem= True)[0]

    #concatenate path to file 
    file_to_load= str(project  + '/' + selected_file)

    # delete existing secondary targets
    if mc.objExists('*joint_targets_GRP*'):
        mc.delete('*joint_targets_GRP*')

    #read file 
    mc.file(file_to_load, i=True, force=True)

    #deselect file and remove from list
    mc.textScrollList("secondary_file_options_menu", edit=True, deselectAll=True)


def initialize_primary_rig_targets_button_press(GUI_window, builder_scene_filepath, main_project_path, scene_scale, maya_button_trash):
    print('initializing_primary_rig_targets...')
    which_pass = 'primary'
    initialize_builder_scene(which_pass)
    print('done')
   
   
def mirror_primary_rig_targets_button_press(GUI_window, builder_scene_filepath, main_project_path, scene_scale, maya_button_trash):
    print('mirroring_primary_rig_targets...')
    mirror_positive_X_direction = mc.checkBox( 'primary_mirror_direction', query = True, value=True )
    character_name = str.capitalize(str(mc.optionMenu("project_options_menu", query=True, value=True)))

    mirrored_side = '_RGT'
    
    # set side variables
    if (mirror_positive_X_direction==False):
        mirrored_side='_RGT'
        side_to_mirror='_LFT'
    else:
        mirrored_side='_LFT'
        side_to_mirror='_RGT'

    #eyes
    proper_xform=mc.xform(character_name + side_to_mirror + '_eye_target_cc_01', query=True, translation=True, relative=True)
    mc.setAttr(character_name + mirrored_side + '_eye_target_cc_01.translateX', proper_xform[0] * -1.0 )
    mc.setAttr(character_name + mirrored_side + '_eye_target_cc_01.translateY', proper_xform[1] )
    mc.setAttr(character_name + mirrored_side + '_eye_target_cc_01.translateZ', proper_xform[2] )

    # arm
    # delete old right arm
    mc.delete(character_name + mirrored_side + '_scapula_target_cc_os_grp_01')
    
    # remove prefix for renaming of duplicated scapula
    name_minus_character_and_side=naming.remove_prefix(naming.remove_prefix(character_name + side_to_mirror + '_scapula_target_cc_os_grp_01'))
    
    #duplicate scapula
    mc.duplicate(character_name + side_to_mirror + '_scapula_target_cc_os_grp_01', name=character_name + mirrored_side + '_scapula_target_cc_os_grp_01', renameChildren=True)
    
    # rename all children of duplicated scapula
    objects_to_rename = mc.listRelatives(character_name + mirrored_side + '_scapula_target_cc_os_grp_01', allDescendents=True)
    for object in objects_to_rename:
        name_minus_character_and_side=naming.renumber(naming.remove_prefix(naming.remove_prefix(object)))
        mc.rename(object, character_name + mirrored_side + '_' + name_minus_character_and_side)

    # flip over X axis
    temp_group = mc.group(name='temp_flip_GRP_01', world=True, empty=True)
    mc.parent(character_name + mirrored_side + '_scapula_target_cc_os_grp_01', 'temp_flip_GRP_01')
    mc.scale(-1,1,1, 'temp_flip_GRP_01')
    #mc.makeIdentity ('temp_flip_GRP_01', apply=True, translate=False, rotate=False, scale=True)
    mc.parent(character_name + mirrored_side + '_scapula_target_cc_os_grp_01', character_name + '_lower_ribcage_target_cc_01')
    
    # delete temp flip group
    mc.delete(temp_group)
    
    
    # leg
    # delete old right leg
    mc.delete(character_name + mirrored_side + '_upper_leg_target_cc_os_grp_01')
    
    # remove prefix for renaming of duplicated upper_leg
    name_minus_character_and_side=naming.remove_prefix(naming.remove_prefix(character_name + side_to_mirror + '_upper_leg_target_cc_os_grp_01'))
    
    #duplicate upper_leg
    mc.duplicate(character_name + side_to_mirror + '_upper_leg_target_cc_os_grp_01', name=character_name + mirrored_side + '_upper_leg_target_cc_os_grp_01', renameChildren=True)
    
    # rename all children of duplicated upper_leg
    objects_to_rename = mc.listRelatives(character_name + mirrored_side + '_upper_leg_target_cc_os_grp_01', allDescendents=True)
    for object in objects_to_rename:
        name_minus_character_and_side=naming.renumber(naming.remove_prefix(naming.remove_prefix(object)))
        mc.rename(object, character_name + mirrored_side + '_' + name_minus_character_and_side)

    # flip over X axis
    temp_group = mc.group(name='temp_flip_GRP_01', world=True, empty=True)
    mc.parent(character_name + mirrored_side + '_upper_leg_target_cc_os_grp_01', 'temp_flip_GRP_01')
    mc.scale(-1,1,1, 'temp_flip_GRP_01')
    #mc.makeIdentity ('temp_flip_GRP_01', apply=True, translate=False, rotate=False, scale=True)
    mc.parent(character_name + mirrored_side + '_upper_leg_target_cc_os_grp_01', character_name + '_root_target_cc_01')

    # delete temp flip group
    mc.delete(temp_group)
    
    print('done')
   
   
def initialize_secondary_rig_targets_button_press(GUI_window, builder_scene_filepath, main_project_path, scene_scale, maya_button_trash):
    print('initializing_secondary_rig_targets...')
    which_pass = 'secondary'
    initialize_builder_scene(which_pass)
    print('done')
    
    
def mirror_secondary_rig_targets_button_press(GUI_window, builder_scene_filepath, main_project_path, maya_button_trash):
    print('mirroring_secondary_rig_targets...')
    print('done')


def save_primary_rig_targets_button_press(GUI_window, character_name, primary_targets_filepath, main_project_path, maya_button_trash):
    print('saving_primary_rig_targets...')
    
    #query the project selected in option Menu
    selected_project = str.capitalize(str(mc.optionMenu("project_options_menu", query=True, value=True)))
    
    # select primary joint targets and export them exclusively
    file_name = mc.textField( "save_primary_targets_filename", query = True, text=True )
    primary_targets_file = primary_targets_filepath % ( main_project_path, str.lower(selected_project), file_name )
    mc.select( ['*joint_targets_GRP*'] )
    mc.file( primary_targets_file, force=True, exportSelected=True, type='mayaBinary' )
    get_primary_files(main_project_path)
    
    print('done')


def save_secondary_rig_targets_button_press(GUI_window, character_name, secondary_targets_filepath, main_project_path, maya_button_trash):
    print('saving_secondary_rig_targets...')
    
    #query the project selected in option Menu
    selected_project = str.capitalize(str(mc.optionMenu("project_options_menu", query=True, value=True)))

    # select secondary joint targets and export them exclusively
    file_name = mc.textField( "save_secondary_targets_filename", query = True, text=True )
    secondary_targets_file = secondary_targets_filepath % ( main_project_path, str.lower(selected_project), file_name )
    mc.select( ['*joint_targets_GRP*'] )
    mc.file( secondary_targets_file, force=True, exportSelected=True, type='mayaBinary' )
    get_secondary_files(main_project_path)
    
    print('done')


def build_rig_button_press(GUI_window, builder_scene_filepath, main_project_path, character_name, maya_button_trash):
    print('building_rig...')

    #import variables
    selected_project=str.capitalize(str(mc.optionMenu("project_options_menu", query=True, value=True)))
    character_name, scene_scale, main_project_path, geometry_filepath, builder_scene_filepath, primary_targets_filepath, secondary_targets_filepath, skin_weights_directory, skin_weights_extension, controls_directory = set_project_variables(selected_project) 
    
    # select joint targets and export them exclusively
    builder_file = builder_scene_filepath % ( main_project_path, str.lower(character_name), str.lower(character_name) )

    # re-unlock channels 
    mc.select('*finger*', '*thumb*', replace=True)
    selected_objects = mc.ls(selection=True, transforms=True)
    for object in selected_objects:
        mc.setAttr(str(object) + '.scale', lock=False)
        mc.setAttr(str(object) + '.translate', lock=False)
        mc.setAttr(str(object) + '.rotateY', lock=False)
        mc.setAttr(str(object) + '.rotateZ', lock=False)

    # scale back to 1.0 for build iteration
    #mc.scale(1.0,1.0,1.0, 'joint_targets_GRP_01') 
    mc.select( ['*_cc_01'] )
    control_target_objects = mc.ls( selection=True )
    for control_target_object in control_target_objects:
        mc.setAttr(str(control_target_object) + '.translateY', lock=False)
        mc.setAttr(str(control_target_object) + '.translateZ', lock=False)
        mc.parent(control_target_object, world=True)

    # delete children
    for control_target_object in control_target_objects:
        children=mc.listRelatives(control_target_objects, children=True, shapes=False, type="transform")
        if(children != None):
            mc.delete(mc.listRelatives(control_target_objects, children=True, shapes=False, type="transform"))
    mc.select( '*_cc_01', replace=True)
    mc.file(rename=builder_file)
    ############################## line below throwing warning about sets
    mc.file( force=True, exportSelected=True, type='mayaBinary' )

    # call the build function
    character_setup.build_rig( character_name, scene_scale, main_project_path, geometry_filepath, builder_scene_filepath, primary_targets_filepath, secondary_targets_filepath, skin_weights_directory, skin_weights_extension, controls_directory )
    
    # delete prep GUI
    mc.deleteUI ( GUI_window, window=True ) 
    
   
    
    
    
    
    print('done')


def initialize_builder_scene(which_pass):
    
    """
    function to store user input from the GUI and use it to initialize the rig scene
    """
    
    # ********************** gather all UI user input *************************************************************************************************
    
    selected_project = str.capitalize(str(mc.optionMenu("project_options_menu", query=True, value=True)))
    character_name, scale, main_project_path, geometry_filepath, builder_scene_filepath, primary_targets_filepath, secondary_targets_filepath, skin_weights_directory, skin_weights_extension, controls_directory = set_project_variables(selected_project)
    number_of_fingers = mc.intField( "number_of_fingers", query = True, value=True )
    number_of_joints_per_finger = mc.intField( "number_of_joints_per_finger", query = True , value=True )
    number_of_toes = mc.intField( "number_of_toes", query = True , value=True )
    number_of_joints_per_toe = mc.intField( "number_of_joints_per_toe", query = True, value=True  )
    number_of_spine_joints = mc.intField('number_of_spine_spans', query = True, value=True)
    number_of_neck_joints = mc.intField( "number_of_neck_spans", query = True, value=True )
    number_of_upper_arm_joints = mc.intField( "number_of_upper_arm_spans", query = True, value=True )
    number_of_lower_arm_joints = mc.intField( "number_of_lower_arm_spans", query = True, value=True )
    number_of_upper_leg_joints = mc.intField( "number_of_upper_leg_spans", query = True, value=True )
    number_of_lower_leg_joints = mc.intField( "number_of_lower_leg_spans", query = True, value=True )
    has_tail = mc.checkBox( 'has_tail', query = True, value=True )
    number_of_upper_tail_joints = mc.intField( "number_of_upper_tail_spans", query = True, value=True )
    number_of_lower_tail_joints = mc.intField( "number_of_lower_tail_spans", query = True, value=True )
    
    # ****************** populate new scene with targets for joint placement *************************************************************************

    
    
    if which_pass == 'primary':
    
        # delete existing targets
        if mc.objExists("*target_cc_01"):
            mc.delete("*target_cc_01")
            mc.delete('*joint_targets_GRP*')
        
        # MAIN TARGETS (centerline)
        root_target = control.Control(
                                      prefix = character_name + '_root_target',
                                      scale = .01,
                                      use_numerical_transforms = True,
                                      transform_x = 0.0,
                                      transform_y = .360,
                                      transform_z = 0.0,
                                      shape = 'spherical_target',
                                      locked_channels = ['visibility']
                                      )
        
        belly_target = control.Control(
                                      prefix = character_name + '_belly_target',
                                      scale = .01,
                                      use_numerical_transforms = True,
                                      transform_x = 0.0,
                                      transform_y = .09,
                                      transform_z = 0.0,
                                      parent = root_target.C,
                                      shape = 'spherical_target',
                                      locked_channels = ['visibility']
                                      )
        if has_tail:
            tail_base_target = control.Control(
                                          prefix = character_name + '_tail_base_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = 0.0,
                                          transform_y = 0.0,
                                          transform_z = -.02,
                                          parent = root_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          )
            
            tail_MID_target = control.Control(
                                          prefix = character_name + '_tail_MID_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = 0.0,
                                          transform_y = 0.0,
                                          transform_z = -.10,
                                          parent = tail_base_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          )
    
            tail_tip_target = control.Control(
                                          prefix = character_name + '_tail_tip_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = 0.0,
                                          transform_y = 0.0,
                                          transform_z = -.10,
                                          parent = tail_MID_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          )
        
        lower_ribcage_target = control.Control(
                                      prefix = character_name + '_lower_ribcage_target',
                                      scale = .01,
                                      use_numerical_transforms = True,
                                      transform_x = 0.0,
                                      transform_y = .09,
                                      transform_z = 0.0,
                                      parent = belly_target.C,
                                      shape = 'spherical_target',
                                      locked_channels = ['visibility']
                                      )
        
        neck_base_target = control.Control(
                                      prefix = character_name + '_neck_base_target',
                                      scale = .01,
                                      use_numerical_transforms = True,
                                      transform_x = 0.0,
                                      transform_y = .008,
                                      transform_z = 0.0,
                                      parent = lower_ribcage_target.C,
                                      shape = 'spherical_target',
                                      locked_channels = ['visibility']
                                      )
        
        neck_MID_target = control.Control(
                                      prefix = character_name + '_neck_MID_target',
                                      scale = .01,
                                      use_numerical_transforms = True,
                                      transform_x = 0.0,
                                      transform_y = .05,
                                      transform_z = 0.0,
                                      parent = neck_base_target.C,
                                      shape = 'spherical_target',
                                      locked_channels = ['visibility']
                                      )    
        
        head_target = control.Control(
                                      prefix = character_name + '_head_target',
                                      scale = .01,
                                      use_numerical_transforms = True,
                                      transform_x = 0.0,
                                      transform_y = .050,
                                      transform_z = 0.0,
                                      parent = neck_MID_target.C,
                                      shape = 'spherical_target',
                                      locked_channels = ['visibility']
                                      )  
        
        jaw_target = control.Control(
                                      prefix = character_name + '_jaw_target',
                                      scale = .01,
                                      use_numerical_transforms = True,
                                      transform_x = 0.0,
                                      transform_y = -.02,
                                      transform_z = .02,
                                      parent = head_target.C,
                                      shape = 'spherical_target',
                                      locked_channels = ['visibility']
                                      )  
        
        UPP_teeth_target = control.Control(
                                      prefix = character_name + '_UPP_teeth_target',
                                      scale = .01,
                                      use_numerical_transforms = True,
                                      transform_x = 0.0,
                                      transform_y = .01,
                                      transform_z = .08,
                                      parent = head_target.C,
                                      shape = 'spherical_target',
                                      locked_channels = ['visibility']
                                      )  
                
        LOW_teeth_target = control.Control(
                                      prefix = character_name + '_LOW_teeth_target',
                                      scale = .01,
                                      use_numerical_transforms = True,
                                      transform_x = 0.0,
                                      transform_y = -.01,
                                      transform_z = .060,
                                      parent = jaw_target.C,
                                      shape = 'spherical_target',
                                      locked_channels = ['visibility']
                                      )  
                        
                        
        tongue_root_target = control.Control(
                                      prefix = character_name + '_tongue_root_target',
                                      scale = .01,
                                      use_numerical_transforms = True,
                                      transform_x = 0.0,
                                      transform_y = 0.0,
                                      transform_z = .04,
                                      parent = jaw_target.C,
                                      shape = 'spherical_target',
                                      locked_channels = ['visibility']
                                      )  
                                
                                
        tongue_middle_target = control.Control(
                                      prefix = character_name + '_tongue_middle_target',
                                      scale = .01,
                                      use_numerical_transforms = True,
                                      transform_x = 0.0,
                                      transform_y = 0.0,
                                      transform_z = .02,
                                      parent = tongue_root_target.C,
                                      shape = 'spherical_target',
                                      locked_channels = ['visibility']
                                      )  
                                        
                                        
        tongue_tip_target = control.Control(
                                      prefix = character_name + '_tongue_tip_target',
                                      scale = .01,
                                      use_numerical_transforms = True,
                                      transform_x = 0.0,
                                      transform_y = 0.0,
                                      transform_z = .02,
                                      parent = tongue_middle_target.C,
                                      shape = 'spherical_target',
                                      locked_channels = ['visibility']
                                      )  
                                                                         
                                     
                                                

        
        # MAIN TARGETS (mirrored)
        for side in ["_LFT" , "_RGT"]:
            if side=="_RGT":
                x_scale = -1.0
            else:
                x_scale = 1.0
                
            eye_target = control.Control(
                                          prefix = character_name + side + '_eye_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = .02 * x_scale,
                                          transform_y = .02,
                                          transform_z = .02,
                                          parent = head_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          )               
            
            eyebrow_INN_target = control.Control(
                                          prefix = character_name + side + '_INN_eyebrow_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = .015 * x_scale,
                                          transform_y = .04,
                                          transform_z = .04,
                                          parent = head_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          )                
            
            eyebrow_MID_target = control.Control(
                                          prefix = character_name + side + '_MID_eyebrow_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = .02 * x_scale,
                                          transform_y = .04,
                                          transform_z = .04,
                                          parent = head_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          )     
            
            eyebrow_OUT_target = control.Control(
                                          prefix = character_name + side + '_OUT_eyebrow_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = .025 * x_scale,
                                          transform_y = .04,
                                          transform_z = .04,
                                          parent = head_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          )                 
                                        
            scapula_target = control.Control(
                                          prefix = character_name + side + '_scapula_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = .04 * x_scale,
                                          transform_y = .03,
                                          transform_z = 0.0,
                                          parent = lower_ribcage_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          ) 
            
            upper_arm_target = control.Control(
                                          prefix = character_name + side + '_upper_arm_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = .04 * x_scale,
                                          transform_y = .03,
                                          transform_z = 0.0,
                                          parent = scapula_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          )       
            
            lower_arm_target = control.Control(
                                          prefix = character_name + side + '_lower_arm_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = .13 * x_scale,
                                          transform_y = 0.0,
                                          transform_z = -.02,
                                          parent = upper_arm_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          ) 
            
            hand_target = control.Control(
                                          prefix = character_name + side + '_hand_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = .13 * x_scale,
                                          transform_y = 0.0,
                                          transform_z = .02,
                                          parent = lower_arm_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          ) 
                   
            upper_leg_target = control.Control(
                                          prefix = character_name + side + '_upper_leg_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = .060 * x_scale,
                                          transform_y = 0.0,
                                          transform_z = 0.0,
                                          parent = root_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          ) 
            
            lower_leg_target = control.Control(
                                          prefix = character_name + side + '_lower_leg_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = 0.0 * x_scale,
                                          transform_y = -.18,
                                          transform_z = .02,
                                          parent = upper_leg_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          )     
            
            foot_target = control.Control(
                                          prefix = character_name + side + '_foot_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = 0.0 * x_scale,
                                          transform_y = -.14,
                                          transform_z = -.02,
                                          parent = lower_leg_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          ) 
            
            foot_ball_target = control.Control(
                                          prefix = character_name + side + '_foot_ball_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = 0.0 * x_scale,
                                          transform_y = -.02,
                                          transform_z = .03,
                                          parent = foot_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          ) 
            mc.setAttr(foot_ball_target.Off + '.rotateY', -90.0)
            
            foot_tip_target = control.Control(
                                          prefix = character_name + side + '_foot_tip_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = .03,
                                          transform_y = 0.0,
                                          transform_z = 0.0,
                                          parent = foot_ball_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          ) 
            
            foot_heel_target = control.Control(
                                          prefix = character_name + side + '_foot_heel_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = 0.0 * x_scale,
                                          transform_y = -.02,
                                          transform_z = -.01,
                                          parent = foot_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          ) 
            
            foot_inner_target = control.Control(
                                          prefix = character_name + side + '_foot_inner_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = 0.0,
                                          transform_y = 0.0,
                                          transform_z = -.02 * x_scale,
                                          parent = foot_ball_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          ) 
                        
            foot_outer_target = control.Control(
                                          prefix = character_name + side + '_foot_outer_target',
                                          scale = .01,
                                          use_numerical_transforms = True,
                                          transform_x = 0.0,
                                          transform_y = 0.0,
                                          transform_z = .02 * x_scale,
                                          parent = foot_ball_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          ) 
            
            #initialize second joint name for thumb
            if number_of_joints_per_finger == 1:
                second_thumb_joint_name = 'END'
            elif number_of_joints_per_finger == 2:
                second_thumb_joint_name = 'DIS'
            else:
                second_thumb_joint_name = 'MED'
            
            # initialize list for names of thumb joints
            if number_of_joints_per_finger == 1:
                thumb_phalanges = []
            elif number_of_joints_per_finger == 2:
                thumb_phalanges = ['END']
            elif number_of_joints_per_finger == 3:
                thumb_phalanges = ['DIS', 'END']  
            elif number_of_joints_per_finger == 4:
                thumb_phalanges = ['DIS', 'DIS_2', 'END']   
            elif number_of_joints_per_finger == 5:
                thumb_phalanges = ['DIS', 'DIS_2', 'DIS_3', 'END']
    
            thumb_PRO_target = control.Control(
                                          prefix = character_name + side + '_thumb_PRO_target',
                                          scale = 0.006,
                                          use_numerical_transforms = True,
                                          transform_x = 0.0 * x_scale,
                                          transform_y = -0.003,
                                          transform_z = .012,
                                          parent = hand_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          )
                    
            thumb_second_target = control.Control(
                                          prefix = character_name + side + '_thumb_' + second_thumb_joint_name + '_target',
                                          scale = 0.006,
                                          use_numerical_transforms = True,
                                          transform_x = .020 * x_scale,
                                          transform_y = -0.006,
                                          transform_z = .024,
                                          parent = hand_target.C,
                                          shape = 'spherical_target',
                                          locked_channels = ['visibility']
                                          )   
            # point PRO target at second target
            mc.aimConstraint(thumb_second_target.C, thumb_PRO_target.C, maintainOffset=False, worldUpType='scene')
            
            # make other thumb targets
            last_phalange=second_thumb_joint_name
            for phalange in thumb_phalanges:
                thumb_target = control.Control(
                              prefix = character_name + side + '_thumb_' + phalange + '_target',
                              scale = 0.006,
                              use_numerical_transforms = True,
                              transform_x = .010 * x_scale * (thumb_phalanges.index(phalange)+3),
                              transform_y = -0.006,
                              transform_z = .024,
                              parent = hand_target.C,
                              shape = 'spherical_target',
                              locked_channels = ['visibility']
                              )   
                mc.aimConstraint(thumb_target.C, character_name + side + '_thumb_' + last_phalange + '_target_cc_01', maintainOffset=False, worldUpType='scene')
                last_phalange = phalange


  
  
    
            # initialize list for names of finger joints
            if number_of_joints_per_finger == 1:
                finger_phalanges = ['PRO', 'END']
            elif number_of_joints_per_finger == 2:
                finger_phalanges = ['PRO', 'DIS', 'END']
            elif number_of_joints_per_finger == 3:
                finger_phalanges = ['PRO', 'MED', 'DIS', 'END']  
            elif number_of_joints_per_finger == 4:
                finger_phalanges = ['PRO', 'MED', 'DIS', 'DIS_2', 'END']   
            elif number_of_joints_per_finger == 5:
                finger_phalanges = ['PRO', 'MED', 'DIS', 'DIS_2', 'DIS_3', 'END']
            
            # initialize list for names of fingers
            if number_of_fingers == 1:
                fingers = ['index']
            elif number_of_fingers == 2:
                fingers = ['index', 'pinky']
            elif number_of_fingers == 3:
                fingers = ['index', 'middle', 'pinky']  
            elif number_of_fingers == 4:
                fingers = ['index', 'middle', 'ring', 'pinky']   
            elif number_of_fingers == 5:
                fingers = ['index', 'middle', 'ring', 'pinky', 'second_pinky']
            
            # make finger targets
            for finger in fingers:
                # make metacarpals
                metacarpal_target = control.Control(
                                                  prefix = character_name + side + '_' + finger + '_finger_metacarpal_target',
                                                  scale = 0.006,
                                                  use_numerical_transforms = True,
                                                  transform_x = (.010 * x_scale),
                                                  transform_y = 0.0,
                                                  transform_z = (.0125-((fingers.index(finger)*.015+.01)/2.0)),
                                                  parent = hand_target.C,
                                                  shape = 'spherical_target',
                                                  locked_channels = ['visibility']
                                                  )
                last_phalange='metacarpal'
                print('finger_phalanges: ' + str(finger_phalanges))
                for phalange in finger_phalanges:
                    finger_target = control.Control(
                                                  prefix = character_name + side + '_' + finger + '_finger_' + phalange + '_target',
                                                  scale = 0.006,
                                                  use_numerical_transforms = True,
                                                  transform_x = (1.0 * x_scale * (finger_phalanges.index(phalange)+1)/100)+.02*x_scale,
                                                  transform_y = 0.0,
                                                  transform_z = (.0125-((fingers.index(finger)*.015+.01)/2.0)),
                                                  parent = hand_target.C,
                                                  shape = 'spherical_target',
                                                  locked_channels = ['visibility']
                                                  )
                    mc.aimConstraint(finger_target.C, character_name + side + '_' + finger + '_finger_' + last_phalange + '_target_cc_01', maintainOffset=False, worldUpType='scene')
                    last_phalange = phalange                
    
            # initialize list for names of toe joints
            if number_of_joints_per_toe == 1:
                toe_phalanges = ['PRO', 'END']
            elif number_of_joints_per_toe == 2:
                toe_phalanges = ['PRO', 'DIS', 'END']
            elif number_of_joints_per_toe == 3:
                toe_phalanges = ['PRO', 'MED', 'DIS', 'END']  
            elif number_of_joints_per_toe == 4:
                toe_phalanges = ['PRO', 'MED', 'DIS', 'DIS_2', 'END']   
            elif number_of_joints_per_toe == 5:
                toe_phalanges = ['PRO', 'MED', 'DIS', 'DIS_2', 'DIS_3', 'END']
            
            # initialize list for names of toes
            if number_of_toes == 1:
                toes = ['big']
            elif number_of_toes == 2:
                toes = ['big', 'index']
            elif number_of_toes == 3:
                toes = ['big', 'index', 'middle']  
            elif number_of_toes == 4:
                toes = ['big', 'index', 'middle', 'fourth']   
            elif number_of_toes == 5:
                toes = ['big', 'index', 'middle', 'fourth', 'pinky']
            elif number_of_toes == 6:
                toes = ['big', 'index', 'middle', 'fourth', 'pinky', 'second_pinky']
            
            # make toe targets
            for toe in toes:
                for phalanx in toe_phalanges:
                    toe_target = control.Control(
                                              prefix = character_name + side + '_' + toe + '_toe_' + phalanx + '_target',
                                              scale = 0.006,
                                              use_numerical_transforms = True,
                                              transform_x = 0.005 * (toe_phalanges.index(phalanx)+1), 
                                              transform_y = 0.0,
                                              transform_z = (-.0125+((toes.index(toe)/100+.01)/2.0)),
                                              parent = foot_ball_target.C,
                                              shape = 'spherical_target',
                                              locked_channels = ['visibility']
                                              )
                #orient PRO targets
                mc.setAttr(character_name + side + '_' + toe + '_toe_PRO_target_cc_os_grp_01.rotateY', -90.0)
            
        # organize targets
        mc.select(clear=True)
        mc.group(name='joint_targets_GRP_01', empty=True)
        mc.parent(character_name + '_root_target_cc_os_grp_01', 'joint_targets_GRP_01')
        
        # scale to scene scale
        mc.scale(scale,scale,scale, 'joint_targets_GRP_01') 
    
    elif which_pass == 'secondary':
        
        # delete existing secondary targets
        if mc.objExists("*secondar*"):
            mc.delete("*secondar*")
        if mc.objExists("*measure*"):
            mc.delete('*measure*')
        

        
        def make_stretchy_joint_targets( side, part, character_name, number_of_joints, scale, parent, end_target ):
                
            # make measure transforms 
            start = mc.createNode('transform', name = character_name + side + "_" + part + '_measure_start', parent=parent)
            end = mc.createNode('transform', name = character_name + "_" + part + '_measure_end', parent=start)
            # constrain transforms to targets
            mc.pointConstraint(parent, start)
            mc.aimConstraint(end_target, start)
            mc.pointConstraint(end_target, end)
            # find length of neck
            tx = mc.getAttr(end + '.translateX')
            length = abs(tx)
            # make stretchy joint targets
            for stretchy_joint_number in range(2, number_of_joints):
                stretchy_target = control.Control(
                                          prefix = character_name + side + '_' + part + '_stretchy_target_' + str(stretchy_joint_number),
                                          scale = 0.004,
                                          use_numerical_transforms = True,
                                          transform_x = (stretchy_joint_number-1) * (float(length / (number_of_joints-1))),
                                          transform_y = 0.0,
                                          transform_z = 0.0,
                                          parent = start,
                                          shape = 'spherical_target',
                                          locked_channels = ['scale', 'rotate', 'translateY', 'translateZ', 'visibility']
                                          ) 
        
        
        # STRETCHY JOINT TARGETS (centerline)
    
        # make spine stretchy joint targets
        #make_stretchy_joint_targets('', 'spine', character_name, number_of_spine_joints, scale, character_name + "_character_name + '_root_target_cc_01'_cc_01", character_name + "_character_name + '_lower_ribcage_target_cc_01'_cc_01")
        upper_belly_secondary_target = control.Control(
                                                      prefix = character_name + '_upper_belly_secondary_target',
                                                      scale = 0.004,
                                                      use_numerical_transforms = True,
                                                      transform_x = 0.0,
                                                      transform_y = 0.0,
                                                      transform_z = 0.0,
                                                      parent = character_name + '_belly_target_cc_01',
                                                      shape = 'spherical_target',
                                                      locked_channels = ['visibility']
                                      ) 
        mc.delete(mc.parentConstraint(character_name + '_belly_target_cc_01', character_name + '_lower_ribcage_target_cc_01', upper_belly_secondary_target.Off, maintainOffset=False))
        lower_belly_secondary_target = control.Control(
                                                      prefix = character_name + '_lower_belly_secondary_target',
                                                      scale = 0.004,
                                                      use_numerical_transforms = True,
                                                      transform_x = 0.0,
                                                      transform_y = 0.0,
                                                      transform_z = 0.0,
                                                      parent = character_name + '_root_target_cc_01',
                                                      shape = 'spherical_target',
                                                      locked_channels = ['visibility']
                                                      ) 
        mc.delete(mc.parentConstraint(character_name + '_belly_target_cc_01', character_name + '_root_target_cc_01', lower_belly_secondary_target.Off, maintainOffset=False))
        
        # make neck stretchy joint targets
        #make_stretchy_joint_targets('', 'neck', character_name, number_of_neck_joints, scale, character_name + "_neck_base_target_cc_01", character_name + "_head_target_cc_01")
        upper_neck_secondary_target = control.Control(
                                                      prefix = character_name + '_upper_neck_secondary_target',
                                                      scale = 0.004,
                                                      use_numerical_transforms = True,
                                                      transform_x = 0.0,
                                                      transform_y = 0.0,
                                                      transform_z = 0.0,
                                                      parent = character_name + '_neck_MID_target_cc_01',
                                                      shape = 'spherical_target',
                                                      locked_channels = ['visibility']
                                      ) 
        mc.delete(mc.parentConstraint(character_name + '_neck_MID_target_cc_01', character_name + '_head_target_cc_01', upper_neck_secondary_target.Off, maintainOffset=False))
        lower_neck_secondary_target = control.Control(
                                                      prefix = character_name + '_lower_neck_secondary_target',
                                                      scale = 0.004,
                                                      use_numerical_transforms = True,
                                                      transform_x = 0.0,
                                                      transform_y = 0.0,
                                                      transform_z = 0.0,
                                                      parent = character_name + '_neck_base_target_cc_01',
                                                      shape = 'spherical_target',
                                                      locked_channels = ['visibility']
                                                      ) 
        mc.delete(mc.parentConstraint(character_name + '_neck_base_target_cc_01', character_name + '_neck_MID_target_cc_01', lower_neck_secondary_target.Off, maintainOffset=False))
                
        
        if has_tail:
            
            # make upper tail stretchy joint targets
            #make_stretchy_joint_targets('', 'upper_tail', character_name, number_of_upper_tail_joints, scale, character_name + "_tail_PRO_target_cc_01", character_name + "_tail_MED_target_cc_01")
            # make lower tail stretchy joint targets
            #make_stretchy_joint_targets('', 'lower_tail', character_name, number_of_lower_tail_joints, scale, character_name + "_tail_MED_target_cc_01", character_name + "_tail_DIS_target_cc_01")
            upper_tail_secondary_target = control.Control(
                                                          prefix = character_name + '_upper_tail_secondary_target',
                                                          scale = 0.004,
                                                          use_numerical_transforms = True,
                                                          transform_x = 0.0,
                                                          transform_y = 0.0,
                                                          transform_z = 0.0,
                                                          parent = character_name + '_tail_MID_target_cc_01',
                                                          shape = 'spherical_target',
                                                          locked_channels = ['visibility']
                                          ) 
            mc.delete(mc.parentConstraint(character_name + '_tail_MID_target_cc_01', character_name + '_tail_tip_target_cc_01', upper_tail_secondary_target.Off, maintainOffset=False))
            lower_tail_secondary_target = control.Control(
                                                          prefix = character_name + '_lower_tail_secondary_target',
                                                          scale = 0.004,
                                                          use_numerical_transforms = True,
                                                          transform_x = 0.0,
                                                          transform_y = 0.0,
                                                          transform_z = 0.0,
                                                          parent = character_name + '_tail_base_target_cc_01',
                                                          shape = 'spherical_target',
                                                          locked_channels = ['visibility']
                                                          ) 
            mc.delete(mc.parentConstraint(character_name + '_tail_base_target_cc_01', character_name + '_tail_MID_target_cc_01', lower_tail_secondary_target.Off, maintainOffset=False))
                    
        
    
    
        # STRETCHY JOINT TARGETS (mirrored)  
        for side in ["_LFT" , "_RGT"]:

            # make upper_arm stretchy joint targets
            make_stretchy_joint_targets(side, 'upper_arm', character_name, number_of_upper_arm_joints, scale, character_name + side + "_upper_arm_target_cc_01", character_name + side + "_lower_arm_target_cc_01")
            
            # make lower_arm stretchy joint targets
            make_stretchy_joint_targets(side, 'lower_arm', character_name, number_of_lower_arm_joints, scale, character_name + side + "_lower_arm_target_cc_01", character_name + side + "_hand_target_cc_01")
            
            # make upper_leg stretchy joint targets
            make_stretchy_joint_targets(side, 'upper_leg', character_name, number_of_upper_leg_joints, scale, character_name + side + "_upper_leg_target_cc_01", character_name + side + "_lower_leg_target_cc_01")
            
            # make lower_leg stretchy joint targets
            make_stretchy_joint_targets(side, 'lower_leg', character_name, number_of_lower_leg_joints, scale, character_name + side + "_lower_leg_target_cc_01", character_name + side + "_foot_target_cc_01")
        
        # scale back to scene scale
        #mc.scale(scale,scale,scale, 'joint_targets_GRP_01') 

        
        # allow for only orientation of fingers
        mc.delete('*aimConstraint*')
        mc.select('*finger*', '*thumb*')
        selected_objects = mc.ls(selection=True, transforms=True)
        for object in selected_objects:
            mc.setAttr(str(object) + '.scale', lock=True)
            mc.setAttr(str(object) + '.translate', lock=True)
            mc.setAttr(str(object) + '.rotateY', lock=True)
            mc.setAttr(str(object) + '.rotateZ', lock=True)
        
 

    
# ****************** open main GUI windows *****************************   

def make_GUI(character_name, scene_scale, main_project_path, geometry_filepath, builder_scene_filepath, primary_targets_filepath, secondary_targets_filepath, skin_weights_directory, skin_weights_extension):
    
    """
    function to build GUI to gather information needed to initialize the rig joint-target-placement scene
    """
    
    # check to see if the window exists
    if mc.windowPref("get_builder_scene_parameters",exists=True): mc.windowPref("get_builder_scene_parameters",remove=True)
    if mc.window("get_builder_scene_parameters",exists=True): mc.deleteUI("get_builder_scene_parameters",window=True)
    
    # create the window
    GUI_window = mc.window("get_builder_scene_parameters",title="Rig_Parameters",width=300,height=550,sizeable=True)
    
    # set overarching form layout
    form_layout = mc.formLayout(numberOfDivisions=100)
    
    # banner image
    image_path = mc.internalVar(userPrefDir=True) + 'icons/BYU_logo.jpg'
    BYU_icon = mc.image(w=300, h=136, image=image_path)
    
    # add button to initialize rig builder scene 
    initialize_primary_targets_button = mc.button("initialize_primary_targets_button", label = "Initialize Primary Joint Targets", width = 270, 
                                          command = partial(initialize_primary_rig_targets_button_press, GUI_window, builder_scene_filepath, main_project_path, scene_scale))
    
    # add button to reinitialize rig builder scene with secondaries
    initialize_secondary_targets_button = mc.button("initialize_secondary_targets_button", label = "Initialize Secondary Joint Targets", width = 270, 
                                          command = partial(initialize_secondary_rig_targets_button_press, GUI_window, builder_scene_filepath, main_project_path, scene_scale))
    
    # add button to initialize rig builder scene 
    build_rig_button = mc.button("build_rig_button", label = "Build Rig!", width = 270, 
                                 command = partial(build_rig_button_press, GUI_window, builder_scene_filepath, main_project_path, character_name))
       
    '''
    Props to Ricardo Viana for file open/save GUI functionality
    '''

    #projects option menu
    project_options_menu=mc.optionMenu("project_options_menu", label="Projects:", width=290, height=25, changeCommand=partial(change_project, main_project_path), parent=form_layout)
    #call function to populate it with projects
    populate_projects(main_project_path)
    #set starting menu item
    mc.optionMenu("project_options_menu", edit=True, select=3)

    # set primary targets layout to be nested in form layout after save primaries button
    load_primaries_file_browser_layout = mc.rowColumnLayout( numberOfColumns=1, columnAttach=(1, 'left', 5), columnWidth=[(1, 290)], parent= form_layout)
    #text
    mc.text("LOAD PRIMARY JOINTS: double click to open", align='center', width=290)
    #mayafiles textScrollList
    primary_file_options_menu=mc.textScrollList("primary_file_options_menu", width=290, height = 70, doubleClickCommand=partial(primary_load, GUI_window, character_name, primary_targets_filepath, main_project_path))
    #function to load files
    get_primary_files(main_project_path)
    
    # set secondary targets layout to be nested in form layout after save primaries button
    load_secondaries_file_browser_layout = mc.rowColumnLayout( numberOfColumns=1, columnAttach=(1, 'left', 5), columnWidth=[(1, 290)], parent= form_layout)
    #text
    mc.text("LOAD secondary JOINTS: double click to open", align='center', width=290)
    #mayafiles textScrollList
    secondary_file_options_menu=mc.textScrollList("secondary_file_options_menu", width=290, height = 70, doubleClickCommand=partial(secondary_load, GUI_window, character_name, secondary_targets_filepath, main_project_path))
    #function to load files
    get_secondary_files(main_project_path)
    
    
    
    # set row column layout to be nested in form layout
    row_column_layout = mc.rowColumnLayout( numberOfColumns=2, columnAttach=(1, 'left', 10), columnWidth=[(1, 190), (2, 100)], parent=form_layout )

    # add text (label) and integer field for number of fingers, finger joints, toes, and toe joints
    mc.text("Number_of_fingers: ")
    number_of_fingers = mc.intField( "number_of_fingers", value=4 )
    mc.text("Number_of_joints_per_finger: ")
    number_of_joints_per_finger = mc.intField( "number_of_joints_per_finger", value=3 )
    mc.text("Number_of_toes: ")
    number_of_fingers = mc.intField( "number_of_toes", value=4 )
    mc.text("Number_of_joints_per_toe: ")
    number_of_joints_per_toe = mc.intField( "number_of_joints_per_toe", value=3 )   
    
    mc.separator(h=15)
    mc.separator(h=15)
        
    # add text (label) and integer field for number of spine joints, neck joints, upper arm joints, lower arm joints, upper leg joints, and lower leg joints   
    mc.text( label='Number of Spine Spans' )
    number_of_spine_spans = mc.intField("number_of_spine_spans", value=13)
    mc.text( label='Number of Neck Spans' )
    number_of_neck_spans = mc.intField( "number_of_neck_spans", value=9 )
    mc.text( label='Number of Upper Arm Spans' )
    number_of_upper_arm_spans = mc.intField( "number_of_upper_arm_spans", value=10 )
    mc.text( label='Number of Lower Arm Spans' )
    number_of_lower_arm_spans = mc.intField( "number_of_lower_arm_spans", value=10 )
    mc.text( label='Number of Upper Leg Spans' )
    number_of_upper_leg_spans = mc.intField( "number_of_upper_leg_spans", value=10 )
    mc.text( label='Number of Lower Leg Spans' )
    number_of_lower_leg_spans = mc.intField( "number_of_lower_leg_spans", value=10 )
    
    mc.separator(h=15)
    mc.separator(h=15)
    
    # add option for tail
    mc.text("Has tail: ")
    has_tail = mc.checkBox( "has_tail", label='Has Tail' )
    mc.text( label='Number of Upper Tail Spans' )
    number_of_upper_tail_spans = mc.intField( "number_of_upper_tail_spans", value=10 )
    mc.text( label='Number of Lower Tail Spans' )
    number_of_lower_tail_spans = mc.intField( "number_of_lower_tail_spans", value=10 )
      
   
    # set second column layout to be nested in form layout after primaries button
    second_row_column_layout = mc.rowColumnLayout( numberOfColumns=2, columnAttach=(1, 'left', 5), columnWidth=[(1, 150), (2, 150)], parent= form_layout)
    
    primary_mirror_direction = mc.checkBox( "primary_mirror_direction", label='+X' )
    mirror_primary_targets_button = mc.button("mirror_primary_targets_button", label = "Mirror Primary Joint Targets", width = 150, 
                                          command = partial(mirror_primary_rig_targets_button_press, GUI_window, builder_scene_filepath, main_project_path, scene_scale))
   
    mc.separator(h=5)
    mc.separator(h=5)

    selected_project = str.capitalize(str(mc.optionMenu("project_options_menu", query=True, value=True)))
    save_primary_targets_filename = mc.textField( "save_primary_targets_filename", text=selected_project + '_primaries_01', width = 140 )
    save_primary_targets_button = mc.button("save_primary_targets_button", label = "Save Primary Joint Targets", width = 150, 
                                          command = partial(save_primary_rig_targets_button_press, GUI_window, character_name, primary_targets_filepath, main_project_path))



    # set third column layout to be nested in form layout after secondaries button
    third_row_column_layout = mc.rowColumnLayout( numberOfColumns=2, columnAttach=(1, 'left', 5), columnWidth=[(1, 150), (2, 150)], parent= form_layout)
    
    secondary_mirror_direction = mc.checkBox( "secondary_mirror_direction", label='+X' )
    mirror_secondary_targets_button = mc.button("mirror_secondary_targets_button", label = "Mirror secondary Joint Targets", width = 150, 
                                          command = partial(mirror_secondary_rig_targets_button_press, GUI_window, builder_scene_filepath, main_project_path))
   
    mc.separator(h=5)
    mc.separator(h=5)
    
    save_secondary_targets_filename = mc.textField( "save_secondary_targets_filename", text=selected_project + '_secondaries_01', width = 140 )
    save_secondary_targets_button = mc.button("save_secondary_targets_button", label = "Save secondary Joint Targets", width = 150, 
                                          command = partial(save_secondary_rig_targets_button_press, GUI_window, character_name, secondary_targets_filepath, main_project_path))

    
    
    mc.formLayout(form_layout, 
                    edit=True, 
                    attachForm =     [(BYU_icon, 'top', 5),
                                      (BYU_icon, 'left', 5), 
                                      (BYU_icon, 'right', 5), 
                                      (build_rig_button, 'left', 5), 
                                      (build_rig_button, 'bottom', 5), 
                                      (build_rig_button, 'right', 5), 
                                      (project_options_menu, 'left', 10),
                                      (project_options_menu, 'right', 10),
                                      (load_primaries_file_browser_layout, 'left', 5),
                                      (load_primaries_file_browser_layout, 'right', 5),
                                      (load_secondaries_file_browser_layout, 'left', 5),
                                      (load_secondaries_file_browser_layout, 'right', 5),                                      (initialize_primary_targets_button, 'left', 5), 
                                      (initialize_primary_targets_button, 'right', 5), 
                                      (initialize_secondary_targets_button, 'left', 5), 
                                      (initialize_secondary_targets_button, 'right', 5), 
                                      (second_row_column_layout, 'left', 5), 
                                      (second_row_column_layout, 'right', 5), 
                                      (third_row_column_layout, 'left', 5), 
                                      (third_row_column_layout, 'right', 5), 
                                      (row_column_layout, 'left', 5), 
                                      (row_column_layout, 'right', 5)],
                    attachControl =  [(project_options_menu, 'top', 5, BYU_icon),
                                      (row_column_layout, 'top', 5, project_options_menu),
                                      (initialize_primary_targets_button, 'top', 5, row_column_layout),
                                      (second_row_column_layout, 'top', 5, initialize_primary_targets_button),
                                      (load_primaries_file_browser_layout, 'top', 5, second_row_column_layout),
                                      (initialize_secondary_targets_button, 'top', 5, load_primaries_file_browser_layout),
                                      (third_row_column_layout, 'top', 5, initialize_secondary_targets_button),
                                      (load_secondaries_file_browser_layout, 'top', 5, third_row_column_layout),
                                      (build_rig_button, 'top', 5, load_secondaries_file_browser_layout)]
                 )
    
    
    
    # add commands to move to next line when input entered
    #mc.textField( "character_name", edit=True, changeCommand = ('mc.setFocus("number_of_fingers")') )
    mc.intField( "number_of_fingers", edit=True, changeCommand = ('mc.setFocus("number_of_joints_per_finger")') )
    mc.intField( "number_of_joints_per_finger", edit=True, changeCommand = ('mc.setFocus("number_of_toes")') )
    mc.intField( "number_of_toes", edit=True, changeCommand = ('mc.setFocus("number_of_joints_per_toe")') )
    mc.intField( "number_of_joints_per_toe", edit=True, changeCommand = ('mc.setFocus("number_of_spine_spans")') ) 
    mc.intField( "number_of_spine_spans", edit=True, changeCommand = ('mc.setFocus("number_of_neck_spans")') )
    mc.intField( "number_of_neck_spans", edit=True, changeCommand = ('mc.setFocus("number_of_upper_arm_spans")') )
    mc.intField( "number_of_upper_arm_spans", edit=True, changeCommand = ('mc.setFocus("number_of_lower_arm_spans")') )
    mc.intField( "number_of_lower_arm_spans", edit=True, changeCommand = ('mc.setFocus("number_of_upper_leg_spans")') )
    mc.intField( "number_of_upper_leg_spans", edit=True, changeCommand = ('mc.setFocus("number_of_lower_leg_spans")') )
    mc.intField( "number_of_lower_leg_spans", edit=True, changeCommand =  ('mc.setFocus("number_of_upper_tail_spans")') )
    mc.intField( "number_of_upper_tail_spans", edit=True, changeCommand = ('mc.setFocus("number_of_lower_tail_spans")') )
    mc.intField( "number_of_lower_tail_spans", edit=True, changeCommand = ('mc.setFocus("initialize_button")') )
    
    mc.showWindow( GUI_window )

    

    
    
    
    

    