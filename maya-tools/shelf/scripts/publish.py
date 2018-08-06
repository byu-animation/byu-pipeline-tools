from byuam import Department
from byuam import Environment
from byuam import pipeline_io
from byugui.publish_gui import PublishWindow
from PySide2 import QtWidgets
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import os
import alembic_exporter
from byugui import message_gui
import pymel.core as pm
import sketchfab_exporter
import education

maya_publish_dialog = None

def maya_main_window():
	'''Return Maya's main window'''
	for obj in QtWidgets.qApp.topLevelWidgets():
		if obj.objectName() == 'MayaWindow':
			return obj
	raise RuntimeError('Could not find MayaWindow instance')

def clear_construction_history():
	pm.delete(constructionHistory=True, all=True)

def freeze_transformations():
	objects = pm.ls(transforms=True)
	for sceneObj in objects:
	    pm.makeIdentity(sceneObj, apply=True)


def post_publish():
	element = maya_publish_dialog.result

	if maya_publish_dialog.published:
		if not cmds.file(q=True, sceneName=True) == '':
			cmds.file(save=True, force=True) #save file

		#Publish
		user = maya_publish_dialog.user
		src = maya_publish_dialog.src
		comment = maya_publish_dialog.comment
		publishElement(element, user, src, comment)

def publishElement(element, user, src, comment):
	dst = element.publish(user, src, comment)
	#Ensure file has correct permissions
	try:
		os.chmod(dst, 0660)
	except:
		pass

	#freeze transformations and clear history
	if maya_publish_dialog.clearHistoryCheckbox.isChecked():
		clear_construction_history()
		try:
			freeze_transformations()
		except:
			freeze_error_msg = ("Failed to freeze transformations, probably because "
			"there are one or more keyframed values in your object. Remove all "
			"keyframed values and expressions from your object and try again.")
			cmds.confirmDialog(title="Freeze Transformations Error", message=freeze_error_msg)
			print(freeze_error_msg)

	#Export a playblast
	print 'TODO: export playblast'
	print element.get_name()

	#Export Alembics
	print 'Publish Complete. Begin Exporting Alembic'
	alembic_exporter.go(element=element)
	noEducationalLicence()
	sketchfab_exporter.go(element=element, dept=maya_publish_dialog.department)

def noEducationalLicence():
	pm.FileInfo()['license'] = 'education'
	fileName = pm.sceneName()
	pm.saveFile()
	message_gui.info('This Maya file has been converted to an education licence')


def go():
	parent = maya_main_window()
	filePath = cmds.file(q=True, sceneName=True)
	if not filePath:
		filePath = Environment().get_user_workspace()
		filePath = os.path.join(filePath, 'untitled.mb')
		filePath = pipeline_io.version_file(filePath)
		cmds.file(rename=filePath)
		cmds.file(save=True)
	global maya_publish_dialog
	maya_publish_dialog = PublishWindow(filePath, parent, [Department.MODEL, Department.RIG, Department.LAYOUT, Department.ANIM, Department.CFX, Department.CYCLES])
	maya_publish_dialog.finished.connect(post_publish)
