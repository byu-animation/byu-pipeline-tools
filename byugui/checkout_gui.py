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
from byuam.environment import Department, Environment


WINDOW_WIDTH = 650
WINDOW_HEIGHT = 600

class CheckoutWindow(QtWidgets.QWidget):

	finished = QtCore.Signal()

	def __init__(self, parent, dept_list=Department.ALL):
		super(CheckoutWindow, self).__init__()
		self.parent = parent
		self.project = Project()
		self.environment = Environment()
		self.initUI(dept_list)

	def initUI(self, dept_list):
		#define gui elements
		self.resize(WINDOW_WIDTH,WINDOW_HEIGHT)
		self.setWindowTitle('Checkout')
		self.dept_tabs = QtWidgets.QTabWidget()
		self.dept_list = dept_list
		self.result = None

		#create checkbox to show only published assets
		self.show_published = QtWidgets.QCheckBox("Display only assets or shots with previous publishes")
		self.show_published.setCheckState(QtCore.Qt.Unchecked)
		self.show_published.stateChanged.connect(self.changeBodyCheckoutVisibility)

		#create Tabs
		self.createTabs()

		#create buttons
		self.checkout_button = QtWidgets.QPushButton('Checkout')
		self.checkout_button.clicked.connect(self.checkout)
		self.cancel_button = QtWidgets.QPushButton('Cancel')
		self.cancel_button.clicked.connect(self.close)

		#create button layout
		button_layout = QtWidgets.QHBoxLayout()
		button_layout.addWidget(self.checkout_button)
		button_layout.addWidget(self.cancel_button)

		self.img = QtWidgets.QLabel()
		banner_path = os.path.join(os.environ['BYU_TOOLS_DIR'], 'byugui', 'assets', 'images', 'film-banner.jpg')
		pixmap = QtGui.QPixmap(banner_path)
		scaled = pixmap.scaledToWidth(self.size().width())
		self.img.setPixmap(scaled)

		#create main layout
		main_layout = QtWidgets.QVBoxLayout()
		self.setLayout(main_layout)
		main_layout.addWidget(self.img)
		main_layout.setSpacing(5)
		# main_layout.setMargin(6)
		main_layout.addWidget(self.dept_tabs)
		main_layout.addWidget(self.show_published)
		main_layout.addLayout(button_layout)

		self.show()

	#Recursivly goes through the asset's file name
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

	def createTabs(self):
		#remember the current index so that we can restore it when we create the tabs
		currIndex = self.dept_tabs.currentIndex()
		#clear out the old tabs
		self.dept_tabs.clear()
		#create tabs
		for dept in self.dept_list:
			tab = DepartmentTab(self)
			self.dept_tabs.addTab(tab, dept)
			tab_layout = QtWidgets.QHBoxLayout()
			element_list = QtWidgets.QTreeWidget()
			element_list.setColumnCount(1)
			commentBox = QtWidgets.QTextEdit()
			commentBox.setReadOnly(False)
			tab.commentBox = commentBox

			if dept in Department.ASSET_DEPTS:
				for asset in self.project.list_assets():
					#print(asset)
					if not self.show_published.isChecked() or self.hasPreviousPublish(asset, dept):
						asset_array = asset.split("_")
						firstelement = element_list.findItems(asset_array[0], 0, 0)
						if not firstelement:
							item = QtWidgets.QTreeWidgetItem(asset_array[0])
							item.setText(0,asset_array[0])
							item.setTextColor(0,"#d0d0d0")
							font = QtGui.QFont()
							font.setPointSize(11)
							font.setBold(True)
							item.setFont(0,font)
							self.recurseTree(item, asset_array[1:],asset)
							element_list.insertTopLevelItem(0,item)
						else:
							self.recurseTree(firstelement[0], asset_array[1:],asset)
						element_list.currentItemChanged.connect(self.set_current_item)
			elif dept in Department.SHOT_DEPTS:
				for shot in self.project.list_shots():
					#print(shot)
					if not self.show_published.isChecked() or self.hasPreviousPublish(shot, dept):
						shot_array = shot.split("_")
						firstelement = element_list.findItems(shot_array[0], 0, 0)
						if not firstelement:
							item = QtWidgets.QTreeWidgetItem(shot_array[0])
							item.setText(0,shot_array[0])
							item.setTextColor(0,"#d0d0d0")
							font = QtGui.QFont()
							font.setPointSize(11)
							font.setBold(True)
							item.setFont(0,font)
							self.recurseTree(item, shot_array[1:],shot)
							element_list.insertTopLevelItem(0,item)
						else:
							self.recurseTree(firstelement[0], shot_array[1:],shot)
						element_list.currentItemChanged.connect(self.set_current_item)
			elif dept in Department.CROWD_DEPTS:
				for crowdCycle in self.project.list_crowd_cycles():
					if not self.show_published.isChecked() or self.hasPreviousPublish(crowdCycle, dept):
						crowdCycle_array = crowdCycle.split("_")
						firstelement = element_list.findItems(crowdCycle_array[0], 0, 0)
						if not firstelement:
							item = QtWidgets.QTreeWidgetItem(crowdCycle_array[0])
							item.setText(0,crowdCycle_array[0])
							item.setTextColor(0,"#d0d0d0")
							font = QtGui.QFont()
							font.setPointSize(11)
							font.setBold(True)
							item.setFont(0,font)
							self.recurseTree(item, crowdCycle_array[1:],crowdCycle)
							element_list.insertTopLevelItem(0,item)
						else:
							self.recurseTree(firstelement[0], crowdCycle_array[1:],crowdCycle)
						element_list.currentItemChanged.connect(self.set_current_item)
			tab_layout.addWidget(element_list)
			tab_layout.addWidget(commentBox)
			tab.setLayout(tab_layout)

		#restore the previous index
		self.dept_tabs.setCurrentIndex(currIndex)


	def hasPreviousPublish(self, body, department):
		asset_obj = self.project.get_body(body)
		element_obj = asset_obj.get_element(department)
		last_publish = element_obj.get_last_publish()
		if last_publish is None:
			return False
		return True

	def changeBodyCheckoutVisibility(self):
		#recreate tabs the with the new check option
		self.createTabs()

	def set_current_item(self, index):
		current_dept = self.dept_list[self.dept_tabs.currentIndex()]
		if current_dept in Department.ASSET_DEPTS:
			self.current_item = str(index.text(1))
		elif current_dept in Department.SHOT_DEPTS:
			self.current_item = str(index.text(1))
		elif current_dept in Department.CROWD_DEPTS:
			self.current_item = str(index.text(1))
			#TODO what the heck? Why do we have three identical results from three different conditions? What are we trying to accomplish here? Admitadly the last one I added just following the crowd.

		asset_obj = self.project.get_body(self.current_item)
		element_obj = asset_obj.get_element(current_dept)
		last_publish = element_obj.get_last_publish()
		last_publish_comment = None
		if last_publish is not None:
			last_publish_comment = "Last published {0} by {1} \n \"{2}\"".format(last_publish[1], last_publish[0], last_publish[2])
		else:
			last_publish_comment = "No publishes for this element"
		currentTab = self.dept_tabs.currentWidget()
		currentTab.commentBox.setText(last_publish_comment)

	def checkout(self):
		"""
		Checks out the currently selected item
		:return:
		"""
		current_user = self.environment.get_current_username()
		current_dept = self.dept_list[self.dept_tabs.currentIndex()]
		asset_obj = self.project.get_body(self.current_item)
		element_obj = asset_obj.get_element(current_dept)
		element_path = element_obj.checkout(current_user)
		if element_path != None:
			self.result = element_path
			self.close()


	def closeEvent(self, event):
		self.finished.emit()
		event.accept()

class DepartmentTab(QtWidgets.QWidget):
	def __init__(self, parent):
		super(DepartmentTab, self).__init__()
		self.parent = parent
		self.commentBox = None

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	ex = CheckoutWindow(app)
	sys.exit(app.exec_())
