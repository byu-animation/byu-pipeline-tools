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
from byugui import message_gui

WINDOW_WIDTH = 300
WINDOW_HEIGHT = 200

class CreateWindow(QtWidgets.QTabWidget):

	finished = QtCore.Signal()

	ASSET_INDEX = 0
	SHOT_INDEX = 1
	TOOL_INDEX = 2

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

		self.insertTab(self.ASSET_INDEX, assetTab, 'Asset')
		self.insertTab(self.SHOT_INDEX, shotTab, 'Shot')
		self.insertTab(self.TOOL_INDEX, toolsTab, 'Tool')

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
		self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
		self.label = QtWidgets.QLabel('Enter the %s name' % self.element)
		self.textField = QtWidgets.QLineEdit()
		self.okBtn = QtWidgets.QPushButton('Ok')
		self.okBtn.clicked.connect(self.createBody)
		self.cancelBtn = QtWidgets.QPushButton('Cancel')
		self.cancelBtn.clicked.connect(self.parent.close)
		#set image
		self.img = QtWidgets.QLabel()
		pixmap = QtGui.QPixmap(os.environ['BYU_TOOLS_DIR'] + '/byugui/assets/images/film-banner.jpg')
		scaled = pixmap.scaledToWidth(self.size().width()/3)
		self.img.setPixmap(scaled)

		#set gui layout
		grid = QtWidgets.QGridLayout(self)
		self.setLayout(grid)
		grid.addWidget(self.img, 0, 0)
		grid.addWidget(self.label, 0, 1, 0, 2)
		grid.addWidget(self.textField, 1, 0, 1, 3)
		grid.addWidget(self.okBtn, 2, 1)
		grid.addWidget(self.cancelBtn, 2, 2)

	#generate directories
	def createBody(self):
		try:
			name = str(self.textField.text())
			name = name.replace(' ', '_')
			project = Project()
			if self.element == 'asset':

				msgBox = QtWidgets.QMessageBox()
				msgBox.setText(self.tr("What type of asset is this?"))
				# noButton = msgBox.addButton(QtWidgets.QMessageBox.No)
				# yesButton = msgBox.addButton(QtWidgets.QMessageBox.Yes)
				cancelButton = msgBox.addButton(QtWidgets.QMessageBox.Cancel)
				setButton = msgBox.addButton(self.tr("Set"), QtWidgets.QMessageBox.YesRole)
				propButton = msgBox.addButton(self.tr("Prop"), QtWidgets.QMessageBox.YesRole)
				characterButton = msgBox.addButton(self.tr("Character"), QtWidgets.QMessageBox.YesRole)
				accessoryButton = msgBox.addButton(self.tr("Accessory"), QtWidgets.QMessageBox.YesRole)

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
			elif self.element == 'shot':
				shot = project.create_shot(name)
			elif self.element == 'tool':
				tool = project.create_tool(name)
			else:
				message_gui.error(self.element + " is not a valid type!\nThis should not have happend. Please contact a Pipline Management Team member for help!\nTake a screenshot of this error and tell him/her that it came from new_body_gui.py")
			self.parent.accept()
		except EnvironmentError, e:
			print e
			self.parent.accept()

	def keyPressEvent(self, event):
		key = event.key()
		if key == QtCore.Qt.Key_Return:
			self.createBody()


if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	ex = CreateWindow()
	sys.exit(app.exec_())
