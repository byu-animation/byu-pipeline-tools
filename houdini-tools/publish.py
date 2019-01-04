#Author: Trevor Barrus and Ben DeMann
import hou
import os
from PySide2 import QtGui, QtWidgets, QtCore
from byugui import PublishWindow, message_gui

from byuam import Department, Project, Element, Environment

def publish_hda(publishWindow, selectedHDA, src):
	project = Project()
	environment = Environment()

	if publishWindow.published:
		user = publishWindow.user
		comment = publishWindow.comment

		# Get name of the selectedHDA
		hdaName = selectedHDA.type().name()
		index = hdaName.find('_main')
		if index > 0:
			hdaName = hdaName[:index]

		if hdaName in project.list_assets():
			body = project.get_asset(hdaName)
			department = Department.ASSEMBLY
			element_type = 'assembly'
		elif hdaName in project.list_tools():
			body = project.get_tool(hdaName)
			department = Department.HDA
			element_type = 'hda'
		else:
			message_gui.error('We couldn\'t find the selected asset in the pipeline.')
			return

		if os.path.exists(src):
			if body is not None:
				if Element.DEFAULT_NAME in body.list_elements(department):
					try:
						#save node definition this is the same as the Save Node Type menu option. Just to make sure I remember how this works - We are getting the definition of the selected hda and calling the function on it passing in the selected hda. We are not calling the funciton on the selected hda.
						selectedHDA.type().definition().updateFromNode(selectedHDA)
					except hou.OperationFailed, e:
						print 'There was a problem saving the node. This is a pretty serious problem. Because if it doesn\'t save then it\'s not in the pipe.'
						print str(e)
						message_gui.error('There was a problem publishing the HDA to the pipeline.\n', details=str(e))
						return
					try:
						selectedHDA.matchCurrentDefinition()
					except hou.OperationFailed, e:
						print str(e)
						#Here on the other hand we are just trying to match the current definition. If it doesn't do that it's not fatal. This is just for convience. We are currently having a lot of problem with unrecognized paramter warnings that are causing this to fail. But I can't figure out where they are coming from.
						message_gui.warning('There was a problem while trying to match the current definition. It\'s not a critical problem but it is a little troubling. Take a look at it and see if you can resolve the problem. Rest assured that the publish did work though', details=str(e))
					aa = selectedHDA.parm("ri_auto_archive")
					if aa:
						aa.set("exist")
					element = body.get_element(department, Element.DEFAULT_NAME)
					dst = element.publish(user, src, comment)
					#Ensure file has correct permissions
					try:
						os.chmod(dst, 0660)
					except:
						pass
					saveFile = hdaName + '_' + element_type + '_main.hdanc'
					dst = os.path.join(environment.get_hda_dir(), saveFile)
					hou.hda.installFile(dst)
					hou.hda.uninstallFile(src, change_oplibraries_file=False)
		else:
			message_gui.error('File does not exist', details=src)

def publish_shot(publishWindow):
	element = publishWindow.result

	if publishWindow.published:
		hou.hipFile.save()

		#Publish
		user = publishWindow.user
		src = publishWindow.src
		comment = publishWindow.comment
		element.publish(user, src, comment)

def publish_hda_go(selectedHDA=None, departments=[Department.ASSEMBLY]):
	if selectedHDA is None:
		nodes = hou.selectedNodes()
		if len(nodes) == 1:
			selectedHDA = nodes[0]
		elif len(nodes) > 1:
			message_gui.error('Please select only one node.')
			return
		else:
			message_gui.error('Please select a node.')
			return

	if selectedHDA.type().definition() is not None:
		src = selectedHDA.type().definition().libraryFilePath()
		publishWindow = PublishWindow(src, hou.ui.mainQtWindow(), departments)
	else:
		message_gui.error('The selected node is not a digital asset')
		return
	publishWindow.finished.connect(lambda *args: publish_hda(publishWindow, selectedHDA, src))

def publish_tool_go(node=None):
	publish_hda_go(selectedHDA=node, departments=[Department.HDA])

def publish_asset_go(node=None):
	publish_hda_go(selectedHDA=node, departments=[Department.ASSEMBLY])

def publish_shot_go():
	scene = hou.hipFile.name()
	print scene
	publishWindow = PublishWindow(scene, hou.ui.mainQtWindow(), [Department.LIGHTING, Department.FX])
	publishWindow.finished.connect(lambda *args: publish_shot(publishWindow))
