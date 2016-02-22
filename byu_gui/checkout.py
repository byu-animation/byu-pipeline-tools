import sys
from PyQt4 import QtGui
from byuam.project import Project
from byuam.environment import Department
		
CHECKOUT_WINDOW_WIDTH = 340
CHECKOUT_WINDOW_HEIGHT = 575
dept_list = ['Model', 'Rig', 'Animation', 'Layout']

class checkoutWindow(QtGui.QTabWidget):
	def __init__(self):
		super(checkoutWindow, self).__init__()
		self.project = Project()
		self.initUI()

	def initUI(self):
		#define gui elements
		self.setWindowTitle('Checkout')
		self.resize(CHECKOUT_WINDOW_WIDTH, CHECKOUT_WINDOW_HEIGHT)

		#create tabs
		self.dept_tabs = QtGui.QTabWidget()
		asset_list = QtGui.QListWidget()
		for asset in self.project.list_assets():
			item = QtGui.QListWidgetItem(asset)
			asset_list.addItem(item)
		shot_list = QtGui.QListWidget()
		for shot in self.project.list_shots():
			item = QtGui.QListWidgetItem(shot)
			shot_list.addItem(item)
		
		for dept in dept_list:
			if dept in Department.FRONTEND:
				tab = QtGui.QWidget()
				tab.addWidget(asset_list)
				self.dept_tabs.addTab(tab, dept)
			elif dept in Department.BACKEND:
				tab = QtGui.QWidget()
				tab.addWidget(shot_list)
				self.dept_tabs.addTab(tab, dept)
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

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	ex = checkoutWindow()
	sys.exit(app.exec_())
