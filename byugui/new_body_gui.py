# Author: Trevor Barrus

import sys
import os
try:
	from PySide import QtGui as QtWidgets
	from PySide import QtGui as QtGui
	from PySide import QtCore
except ImportError:
	from PySide2 import QtWidgets, QtGui, QtCore
from byuam.project import Project
from byuam.body import AssetType
from byuam.body_list import NameList
from byugui import message_gui

WINDOW_WIDTH = 300
WINDOW_HEIGHT = 200

class CreateWindow(QtWidgets.QTabWidget):

	finished = QtCore.Signal()

	ASSET_INDEX = 0
	SHOT_INDEX = 1
	TOOL_INDEX = 2
	CROWD_INDEX = 3

	def __init__(self, parent):
		super(CreateWindow, self).__init__()
		self.parent = parent
		self.initUI()

	def initUI(self):
		#define gui elements
		self.setGeometry(300,300,WINDOW_WIDTH,WINDOW_HEIGHT)
		self.setWindowTitle('Create New Body')

		#create tabs
		assetTab = NewBodyWindow('asset', self)
		shotTab = NewBodyWindow('shot', self)
		toolsTab = NewBodyWindow('tool', self)
		crowdTab = NewBodyWindow('crowd cycle', self)

		self.insertTab(self.ASSET_INDEX, assetTab, 'Asset')
		self.insertTab(self.SHOT_INDEX, shotTab, 'Shot')
		self.insertTab(self.TOOL_INDEX, toolsTab, 'Tool')
		self.insertTab(self.CROWD_INDEX, crowdTab, 'Crowd Cycle')

		self.show()

	def accept(self):
		self.finished.emit()
		self.close()


class NewBodyWindow(QtWidgets.QWidget):
	def __init__(self, element, parent):
		super(NewBodyWindow, self).__init__()
		self.parent = parent
		self.element = element
		self.initUI()

	def initUI(self):
		#define gui elements

		#this is a test
		list_path = os.path.join(os.environ['BYU_TOOLS_DIR'], 'byugui', 'assets', 'Asset_Category_List.json')
		self.body_categories = NameList().loadList(list_path)
		print(self.body_categories)

		self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
		self.categories = QtWidgets.QComboBox() #Main category
		self.categories.setDuplicatesEnabled(False)
		self.categories_2 = QtWidgets.QComboBox() #sub category 1
		self.categories_2.setDuplicatesEnabled(False)
		self.categories_3 = QtWidgets.QComboBox() #sub category 2
		self.categories_3.setDuplicatesEnabled(False)

		for bc in self.body_categories:
			self.categories.addItem(bc.strip('_'))
			print(bc)

		self.categories.activated[str].connect(self.setCategory1)
		self.categories_2.activated[str].connect(self.setCategory2)
		self.categories_3.activated[str].connect(self.setCategory3)

		self.label = QtWidgets.QLabel('Enter the %s name' % self.element)
		self.textField = QtWidgets.QLineEdit()
		self.okBtn = QtWidgets.QPushButton('Ok')
		self.okBtn.clicked.connect(self.createBodyHandler)
		self.cancelBtn = QtWidgets.QPushButton('Cancel')
		self.cancelBtn.clicked.connect(self.parent.close)
		#set image
		self.img = QtWidgets.QLabel()
		image_path = os.path.join(os.environ['BYU_TOOLS_DIR'], 'byugui', 'assets', 'images', 'film-banner.jpg')
		pixmap = QtGui.QPixmap(image_path)
		scaled = pixmap.scaledToWidth(self.size().width()/3)
		self.img.setPixmap(scaled)
		self.setCategory1()
		self.setCategory2()
		self.setCategory3()
		#set gui layout
		grid = QtWidgets.QGridLayout(self)
		self.setLayout(grid)
		grid.addWidget(self.img,0, 1,3,3)
		grid.addWidget(self.categories, 0 ,0)
		grid.addWidget(self.categories_2, 1, 0)
		grid.addWidget(self.categories_3, 2, 0)
		grid.addWidget(self.label, 3, 1, 1)
		grid.addWidget(self.textField, 4, 0, 1, 3)
		grid.addWidget(self.okBtn, 5, 1)
		grid.addWidget(self.cancelBtn, 5, 2)

	#generate directories
	def createBodyHandler(self):
		try:
			name = ""
			has_prefix = False
			if not self.categories_2.currentText() == '':
				has_prefix = True
				name = str(self.categories.currentText())
			if not self.categories_2.currentText() == '':
				has_prefix = True
				name += "_" + str(self.categories_2.currentText())
			if not self.categories_3.currentText() =='':
				has_prefix = True
				name += "_" + str(self.categories_3.currentText())
			if not self.textField.text() == "" and has_prefix == True:
				name += '_'
			name += str(self.textField.text())
			name = name.replace(' ', '_')
			createBody(self.element, name)
			self.parent.accept()
		except EnvironmentError, e:
			message_gui.error('There is already an crowd cycle with that name.', details=e)
			print e
			self.parent.accept()

	def keyPressEvent(self, event):
		key = event.key()
		if key == QtCore.Qt.Key_Return:
			self.createBodyHandler()

	def setCategory1(self):
		selection = self.body_categories[self.categories.currentText()]
		self.categories_2.clear()
		self.categories_3.clear()
		if isinstance(selection, dict):
			for name in selection:
				if not self.dropDownContains(self.categories_2, name):
					self.categories_2.addItem(name)
			self.setCategory2()

	def setCategory2(self):
		selection = self.body_categories[self.categories.currentText()]
		selection2 =""
		if isinstance(selection, dict):
			selection2 = selection[self.categories_2.currentText()]
		self.categories_3.clear()
		if isinstance(selection2, dict):
			for name in selection2:
				if not self.dropDownContains(self.categories_3, name):
					self.categories_3.addItem(name)

	def setCategory3(self):
		return None

	def dropDownContains(self, drop_down, value):
		for i in range(drop_down.count()):
			if drop_down.itemText(i) == value:
				return True
		return False

def createBody(bodyType, name):
	project = Project()
	if bodyType == 'asset':

		msgBox = QtWidgets.QMessageBox()
		msgBox.setText(msgBox.tr("What type of asset is this?"))
		# noButton = msgBox.addButton(QtWidgets.QMessageBox.No)
		# yesButton = msgBox.addButton(QtWidgets.QMessageBox.Yes)
		cancelButton = msgBox.addButton(QtWidgets.QMessageBox.Cancel)
		setButton = msgBox.addButton(msgBox.tr("Set"), QtWidgets.QMessageBox.YesRole)
		propButton = msgBox.addButton(msgBox.tr("Prop"), QtWidgets.QMessageBox.YesRole)
		characterButton = msgBox.addButton(msgBox.tr("Character"), QtWidgets.QMessageBox.YesRole)
		accessoryButton = msgBox.addButton(msgBox.tr("Accessory"), QtWidgets.QMessageBox.YesRole)

		msgBox.exec_()

		if msgBox.clickedButton() == propButton:
			asset_type = AssetType.PROP
		elif msgBox.clickedButton() == characterButton:
			asset_type = AssetType.CHARACTER
		elif msgBox.clickedButton() == setButton:
			asset_type = AssetType.SET
		elif msgBox.clickedButton() == accessoryButton:
			asset_type = AssetType.ACCESSORY

		print asset_type + " is the asset type"
		asset = project.create_asset(name, asset_type)
	elif bodyType == 'shot':
		shot = project.create_shot(name)
	elif bodyType == 'tool':
		tool = project.create_tool(name)
	elif bodyType == 'crowd cycle':
		cycle = project.create_crowd_cycle(name)
	else:
		message_gui.error(bodyType + " is not a valid type!\nThis should not have happend. Please contact a Pipline Management Team member for help!\nTake a screenshot of this error and tell him/her that it came from new_body_gui.py")

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	ex = CreateWindow()
	sys.exit(app.exec_())
