from byugui.reference_gui import ReferenceWindow
from byuam.environment import Department
import maya.cmds as cmds
from PyQt4 import QtCore, QtGui
import maya.OpenMayaUI as omu
import os
import sip

maya_reference_dialog = None

def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)
    
def post_reference():
    file_path = maya_reference_dialog.filePath
    done = maya_reference_dialog.done
    reference = maya_reference_dialog.reference

    if file_path is not None and reference:
        if os.path.exists(file_path):
            cmds.file(file_path, reference=True)
        else:
            error_dialog = QtGui.QErrorMessage(maya_main_window())
            error_dialog.showMessage("The chosen element is empty. Nothing has been published to it, so it can't be referenced.")
    if not done:
        go()


def go():
    parent = maya_main_window()
    filePath = cmds.file(q=True, sceneName=True)
    global maya_reference_dialog
    maya_reference_dialog = ReferenceWindow(parent, filePath, [Department.RIG, Department.MODEL])
    maya_reference_dialog.finished.connect(post_reference)
