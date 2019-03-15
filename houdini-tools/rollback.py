#Author: Trevor Barrus and Ben DeMann
import hou
import os
from PySide2 import QtGui, QtWidgets, QtCore
from byugui import RollbackWindow, SelectionWindow, message_gui

from byuam import Project, Department, Environment

def rollback_hda():
	filepath = rollback_window.result
	if filepath is not None:
		environment = Environment()
		hou.hda.uninstallFile(src, change_oplibraries_file=False)
		dst = os.path.join(environment.get_hda_dir(), asset_name)
		hou.hda.installFile(dst)
		message_gui.info('Rollback successful')

def rollback_shot():
	filepath = rollback_window.result
	if filepath is not None:
		hou.hipFile.load(filepath)
		message_gui.info('Rollback successful')

def post_selection():
	element = rollback_selection_window.result
	if element is None:
		return

	global rollback_window
	rollback_window = RollbackWindow(element, hou.ui.mainQtWindow())
	rollback_window.finished.connect(rollback_shot)


def rollback_shot_go():
	scene_name = hou.hipFile.name()
	shot = os.path.basename(scene_name)
	index = shot.find('_lighting')
	if index > 0:
		base_name = shot[:index]
		department = Department.LIGHTING
	else:
		index = shot.find('_fx')
		if index > 0:
			base_name = shot[:index]
			department = Department.FX
		else:
			# If there is no shot opened then we allow the user to select one from all of the comps.
			global rollback_selection_window
			rollback_selection_window = SelectionWindow(hou.ui.mainQtWindow(), dept_list=[Department.LIGHTING, Department.FX])
			rollback_selection_window.finished.connect(post_selection)
			return
	print base_name
	project = Project()
	body = project.get_body(base_name)
	element = body.get_element(department)

	global rollback_window
	rollback_window = RollbackWindow(element, hou.ui.mainQtWindow())
	rollback_window.finished.connect(rollback_shot)

def rollback_asset_go(node=None):
	global rollback_window
	global asset_name
	global src

	if node is None:
		nodes = hou.selectedNodes()
		if len(nodes) == 1:
			node = nodes[0]
		elif len(nodes) > 1:
			message_gui.error('Please select only one node to rollback')
			return
		elif len(nodes) < 1:
			message_gui.error('Please select a node to rollback')
			return

	project = Project()
	src = node.type().definition().libraryFilePath()
	asset_name = os.path.basename(src)



	base_name=node.type().name()
	print base_name

	index = asset_name.find('_assembly')

	base_name=base_name.replace('_main1','')
	print base_name
	#if index > 0:
	#	base_name = asset_name[:index]
	##	message_gui.error('There was a problem finding the asset')
	#	return
	#print '--------'
	#print base_name

	body = None
	element=None

	if  node.name() in Department.ASSET_DEPTS:
		base_name=base_name.replace('_'+str(node.name()),'')
		body=project.get_body(base_name)
		element = body.get_element(str(node.name()))

	else:
		body = project.get_body(base_name.replace('_main',''))
		element = body.get_element(Department.ASSEMBLY)



	rollback_window = RollbackWindow(element, hou.ui.mainQtWindow())
	rollback_window.finished.connect(rollback_hda)

def rollback_tool_go(node=None):
	global rollback_window
	global asset_name
	global src

	if node is None:
		nodes = hou.selectedNodes()
		if len(nodes) == 1:
			node = nodes[0]
		elif len(nodes) > 1:
			message_gui.error('Please select only one node to rollback')
			return
		elif len(nodes) < 1:
			message_gui.error('Please select a node to rollback')
			return

	project = Project()
	src = node.type().definition().libraryFilePath()
	asset_name = os.path.basename(src)
	index = asset_name.find('_hda')
	if index > 0:
		base_name = asset_name[:index]
	else:
		message_gui.error('There was a problem finding the tool')
		return
	body = project.get_body(base_name)
	element = body.get_element(Department.HDA)
	rollback_window = RollbackWindow(element, hou.ui.mainQtWindow())
	rollback_window.finished.connect(rollback_hda)
