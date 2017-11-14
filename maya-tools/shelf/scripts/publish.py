from byuam import Department
from byuam import Environment
from byuam import pipeline_io
from byugui.publish_gui import PublishWindow
from PySide2 import QtWidgets
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import alembic_static_exporter
import os
import alembic_exporter
from byugui import message_gui

maya_publish_dialog = None

def maya_main_window():
	"""Return Maya's main window"""
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
		dst = element.publish(user, src, comment)
		#Ensure file has correct permissions
		try:
			os.chmod(dst, 0660)
		except:
			pass

		print "TODO: export playblast"
		print maya_publish_dialog.result.get_name()

		#TODO I put this here becuase we have a people with the alemic export that will always fail unless the user is publishing or exporting from an already checkouted file. Without this whenever we do the first publish they will get an error duing the alembic export process that would be disconcerting and pershaps suggest that the publish was unsucessful. So I want them to feel confident that the publish was successfull. Ultimatly I want this gone so the process is more streamlined. So when the exporter is fixed so that it can export on the first publish then we will be fine.
		message_gui.info("Publish Complete. Starting Alembic Export")

		if element.get_department() == Department.MODEL:
			print "Exporting Alembic"
			alembic_static_exporter.go()
		if element.get_department() == Department.ANIM:
			print "Giving the Animator the opportunity to export alembic"
			alembic_exporter.go()

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
	maya_publish_dialog = PublishWindow(filePath, parent, [Department.MODEL, Department.RIG, Department.LAYOUT, Department.ANIM, Department.CFX])
	maya_publish_dialog.finished.connect(post_publish)
