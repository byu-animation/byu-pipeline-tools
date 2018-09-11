# Author: Ben DeMann

from byuam import Department, Environment
try:
	from PySide import QtGui as QtWidgets
	from PySide import QtGui as QtGui
	from PySide import QtCore
	print 'trying'
except ImportError:
	try:
		from PySide2 import QtWidgets, QtGui, QtCore
	except:
		print 'failed second import'
import os
import mari
from byugui import message_gui
from byugui.rollback_gui import RollbackWindow

from byuam import Project, Department, Environment

def post_rollback():
	project = mari.projects.current()
	project_id = project.uuid()
	project.close()
	filepath = rollback_window.result
	if filepath is not None:
		mari.projects.remove(project_id)
		project = mari.projects.extract(filepath)
		mari.projects.open(project.name())

def go():
	try:
		scene_name = mari.projects.current().name()
	except:
		message_gui.error("You need to open the project that you would like to rollback.")
		return

	shot = os.path.basename(scene_name)
	index = shot.find("_texture")
	if index > 0:
		base_name = shot[:index]
		print base_name
	else:
		message_gui.error("We couldn't figure out what asset you are working on.")
		return

	project = Project()
	body = project.get_body(base_name)
	element = body.get_element(Department.TEXTURE)

	global rollback_window
	parent = QtGui.QApplication.activeWindow()
	rollback_window = RollbackWindow(element, parent)
	rollback_window.finished.connect(post_rollback)
