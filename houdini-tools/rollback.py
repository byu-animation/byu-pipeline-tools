#Author: Trevor Barrus
import hou
import os
from PySide2 import QtGui, QtWidgets, QtCore
from byugui import RollbackWindow

from byuam import Project, Department, Environment

def rollback_hda():
	filepath = rollback_window.result
	if filepath is not None:
		environment = Environment()
		hou.hda.uninstallFile(src, change_oplibraries_file=False)
		dst = os.path.join(environment.get_hda_dir(), asset_name)
		hou.hda.installFile(dst)
		hou.ui.displayMessage("Rollback successful")

def rollback_shot():
	filepath = rollback_window.result
	if filepath is not None:
		hou.hipFile.load(filepath)
		hou.ui.displayMessage("Rollback successful")

def rollback_shot_go():
	scene_name = hou.hipFile.name()
	shot = os.path.basename(scene_name)
	index = shot.find("_lighting")
	if index > 0:
		base_name = shot[:index]
	print base_name
	body = project.get_body(base_name)
	element = body.get_element(Department.LIGHTING)
	rollback_window = RollbackWindow(element, hou.ui.mainQtWindow())
	rollback_window.finished.connect(rollback_shot)

def rollback_asset_go():
	global rollback_window
	global asset_name
	global src

	nodes = hou.selectedNodes()
	project = Project()
	if len(nodes) == 1:
		asset = nodes[0]
		src = asset.type().definition().libraryFilePath()
		asset_name = os.path.basename(src)
		index = asset_name.find("_assembly")
		if index > 0:
			base_name = asset_name[:index]
		else:
			error_gui.error("There was a problem finding the asset")
			return
		body = project.get_body(base_name)
		element = body.get_element(Department.ASSEMBLY)
		rollback_window = RollbackWindow(element, hou.ui.mainQtWindow())
		rollback_window.finished.connect(rollback_hda)
	elif len(node) > 1:
		error_gui.error('Please select only one node to rollback')
	elif len(node) < 1:
		error_gui.error('Please select a node to rollback')

def rollback_tool_go():
	global rollback_window
	global asset_name
	global src

	nodes = hou.selectedNodes()
	project = Project()
	if len(nodes) == 1:
		asset = nodes[0]
		src = asset.type().definition().libraryFilePath()
		asset_name = os.path.basename(src)
		index = asset_name.find("_hda")
		if index > 0:
			base_name = asset_name[:index]
		else:
			error_gui.error("There was a problem finding the tool")
			return
		body = project.get_body(base_name)
		element = body.get_element(Department.HDA)
		rollback_window = RollbackWindow(element, hou.ui.mainQtWindow())
		rollback_window.finished.connect(rollback_hda)
	elif len(node) > 1:
		error_gui.error('Please select only one node to rollback')
	elif len(node) < 1:
		error_gui.error('Please select a node to rollback')
