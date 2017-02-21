from byuam import Department
import maya.cmds as cmds
import os


def go():
    path = os.environ['BYU_TOOLS_DIR'] + '/byugui/assets/'
    cmds.file("/users/animation/bdemann/Documents/grendel-dev/byu-pipeline-tools/byugui/assets/gnome.obj", reference=False, typ="OBJ")
    cmds.file( path + "gnome.obj", reference=False, typ="OBJ" )
