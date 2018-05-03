from byuam import Department, Project
from byugui import RollbackWindow, SelectionWindow, message_gui
from PySide import QtGui
import os
import nuke

nuke_checkout_dialog = None

def post_rollback():
	filepath = rollback_window.result

	if filepath is not None:
		nuke.scriptClose()
		print "open file " + filepath
		nuke.scriptOpen(filepath)

def post_selection():
	parent = QtGui.QApplication.activeWindow()
	element = rollback_selection_window.result
	if element is None:
		return
	global rollback_window
	rollback_window = RollbackWindow(element, parent)
	rollback_window.finished.connect(post_rollback)

def go():
	parent = QtGui.QApplication.activeWindow()
	filepath = nuke.toNode("root").name()
	shot = os.path.basename(filepath)
	index = shot.find("_comp")
	if index > 0:
		base_name = shot[:index]
		print base_name
	else:
		# If there is no composition opened then we allow the user to select one from all of the comps.
		global rollback_selection_window
		rollback_selection_window = SelectionWindow(parent, dept_list=[Department.COMP])
		rollback_selection_window.finished.connect(post_selection)
		return

	project = Project()
	body = project.get_body(base_name)
	element = body.get_element(Department.COMP)

	# nuke.scriptClose()
	global rollback_window
	rollback_window = RollbackWindow(element, parent)
	rollback_window.finished.connect(post_rollback)
