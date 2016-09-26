from PyQt4 import QtCore
import sip
import nuke
import checkout
import publish

menubar = nuke.menu("Nuke")
# Custom Lab Tools
toolbar = nuke.toolbar("Nodes")
m = toolbar.addMenu("byu-pipeline Menu", icon="make me.png")
m.addCommand("Checkout", 'checkout.go()', icon="checkout.xpm")
m.addCommand("Publish", 'publish.go()', icon="publish.xpm")
#m.addCommand("Auto Comp", 'print 30', icon="")
#Allen was asking about Nuke + Pipeline
 

