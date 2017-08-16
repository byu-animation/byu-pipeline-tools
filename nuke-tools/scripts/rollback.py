from byuam import Department, Project
from byugui import RollbackWindow, error_gui
from PySide import QtGui
import os
import nuke

nuke_checkout_dialog = None

def post_rollback():
	filepath = rollback_window.result

	if filepath is not None:
		print "open file " + filepath
		nuke.scriptOpen(filepath)

def go():
	filepath = nuke.toNode("root").name()
	shot = os.path.basename(filepath)
	index = shot.find("_comp")
	if index > 0:
		base_name = shot[:index]
		print base_name
	else:
		error_gui.error("We couldn't figure out what asset you are working on.")
		return

	project = Project()
	body = project.get_body(base_name)
	element = body.get_element(Department.COMP)

	nuke.scriptClose()
	global rollback_window
	parent = QtGui.QApplication.activeWindow()
	rollback_window = RollbackWindow(element, parent)
	rollback_window.finished.connect(post_rollback)
