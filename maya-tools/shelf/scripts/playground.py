import pymel.core as pm

def go():
	pm.env.optionVars['generateUVTilePreviewsOnSceneLoad'] = 1
	import maya.cmds as cmds
	if cmds.shelfLayout("TURTLE", exists=True):
		cmds.deleteUI("TURTLE", lay=True)
		print "You are now free from TURTLE. You're welcome!"
	else:
		print "There was no TURTLE to be removed."
