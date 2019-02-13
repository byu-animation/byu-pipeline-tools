# Author: Trevor Barrus

import sys
import os
import traceback
try:
	from PySide import QtGui as QtWidgets
	from PySide import QtGui as QtGui
	from PySide import QtCore
except ImportError:
	from PySide2 import QtWidgets, QtGui, QtCore
from byuam.project import Project
from byuam.environment import Environment, Department, Status
import message_gui

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

class PublishWindow(QtWidgets.QWidget):

	finished = QtCore.Signal()

	def __init__(self, src, parent, dept_list=Department.ALL):
		super(PublishWindow, self).__init__()
		self.environment = Environment()
		self.project = Project()
		self.eList = ElementList(self)
		self.parent = parent
		self.src = src
		self.result = None
		self.elementType = None
		self.initUI(dept_list)
		self.published = False

	def initUI(self, dept_list):
		#load checkout information
		src_dir = os.path.dirname(self.src)
		checkout_element = self.project.get_checkout_element(src_dir)
		checkout_dept = None
		checkout_body_name = None
		if checkout_element is not None:
			checkout_dept = checkout_element.get_department()
			checkout_body_name = checkout_element.get_parent()

		#define gui elements
		self.setGeometry(300,300,WINDOW_WIDTH,WINDOW_HEIGHT)
		self.setWindowTitle('Publish')
		self.menu = QtWidgets.QComboBox()
		self.menu.addItem('Asset')
		self.menu.addItem('Shot')
		self.departmentMenu = QtWidgets.QComboBox()
		checkout_idx = -1
		for i, dept in enumerate(dept_list):
			self.departmentMenu.addItem(dept)
			if dept==checkout_dept:
				checkout_idx = i

		self.departmentMenu.activated[str].connect(self.setElementType)
		self.filePath = QtWidgets.QLineEdit()
		self.filePath.setReadOnly(True)
		self.label = QtWidgets.QLabel('What did you change?')
		self.comment = QtWidgets.QTextEdit()
		self.lastPublish = QtWidgets.QTextEdit()
		self.lastPublish.setReadOnly(True)
		self.publishBtn = QtWidgets.QPushButton('Publish')
		self.publishBtn.setEnabled(False)

		self.eList.currentItemChanged.connect(self.selectElement)
		self.publishBtn.clicked.connect(self.publish)

		if checkout_idx>-1:
			self.departmentMenu.setCurrentIndex(checkout_idx)
		self.setElementType()
		self.eList.setElement(checkout_body_name)

		self.clearHistoryCheckbox = QtWidgets.QCheckBox('Freeze all transformations and clear all construction history')

		#set gui layout
		self.grid = QtWidgets.QGridLayout(self)
		self.setLayout(self.grid)
		self.grid.addWidget(self.departmentMenu, 0, 0)
		self.grid.addWidget(self.clearHistoryCheckbox, 0, 1)

		self.grid.addWidget(self.lastPublish, 1, 1)
		self.grid.addWidget(self.label, 2, 1)
		self.grid.addWidget(self.comment, 3, 1)

		self.grid.addWidget(self.eList, 1, 0, 3, 1)
		self.grid.addWidget(self.filePath, 4, 0)
		self.grid.addWidget(self.publishBtn, 4, 1)

		self.show()

	def setElementType(self):
		self.department = str(self.departmentMenu.currentText())
		if self.department in Department.ASSET_DEPTS:
			self.elementType = 'Asset'
		elif self.department in Department.SHOT_DEPTS:
			self.elementType = 'Shot'
		elif self.department in Department.TOOL_DEPTS:
			self.elementType = 'Tool'
		elif self.department in Department.CROWD_DEPTS:
			self.elementType = 'CrowdCycle'
		else:
			message_gui.error('There was an error loading the ' + str(self.department) + ' department')
		self.eList.refreshList(self.elementType)

	def selectElement(self):
		currentItem = self.eList.currentItem()
		print(currentItem)
		if currentItem is not None:
		   self.filePath.setText(self.eList.currentItem().text(1))
		   print("Current Item 0: " + self.eList.currentItem().text(0))
		   print("Current Item 1: " + self.eList.currentItem().text(1))
		   self.publishBtn.setEnabled(True)

		   current_dept = str(self.departmentMenu.currentText())
		   print("Current Department " + current_dept)

		   asset_obj = self.project.get_body(str(currentItem.text(1)))
		   element_obj = asset_obj.get_element(current_dept)
		   last_publish = element_obj.get_last_publish()
		   last_publish_comment = None
		   if last_publish is not None:
			  last_publish_comment = 'Last published {0} by {1} \n "{2}"'.format(last_publish[1], last_publish[0], last_publish[2])
		   else:
			  last_publish_comment = 'No publishes for this element'
		   self.lastPublish.setText(last_publish_comment)

	def publish(self):

		if str(self.comment.toPlainText()) == '':
			message_gui.error('Please add a publish comment.\nComments help to track the progress.')
			return


		self.elementType = str(self.menu.currentText())
		try:
			body = self.project.get_body(str(self.filePath.text()))
			element = body.get_element(str(self.departmentMenu.currentText()))

			self.user = self.environment.get_current_username()
			self.comment = str(self.comment.toPlainText())
			self.elementName = str(self.departmentMenu.currentText())
			self.result = element
			self.published = True
			self.close()
		except Exception, e:
			print e
			error = QtWidgets.QLineEdit()
			error.setText(str(e))
			self.grid.addWidget(error, 4, 1, 2, 1)
			traceback.print_stack()



	def closeEvent(self, event):
		self.finished.emit()
		event.accept()

class ElementList(QtWidgets.QTreeWidget):
	def __init__(self, parent):
		super(ElementList, self).__init__()
		self.parent = parent
		self.project = Project()
		self.elements = self.project.list_assets()
		self.initUI()

	def initUI(self):
		#define gui elements
		self.refreshList('Asset')

	def recurseTree(self, treeItem, array, asset):
		#This is for setting bottom level text attributes
		if len(array) == 0:
			treeItem.setText(1,asset)
			treeItem.setTextColor(0,"#3c83f9")
			font = QtGui.QFont()
			font.setPointSize(12)
			font.setBold(False)
			treeItem.setFont(0,font)
			return
		else: #This is for setting parent level text attributes and settin up the structure
			item = QtWidgets.QTreeWidgetItem(array[0])
			item.setText(0,array[0])
			item.setText(1,"This is not a file")
			item.setTextColor(0,"#d0d0d0")
			font = QtGui.QFont()
			font.setPointSize(11)
			font.setBold(True)
			item.setFont(0,font)
			skip = False
			# this is to check if the child already exists
			for i in range(0,treeItem.childCount()):
				if treeItem.child(i).text(0) == item.text(0):
					item = treeItem.child(i)
					skip = True
			if skip == False: # Executes if the child doesnt already exist
				treeItem.addChild(item)
			newArray = array[1:]
			self.recurseTree(item, newArray,asset)
		return

	#Update the list based on the input element type
	def refreshList(self, element):
		if element == 'Asset':
			self.elements = self.project.list_assets()
		elif element == 'Shot':
			self.elements = self.project.list_shots()
		elif element == 'Tool':
			self.elements = self.project.list_tools()
		elif element == 'CrowdCycle':
			self.elements = self.project.list_crowd_cycles()
		else:
			self.elements = list()
			message_gui.error('There was a problem loading in the elements from of ' + str(element)  + ' type.')
		self.clear()
		for e in self.elements:
			asset_array = e.split("_")
			firstelement = self.findItems(asset_array[0], 0, 0)
			if not firstelement:
				item = QtWidgets.QTreeWidgetItem(asset_array[0])
				item.setText(0,asset_array[0])
				item.setTextColor(0,"#d0d0d0")
				font = QtGui.QFont()
				font.setPointSize(11)
				font.setBold(True)
				item.setFont(0,font)
				self.recurseTree(item, asset_array[1:],e)
				self.insertTopLevelItem(0,item)
			else:
				self.recurseTree(firstelement[0], asset_array[1:],e)
			#self.addItem(e)

	def setElement(self, element):
		print(element)
		#for idx in xrange(self.count()):
			#eItem = self.item(idx)
			#if str(eItem.text())==element:
				#self.setCurrentRow(idx)
				#break


if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	test_path = os.path.join(os.environ['BYU_TOOLS_DIR'], 'byu_gui',  'test.txt')
	ex = PublishWindow(test_path, app)
	sys.exit(app.exec_())
