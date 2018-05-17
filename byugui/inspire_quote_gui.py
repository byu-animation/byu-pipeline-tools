# Author: Ben DeMann

import sys
import os
import traceback
import json
import random
import requests
from requests.api import get
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
		self.addQuotesFromSlack()
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

# Scales image to proper size. Minimizes code duplication.
	def scaleImage(self, pixmap):
		scaled = pixmap.scaledToWidth(self.size().width()/2)
		print scaled
		print "\n" + str(self.size()) + " " + str(self.size().width())
		self.img.setPixmap(scaled)

	def populateQuote(self):
		quoteInfo = self.getQuote()
		self.quote.setText(quoteInfo["quote"] + "\n\t-" + quoteInfo["author"])# + "\n\n\n Submitted by: " + quoteInfo["contributor"])
		# If we obtained the quote from Slack, this grabs the avatar of the user who posted the quote.
		if "slack" in quoteInfo['image']:
			path = quoteInfo['image']
			res = get(path)
			pixmap = QtGui.QPixmap()
			pixmap.loadFromData(res.content)
			self.scaleImage(pixmap)
		else:
			image_path = os.path.join(os.environ['BYU_TOOLS_DIR'], 'byugui', 'assets', 'images', quoteInfo['image'])
			pixmap = QtGui.QPixmap(image_path)
			self.scaleImage(pixmap)

	def closeEvent(self, event):
		self.finished.emit()
		event.accept()

# Gets image to use for each Slack quote.
	def getImageForSlackQuote(self, userID):
		# We will send another GET request to the slack API.
		URL = "https://slack.com/api/users.profile.get?token=xoxp-262198519712-364750013863-363181322081-b04dd4517e6975431c598decc65c85fd&user=" + userID
		result = get(URL)
		jsonData = result.json()
		imageID = jsonData['profile']['image_1024']
		return imageID

# Pulls quotes from the all_the_quotes Slack channel.
	def addQuotesFromSlack(self):
		# Authentication via Dandbot's user account. Dandbot isn't actually a bot, but rather a user registered to the Slack workspace.
		URL = "https://slack.com/api/channels.history?token=xoxp-262198519712-364750013863-363181322081-b04dd4517e6975431c598decc65c85fd&channel=C98MS1YH1"
		# Send a GET request to the Slack service, and convert it into a JSON object.
		result = get(URL)
		myJson = result.json()
		# Iterate through all the received messages from Slack.
		for message in myJson['messages']:
			# Ensures that we only pull quotes from the chat, while omitting "user_x joined #all_the_quotes" messages.
			if "-" in message['text']:
				userID = message['user']
				print "userID: ", userID
				img = self.getImageForSlackQuote(userID)
				# rsplit accounts for quotes that might have hyphens in them, such as "flaming hell-octo-copter".
				data = message['text'].rsplit("-", 1)
				author = data[1]
				quote = data[0]
				# Format JSON object for appending to the JSON array.
				toAppendToJson = ("{\"author\": \"" + author + "\","
					+ "\"quote\": " + quote + ","
					+ "\"image\": \"" + img + "\","
					+ "\"contributor\": \"Alex Neville and Dandbot\"}")
				# Appends data to the JSON object at runtime, so we don't have to create a database of already uploaded quotes.
				jsonDict = json.loads(toAppendToJson)
				self.quoteData.append(jsonDict)

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	ex = QuoteWindow(app)
	sys.exit(app.exec_())
