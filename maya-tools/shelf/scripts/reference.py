from byugui.reference_gui import ReferenceWindow
from byuam.environment import Department
import pymel.core as pm
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

def post_reference(dialog):
	file_paths = dialog.filePaths
	done = dialog.done
	isReferenced = dialog.reference

	print "The filePaths are", file_paths
	print "The reference is", isReferenced

	if file_paths is not None and isReferenced:
		empty = []
		for path in file_paths:
			if os.path.exists(path):
				pm.system.createReference(path, namespace="HelloWorld1")
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
	# filePath = pm.file(q=True, sceneName=True)
	filePath = pm.system.sceneName()
	maya_reference_dialog = ReferenceWindow(parent, filePath, [Department.MODEL, Department.RIG])
	maya_reference_dialog.finished.connect(lambda: post_reference(maya_reference_dialog))
