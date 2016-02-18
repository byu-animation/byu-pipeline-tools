import sys
import os
from PyQt4 import QtGui
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

class newAssetWindow(QtGui.QWidget):
    def __init__(self):
	    super(newAssetWindow, self).__init__()
	    self.initUI()
	    
    def initUI(self):
	    #define gui elements
	    self.setGeometry(300,300,400,150)
	    self.setWindowTitle('New Asset')
	    self.setStyleSheet(stylesheet)
	    self.label = QtGui.QLabel('Enter the asset name')
	    self.textField = QtGui.QLineEdit()
	    self.okBtn = QtGui.QPushButton('Ok')
	    self.okBtn.clicked.connect(self.createAsset)
	    self.cancelBtn = QtGui.QPushButton('Cancel')
	    self.cancelBtn.clicked.connect(app.quit)
	    #set image
	    self.img = QtGui.QLabel()
	    pixmap = QtGui.QPixmap(os.getcwd() + '/assets/images/taijitu.jpg')
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
	    self.show()
	
	#create container
    def createAsset(self):
	    try:
	        name = str(self.textField.text())
	        project = Project()
	        asset = project.create_asset(name)
	        app.quit()
	    except EnvironmentError, e:
		    print e
		    app.quit()
    
	    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = newAssetWindow()
    sys.exit(app.exec_())
