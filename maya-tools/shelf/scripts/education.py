import pymel.core as pm
from byugui mport message_gui

def go():
	pm.FileInfo()['license'] = 'education'
	fileName = pm.sceneName()
	pm.saveFile()
	message_gui.info('This Maya file has been converted to an education licence')
