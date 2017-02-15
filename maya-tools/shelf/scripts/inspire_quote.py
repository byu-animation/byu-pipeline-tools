# Author: Ben DeMann

from byuam import Department
from byugui.inspire_quote_gui import QuoteWindow
from PyQt4 import QtCore
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip
import alembic_static_exporter
import os
import alembic_exporter

maya_publish_dialog = None

def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

def go():
    parent = maya_main_window()
    filePath = cmds.file(q=True, sceneName=True)
    global maya_publish_dialog
    maya_publish_dialog = QuoteWindow(parent)
