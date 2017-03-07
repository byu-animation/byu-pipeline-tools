# Author: Ben DeMann

from byugui.inspire_quote_gui import QuoteWindow
from PyQt4 import QtCore
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip
import os

maya_inspire_dialog = None

def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

def go():
    #parent = maya_main_window()
    global maya_inspire_dialog
    maya_inspire_dialog = QuoteWindow()
