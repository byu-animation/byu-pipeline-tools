import reference_selection
import alembic_static_exporter
from byugui import selection_gui, message_gui
from PySide2 import QtWidgets
from byuam import Project
import pymel.core as pm
import os

class NoTaggedGeo(Exception):
	'''Raised when the geo has no tags'''

def go(element=None, dept=None, cfx=False, selection=None):
	if cfx:
		print 'There is a new way. Come talk to me about it.'
		raise Exception
	pm.loadPlugin('AbcExport')
	try:
		pm.saveFile(force=True)
	except Exception, e:
		message_gui.error('Congratulation you have found out why we need to check the file name. Please talk to the pipeline people to get this fixed up')

	if element is None:
		filePath = pm.sceneName()
		fileDir = os.path.dirname(filePath)
		proj = Project()
		checkout = proj.get_checkout(fileDir)
		print 'Here is the checkout', checkout
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
	return export(element, selection=selection)

def export(element, selection=None):
	proj = Project()
	bodyName = element.get_parent()
	body = proj.get_body(bodyName)
	abcFilePath = element.get_cache_dir()
	#TODO we don't want to put them into the element cache right away. We want to put them in a seperate place and then copy them over later.

	if body.is_shot():
		files = exportReferences(abcFilePath, static=False, tag='BYU_Alembic_Export_Flag', selectionMode=True)
	elif body.is_asset():
		if body.get_type() == AssetType.SET:
			files = exportReferences(abcFilePath, static=True)
		else:
			files = exportAll(abcFilePath, static=True)
	elif body.is_crowd_cycle():
		files = exportSelected(selection, abcFilePath, static=False, tag='BYU_Alembic_Export_Flag')

	if not files:
		#Maybe this is a bad distinction but None is if it was canceled or something and empty is if it went but there weren't any alembics
		if files is None:
			return
		message_gui.error('No alembics were exported')
		return

	for abcFile in files:
		os.system('chmod 774 ' + abcFile)

	#TODO install the geometry
	print "These are the files that we are returning", files
	return files


def exportSelected(selection, destination, static=False, tag=None):
	print "This is the selection", selection
	if not static:
		# Start the export 5 frames before the beginning and end it 5 frames after the end for reason? I don't know I didn't write it. But I'm sure it's important.
		start_frame = pm.playbackOptions(q=True, animationStartTime=True)
		end_frame = pm.playbackOptions(q=True, animationEndTime=True)
	else:
		start_frame = 1
		end_frame = 1

	abcFiles = []
	for node in selection:
		abcFilePath = os.path.join(destination, str(node) + '.abc')
		try:
			command = build_tagged_alembic_command(node, abcFilePath, tag, start_frame, end_frame)
			print 'Command:', command
		except NoTaggedGeo, e:
			message_gui.error('Unable to locate Alembic Export tag for ' + str(ref), title='No Alembic Tag Found')
			return
		print 'Export Alembic command: ', command
		pm.Mel.eval(command)
		abcFiles.append(abcFilePath)
	return abcFiles

def exportAll():
	alembic_static_exporter.go()

def exportReferences(destination, static=False, tag=None, selectionMode=False):
	if not static:
		# Start the export 5 frames before the beginning and end it 5 frames after the end for reason? I don't know I didn't write it. But I'm sure it's important.
		start_frame = pm.playbackOptions(q=True, animationStartTime=True) - 5
		end_frame = pm.playbackOptions(q=True, animationEndTime=True) + 5
	else:
		start_frame = 1
		end_frame = 1

	if selectionMode:
		selection = reference_selection.getSelectedReferences()
	else:
		selection = reference_selection.getLoadedReferences()

	if selection is None:
		return
	message_gui.yes_or_no('Would any one even want a confirmation of export really? Would they even read it?')
	#TODO do we want the above confirmation here?

	abcFiles = []

	for ref in selection:
		# refNodes = cmds.referenceQuery(unicode(ref), nodes=True)
		refPath = pm.referenceQuery(unicode(ref), filename=True)
		refNodes = pm.referenceQuery(unicode(refPath), nodes=True )
		rootNode = pm.ls(refNodes[0])[0]
		refAbcFilePath = os.path.join(destination, get_filename_for_reference(rootNode))
		print refAbcFilePath
		try:
			command = build_tagged_alembic_command(rootNode, refAbcFilePath, tag, start_frame, end_frame)
			print 'Command:', command
		except NoTaggedGeo, e:
			message_gui.error('Unable to locate Alembic Export tag for ' + str(ref), title='No Alembic Tag Found')
			return
		print 'Export Alembic command: ', command
		pm.Mel.eval(command)
		abcFiles.append(refAbcFilePath)
	return abcFiles

def get_filename_for_reference(ref):
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

def build_tagged_alembic_command(rootNode, filepath, tag, startFrame, endFrame, step=0.25):
	# First check and see if the reference has a tagged node on it.
	taggedNodes = get_tagged_nodes(rootNode, tag)

	if not taggedNodes:
		raise NoTaggedGeo

	# Visualize References and tags
	print rootNode
	print 'Tagged:', taggedNodes

	return build_alembic_command(taggedNodes, filepath, startFrame, endFrame, step=step)

def build_alembic_command(geoList, outFilePath, startFrame, endFrame, step=0.25):
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

def get_tagged_nodes(node, tag):
	# Looks for a tagged node that has the BYU Alembic Export flag on it.
	# If the parent has a tag all the children will be exported
	if node.hasAttr(tag):
		return [node]

	#Otherwise search all the children for any nodes with the flag
	tagged_children = []
	for child in node.listRelatives(c=True):
		tagged_children.extend(get_tagged_nodes(child, tag))

	return tagged_children
