from byuam import Department
from byugui.checkout_gui import CheckoutWindow
from byugui.publish_gui import PublishWindow
from PyQt4 import QtCore
from PyQt4 import QtGui
import sip
import os
import nuke

nuke_checkout_dialog = None
nuke_publish_dialog = None

def checkout():
    global nuke_checkout_dialog
    parent = QtGui.QApplication.activeWindow()
    nuke_checkout_dialog = CheckoutWindow(parent, [Department.COMP])
    nuke_checkout_dialog.finished.connect(post_checkout)

def post_checkout():
    filepath = nuke_checkout_dialog.result
    print filepath
    if filepath is not None:
#Find nuke alternative for cmds --> import maya.cmds as cmds
#        if not cmds.file(q=True, sceneName=True) == '':
#            cmds.file(save=True, force=True) #save file

        if not os.path.exists(filepath):
#            cmds.file(new=True, force=True)
#            cmds.file(rename=filepath)
#            cmds.file(save=True, force=True)
            print "new file "+filepath
        else:
#            cmds.file(filepath, open=True, force=True)
            print "open file "+filepath

def publish():
    parent = QtGui.QApplication.activeWindow()
    #get file path
    filepath = ""
    global nuke_publish_dialog
    nuke_publish_dialog = PublishWindow(filepath, parent, [Department.COMP])
    nuke_publish_dialog.finished.connect(post_publish)

def post_publish():
    print "this is the post publish function"


menubar = nuke.menu("Nuke")
# Custom Lab Tools
toolbar = nuke.toolbar("Nodes")
m = toolbar.addMenu("byu-pipeline Menu", icon="make me.png")
m.addCommand("Checkout", 'checkout()', icon="checkout.xpm")
m.addCommand("Publish", 'publish()', icon="publish.xpm")
#m.addCommand("Chris Romney's script thingy", 'print 30', icon="")
#Allen was asking about Nuke + Pipeline
 

