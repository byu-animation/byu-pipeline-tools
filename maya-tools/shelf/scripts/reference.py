from byugui.reference_gui import ReferenceWindow
from byuam.environment import Department
import maya.cmds as cmds
from PyQt4 import QtCore
import maya.OpenMayaUI as omu
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
        print file_path
        cmds.file(file_path, reference=True)
    if not done:
        go()


def go():
    parent = maya_main_window()
    global maya_reference_dialog
    maya_reference_dialog = ReferenceWindow(parent, [Department.MODEL, Department.RIG, Department.LAYOUT, Department.ANIM])
    maya_reference_dialog.finished.connect(post_reference)
