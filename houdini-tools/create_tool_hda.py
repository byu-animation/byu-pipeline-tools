import hou
import os

from PySide2 import QtGui, QtWidgets, QtCore

from byuam import Department, Project, Environment
from byugui.assemble_gui import AssembleWindow
from byuam.environment import AssetType
from byugui import message_gui
import checkout

def go(node=None):
	global create_window
	global hda
	hda = node

	if hda is None:
		selection = hou.selectedNodes()
		if len(selection) > 1:
			message_gui.error('Please select only one node')
			return
		elif len(selection) < 1:
			message_gui.error('Please select a node')
			return
		hda = selection[0]

	create_window = AssembleWindow(hou.ui.mainQtWindow(), [Department.HDA])
	create_window.finished.connect(create_hda)

def create_hda():

	tool_name = create_window.result

	if tool_name is None:
		return

	if not node.canCreateDigitalAsset():
		message_gui.error('You can\'t make a digital asset from the selected node')
		return

	project = Project()
	environment = Environment()
	username = project.get_current_username()
	tool = project.get_tool(tool_name)
	hda = tool.get_element(Department.HDA)

	checkout_file = hda.checkout(username)

	operatorName = hda.get_short_name()
	operatorLabel = (project.get_name() + ' ' + tool.get_name()).title()
	saveToLibrary = checkout_file

	num_inputs = len(node.inputs())

	try:
		hda_node = node.createDigitalAsset(name=operatorName, description=operatorLabel, hda_file_name=saveToLibrary, min_num_inputs=num_inputs)
	except hou.OperationFailed, e:
		print message_gui.error(str(e))
		return

	assetTypeDef = hda_node.type().definition()
	assetTypeDef.setIcon(environment.get_project_dir() + '/byu-pipeline-tools/assets/images/icons/hda-icon.png')
