try:
	from PySide import QtGui as QtWidgets
	from PySide import QtGui as QtGui
	from PySide import QtCore
except ImportError:
	from PySide2 import QtWidgets, QtGui, QtCore

def error(message):
	'''Reports an error'''
	msgBox = QtWidgets.QMessageBox()
	msgBox.setText(msgBox.tr(message))
	msgBox.addButton(QtWidgets.QMessageBox.Ok)

	msgBox.exec_()

def light_error(message):
	'''Reports an error that can be resolved with a yes or no'''
	'''returns True if yes, otherwise False'''
	msgBox = QtWidgets.QMessageBox()
	msgBox.setText(msgBox.tr(message))
	noButton = msgBox.addButton(QtWidgets.QMessageBox.No)
	yesButton = msgBox.addButton(QtWidgets.QMessageBox.Yes)

	msgBox.exec_()

	if msgBox.clickedButton() == yesButton:
		return True
	elif msgBox.clickedButton() == noButton:
		return False
