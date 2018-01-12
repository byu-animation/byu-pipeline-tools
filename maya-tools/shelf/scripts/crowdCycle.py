import pymel.core as pm
from byugui import message_gui
# from byuam.environment import Environment, Department, Status
from byuam import Project, Department
import alembic_exporter
import os

def go():
	fileName = pm.sceneName()
	listOfChanges = pm.dgmodified()

	#Check to see if there are unsaved changes
	if listOfChanges is not None:
		result = message_gui.save('In order to continue the file will need to be saved and closed. Are you ready to proceed?')
		if not result:
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
	element = cycleAsset.get_element(Department.CYCLES)

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
	pm.saveFile() #Make sure we save it so that we will have that group again when we open it.
	pm.openFile(cycleFile, force=True)

	user = project.get_current_username()
	comment = 'First crowd cycle publish'

	element.publish(user, cycleFile, comment)

	selection = pm.select(name)
	selection = pm.ls(selection=True)

	print selection

	alembics = alembic_exporter.go(element, selection=selection)
	print 'These are the alembic files that we got', alembics

	pm.saveFile()
	pm.openFile(fileName, force=True)

	group = pm.ls(name)[0]

	delete(group)
	referenceCrowdCycle(alembics)

def referenceCrowdCycle(paths):
	for cycle in paths:
		fileName = os.path.basename(cycle)
		#The file is going to be an alembic so we can drop the last four characters '.abc' to get the file name
		cycleName = fileName[:len(fileName)-4]

		cycleRefGroup = cycleName + 'RNgroup'
		cycleControls = cycleName + '_controls'
		offset = 'offset'
		speed = 'speed'
		cycleType = 'cycleType'
		refAlembicNode = cycleName + '_' + cycleName + '_AlembicNode'
		refAlembicOffset = refAlembicNode + '.' + offset
		refAlembicSpeed = refAlembicNode + '.' + speed
		refAlembicCycleType = refAlembicNode + '.' + cycleType
		controlAlembicOffset = cycleControls + '.' + offset
		controlAlembicSpeed = cycleControls + '.' + speed

		pm.system.createReference(cycle, groupReference=True)

		node = pm.ls(cycleRefGroup)[0]
		circ = pm.circle(r=0.25,nr=(0, 1, 0), n=cycleControls)[0]
		pm.parent(circ, node)

		if circ.hasAttr(offset):
			circ.deleteAttr(offset)
		if circ.hasAttr(speed):
			circ.deleteAttr(speed)
		circ.addAttr(offset, at='double', hidden=False, dv=0.0, k=True)
		circ.addAttr(speed, at='double', hidden=False, dv=1.0, k=True)

		# When passing in arguments to connectAttr remember that attr 1 controls attr 2
		pm.connectAttr(controlAlembicOffset, refAlembicOffset)
		pm.connectAttr(controlAlembicSpeed, refAlembicSpeed)
		pm.setAttr(refAlembicCycleType, 1)

def delete(node):
	if pm.referenceQuery(node, inr = True):
		refFile = pm.referenceQuery(node, f = True)
		ref = pm.FileReference(refFile)
		ref.remove()
		return
	for child in node.listRelatives(c=True):
		delete(child)
	pm.delete(node)
