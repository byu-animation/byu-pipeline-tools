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

	#Export a playblast
	print 'TODO: export playblast'
	print element.get_name()

	#Export Alembics
	print 'Publish Complete. Begin Exporting Alembic'
	alembic_exporter.go(element=element)
	noEducationalLicence()
	sketchfab_exporter.go(element=element, dept=maya_publish_dialog.department)

def noEducationalLicence():
	print pm
	pm.FileInfo()['license'] = 'education'
	fileName = pm.sceneName()
	pm.saveFile()



def go():

	parent = maya_main_window()
	filePath = cmds.file(q=True, sceneName=True)

	if not filePath:

		filePath = Environment().get_user_workspace()
		filePath = os.path.join(filePath, 'untitled.ma')
		filePath = pipeline_io.version_file(filePath)
		cmds.file(rename=filePath)
	cmds.file(type='mayaAscii')
	cmds.file(save=True)

	global maya_publish_dialog
	maya_publish_dialog = PublishWindow(filePath, parent, [Department.MODEL, Department.RIG, Department.LAYOUT, Department.ANIM, Department.CFX, Department.CYCLES])
	maya_publish_dialog.finished.connect(post_publish)
