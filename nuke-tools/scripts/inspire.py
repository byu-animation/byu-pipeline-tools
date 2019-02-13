from byugui.inspire_quote_gui import QuoteWindow
from PySide import QtGui

nuke_inpire_dialog = None

def go():
	global nuke_inpire_dialog
	parent = QtGui.QApplication.activeWindow()
	nuke_inpire_dialog = QuoteWindow(parent)
