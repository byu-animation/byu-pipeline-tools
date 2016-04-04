# Author: Trevor Barrus

import sys
import os
import traceback
from PyQt4 import QtGui, QtCore
from byuam.project import Project
from byuam.environment import Environment, Department, Status

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
    
class PublishWindow(QtGui.QWidget):

    finished = QtCore.pyqtSignal()

    def __init__(self, src, parent, dept_list=Department.ALL):
        super(PublishWindow, self).__init__()
        self.environment = Environment()
        self.project = Project()
        self.eList = ElementList(self)
        self.parent = parent
        self.src = src
        self.result = None
        self.elementType = None
        self.initUI(dept_list)
        self.published = False
	    
    def initUI(self, dept_list):
	    #define gui elements
	    self.setGeometry(300,300,WINDOW_WIDTH,WINDOW_HEIGHT)
	    self.setWindowTitle('Publish')
	    self.menu = QtGui.QComboBox()
	    self.menu.addItem('Asset')
	    self.menu.addItem('Shot')
	    self.departmentMenu = QtGui.QComboBox()
	    for i in dept_list:
		    self.departmentMenu.addItem(i)
        
	    self.departmentMenu.activated[str].connect(self.setElementType)
	    self.filePath = QtGui.QLineEdit();
	    self.filePath.setReadOnly(True)
	    self.label = QtGui.QLabel('What did you change?')
	    self.comment = QtGui.QTextEdit()
	    self.publishBtn = QtGui.QPushButton('Publish')
	    self.publishBtn.setEnabled(False)
	    
	    self.eList.currentItemChanged.connect(self.selectElement)
	    self.publishBtn.clicked.connect(self.publish)
	    
	    #set gui layout
	    self.grid = QtGui.QGridLayout(self)
	    self.setLayout(self.grid)
	    self.grid.addWidget(self.departmentMenu, 0, 0)
	    self.grid.addWidget(self.label, 1, 1)
	    self.grid.addWidget(self.eList, 2, 0)
	    self.grid.addWidget(self.comment, 2, 1)
	    self.grid.addWidget(self.filePath, 3, 0)
	    self.grid.addWidget(self.publishBtn, 3, 1)
	    
	    self.show()
	    
    def setElementType(self):
        department = str(self.departmentMenu.currentText())
        if department in Department.FRONTEND:
            self.elementType = 'Asset'
        else:
            self.elementType = 'Shot'
        self.eList.refreshList(self.elementType)
	    
    def selectElement(self):
        currentItem = self.eList.currentItem()
        if currentItem is not None:
	       self.filePath.setText(self.eList.currentItem().text())
	       self.publishBtn.setEnabled(True)

    def publish(self):
        self.elementType = str(self.menu.currentText())
        #element = None
        element = self.project.get_checkout_element(os.path.dirname(self.src))
        try:
            #Leave here to use for advanced options
            #if self.elementType == 'Asset':
            #    asset = self.project.get_asset(str(self.filePath.text()))
            #    element = asset.get_element(str(self.departmentMenu.currentText()))
            #else:
            #    shot = self.project.get_shot(str(self.filePath.text()))
            #    element = shot.get_element(str(self.departmentMenu.currentText()))
		
            self.user = self.environment.get_current_username()
            self.comment = str(self.comment.toPlainText())
            self.result = element
            self.published = True
            self.close()
        except Exception, e:
            print e
            error = QtGui.QLineEdit()
            error.setText(str(e))
            self.grid.addWidget(error, 4, 1, 2, 1)
            traceback.print_stack()

    def closeEvent(self, event):
        self.finished.emit()
        event.accept()
	    
class ElementList(QtGui.QListWidget):
    def __init__(self, parent):
        super(ElementList, self).__init__()
        self.parent = parent
        self.project = Project()
        self.elements = self.project.list_assets()
        self.initUI()	    
	    
    def initUI(self):
	    #define gui elements
	    self.refreshList('Asset')
		    
    #Update the list based on the input element type
    def refreshList(self, element):
        if element == 'Asset':
		    self.elements = self.project.list_assets()
        else:
		    self.elements = self.project.list_shots()
		    
        self.clear()
        for e in self.elements:
		    self.addItem(e)
	    

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = PublishWindow(os.environ['BYU_TOOLS_DIR'] + '/byu_gui/test.txt', app)
    sys.exit(app.exec_())
