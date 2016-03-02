# Author: Trevor Barrus

import sys
import os
from PyQt4 import QtGui, QtCore
from byuam.project import Project

#set widget styles
stylesheet = """
	        QWidget {
	            background-color:#2E2E2E;
	            color: white;
	        }
	        QLineEdit {
			    background-color: black;
	        }
	    """

WINDOW_WIDTH = 300
WINDOW_HEIGHT = 200
	    
class createWindow(QtGui.QTabWidget):
    def __init__(self):
	    super(createWindow, self).__init__()
	    self.initUI()
	    
    def initUI(self):
	    #define gui elements
	    self.setGeometry(300,300,WINDOW_WIDTH,WINDOW_HEIGHT)
	    self.setWindowTitle('Create New Element')
	    self.setStyleSheet(stylesheet)
	    
	    #create tabs
	    tab1 = newAssetWindow('asset')
	    tab2 = newAssetWindow('shot')
	    
	    self.addTab(tab1, 'Asset')
	    self.addTab(tab2, 'Shot')
	    self.show()

class newAssetWindow(QtGui.QWidget):
    def __init__(self, element):
	    super(newAssetWindow, self).__init__()
	    self.element = element
	    self.initUI()
	    
    def initUI(self):
	    #define gui elements
	    self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
	    self.label = QtGui.QLabel('Enter the %s name' % self.element)
	    self.textField = QtGui.QLineEdit()
	    self.okBtn = QtGui.QPushButton('Ok')
	    self.okBtn.clicked.connect(self.createAsset)
	    self.cancelBtn = QtGui.QPushButton('Cancel')
	    self.cancelBtn.clicked.connect(app.quit)
	    #set image
	    self.img = QtGui.QLabel()
	    pixmap = QtGui.QPixmap(os.environ['BYU_TOOLS_DIR'] + '/byu_gui/assets/images/taijitu.jpg')
	    scaled = pixmap.scaledToWidth(self.size().width()/3)
	    self.img.setPixmap(scaled)
	    
	    #set gui layout
	    grid = QtGui.QGridLayout(self)
	    self.setLayout(grid)
	    grid.addWidget(self.img, 0, 0)
	    grid.addWidget(self.label, 0, 1, 0, 2)
	    grid.addWidget(self.textField, 1, 0, 1, 3)
	    grid.addWidget(self.okBtn, 2, 1)
	    grid.addWidget(self.cancelBtn, 2, 2)
	
	#generate directories
    def createAsset(self):
	    try:
	        name = str(self.textField.text())
	        name = name.replace(' ', '_')
	        project = Project()
	        if self.element == 'asset':
	            asset = project.create_asset(name)
	        else:
			    shot = project.create_shot(name)
	        app.quit()
	    except EnvironmentError, e:
		    print e
		    app.quit()
		    
    def keyPressEvent(self, event):
	    key = event.key()
	    if key == QtCore.Qt.Key_Return:
		    self.createAsset()
    
	    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = createWindow()
    sys.exit(app.exec_())
