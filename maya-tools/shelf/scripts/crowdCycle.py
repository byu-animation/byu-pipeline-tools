import pymel.core as pm
from byugui import message_gui
# from byuam.environment import Environment, Department, Status
from byuam import Project, Department
import alembic_exporter
import reference
from byuam import byuutil
import os

def go():
	fileName = pm.sceneName()
	listOfChanges = pm.dgmodified()

	#Check to see if there are unsaved changes
	if listOfChanges is not None:
		result = message_gui.yes_or_no('In order to continue the file will need to be saved and closed. Are you ready to proceed?')
		if not result:
			return None

	name = message_gui.input('What is the name of this cycle?')
	if name is None:
		return None

	invalidInput = True
	while(invalidInput):
		firstFrame = message_gui.input('What is the first frame of the cycle?')
		try:
			firstFrame = int(firstFrame)
		except ValueError:
			message_gui.error('Please enter a number')
			continue
		invalidInput = False

	invalidInput = True
	while(invalidInput):
		lastFrame = message_gui.input('What is the last frame of the cycle?')
		try:
			lastFrame = int(lastFrame)
		except ValueError:
			message_gui.error('Please enter a number')
			continue
		invalidInput = False

	name = name.replace(' ', '_')
	project = Project()
	try:
		cycleAsset = project.create_crowd_cycle(name)
	except EnvironmentError, e:
		message_gui.error('There is already an crowd cycle with that name.', details=e)
		return None

	element = cycleAsset.get_element(Department.CYCLES)

	projDir = project.get_project_dir()
	crowdCache = os.path.join(projDir, 'production', 'crowdCache')
	if not os.path.exists(crowdCache):
		os.makedirs(crowdCache)

	cacheFileName = name + '.mb'
	cacheFileName = os.path.join(crowdCache, cacheFileName)
	backupFileDir = os.path.join(os.path.dirname(fileName), 'backup')
	if not os.path.exists(backupFileDir):
		os.makedirs(backupFileDir)
	backupFileName = os.path.join(backupFileDir, os.path.basename(fileName) + '.backup.mb')

	backupResult = pm.exportAll(backupFileName, preserveReferences=True, force=True)
	print 'For your information there is a back up of your file before you did this operation. That file is located here:', backupResult

	#now that we have gotten past all the things that could go wrong we will make a quick grouping to the selection that we don't want the user to know about.
	try:
		pm.group(name=name)
	except:
		millis = byuutil.timestampThisYear()
		name = name + str(millis)
		pm.group(name=name)

	#get the file name for our new asset
	cycleFile = pm.exportSelected(cacheFileName, preserveReferences=True, force=True)
	pm.saveFile() #Make sure we save it so that we will have that group again when we open it.
	print 'opening', cycleFile
	pm.openFile(cycleFile, force=True)

	#Set frameRange as specified by the user.
	pm.playbackOptions(ast=firstFrame)
	pm.playbackOptions(aet=lastFrame)
	pm.saveFile()

	user = project.get_current_username()
	comment = 'First crowd cycle publish'

	element.publish(user, cycleFile, comment)

	# Select the group then grab the selection
	selection = pm.select(name)
	selection = pm.ls(selection=True)

	alembics = alembic_exporter.go(element, selection=selection, startFrame=firstFrame, endFrame=lastFrame)

	pm.saveFile()
	print 'opening', fileName
	pm.openFile(fileName, force=True)

	group = pm.ls(name)[0]

	delete(group)
	reference.referenceCrowdCycle(alembics)

def delete(node):
	if pm.referenceQuery(node, inr = True):
		refFile = pm.referenceQuery(node, f = True)
		ref = pm.FileReference(refFile)
		ref.remove()
		return
	for child in node.listRelatives(c=True):
		delete(child)
	pm.delete(node)
