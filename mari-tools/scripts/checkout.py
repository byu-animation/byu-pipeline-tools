from byuam import Department
from byugui.checkout_gui import CheckoutWindow

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


import os
import mari

mari_checkout_dialog = None


def go():
	global mari_checkout_dialog
	parent = QtGui.QApplication.activeWindow()
	mari_checkout_dialog = CheckoutWindow(parent, [Department.TEXTURE])
	mari_checkout_dialog.finished.connect(post_checkout)

def post_checkout():
	filepath = mari_checkout_dialog.result
	if filepath is not None:

		if not os.path.exists(filepath):
			print "new file "+filepath
			#TODO: make a new project if there are not publishes?
			print "We don't handle creating new files"
		else:
			project = mari.projects.extract(filepath)
			mari.projects.open(project.name())
