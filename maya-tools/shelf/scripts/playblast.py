import maya_geo_export as geo
import utilities as amu
import maya.cmds as mc
import maya.mel as mel
import os
import shutil

def simpleBlast(name, startFrame, endFrame):

    currentPanel = mc.getPanel(wf=True)
    currentCamera = mc.modelEditor(currentPanel, q=True, camera=True)

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
                 width=1280, height=692, offScreen=True, percent=100, v=False)

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

    filename = name +".mov"
    #Element new_element = Project.getelement?
    #filepath = new_element.get_render_dir()
    djv_cmd = (" /usr/local/djv/bin/djv_view  " + filename + " &");
    os.system(djv_cmd)
    print "playblast saved here: "+filename
    for_edit_dir = os.path.join(os.environ['PRODUCTION_DIR'], 'FOR_EDIT', 'ANIMATION_PLAYBLASTS')
    for_edit_name = os.path.basename(filename).split('_')[0]+'.mov'
    for_edit_path = os.path.join(for_edit_dir, for_edit_name)
    shutil.copy(filename, for_edit_path)

def showErrorDialog():
    return mc.confirmDialog(title = 'Error'
                        , message       = 'This is not an animation file!'
                        , button        = ['Ok']
                        , defaultButton = 'Ok'
                        , cancelButton  = 'Ok'
                        , dismissString = 'Ok')
    

def go():
    try:
        assetName, assetType, version = geo.decodeFileName()
    except IndexError:
        showErrorDialog()
        return

    if not assetType == Department.LAYOUT:
        showErrorDialog()
        return

    fileName = mc.file(q=True, sceneName=True)
    dirName = os.path.dirname(fileName)
    source = amu.getCheckinDest(dirName)
    blastPath = os.path.join(os.path.dirname(source), 'playblasts')
    versionNum = amu.getLatestVersion(source)+1
    name = os.path.join(blastPath, assetName+"_v"+("%03d" % versionNum))

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

if __name__ == '__main__':
    go()
