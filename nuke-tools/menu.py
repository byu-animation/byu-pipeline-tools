import sys
import nuke
 
 
print 'Loading Lab Tools...'
menubar = nuke.menu("Nuke")
 
# Custom Lab Tools
toolbar = nuke.toolbar("Nodes")
m = toolbar.addMenu("CUSTOM MENU 1", icon="ICON NAME HERE.png")
 
m.addCommand("CUSTOMGIZMO", "nuke.createNode(\"CUSTOMGIZMO\")", icon="IMAGE NAME HERE.png")
m.addCommand("CUSTOMGIZMO", "nuke.createNode(\"CUSTOMGIZMO\")", icon="IMAGE NAME HERE.png")
m.addCommand("CUSTOMGIZMO", "nuke.createNode(\"CUSTOMGIZMO\")", icon="IMAGE NAME HERE.png")
 
# Custom Lab Tools
toolbar = nuke.toolbar("Nodes")
m = toolbar.addMenu("CUSTOM MENU 2", icon="ICON NAME HERE.png")
 
m.addCommand("CUSTOMGIZMO", "nuke.createNode(\"CUSTOMGIZMO\")", icon="IMAGE NAME HERE.png")
m.addCommand("CUSTOMGIZMO", "nuke.createNode(\"CUSTOMGIZMO\")", icon="IMAGE NAME HERE.png")
m.addCommand("CUSTOMGIZMO", "nuke.createNode(\"CUSTOMGIZMO\")", icon="IMAGE NAME HERE.png")
 
# Custom Lab Tools
toolbar = nuke.toolbar("Nodes")
m = toolbar.addMenu("CUSTOM MENU 3", icon="ICON NAME HERE.png")
 
m.addCommand("CUSTOMGIZMO", "nuke.createNode(\"CUSTOMGIZMO\")", icon="IMAGE NAME HERE.png")
m.addCommand("CUSTOMGIZMO", "nuke.createNode(\"CUSTOMGIZMO\")", icon="IMAGE NAME HERE.png")
m.addCommand("CUSTOMGIZMO", "nuke.createNode(\"CUSTOMGIZMO\")", icon="IMAGE NAME HERE.png")
