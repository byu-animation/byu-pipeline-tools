from byugui.inspire_quote_gui import QuoteWindow
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

mari_inpire_dialog = None

def go():
	global mari_inpire_dialog
	parent = QtWidgets.QApplication.activeWindow()
	mari_inpire_dialog = QuoteWindow(parent)
