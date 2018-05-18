import hou
import os
from PySide2 import QtGui, QtWidgets, QtCore

from byuam import Department, Project, Environment
from byugui.assemble_gui import AssembleWindow
from byuam.body import AssetType
from byugui import message_gui
import checkout

def go():
	print "Heyo"
