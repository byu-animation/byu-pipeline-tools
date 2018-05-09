from byuam import Department
import maya.cmds as cmds
import os

def go():
    path = os.environ['BYU_TOOLS_DIR'] + '/maya-tools/shelf/geo/'
    cmds.file( path + "death.obj", i = True, type="OBJ", iv=True, ra=True, mnc=False, ns="death", op="mo=1", pr=True)
