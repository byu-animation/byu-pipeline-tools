import hou
import os
# import pyqt_houdini
from PyQt4 import QtGui, QtCore
from byugui import CheckoutWindow

from byuam import Department, Project

#def checkout_hda():
#    project = Project()
#    item = checkout_window.current_item
#    if checkout_window.current_dept in Department.FRONTEND:
#        body = project.get_asset(item)
#    else:
#        body = project.get_shot(item)
#    
#    if body is None:
#        hou.ui.displayMessage("Not a valid asset or shot")
        
def go():
    global checkout_window
    checkout_window = CheckoutWindow(hou.ui.mainQtWindow(), [Department.ASSEMBLY, Department.LAYOUT])
#    checkout_window.finished.connect(checkout_hda)    
