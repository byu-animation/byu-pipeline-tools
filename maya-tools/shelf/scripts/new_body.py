from byugui.new_body_gui import CreateWindow, NewBodyWindow
from PySide2 import QtWidgets
import maya.OpenMayaUI as omu

def maya_main_window():
	"""Return Maya's main window"""
	for obj in QtWidgets.qApp.topLevelWidgets():
		if obj.objectName() == 'MayaWindow':
			return obj
	raise RuntimeError('Could not find MayaWindow instance')

def go():
	parent = maya_main_window()
	dialog = CreateWindow(parent)
