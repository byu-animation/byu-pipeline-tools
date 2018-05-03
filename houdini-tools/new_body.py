from byugui.new_body_gui import CreateWindow, NewBodyWindow
from PySide2 import QtWidgets
import hou
import os

def go():
	global quote_window
	dialog = CreateWindow(hou.ui.mainQtWindow())
