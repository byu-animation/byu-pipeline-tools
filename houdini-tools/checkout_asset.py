import hou
import os
# import pyqt_houdini
from PyQt4 import QtGui, QtCore
from byugui import CheckoutWindow

from byuam import Department, Project, Environment, Element
        
def go():
    global checkout_window
    project = Project()
    environment = Environment()
    
    nodes = hou.selectedNodes()
    if len(nodes) == 1:
        #if selected node is digital asset
        if nodes[0].type().definition() is not None:
            asset = nodes[0]
            asset_name = nodes[0].type().name() #get name of asset
            index = asset_name.find("_main")
            asset_name = asset_name[:index]
            src = nodes[0].type().definition().libraryFilePath()
            current_user = environment.get_current_username()
            
            if asset_name in project.list_assets():
                body = project.get_asset(asset_name)
                
            if os.path.exists(src):
                if body is not None: 
                    if Element.DEFAULT_NAME in body.list_elements(Department.ASSEMBLY):
                        element = body.get_element(Department.ASSEMBLY, Element.DEFAULT_NAME)
                        element_path = element.checkout(current_user)
                        hou.hda.uninstallFile(src, change_oplibraries_file=False)
                        hou.hda.installFile(element_path)
                        asset.allowEditingOfContents()
                        hou.ui.displayMessage("Checkout Successful!", title='Success!')
            
    elif len(nodes) > 1:
        hou.ui.displayMessage("Only one node can be selected for checkout")
    else:
        checkout_window = CheckoutWindow(hou.ui.mainQtWindow(), [Department.LAYOUT])    
