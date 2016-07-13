#Author: Trevor Barrus
import hou
import os
from PyQt4 import QtGui, QtCore
from byugui import RollbackWindow

from byuam import Project, Department, Environment

def rollback_hda():
    filepath = rollback_window.result
    if filepath is not None:
        environment = Environment()
        hou.hda.uninstallFile(src, change_oplibraries_file=False)
        dst = os.path.join(environment.get_assembly_dir(), asset_name)
        hou.hda.installFile(dst)
        hou.ui.displayMessage("Rollback successful")
        
def go():
    global rollback_window
    global src
    global asset_name
    nodes = hou.selectedNodes()
    if len(nodes) == 1:
        asset = nodes[0]
        src = asset.type().definition().libraryFilePath()
        asset_name = os.path.basename(src)
        index = asset_name.find("_assembly")
        if index > 0:
            base_name = asset_name[:index]
        project = Project()
        body = project.get_body(base_name)
        element = body.get_element(Department.ASSEMBLY)
        rollback_window = RollbackWindow(element, hou.ui.mainQtWindow())
    else:
        #TODO: Implement rollback for shots
        print "Rollback shot"
        

    rollback_window.finished.connect(rollback_hda)
