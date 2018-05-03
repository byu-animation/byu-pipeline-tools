try:
	from PySide import QtGui as QtWidgets
	from PySide import QtGui as QtGui
	from PySide import QtCore
except ImportError:
	from PySide2 import QtWidgets, QtGui, QtCore

def error(errMsg, details=None, title='Error'):
	message(errMsg, details=details, title=title)

def warning(warnMsg, details=None, title='Warning'):
	message(warnMsg, details=details, title=title)

def message(msg, details=None, title='Message'):
	'''Reports a message'''
	msgBox = QtWidgets.QMessageBox()
	msgBox.setText(msgBox.tr(msg))
	msgBox.setIcon(QtWidgets.QMessageBox.Warning)
	msgBox.setWindowTitle(title)
	msgBox.addButton(QtWidgets.QMessageBox.Ok)

	if details is not None:
		msgBox.setDetailedText(str(details))

	msgBox.exec_()

def info(infoMsg, title='Info'):
	'''Reports an message'''
	msgBox = QtWidgets.QMessageBox()
	msgBox.setText(msgBox.tr(infoMsg))
	msgBox.setIcon(QtWidgets.QMessageBox.Information)
	msgBox.setWindowTitle(title)
	msgBox.addButton(QtWidgets.QMessageBox.Ok)

	msgBox.exec_()

def light_error(errMsg, title='Warning'):
	'''Reports an error that can be resolved with a yes or no'''
	'''returns True if yes, otherwise False'''
	msgBox = QtWidgets.QMessageBox()
	msgBox.setText(msgBox.tr(errMsg))
	msgBox.setIcon(QtWidgets.QMessageBox.Warning)
	msgBox.setWindowTitle(title)
	noButton = msgBox.addButton(QtWidgets.QMessageBox.No)
	yesButton = msgBox.addButton(QtWidgets.QMessageBox.Yes)

	msgBox.exec_()

	if msgBox.clickedButton() == yesButton:
		return True
	elif msgBox.clickedButton() == noButton:
		return False

def yes_or_no(question, details=None, title='Question'):
	'''Reports an error that can be resolved with a yes or no'''
	'''returns True if yes, otherwise False'''
	msgBox = QtWidgets.QMessageBox()
	msgBox.setText(msgBox.tr(question))
	msgBox.setWindowTitle(title)
	msgBox.setIcon(QtWidgets.QMessageBox.Question)
	noButton = msgBox.addButton(QtWidgets.QMessageBox.No)
	yesButton = msgBox.addButton(QtWidgets.QMessageBox.Yes)

	if details is not None:
		msgBox.setDetailedText(details)

	msgBox.exec_()

	if msgBox.clickedButton() == yesButton:
		return True
	elif msgBox.clickedButton() == noButton:
		return False

def input(label, title='Input', text=None):
	'''Allows the user to respond with a text input'''
	'''If the okay button is pressed it returns the inputed text, otherwise None'''
	text = QtWidgets.QInputDialog.getText(None, title, label, text=text)

	if text[1]:
		return text[0]
	else:
		return None

def binary_option(text, optionOne, optionTwo, title='Question'):
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

def save(text):
	'''Prompts the user to save'''
	'''returns True if save is selected, False if don't save is selected otherwise None'''
	return binary_option(text, 'Save', 'Don\'t Save', title='Save Changes')
