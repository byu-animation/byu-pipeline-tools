import sys
import os
from PyQt4 import QtGui
from byuam.project import Project
from byuam.environment import Department
		
CHECKOUT_WINDOW_WIDTH = 340
CHECKOUT_WINDOW_HEIGHT = 575
stylesheet = """
	        QWidget {
	            background-color:#2E2E2E;
	            color: white;
	        }
	        QLineEdit {
			    background-color: black;
	        }
	    """

dept_list = ['model', 'rig', 'anim', 'layout']

class checkoutWindow(QtGui.QTabWidget):
	def __init__(self):
		super(checkoutWindow, self).__init__()
		self.project = Project()
		self.initUI()

	def initUI(self):
		#define gui elements
		self.setWindowTitle('Checkout')
		self.resize(CHECKOUT_WINDOW_WIDTH, CHECKOUT_WINDOW_HEIGHT)
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
				elif dept in Department.BACKEND:
					for shot in self.project.list_shots():
						item = QtGui.QListWidgetItem(shot)
						element_list.addItem(item)
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

	def checkout(self):
		"""
		Checks out the currently selected item
		:return:
		"""
		#self.dept = dept_list[self.dept_tabs.currentIndex()]
		#self.current_item = 
		print('Checkout')

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	ex = checkoutWindow()
	sys.exit(app.exec_())
