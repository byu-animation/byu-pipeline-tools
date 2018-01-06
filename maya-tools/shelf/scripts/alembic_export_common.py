import maya.cmds as cmds
import pymel.core as pm

# class NoTaggedGeo(Exception):
# 	'''Raised when the geo has no tags'''
# 	pass

def build_tagged_alembic_command(ref, filepath, startFrame, endFrame, step=0.25):
	# First check and see if the reference has a tagged node on it.
	print "hello from here"
	taggedNodes = get_tagged_node(ref)
	print "we have finished the tagged process"

	if taggedNodes is None:
		raise Exception

	# Visualize References and tags
	print ref
	print "Tagged:", taggedNodes

	return build_alembic_command(taggedNodes, filepath, startFrame, endFrame, step=step)

def build_alembic_command(geoList, outFilePath, startFrame, endFrame, step=0.25):
	# This determines the pieces that are going to be exported via alembic.
	roots_string = ""

	# Each of these should be in a list, so it should know how many to add the -root tag to the alembic.
	for alem_obj in geoList:
		print "alem_obj: " + alem_obj
		roots_string += (" -root %s"%(alem_obj))
	print "roots_string: " + roots_string

	# Then here is the actual Alembic Export command for Mel.
	command = 'AbcExport -j "%s -frameRange %s %s -stripNamespaces -step %s -writeVisibility -noNormals -uvWrite -worldSpace -file %s"'%(roots_string, str(startFrame), str(endFrame), str(step), outFilePath)
	print "Command", command
	return command

def get_tagged_node(ref):
	refNodes = cmds.referenceQuery(unicode(ref), nodes=True)
	rootNode = pm.ls(refNodes[0])
	taggedNodes = get_tagged_tree(rootNode[0])

	if not taggedNodes:
		return None

	return taggedNodes

def get_tagged_tree(node):
	# Looks for a tagged node that has the BYU Alembic Export flag on it.
	# If the parent has a tag all the children will be exported
	print "we are looking at this node", node
	if node.hasAttr("BYU_Alembic_Export_Flag"):
		print "We have a tag here"
		return [node]

	#Otherwise search all the children for any nodes with the flag
	tagged_children = []
	print "Here is the len of the children", len(node.listRelatives(c=True))
	for child in node.listRelatives(c=True):
		print "Here is a child", child
		tagged_children.extend(get_tagged_tree(child))

	print "We are leaving here with these tagged children", tagged_children
	return tagged_children
