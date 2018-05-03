from byugui.inspire_quote_gui import QuoteWindow
from PySide import QtGui

mari_inpire_dialog = None

def go():
	global mari_inpire_dialog
	parent = QtGui.QApplication.activeWindow()
	mari_inpire_dialog = QuoteWindow(parent)
