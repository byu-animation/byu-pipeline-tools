from byugui.publish_gui import PublishWindow
import maya.cmds as cmds
from PyQt4 import QtCore
import maya.OpenMayaUI as omu
import sip

def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

def go():
    parent = maya_main_window()
    filePath = cmds.file(q=True, sceneName=True)
    dialog = PublishWindow(filePath, parent)
