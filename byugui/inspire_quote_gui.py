# Author: Ben DeMann

import sys
import os
import traceback
import json
import random
try:
	from PySide import QtGui as QtWidgets
	from PySide import QtGui as QtGui
	from PySide import QtCore
except ImportError:
	from PySide2 import QtWidgets, QtGui, QtCore

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 200

class QuoteWindow(QtWidgets.QWidget):

	finished = QtCore.Signal()

	def __init__(self, parent):
		super(QuoteWindow, self).__init__()
		self.parent = parent
		quotes_path = os.path.join(os.environ['BYU_TOOLS_DIR'], 'byugui', 'assets', 'inspire-quotes.json')
		quote_json = file(quotes_path)
		self.quoteData = json.loads(quote_json.read())['quotes']
		self.initUI()

	def initUI(self):
		#define gui elements
		self.setGeometry(300,300,WINDOW_WIDTH,WINDOW_HEIGHT)
		self.setWindowTitle('Inspirational Quotes')

		self.quote = QtWidgets.QTextEdit()
		self.quote.setReadOnly(True)
		self.img = QtWidgets.QLabel()
		self.returnBtn = QtWidgets.QPushButton('Return to Work')
		self.returnBtn.setEnabled(True)
		self.moreBtn = QtWidgets.QPushButton('Be More Inspired')
		self.moreBtn.setEnabled(True)

		self.returnBtn.clicked.connect(self.close)
		self.moreBtn.clicked.connect(self.populateQuote)

		self.populateQuote()

		#set gui layout
		self.grid = QtWidgets.QGridLayout(self)
		self.setLayout(self.grid)

		self.grid.addWidget(self.img, 0, 0)
		self.grid.addWidget(self.quote, 0, 1)
		self.grid.addWidget(self.moreBtn, 1, 0)
		self.grid.addWidget(self.returnBtn, 1, 1)

		self.show()

	def getQuote(self):
		index = random.randrange(0,len(self.quoteData))
		return self.quoteData[index]

	def populateQuote(self):
	quoteInfo = self.getQuote()

		self.quote.setText(quoteInfo["quote"] + "\n\t-" + quoteInfo["author"])# + "\n\n\n Submitted by: " + quoteInfo["contributor"])
		image_path = os.path.join(os.environ['BYU_TOOLS_DIR'], 'byugui', 'assets', 'images', quoteInfo['image'])
		pixmap = QtGui.QPixmap(image_path)
		scaled = pixmap.scaledToWidth(self.size().width()/2)
		print scaled
		print "\n" + str(self.size()) + " " + str(self.size().width())
		self.img.setPixmap(scaled)

	def closeEvent(self, event):
		self.finished.emit()
		event.accept()

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	ex = QuoteWindow(app)
	sys.exit(app.exec_())
