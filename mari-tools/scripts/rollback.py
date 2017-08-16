# Author: Ben DeMann

from byuam import Department, Environment
from PySide import QtGui
import os
import mari
from byugui import RollbackWindow, error_gui

from byuam import Project, Department, Environment

def go():
	project = Project()
	try:
		scene_name = mari.projects.current().name()
	except:
		error_gui.error("You need to open the project that you would like to rollback.")
	shot = os.path.basename(scene_name)
	index = shot.find("_texture")
	if index > 0:
		base_name = shot[:index]
		print base_name
	else:
		error_gui.error("We couldn't figure out what asset you are working on.")
		return
	body = project.get_body(base_name)
	element = body.get_element(Department.TEXTURE)
	global rollback_window
	parent = QtGui.QApplication.activeWindow()
	rollback_window = RollbackWindow(element, parent)
	rollback_window.finished.connect(rollback)

def rollback():
	project = mari.projects.current()
	project_id = project.uuid()
	project.close()
	filepath = rollback_window.result
	if filepath is not None:
		mari.projects.remove(project_id)
		project = mari.projects.extract(filepath)
		mari.projects.open(project.name())
