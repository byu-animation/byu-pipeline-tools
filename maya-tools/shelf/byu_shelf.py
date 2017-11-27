#### Shelf code written for the BYU Animation Program by
#### Murphy Randle (murphyspublic@gmail.com). Inspiration and some code
#### snippets taken from http://etoia.free.fr/?p=1771

####
#  /$$   /$$		   /$$ /$$		   /$$ /$$
# | $$  | $$		  | $$| $$		  | $$| $$
# | $$  | $$  /$$$$$$ | $$| $$  /$$$$$$ | $$| $$
# | $$$$$$$$ /$$__  $$| $$| $$ /$$__  $$| $$| $$
# | $$__  $$| $$$$$$$$| $$| $$| $$  \ $$|__/|__/
# | $$  | $$| $$_____/| $$| $$| $$  | $$
# | $$  | $$|  $$$$$$$| $$| $$|  $$$$$$/ /$$ /$$
# |__/  |__/ \_______/|__/|__/ \______/ |__/|__/
####
#### Welcome to the shelf script!
####
#### If you'd like to add a shelf button, you can add it to
#### shelf.json. Follow the example of the other buttons in there.
#### Remember, the icon must be a 33X33 .xpm, and the python_file key
#### must be the name of the file where your python script is
#### stored. (Careful, it's not an absolute path!)
####
from pymel.core import *
import os
import sys
import json
from byuam.environment import Environment

byuEnv = Environment()

#### CONSTANTS, Edit these for customization.
PROJ = byuEnv.get_project_name()
SHELF_DIR = os.environ.get('MAYA_SHELF_DIR')
ICON_DIR = os.path.join(SHELF_DIR, "icons")
ICON_DIR = os.path.join(os.environ.get('BYU_TOOLS_DIR'), "assets", "images", "icons", "tool-icons")
SCRIPT_DIR = os.path.join(SHELF_DIR, "scripts")
####

#### Shelf building code. You shouldn't have to edit anything
#### below these lines. If you want to add a new shelf item,
#### follow the instructions in shelf.json.
sys.path.append(SCRIPT_DIR)

def BYU_load_shelf():
	BYU_delete_shelf()

	gShelfTopLevel = mel.eval('global string $gShelfTopLevel; string $temp=$gShelfTopLevel')
	shelfLayout(PROJ, cellWidth=33, cellHeight=33, p=gShelfTopLevel)

	#### Okay, for some reason, deleting the shelf from a shelf button crashes Maya.
	#### I'm saving this for another day, or for someone more adventurous.
	#### Make the hard-coded reload button:
	# shelfButton(command="printcow()", annotation="Reload the shelf",
	#			 image=os.path.join(ICON_DIR, "reload.xpm"))

	#### Load in the buttons
	json_file = file(os.path.join(SHELF_DIR, "shelf.json"))
	data = json.loads(json_file.read())
	for button in data['buttons']:
		icon = os.path.join(ICON_DIR, button['icon'])
		annotation = button['annotation']
		python_file = button['python_file'][:-3]
		shelfButton(command="import %s; %s.go()"%(python_file, python_file),annotation=annotation, image=icon)
	remove_unwanted_shelfs()
	setUpSoup(gShelfTopLevel)
	# Set default preferences
	env.optionVars['generateUVTilePreviewsOnSceneLoad'] = 1

	import maya.cmds as cmds

	saveLayouts = 0
	restoreLayouts = 0

	env.optionVars['useSaveScenePanelConfig'] = saveLayouts
	cmds.file(uc=saveLayouts)
	mel.eval('$gUseSaveScenePanelConfig=' + str(saveLayouts))

	env.optionVars['useScenePanelConfig'] = restoreLayouts
	cmds.file(uc=restoreLayouts)
	mel.eval('$gUseScenePanelConfig=' + str(restoreLayouts))

def remove_unwanted_shelfs():
	#There was a little bit of murmuring about the TURTLE shelf tab and how it not removeable. So I just removed at startup.
	import maya.cmds as cmds
	if cmds.shelfLayout("TURTLE", exists=True):
		cmds.deleteUI("TURTLE", lay=True)
		print "You are now free from TURTLE. You're welcome!"
	else:
		print "There was no TURTLE to be removed."

def setUpSoup(shelf):
	if cmds.shelfLayout("soup", exists=True):
		cmds.deleteUI("soup", lay=True)
		print "We just got rid of the soup shelf so that we can load it in fresh"

	shelfLayout("soup", cellWidth=33, cellHeight=33, p=shelf) #Try recreating the soup shelf
	import maya.mel as mel
	import os
	melpath = os.path.join(os.environ['MAYA_SHELF_PATH'], 'shelf_soup.mel')
	print melpath

	melCmd = ''

	melfile = open(melpath)
	print melfile
	for line in melfile:
		melCmd += line

	mel.eval(melCmd)
	mel.eval('shelf_soup()')

def BYU_delete_shelf():
	if shelfLayout(PROJ, exists=True):
		deleteUI(PROJ)

BYU_load_shelf()
