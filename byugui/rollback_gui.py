#Author Trevor Barrus

import sys
import os
from os import listdir
from PyQt4 import QtGui, QtCore
from byuam.project import Project
from byuam.environment import Environment

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 300

class RollbackWindow(QtGui.QWidget):
    
    finished = QtCore.pyqtSignal()
    
    def __init__(self, src, parent):
        super(RollbackWindow, self).__init__()
        self.src = src
        self.parent = parent
        self.environment = Environment()
        self.project = Project()
        self.publishes = []
        self.result = None
        self.initUI()
        self.list_publishes()
        
    def initUI(self):
        #define gui elements
        self.setGeometry(300,300,WINDOW_WIDTH,WINDOW_HEIGHT)
        self.setWindowTitle('Rollback Manager')
        
        self.publish_list = QtGui.QListWidget()
        self.publish_list.currentItemChanged.connect(self.update_detail_view)
        self.infoLabel = QtGui.QLabel()
        
        self.rollbackButton = QtGui.QPushButton('Rollback')
        self.rollbackButton.clicked.connect(self.rollback)
        self.cancelButton = QtGui.QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.close)
        
        #set gui layout
        self.grid = QtGui.QGridLayout(self)
        self.setLayout(self.grid)
        self.grid.addWidget(self.publish_list, 0, 0, 3, 1)
        self.grid.addWidget(self.infoLabel, 0, 1)
        self.grid.addWidget(self.rollbackButton, 3, 0)
        self.grid.addWidget(self.cancelButton, 3, 1)
        
        self.show()
        
    def list_publishes(self):
        element = self.project.get_checkout_element(os.path.dirname(self.src))
        publishes = element.list_publishes();
        for p in publishes:
            publish = Publish(p[0], p[1], p[2])
            self.publishes = self.publishes + [publish]
            item = QtGui.QListWidgetItem(publish.timestamp)
            self.publish_list.addItem(item)
            
    def update_detail_view(self):
        selectedVersion = self.publishes[self.publish_list.currentRow()]
        self.infoLabel.setText("Author: {0} \nTimestamp: {1} \n\nComment: {2}".format(selectedVersion.author, selectedVersion.timestamp, selectedVersion.comment))
        
    def rollback(self):
        selectedVersion = self.publishes[self.publish_list.currentRow()]
        element = self.project.get_checkout_element(os.path.dirname(self.src))
        versionDir = element.get_version_dir(self.publish_list.currentRow())
        versionFile = listdir(versionDir)[0]
        filepath = versionDir + '/' + versionFile
        user = self.environment.get_current_username()
        comment = "Rollback to version dated \n{0}".format(selectedVersion.timestamp)
        element.publish(user, filepath, comment)
        #checkout element again to user to remove errors upon multiple uses of rollback
        self.result = element.checkout(user)
        self.close()
        
    def closeEvent(self, event):
        self.finished.emit()
        event.accept()
        
class Publish:
    def __init__(self, author, timestamp, comment):
        self.author = author
        self.timestamp = timestamp
        self.comment = comment
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = RollbackWindow(app)
    sys.exit(app.exec_())

