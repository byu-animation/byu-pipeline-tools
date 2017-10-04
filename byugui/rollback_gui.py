# Author: Trevor Barrus

import sys
import os
from os import listdir
try:
	from PySide import QtGui as QtWidgets
	from PySide import QtCore
except ImportError:
	from PySide2 import QtWidgets, QtCore
from byuam.project import Project
from byuam.environment import Environment
import message_gui

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 300

class RollbackWindow(QtWidgets.QWidget):

	finished = QtCore.Signal()

	def __init__(self, element, parent):
		super(RollbackWindow, self).__init__()
		if element is None:
			message_gui.error("Please checkout a shot to rollback.\n")
			return
		self.element = element
		self.parent = parent
		self.environment = Environment()
		self.project = Project()
		self.publishes = []
		self.result = None
		self.initUI()
		self.list_publishes()

	def initUI(self):
		#define gui elements
		self.setGeometry(300,300,WINDOW_WIDTH,WINDOW_HEIGHT)
		self.setWindowTitle('Rollback Manager')

		self.publish_list = QtWidgets.QListWidget()
		self.publish_list.currentItemChanged.connect(self.update_detail_view)
		self.infoLabel = QtWidgets.QLabel()

		self.rollbackButton = QtWidgets.QPushButton('Rollback')
		self.rollbackButton.clicked.connect(self.rollback)
		self.cancelButton = QtWidgets.QPushButton('Cancel')
		self.cancelButton.clicked.connect(self.close)

		#set gui layout
		self.grid = QtWidgets.QGridLayout(self)
		self.setLayout(self.grid)
		self.grid.addWidget(self.publish_list, 0, 0, 3, 1)
		self.grid.addWidget(self.infoLabel, 0, 1)
		self.grid.addWidget(self.rollbackButton, 3, 0)
		self.grid.addWidget(self.cancelButton, 3, 1)

		self.show()

	def list_publishes(self):
		publishes = self.element.list_publishes();
		for p in publishes:
			publish = Publish(p[0], p[1], p[2])
			self.publishes = self.publishes + [publish]
			item = QtWidgets.QListWidgetItem(publish.timestamp)
			self.publish_list.addItem(item)

	def update_detail_view(self):
		selectedVersion = self.publishes[self.publish_list.currentRow()]
		self.infoLabel.setText("Author: {0} \nTimestamp: {1} \n\nComment: {2}".format(selectedVersion.author, selectedVersion.timestamp, selectedVersion.comment))

	def rollback(self):
		selectedVersion = self.publishes[self.publish_list.currentRow()]
		versionDir = self.element.get_version_dir(self.publish_list.currentRow())
		versionFile = listdir(versionDir)[0]
		filepath = versionDir + '/' + versionFile
		user = self.environment.get_current_username()
		comment = "Rollback to version dated \n{0}".format(selectedVersion.timestamp)
		self.element.publish(user, filepath, comment)
		#checkout element again to user to remove errors upon multiple uses of rollback
		self.result = self.element.checkout(user)
		self.close()

	def closeEvent(self, event):
		self.finished.emit()
		event.accept()

class Publish:
	def __init__(self, author, timestamp, comment):
		self.author = author
		self.timestamp = timestamp
		self.comment = comment

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	ex = RollbackWindow(app)
	sys.exit(app.exec_())
