#Author Trevor Barrus

import sys
import os
import operator
from PyQt4 import QtGui, QtCore
from byuam.project import Project
from byuam.body import Asset
from byuam.environment import Department, AssetType

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

class ReferenceWindow(QtGui.QWidget):
    
    finished = QtCore.pyqtSignal()
    
    def __init__(self, parent, src, dept_list=Department.ALL):
        super(ReferenceWindow, self).__init__()
        self.project = Project()
        self.parent = parent
        self.src = src
        self.filePaths = []
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

        self.typeFilterLabel = QtGui.QLabel("Type Filter")
        self.typeFilterLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.typeFilter = QtGui.QComboBox()
        self.typeFilter.addItem("all")
        for i in AssetType.ALL:
            self.typeFilter.addItem(i)
            
        self.typeFilter.currentIndexChanged.connect(self.setElementType)
        self.referenceButton = QtGui.QPushButton('Reference')
        self.referenceButton.clicked.connect(self.createReference)
        self.cancelButton = QtGui.QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.close)
            
        #set gui layout
        self.grid = QtGui.QGridLayout(self)
        self.setLayout(self.grid)
        self.grid.addWidget(self.departmentMenu, 0, 0)
        self.grid.addWidget(self.assetList, 1, 0, 1, 0)
        self.grid.addWidget(self.typeFilterLabel, 2, 0)
        self.grid.addWidget(self.typeFilter, 2, 1)
        self.grid.addWidget(self.referenceButton, 3, 0)
        self.grid.addWidget(self.cancelButton, 3, 1)
        
        self.show()
        
    def setElementType(self, idx=0):
        department = str(self.departmentMenu.currentText())
        self.refreshList(department)
        
    def createReference(self):
        selected = []
        del self.filePaths[:]
        for item in self.assetList.selectedItems():
            body = self.project.get_body(str(item.text()))
            element = body.get_element(str(self.departmentMenu.currentText()))
            path = element.get_app_filepath()
            self.filePaths.append(path)
            selected.append(str(item.text()))
        checkout = self.project.get_checkout(os.path.dirname(self.src))
        if checkout is not None:
            body_name = checkout.get_body_name()
            body = self.project.get_body(body_name)
            for sel in selected:
                body.add_reference(sel)
        self.done = False
        self.reference = True
        self.close()

    def refreshList(self, department):
        if department in Department.FRONTEND:
            asset_filter = None
            if(self.typeFilter.currentIndex()):
                asset_filter_str = str(self.typeFilter.currentText())
                asset_filter = (Asset.TYPE, operator.eq, asset_filter_str)
            self.elements = self.project.list_assets(asset_filter)
        else:
            self.elements = self.project.list_shots()
            
        self.assetList.clear()
        for e in self.elements:
            self.assetList.addItem(e)
        
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
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = ReferenceWindow(app, None)
    sys.exit(app.exec_())

