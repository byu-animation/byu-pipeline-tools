#Author: Trevor Barrus
import hou
import os
from PySide2 import QtGui, QtWidgets, QtCore
from byugui import RollbackWindow, message_gui

from byuam import Project, Department, Environment

def rollback_hda():
	filepath = rollback_window.result
	if filepath is not None:
		environment = Environment()
		hou.hda.uninstallFile(src, change_oplibraries_file=False)
		dst = os.path.join(environment.get_hda_dir(), asset_name)
		hou.hda.installFile(dst)
		message_gui.info("Rollback successful")

def rollback_shot():
	filepath = rollback_window.result
	if filepath is not None:
		hou.hipFile.load(filepath)
		message_gui.info("Rollback successful")

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

def rollback_asset_go(node=None):
	global rollback_window
	global asset_name
	global src

	if node is None:
		nodes = hou.selectedNodes()
		if len(nodes) == 1:
			node = nodes[0]
		elif len(node) > 1:
			message_gui.error('Please select only one node to rollback')
		elif len(node) < 1:
			message_gui.error('Please select a node to rollback')

	project = Project()
	src = node.type().definition().libraryFilePath()
	asset_name = os.path.basename(src)
	index = asset_name.find("_assembly")
	if index > 0:
		base_name = asset_name[:index]
	else:
		message_gui.error("There was a problem finding the asset")
		return
	body = project.get_body(base_name)
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
		elif len(node) > 1:
			message_gui.error('Please select only one node to rollback')
		elif len(node) < 1:
			message_gui.error('Please select a node to rollback')

	project = Project()
	src = node.type().definition().libraryFilePath()
	asset_name = os.path.basename(src)
	index = asset_name.find("_hda")
	if index > 0:
		base_name = asset_name[:index]
	else:
		message_gui.error("There was a problem finding the tool")
		return
	body = project.get_body(base_name)
	element = body.get_element(Department.HDA)
	rollback_window = RollbackWindow(element, hou.ui.mainQtWindow())
	rollback_window.finished.connect(rollback_hda)
