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
		hdaName = selectedHDA.type().name()
        department = publishWindow.elementName
        body = project.get_body(hdaName.replace("_" + department, ""))

        if body is None:
            message_gui.error("Asset not found in pipe.")
            return

        if os.path.exists(src):
            try:
                #save node definition this is the same as the Save Node Type menu option. Just to make sure I remember how this works - We are getting the definition of the selected hda and calling the function on it passing in the selected hda. We are not calling the funciton on the selected hda.
                selectedHDA.type().definition().updateFromNode(selectedHDA)
            except hou.OperationFailed, e:
                message_gui.error('There was a problem publishing the HDA to the pipeline.\n', details=str(e))
                return
            try:
                selectedHDA.matchCurrentDefinition()
            except hou.OperationFailed, e:
                message_gui.warning('There was a problem while trying to match the current definition. It\'s not a critical problem but it is a little troubling. Take a look at it and see if you can resolve the problem. Rest assured that the publish did work though', details=str(e))
            element = body.get_element(department, Element.DEFAULT_NAME)
            dst = element.publish(user, src, comment)
            #Ensure file has correct permissions
            try:
                os.chmod(dst, 0660)
            except:
                pass
            saveFile = hdaName + '.hdanc'
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

def publish_hda_go(selectedHDA=None, departments=[Department.HDA, Department.ASSEMBLY, Department.MATERIAL, Department.HAIR, Department.CLOTH]):
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
	publish_hda_go(selectedHDA=node, departments=[Department.ASSEMBLY, Department.MATERIAL, Department.HAIR, Department.CLOTH])

def publish_shot_go():
	scene = hou.hipFile.name()
	print scene
	publishWindow = PublishWindow(scene, hou.ui.mainQtWindow(), [Department.LIGHTING, Department.FX])
	publishWindow.finished.connect(lambda *args: publish_shot(publishWindow))
