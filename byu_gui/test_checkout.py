import sys
import os
from PyQt4 import QtGui
#from byuam.project import Project


CHECKOUT_WINDOW_WIDTH = 340
CHECKOUT_WINDOW_HEIGHT = 575
dept_list = ['Model', 'Rig', 'Animation', 'Layout']

class checkoutWindow(QtGui.QTabWidget):
	def __init__(self):
		super(checkoutWindow, self).__init__()
		self.initUI()

	def initUI(self):
		#define gui elements
		self.setWindowTitle('Checkout')
		self.resize(CHECKOUT_WINDOW_WIDTH, CHECKOUT_WINDOW_HEIGHT)

		#create tabs
		self.dept_tabs = QtGui.QTabWidget()
		for dept in dept_list:
			tab = QtGui.QWidget()
			self.dept_tabs.addTab(tab, dept)

		#create buttons
		self.checkout_button = QtGui.QPushButton('Checkout')
		self.cancel_button = QtGui.QPushButton('Cancel')    
		
		#create button layout
		button_layout = QtGui.QHBoxLayout()
		button_layout.setSpacing(2)
		
		button_layout.addWidget(self.checkout_button)
		button_layout.addWidget(self.cancel_button)
		
		main_layout = QtGui.QVBoxLayout()
		self.setLayout(main_layout)
		main_layout.setSpacing(5)
		main_layout.setMargin(6)
		main_layout.addWidget(self.dept_tabs)
		main_layout.addLayout(button_layout)

		self.show()

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
	ex = checkoutWindow()
	sys.exit(app.exec_())
