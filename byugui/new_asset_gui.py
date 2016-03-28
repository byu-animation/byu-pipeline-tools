# Author: Trevor Barrus

import sys
import os
from PyQt4 import QtGui, QtCore
from byuam.project import Project

WINDOW_WIDTH = 300
WINDOW_HEIGHT = 200
        
class CreateWindow(QtGui.QTabWidget):

    finished = QtCore.pyqtSignal()

    ASSET_INDEX = 0
    SHOT_INDEX = 1

    def __init__(self, parent):
        super(CreateWindow, self).__init__()
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        #define gui elements
        self.setGeometry(300,300,WINDOW_WIDTH,WINDOW_HEIGHT)
        self.setWindowTitle('Create New Body')
        
        #create tabs
        assetTab = NewAssetWindow('asset', self)
        shotTab = NewAssetWindow('shot', self)
        
        self.insertTab(self.ASSET_INDEX, assetTab, 'Asset')
        self.insertTab(self.SHOT_INDEX, shotTab, 'Shot')
        
        self.show()

    def closeEvent(self, event):
        self.finished.emit()
        event.accept()

class NewAssetWindow(QtGui.QWidget):
    def __init__(self, element, parent):
        super(NewAssetWindow, self).__init__()
        self.parent = parent
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
        self.cancelBtn.clicked.connect(self.parent.close)
        #set image
        self.img = QtGui.QLabel()
        pixmap = QtGui.QPixmap(os.environ['BYU_TOOLS_DIR'] + '/byugui/assets/images/taijitu.jpg')
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
            # app.quit()
            self.parent.close()
        except EnvironmentError, e:
            print e
            # app.quit()
            self.parent.close()
            
    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Return:
            self.createAsset()
    
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = createWindow()
    sys.exit(app.exec_())
