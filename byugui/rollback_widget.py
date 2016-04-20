import sys

from PyQt4 import QtCore
from PyQt4.QtGui import *

WIDTH = 400
HEIGHT = 500

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
		self.commentLabel.setWordWrap(True)
		detailView = QVBoxLayout()
		detailView.addWidget(self.versionLabel, alignment=QtCore.Qt.AlignHCenter)
		detailView.addStretch(1)
		detailView.addWidget(self.authorLabel, alignment=QtCore.Qt.AlignHCenter)
		detailView.addStretch(1)
		detailView.addWidget(self.commentLabel)
		detailView.addStretch(4)
		rollbackBtn = QPushButton('Rollback to this Version')
		rollbackBtn.clicked.connect(lambda: self._rollback_to_version(self.versionsList.currentItem()))
		detailView.addWidget(rollbackBtn)
		detailView.addStretch(1)
		cancel = QPushButton('Cancel')
		cancel.clicked.connect(self._cancel)
		detailView.addWidget(cancel)

		hbox = QHBoxLayout()
		hbox.addWidget(self.versionsList)
		hbox.addLayout(detailView)
		hbox.setStretchFactor(self.versionsList, 1)
		hbox.setStretchFactor(detailView, 2)

		self.setLayout(hbox)

		self.versions = []
		self._fill_dummy_data()
		self.show()

	def _fill_dummy_data(self):
		for i in range(20):
			v = VersionInfo('Revision %s' % (i + 1), "Bob Jenkins\n(bob@jenkins.com)", "Changed some stuff and did some things to make the whatever be better")
			self.versions = [v] + self.versions
			item = QListWidgetItem(v.version)
			self.versionsList.insertItem(0, item)

	def _update_detail_view(self, currentSelection, prevSelection):
		selectedVersion = self.versions[self.versionsList.currentRow()]
		self.versionLabel.setText(selectedVersion.version)
		self.authorLabel.setText(selectedVersion.author)
		self.commentLabel.setText(selectedVersion.comment)

	def _rollback_to_version(self, version):
		print "Not yet implemented"

	def _cancel(self):
		self.close()

class VersionInfo:
	def __init__(self, version, author, comment):
		self.version = version
		self.author = author
		self.comment = comment


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = RollbackWidget(app)
	sys.exit(app.exec_())
