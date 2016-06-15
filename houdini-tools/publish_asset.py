import hou
import os
# import pyqt_houdini
from PyQt4 import QtGui, QtCore
from byugui import PublishWindow

from byuam import Department, Project, Element

def publish_hda():
    project = Project()
    if publish_window.published:
        user = publish_window.user
        comment = publish_window.comment
        
        if is_asset:
            if asset in project.list_assets():
                body = project.get_asset(asset)
                
            if os.path.exists(src):
                if body is not None:
                    if Element.DEFAULT_NAME in body.list_elements(Department.ASSEMBLY):
                        element = body.get_element(Department.ASSEMBLY, Element.DEFAULT_NAME)
                        element.publish(user, src, comment)		
            else:
                hou.ui.displayMessage("File does not exist")
                
        #TODO - Add logic for publishing shot
        #else:
        
def go():
    global publish_window
    global asset
    global src
    global is_asset
    is_asset = False
    
    nodes = hou.selectedNodes()
    if len(nodes) == 1:
        is_asset = True
        asset = nodes[0].type().name() #get name of asset
        index = asset.find("_main")
        asset = asset[:index]
        src = nodes[0].type().definition().libraryFilePath()
        publish_window = PublishWindow("", hou.ui.mainQtWindow(), [Department.ASSEMBLY])
    
    else:
        publish_window = PublishWindow("", hou.ui.mainQtWindow(), [Department.LIGHTING])
    
    publish_window.finished.connect(publish_hda)
