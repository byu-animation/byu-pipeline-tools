from byugui.reference_gui import ReferenceWindow
from byuam.environment import Department
import maya.cmds as cmds
from PySide2 import QtWidgets
import maya.OpenMayaUI as omu
import os

maya_reference_dialog = None

def maya_main_window():
	"""Return Maya's main window"""
	for obj in QtWidgets.qApp.topLevelWidgets():
		if obj.objectName() == 'MayaWindow':
			return obj
	raise RuntimeError('Could not find MayaWindow instance')

def post_reference():
	file_paths = maya_reference_dialog.filePaths
	done = maya_reference_dialog.done
	reference = maya_reference_dialog.reference

	if file_paths is not None and reference:
		empty = []
		for path in file_paths:
			if os.path.exists(path):
				cmds.file(path, reference=True)
			else:
				empty.append(path)

		if empty:
			empty_str = '\n'.join(empty)
			error_dialog = QtWidgets.QErrorMessage(maya_main_window())
			error_dialog.showMessage("The following elements are empty. Nothing has been published to them, so they can't be referenced.\n"+empty_str)
	# if not done:
	#	 go()


def go():
	parent = maya_main_window()
	filePath = cmds.file(q=True, sceneName=True)
	global maya_reference_dialog
	maya_reference_dialog = ReferenceWindow(parent, filePath, [Department.MODEL, Department.RIG])
	maya_reference_dialog.finished.connect(post_reference)
