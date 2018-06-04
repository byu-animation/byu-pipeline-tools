from byugui.new_body_gui import CreateWindow, NewBodyWindow
from PySide2 import QtWidgets
import maya.OpenMayaUI as omu
import os

def maya_main_window():
	"""Return Maya's main window"""
	print "get main window"
	for obj in QtWidgets.qApp.topLevelWidgets():
		if obj.objectName() == 'MayaWindow':
			print "leaving get main window"
			return obj
	raise RuntimeError('Could not find MayaWindow instance')


def go():
	try:
		print"in main function"
		parent = maya_main_window()
		dialog = CreateWindow(parent)
	except:
		print "caught error"
