#Author Trevor Barrus

import sys
import os
from PyQt4 import QtGui, QtCore
from byuam.project import Project
from byuam.environment import Department

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

class ReferenceWindow(QtGui.QWidget):
    
    finished = QtCore.pyqtSignal()
    
    def __init__(self, parent, src, dept_list=Department.ALL):
        super(ReferenceWindow, self).__init__()
        self.project = Project()
        self.parent = parent
        self.src = src
        self.filePath = None
        self.done = True
        self.reference = False
        self.initUI(dept_list)
        
    def initUI(self, dept_list):
        #define gui elements
        self.setGeometry(300,300,WINDOW_WIDTH,WINDOW_HEIGHT)
        self.setWindowTitle('Taijitu Reference Manager')
        self.departmentMenu = QtGui.QComboBox()
        for i in dept_list:
            self.departmentMenu.addItem(i)
        self.departmentMenu.activated[str].connect(self.setElementType)
        
        self.assetList = AssetListWindow(self)
        for asset in self.project.list_assets():
            item = QtGui.QListWidgetItem(asset)
            self.assetList.addItem(item)
            
        self.referenceButton = QtGui.QPushButton('Reference')
        self.referenceButton.clicked.connect(self.createReference)
        self.cancelButton = QtGui.QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.close)
            
        #set gui layout
        self.grid = QtGui.QGridLayout(self)
        self.setLayout(self.grid)
        self.grid.addWidget(self.departmentMenu, 0, 0)
        self.grid.addWidget(self.assetList, 1, 0, 1, 0)
        self.grid.addWidget(self.referenceButton, 2, 0)
        self.grid.addWidget(self.cancelButton, 2, 1)
        
        self.show()
        
    def setElementType(self):
        department = str(self.departmentMenu.currentText())
        self.assetList.refreshList(department)
        
    def createReference(self):
        checkout = self.project.get_checkout(os.path.dirname(self.src))
        if checkout is not None:
            body_name = checkout.get_body_name()
            body = self.project.get_body(body_name)
            body.add_reference(self.assetList.current_selection)
        self.done = False
        self.reference = True
        self.close()
        
    def closeEvent(self, event):
        self.finished.emit()
        event.accept()
        
class AssetListWindow(QtGui.QListWidget):
    def __init__(self, parent):
        super(AssetListWindow, self).__init__()
        self.parent = parent
        self.current_selection = None
        self.project = Project()
        self.initUI()
        
    def initUI(self):
        self.currentItemChanged.connect(self.set_current_item)
        
    def set_current_item(self, index):
        self.current_selection = str(index.text())
        body = self.project.get_body(self.current_selection)
        element = body.get_element(str(self.parent.departmentMenu.currentText()))
        path = element.get_app_filepath()
        self.parent.filePath = path
        
    def refreshList(self, department):
        if department in Department.FRONTEND:
            self.elements = self.project.list_assets()
        else:
            self.elements = self.project.list_shots()
		    
        self.clear()
        for e in self.elements:
		    self.addItem(e)
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = ReferenceWindow(app)
    sys.exit(app.exec_())

