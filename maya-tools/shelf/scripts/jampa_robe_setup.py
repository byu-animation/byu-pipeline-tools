#Author: Trevor Barrus
'''
    Preconditions: This script is to be called inside of the animation shot. Also, in order to work, this script requires Jampa's animation to have already been exported using the alembic export tool.
    Result: A checkout out cfx file with Jampa's robe set in starting position with attached nCloth nodes and proper nucleus parameters.
'''
import os
import maya.cmds as mc
from byuam.project import Project
from byuam.environment import Department, Environment

def go():
    project = Project()
    environment = Environment()

    # Create a global position locator which will grab Jampa's position despite his scaled translations
    globalPos = mc.spaceLocator(p=[0,0,0])
    globPos = mc.rename(globalPos, "jampaGlobalPos")
    mc.select("jampa_rig_main_global_cc_01")
    mc.select(globPos, add=True)
    mc.pointConstraint(offset=[0,0,0], weight=1)
    mc.orientConstraint(offset=[0,0,0], weight=1)

    # Get transformation variables from globPos locator
    tx = mc.getAttr(globPos+".translateX")
    ty = mc.getAttr(globPos+".translateY")
    tz = mc.getAttr(globPos+".translateZ")
    rx = mc.getAttr(globPos+".rotateX")
    ry = mc.getAttr(globPos+".rotateY")
    rz = mc.getAttr(globPos+".rotateZ")

    # get alembic filepath for scene's animation (requires prior export)
    src = cmds.file(q=True, sceneName=True)
    src_dir = os.path.dirname(src)
    checkout_element = project.get_checkout_element(src_dir)
    checkout_body_name = checkout_element.get_parent()
    body = project.get_body(checkout_body_name)
    element = body.get_element(Department.ANIM)
    cache_file = os.path.join(element.get_dir(), "cache", "jampa_rig_main.abc")

    # checkout cfx scene for corresponding shot number
    current_user = environment.get_current_username()
    element = body.get_element(Department.CFX)
    cfx_filepath = element.checkout(current_user)

    #open cfx file 
    if cfx_filepath is not None:
        if not cmds.file(q=True, sceneName=True) == '':
            cmds.file(save=True, force=True) #save file

        if not os.path.exists(cfx_filepath):
            cmds.file(new=True, force=True)
            cmds.file(rename=cfx_filepath)
            cmds.file(save=True, force=True)
        else:
            cmds.file(cfx_filepath, open=True, force=True)

    # import alembic
    command = "AbcImport -mode import \"" + cache_file + "\""
    maya.mel.eval(command)

    # delete all geo except jampa skin and rename
    geometry = mc.ls(geometry=True)
    transforms = mc.listRelatives(geometry, p=True, path=True)
    mc.select(transforms, r=True)
    for geo in mc.ls(sl=True):
        if(geo != "jampa_rig_main_jampa_geo_body"):
            mc.delete(geo)
    collide = "JAMPA_COLLIDE"
    mc.rename("jampa_rig_main_jampa_geo_body", collide)

    # reference robe
    body = project.get_body("jampa_robe")
    element = body.get_element(Department.MODEL)
    robe_file = element.get_app_filepath()
    mc.file(robe_file, reference=True)

    # set robe transforms to variables above
    mc.setAttr("jampa_robe_model_main_jampa_robe_sim.translateX", tx)
    mc.setAttr("jampa_robe_model_main_jampa_robe_sim.translateY", ty)
    mc.setAttr("jampa_robe_model_main_jampa_robe_sim.translateZ", tz)
    mc.setAttr("jampa_robe_model_main_jampa_robe_sim.rotateX", rx)
    mc.setAttr("jampa_robe_model_main_jampa_robe_sim.rotateY", ry)
    mc.setAttr("jampa_robe_model_main_jampa_robe_sim.rotateZ", rz)

    # make jampa skin a passive collider
    mc.select(collide)
    command = "makeCollideNCloth"
    maya.mel.eval(command)
    rigid_shape = "nRigid_jampa"
    mc.rename("nRigid1", rigid_shape)

    # make cloth objects and display layers of each robe piece
    jampa_torso = "jampa_robe_model_main_robe_torso_01"
    jampa_sash = "jampa_robe_model_main_robe_sash_01"
    jampa_skirt = "jampa_robe_model_main_robe_skirt_01"

    cloth_pieces = {jampa_torso, jampa_sash, jampa_skirt}
    command = "createNCloth 0"
    for cp in cloth_pieces:
        mc.select(cp)
        maya.mel.eval(command)
        mc.rename("nCloth1", "nCloth_"+cp)
        mc.select(cp)
        layername = "cloth_"+cp[:-3].replace("robe_model_main_robe_", "")
        mc.createDisplayLayer(name=layername.upper(), number=1, noRecurse=True)

    # set appropriate values in nucleus node
    nucleus = "nucleus_jampa"
    mc.rename("nucleus1", nucleus)
    mc.setAttr(nucleus+".subSteps", 30)
    mc.setAttr(nucleus+".startFrame", -50)
    mc.setAttr(nucleus+".spaceScale", 0.23)

    mc.currentTime(-50)
