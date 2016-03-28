# Author: Trevor Barrus

import sys
import os
from PyQt4 import QtGui, QtCore
from byuam.project import Project
from byuam.environment import Department, Environment

WINDOW_WIDTH = 650
WINDOW_HEIGHT = 600

# dept_list = Department.ALL
        
class CheckoutWindow(QtGui.QWidget):

    finished = QtCore.pyqtSignal()

    def __init__(self, parent, dept_list=Department.ALL):
        super(CheckoutWindow, self).__init__()
        self.parent = parent
        self.project = Project()
        self.environment = Environment()
        self.initUI(dept_list)
        
    def initUI(self, dept_list):
        #define gui elements
        self.resize(WINDOW_WIDTH,WINDOW_HEIGHT)
        self.setWindowTitle('Checkout')
        self.dept_tabs = QtGui.QTabWidget()
        self.dept_list = dept_list
        self.result = None
        #create tabs
        for dept in dept_list:
            tab = DepartmentTab(self)
            #tab = QtGui.QWidget()
            # self.dept_tabs.insertTab(self.ASSET_INDEX, tab, dept)
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
            
        #create buttons
        self.checkout_button = QtGui.QPushButton('Checkout')
        self.checkout_button.clicked.connect(self.checkout)
        self.cancel_button = QtGui.QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.close)    
		
        #create button layout
        button_layout = QtGui.QHBoxLayout()
        #button_layout.setSpacing(2)
        button_layout.addWidget(self.checkout_button)
        button_layout.addWidget(self.cancel_button)

        self.img = QtGui.QLabel()
        pixmap = QtGui.QPixmap(os.environ['BYU_TOOLS_DIR'] + '/byugui/assets/images/taijitu.jpg')
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
        current_dept = self.dept_list[self.dept_tabs.currentIndex()]
        if current_dept in Department.FRONTEND:
            self.current_item = str(index.text())
        elif current_dept in Department.BACKEND:
            self.current_item = str(index.text())
            
    def checkout(self):
        """
        Checks out the currently selected item
        :return:
        """
        current_user = self.environment.get_current_username()
        current_dept = self.dept_list[self.dept_tabs.currentIndex()]
        asset_obj = self.project.get_body(self.current_item)
        element_obj = asset_obj.get_element(current_dept)
        element_path = element_obj.checkout(current_user)
        if element_path != None:
            # self.parent.close()
            self.result = element_path
            self.close()
            

    def closeEvent(self, event):
        self.finished.emit()
        event.accept()
        
class DepartmentTab(QtGui.QWidget):
    def __init__(self, parent):
        super(DepartmentTab, self).__init__()
        self.parent = parent
        #self.initUI()
        
    def initUI(self):
        #define gui elements
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = CheckoutWindow(app)
    sys.exit(app.exec_())
