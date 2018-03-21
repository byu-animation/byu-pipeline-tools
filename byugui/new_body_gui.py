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
		self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
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

		#set gui layout
		grid = QtWidgets.QGridLayout(self)
		self.setLayout(grid)
		grid.addWidget(self.img, 0, 0)
		grid.addWidget(self.label, 0, 1, 0, 2)
		grid.addWidget(self.textField, 1, 0, 1, 3)
		grid.addWidget(self.okBtn, 2, 1)
		grid.addWidget(self.cancelBtn, 2, 2)

	#generate directories
	def createBodyHandler(self):
		try:
			name = str(self.textField.text())
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
