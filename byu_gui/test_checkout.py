import sys
import os
from PyQt4 import QtGui
#from byuam.project import Project

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

class newAssetWindow(QtGui.QWidget):
    def __init__(self):
	   super(newAssetWindow, self).__init__()
	   self.initUI()
   
    def initUI(self):
	   #define gui elements
	   self.setGeometry(300,300,340,575)
	   self.setWindowTitle('Checkout')
	   self.setStyleSheet(stylesheet)
	   
	   self.dept_list = ['Model', 'Rig', 'Animation', 'Layout']
	   self.dept_tabs = QtGui.QTabWidget()
	   for dept in self.dept_list:
			widget = QtGui.QWidget()
			self.dept_tabs.addTab(widget, dept)
            
	   self.textField = QtGui.QLineEdit()
	   self.okBtn = QtGui.QPushButton('Ok')
	   self.okBtn.clicked.connect(self.createAsset)
	   self.cancelBtn = QtGui.QPushButton('Cancel')
	   self.cancelBtn.clicked.connect(app.quit)
	   
	   #set gui layout
	   grid = QtGui.QGridLayout(self)
	   self.setLayout(grid)
	   grid.addWidget(self.textField, 1, 0, 1, 3)
	   grid.addWidget(self.okBtn, 2, 1)
	   grid.addWidget(self.cancelBtn, 2, 2)
	   self.show()
	#create container
    def createAsset(self):
	   name = self.textField.text()
	   project = Project()
	   project.create_asset(name)
		
   
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = newAssetWindow()
    sys.exit(app.exec_())
