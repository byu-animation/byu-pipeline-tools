import reference_selection
import alembic_static_exporter
from byugui import selection_gui, message_gui
from byuam.body import AssetType
from PySide2 import QtWidgets
from byuam import Project
import pymel.core as pm
import os

class NoTaggedGeo(Exception):
	'''Raised when the geo has no tags'''

def go(element=None, dept=None, selection=None, startFrame=None, endFrame=None):
	pm.loadPlugin('AbcExport')

	if not pm.sceneName() == '':
		pm.saveFile(force=True)

	if element is None:
		filePath = pm.sceneName()
		fileDir = os.path.dirname(filePath)
		proj = Project()
		checkout = proj.get_checkout(fileDir)
		if checkout is None:
			parent = QtWidgets.QApplication.activeWindow()
			element = selection_gui.getSelectedElement(parent)
			if element is None:
				return None
		else:
			bodyName = checkout.get_body_name()
			deptName = checkout.get_department_name()
			elemName = checkout.get_element_name()
			body = proj.get_body(bodyName)
			element = body.get_element(deptName, name=elemName)

	#Get the element from the right Department
	if dept is not None and not element.get_department() == dept:
		print 'We are overwriting the', element.get_department(), 'with', dept
		body = element.get_parent()
		element = body.get_element(dept)

	return export(element, selection=selection, startFrame=startFrame, endFrame=endFrame)

def export(element, selection=None, startFrame=None, endFrame=None):
	proj = Project()
	bodyName = element.get_parent()
	body = proj.get_body(bodyName)
	abcFilePath = element.get_cache_dir()
	#TODO we don't want to put them into the element cache right away. We want to put them in a seperate place and then copy them over later.

	if startFrame is None:
		startFrame = pm.playbackOptions(q=True, animationStartTime=True)
	if endFrame is None:
		endFrame = pm.playbackOptions(q=True, animationEndTime=True)

	if body.is_shot():
		startFrame -= 5
		endFrame += 5
		files = exportReferences(abcFilePath, tag='BYU_Alembic_Export_Flag', selectionMode=True, startFrame=startFrame, endFrame=endFrame)
	elif body.is_asset():
		if body.get_type() == AssetType.SET:
			files = exportReferences(abcFilePath)
		else:
			files = exportAll(abcFilePath)
	elif body.is_crowd_cycle():
			files = exportAll(abcFilePath, tag='BYU_Alembic_Export_Flag', startFrame=startFrame, endFrame=endFrame)

	if not files:
		#Maybe this is a bad distinction but None is if it was canceled or something and empty is if it went but there weren't any alembics
		if files is None:
			return
		message_gui.error('No alembics were exported')
		return

	for abcFile in files:
		os.system('chmod 774 ' + abcFile)

	#TODO install the geometry
	print 'These are the files that we are returning', files
	return files


def exportSelected(selection, destination, tag=None, startFrame=1, endFrame=1, disregardNoTags=False):
	abcFiles = []
	for node in selection:
		abcFilePath = os.path.join(destination, str(node) + '.abc')
		try:
			command = buildTaggedAlembicCommand(node, abcFilePath, tag, startFrame, endFrame)
			print 'Command:', command
		except NoTaggedGeo, e:
			if disregardNoTags:
				continue
			message_gui.error('Unable to locate Alembic Export tag for ' + str(node), title='No Alembic Tag Found')
			continue
		print 'Export Alembic command: ', command
		pm.Mel.eval(command)
		abcFiles.append(abcFilePath)
	return abcFiles

def exportAll(destination, tag=None, startFrame=1, endFrame=1):
	if tag is not None:
		selection = pm.ls(assemblies=True)
		return exportSelected(selection, destination, tag='BYU_Alembic_Export_Flag', startFrame=startFrame, endFrame=endFrame, disregardNoTags=True)
	else:
		return alembic_static_exporter.go()

def exportReferences(destination, tag=None, selectionMode=False, startFrame=1, endFrame=1):
	if selectionMode:
		selection = reference_selection.getSelectedReferences()
	else:
		selection = reference_selection.getLoadedReferences()

	if selection is None:
		return

	abcFiles = []

	for ref in selection:
		# refNodes = cmds.referenceQuery(unicode(ref), nodes=True)
		refPath = pm.referenceQuery(unicode(ref), filename=True)
		print 'the refpath', refPath
		refNodes = pm.referenceQuery(unicode(refPath), nodes=True )
		print 'the refNode', refNodes
		rootNode = pm.ls(refNodes[0])[0]
		print 'rootNode', rootNode
		refAbcFilePath = os.path.join(destination, getFilenameForReference(rootNode))
		print refAbcFilePath
		try:
			if tag is None:
				command = buildAlembicCommand(refAbcFilePath, startFrame, endFrame, geoList=[rootNode])
			else:
				command = buildTaggedAlembicCommand(rootNode, refAbcFilePath, tag, startFrame, endFrame)
			print 'Command:', command
		except NoTaggedGeo, e:
			message_gui.error('Unable to locate Alembic Export tag for ' + str(ref), title='No Alembic Tag Found')
			return
		print 'Export Alembic command: ', command
		pm.Mel.eval(command)
		abcFiles.append(refAbcFilePath)
	return abcFiles

def getFilenameForReference(ref):
	#TODO Make sure that we test for multiple files
	# When we get the file name we need to make sure that we also get the reference number. This will allow us to have multiple alembics from a duplicated reference.
	# refPath = ref.fileName(False,True,True)
	refPath = refPath = pm.referenceQuery(unicode(ref), filename=True)
	start = refPath.find('{')
	end = refPath.find('}')
	if start == -1 or end == -1:
		copyNum = ''
	else:
		copyNum = refPath[start+1:end]
	return os.path.basename(refPath).split('.')[0] + str(copyNum) + '.abc'

def buildTaggedAlembicCommand(rootNode, filepath, tag, startFrame, endFrame, step=0.25):
	# First check and see if the reference has a tagged node on it.
	taggedNodes = getTaggedNodes(rootNode, tag)

	if not taggedNodes:
		raise NoTaggedGeo

	# Visualize References and tags
	print rootNode
	print 'Tagged:', taggedNodes

	return buildAlembicCommand(filepath, startFrame, endFrame, step=step, geoList=taggedNodes)

def buildAlembicCommand(outFilePath, startFrame, endFrame, step=0.25, geoList=[]):
	# This determines the pieces that are going to be exported via alembic.
	roots_string = ''

	# Each of these should be in a list, so it should know how many to add the -root tag to the alembic.
	for alem_obj in geoList:
		print 'alem_obj: ' + alem_obj
		roots_string += (' -root %s'%(alem_obj))
	print 'roots_string: ' + roots_string

	# Then here is the actual Alembic Export command for Mel.
	command = 'AbcExport -j "%s -frameRange %s %s -stripNamespaces -step %s -writeVisibility -noNormals -uvWrite -worldSpace -file %s"'%(roots_string, str(startFrame), str(endFrame), str(step), outFilePath)
	print 'Command', command
	return command

def getTaggedNodes(node, tag):
	# Looks for a tagged node that has the BYU Alembic Export flag on it.
	# If the parent has a tag all the children will be exported
	print 'has attr?', node, tag
	if node.hasAttr(tag):
		print 'returning'
		return [node]

	print 'children'
	#Otherwise search all the children for any nodes with the flag
	tagged_children = []
	print 'we made it here before crashing', node.listRelatives(c=True)
	for child in node.listRelatives(c=True):
		tagged_children.extend(getTaggedNodes(child, tag))

	return tagged_children
