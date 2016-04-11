import sys

from PyQt4 import QtCore
from PyQt4.QtGui import *

WIDTH = 300
HEIGHT = 600

class RollbackWidget(QWidget):
	def __init__(self, parent):
		super(RollbackWidget, self).__init__()
		self.parent = parent
		self.build_ui()

	def build_ui(self):
		self.setGeometry(300, 300, WIDTH, HEIGHT)
		self.setWindowTitle('Rollback to Previous Version')
		self.versionsList = QListWidget(self)
		self.versionsList.currentItemChanged.connect(self._update_detail_view)

		self.versionLabel = QLabel()
		self.authorLabel = QLabel()
		self.commentLabel = QLabel()
		detailView = QVBoxLayout()
		detailView.addWidget(self.versionLabel)
		detailView.addWidget(self.authorLabel)
		detailView.addWidget(self.commentLabel)
		detailView.addWidget(QPushButton('Rollback'))

		hbox = QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(self.versionsList)
		hbox.addLayout(detailView)

		self.setLayout(hbox)
		self._fill_dummy_data()
		self.show()

	def _fill_dummy_data(self):
		dummy_items = ['Item %s' % (i + 1) for i in range(10)]
		self.versionsList.addItems(dummy_items)

	def _update_detail_view(self, currentSelection, prevSelection):
		self.versionLabel.setText(currentSelection.text())
		self.authorLabel.setText('Bob Jenkins')
		self.commentLabel.setText('Change the stuff and things to do whatever')


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = RollbackWidget(app)
	sys.exit(app.exec_())
