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
    def __init__(self, src, parent):
        super(PublishWindow, self).__init__()
        self.environment = Environment()
        self.project = Project()
        self.eList = elementList()
        self.parent = parent
        self.src = src
        self.elementType = None
        self.initUI()
	    
    def initUI(self):
	    #define gui elements
	    self.setGeometry(300,300,WINDOW_WIDTH,WINDOW_HEIGHT)
	    self.setWindowTitle('Publish')
	    self.menu = QtGui.QComboBox()
	    self.menu.addItem('Asset')
	    self.menu.addItem('Shot')
	    self.departmentMenu = QtGui.QComboBox()
	    for i in Department.ALL:
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
	    self.filePath.setText(self.eList.currentItem().text())
	    self.publishBtn.setEnabled(True)

    def publish(self):
        elementType = str(self.menu.currentText())
        element = None
        try:
            if self.elementType == 'Asset':
                asset = self.project.get_asset(str(self.filePath.text()))
                element = asset.get_element(str(self.departmentMenu.currentText()))
            else:
                shot = self.project.get_shot(str(self.filePath.text()))
                element = shot.get_element(str(self.departmentMenu.currentText()))
		
            user = self.environment.get_current_user()
            src = self.src
            comment = str(self.comment.toPlainText())
            element.publish(user, src, comment)
            app.quit()
        except Exception, e:
            print e
            error = QtGui.QLineEdit()
            error.setText(str(e))
            self.grid.addWidget(error, 4, 1, 2, 1)
            traceback.print_stack()
	    
class elementList(QtGui.QListWidget):
    def __init__(self):
	    super(elementList, self).__init__()
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
    ex = PublishWindow(os.environ['BYU_TOOLS_DIR'] + '/byu_gui/test.txt')
    sys.exit(app.exec_())
