# Author: Samuel 

import sys
import os
from PyQt4 import QtGui, QtCore
from byuam.project import Project
from byuam.environment import Department, Environment

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

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

dept_list = Department.FRONTEND

class checkoutWindow(QtGui.QTabWidget):
    def __init__(self):
        super(checkoutWindow, self).__init__()
        self.project = Project()
        self.environment = Environment()
        self.initUI()

    def initUI(self):
        #define gui elements
        self.setWindowTitle('Checkout')
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(stylesheet)

        #create tabs
        self.dept_tabs = QtGui.QTabWidget()
        for dept in dept_list:
            if dept in Department.ALL:
                tab = QtGui.QWidget()
                self.dept_tabs.addTab(tab, dept)
                tab_layout = QtGui.QVBoxLayout()
                element_list = QtGui.QListWidget()
				
                if dept in Department.FRONTEND:
                    for asset in self.project.list_assets():
                        item = QtGui.QListWidgetItem(asset)
                        element_list.addItem(item)
                        element_list.currentItemChanged.connect(self.set_current_item)
                elif dept in Department.BACKEND:
                    for shot in self.project.list_shots():
                        item = QtGui.QListWidgetItem(shot)
                        element_list.addItem(item)
                        element_list.currentItemChanged.connect(self.set_current_item)
                tab_layout.addWidget(element_list)
                tab.setLayout(tab_layout)
            else:
                print("Not a valid Department")

        #create buttons
        self.checkout_button = QtGui.QPushButton('Checkout')
        self.checkout_button.clicked.connect(self.checkout)
        self.cancel_button = QtGui.QPushButton('Cancel')
        self.cancel_button.clicked.connect(app.quit)    
		
        #create button layout
        button_layout = QtGui.QHBoxLayout()
        button_layout.setSpacing(2)
        button_layout.addWidget(self.checkout_button)
        button_layout.addWidget(self.cancel_button)

        self.img = QtGui.QLabel()
        pixmap = QtGui.QPixmap(os.getcwd() + '/assets/images/taijitu.jpg')
        scaled = pixmap.scaledToWidth(self.size().width())
        self.img.setPixmap(scaled)

        #create main layout
        main_layout = QtGui.QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(self.img)
        main_layout.setSpacing(5)
        main_layout.setMargin(6)
        main_layout.addWidget(self.dept_tabs)
        main_layout.addLayout(button_layout)

        self.show()
        
        
    def set_current_item(self, index):
        current_dept = dept_list[self.dept_tabs.currentIndex()]
        if current_dept in Department.FRONTEND:
            self.current_item = str(index.text())
        elif current_dept in Department.BACKEND:
            self.current_item = str(index.text())

    def checkout(self):
        """
        Checks out the currently selected item
        :return:
        """
        current_user = self.environment.get_current_user()
        current_dept = dept_list[self.dept_tabs.currentIndex()]
        asset_obj = self.project.get_asset(self.current_item)
        element_obj = asset_obj.get_element(current_dept)
        element_path = element_obj.checkout(current_user)
        if element_path != None:
            app.quit()
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = checkoutWindow()
    sys.exit(app.exec_())
