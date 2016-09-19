import sys
import nuke

 
print 'Loading Lab Tools...'
menubar = nuke.menu("Nuke")
 
# Custom Lab Tools
toolbar = nuke.toolbar("Nodes")
m = toolbar.addMenu("byu-pipeline Menu", icon="make me.png")
 
m.addCommand("Checkout", 'print 10', icon="checkout.xpm")
m.addCommand("Publish", 'print 20', icon="publish.xpm")
m.addCommand("Chris Romney's script thingy", 'print 30', icon="")
#Allen was asking about Nuke + Pipeline
 

