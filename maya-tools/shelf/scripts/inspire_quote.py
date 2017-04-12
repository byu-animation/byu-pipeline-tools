# Author: Ben DeMann

from byugui.inspire_quote_gui import QuoteWindow
from PySide2 import QtGui, QtWidgets, QtCore
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip
import os

maya_inspire_dialog = None

def maya_main_window():
    """Return Maya's main window"""
    for obj in QtWidgets.qApp.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj
    raise RuntimeError('Could not find MayaWindow instance')

def go():
    parent = maya_main_window()
    global maya_inspire_dialog
    maya_inspire_dialog = QuoteWindow(parent)
