import maya.cmds as mc
import maya.mel as mel
import os
import shutil
from byuam.project import Project
from byuam.environment import Environment, Department, Status

def simpleBlast(name, startFrame, endFrame):

    currentPanel = mc.getPanel(wf=True)
    currentCamera = mc.modelEditor(currentPanel, q=True, camera=True)
    
    src_dir = os.path.dirname(mc.file(q=True, sceneName=True))
    project = Project()
    playblast_element = project.get_checkout_element(src_dir)
    playblast_dept = None
    playblast_body_name = None
    playblast_dir = src_dir
    playblast_filename = "playblast.mov"
    if playblast_element is not None:
		playblast_dir = playblast_element.get_render_dir()
		playblast_filename = playblast_element.get_name()+".mov"
		playblast_dept = playblast_element.get_department()
		playblast_body_name = playblast_element.get_parent()
	name = os.path.join(playblast_dir, playblast_filename)

    panelSwitch = []
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, nc=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, ns=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, pm=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, sds=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, pl=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, lt=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, ca=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, j=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, ikh=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, df=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, dy=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, fl=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, hs=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, fo=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, lc=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, dim=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, ha=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, pv=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, tx=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, str=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, gr=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, cv=True))
    panelSwitch.append(mc.modelEditor(currentPanel, q=True, hu=True))

    mel.eval("lookThroughModelPanel "+currentCamera+" "+currentPanel)
    mc.modelEditor(currentPanel, e=True, allObjects=0)
    mc.modelEditor(currentPanel, e=True, polymeshes=1)
    mc.modelEditor(currentPanel, e=True, nurbsSurfaces=0)
    mc.modelEditor(currentPanel, e=True, strokes=1)
    mc.modelEditor(currentPanel, e=True, cameras=0)

    playback_slider = mel.eval('$tmpVar=$gPlayBackSlider')
    soundfile = mc.timeControl(playback_slider, q=True, sound=True)
    print soundfile

    mc.playblast(st=startFrame, et=endFrame, sound=soundfile, fmt="qt", compression="jpeg", qlt=100, forceOverwrite=True, filename=name,
                 width=1920, height=817, offScreen=True, percent=100, v=False)

    mel.eval("lookThroughModelPanel "+currentCamera+" "+currentPanel)
    mc.modelEditor(currentPanel, e=True, nc=panelSwitch[0])
    mc.modelEditor(currentPanel, e=True, ns=panelSwitch[1])
    mc.modelEditor(currentPanel, e=True, pm=panelSwitch[2])
    mc.modelEditor(currentPanel, e=True, sds=panelSwitch[3])
    mc.modelEditor(currentPanel, e=True, pl=panelSwitch[4])
    mc.modelEditor(currentPanel, e=True, lt=panelSwitch[5])
    mc.modelEditor(currentPanel, e=True, ca=panelSwitch[6])
    mc.modelEditor(currentPanel, e=True, j=panelSwitch[7])
    mc.modelEditor(currentPanel, e=True, ikh=panelSwitch[8])
    mc.modelEditor(currentPanel, e=True, df=panelSwitch[9])
    mc.modelEditor(currentPanel, e=True, dy=panelSwitch[10])
    mc.modelEditor(currentPanel, e=True, fl=panelSwitch[11])
    mc.modelEditor(currentPanel, e=True, hs=panelSwitch[12])
    mc.modelEditor(currentPanel, e=True, fo=panelSwitch[13])
    mc.modelEditor(currentPanel, e=True, lc=panelSwitch[14])
    mc.modelEditor(currentPanel, e=True, dim=panelSwitch[15])
    mc.modelEditor(currentPanel, e=True, ha=panelSwitch[16])
    mc.modelEditor(currentPanel, e=True, pv=panelSwitch[17])
    mc.modelEditor(currentPanel, e=True, tx=panelSwitch[18])
    mc.modelEditor(currentPanel, e=True, str=panelSwitch[19])
    mc.modelEditor(currentPanel, e=True, gr=panelSwitch[20])
    mc.modelEditor(currentPanel, e=True, cv=panelSwitch[21])
    mc.modelEditor(currentPanel, e=True, hu=panelSwitch[22])

def showErrorDialog():
    return mc.confirmDialog(title = 'Error'
                        , message       = 'This is not an animation file!'
                        , button        = ['Ok']
                        , defaultButton = 'Ok'
                        , cancelButton  = 'Ok'
                        , dismissString = 'Ok')
    
def decodeFileName():
	'''
			Decodes the base name of the folder to get the asset name, assetType, and asset directory.
			@return: Array = [assetName:- the asset name, assetType:- the asset Type, version:- the asset version]
	'''
	# get the encoded folder name from the filesystem        
	encodedFolderName = os.path.basename(os.path.dirname(mc.file(q=True, sceneName=True)))

	# split the string based on underscore delimiters
	namesAry = encodedFolderName.split("_")
	
	# pop off the version and asset type information
	version   = namesAry.pop()
	assetType = namesAry.pop()

	#combine the array into a string to form the assetname
	assetName = '_'.join(namesAry)
	
	# return the assetName, assetType, and version
	return [assetName, assetType]

def go():
    try:
        assetName, assetType = decodeFileName()
    except IndexError:
        showErrorDialog()
        return

    if not assetType in Department.BACKEND:
        showErrorDialog()
        return

    #fileName = mc.file(q=True, sceneName=True)
    #group_path = os.path.join(os.environ['BYU_PROJECT_DIR'], 'production', 'shots', assetName, 'render')
    #blastPath = os.path.join(group_path, 'playblast')
    #name = os.path.join(blastPath, assetName)

    startFrame = mc.playbackOptions(q=True, min=True)
    endFrame = mc.playbackOptions(q=True, max=True)

    choice = mc.confirmDialog( title = 'Playblast Tool'
                              , message       = 'Playblast this shot?'
                              , button        = ['Cancel', 'Playblast']
                              , defaultButton = 'Playblast'
                              , cancelButton  = 'Cancel'
                              , dismissString = 'Cancel')
    if choice == 'Playblast':
        simpleBlast(name, startFrame, endFrame)
