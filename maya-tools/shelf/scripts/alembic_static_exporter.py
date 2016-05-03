# Created by a lot of people

import maya.cmds as mc
import os
import shutil
from pymel.core import *

import byuam.pipeline_io as pio
from byuam.environment import Environment
from byuam.project import Project
#from ui_tools import ui, messageSeverity

def objExport(selected, path):
	'''
		Creates .obj files from a selection of objects

		@param: selected - a list of strings representing the geometry
		@param: path - a string to the path of the directory for .obj files to go

		@return: a list of strings that contain the full paths to all of the .obj
				files that were created

		@post: directory for 'path' is created if it wasn't already
	'''
	mc.loadPlugin("objExport")

	if not os.path.exists(path):
		os.makedirs(path)

	size = len(selected)

	mc.sysFile(path, makeDir=True)
	optionsStr = "groups=0;ptgroups=0;materials=0;smoothing=0;normals=0;uvs=1"
	exportType = "OBJexport"

	objfiles = []

	for geo in selected:
		mc.select(geo, r=True)
		geoName = formatFilename(geo) + ".obj"
		filename = os.path.join(path, geoName)
		print("Exporting \'" + filename + "\'...")
		mc.file(filename,
				force=True,
				options=optionsStr,
				type=exportType,
				preserveReferences=True,
				exportSelected=True)

		print("\tCOMPLETED")
		objfiles.append(filename)

	return objfiles

def abcExport(selected, path):
	if not os.path.exists(path):
		os.makedirs(path)

	abcfiles = []

	loadPlugin("AbcExport")
	for geo in selected:
		chop = geo.rfind('|')
		parent_geo = geo[:chop]
		abcFile = geo[(chop+1):]
		abcFile = formatFilename(abcFile) + ".abc"
		abcFilePath = os.path.join(path, abcFile)
		print abcFilePath
		command = "AbcExport -j \"-frameRange 1 1 -root "+parent_geo+" -nn -uv -file "+abcFilePath+"\";"
		print command
		Mel.eval(command)
		abcfiles.append(abcFilePath)

	return abcfiles

def formatFilename(filename):
	filename = filename.replace("Shape", "")
	filename = pio.alphanumeric(filename)
	return filename

def checkFiles(files):
	'''
		Checks the list of output files against which files were actually created

		@param: files - a list of strings representing full paths

		@return: a list of paths to files that do not exist
	'''

	missingFiles = []

	for filename in files:
		print "CHECKING********** " + filename
		if not os.path.exists(filename):
			missingFiles.append(filename)

	if not len(missingFiles) == 0:
		errorMessage = ""
		for f in missingFiles:
			errorMessage += "MISSING FILE: " + f + "\n"
		print(errorMessage)
		errorMessage = str(len(missingFiles)) + " Files Missing:\n\n" + errorMessage
		#mc.confirmDialog(title="Error exporting files", message=errorMessage)
		#ui.infoWindow(errorMessage, wtitle="Error exporting files", msev=messageSeverity.Error)

	return missingFiles


def decodeFileName():
	'''
		Decodes the base name of the folder to get the asset name, assetType, and asset directory.

		@return: Array = [assetName, assetType, version]
	'''
	encodedFolderName = os.path.basename(os.path.dirname(mc.file(q=True, sceneName=True)))
	namesAry = encodedFolderName.split("_")
	version   = namesAry.pop()
	assetType = namesAry.pop()
	assetName = '_'.join(namesAry)
	return [assetName, assetType, version]

def getElementCacheDirectory(path):
	proj = Project()
	checkout = proj.get_checkout(path)
	body = proj.get_body(checkout.get_body_name())
	elem = body.get_element(checkout.get_department_name(), checkout.get_element_name())
	return elem.get_cache_dir()

def installGeometry(path=''):
	'''
		Function to install the geometry into the PRODUCTION asset directory

		@return: True if the files were moved successfully
		@throws: a shutil exception if the move failed
	'''

	print "install newly created geo in files"
	path=os.path.dirname(mc.file(q=True, sceneName=True))
	assetName, assetType, version = decodeFileName()

	#srcOBJ = os.path.join(path, 'cache/objFiles')
	#destOBJ = os.path.join(os.environ['ASSETS_DIR'], assetName, 'cache/objFiles')
	#destABC = os.path.join(os.environ['ASSETS_DIR'], assetName, 'cache/abcFiles')

	srcABC = os.path.join(path, 'cache/abcFiles')
	destABC = getElementCacheDirectory(path)

	#if os.path.exists(destOBJ):
	#	shutil.rmtree(destOBJ)
	if os.path.exists(destABC):
		try:
			shutil.rmtree(destABC)
		except Exception as e:
			print 'Couldn\'t delete old abc files:'
			print e

	#print 'Copying '+srcOBJ+' to '+destOBJ
	#try:
	#	os.system('chmod 774 -R ' + srcOBJ)
	#	shutil.copytree(srcOBJ, destOBJ)
	#	os.system('chmod 774 -R '+ destOBJ)
	#except Exception as e:
	#	print e

	#treat alembic special so we don't mess up concurrent houdini reading . . .
	srcABC = os.path.join(srcABC, '*');
	if not os.path.exists(destABC):
		os.mkdir(destABC);
		os.system('chmod 774 -R ' + destABC)

	print 'Copying '+srcABC+' to '+destABC
	try:
		os.system('chmod 774 -R '+srcABC)
		result = os.system('mv -f '+srcABC+' '+destABC)
		print result
		# shutil.copytree(src=srcABC, dst=destABC)
	except Exception as e:
		print 'Couldn\'t copy newly generated abc files:'
		print e

	print 'Removing '+os.path.join(path, 'cache')
	shutil.rmtree(os.path.join(path, 'cache'))

	return True

def generateGeometry(path=''):
	'''
		Function for generating geometry for Maya files.

		Creates the following output formats:
			.obj

		@return: True if all files were created successfully
				False if some files were not created

		@post: Missing filenames are printed out to both the Maya terminal as well
				as presented in a Maya confirm dialog.
	'''

	path = os.path.dirname(mc.file(q=True, sceneName=True))
	print 'generateGeometry start'
	if not os.path.exists (os.path.join(path, 'cache')):
		os.makedirs(os.path.join(path, 'cache'))

	#OBJPATH = os.path.join(path, "cache/objFiles")
	ABCPATH = os.path.join(path, "cache/abcFiles")

	#if os.path.exists(OBJPATH):
	#	shutil.rmtree(OBJPATH)
	if os.path.exists(ABCPATH):
		shutil.rmtree(ABCPATH)

	filePath = cmds.file(q=True, sceneName=True)
	fileDir = os.path.dirname(filePath)
	proj = Project()
	checkout = proj.get_checkout(fileDir)
	body = proj.get_body(checkout.get_body_name())
	elem = body.get_element(checkout.get_department_name(), checkout.get_element_name())
	abcFilePath = elem.get_cache_dir()


	selection = mc.ls(geometry=True, visible=True)
	selection_long = mc.ls(geometry=True, visible=True, long=True)

	# Temporarily disabled obj support (might not be needed)
	#objs = objExport(selection, OBJPATH)

	# Check to see if all .obj files were created
	#if not len(checkFiles(objs)) == 0:
	#	return False

	abcs = abcExport(selection_long, ABCPATH)
	if not len(checkFiles(abcs)) == 0:
		return False

	return True

def go():
	if generateGeometry():
		installGeometry()

if __name__ == "__main__":
	# Uncomment this line if you want to read in a new destination from
	# command line. Intended to be a new destination for files to go.
	#dest = sys.argv[1]
	go()

