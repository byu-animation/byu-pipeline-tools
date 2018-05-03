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
#### Remember, the icon must be a 33X33 .xpm, and the pythonFile key
#### must be the name of the file where your python script is
#### stored. (Careful, it's not an absolute path!)
####
import pymel.core as pm
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

	gShelfTopLevel = pm.mel.eval('global string $gShelfTopLevel; string $temp=$gShelfTopLevel')
	pm.shelfLayout(PROJ, cellWidth=33, cellHeight=33, p=gShelfTopLevel)

	#### Okay, for some reason, deleting the shelf from a shelf button crashes Maya.
	#### I'm saving this for another day, or for someone more adventurous.
	#### Make the hard-coded reload button:
	# shelfButton(command="printcow()", annotation="Reload the shelf",
	#			 image=os.path.join(ICON_DIR, "reload.xpm"))

	#### Load in the buttons
	json_file = file(os.path.join(SHELF_DIR, "shelf.json"))
	data = json.loads(json_file.read())
	for shelfItem in data['shelfItems']:
		if shelfItem['itemType'] == 'button':
			icon = os.path.join(ICON_DIR, shelfItem['icon'])
			annotation = shelfItem['annotation']
			pythonFile = shelfItem['pythonFile'][:-3]
			pm.shelfButton(command="import %s; %s"%(pythonFile, shelfItem['function']),annotation=annotation, image=icon, label=annotation)
		else:
			pm.separator(horizontal=False, style='none', enable=True, width=7)
			pm.separator(horizontal=False, style='none', enable=True, width=2, backgroundColor=(0.5,0.5,0.5))
			pm.separator(horizontal=False, style='none', enable=True, width=7)


	#setUpSoup(gShelfTopLevel)
	# Set default preferences
	pm.env.optionVars['generateUVTilePreviewsOnSceneLoad'] = 1

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
	if pm.shelfLayout(PROJ, exists=True):
		pm.deleteUI(PROJ)

BYU_load_shelf()
