import hou
import os

from PySide2 import QtGui, QtWidgets, QtCore

from byuam import Department, Project, Environment
from byugui.assemble_gui import AssembleWindow
from byuam.body import AssetType
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

	if not hda.canCreateDigitalAsset():
		if hda.type().definition is not None:
			# we are dealing with an premade hda
			result = message_gui.yes_or_no("The selected node is already a digial asset. Would you like to copy the definition into the pipeline")
			if not result:
				return
			#TODO handle premade hdas here
			copyHDA = True
		else:
			message_gui.error('You can\'t make a digital asset from the selected node')
			return

	project = Project()
	environment = Environment()
	username = project.get_current_username()
	tool = project.get_tool(tool_name)
	hda_element = tool.get_element(Department.HDA)

	checkout_file = hda_element.checkout(username)

	operatorName = hda_element.get_short_name()
	operatorLabel = (project.get_name() + ' ' + tool.get_name()).title()
	saveToLibrary = checkout_file

	num_inputs = len(hda.inputs())

	if copyHDA:
		parent = hda.parent()

		subnet = parent.createNode("subnet")

		hda_node = subnet.createDigitalAsset(name=operatorName, description=operatorLabel, hda_file_name=saveToLibrary, min_num_inputs=num_inputs)

		hou.copyNodesTo(hda.children(), hda_node)
		hda_nodeDef = hda_node.type().definition()
		hdaDef = hda.type().definition()

		#Copy over sections
		#TODO copy over sections
		sects = hdaDef.sections()
		for sectName in sects:
			print "Copying over section: " + str(sectName)
			hda_nodeDef.addSection(sectName, sects[sectName].contents())

		# Copy over paramters
		oldParms = hdaDef.parmTemplateGroup()
		hda_nodeDef.setParmTemplateGroup(oldParms)
	else:
		try:
			hda_node = hda.createDigitalAsset(name=operatorName, description=operatorLabel, hda_file_name=saveToLibrary, min_num_inputs=num_inputs)
		except hou.OperationFailed, e:
			print message_gui.error(str(e))
			return

	assetTypeDef = hda_node.type().definition()
	assetTypeDef.setIcon(environment.get_project_dir() + '/byu-pipeline-tools/assets/images/icons/hda-icon.png')
	if not copyHDA:
		nodeParms = hda_node.parmTemplateGroup()
		assetTypeDef.setParmTemplateGroup(nodeParms)
	hda_node.setSelected(True)
