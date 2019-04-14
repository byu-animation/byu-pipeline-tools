from byuam import Department
from byugui.checkout_gui import CheckoutWindow
from PySide2 import QtWidgets
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import os

maya_checkout_dialog = None

def maya_main_window():
	"""Return Maya's main window"""
	for obj in QtWidgets.qApp.topLevelWidgets():
		if obj.objectName() == 'MayaWindow':
			return obj
	raise RuntimeError('Could not find MayaWindow instance')

def open_file():
	filepath = maya_checkout_dialog.result
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

def non_gui_open(filePath=None,assetName='Temp'):
	if filePath == None:
		print 'no file'
		return
	if os.path.exists(filePath):
		cmds.file(filePath, open=True, force=True)
		print "open file " + assetName
	else:
		print 'Does not Exist: '+assetName

def go():
	parent = maya_main_window()
	global maya_checkout_dialog
	maya_checkout_dialog = CheckoutWindow(parent, [Department.MODEL, Department.RIG, Department.LAYOUT, Department.ANIM, Department.CFX, Department.CYCLES])
	maya_checkout_dialog.finished.connect(open_file)
	# if dialog.exec_():
	#	 print self.result
