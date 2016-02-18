from PyQt4 import QtGui, QtCore
import sys
from byuam.project import Project

CHECKOUT_WINDOW_WIDTH = 340
CHECKOUT_WINDOW_HEIGHT = 575

"""
Checkout Dialog is the Dialog window for the Checkout tool
"""


class CheckoutWindow(QtGui.QWidget):
    def _init_(self):
        super(CheckoutWindow, self)._init_()
        # self.project = Project()
        self.dept_list = ['Model', 'Rig', 'Animation', 'Layout']

        # Initialize the GUI
        self.setWindowTitle('Checkout')
        self.setFixedSize(CHECKOUT_WINDOW_WIDTH, CHECKOUT_WINDOW_HEIGHT)

        # Create tabbed view
        self.dept_tabs = QtGui.QTabWidget()
        for dept in self.dept_list:
            self.dept_tabs.addTab(dept)

        # Create Label to hold asset info
        self.asset_info_label = QtGui.QLabel()
        self.asset_info_label.setWordWrap(True)

        # Create action buttons
        self.checkout_button = QtGui.QPushButton('Checkout')
        self.cancel_button = QtGui.QPushButton('Cancel')

        # Create button layout
        button_layout = QtGui.QHBoxLayout()
        button_layout.setSpacing(2)

        button_layout.addWidget(self.checkout_button)
        button_layout.addWidget(self.cancel_button)

        # Create main layout
        main_layout = QtGui.QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setMargin(6)
        main_layout.addWidget(self.dept_tabs)
        main_layout.addWidget(self.asset_info_label)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Change checkout context
        self.dept_tabs.currentChanged.connect(self.refresh)

        # Connect the buttons
        self.checkout_button.clicked.connect(self.checkout)
        self.cancel_button.clicked.connect(self.cancel)

    def checkout(self):
        """
        Checks out the currently selected item
        :return:
        """
        print('Checkout')

    def cancel(self):
        """
        Cancels the checkout
        :return:
        """
        self.close()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    #window = CheckoutWindow()
    #window.show()
    ex = CheckoutWindow()
    sys.exit(app.exec_())
