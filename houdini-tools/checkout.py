from __future__ import print_function
# Author: Trevor Barrus
import hou
import os
from PySide2 import QtGui, QtWidgets, QtCore
from byugui import CheckoutWindow, message_gui

from byuam import Department, Project, Environment, Element

def checkout_shot():
	filepath = checkout_window.result
	if filepath is not None:
		if not os.path.exists(filepath):
			print('Filepath doesn\'t exist')
			filepath += '.hipnc'
			hou.hipFile.clear()
			hou.hipFile.setName(filepath)
			hou.hipFile.save()
		else:
			hou.hipFile.load(filepath)

def checkout_hda(hda, project, environment):
	'''
	hda - an hda to checkout
	Returns the element_path if the checkout was successful. Otherwise return None
	'''
	#if node is digital asset
	if hda.type().definition() is not None:
		asset_name = hda.type().name() #get name of hda
		index = asset_name.rfind('_')
		department_name = asset_name[index+1:]
		# Our old assets have "_main" at the end. We want them to refer to the "assembly" department.
		department_name = "assembly" if department_name == "main" else department_name
		asset_name = asset_name[:index]
		src = hda.type().definition().libraryFilePath()
		current_user = environment.get_current_username()

		if asset_name in project.list_assets():
			body = project.get_asset(asset_name)
		elif asset_name in project.list_tools():
			body = project.get_tool(asset_name)
		else:
			message_gui.error('We could not find ' + asset_name + ' in the list of things you can checkout.')

		if department_name not in Department.ALL:
			message_gui.error(department_name + ' is not a valid Department')
			return None

		if os.path.exists(src):
			if body is not None:
				if Element.DEFAULT_NAME in body.list_elements(department_name):
					element = body.get_element(department_name, Element.DEFAULT_NAME)
				elif Element.DEFAULT_NAME in body.list_elements(Department.HDA):
					element = body.get_element(Department.HDA, Element.DEFAULT_NAME)
				else:
					message_gui.error('There was a problem checking out the selected hda', details='The body for this HDA could not be found. This seems weird because we were able to find the asset_name in the list of assets. Right off the top of my head I don\'t know why it would do this. We\'ll have to take closer look.')
					return None
				element_path = element.checkout(current_user)
				hou.hda.installFile(element_path)
				definition = hou.hdaDefinition(hda.type().category(), hda.type().name(), element_path)
				definition.setPreferred(True)
				#hou.hda.uninstallFile(src, change_oplibraries_file=False)
				hda.allowEditingOfContents()
				aa = hda.parm("ri_auto_archive")
				if aa:
					aa.set("force")
				return element_path
	return None

def checkout_hda_go(hda=None):
	global checkout_window
	project = Project()
	environment = Environment()
	if hda is None:
		nodes = hou.selectedNodes()
		if len(nodes) == 1:
			hda = nodes[0]
		elif len(nodes) > 1:
			message_gui.error('Only one node can be selected for checkout')
			return
		else:
			message_gui.error('You need to select an asset node to checkout')
			return

	if hda.type().definition() is not None:
		result = checkout_hda(hda, project, environment)
		if result is not None:
			print('checkout successful')
			#I think having the node unlock is visual que enough that the checkout was fine. Mostly it's annoying to have the window there. And we have a window that will let them know if it didn't work.
			#message_gui.info('Checkout Successful!', title='Success!')
		else:
			message_gui.error('Checkout Failed', title='Failure :()')
	else:
		message_gui.error('Node is not a digital asset')
		return

def checkout_tool_go(node=None):
	checkout_hda_go(hda=node)

def checkout_asset_go(node=None):
	checkout_hda_go(hda=node)

def checkout_shot_go():
	global checkout_window
	project = Project()
	environment = Environment()

	checkout_window = CheckoutWindow(hou.ui.mainQtWindow(), [Department.LIGHTING, Department.FX])
	checkout_window.finished.connect(checkout_shot)
