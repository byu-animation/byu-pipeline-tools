from byugui.rollback_gui import RollbackWindow
from byuam.environment import Department
import maya.cmds as cmds
from PyQt4 import QtCore
import maya.OpenMayaUI as omu
import sip
import os

maya_rollback_dialog = None

def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)
    
def rollback():
    filepath = maya_rollback_dialog.result
    if filepath is not None:
        if not cmds.file(q=True, sceneName=True) == '':
            cmds.file(save=True, force=True) #save file

        if not os.path.exists(filepath):
            cmds.file(new=True, force=True)
            cmds.file(rename=filepath)
            cmds.file(save=True, force=True)
            print "new file "+filepath
        else:
            cmds.file(filepath, open=True, force=True)
            print "open file "+filepath

def go():
    parent = maya_main_window()
    filePath = cmds.file(q=True, sceneName=True)
    global maya_rollback_dialog
    maya_rollback_dialog = RollbackWindow(filePath, parent)
    maya_rollback_dialog.finished.connect(rollback)
