from byuam import Department
from byugui.checkout_gui import CheckoutWindow
from PySide import QtGui
import os
import nuke

nuke_checkout_dialog = None


def go():
	global nuke_checkout_dialog
	parent = QtGui.QApplication.activeWindow()
	nuke_checkout_dialog = CheckoutWindow(parent, [Department.COMP])
	nuke_checkout_dialog.finished.connect(post_checkout)

def post_checkout():
	filepath = nuke_checkout_dialog.result
	#print filepath
	if filepath is not None:
#Find nuke alternative for cmds --> import maya.cmds as cmds
#		if not cmds.file(q=True, sceneName=True) == '':
#			cmds.file(save=True, force=True) #save file

		if not os.path.exists(filepath):
#			cmds.file(new=True, force=True)
#			cmds.file(rename=filepath)
#			cmds.file(save=True, force=True)
			print "new file "+filepath
		nuke.scriptSaveAs(filepath+".nk")
		else:
#			cmds.file(filepath, open=True, force=True)
			print "open file "+filepath
			nuke.scriptOpen(filepath)
