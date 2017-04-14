# Author: Trevor Barrus

import sys
import os
from PySide2 import QtWidgets, QtCore, QtGui
from byuam.project import Project
from byuam.environment import Department, Environment


WINDOW_WIDTH = 650
WINDOW_HEIGHT = 600

class CheckoutWindow(QtWidgets.QWidget):

    finished = QtCore.Signal()

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
        self.dept_tabs = QtWidgets.QTabWidget()
        self.dept_list = dept_list
        self.result = None

        #create checkbox to show only published assets
        self.show_published = QtWidgets.QCheckBox("Display only assets or shots with previous publishes")
        self.show_published.setCheckState(QtCore.Qt.Checked)
        self.show_published.stateChanged.connect(self.changeBodyCheckoutVisibility)

        #create Tabs
        self.createTabs()
        print "Tabs have been created"

        #create buttons
        self.checkout_button = QtWidgets.QPushButton('Checkout')
        self.checkout_button.clicked.connect(self.checkout)
        self.cancel_button = QtWidgets.QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.close)
        print "Buttons have been created"

        #create button layout
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.checkout_button)
        button_layout.addWidget(self.cancel_button)

        self.img = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(os.environ['BYU_TOOLS_DIR'] + '/byugui/assets/images/film-banner.jpg')
        scaled = pixmap.scaledToWidth(self.size().width())
        self.img.setPixmap(scaled)

        #create main layout
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(self.img)
        main_layout.setSpacing(5)
        main_layout.setMargin(6)
        main_layout.addWidget(self.dept_tabs)
        main_layout.addWidget(self.show_published)
        main_layout.addLayout(button_layout)
        print "Layout have been created"

        self.show()

    def createTabs(self):
        #remember the current index so that we can restore it when we create the tabs
        currIndex = self.dept_tabs.currentIndex()
        #clear out the old tabs
        self.dept_tabs.clear()
        #create tabs
        for dept in self.dept_list:
            print "we are looking at " + dept
            tab = DepartmentTab(self)
            self.dept_tabs.addTab(tab, dept)
            tab_layout = QtWidgets.QHBoxLayout()
            element_list = QtWidgets.QListWidget()
            commentBox = QtWidgets.QTextEdit()
            commentBox.setReadOnly(True)
            tab.commentBox = commentBox

            if dept in Department.FRONTEND:
                for asset in self.project.list_assets():
                    if not self.show_published.isChecked() or self.hasPreviousPublish(asset, dept):
                        print "We passed the first check"
                        item = QtWidgets.QListWidgetItem(asset)
                        element_list.addItem(item)
                        element_list.currentItemChanged.connect(self.set_current_item)
            elif dept in Department.BACKEND:
                for shot in self.project.list_shots():
                    if not self.show_published.isChecked() or self.hasPreviousPublish(shot, dept):
                        print "We passed the second check"
                        item = QtWidgets.QListWidgetItem(shot)
                        element_list.addItem(item)
                        element_list.currentItemChanged.connect(self.set_current_item)
            tab_layout.addWidget(element_list)
            tab_layout.addWidget(commentBox)
            tab.setLayout(tab_layout)

        #restore the previous index
        self.dept_tabs.setCurrentIndex(currIndex)

    def hasPreviousPublish(self, body, department):
        print body
        print department
        asset_obj = self.project.get_body(body)
        print asset_obj
        element_obj = asset_obj.get_element(department)
        last_publish = element_obj.get_last_publish()
        if last_publish is None:
            return False
        return True

    def changeBodyCheckoutVisibility(self):
        #recreate tabs the with the new check option
        self.createTabs()

    def set_current_item(self, index):
        current_dept = self.dept_list[self.dept_tabs.currentIndex()]
        if current_dept in Department.FRONTEND:
            self.current_item = str(index.text())
        elif current_dept in Department.BACKEND:
            self.current_item = str(index.text())

        asset_obj = self.project.get_body(self.current_item)
        element_obj = asset_obj.get_element(current_dept)
        last_publish = element_obj.get_last_publish()
        last_publish_comment = None
        if last_publish is not None:
            last_publish_comment = "Last published {0} by {1} \n \"{2}\"".format(last_publish[1], last_publish[0], last_publish[2])
        else:
            last_publish_comment = "No publishes for this element"
        currentTab = self.dept_tabs.currentWidget()
        currentTab.commentBox.setText(last_publish_comment)

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
            self.result = element_path
            self.close()


    def closeEvent(self, event):
        self.finished.emit()
        event.accept()

class DepartmentTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super(DepartmentTab, self).__init__()
        self.parent = parent
        self.commentBox = None

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = CheckoutWindow(app)
    sys.exit(app.exec_())
