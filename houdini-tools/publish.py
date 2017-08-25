#Author: Trevor Barrus and Ben DeMann
import hou
import os
from PySide2 import QtGui, QtWidgets, QtCore
from byugui import PublishWindow, message_gui

from byuam import Department, Project, Element, Environment

def publish_hda():
	project = Project()
	environment = Environment()

	if publish_window.published:
		user = publish_window.user
		comment = publish_window.comment

		if hda_name in project.list_assets():
			body = project.get_asset(hda_name)
			department = Department.ASSEMBLY
			element_type = "assembly"
		elif hda_name in project.list_tools():
			body = project.get_tool(hda_name)
			department = Department.HDA
			element_type = "hda"

		if os.path.exists(src):
			if body is not None:
				if Element.DEFAULT_NAME in body.list_elements(department):
					#save node definition
					asset.type().definition().updateFromNode(asset)
					asset.matchCurrentDefinition()
					element = body.get_element(department, Element.DEFAULT_NAME)
					dst = element.publish(user, src, comment)
					#Ensure file has correct permissions
					try:
						os.chmod(dst, 0660)
					except:
						pass
					hou.hda.uninstallFile(src, change_oplibraries_file=False)
					saveFile = hda_name + "_" + element_type + "_main.hdanc"
					dst = os.path.join(environment.get_hda_dir(), saveFile)
					hou.hda.installFile(dst)
		else:
			message_gui.error("File does not exist")

def publish_shot():
	element = publish_window.result

	if publish_window.published:
		hou.hipFile.save()

		#Publish
		user = publish_window.user
		src = publish_window.src
		comment = publish_window.comment
		element.publish(user, src, comment)

def publish_hda_go(hda=None, departments=[Department.ASSEMBLY]):
	global publish_window
	global asset
	global hda_name
	global src

	if hda is None:
		nodes = hou.selectedNodes()
		if len(nodes) == 1:
			hda = nodes[0]
		elif len(nodes) > 1:
			message_gui.error("Please select only one node.")
			return
		else:
			message_gui.error("Please select a node.")
			return

	if hda.type().definition() is not None:
		asset = hda
		hda_name = asset.type().name() #get name of asset
		index = hda_name.find("_main")
		if index > 0:
			hda_name = hda_name[:index]
		src = asset.type().definition().libraryFilePath()
		publish_window = PublishWindow(src, hou.ui.mainQtWindow(), departments)
	else:
		message_gui.error("The selected node is not a digital asset")
		return
	publish_window.finished.connect(publish_hda)

def publish_tool_go(node=None):
	publish_hda_go(hda=node, departments=[Department.HDA])

def publish_asset_go(node=None):
	publish_hda_go(hda=node, departments=[Department.ASSEMBLY])

def publish_shot_go():
	global publish_window

	scene = hou.hipFile.name()
	print scene
	publish_window = PublishWindow(scene, hou.ui.mainQtWindow(), [Department.LIGHTING, Department.FX])
	publish_window.finished.connect(publish_shot)
