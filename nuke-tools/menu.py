import sip
import nuke
import checkout
import publish
import rollback
import nukeAutoComp

menubar = nuke.menu("Nuke")
# Custom Lab Tools
toolbar = nuke.toolbar("Nodes")
m = toolbar.addMenu("byu-pipeline Menu", icon="y.svg")
m.addCommand("Checkout", 'checkout.go()', icon="checkout.svg")
m.addCommand("Publish", 'publish.go()', icon="publish.svg")
m.addCommand("Rollback", 'rollback.go()', icon="rollback.svg")
m.addCommand("Auto Comp", 'nukeAutoComp.go()', icon="auto-comp.svg")
#Allen was asking about Nuke + Pipeline
