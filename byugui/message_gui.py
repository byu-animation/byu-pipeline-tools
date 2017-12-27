try:
	from PySide import QtGui as QtWidgets
	from PySide import QtGui as QtGui
	from PySide import QtCore
except ImportError:
	from PySide2 import QtWidgets, QtGui, QtCore

def error(text, error=None, title="Error"):
	message(text, details=warning, title=title)

def warning(text, warning=None, title="Warning"):
	message(text, details=warning, title=title)

def message(text, details=None, title="Message"):
	'''Reports a message'''
	msgBox = QtWidgets.QMessageBox()
	msgBox.setText(msgBox.tr(text))
	msgBox.setIcon(QtWidgets.QMessageBox.Warning)
	msgBox.setWindowTitle(title)
	msgBox.addButton(QtWidgets.QMessageBox.Ok)

	if details is not None:
		msgBox.setDetailedText(details)

	msgBox.exec_()

def info(text, title="Info"):
	'''Reports an message'''
	msgBox = QtWidgets.QMessageBox()
	msgBox.setText(msgBox.tr(text))
	msgBox.setIcon(QtWidgets.QMessageBox.Information)
	msgBox.setWindowTitle(title)
	msgBox.addButton(QtWidgets.QMessageBox.Ok)

	msgBox.exec_()

def light_error(text, title="Warning"):
	'''Reports an error that can be resolved with a yes or no'''
	'''returns True if yes, otherwise False'''
	msgBox = QtWidgets.QMessageBox()
	msgBox.setText(msgBox.tr(text))
	msgBox.setIcon(QtWidgets.QMessageBox.Warning)
	msgBox.setWindowTitle(title)
	noButton = msgBox.addButton(QtWidgets.QMessageBox.No)
	yesButton = msgBox.addButton(QtWidgets.QMessageBox.Yes)

	msgBox.exec_()

	if msgBox.clickedButton() == yesButton:
		return True
	elif msgBox.clickedButton() == noButton:
		return False

def yes_or_no(text, title="Question"):
	'''Reports an error that can be resolved with a yes or no'''
	'''returns True if yes, otherwise False'''
	msgBox = QtWidgets.QMessageBox()
	msgBox.setText(msgBox.tr(text))
	msgBox.setWindowTitle(title)
	msgBox.setIcon(QtWidgets.QMessageBox.Question)
	noButton = msgBox.addButton(QtWidgets.QMessageBox.No)
	yesButton = msgBox.addButton(QtWidgets.QMessageBox.Yes)

	msgBox.exec_()

	if msgBox.clickedButton() == yesButton:
		return True
	elif msgBox.clickedButton() == noButton:
		return False

def binary_option(text, optionOne, optionTwo, title="Question"):
	'''Gives the user a message and a binary choice'''
	'''returns True if option one is selected, false if the second option is selected, otherwise None'''
	msgBox = QtWidgets.QMessageBox()
	msgBox.setText(msgBox.tr(text))
	msgBox.setIcon(QtWidgets.QMessageBox.Question)
	msgBox.setWindowTitle(title)
	fristButton = msgBox.addButton(msgBox.tr(optionOne), QtWidgets.QMessageBox.ActionRole)
	secondButton = msgBox.addButton(msgBox.tr(optionTwo), QtWidgets.QMessageBox.ActionRole)
	cancelButton = msgBox.addButton(QtWidgets.QMessageBox.Cancel)

	msgBox.exec_()

	if msgBox.clickedButton() == fristButton:
		return True
	elif msgBox.clickedButton() == secondButton:
		return False
	return None
