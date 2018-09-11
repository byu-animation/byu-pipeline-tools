import os
import mari
#import PySide.QtGui as QtGui
import sys
from byuam import Project

try:
	from PySide import QtGui as QtWidgets
	from PySide import QtGui as QtGui
	from PySide import QtCore
	print 'trying'
except ImportError:
	try:
		from PySide2 import QtWidgets, QtGui, QtCore
	except:
		print 'failed second import'



def init():
	toolbar = mari.app.findToolBar("BYU Tools")
	if toolbar is not None:
		label = QtGui.QLabel("BYU Tools")
		toolbar.addWidget(label)

init()

project = Project()

script_path = os.path.join(project.get_project_dir(), "byu-pipeline-tools", "mari-tools", "scripts")

sys.path.append(script_path)
