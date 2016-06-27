#Author: Trevor Barrus
import hou
import os
from PyQt4 import QtGui, QtCore
from byugui import PublishWindow

from byuam import Department, Project, Element

def publish_hda():
    project = Project()
    if publish_window.published:
        user = publish_window.user
        comment = publish_window.comment
        
        if is_asset:
            if asset_name in project.list_assets():
                body = project.get_asset(asset_name)
                
            if os.path.exists(src):
                if body is not None:
                    if Element.DEFAULT_NAME in body.list_elements(Department.ASSEMBLY):
                        #save node definition
                        asset.type().definition().updateFromNode(asset)
                        asset.matchCurrentDefinition()
                        element = body.get_element(Department.ASSEMBLY, Element.DEFAULT_NAME)
                        element.publish(user, src, comment)		
            else:
                hou.ui.displayMessage("File does not exist")
                
        
def go():
    global publish_window
    global asset
    global asset_name
    global src
    global is_asset
    is_asset = False
    
    nodes = hou.selectedNodes()
    if len(nodes) == 1:
        if nodes[0].type().definition() is not None:
            is_asset = True
            asset = nodes[0]
            asset_name = nodes[0].type().name() #get name of asset
            index = asset_name.find("_main")
            if index > 0:
                asset_name = asset_name[:index]
            src = nodes[0].type().definition().libraryFilePath()
            publish_window = PublishWindow("", hou.ui.mainQtWindow(), [Department.ASSEMBLY])
        else:
            hou.ui.displayMessage("Node is not a digital asset")
            return
    
    else:
        publish_window = PublishWindow("", hou.ui.mainQtWindow(), [Department.LIGHTING])
    
    publish_window.finished.connect(publish_hda)
