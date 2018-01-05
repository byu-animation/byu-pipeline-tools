import pymel.core as pm
from byugui import message_gui
from byuam import Project
import os

def go():
	fileName = pm.sceneName()
	listOfChanges = pm.dgmodified()

	#Check to see if there are unsaved changes
	if listOfChanges is not None:
		result = message_gui.save('Save changes to ' + str(fileName))
		if result is True:
			pm.saveFile()
		if result is None:
			return None

	name = message_gui.input('What is the name of this cycle?')
	if name is None:
		return None
	else:
		print 'This is the name that we got', name

	name = name.replace(' ', '_')
	print "This is the name", name
	project = Project()
	print "this is the project", project
	try:
		cycleAsset = project.create_crowd_cycle(name)
	except EnvironmentError, e:
		message_gui.error('There is already an crowd cycle with that name.', details=e)
		return None

	print "Here is the cycle asset", cycleAsset

	projDir = project.get_project_dir()
	crowdCache = os.path.join(projDir, 'crowdCache')
	if not os.path.exists(crowdCache):
		os.makedirs(crowdCache)

	fileName = name + '.mb'
	fileName = os.path.join(crowdCache, fileName)

	print 'This is the file name for the exported thing', fileName

	#now that we have gotten past all the things that could go wrong we will make a quick grouping to the selection that we don't want the user to know about.
	try:
		pm.group(name=name)
	except:
		# millis = byuutil.timestampThisYear()
		millis = 1
		name = name + str(millis)
		pm.group(name=name)

	#get the file name for our new asset
	cycleFile = pm.exportSelected(fileName, preserveReferences=1, force=1)
	print "This is the exported File", cycleFile
	pm.openFile(cycleFile, force=1)
