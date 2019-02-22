# Gets list of all referenced objects in the current scene
# Exports list to JSON file with the following info for each asset:
    # asset name
    # version number
    # Translation/Position [X,Y,Z]
    # Scale [X, Y, Z]
    # Rotation [X, Y, Z]
# Each scene asset is a JSON object in a JSON array

import maya.cmds as mc
import maya.mel as mel
import pymel.core as pm
from byuam import Project
import os
import shutil
import json
import reference_selection
from byugui import selection_gui, message_gui
from byuam.body import AssetType
from byuam.project import Project
from byuam.environment import Environment, Department, Status
import publish
from byugui.publish_gui import PublishWindow


global maya_publish_dialog

def confirmWriteSetReferences(body=None):

    response = showConfirmationPopup()
    if response == "Yes":
        filePath = pm.sceneName()
        fileDir = os.path.dirname(filePath)
        proj = Project()
        if not body:
            checkout = proj.get_checkout(fileDir)
            bodyName = checkout.get_body_name()
            body = proj.get_body(bodyName)

        refsFilePath = os.path.join(Project().get_assets_dir(), body.get_name())    # I'm pretty sure this is how you get the name of the set?
        #refsFilePath = "/groups/dand/production/assets/b005_hallway" #TEMP ONLY!

        if body.is_asset():
            if body.get_type() == AssetType.SET:
                print("SET OK")
                exportReferences(refsFilePath)
            else:
                print("NOT A SET")
                # I don't think we want to export anything in this case, just stop it
                showFailurePopup('No set found in current scene.')

def getLoadedReferences():
	references = pm.ls(references=True, transforms=True)
	loaded=[]
	print "Loaded References: "
	for ref in references:
		print "Checking status of " + ref
		try:
			if ref.isLoaded():
				loaded.append(ref)
		except:
			print "Warning: " + ref + " was not associated with a reference file"
	return loaded

# Creates a list of all reference files in the current set
def exportReferences(filePath):
    refsSelection = getLoadedReferences()
    print("refsSelection = ", refsSelection)

    allReferences = [] #this will be the JSON array with one {} obj for each ref
    for ref in refsSelection:
        currRefObj = {}
        # refNodes = cmds.referenceQuery(unicode(ref), nodes=True)
        refPath = pm.referenceQuery(unicode(ref), filename=True)
        #print("\t Curr refpath:", refPath)
        refNodes = pm.referenceQuery(unicode(refPath), nodes=True )
        #print("\t Curr refNode:", refNodes)
        rootNode = pm.ls(refNodes[0])[0]
        #print("\t Curr rootNode:", rootNode)
        currRefName, currRefVerNum = getReferenceName(rootNode)
        print("\t CurrRefName:", currRefName)

        # Check if verNum is nothing - if so, we need to make it be an int 0
        if not currRefVerNum:
            currRefVerNum = 0

        # Get transform data
        tx = pm.getAttr(rootNode + '.translateX')
        ty = pm.getAttr(rootNode + '.translateY')
        tz = pm.getAttr(rootNode + '.translateZ')
        rx = pm.getAttr(rootNode + '.rotateX')
        ry = pm.getAttr(rootNode + '.rotateY')
        rz = pm.getAttr(rootNode + '.rotateZ')
        sx = pm.getAttr(rootNode + '.scaleX')
        sy = pm.getAttr(rootNode + '.scaleY')
        sz = pm.getAttr(rootNode + '.scaleZ')

        # Put all relevant data into dictionary object
        currRefObj = {"asset_name": currRefName,
                      "version_number": currRefVerNum,
                      "tx": tx,
                      "ty": ty,
                      "tz": tz,
                      "rx": rx,
                      "ry": ry,
                      "rz": rz,
                      "sx": sx,
                      "sy": sy,
                      "sz": sz }
        print("Finished currRefObj: ", currRefObj)
        allReferences.append(currRefObj)

    # Convert allReferences to JSON string
    jsonRefs = json.dumps(allReferences)
    print("\n FINAL JSON")
    print(jsonRefs)

    # Write JSON to file
    try:
        wholePath = os.path.join(filePath, "references.json")
        print(">> Writing to: " + wholePath)
        outfile = open(wholePath, "w")  # *** THIS IS THE NAME OF THE OUTPUT FILE ***
        outfile.write(jsonRefs)
        outfile.close()
    except IOError as e:
        showFailurePopup("I/O error({0}): {1}".format(e.errno, e.strerror))
    except:
        showFailurePopup("Unexpected error: " + str(sys.exc_info()[0]))
    else:
        showSuccessPopup()


def getReferenceName(ref):
        # When we get the file name we need to make sure that we also get the reference number. This will allow us to have multiple alembics from a duplicated reference.
    refPath = pm.referenceQuery(unicode(ref), filename=True)
    print("ref= " + ref)
    print("refpath= " + refPath)
    #refName = str(ref).split(':')[1]
    refName = refPathToRefName(refPath)
    print("refName= " + refName)

    start = refPath.find('{')
    end = refPath.find('}')
    if start == -1 or end == -1:
        vernum = ''
    else:
        vernum = refPath[start+1:end]
    return refName, vernum

def refPathToRefName(path):
    pathItems = str(path).split("/")
    for i in range(len(pathItems)):
        if pathItems[i - 1] == "assets":
            return pathItems[i]

def showConfirmationPopup():
    return mc.confirmDialog( title         = 'JSON Set Reference'
                                     , message       = 'Write JSON reference file for set?' #it'd be nice to print the set name here
                                     , button        = ['Yes', 'No']
                                     , defaultButton = 'Yes'
                                     , cancelButton  = 'No'
                                     , dismissString = 'No')

def showSuccessPopup():
    return mc.confirmDialog( title         = 'Success'
                                     , message       = 'JSON set reference written successfully.'
                                     , button        = ['OK']
                                     , defaultButton = 'OK'
                                     , cancelButton  = 'OK'
                                     , dismissString = 'OK')

def showFailurePopup(msg):
    return mc.confirmDialog( title         = 'Error'
                                     , message       = msg
                                     , button        = ['OK']
                                     , defaultButton = 'OK'
                                     , cancelButton  = 'OK'
                                     , dismissString = 'OK')

def post_publish():
    global maya_publish_dialog
    element = maya_publish_dialog.result
    confirmWriteSetReferences(Project().get_body(element.get_parent()))

def go(body=None):
    if not body:
        parent = publish.maya_main_window()
    	filePath = pm.sceneName()
        fileDir = os.path.dirname(filePath)
        proj = Project()
        checkout = proj.get_checkout(fileDir)
    	if not checkout:
    		filePath = Environment().get_user_workspace()
    		filePath = os.path.join(filePath, 'untitled.mb')
    		filePath = pipeline_io.version_file(filePath)
    	global maya_publish_dialog
    	maya_publish_dialog = PublishWindow(filePath, parent, [Department.MODEL])
    	maya_publish_dialog.finished.connect(post_publish)
    else:
        confirmWriteSetReferences(body)
