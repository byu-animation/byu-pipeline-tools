from byuam import Department
import maya.cmds as cmds
import os


def go():
    path = os.environ['BYU_TOOLS_DIR'] + '/maya-tools/shelf/geo/'
    cmds.file( path + "gnome.obj", i = True, type="OBJ", iv=True, ra=True, mnc=False, ns="gnome", op="mo=1", pr=True)
