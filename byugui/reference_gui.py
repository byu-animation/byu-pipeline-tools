#Author Trevor Barrus

import sys
import os
import operator
try:
	from PySide import QtGui as QtWidgets
	from PySide import QtCore
except ImportError:
	from PySide2 import QtWidgets, QtCore
from byuam.project import Project
from byuam.body import Asset, AssetType
from byuam.environment import Department

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

class ReferenceWindow(QtWidgets.QWidget):

	finished = QtCore.Signal()

	def __init__(self, parent, src, dept_list=Department.ALL):
		super(ReferenceWindow, self).__init__()
		self.project = Project()
		self.parent = parent
		self.src = src
		self.filePaths = []
		self.done = True
		self.reference = False
		self.initUI(dept_list)

	def initUI(self, dept_list):
		#define gui elements
		self.setGeometry(300,300,WINDOW_WIDTH,WINDOW_HEIGHT)
		self.setWindowTitle('Reference Manager')
		self.departmentMenu = QtWidgets.QComboBox()
		for i in dept_list:
			self.departmentMenu.addItem(i)
		self.departmentMenu.activated[str].connect(self.setElementType)

		self.assetList = AssetListWindow(self)
		for asset in self.project.list_assets():
			item = QtWidgets.QListWidgetItem(asset)
			self.assetList.addItem(item)

		self.typeFilterLabel = QtWidgets.QLabel("Type Filter")
		self.typeFilterLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.typeFilter = QtWidgets.QComboBox()
		self.typeFilter.addItem("all")
		for i in AssetType.ALL:
			self.typeFilter.addItem(i)

		self.typeFilter.currentIndexChanged.connect(self.setElementType)
		self.referenceButton = QtWidgets.QPushButton('Reference')
		self.referenceButton.clicked.connect(self.createReference)
		self.cancelButton = QtWidgets.QPushButton('Cancel')
		self.cancelButton.clicked.connect(self.close)

		#set gui layout
		self.grid = QtWidgets.QGridLayout(self)
		self.setLayout(self.grid)
		self.grid.addWidget(self.departmentMenu, 0, 0)
		self.grid.addWidget(self.assetList, 1, 0, 1, 0)
		self.grid.addWidget(self.typeFilterLabel, 2, 0)
		self.grid.addWidget(self.typeFilter, 2, 1)
		self.grid.addWidget(self.referenceButton, 3, 0)
		self.grid.addWidget(self.cancelButton, 3, 1)

		self.show()

	def setElementType(self, idx=0):
		department = str(self.departmentMenu.currentText())
		self.refreshList(department)

	def createReference(self):
		selected = []
		del self.filePaths[:]
		for item in self.assetList.selectedItems():
			body = self.project.get_body(str(item.text()))
			element = body.get_element(str(self.departmentMenu.currentText()))
			path = element.get_app_filepath()
			self.filePaths.append(path)
			selected.append(str(item.text()))
		checkout = self.project.get_checkout(os.path.dirname(self.src))
		if checkout is not None:
			body_name = checkout.get_body_name()
			body = self.project.get_body(body_name)
			for sel in selected:
				body.add_reference(sel)
		self.done = False
		self.reference = True
		self.close()

	def refreshList(self, department):
		if department in Department.ASSET_DEPTS:
			asset_filter = None
			if(self.typeFilter.currentIndex()):
				asset_filter_str = str(self.typeFilter.currentText())
				asset_filter = (Asset.TYPE, operator.eq, asset_filter_str)
			self.elements = self.project.list_assets(asset_filter)
		elif department in Department.CROWD_DEPTS:
			self.elements = self.project.list_crowd_cycles()
		else:
			self.elements = self.project.list_shots()

		self.assetList.clear()
		for e in self.elements:
			self.assetList.addItem(e)

	def closeEvent(self, event):
		self.finished.emit()
		event.accept()

class AssetListWindow(QtWidgets.QListWidget):
	def __init__(self, parent):
		super(AssetListWindow, self).__init__()
		self.parent = parent
		self.current_selection = None
		self.project = Project()
		self.initUI()

	def initUI(self):
		self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)


if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	ex = ReferenceWindow(app, None)
	sys.exit(app.exec_())
