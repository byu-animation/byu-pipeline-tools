# Author: Trevor Barrus

import sys
import os
from PySide2 import QtWidgets, QtCore, QtGui
from byuam.project import Project

WINDOW_WIDTH = 300
WINDOW_HEIGHT = 200

class CreateWindow(QtWidgets.QTabWidget):

    finished = QtCore.Signal()

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

    def accept(self):
        self.finished.emit()
        self.close()


class NewAssetWindow(QtWidgets.QWidget):
    def __init__(self, element, parent):
        super(NewAssetWindow, self).__init__()
        self.parent = parent
        self.element = element
        self.initUI()

    def initUI(self):
        #define gui elements
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.label = QtWidgets.QLabel('Enter the %s name' % self.element)
        self.textField = QtWidgets.QLineEdit()
        self.okBtn = QtWidgets.QPushButton('Ok')
        self.okBtn.clicked.connect(self.createAsset)
        self.cancelBtn = QtWidgets.QPushButton('Cancel')
        self.cancelBtn.clicked.connect(self.parent.close)
        #set image
        self.img = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(os.environ['BYU_TOOLS_DIR'] + '/byugui/assets/images/film-banner.jpg')
        scaled = pixmap.scaledToWidth(self.size().width()/3)
        self.img.setPixmap(scaled)

        #set gui layout
        grid = QtWidgets.QGridLayout(self)
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
            self.parent.accept()
        except EnvironmentError, e:
            print e
            self.parent.accept()

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Return:
            self.createAsset()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = CreateWindow()
    sys.exit(app.exec_())
