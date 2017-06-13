from byuam import Department
from byugui.checkout_gui import CheckoutWindow
from PySide import QtGui
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
	#print filepath



	if True:
		return
	if filepath is not None:
#Find mari alternative for cmds --> import maya.cmds as cmds
#		if not cmds.file(q=True, sceneName=True) == '':
#			cmds.file(save=True, force=True) #save file

		if not os.path.exists(filepath):
#			cmds.file(new=True, force=True)
#			cmds.file(rename=filepath)
#			cmds.file(save=True, force=True)
			print "new file "+filepath
			mari.scriptSaveAs(filepath+".nk")
		else:
#			cmds.file(filepath, open=True, force=True)
			print "open file "+filepath
			mari.scriptOpen(filepath)
